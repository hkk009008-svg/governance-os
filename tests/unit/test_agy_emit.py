import subprocess
import sys

import agy_emit


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
    exit_code = agy_emit.main(["--to", "director", "--subject", "Test"])
    assert exit_code == 1


def test_agy_emit_dispatch_option_reports_hint_without_claiming_execution(
    monkeypatch, capsys, tmp_path
):
    created = tmp_path / "coordination/mailbox/sent/event.md"
    monkeypatch.setattr(agy_emit, "emit_event", lambda **kwargs: created)

    exit_code = agy_emit.main(
        ["--to", "director", "--subject", "Test", "--body", "Body", "--dispatch"]
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
        ["--to", "director", "--subject", "Test", "--body", "Body", "--no-dispatch"]
    )

    assert exit_code == 0
    assert "[AGY ROUTING HINT]" not in capsys.readouterr().out
