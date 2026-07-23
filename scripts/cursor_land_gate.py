#!/usr/bin/env python3
"""Run the Cursor-unit land gate before claiming a Cursor adapter change is ready."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TESTS = (
    "tests/unit/test_cursor_auto_relay.py",
    "tests/unit/test_cursor_hook_policy.py",
    "tests/unit/test_cursor_mailbox.py",
    "tests/unit/test_cursor_surface_sync.py",
    "tests/unit/test_cursor_seat_launcher.py",
    "tests/unit/test_cursor_protocol_model.py",
    "tests/unit/test_cursor_apply_bundle.py",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    python = root / ".venv" / "bin" / "python"
    exe = str(python if python.is_file() else Path(sys.executable))
    cmd = [
        "/usr/bin/env",
        "-u",
        "GIT_INDEX_FILE",
        exe,
        "-m",
        "pytest",
        *TESTS,
        "-q",
    ]
    print("running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=root, check=False)
    if result.returncode != 0:
        return result.returncode
    for git_cmd in (
        ["git", "log", "--oneline", "-3"],
        ["git", "status", "--short", "--branch"],
    ):
        subprocess.run(
            ["/usr/bin/env", "-u", "GIT_INDEX_FILE", *git_cmd],
            cwd=root,
            check=False,
        )
    print("cursor_land_gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
