"""Receipt-side controls for the 2026-08-21 Codex findings.

The receipt has three invariants and each was a real defect first: it must
stay inside coordination/peer/, it must never overwrite a record, and a lost
race must still leave the loser recorded rather than silent.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import peer
import peer_backends
import peer_receipt

from test_peer import _spec, peers_on_path  # noqa: F401 — fixture re-export


def test_a_lost_sequence_race_takes_the_next_number(tmp_path: Path, monkeypatch) -> None:
    """Concurrent writers must both end up recorded.

    O_EXCL alone made them safe from overwrite and unsafe from silence: the
    loser raised FileExistsError, and a provider run that had already happened
    ended with no receipt at all.
    """

    def ok(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "done"}), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=ok)
    first = peer.write_receipt(tmp_path, outcome, "2026-08-22T00:00:00Z")

    # Simulate the loser: next_seq still reports the number the winner took.
    taken = [1]

    def stale_seq(repo_root, task):
        return taken[0]

    monkeypatch.setattr(peer_receipt, "next_seq", stale_seq)
    second = peer.write_receipt(tmp_path, outcome, "2026-08-22T00:00:01Z")

    assert first.name == "0001-claude.json"
    assert second.name == "0002-claude.json", "the loser must still be recorded"
    assert json.loads(first.read_text(encoding="utf-8"))["schema"] == "peer-receipt/1"


def test_an_unclaimable_sequence_fails_loudly_and_preserves_the_record(
    tmp_path: Path, monkeypatch
) -> None:
    """When no number can be claimed, say a run is unrecorded rather than lie."""

    def ok(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "done"}), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=ok)
    first = peer.write_receipt(tmp_path, outcome, "2026-08-22T00:00:00Z")
    prior = first.read_text(encoding="utf-8")

    # Genuinely exhaust the window: every number the loop will try is taken.
    directory = first.parent
    for seq in range(2, 2 + peer_receipt._SEQUENCE_ATTEMPTS):
        (directory / f"{seq:04d}-claude.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(peer_receipt, "next_seq", lambda repo_root, task: 1)

    with pytest.raises(peer_backends.PeerError, match="unrecorded"):
        peer.write_receipt(tmp_path, outcome, "2026-08-22T00:00:01Z")

    assert first.read_text(encoding="utf-8") == prior


def test_a_symlinked_task_directory_cannot_escape_the_receipt_root(
    tmp_path: Path,
) -> None:
    """Codex finding: validate_task constrains the NAME, not what it points at.

    A lexically valid task that is already a symlink wrote its receipt outside
    coordination/peer/ entirely.
    """

    outside = tmp_path / "outside"
    outside.mkdir()
    receipts = tmp_path / peer_receipt.RECEIPTS
    receipts.mkdir(parents=True)
    (receipts / "escape").symlink_to(outside)

    with pytest.raises(peer_backends.PeerError, match="symlink"):
        peer_receipt.receipt_path(tmp_path, "escape", 1, "codex")

    assert list(outside.iterdir()) == [], "nothing may be written outside the root"
