"""One seat roster across the surviving runtime and transport surfaces."""

from __future__ import annotations

import re
from pathlib import Path

import codex_seat_launcher
import compact_pair_loop
import consume_bus
import ledger_start_guard
import mailbox_writer
import protocol_mailbox
import seat_emit
from threeway import cursor_backfill


ROOT = Path(__file__).resolve().parents[2]


def test_python_surfaces_import_the_canonical_roster() -> None:
    assert consume_bus.SEATS == protocol_mailbox.SEATS
    assert seat_emit.SEATS == protocol_mailbox.SENDERS
    assert mailbox_writer._ROLES == frozenset(protocol_mailbox.SEATS)
    assert compact_pair_loop.PAIR_SEATS == frozenset(protocol_mailbox.SEATS)
    assert codex_seat_launcher.LAUNCH_SEATS == protocol_mailbox.LAUNCHABLE_SEATS
    assert ledger_start_guard.VALID_SEATS == tuple(
        sorted(protocol_mailbox.LAUNCHABLE_SEATS)
    )


def test_transport_roster_stays_bound_to_the_canonical_one() -> None:
    assert cursor_backfill.SEATS == protocol_mailbox.RECEIVING_SEATS


def test_cold_capacity_declaration_shape() -> None:
    assert "coordinator2" in protocol_mailbox.SENDERS
    assert "coordinator2" in protocol_mailbox.RECEIVING_SEATS
    assert "coordinator2" not in protocol_mailbox.LAUNCHABLE_SEATS
    assert set(protocol_mailbox.LAUNCHABLE_SEATS) == {
        *protocol_mailbox.SEATS,
        "coordinator",
    }


def test_send_event_bash_whitelists_match_the_roster() -> None:
    text = (ROOT / "coordination/bin/send-event").read_text(encoding="utf-8")
    alternations = [
        set(found.split("|"))
        for found in re.findall(r"^\s*([a-z0-9|]+)\) ;;$", text, re.MULTILINE)
    ]
    assert len(alternations) == 5, (
        "send-event's seat case-lists changed shape; re-bind this test"
    )
    from_roster, to_roster, report_authors, request_authors, learning_authors = (
        alternations
    )
    assert from_roster == set(protocol_mailbox.SENDERS)
    assert to_roster == set(protocol_mailbox.RECIPIENTS)
    assert report_authors == {
        seat for seat in protocol_mailbox.SEATS if seat.startswith("operator")
    }
    assert request_authors == set(protocol_mailbox.SEATS)
    assert learning_authors == set(protocol_mailbox.SEATS)
