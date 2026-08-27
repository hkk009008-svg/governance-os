"""Focused coverage for the live desktop-team status surface."""

import json
import os
import subprocess
from pathlib import Path

import check_coordination as cc
import codex_protocol_model as protocol_model
import status


MEMBERS = ("codex", "claude", "agy")


def _git(repo: Path, *args: str, env=None) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, capture_output=True, text=True,
        check=True,
    ).stdout.strip()


def _init_clean_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "status-test@example.com")
    _git(repo, "config", "user.name", "Status Test")
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "test: initial state")
    return repo


def _desktop_readiness() -> dict:
    rows = {
        member: {"ready": True, "detail": "fixture", "remedy": None}
        for member in MEMBERS
    }
    return {
        "state": "ready", "ready": True, "apps": rows, "manifests": rows,
        "detail": "fixture", "live_handshake": "not-run",
    }


def _absent_team_transport() -> dict:
    return {
        "state": "absent",
        "detail": "not initialized; status did not create it",
        "members": {},
        "pending": {member: 0 for member in MEMBERS},
        "queued_messages": 0,
        "acknowledgement_receipts": 0,
        "reply_messages": 0,
    }


def test_malformed_app_manifests_are_visible_in_desktop_readiness(
    tmp_path: Path, monkeypatch,
) -> None:
    import harness_preflight

    (tmp_path / ".codex").mkdir()
    (tmp_path / ".agents/plugins/pipeline-team").mkdir(parents=True)
    (tmp_path / ".codex/config.toml").write_text("broken = [", encoding="utf-8")
    (tmp_path / ".mcp.json").write_text("{broken", encoding="utf-8")
    (tmp_path / ".agents/plugins/pipeline-team/mcp_config.json").write_text(
        "[]", encoding="utf-8"
    )
    monkeypatch.setattr(
        harness_preflight, "check_apps",
        lambda: [harness_preflight.Result(member, True, "fixture") for member in MEMBERS],
    )

    observed = status.collect_desktop_readiness(tmp_path)

    assert observed["state"] == "needs-attention"
    assert all(not row["ready"] for row in observed["manifests"].values())
    assert all("invalid" in row["detail"] for row in observed["manifests"].values())


def test_collect_git_uses_requested_repo_and_ignores_ambient_index(
    tmp_path: Path, monkeypatch,
) -> None:
    repo = _init_clean_repo(tmp_path)
    expected = _git(repo, "rev-parse", "--short", "HEAD")
    alternate_index = tmp_path / "seat.index"
    alternate_env = os.environ.copy()
    alternate_env["GIT_INDEX_FILE"] = str(alternate_index)
    _git(repo, "read-tree", "--empty", env=alternate_env)
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    monkeypatch.setenv("GIT_INDEX_FILE", str(alternate_index))

    result = status.collect_git(repo)

    assert result == {"git_sha": expected, "git_branch": "main", "git_dirty": 0}


