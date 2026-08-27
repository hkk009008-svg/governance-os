"""Committed payloads never fall back to mutable publication candidates."""
from __future__ import annotations

import subprocess
from pathlib import Path

import mailbox_writer
from mailbox_admission_test_support import (
    APP_FINDINGS,
    ORPHAN_REPORT,
    event,
    run_gate,
)


def test_checkpoint_replay_avoids_publication_validator(
    monkeypatch, repo_root: Path
) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    body = f"""\
Checkpoint: committed-replay
Boundary: wrap
Objective: prove committed replay is independent of dirty candidates
Accepted scope: the desktop admission gate
Owner: codex
Policy revision: {head}
Base: {head}
Head: {head}
Evidence refs: none
Verification status: focused control is green
Blockers: none
Next action: keep using committed projections
Lessons: none-considered
"""
    monkeypatch.setattr(
        mailbox_writer,
        "validate_event_candidate_bytes",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("committed replay called publication validation")
        ),
    )
    issues = run_gate(
        monkeypatch,
        {APP_FINDINGS: event(APP_FINDINGS, body)},
        {},
        {APP_FINDINGS: "8" * 40},
        repo_root=repo_root,
    )
    assert issues == []


def test_orphan_report_is_refused_instead_of_skipped(
    monkeypatch, repo_root: Path
) -> None:
    request_path = (
        "coordination/mailbox/sent/"
        "2026-09-07T23-59-00Z-author-to-reviewer-verify-request.md"
    )
    raw = event(
        ORPHAN_REPORT,
        f"""\
Event type: verification-report
VERDICT: FAIL
Verification request: {request_path}@{'a' * 40}
Reviewed head: {'b' * 40}
Reviewed base: {'c' * 40}
Reviewer seat: reviewer
Reviewer model: claude-opus-4-6-thinking
Risk class: material-behavior

## Finding Refs

## Finding Dispositions

## Findings

The request is absent.
""",
    )
    issues = run_gate(
        monkeypatch,
        {ORPHAN_REPORT: raw},
        {},
        {ORPHAN_REPORT: "9" * 40},
        repo_root=repo_root,
    )
    assert any(
        "request binding is not its exact introduction" in issue.message
        for issue in issues
    )
