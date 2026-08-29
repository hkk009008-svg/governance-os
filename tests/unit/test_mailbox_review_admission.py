"""Committed payloads never fall back to mutable publication candidates."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import mailbox_review_admission as admission
import mailbox_writer
import protocol_mailbox
from mailbox_admission_test_support import (
    APP_FINDINGS,
    ORPHAN_REPORT,
    event,
    run_gate,
)


REQUEST = (
    "coordination/mailbox/sent/2026-08-27T20-35-21Z-director-to-operator-verify-request.md",
    "5601411162075259c039b89c72f40d1fa0b6a12b",
    "d5abf22a35ddc2e2912d8c1f35fa57e4b848cbe96f8f7236eff35dbe1a751cb3",
)
REPORT = (
    "coordination/mailbox/sent/2026-08-28T02-43-08Z-operator-to-director-verification-report.md",
    "3f4ba504016d622f97a0675890cb0803dcdff3c8",
    "0e713967e928b1b124a82b0990bdbfefb084a2fb0679d36631862abaff96a767",
)


def _legacy(path: str, kind: str) -> bytes:
    return event(path, f"Event type: {kind}").replace(
        b"Cursor at send: cursorless", b"Cursor at send: 0"
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
        "2026-09-07T23-59-00Z-codex-to-claude-verify-request.md"
    )
    raw = event(
        ORPHAN_REPORT,
        f"""\
Event type: verification-report
VERDICT: FAIL
Verification request: {request_path}@{'a' * 40}
Reviewed head: {'b' * 40}
Reviewed base: {'c' * 40}
Reviewer seat: claude
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


def test_exact_pin_reaches_only_the_committed_reader(monkeypatch, repo_root: Path) -> None:
    assert admission._FROZEN_FORWARD_READER_REVIEW_ARTIFACTS == {
        REQUEST[0]: REQUEST[1:], REPORT[0]: REPORT[1:]
    }
    cases = ((REQUEST, "verify-request", "projected_request"),
             (REPORT, "verification-report", "projected_report"))
    for spec, kind, target in cases:
        path, commit, _digest = spec
        raw, calls = _legacy(path, kind), []
        monkeypatch.setitem(admission._FROZEN_FORWARD_READER_REVIEW_ARTIFACTS,
                            path, (commit, hashlib.sha256(raw).hexdigest()))
        monkeypatch.setattr(admission, target, lambda *_args, **kw: calls.append(kw))
        admission.validate_committed_new_event(
            SimpleNamespace(kinds=protocol_mailbox.KNOWN_KINDS), repo_root, path, raw, commit
        )
        assert calls == [{"current_policy": False}]
        with pytest.raises(mailbox_writer.MailboxWriterError, match="codex"):
            mailbox_writer.validate_event_candidate_bytes(repo_root, raw, path, validate_range=False)


def test_pin_rejects_one_variable_drift(monkeypatch, repo_root: Path) -> None:
    path, commit, _digest = REQUEST
    raw = _legacy(path, "verify-request")
    monkeypatch.setitem(admission._FROZEN_FORWARD_READER_REVIEW_ARTIFACTS,
                        path, (commit, hashlib.sha256(raw).hexdigest()))
    moved = path.replace("20-35-21Z", "20-35-22Z")
    cases = (
        (moved, commit, _legacy(moved, "verify-request")),
        (path, "9" * 40, raw),
        (path, commit, raw.replace(b"verify-request", b"verify-request\nChanged: true")),
    )
    for candidate_path, candidate_commit, candidate_raw in cases:
        with pytest.raises(mailbox_writer.MailboxWriterError, match="codex"):
            admission.validate_committed_new_event(
                SimpleNamespace(kinds=protocol_mailbox.KNOWN_KINDS), repo_root,
                candidate_path, candidate_raw, candidate_commit,
            )


def test_pin_cannot_reopen_non_formal_legacy_routes(monkeypatch, repo_root: Path) -> None:
    path, commit = REQUEST[0].replace("verify-request", "findings"), REQUEST[1]
    raw = _legacy(path, "findings")
    monkeypatch.setitem(admission._FROZEN_FORWARD_READER_REVIEW_ARTIFACTS,
                        path, (commit, hashlib.sha256(raw).hexdigest()))
    with pytest.raises(mailbox_writer.MailboxWriterError, match="sender must be a desktop app"):
        admission.validate_committed_new_event(
            SimpleNamespace(kinds=protocol_mailbox.KNOWN_KINDS), repo_root, path, raw, commit)


def test_retired_role_route_stops_at_the_app_member_cutover() -> None:
    check = admission.is_historical_retired_review_route
    cutoff = admission.FORMAL_REVIEW_APP_MEMBER_CUTOVER_COMMIT
    ancestor = lambda candidate, _cutoff: candidate == "pre"
    assert check("verify-request", "author", "reviewer", cutoff, ancestor)
    assert check("verification-report", "reviewer", "all", "pre", ancestor)
    assert not check("verify-request", "author", "reviewer", "post", ancestor)
    assert not check("verification-report", "agy", "all", "pre", ancestor)