def test_live_review_filter_keeps_only_post_cutover_formal_artifacts() -> None:
    cutover = protocol_model.CURRENT_REVIEW_FAMILY_CUTOVER
    historical, request_commit, report_commit = "a" * 40, "c" * 40, "d" * 40

    class Commits:
        def require_commit(self, value, _label):
            if value not in {historical, cutover, request_commit, report_commit}:
                raise ValueError("unknown commit")
            return value

        @staticmethod
        def is_ancestor(ancestor, descendant):
            live = {request_commit, report_commit}
            if ancestor == descendant:
                return True
            if ancestor == historical:
                return descendant in {cutover, *live}
            return ancestor == cutover and descendant in live or (
                ancestor == request_commit and descendant == report_commit
            )

    def request(stamp: str, commit: str) -> cc.CurrentVerifyRequest:
        return cc.CurrentVerifyRequest(
            path=(
                "coordination/mailbox/sent/"
                f"{stamp}-author-to-reviewer-verify-request.md"
            ),
            commit=commit, assigned_operator="reviewer", valid=True, problem=None,
        )

    old, live = request("2026-08-20T12-00-00Z", historical), request(
        "2026-08-27T12-00-00Z", request_commit
    )
    old_fail = cc.FailedVerifyRequest(
        old.path, historical,
        "coordination/mailbox/sent/2026-08-20T12-10-00Z-reviewer-to-all-verification-report.md",
        cutover, "reviewer",
    )
    live_fail = cc.FailedVerifyRequest(
        live.path, request_commit,
        "coordination/mailbox/sent/2026-08-27T12-10-00Z-reviewer-to-all-verification-report.md",
        report_commit, "reviewer",
    )

    filtered = status._live_review_state(
        cc.VerifyReviewState(
            pending=(old, live), failed=(old_fail, live_fail),
            grandfathered_history=("fixture",),
        ),
        type("Projection", (), {"commits": Commits()})(),
    )

    assert filtered.pending == (live,)
    assert filtered.failed == (live_fail,)
    assert filtered.problem is None
    assert filtered.grandfathered_history == ()


def test_default_snapshot_combines_live_sources(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        status, "collect_git",
        lambda _root: {"git_sha": "abc1234", "git_branch": "test", "git_dirty": 0},
    )
    monkeypatch.setattr(status, "collect_desktop_readiness", lambda _root: _desktop_readiness())
    monkeypatch.setattr(status, "collect_team_transport", lambda _root: _absent_team_transport())
    review = {
        "current_request": None, "failed_review": None,
        "gate": {"status": "PASS", "fatal": 0, "advisory": 0, "failed_review": 0},
        "blocker": None, "next_action": "continue scoped team work",
    }
    calls = []

    def collect_review(*args):
        calls.append(args)
        return review, None

    monkeypatch.setattr(status, "_collect_review_state", collect_review)

    snapshot = status.collect_orientation_snapshot(tmp_path)

    assert set(snapshot) == {
        "generated_at", "git", "desktop", "team_transport", "formal_review"
    }
    assert snapshot["formal_review"] == review
    assert calls == [(tmp_path, {"git_sha": "abc1234", "git_branch": "test", "git_dirty": 0})]


def test_compact_render_foregrounds_apps_messages_and_formal_gate() -> None:
    snapshot = {
        "generated_at": "2026-07-25T00:00:00Z",
        "git": {"sha": "abc1234", "branch": "main", "dirty": 2},
        "desktop": _desktop_readiness(),
        "team_transport": {
            "state": "ready", "members": {"codex": {"last_seen": "fixture"}},
            "pending": {"codex": 1, "claude": 2, "agy": 3},
            "queued_messages": 7, "acknowledgement_receipts": 4,
            "reply_messages": 2,
        },
        "formal_review": {
            "current_request": None, "failed_review": None,
            "gate": {"status": "PASS", "fatal": 0, "advisory": 0, "failed_review": 0},
            "blocker": None, "next_action": "continue scoped team work",
        },
    }

    rendered = status.render_orientation_snapshot(snapshot)

    assert "Apps: codex=ready claude=ready agy=ready" in rendered
    assert "pending[codex=1 claude=2 agy=3]" in rendered
    assert "queued=7 acknowledgement-receipts=4 reply-messages=2" in rendered
    assert "Formal review: none" in rendered
    assert "Formal gate: PASS" in rendered


def test_json_cli_emits_machine_readable_snapshot(monkeypatch, capsys) -> None:
    snapshot = {
        "generated_at": "2026-07-25T00:00:00Z",
        "git": {"sha": "abc1234", "branch": "main", "dirty": 0},
        "desktop": _desktop_readiness(), "team_transport": _absent_team_transport(),
    }
    monkeypatch.setattr(status, "collect_orientation_snapshot", lambda _root: snapshot)

    assert status.main(["--json"]) == 0
    assert json.loads(capsys.readouterr().out)["git"]["sha"] == "abc1234"
