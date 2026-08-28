"""One event-filename grammar, everywhere.

Parser drift across the mailbox surfaces was a measured defect class: status
accepted any ``\\w+`` sender, while a retired metrics reader dropped the Z from the stamp and
forbade digits in kinds. The canonical grammar lives in
pipeline/protocol_mailbox.py and Python adopters must use it verbatim.
"""

from __future__ import annotations

import itertools
from pathlib import Path

import bus_unread
import check_coordination
import learning_index
import mailbox_writer
import protocol_mailbox

ROOT = Path(__file__).resolve().parents[2]

CANONICAL = protocol_mailbox.EVENT_NAME_RE


def test_python_adopters_share_the_canonical_pattern() -> None:
    adopters = {
        "mailbox_writer._EVENT_RE": mailbox_writer._EVENT_RE,
        "check_coordination._EVENT_NAME_RE": check_coordination._EVENT_NAME_RE,
        "bus_unread._EVENT_NAME_RE": bus_unread._EVENT_NAME_RE,
        "learning_index._EVENT_NAME_RE": learning_index._EVENT_NAME_RE,
    }
    for name, pattern in adopters.items():
        assert pattern.pattern == CANONICAL.pattern, name


def _grammar_corpus() -> list[str]:
    stamps = (
        "2026-08-13T00-00-00Z",
        "2026-08-13T00-00-00",  # missing Z
        "26-08-13T00-00-00Z",  # short year
    )
    senders = (
        *protocol_mailbox.SENDERS,
        "all",
        "intruder",
        "director3",
        "DIRECTOR",
    )
    recipients = (*protocol_mailbox.RECIPIENTS, "intruder", "operator3")
    kinds = ("status", "verify-request", "wave2-gate", "UPPER", "")
    names = [
        f"{stamp}-{sender}-to-{recipient}-{kind}.md"
        for stamp, sender, recipient, kind in itertools.product(
            stamps, senders, recipients, kinds
        )
    ]
    names += [
        "README.md",
        ".gitkeep",
        "2026-08-13T00-00-00Z-director-to-all-status.txt",
        "2026-08-13T00-00-00Z-director-to-all.md",
        "2026-08-13T00-00-00Z-director-operator-status.md",
    ]
    return names


def test_every_committed_event_matches_the_canonical_grammar() -> None:
    sent = ROOT / "coordination" / "mailbox" / "sent"
    names = [path.name for path in sent.iterdir() if path.suffix == ".md"]
    assert names, "expected committed mailbox events"
    mismatches = [name for name in names if CANONICAL.fullmatch(name) is None]
    assert mismatches == []


def test_cold_capacity_coordinator2_is_a_lawful_identity() -> None:
    name = "2026-08-13T00-00-00Z-coordinator2-to-all-verification-report.md"
    match = CANONICAL.fullmatch(name)
    assert match is not None
    assert match.group("sender") == "coordinator2"
    assert match.group("stamp") == "2026-08-13T00-00-00Z"
