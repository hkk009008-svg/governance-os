"""End-to-end committed-history controls for desktop mailbox writes."""
from __future__ import annotations

import pytest

import mailbox_writer
from mailbox_admission_test_support import (
    APP_FINDINGS,
    APP_FORMAL,
    APP_STATUS,
    HISTORICAL,
    POST,
    PRE,
    event,
    run_gate,
)


def test_every_new_event_passes_committed_payload_admission(monkeypatch) -> None:
    calls = []
    issues = run_gate(
        monkeypatch,
        {APP_FINDINGS: b"typed checkpoint"},
        {},
        {APP_FINDINGS: "8" * 40},
        validator=lambda _p, _r, path, raw, commit: calls.append(
            (path, raw, commit)
        ),
    )
    assert issues == []
    assert calls == [(APP_FINDINGS, b"typed checkpoint", POST)]


def test_frozen_and_cross_lane_direct_git_events_are_refused(monkeypatch) -> None:
    issues = run_gate(
        monkeypatch,
        {APP_STATUS: event(APP_STATUS), APP_FORMAL: event(APP_FORMAL)},
        {},
        {APP_STATUS: "8" * 40, APP_FORMAL: "9" * 40},
    )
    messages = [issue.message for issue in issues]
    assert len(issues) == 2
    assert any("frozen for new writes" in message for message in messages)
    assert any("formal review role route" in message for message in messages)


def test_payload_failure_mutation_and_current_archive_are_refused(monkeypatch) -> None:
    archived = (
        "coordination/mailbox/archive/2026/"
        "2026-09-07T00-00-00Z-codex-to-all-findings.md"
    )

    def invalid(*_args):
        raise mailbox_writer.MailboxWriterError("typed checkpoint is malformed")

    issues = run_gate(
        monkeypatch,
        {APP_FINDINGS: b"bad"},
        {HISTORICAL: "1" * 40},
        {
            HISTORICAL: "2" * 40,
            APP_FINDINGS: "8" * 40,
            archived: "9" * 40,
        },
        validator=invalid,
    )
    messages = [issue.message for issue in issues]
    assert any("changed bytes, mode, or type" in message for message in messages)
    assert any("typed checkpoint is malformed" in message for message in messages)
    assert any("outside mailbox/sent" in message for message in messages)


def test_byte_identical_historical_archive_move_is_preserved(monkeypatch) -> None:
    archived = HISTORICAL.replace("/sent/", "/archive/2026/")
    issues = run_gate(
        monkeypatch,
        {},
        {HISTORICAL: "1" * 40},
        {archived: "1" * 40},
        validator=lambda *_args: pytest.fail("historical bytes reached admission"),
    )
    assert issues == []


def test_invalid_intermediate_event_remains_visible_after_delete(monkeypatch) -> None:
    deleted = "c" * 40
    issues = run_gate(
        monkeypatch,
        {APP_STATUS: event(APP_STATUS)},
        {},
        {},
        history=[(POST, {APP_STATUS: "8" * 40}), (deleted, {})],
    )
    messages = [issue.message for issue in issues]
    assert any("frozen for new writes" in message for message in messages)
    assert any("absent or changed at HEAD" in message for message in messages)


def test_pre_cutover_introduction_cannot_be_reused(monkeypatch) -> None:
    issues = run_gate(
        monkeypatch,
        {APP_FINDINGS: event(APP_FINDINGS)},
        {},
        {APP_FINDINGS: "8" * 40},
        introductions_override={APP_FINDINGS: (PRE, "8" * 40)},
    )
    assert any("cannot reuse a pre-cutover introduction" in x.message for x in issues)


def test_missing_cutover_fails_closed_for_current_identity(monkeypatch) -> None:
    issues = run_gate(
        monkeypatch,
        {APP_FORMAL: event(APP_FORMAL)},
        {},
        {APP_FORMAL: "9" * 40},
        boundary=False,
    )
    assert [issue.kind for issue in issues] == [
        "post_cutover_event_admission_unavailable"
    ]


def test_restored_boundary_blob_does_not_hide_mutation(monkeypatch) -> None:
    issues = run_gate(
        monkeypatch,
        {},
        {HISTORICAL: "1" * 40},
        {HISTORICAL: "1" * 40},
        history=[
            (POST, {HISTORICAL: "2" * 40}),
            ("c" * 40, {HISTORICAL: "1" * 40}),
        ],
    )
    assert any("changed bytes, mode, or type" in issue.message for issue in issues)


@pytest.mark.parametrize("mode", ["100755", "120000"])
def test_non_regular_event_mode_is_rejected(monkeypatch, mode: str) -> None:
    entry = (mode, "blob", "8" * 40)
    issues = run_gate(
        monkeypatch,
        {APP_FINDINGS: b"unused"},
        {},
        {APP_FINDINGS: entry},
        history=[(POST, {APP_FINDINGS: entry})],
        validator=lambda *_args: pytest.fail("invalid mode reached payload parsing"),
    )
    assert any("must be a 100644 blob" in issue.message for issue in issues)
