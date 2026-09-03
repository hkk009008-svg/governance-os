#!/usr/bin/env python3
"""Desktop-app team entry point and stable public imports."""
from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from team_mcp import MCP_PROTOCOL_VERSION, McpServer
from team_messages import Team
from team_store import (
    CAPABILITIES, CURSOR_SEMANTICS, IDENTITY_ASSURANCE, MAX_BODY_BYTES,
    MAX_IDEMPOTENCY_KEY_BYTES, MAX_MESSAGE_ID, MAX_READ_LIMIT, MAX_WAIT_SECONDS,
    MEMBERS,
    RECIPIENTS, TeamError,
)

__all__ = [
    "CAPABILITIES", "CURSOR_SEMANTICS", "IDENTITY_ASSURANCE", "MAX_BODY_BYTES",
    "MAX_IDEMPOTENCY_KEY_BYTES", "MAX_MESSAGE_ID", "MAX_READ_LIMIT", "MAX_WAIT_SECONDS",
    "MCP_PROTOCOL_VERSION", "MEMBERS", "RECIPIENTS", "McpServer", "Team",
    "TeamError", "main",
]


import json


def _format_status(payload: dict) -> str:
    lines = [
        f"Member: {payload['member']}",
        f"Store: {payload['store']}",
        "Active team members:",
    ]
    for m in payload.get("members", []):
        seen = m.get("last_seen") or "never"
        lines.append(f"  - {m['name']}: pending={m.get('pending', 0)} last_seen={seen}")
    sent = payload.get("sent", [])
    lines.append(f"Recent sent messages: {len(sent)}")
    return "\n".join(lines)


def _format_wait(payload: dict) -> str:
    messages = payload.get("messages", [])
    next_cursor = payload.get("next_cursor", 0)
    lines = [f"Messages returned: {len(messages)} (next cursor: {next_cursor})"]
    for m in messages:
        reply_info = f" (reply to #{m['reply_to']})" if m.get("reply_to") else ""
        lines.append(f"  [{m['id']}] {m['sender']} -> {m['recipient']}{reply_info}: {m['body']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bin/pipeline team")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command")

    # serve (MCP stdio adapter)
    serve = subparsers.add_parser("serve", help="run one app's stdio MCP adapter")
    serve.add_argument("--member", required=True, choices=MEMBERS)
    serve.add_argument("--repo-root", type=Path, default=Path.cwd())

    # status (CLI)
    status_p = subparsers.add_parser("status", help="show team status and pending counts")
    status_p.add_argument("--member", choices=MEMBERS, default="agy")
    status_p.add_argument("--repo-root", type=Path, default=Path.cwd())
    status_p.add_argument("--json", action="store_true", help="output JSON")

    # send (CLI)
    send_p = subparsers.add_parser("send", help="send a message over the team transport")
    send_p.add_argument("--to", required=True, choices=RECIPIENTS, dest="recipient", help="recipient member or 'all'")
    send_p.add_argument("--body", required=True, help="message body text")
    send_p.add_argument("--key", required=True, dest="idempotency_key", help="unique sender-scoped idempotency key")
    send_p.add_argument("--reply-to", type=int, default=None, help="message ID this replies to")
    send_p.add_argument("--member", choices=MEMBERS, default="agy", help="sending member label (default: agy)")
    send_p.add_argument("--repo-root", type=Path, default=Path.cwd())
    send_p.add_argument("--json", action="store_true", help="output JSON")

    # wait (CLI)
    wait_p = subparsers.add_parser("wait", help="read messages after cursor and acknowledge")
    wait_p.add_argument("--after-id", type=int, default=0, help="read messages after this ID (default: 0)")
    wait_p.add_argument("--limit", type=int, default=50, help="maximum messages to return (default: 50)")
    wait_p.add_argument("--wait-seconds", type=float, default=0.0, help="seconds to wait for new messages (default: 0)")
    wait_p.add_argument("--member", choices=MEMBERS, default="agy", help="reading member label (default: agy)")
    wait_p.add_argument("--repo-root", type=Path, default=Path.cwd())
    wait_p.add_argument("--json", action="store_true", help="output JSON")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "serve":
        try:
            member = (
                _DiscoveryTeam(args.member)
                if os.environ.get("PIPELINE_TEAM_DISCOVERY_ONLY") == "1"
                else Team(args.repo_root, args.member)
            )
        except (TeamError, OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
            print(f"bin/pipeline team: {exc}", file=sys.stderr)
            return 2
        return McpServer(member).serve()

    try:
        team_inst = Team(args.repo_root, args.member)
        if args.command == "status":
            res = team_inst.status()
            if args.json:
                print(json.dumps(res, indent=2, sort_keys=True))
            else:
                print(_format_status(res))
            return 0

        if args.command == "send":
            res = team_inst.send(
                args.recipient,
                args.body,
                idempotency_key=args.idempotency_key,
                reply_to=args.reply_to,
            )
            if args.json:
                print(json.dumps(res, indent=2, sort_keys=True))
            else:
                print(f"Message {res['id']} {res.get('state', 'queued')} [{res['sender']} -> {res['recipient']}]: {res['idempotency_key']}")
            return 0

        if args.command == "wait":
            res = team_inst.wait(
                after_id=args.after_id,
                limit=args.limit,
                wait_seconds=args.wait_seconds,
            )
            if args.json:
                print(json.dumps(res, indent=2, sort_keys=True))
            else:
                print(_format_wait(res))
            return 0

    except (TeamError, OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(f"bin/pipeline team: {exc}", file=sys.stderr)
        return 2

    return 0


class _DiscoveryTeam:
    """Schema-only member used by read-only native discovery."""

    def __init__(self, member: str) -> None:
        self.member = member

    @staticmethod
    def _unavailable(*_args, **_kwargs):
        raise TeamError("team operations are disabled during read-only discovery")

    status = send = wait = _unavailable


if __name__ == "__main__":
    raise SystemExit(main())
