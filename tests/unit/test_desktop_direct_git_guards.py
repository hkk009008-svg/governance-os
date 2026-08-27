"""Direct Git cannot bypass desktop mailbox admission."""
from __future__ import annotations

import subprocess
from pathlib import Path

import check_coordination as coordination
import mailbox_admission


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _clone(repo_root: Path, tmp_path: Path, name: str) -> Path:
    clone = tmp_path / name
    _git(tmp_path, "clone", "--no-local", "-q", str(repo_root), str(clone))
    _git(clone, "config", "user.name", "Coord Test")
    _git(clone, "config", "user.email", "coord@example.invalid")
    return clone


def test_coordination_run_wires_desktop_admission(tmp_path, monkeypatch) -> None:
    coord = tmp_path / "coordination"
    (coord / "mailbox/sent").mkdir(parents=True)
    sentinel = coordination.CoordIssue(
        "mailbox/sent/refused.md",
        "post_cutover_event_admission",
        "FATAL",
        "refused by committed desktop admission",
    )

    class Commits:
        @staticmethod
        def assert_current():
            return None

    class Projection:
        commits = Commits()

    projection, calls = Projection(), []
    for name in (
        "_check_cursors",
        "_check_events",
        "_unread_report",
        "_check_current_verify_requests",
        "_check_committed_learning_history",
        "_check_coordinator_handoff_theater",
    ):
        monkeypatch.setattr(coordination, name, lambda *_args, **_kwargs: [])

    def gate(*args):
        calls.append(args)
        return [sentinel]

    monkeypatch.setattr(
        mailbox_admission, "check_post_cutover_event_admission", gate
    )
    issues = coordination.run(
        coord,
        review_state=coordination.VerifyReviewState(pending=(), failed=()),
        committed_projection=(projection, None),
    )
    assert issues == [sentinel]
    assert calls == [(
        projection,
        coordination.CoordIssue,
        coordination._ARCHIVE_SENT_PREFIX,
        coordination._projection_git,
        tmp_path,
    )]


def test_remediation_request_cannot_bypass_target_binding(
    repo_root: Path, tmp_path: Path
) -> None:
    clone = _clone(repo_root, tmp_path, "bad-remediation-binding")
    failed_report = (
        "coordination/mailbox/sent/"
        "2026-08-21T22-12-09Z-reviewer-to-author-verification-report.md"
    )
    failed_commit = "1b37caf84372e3f5ebb4d30fe16c38f2da704e17"
    (clone / "candidate.txt").write_text("candidate\n", encoding="utf-8")
    _git(clone, "add", "candidate.txt")
    _git(clone, "commit", "-q", "-m", "remediation candidate")
    head = _git(clone, "rev-parse", "HEAD")
    path = (
        "coordination/mailbox/sent/"
        "2027-01-01T00-00-00Z-author-to-reviewer-verify-request.md"
    )
    (clone / path).write_text(
        f"""\
# Author → Reviewer: malformed remediation binding

**When:** 2027-01-01T00:00:00Z · **From:** author (online)

Event type: verify-request
Reviewed base: {failed_commit}
Reviewed head: {head}
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: material-behavior
Remediates failed report: {failed_report}@{failed_commit}

## Outcome

This deliberately mismatches the failed report's high-risk class.

Cursor at send: cursorless
""",
        encoding="utf-8",
    )
    _git(clone, "add", "-f", path)
    _git(clone, "commit", "-q", "-m", "malformed remediation request")
    projection = coordination.committed_mailbox_projection(clone)
    state = coordination.inspect_verify_review_state(clone, projection_result=projection)
    issues = coordination.run(
        clone / "coordination",
        docs_root=clone / "docs",
        review_state=state,
        committed_projection=projection,
    )
    current = next(item for item in state.pending if item.path == path)
    assert current.valid is False and "Risk class" in (current.problem or "")
    assert any(
        issue.kind == "post_cutover_event_admission"
        and "remediation binding invalid" in issue.message
        for issue in issues
    )


def test_report_cannot_supersede_nonexistent_verdict(
    repo_root: Path, tmp_path: Path
) -> None:
    clone = _clone(repo_root, tmp_path, "bad-supersedes-binding")
    base = _git(clone, "rev-parse", "HEAD")
    (clone / "candidate.txt").write_text("candidate\n", encoding="utf-8")
    _git(clone, "add", "candidate.txt")
    _git(clone, "commit", "-q", "-m", "supersedes candidate")
    head = _git(clone, "rev-parse", "HEAD")
    request_path = (
        "coordination/mailbox/sent/"
        "2027-01-01T00-10-00Z-author-to-reviewer-verify-request.md"
    )
    (clone / request_path).write_text(
        f"""\
# Author → Reviewer: supersession control request

**When:** 2027-01-01T00:10:00Z · **From:** author (online)

Event type: verify-request
Reviewed base: {base}
Reviewed head: {head}
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: material-behavior

## Outcome

Review the exact candidate range.

Cursor at send: cursorless
""",
        encoding="utf-8",
    )
    _git(clone, "add", "-f", request_path)
    _git(clone, "commit", "-q", "-m", "supersession control request")
    request_commit = _git(clone, "rev-parse", "HEAD")
    nonexistent = (
        "coordination/mailbox/sent/"
        "2026-12-31T00-00-00Z-reviewer-to-author-verification-report.md"
    )
    report_path = (
        "coordination/mailbox/sent/"
        "2027-01-01T00-20-00Z-reviewer-to-author-verification-report.md"
    )
    (clone / report_path).write_text(
        f"""\
# Reviewer → Author: invalid supersession

**When:** 2027-01-01T00:20:00Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: NITS
Verification request: {request_path}@{request_commit}
Supersedes: {nonexistent}@{'a' * 40}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: reviewer
Reviewer model: claude-opus-4-6-thinking
Risk class: material-behavior

## Finding Refs

## Finding Dispositions

## Findings

The supersession target does not exist.

Cursor at send: cursorless
""",
        encoding="utf-8",
    )
    _git(clone, "add", "-f", report_path)
    _git(clone, "commit", "-q", "-m", "invalid supersession report")
    projection = coordination.committed_mailbox_projection(clone)
    state = coordination.inspect_verify_review_state(clone, projection_result=projection)
    issues = coordination.run(
        clone / "coordination",
        docs_root=clone / "docs",
        review_state=state,
        committed_projection=projection,
    )
    assert any(item.path == request_path for item in state.pending)
    assert any(
        issue.kind == "post_cutover_event_admission"
        and "report binding is not its exact introduction" in issue.message
        for issue in issues
    )
