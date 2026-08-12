#!/usr/bin/env python3
"""Run the Cursor app-seat unit gate before readiness claims."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


TESTS = (
    "tests/unit/test_cursor_app_binding.py",
    "tests/unit/test_cursor_hook_policy.py",
    "tests/unit/test_cursor_mailbox.py",
    "tests/unit/test_cursor_review_snapshot.py",
    "tests/unit/test_cursor_surface_sync.py",
    "tests/unit/test_cursor_seat_launcher.py",
    "tests/unit/test_cursor_protocol_model.py",
    "tests/unit/test_claude_cursor_alias_guard.py",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if os.environ.get("GIT_INDEX_FILE"):
        print(
            "cursor_land_gate: Cursor app worktrees reject GIT_INDEX_FILE",
            file=sys.stderr,
        )
        return 2
    python = root / ".venv" / "bin" / "python"
    exe = str(python if python.is_file() else Path(sys.executable))
    cmd = [
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
            git_cmd,
            cwd=root,
            check=False,
        )
    print("cursor_land_gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
