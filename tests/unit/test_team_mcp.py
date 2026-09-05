"""End-to-end stdio MCP behavior for Codex, Claude, and AGY."""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

import team
import team_mcp
from team_test_support import McpProcess, git, make_repo


@pytest.fixture
def team_repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


def test_linked_worktrees_share_one_store(team_repo: Path, tmp_path: Path) -> None:
    linked = tmp_path / "linked"
    git(team_repo, "worktree", "add", "-q", "--detach", str(linked), "HEAD")
    try:
        sender = team.Team(team_repo, "codex")
        receiver = team.Team(linked, "claude")
        assert sender.store_path == receiver.store_path
        queued = sender.send("claude", "shared", idempotency_key="worktree")
        assert receiver.wait()["messages"][0]["id"] == queued["id"]
    finally:
        git(team_repo, "worktree", "remove", "--force", str(linked))


def test_three_stdio_mcp_apps_complete_round_trip(team_repo: Path) -> None:
    apps = [McpProcess(team_repo, member) for member in team.MEMBERS]
    codex, claude, agy = apps
    try:
        assert [tool["name"] for tool in codex.request("tools/list")["tools"]] == [
            "team_status", "team_send", "team_wait"
        ]
        first = codex.tool(
            "team_send",
            {"recipient": "claude", "body": "review", "idempotency_key": "chain-1"},
        )
        claude.tool("team_wait")
        reply = claude.tool(
            "team_send",
            {
                "recipient": "codex",
                "body": "reviewed",
                "reply_to": first["id"],
                "idempotency_key": "chain-2",
            },
        )
        codex.tool("team_wait", {"after_id": first["id"]})
        broadcast = codex.tool(
            "team_send",
            {
                "recipient": "all",
                "body": "accepted context",
                "idempotency_key": "chain-3",
            },
        )
        assert broadcast["id"] > reply["id"]
        assert agy.tool("team_wait")["messages"][-1]["body"] == "accepted context"
        agy_reply = agy.tool(
            "team_send",
            {
                "recipient": "codex",
                "body": "challenge complete",
                "reply_to": broadcast["id"],
                "idempotency_key": "chain-4",
            },
        )
        assert codex.tool("team_wait", {"after_id": broadcast["id"]})["messages"][0][
            "id"
        ] == agy_reply["id"]
    finally:
        for app in apps:
            app.close()


def test_stdio_status_compaction_and_own_message_readback(team_repo: Path) -> None:
    codex = McpProcess(team_repo, "codex")
    try:
        schema = codex.request("tools/list")["tools"][0]["inputSchema"]
        assert set(schema["properties"]) == {"message_id"}
        assert {key: schema["properties"]["message_id"][key] for key in (
            "type", "minimum", "maximum"
        )} == {
            "type": "integer", "minimum": 1, "maximum": team.MAX_MESSAGE_ID,
        }
        body = "🙂large message " * 800
        queued = codex.tool("team_send", {
            "recipient": "claude", "body": body, "idempotency_key": "status-full",
        })
        wire = codex.request("tools/call", {"name": "team_status", "arguments": {}})
        assert body not in json.dumps(wire, ensure_ascii=False)
        assert len(json.dumps(wire, ensure_ascii=False).encode()) < 6000
        summary = wire["structuredContent"]["sent"][0]
        assert "body" not in summary
        assert summary["body_bytes"] == len(body.encode())
        full = codex.tool("team_status", {"message_id": queued["id"]})
        assert full["sent"][0]["body"] == body
        assert full["sent"][0]["grants_authority"] is False
        assert full["identity_assurance"] == team.IDENTITY_ASSURANCE
        inbound = team.Team(team_repo, "claude").send("codex", "unread", idempotency_key="inbound")
        for arguments in (
            {"message_id": inbound["id"]}, {"message_id": True},
            {"message_id": None},
            {"message_id": queued["id"], "member": "claude"},
        ):
            rejected = codex.request("tools/call", {"name": "team_status", "arguments": arguments})
            assert rejected["isError"] is True
            assert "unread" not in rejected["content"][0]["text"]
        assert codex.tool("team_wait")["messages"][0]["id"] == inbound["id"]
    finally:
        codex.close()


