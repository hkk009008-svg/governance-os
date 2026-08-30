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

_FROZEN = (
    "acknowledgement", "convergence", "coordination", "dispatch-claim",
    "discussion", "doc-sync-notice", "fold-notice", "fyi",
    "measurement-report", "proposal", "proposal-reply", "query", "reply",
    "scout-report", "scout-request", "status", "verify-addendum",
    "verify-readiness", "verify-readiness-converged", "wrap",
)


def _candidate(
    kind: str, sender: str = "codex", recipient: str = "claude"
) -> tuple[bytes, str]:
    name = f"2026-08-10T00-00-00Z-{sender}-to-{recipient}-{kind}.md"
    body = (
        f"# {sender.capitalize()} → {recipient.capitalize()}: probe\n"
        "\n"
        f"**When:** 2026-08-10T00:00:00Z · **From:** {sender} (online)\n"
        "\n"
        "Body line.\n"
        "\n"
        # Legacy pair seats are the only senders still required to carry a
        # real cursor value; the roles are cursorless.
        f"Cursor at send: {'0' if sender in protocol_mailbox.SEATS else 'cursorless'}\n"
    )
    return body.encode("utf-8"), f"coordination/mailbox/sent/{name}"


def test_a_retired_seat_name_cannot_publish_a_new_event() -> None:
    """The collapse is enforced at the writer, not merely documented.

    Reading history keeps working -- the grammar still parses every seat that
    ever appeared -- but a NEW event from one of them is refused here.
    """

    raw, relative = _candidate("findings", sender="director")

    with pytest.raises(mailbox_writer.MailboxWriterError, match="desktop app member"):
        mailbox_writer.validate_event_candidate_bytes(_REPO_ROOT, raw, relative)

    assert protocol_mailbox.EVENT_NAME_RE.fullmatch(
        relative.rsplit("/", 1)[1]
    ), "a retired sender must still PARSE; refusing to read history is a rewrite"


def test_allowlist_is_a_subset_of_the_registry_and_partitions_it() -> None:
    registry = protocol_mailbox.load_known_kinds(_REPO_ROOT)
    assert mailbox_writer.NEW_WRITE_KINDS <= registry
    assert set(_FROZEN) == registry - mailbox_writer.NEW_WRITE_KINDS, (
        "every registry kind must be explicitly allowed or explicitly frozen"
    )
    assert mailbox_writer.FORMAL_REVIEW_KINDS == {
        "verification-report",
        "verify-request",
    }
    assert mailbox_writer.APP_DURABLE_KINDS == {
        "decision",
        "findings",
        "learning-candidate",
    }
    assert not mailbox_writer.FORMAL_REVIEW_KINDS & mailbox_writer.APP_DURABLE_KINDS


@pytest.mark.parametrize(
    "kind,sender,recipient",
    (
        ("verify-request", "codex", "claude"),
        ("verify-request", "claude", "codex"),
        ("verify-request", "agy", "claude"),
        ("verification-report", "claude", "agy"),
        ("verification-report", "codex", "all"),
        ("findings", "codex", "claude"),
        ("learning-candidate", "agy", "all"),
        ("decision", "claude", "codex"),
    ),
)
def test_new_write_envelope_rule_accepts_only_exact_capability_lanes(
    kind: str, sender: str, recipient: str
) -> None:
    assert mailbox_writer.new_write_envelope_problem(
        kind, sender, recipient
    ) is None


@pytest.mark.parametrize(
    "kind,sender,recipient",
    (
        ("status", "codex", "claude"),
        ("verify-request", "author", "reviewer"),
        ("verify-request", "agy", "agy"),
        ("verify-request", "codex", "agy"),
        ("verification-report", "agy", "codex"),
        ("verification-report", "claude", "claude"),
        ("findings", "author", "reviewer"),
        ("decision", "codex", "reviewer"),
        ("learning-candidate", "agy", "agy"),
    ),
)
def test_new_write_envelope_rule_rejects_frozen_cross_lane_or_self_routes(
    kind: str, sender: str, recipient: str
) -> None:
    assert mailbox_writer.new_write_envelope_problem(kind, sender, recipient)


@pytest.mark.parametrize("kind", _FROZEN)
def test_frozen_kinds_are_refused_for_new_writes(kind: str) -> None:
    raw, relative = _candidate(kind)
    with pytest.raises(mailbox_writer.MailboxWriterError) as excinfo:
        mailbox_writer.validate_event_candidate_bytes(
            _REPO_ROOT, raw, relative, validate_range=False
        )
    assert "frozen for new writes" in str(excinfo.value)
    assert "new-write allowlist" in str(excinfo.value)


@pytest.mark.parametrize("kind", ("decision", "findings"))
def test_typed_only_kinds_refuse_generic_payloads(kind: str) -> None:
    raw, relative = _candidate(kind)
    with pytest.raises(mailbox_writer.MailboxWriterError, match="fully typed"):
        mailbox_writer.validate_event_candidate_bytes(
            _REPO_ROOT, raw, relative, validate_range=False
        )


@pytest.mark.parametrize(
    ("kind", "sender", "recipient", "message"),
    (
        ("verify-request", "author", "reviewer", "author must be"),
        ("verification-report", "reviewer", "author", "publisher must be"),
        ("verification-report", "agy", "codex", "publisher must be"),
    ),
)
def test_formal_review_kinds_reject_retired_or_nonreviewer_publishers(
    kind: str, sender: str, recipient: str, message: str
) -> None:
    raw, relative = _candidate(kind, sender=sender, recipient=recipient)
    with pytest.raises(mailbox_writer.MailboxWriterError, match=message):
        mailbox_writer.validate_event_candidate_bytes(
            _REPO_ROOT, raw, relative, validate_range=False
        )


@pytest.mark.parametrize("kind", ("decision", "findings", "learning-candidate"))
def test_durable_record_kinds_reject_temporary_review_identities(kind: str) -> None:
    raw, relative = _candidate(kind, sender="author", recipient="reviewer")
    with pytest.raises(mailbox_writer.MailboxWriterError, match="desktop app member"):
        mailbox_writer.validate_event_candidate_bytes(
            _REPO_ROOT, raw, relative, validate_range=False
        )


@pytest.mark.parametrize("kind", ("decision", "findings", "learning-candidate"))
def test_durable_record_kinds_reject_temporary_review_recipients(kind: str) -> None:
    raw, relative = _candidate(kind, sender="codex", recipient="reviewer")
    with pytest.raises(mailbox_writer.MailboxWriterError, match="desktop app member"):
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

    for kind in ("decision", "findings", "verify-addendum"):
        raw, relative = _candidate(kind)
        historical_match = mailbox_writer.validate_event_envelope_bytes(
            _REPO_ROOT, raw, relative
        )
        assert historical_match.group("kind") == kind
