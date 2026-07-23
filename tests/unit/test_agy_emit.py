import subprocess
from pathlib import Path
import pytest

import agy_emit


def test_agy_emit_cli_help():
    result = subprocess.run(
        [".venv/bin/python", "scripts/agy_emit.py", "--help"],
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
