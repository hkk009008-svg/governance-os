"""Current desktop model and target-repository review-state controls."""
from __future__ import annotations

import subprocess
from pathlib import Path

import check_coordination as coordination
import status


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


def test_unknown_author_model_is_invalid_in_state_and_status(
    repo_root: Path, tmp_path: Path
) -> None:
    clone = _clone(repo_root, tmp_path, "current-author-model")
    base = _git(clone, "rev-parse", "HEAD")
    (clone / "desktop-model-control.txt").write_text("candidate\n", encoding="utf-8")
    _git(clone, "add", "desktop-model-control.txt")
    _git(clone, "commit", "-q", "-m", "candidate range")
    head = _git(clone, "rev-parse", "HEAD")
    path = (
        "coordination/mailbox/sent/"
        "2026-12-31T23-59-00Z-codex-to-claude-verify-request.md"
    )
    (clone / path).write_text(
        f"""\
# Codex → Claude: current model admission control

**When:** 2026-12-31T23:59:00Z · **From:** codex (online)

Event type: verify-request
Reviewed base: {base}
Reviewed head: {head}
Author seat: codex
Author model: retired-unknown-model
Assigned operator: claude
Risk class: material-behavior

## Outcome

Prove current review state refuses an unknown author model.

Cursor at send: cursorless
""",
        encoding="utf-8",
    )
    _git(clone, "add", "-f", path)
    _git(clone, "commit", "-q", "-m", "invalid current author model")

    state = coordination.inspect_verify_review_state(clone)
    current = next(item for item in state.pending if item.path == path)
    review, _ = status._collect_review_state(clone, status.collect_git(clone))
    assert state.problem is None
    assert current.valid is False
    assert "currently admitted author model" in (current.problem or "")
    assert review["current_request"]["path"] == path
    assert review["current_request"]["valid"] is False
    assert review["gate"]["status"] == "FAIL"


def test_cross_repository_request_and_report_use_target_git_objects(
    repo_root: Path, tmp_path: Path
) -> None:
    target = (tmp_path / "target-repository").resolve()
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.name", "Target Test")
    _git(target, "config", "user.email", "target@example.invalid")
    (target / "payload.txt").write_text("base\n", encoding="utf-8")
    _git(target, "add", "payload.txt")
    _git(target, "commit", "-q", "-m", "target base")
    base = _git(target, "rev-parse", "HEAD")
    (target / "payload.txt").write_text("head\n", encoding="utf-8")
    _git(target, "add", "payload.txt")
    _git(target, "commit", "-q", "-m", "target head")
    head = _git(target, "rev-parse", "HEAD")

    clone = _clone(repo_root, tmp_path, "cross-repository-harness")
    request_path = (
        "coordination/mailbox/sent/"
        "2026-12-31T23-58-00Z-codex-to-claude-verify-request.md"
    )
    (clone / request_path).write_text(
        f"""\
# Codex → Claude: cross-repository request

**When:** 2026-12-31T23:58:00Z · **From:** codex (online)

Event type: verify-request
Reviewed repository: {target}
Reviewed base: {base}
Reviewed head: {head}
Author seat: codex
Author model: gpt-5.6-sol
Assigned operator: claude
Risk class: material-behavior

## Outcome

Review the target repository's exact committed range.

Cursor at send: cursorless
""",
        encoding="utf-8",
    )
    _git(clone, "add", "-f", request_path)
    _git(clone, "commit", "-q", "-m", "cross-repository verify request")
    request_commit = _git(clone, "rev-parse", "HEAD")
    state = coordination.inspect_verify_review_state(clone)
    current = next(item for item in state.pending if item.path == request_path)
    assert state.problem is None and current.valid is True
    assert current.reviewed_repository == str(target)

    report_path = (
        "coordination/mailbox/sent/"
        "2026-12-31T23-59-00Z-claude-to-codex-verification-report.md"
    )
    (clone / report_path).write_text(
        f"""\
# Claude → Codex: cross-repository report

**When:** 2026-12-31T23:59:00Z · **From:** claude (online)

Event type: verification-report
VERDICT: NITS
Verification request: {request_path}@{request_commit}
Reviewed repository: {target}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: claude
Reviewer model: claude-opus-4-6-thinking
Risk class: material-behavior

## Finding Refs

## Finding Dispositions

## Findings

No blocking findings.

Cursor at send: cursorless
""",
        encoding="utf-8",
    )
    _git(clone, "add", "-f", report_path)
    _git(clone, "commit", "-q", "-m", "cross-repository review report")
    reviewed = coordination.inspect_verify_review_state(clone)
    review, _ = status._collect_review_state(clone, status.collect_git(clone))
    assert all(item.path != request_path for item in reviewed.pending)
    assert review["current_request"] is None
    assert review["gate"]["status"] == "PASS"
