"""Controls for the defects the 2026-08-21 Codex review found.

Each test is the reviewer's own attack, kept so it cannot come back. Nothing
here launches a provider: `shutil.which` is monkeypatched and `run()` takes an
injected runner.
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


def test_a_run_that_wrote_nothing_cannot_inherit_a_previous_answer(
    tmp_path: Path, monkeypatch
) -> None:
    """Codex finding: a fixed last-message path made forged evidence.

    codex used one `codex-last-message.txt` in TMPDIR and read it merely
    because it existed. A fake exit-0 run that wrote nothing reused the
    previous run's text, printed it as its own answer, and hashed it into a
    fresh receipt with no warning -- the receipt mechanism assembling exactly
    the fabrication it exists to prevent.
    """

    stale = tmp_path / "codex-last-message-0.txt"
    stale.write_text("a previous run's answer", encoding="utf-8")

    def wrote_nothing(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, "", "")

    outcome = peer.run(_spec(tmp_path, "codex"), "prompt", runner=wrote_nothing)

    assert outcome.result == "", "a stale file must not become this run's result"
    assert any("produced no result" in note for note in outcome.notes)
    assert stale.read_text(encoding="utf-8") == "a previous run's answer", (
        "the unique-name fix must not have collided with the stale file at all"
    )


def test_each_invocation_gets_its_own_last_message_path(tmp_path: Path) -> None:
    first = peer_backends.build(_spec(tmp_path, "codex", invocation_id="aaaa"))
    second = peer_backends.build(_spec(tmp_path, "codex", invocation_id="bbbb"))

    assert first.last_message_file != second.last_message_file


def test_an_unrelated_nested_model_string_cannot_back_fill_the_receipt() -> None:
    """Codex finding: `_find_key` read "model" at any depth.

    An unrelated tool argument that merely echoed the requested model back
    produced model_reported="claude-opus-5" -- a receipt agreeing with its
    author by construction, which is the one outcome it must never reach.
    """

    echoed = json.dumps(
        {
            "type": "item.completed",
            "item": {
                "tool": "shell",
                "args": {"command": "grep -r model=claude-opus-5 ."},
                "deep": {"nested": {"model": "claude-opus-5"}},
            },
        }
    )

    model, _cost, _result, notes = peer_backends.reported_result("codex", echoed)

    assert model is None, "a model may only be read from a declared position"
    assert any("no codex event carried a model field" in note for note in notes)


@pytest.mark.parametrize(
    "declared",
    [
        {"model": "gpt-5.6-sol"},
        {"session": {"model": "gpt-5.6-sol"}},
        {"turn": {"model": "gpt-5.6-sol"}},
    ],
)
def test_a_model_at_a_declared_position_is_still_read(declared) -> None:
    model, _cost, _result, _notes = peer_backends.reported_result(
        "codex", json.dumps(declared)
    )

    assert model == "gpt-5.6-sol"


@pytest.mark.parametrize(
    "task",
    ["../mailbox/sent", "/etc", "a/b", "..", "", "A" * 80, "has space"],
)
def test_a_task_that_could_traverse_is_refused(task: str) -> None:
    """Codex finding: --task is an unsanitized path component.

    `../mailbox/sent` and absolute paths escaped coordination/peer/ entirely,
    which put committed mail within reach of a receipt write.
    """

    with pytest.raises(peer_backends.PeerError, match="must match"):
        peer_receipt.validate_task(task)


def test_a_gap_in_the_sequence_does_not_reuse_a_number(tmp_path: Path) -> None:
    """Codex finding: next_seq counted files instead of taking the maximum.

    A directory holding 0001 and 0003 returned 3, and the next receipt
    overwrote 0003 -- a record of something that happened, replaced silently.
    """

    directory = tmp_path / peer_receipt.RECEIPTS / "t1"
    directory.mkdir(parents=True)
    (directory / "0001-codex.json").write_text("{}", encoding="utf-8")
    (directory / "0003-codex.json").write_text('{"keep": true}', encoding="utf-8")

    assert peer_receipt.next_seq(tmp_path, "t1") == 4


def test_a_receipt_never_overwrites_an_existing_one(tmp_path: Path, monkeypatch) -> None:
    """Defence in depth behind next_seq: losing a race must fail loudly.

    next_seq no longer returns a used number, so this forces the collision it
    used to reach naturally. A receipt records something that happened; a
    silent replacement destroys evidence.
    """

    def ok(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "done"}), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=ok)
    first = peer.write_receipt(tmp_path, outcome, "2026-08-22T00:00:00Z")
    prior = first.read_text(encoding="utf-8")

    # the receipt module owns next_seq now; patching peer would miss it
    monkeypatch.setattr(peer_receipt, "next_seq", lambda repo_root, task: 1)
    with pytest.raises(peer_backends.PeerError, match="refusing to overwrite"):
        peer.write_receipt(tmp_path, outcome, "2026-08-22T00:00:01Z")

    assert first.read_text(encoding="utf-8") == prior