def test_mcp_identity_is_not_a_tool_argument(team_repo: Path) -> None:
    codex = McpProcess(team_repo, "codex")
    try:
        called = codex.request(
            "tools/call",
            {
                "name": "team_send",
                "arguments": {
                    "sender": "claude",
                    "recipient": "agy",
                    "body": "spoof",
                    "idempotency_key": "spoof",
                },
            },
        )
        assert called["isError"] is True
        assert "sender" in called["content"][0]["text"]
        assert team.Team(team_repo, "agy").wait()["messages"] == []
    finally:
        codex.close()


def test_flushed_wait_replays_after_client_session_ends_before_cursor_advance(
    team_repo: Path,
) -> None:
    sent = team.Team(team_repo, "codex").send(
        "claude", "replay after flush", idempotency_key="after-flush"
    )
    first = McpProcess(team_repo, "claude")
    try:
        flushed = first.tool("team_wait", {"after_id": 0})
        assert flushed["messages"][0]["id"] == sent["id"]
    finally:
        first.close()

    restarted = McpProcess(team_repo, "claude")
    try:
        replayed = restarted.tool("team_wait", {"after_id": 0})
        assert replayed["messages"][0]["id"] == sent["id"]
        assert restarted.tool("team_wait", {"after_id": sent["id"]})[
            "messages"
        ] == []
    finally:
        restarted.close()


def test_wait_rejects_cursor_beyond_log_without_skipping_future_message(
    team_repo: Path,
) -> None:
    claude = McpProcess(team_repo, "claude")
    try:
        rejected = claude.request(
            "tools/call",
            {"name": "team_wait", "arguments": {"after_id": 1}},
        )
        assert rejected["isError"] is True
        assert "beyond the current message log" in rejected["content"][0]["text"]
        sent = team.Team(team_repo, "codex").send(
            "claude", "still visible", idempotency_key="after-bad-cursor"
        )
        assert claude.tool("team_wait", {"after_id": 0})["messages"][0]["id"] == sent["id"]
    finally:
        claude.close()


def test_wait_rejects_sent_id_that_would_skip_unread_inbound_message(
    team_repo: Path,
) -> None:
    inbound = team.Team(team_repo, "agy").send(
        "codex", "must remain visible", idempotency_key="mcp-unread"
    )
    codex = McpProcess(team_repo, "codex")
    try:
        outbound = codex.tool(
            "team_send",
            {
                "recipient": "claude",
                "body": "later outbound",
                "idempotency_key": "mcp-outbound",
            },
        )
        rejected = codex.request(
            "tools/call",
            {"name": "team_wait", "arguments": {"after_id": outbound["id"]}},
        )
        assert rejected["isError"] is True
        assert "skip unread addressed messages" in rejected["content"][0]["text"]
        assert codex.tool("team_wait", {"after_id": 0})["messages"][0]["id"] == inbound[
            "id"
        ]
    finally:
        codex.close()


