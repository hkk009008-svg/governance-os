"""Unit tests for bin/pipeline team CLI subcommands."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import team
from team_test_support import git, make_repo


@pytest.fixture
def team_repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


def _run_team(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = {
        key: value for key, value in sys.modules["os"].environ.items() if key != "GIT_INDEX_FILE"
    }
    return subprocess.run(
        [
            sys.executable,
            str(Path(team.__file__).resolve()),
            *args,
            "--repo-root",
            str(repo),
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )


def test_team_cli_help(team_repo: Path) -> None:
    for cmd in ([], ["status", "--help"], ["send", "--help"], ["wait", "--help"], ["serve", "--help"]):
        result = _run_team(team_repo, *cmd)
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()


def test_team_cli_status(team_repo: Path) -> None:
    # Text output
    result = _run_team(team_repo, "status", "--member", "agy")
    assert result.returncode == 0
    assert "Member: agy" in result.stdout
    assert "Active team members:" in result.stdout

    # JSON output
    result_json = _run_team(team_repo, "status", "--member", "agy", "--json")
    assert result_json.returncode == 0
    payload = json.loads(result_json.stdout)
    assert payload["member"] == "agy"
    assert "members" in payload


def test_team_cli_send_and_wait_roundtrip(team_repo: Path) -> None:
    # 1. Send a message from agy to codex
    send_res = _run_team(
        team_repo,
        "send",
        "--member", "agy",
        "--to", "codex",
        "--body", "test message from agy",
        "--key", "cli-test-key-1",
        "--json",
    )
    assert send_res.returncode == 0
    msg = json.loads(send_res.stdout)
    assert msg["sender"] == "agy"
    assert msg["recipient"] == "codex"
    assert msg["body"] == "test message from agy"
    msg_id = msg["id"]

    # 2. Re-send with same key -> already-queued
    send_res_dup = _run_team(
        team_repo,
        "send",
        "--member", "agy",
        "--to", "codex",
        "--body", "test message from agy",
        "--key", "cli-test-key-1",
        "--json",
    )
    assert send_res_dup.returncode == 0
    msg_dup = json.loads(send_res_dup.stdout)
    assert msg_dup["state"] == "already-queued"

    # 3. Read the message as codex
    wait_res = _run_team(
        team_repo,
        "wait",
        "--member", "codex",
        "--after-id", "0",
        "--json",
    )
    assert wait_res.returncode == 0
    wait_payload = json.loads(wait_res.stdout)
    assert len(wait_payload["messages"]) == 1
    assert wait_payload["messages"][0]["id"] == msg_id
    assert wait_payload["messages"][0]["sender"] == "agy"

    # 4. Human-readable wait output
    wait_text = _run_team(
        team_repo,
        "wait",
        "--member", "codex",
        "--after-id", "0",
    )
    assert wait_text.returncode == 0
    assert f"[{msg_id}] agy -> codex: test message from agy" in wait_text.stdout
