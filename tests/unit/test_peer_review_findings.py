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


def test_a_symlinked_last_message_is_refused_not_read(tmp_path: Path) -> None:
    """Codex finding: is_file() and read_text() both follow symlinks.

    A unique name stopped ordinary stale reuse; it did not stop the class.
    Pointing the generated path at a prior answer made that answer this run's
    result.
    """

    prior = tmp_path / "someone-elses-answer.txt"
    prior.write_text("a previous run's answer", encoding="utf-8")

    spec = _spec(tmp_path, "codex", invocation_id="fixed")
    target = Path(peer_backends.build(spec).last_message_file)
    target.symlink_to(prior)

    def wrote_nothing(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, "", "")

    outcome = peer.run(spec, "prompt", runner=wrote_nothing)

    assert outcome.result == ""
    assert any("refusing to read" in note for note in outcome.notes), outcome.notes
    assert prior.read_text(encoding="utf-8") == "a previous run's answer"


def test_the_argv_shown_is_the_argv_launched(tmp_path: Path, monkeypatch, capsys) -> None:
    """Codex finding, and the sharpest one: --dry-run advertised a different run.

    The invocation id was randomized inside run(), AFTER main() had printed the
    argv, so the proposed path was codex-last-message-0.txt and the executed
    one carried a uuid. A --dry-run whose output differs from the invocation is
    worse than no --dry-run, because it is the artifact the spend is approved
    against.
    """

    launched: list[list[str]] = []

    def capture(argv, **kwargs):
        launched.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "x"}), "")

    monkeypatch.setattr(peer.subprocess, "run", capture)
    monkeypatch.setattr(peer, "ROOT", tmp_path)
    monkeypatch.setattr(peer_receipt, "RECEIPTS", "coordination/peer")

    peer.main(["ask", "codex", "--task", "argvcheck", "--prompt", "hi", "--cwd", str(tmp_path)])
    printed = [
        line[2:] for line in capsys.readouterr().err.splitlines() if line.startswith("$ ")
    ]

    assert printed, "main must print the argv it is about to run"
    assert launched, "the runner must have been reached"
    assert printed[0].split() == launched[0], (
        "the advertised argv and the executed argv must be identical"
    )
