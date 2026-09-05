from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import status
import check_coordination


MEMBERS = ("codex", "claude", "agy")


def _git(repo: Path, *args: str, env=None) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, capture_output=True, text=True, check=True
    ).stdout.strip()


def _desktop() -> dict:
    rows = {member: {"ready": True, "detail": "fixture", "remedy": None} for member in MEMBERS}
    return {
        "state": "ready",
        "ready": True,
        "apps": rows,
        "manifests": rows,
        "detail": "fixture",
        "live_handshake": "not-run",
    }


def _transport() -> dict:
    return {
        "state": "absent",
        "detail": "not initialized",
        "members": {},
        "pending": {member: 0 for member in MEMBERS},
        "queued_messages": 0,
        "acknowledgement_receipts": 0,
        "reply_messages": 0,
    }


def test_collect_git_uses_requested_repo_and_ignores_ambient_index(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    alternate = tmp_path / "alternate.index"
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(alternate)
    _git(repo, "read-tree", "--empty", env=env)
    monkeypatch.setenv("GIT_INDEX_FILE", str(alternate))
    result = status.collect_git(repo)
    assert result["git_branch"] == "main" and result["git_dirty"] == 0


def test_snapshot_combines_the_four_live_sources(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(status, "collect_git", lambda _root: {"git_sha": "abc", "git_branch": "main", "git_dirty": 0})
    monkeypatch.setattr(status, "collect_desktop_readiness", lambda _root: _desktop())
    monkeypatch.setattr(status, "collect_team_transport", lambda _root: _transport())
    review = {
        "current_request": None,
        "failed_review": None,
        "gate": {"status": "PASS", "fatal": 0, "advisory": 0, "failed_review": 0},
        "blocker": None,
        "next_action": "continue scoped team work",
    }
    monkeypatch.setattr(status, "_collect_review_state", lambda *_args: review)
    snapshot = status.collect_orientation_snapshot(tmp_path)
    assert set(snapshot) == {"generated_at", "git", "desktop", "team_transport", "formal_review"}
    assert snapshot["formal_review"] == review


def test_render_foregrounds_apps_transport_and_formal_gate() -> None:
    snapshot = {
        "generated_at": "2026-09-02T00:00:00Z",
        "git": {"sha": "abc", "branch": "main", "dirty": 0},
        "desktop": _desktop(),
        "team_transport": {
            **_transport(),
            "state": "ready",
            "pending": {"codex": 1, "claude": 2, "agy": 0},
        },
        "formal_review": {
            "current_request": None,
            "failed_review": None,
            "gate": {"status": "PASS", "fatal": 0, "advisory": 0, "failed_review": 0},
            "blocker": None,
            "next_action": "continue scoped team work",
        },
    }
    rendered = status.render_orientation_snapshot(snapshot)
    assert "Apps: codex=ready claude=ready agy=ready" in rendered
    assert "pending[codex=1 claude=2 agy=0]" in rendered
    assert "Mailbox health: PASS" in rendered
    assert "Integration admission: not run" in rendered


def test_pending_request_uses_current_reviewer_field(monkeypatch) -> None:
    pending = check_coordination.CurrentVerifyRequest(
        path="coordination/mailbox/sent/request.md",
        commit="a" * 40,
        reviewer_member="claude",
        valid=True,
        problem=None,
        reviewed_base="b" * 40,
        reviewed_head="c" * 40,
    )
    state = check_coordination.VerifyReviewState((pending,), ())
    monkeypatch.setattr(check_coordination, "inspect_verify_review_state", lambda _root: state)
    monkeypatch.setattr(check_coordination, "run", lambda *_args, **_kwargs: [])
    observed = status._collect_review_state(Path("."))
    assert observed["current_request"]["reviewer"] == "claude"
    assert "claude reviews" in observed["next_action"]


def test_json_cli_is_machine_readable(monkeypatch, capsys) -> None:
    snapshot = {"git": {"sha": "abc"}}
    monkeypatch.setattr(status, "collect_orientation_snapshot", lambda _root: snapshot)
    assert status.main(["--json"]) == 0
    assert json.loads(capsys.readouterr().out) == snapshot
