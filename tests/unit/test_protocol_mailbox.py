"""Unit tests for scripts/protocol_mailbox.py — the shared mailbox vocabulary.

Covers the seat/recipient rosters and the kinds.txt-backed KNOWN_KINDS set.
Hermetic: reads only the committed kinds.txt for module-level constants, and
uses tmp_path for the loader-with-custom-root path.
"""

from __future__ import annotations

from pathlib import Path

import protocol_mailbox


# --- Static roster invariants -------------------------------------------------


def test_seats_exact_membership():
    # The four pair seats; assert membership so a future reorder doesn't break us,
    # plus the exact set so no extras sneak in.
    expected = {"director", "director2", "operator", "operator2"}
    assert set(protocol_mailbox.SEATS) == expected
    for seat in expected:
        assert seat in protocol_mailbox.SEATS
    # No duplicates in the roster tuple.
    assert len(protocol_mailbox.SEATS) == len(set(protocol_mailbox.SEATS))


def test_receiving_seats_superset_of_seats_plus_coordinators():
    receiving = set(protocol_mailbox.RECEIVING_SEATS)
    seats = set(protocol_mailbox.SEATS)
    assert seats <= receiving
    assert "coordinator" in receiving
    assert "coordinator2" in receiving
    # `all` is a broadcast target only — never a receiving seat.
    assert "all" not in receiving
    assert receiving == seats | {"coordinator", "coordinator2"}


def test_senders_roster():
    senders = set(protocol_mailbox.SENDERS)
    assert set(protocol_mailbox.SEATS) <= senders
    assert "coordinator" in senders
    assert "coordinator2" in senders
    # `all` is not a sender.
    assert "all" not in senders
    # Senders mirror the receiving roster (every receiver can also send).
    assert senders == set(protocol_mailbox.RECEIVING_SEATS)


def test_recipients_includes_all_but_all_is_not_a_seat():
    recipients = set(protocol_mailbox.RECIPIENTS)
    assert "all" in recipients
    assert "all" not in protocol_mailbox.SEATS
    # Every receiving seat is also a valid recipient target.
    assert set(protocol_mailbox.RECEIVING_SEATS) <= recipients
    # RECIPIENTS is exactly the receiving roster plus the broadcast target.
    assert recipients == set(protocol_mailbox.RECEIVING_SEATS) | {"all"}


# --- KNOWN_KINDS loaded from coordination/mailbox/kinds.txt --------------------


def test_known_kinds_is_nonempty_frozenset():
    assert isinstance(protocol_mailbox.KNOWN_KINDS, frozenset)
    assert len(protocol_mailbox.KNOWN_KINDS) > 0


def test_known_kinds_contains_representative_kinds():
    for kind in ("verification-report", "status", "findings", "dispatch-claim"):
        assert kind in protocol_mailbox.KNOWN_KINDS


def test_known_kinds_count_matches_nonblank_noncomment_lines():
    kind_file = Path(protocol_mailbox.KIND_FILE)
    lines = kind_file.read_text(encoding="utf-8").splitlines()
    meaningful = [
        ln.strip()
        for ln in lines
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert len(protocol_mailbox.KNOWN_KINDS) == len(meaningful)
    # The frozenset is exactly the deduped set of those lines.
    assert protocol_mailbox.KNOWN_KINDS == frozenset(meaningful)


def test_coordination_kinds_excludes_verification_report():
    assert "verification-report" not in protocol_mailbox.COORDINATION_KINDS
    assert protocol_mailbox.COORDINATION_KINDS == (
        protocol_mailbox.KNOWN_KINDS - {"verification-report"}
    )


# --- load_known_kinds() loader behavior with an explicit root -----------------


def test_load_known_kinds_with_custom_root(tmp_path):
    mbox = tmp_path / "coordination" / "mailbox"
    mbox.mkdir(parents=True)
    (mbox / "kinds.txt").write_text(
        "# a comment line\n"
        "status\n"
        "  findings  \n"          # whitespace stripped
        "\n"                       # blank line ignored
        "   \n"                    # whitespace-only line ignored
        "  # indented comment\n"   # comment after strip → ignored
        "status\n"                 # duplicate → deduped by frozenset
        "dispatch-claim\n",
        encoding="utf-8",
    )
    result = protocol_mailbox.load_known_kinds(root=tmp_path)
    assert isinstance(result, frozenset)
    assert result == frozenset({"status", "findings", "dispatch-claim"})


def test_load_known_kinds_default_root_matches_module_constant():
    # Calling with no root reproduces the module-level KNOWN_KINDS.
    assert protocol_mailbox.load_known_kinds() == protocol_mailbox.KNOWN_KINDS
