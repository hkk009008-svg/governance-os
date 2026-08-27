"""Operational MCP handshake controls for the desktop-app preflight."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

import harness_preflight as preflight


def test_checked_in_adapters_complete_real_handshakes(repo_root: Path) -> None:
    results = preflight.check_team_handshakes(repo_root)

    assert all(result.ok for result in results), [result.detail for result in results]
    assert {result.harness for result in results} == {"codex", "claude", "agy"}


def test_handshake_waits_for_initialize_response_before_later_frames(
    tmp_path: Path,
) -> None:
    server = tmp_path / "strict_server.py"
    server.write_text(
        """import json
import select
import sys

initialize = json.loads(sys.stdin.readline())
if select.select([sys.stdin], [], [], 0.05)[0]:
    print(json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -1}}), flush=True)
    raise SystemExit(7)
print(json.dumps({"jsonrpc": "2.0", "id": initialize["id"], "result": {}}), flush=True)
json.loads(sys.stdin.readline())
listed = json.loads(sys.stdin.readline())
print(json.dumps({"jsonrpc": "2.0", "id": listed["id"], "result": {"tools": []}}), flush=True)
status = json.loads(sys.stdin.readline())
print(json.dumps({"jsonrpc": "2.0", "id": status["id"], "result": {}}), flush=True)
""",
        encoding="utf-8",
    )

    completed = preflight._run_handshake(
        [sys.executable, str(server)], cwd=tmp_path, env=dict(os.environ)
    )

    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout.splitlines()) == 3


def test_operational_handshake_strips_ambient_discovery_only_mode(
    repo_root: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_handshake = preflight._run_handshake
    observed: list[dict[str, str]] = []

    def run(argv, **kwargs):
        observed.append(kwargs["env"])
        return real_handshake(argv, **kwargs)

    monkeypatch.setenv("PIPELINE_TEAM_DISCOVERY_ONLY", "1")
    monkeypatch.setattr(preflight, "_run_handshake", run)

    rows = preflight.check_team_handshakes(repo_root)

    assert all(row.ok for row in rows), [row.detail for row in rows]
    assert len(observed) == 3
    assert all("PIPELINE_TEAM_DISCOVERY_ONLY" not in env for env in observed)


def test_empty_success_is_a_handshake_failure(repo_root: Path, monkeypatch) -> None:
    class Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(preflight, "_run_handshake", lambda *_a, **_k: Completed())

    results = preflight.check_team_handshakes(repo_root)

    assert all(not result.ok for result in results)
    assert all("empty" in result.detail for result in results)


def test_malformed_json_rpc_shapes_fail_closed_without_crashing() -> None:
    ok, detail = preflight._handshake_valid("[]\n[]\n", "codex")
    assert not ok and "JSON-RPC" in detail

    initialized = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "serverInfo": {"name": "pipeline-team"},
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
        },
    }
    missing_version = dict(initialized)
    missing_version["result"] = {}
    assert "serverInfo" in preflight._handshake_valid(
        json.dumps(missing_version), "codex"
    )[1]
    without_jsonrpc = dict(initialized)
    without_jsonrpc.pop("jsonrpc")
    assert preflight._handshake_valid(
        json.dumps(without_jsonrpc), "codex"
    )[1] == "response is not JSON-RPC 2.0"
    assert "expected three" in preflight._handshake_valid(
        json.dumps(initialized), "codex"
    )[1]

    listed = {"jsonrpc": "2.0", "id": 2, "result": {"tools": [None]}}
    called = {"jsonrpc": "2.0", "id": 3, "result": {}}
    ok, detail = preflight._handshake_valid(
        "\n".join(map(json.dumps, (initialized, listed, called))), "codex"
    )
    assert not ok and "tool definitions" in detail