def test_mcp_requires_initialize_then_initialized_notification(team_repo: Path) -> None:
    server = team.McpServer(team.Team(team_repo, "codex"))
    early = server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert early is not None and "error" in early

    initialized = server.dispatch(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "initialize",
            "params": {
                "protocolVersion": team.MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "1"},
            },
        }
    )
    assert initialized is not None and "result" in initialized
    not_ready = server.dispatch(
        {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
    )
    assert not_ready is not None and "error" in not_ready

    assert server.dispatch(
        {"jsonrpc": "2.0", "method": "notifications/initialized"}
    ) is None
    listed = server.dispatch({"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
    assert listed is not None and "result" in listed


def test_tool_schema_matches_configured_adapter_constraints(team_repo: Path) -> None:
    codex = McpProcess(team_repo, "codex")
    try:
        tools = {item["name"]: item for item in codex.request("tools/list")["tools"]}
        send = tools["team_send"]["inputSchema"]
        assert send["properties"]["recipient"]["enum"] == ["claude", "agy", "all"]
        assert "idempotency_key" in send["required"]
        assert send["properties"]["idempotency_key"]["pattern"]
        assert send["properties"]["reply_to"]["maximum"] == team.MAX_MESSAGE_ID
        assert team.MAX_MESSAGE_ID == (1 << 53) - 1
        wait = tools["team_wait"]["inputSchema"]
        assert wait["properties"]["after_id"]["maximum"] == team.MAX_MESSAGE_ID

        missing_key = codex.request(
            "tools/call",
            {
                "name": "team_send",
                "arguments": {"recipient": "claude", "body": "unsafe retry"},
            },
        )
        assert missing_key["isError"] is True

        null_key = codex.request(
            "tools/call",
            {
                "name": "team_send",
                "arguments": {
                    "recipient": "claude",
                    "body": "unsafe retry",
                    "idempotency_key": None,
                },
            },
        )
        assert null_key["isError"] is True
        assert team.Team(team_repo, "claude").wait()["messages"] == []
    finally:
        codex.close()


def test_oversized_message_ids_are_tool_errors_and_server_survives(
    team_repo: Path,
) -> None:
    codex = McpProcess(team_repo, "codex")
    try:
        oversized_reply = codex.request(
            "tools/call",
            {
                "name": "team_send",
                "arguments": {
                    "recipient": "claude",
                    "body": "must not crash",
                    "idempotency_key": "oversized-reply",
                    "reply_to": team.MAX_MESSAGE_ID + 1,
                },
            },
        )
        assert oversized_reply["isError"] is True
        assert "reply_to" in oversized_reply["content"][0]["text"]
        assert codex.request("ping") == {}

        oversized_cursor = codex.request(
            "tools/call",
            {
                "name": "team_wait",
                "arguments": {"after_id": team.MAX_MESSAGE_ID + 1},
            },
        )
        assert oversized_cursor["isError"] is True
        assert "after_id" in oversized_cursor["content"][0]["text"]
        assert codex.request("ping") == {}
    finally:
        codex.close()


def test_exhausted_database_id_space_is_a_tool_error_not_process_exit(
    team_repo: Path,
) -> None:
    first = team.Team(team_repo, "agy").send(
        "claude", "seed sequence", idempotency_key="seed-sequence"
    )
    connection = sqlite3.connect(team.Team(team_repo, "agy").store_path)
    try:
        connection.execute(
            "UPDATE sqlite_sequence SET seq=? WHERE name='messages'",
            (team.MAX_MESSAGE_ID,),
        )
        connection.commit()
    finally:
        connection.close()

    agy = McpProcess(team_repo, "agy")
    try:
        rejected = agy.request(
            "tools/call",
            {
                "name": "team_send",
                "arguments": {
                    "recipient": "claude",
                    "body": "must remain portable",
                    "idempotency_key": "past-json-limit",
                },
            },
        )
        assert rejected["isError"] is True
        assert "JSON-safe" in rejected["content"][0]["text"]
        assert agy.request("ping") == {}
        assert team.Team(team_repo, "claude").wait()["messages"][0]["id"] == first["id"]
    finally:
        agy.close()


def test_discovery_only_handshake_does_not_create_or_touch_team_state(
    team_repo: Path,
) -> None:
    environment = {
        key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"
    }
    environment["PIPELINE_TEAM_DISCOVERY_ONLY"] = "1"
    requests = (
        {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": team.MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "team_status", "arguments": {}},
        },
    )
    completed = subprocess.run(
        [
            sys.executable, str(Path(team.__file__).resolve()), "serve",
            "--repo-root", str(team_repo), "--member", "claude",
        ],
        input="".join(json.dumps(item) + "\n" for item in requests),
        capture_output=True, text=True, env=environment, timeout=10, check=False,
    )

    assert completed.returncode == 0, completed.stderr
    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert [item["id"] for item in responses] == [1, 2, 3]
    assert [tool["name"] for tool in responses[1]["result"]["tools"]] == [
        "team_status", "team_send", "team_wait"
    ]
    assert responses[2]["result"]["isError"] is True
    common = Path(git(team_repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    assert not (common / "pipeline-team").exists()


def test_oversized_request_tail_cannot_execute_as_a_second_request(
    team_repo: Path,
) -> None:
    codex = McpProcess(team_repo, "codex")
    try:
        malicious = {
            "jsonrpc": "2.0",
            "id": 999,
            "method": "tools/call",
            "params": {
                "name": "team_send",
                "arguments": {
                    "recipient": "claude",
                    "body": "must not execute",
                    "idempotency_key": "oversized-tail",
                },
            },
        }
        assert codex.process.stdin is not None
        codex.process.stdin.write(
            "x" * (team_mcp._MAX_LINE_BYTES + 1)
            + json.dumps(malicious, separators=(",", ":"))
            + "\n"
        )
        codex.process.stdin.flush()
        assert codex.process.stdout is not None
        rejected = json.loads(codex.process.stdout.readline())
        assert rejected["error"]["message"] == "request line too large"

        # The server remains usable, but the JSON tail above was discarded.
        assert codex.request("ping") == {}
        assert team.Team(team_repo, "claude").wait()["messages"] == []
    finally:
        codex.close()
