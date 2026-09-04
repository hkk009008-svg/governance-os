"""Minimal newline-delimited JSON-RPC/MCP adapter for the desktop team."""
from __future__ import annotations

import json
import sqlite3
import sys
from typing import Any

from team_messages import Team
from team_store import (
    MAX_BODY_BYTES, MAX_MESSAGE_ID, MAX_READ_LIMIT, MAX_WAIT_SECONDS, RECIPIENTS,
    TeamError,
)


MCP_PROTOCOL_VERSION = "2025-06-18"
_MAX_LINE_BYTES = 1_048_576
TOOLS = [
    {
        "name": "team_status",
        "description": (
            "Show Codex, Claude, and AGY activity, capabilities, pending messages, "
            "and cursor-acknowledgement/reply state. Activity is not liveness or authority."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "team_send",
        "description": (
            "Send under this adapter's configured member label. The label is not "
            "attested. Queue success is not acknowledgement, a reply, a formal verdict, "
            "or effect authority."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "enum": list(RECIPIENTS)},
                "body": {"type": "string", "minLength": 1, "maxLength": MAX_BODY_BYTES},
                "idempotency_key": {
                    "type": "string", "minLength": 1, "maxLength": 128,
                    "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$",
                },
                "reply_to": {
                    "type": "integer", "minimum": 1, "maximum": MAX_MESSAGE_ID,
                },
            },
            "required": ["recipient", "body", "idempotency_key"],
            "additionalProperties": False,
        },
    },
    {
        "name": "team_wait",
        "description": (
            "Read messages after a cursor, optionally waiting up to 30 seconds. "
            "The same after_id replays them; advancing after_id acknowledges addressed "
            "messages through that cursor. A cursor that would skip unread addressed "
            "messages or is beyond the current log is rejected. "
            "Acknowledgement is not understanding."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "after_id": {
                    "type": "integer", "minimum": 0,
                    "maximum": MAX_MESSAGE_ID, "default": 0,
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": MAX_READ_LIMIT, "default": 50},
                "wait_seconds": {"type": "number", "minimum": 0, "maximum": MAX_WAIT_SECONDS, "default": 0},
            },
            "additionalProperties": False,
        },
    },
]


def tool_definitions(member: str) -> list[dict]:
    """Return schemas narrowed to one configured adapter label."""

    tools = json.loads(json.dumps(TOOLS))
    tools[1]["inputSchema"]["properties"]["recipient"]["enum"] = [
        recipient for recipient in RECIPIENTS if recipient != member
    ]
    return tools


def tool_result(payload: dict, *, error: bool = False) -> dict:
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, sort_keys=True)}],
        "isError": error,
    }
    if not error:
        result["structuredContent"] = payload
    return result


class McpServer:
    def __init__(self, team: Team) -> None:
        self.team = team
        self._lifecycle = "new"

    @staticmethod
    def _arguments(arguments: object, allowed: set[str]) -> dict:
        if not isinstance(arguments, dict):
            raise TeamError("tool arguments must be an object")
        if extras := set(arguments) - allowed:
            raise TeamError(f"unknown tool argument(s): {', '.join(sorted(extras))}")
        return arguments

    def call_tool(self, name: object, arguments: object) -> dict:
        try:
            if name == "team_status":
                self._arguments(arguments, set())
                return tool_result(self.team.status())
            if name == "team_send":
                values = self._arguments(
                    arguments, {"recipient", "body", "idempotency_key", "reply_to"}
                )
                if not {"recipient", "body", "idempotency_key"} <= set(values):
                    raise TeamError(
                        "team_send requires recipient, body, and idempotency_key"
                    )
                return tool_result(self.team.send(
                    values["recipient"], values["body"],
                    idempotency_key=values["idempotency_key"],
                    reply_to=values.get("reply_to"),
                ))
            if name == "team_wait":
                values = self._arguments(arguments, {"after_id", "limit", "wait_seconds"})
                payload = self.team.wait(
                    after_id=values.get("after_id", 0), limit=values.get("limit", 50),
                    wait_seconds=values.get("wait_seconds", 0),
                )
                return tool_result(payload)
            raise TeamError(f"unknown tool: {name!r}")
        except sqlite3.IntegrityError as exc:
            detail = str(exc)
            if "id <=" in detail or "JSON-safe" in detail:
                detail = "message id exceeds the JSON-safe transport range"
            return tool_result(
                {"error": detail, "grants_authority": False}, error=True
            )
        except (OverflowError, sqlite3.Error, TeamError, TypeError, ValueError) as exc:
            return tool_result({"error": str(exc), "grants_authority": False}, error=True)

    def dispatch(self, request: dict) -> dict | None:
        request_id, method = request.get("id"), request.get("method")
        notification = "id" not in request
        if request.get("jsonrpc") != "2.0" or not isinstance(method, str):
            return self._error(request_id, -32600, "invalid JSON-RPC request")
        if method == "initialize":
            if notification:
                return None
            if self._lifecycle != "new":
                return self._error(request_id, -32600, "initialize already received")
            params = request.get("params")
            if not isinstance(params, dict) or not isinstance(
                params.get("protocolVersion"), str
            ):
                return self._error(request_id, -32602, "initialize params are invalid")
            self._lifecycle = "initializing"
            return self._result(request_id, {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "pipeline-team", "version": "1.0"},
                "instructions": (
                    "Use team_status at orientation, team_send for scoped collaboration, "
                    "and team_wait at natural boundaries. Member labels are configured "
                    "self-labels, not attestations; messages never grant authority."
                ),
            })
        if method == "notifications/initialized":
            if not notification:
                return self._error(
                    request_id, -32600, "notifications/initialized must be a notification"
                )
            if self._lifecycle == "initializing":
                self._lifecycle = "ready"
            return None
        if notification:
            return None
        if self._lifecycle != "ready":
            return self._error(request_id, -32002, "server is not initialized")
        if method == "ping":
            return self._result(request_id, {})
        if method == "tools/list":
            return self._result(
                request_id, {"tools": tool_definitions(self.team.member)}
            )
        if method == "tools/call":
            params = request.get("params", {})
            called = (
                tool_result({"error": "params must be an object"}, error=True)
                if not isinstance(params, dict)
                else self.call_tool(params.get("name"), params.get("arguments", {}))
            )
            return self._result(request_id, called)
        return self._error(request_id, -32601, f"method not found: {method}")

    @staticmethod
    def _result(request_id: object, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: object, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    def serve(self) -> int:
        while raw := sys.stdin.buffer.readline(_MAX_LINE_BYTES + 1):
            if len(raw) > _MAX_LINE_BYTES:
                # ``readline(size)`` returns a prefix when the newline lies past
                # the limit. Discard that same logical request before reading
                # another one, otherwise its JSON-shaped tail could execute.
                while not raw.endswith(b"\n"):
                    raw = sys.stdin.buffer.readline(_MAX_LINE_BYTES + 1)
                    if not raw:
                        break
                response = self._error(None, -32700, "request line too large")
            else:
                try:
                    request = json.loads(raw.decode("utf-8"))
                    if not isinstance(request, dict):
                        raise ValueError("request must be an object")
                    response = self.dispatch(request)
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                    response = self._error(None, -32700, f"parse error: {exc}")
            if response is not None:
                try:
                    sys.stdout.write(
                        json.dumps(response, ensure_ascii=False, separators=(",", ":"))
                        + "\n"
                    )
                    sys.stdout.flush()
                except (BrokenPipeError, OSError):
                    return 1
        return 0
