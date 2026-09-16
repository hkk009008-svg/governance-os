from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import git_runner
import status
import check_coordination
from formal_review_support import add_report, add_request, commit, init_repo


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


def test_desktop_readiness_checks_app_bundles_only_where_they_can_exist(
    repo_root, monkeypatch,
) -> None:
    import harness_preflight
    import status_desktop

    monkeypatch.setattr(
        harness_preflight, "check_apps",
        lambda *_a: [harness_preflight.Result(m, False, "missing") for m in MEMBERS],
    )
    monkeypatch.setattr(harness_preflight, "desktop_checks_default", lambda: False)
    off = status_desktop.collect_desktop_readiness(repo_root)
    assert off["apps"] == {} and off["apps_checked"] is False and off["ready"] is True
    assert "not checked" in off["detail"]
    rendered = status.render_orientation_snapshot({
        "generated_at": "now", "git": {"sha": "abc", "branch": "main", "dirty": 0},
        "desktop": off, "team_transport": _transport(), "formal_review": None,
    })
    assert "Apps: not checked on this platform (bin/pipeline preflight --desktop)" in rendered
    assert "App configs: codex=ready claude=ready agy=ready" in rendered

    monkeypatch.setattr(harness_preflight, "desktop_checks_default", lambda: True)
    on = status_desktop.collect_desktop_readiness(repo_root)
    assert set(on["apps"]) == set(MEMBERS) and on["apps_checked"] is True
    assert on["ready"] is False
    forced = status_desktop.collect_desktop_readiness(repo_root, desktop=False)
    assert forced["ready"] is True


def test_render_shows_focus_and_hides_historical_fails_unless_verbose() -> None:
    snapshot = {
        "generated_at": "2026-09-02T00:00:00Z",
        "git": {"sha": "abc", "branch": "main", "dirty": 0},
        "desktop": _desktop(),
        "team_transport": {
            **_transport(),
            "state": "ready",
            "members": {"claude": {"focus": "mapping the gate", "handoff": "private"}},
        },
        "formal_review": {
            "current_request": None,
            "failed_review": None,
            "historical_failed_reviews": [{
                "request_path": "coordination/mailbox/sent/old-request.md",
                "request_commit": "a" * 40,
                "report_path": "coordination/mailbox/sent/old-report.md",
                "report_commit": "b" * 40,
                "reviewer": "claude",
            }],
            "gate": {"status": "WARN", "fatal": 0, "advisory": 1, "failed_review": 0},
            "blocker": None,
            "next_action": "continue scoped team work",
        },
    }
    compact = status.render_orientation_snapshot(snapshot)
    verbose = status.render_orientation_snapshot(snapshot, verbose=True)
    assert "  claude focus: mapping the gate" in compact and "private" not in compact
    assert "Mailbox health: WARN (0 fatal, 1 advisory, 0 failed); details: status --verbose" in compact
    assert "Historical FAIL" not in compact
    assert f"Historical FAIL: coordination/mailbox/sent/old-report.md@{'b' * 40}" in verbose
    assert "details: status --verbose" not in verbose


def test_review_state_cache_hits_only_for_an_identical_repository_fingerprint(
    tmp_path, monkeypatch,
) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request, trigger = add_request(root, base, head)
    add_report(root, request, trigger)
    cache = root / ".git" / status.REVIEW_STATE_CACHE_NAME
    calls: list[tuple] = []
    real = git_runner.run_git

    def counting(*args, **kwargs):
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(git_runner, "run_git", counting)
    monkeypatch.setenv("PIPELINE_STATUS_CACHE", "0")
    assert status._collect_review_state(root)["gate"]["status"] == "PASS"
    assert not cache.exists()

    monkeypatch.setenv("PIPELINE_STATUS_CACHE", "1")
    calls.clear()
    cold = status._collect_review_state(root)
    cold_calls = len(calls)
    calls.clear()
    warm = status._collect_review_state(root)
    assert warm == cold and cold["gate"]["status"] == "PASS"
    assert len(calls) <= 4 < cold_calls
    assert cache.is_file() and os.stat(cache).st_mode & 0o777 == 0o600

    # Tampering with a published artifact in the worktree is a miss, not a stale
    # PASS: first a different-length rewrite, then a same-length rewrite with
    # the timestamp restored, which leaves every stat field unchanged and only
    # a digest of the bytes can catch.
    original = (root / request).read_bytes()
    before = os.stat(root / request)
    (root / request).write_bytes(b"tampered\n")
    calls.clear()
    assert status._collect_review_state(root)["gate"]["status"] == "FAIL"
    assert len(calls) > 4
    (root / request).write_bytes(original)
    assert status._collect_review_state(root)["gate"]["status"] == "PASS"
    evasion = original.replace(b"Review the exact", b"Ignore the exact")
    assert len(evasion) == len(original) and evasion != original
    (root / request).write_bytes(evasion)
    os.utime(root / request, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert os.stat(root / request).st_mtime_ns == before.st_mtime_ns
    assert status._collect_review_state(root)["gate"]["status"] == "FAIL"
    (root / request).write_bytes(original)
    os.utime(root / request, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert status._collect_review_state(root)["gate"]["status"] == "PASS"

    # A new commit is a miss; a corrupt cache file is ignored and replaced.
    commit(root, {"notes.txt": "later\n"}, "later")
    calls.clear()
    assert status._collect_review_state(root)["gate"]["status"] == "PASS"
    assert len(calls) > 4
    cache.write_text("{not json", encoding="utf-8")
    assert status._collect_review_state(root)["gate"]["status"] == "PASS"
    assert json.loads(cache.read_text(encoding="utf-8"))["state"]["pending"] == []


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


def test_all_pending_requests_are_visible_without_a_line_limit(monkeypatch) -> None:
    requests = tuple(
        check_coordination.CurrentVerifyRequest(
            path=f"coordination/mailbox/sent/request-{i:02d}.md", commit="a" * 40,
            reviewer_member="claude" if i % 2 else "codex", valid=True, problem=None,
        ) for i in range(25)
    )
    monkeypatch.setattr(check_coordination, "inspect_verify_review_state", lambda _: check_coordination.VerifyReviewState(requests, ()))
    review = status._collect_review_state(Path("."))
    assert len(review["pending_requests"]) == 25
    rendered = status.render_orientation_snapshot({
        "generated_at": "now", "git": {"sha": "abc", "branch": "main", "dirty": 0},
        "desktop": _desktop(), "team_transport": _transport(), "formal_review": review,
    })
    for request in requests:
        assert request.path in rendered
    assert "25 pending" in rendered
