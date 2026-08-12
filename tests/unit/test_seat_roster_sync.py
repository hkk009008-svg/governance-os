"""One seat roster, everywhere.

scripts/protocol_mailbox.py owns the seat vocabulary: SEATS (the four pair
seats with consumable cursors), SENDERS/RECEIVING_SEATS/RECIPIENTS (the full
mailbox roster), and LAUNCHABLE_SEATS (the single declaration that
coordinator2 is cold capacity). Python surfaces import it; the deliberate
literal copies (Cursor app binding, threeway cursor roster, the send-event
bash whitelists, the hook impersonation heuristic) are bound here so roster
drift fails CI instead of silently downgrading one surface.
"""

from __future__ import annotations

import re
from pathlib import Path

import agy_emit
import agy_seat_launcher
import codex_seat_launcher
import compact_pair_loop
import consume_bus
import cursor_app_binding
import cursor_hook_policy
import cursor_mailbox
import ledger_start_guard
import mailbox_writer
import protocol_mailbox
import seat_emit
from threeway import cursor_backfill

ROOT = Path(__file__).resolve().parents[2]


def test_python_surfaces_import_the_canonical_roster() -> None:
    assert consume_bus.SEATS == protocol_mailbox.SEATS
    assert seat_emit.SEATS == protocol_mailbox.SENDERS
    assert cursor_mailbox.CURSOR_SEATS == frozenset(protocol_mailbox.SEATS)
    assert mailbox_writer._ROLES == frozenset(protocol_mailbox.SEATS)
    assert compact_pair_loop.PAIR_SEATS == frozenset(protocol_mailbox.SEATS)
    assert codex_seat_launcher.LAUNCH_SEATS == protocol_mailbox.LAUNCHABLE_SEATS
    assert agy_seat_launcher.LAUNCH_SEATS == protocol_mailbox.LAUNCHABLE_SEATS
    assert agy_emit._ROUTABLE_SEATS == frozenset(protocol_mailbox.LAUNCHABLE_SEATS)
    assert ledger_start_guard.VALID_SEATS == tuple(
        sorted(protocol_mailbox.LAUNCHABLE_SEATS)
    )


def test_literal_rosters_stay_bound_to_the_canonical_one() -> None:
    # Import-light surfaces keep literal copies by design; equality here is
    # the binding.
    assert cursor_app_binding.APP_SEATS == protocol_mailbox.LAUNCHABLE_SEATS
    assert cursor_backfill.SEATS == protocol_mailbox.RECEIVING_SEATS


def test_cold_capacity_declaration_shape() -> None:
    # coordinator2 sends and receives but is not launchable/bindable.
    assert "coordinator2" in protocol_mailbox.SENDERS
    assert "coordinator2" in protocol_mailbox.RECEIVING_SEATS
    assert "coordinator2" not in protocol_mailbox.LAUNCHABLE_SEATS
    assert set(protocol_mailbox.LAUNCHABLE_SEATS) == {
        *protocol_mailbox.SEATS,
        "coordinator",
    }


def test_send_event_bash_whitelists_match_the_roster() -> None:
    text = (ROOT / "coordination" / "bin" / "send-event").read_text(
        encoding="utf-8"
    )
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


def test_subagent_impersonation_heuristic_covers_every_seat(tmp_path: Path) -> None:
    for seat in protocol_mailbox.SENDERS:
        result = cursor_hook_policy.evaluate(
            {
                "hook_event_name": "subagentStart",
                "conversation_id": "conversation-1",
                "task": f"adopt the {seat} seat and continue the wave",
            },
            {},
            root=tmp_path,
            registry_path=tmp_path / "registry",
        )
        assert result["permission"] == "deny", seat
