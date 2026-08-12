"""The fixed writer persists state transitions, not conversation (PR 3)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mailbox_writer  # noqa: E402
import protocol_mailbox  # noqa: E402

_STRUCTURE_FREE_ALLOWED = (
    "findings",
    "dispatch-claim",
    "measurement-report",
    "verify-addendum",
)
_FROZEN = (
    "acknowledgement",
    "convergence",
    "coordination",
    "discussion",
    "doc-sync-notice",
    "fold-notice",
    "fyi",
    "proposal",
    "proposal-reply",
    "query",
    "reply",
    "scout-report",
    "scout-request",
    "status",
    "verify-readiness",
    "verify-readiness-converged",
    "wrap",
)


def _candidate(kind: str) -> tuple[bytes, str]:
    name = f"2026-08-10T00-00-00Z-director-to-operator-{kind}.md"
    body = (
        "# Director → Operator: probe\n"
        "\n"
        "**When:** 2026-08-10T00:00:00Z · **From:** director (online)\n"
        "\n"
        "Body line.\n"
        "\n"
        "Cursor at send: 0\n"
    )
    return body.encode("utf-8"), f"coordination/mailbox/sent/{name}"


def test_allowlist_is_a_subset_of_the_registry_and_partitions_it() -> None:
    registry = protocol_mailbox.load_known_kinds(_REPO_ROOT)
    assert mailbox_writer.NEW_WRITE_KINDS <= registry
    assert set(_FROZEN) == registry - mailbox_writer.NEW_WRITE_KINDS, (
        "every registry kind must be explicitly allowed or explicitly frozen"
    )


@pytest.mark.parametrize("kind", _FROZEN)
def test_frozen_kinds_are_refused_for_new_writes(kind: str) -> None:
    raw, relative = _candidate(kind)
    with pytest.raises(mailbox_writer.MailboxWriterError) as excinfo:
        mailbox_writer.validate_event_candidate_bytes(
            _REPO_ROOT, raw, relative, validate_range=False
        )
    assert "frozen for new writes" in str(excinfo.value)
    assert "new-write allowlist" in str(excinfo.value)


@pytest.mark.parametrize("kind", _STRUCTURE_FREE_ALLOWED)
def test_state_transition_kinds_still_publish(kind: str) -> None:
    raw, relative = _candidate(kind)
    mailbox_writer.validate_event_candidate_bytes(
        _REPO_ROOT, raw, relative, validate_range=False
    )


def test_historical_conversational_events_keep_parsing_read_only() -> None:
    """Freeze is write-side only: the committed corpus stays legible."""
    sent = _REPO_ROOT / "coordination/mailbox/sent"
    historical = sorted(sent.glob("*-status.md")) + sorted(sent.glob("*-fyi.md"))
    assert historical, "corpus should contain historical conversational events"
    sample = historical[0]
    match = mailbox_writer.validate_event_envelope(
        _REPO_ROOT, sample, f"coordination/mailbox/sent/{sample.name}"
    )
    assert match.group("kind") in {"status", "fyi"}
