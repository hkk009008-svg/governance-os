import subprocess
import sys

from pathlib import Path

import agy_emit
import pytest


def test_agy_emit_cli_help():
    result = subprocess.run(
        [sys.executable, "scripts/agy_emit.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Streamlined AGY mailbox event emitter" in result.stdout


def test_agy_emit_no_body_tty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    exit_code = agy_emit.main(
        ["--from", "director", "--to", "operator", "--subject", "Test"]
    )
    assert exit_code == 1


def test_agy_emit_dispatch_option_reports_hint_without_claiming_execution(
    monkeypatch, capsys, tmp_path
):
    created = tmp_path / "coordination/mailbox/sent/event.md"
    monkeypatch.setattr(agy_emit, "emit_event", lambda **kwargs: created)

    exit_code = agy_emit.main(
        ["--from", "director", "--to", "operator", "--subject", "Test", "--body", "Body", "--dispatch"]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "[AGY ROUTING HINT]" in output
    assert "not executed" in output
    assert "dispatched" not in output


def test_agy_emit_no_dispatch_suppresses_routing_hint(monkeypatch, capsys, tmp_path):
    created = tmp_path / "coordination/mailbox/sent/event.md"
    monkeypatch.setattr(agy_emit, "emit_event", lambda **kwargs: created)

    exit_code = agy_emit.main(
        ["--from", "director", "--to", "operator", "--subject", "Test", "--body", "Body", "--no-dispatch"]
    )

    assert exit_code == 0
    assert "[AGY ROUTING HINT]" not in capsys.readouterr().out


def test_emit_event_stages_through_fixed_writer_without_committing(
    tmp_path: Path, monkeypatch
) -> None:
    wrapper = tmp_path / "coordination/bin/send-event"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text("#!/bin/sh\n", encoding="utf-8")
    calls: list[list[str]] = []

    def run(command, **kwargs):
        calls.append([str(part) for part in command])
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=(
                b"created coordination/mailbox/sent/event.md "
                b"(staged; commit with explicit pathspec)\n"
            ),
            stderr=b"",
        )

    monkeypatch.setattr(agy_emit.subprocess, "run", run)

    path = agy_emit.emit_event(
        sender="director",
        recipient="operator",
        kind="coordination",
        subject="subject",
        body="body\n",
        root=tmp_path,
    )

    assert path == tmp_path / "coordination/mailbox/sent/event.md"
    assert calls == [[str(wrapper), "director", "operator", "coordination", "subject"]]


def test_emit_event_fails_when_fixed_writer_keeps_event_unstaged(
    tmp_path: Path, monkeypatch
) -> None:
    wrapper = tmp_path / "coordination/bin/send-event"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text("#!/bin/sh\n", encoding="utf-8")

    monkeypatch.setattr(
        agy_emit.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command,
            0,
            stdout=(
                b"created coordination/mailbox/sent/event.md "
                b"(not staged; git add failed)\n"
            ),
            stderr=b"send-event: git add failed\n",
        ),
    )

    with pytest.raises(RuntimeError, match="did not confirm a staged event"):
        agy_emit.emit_event(
            sender="director",
            recipient="operator",
            kind="coordination",
            subject="subject",
            body="body\n",
            root=tmp_path,
        )
