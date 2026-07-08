"""Tests for the executable Wave gate inventory contract."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_default_wave2_inventory_exists_for_gate():
    """The default Wave 2 gate must not fail from a missing inventory file."""
    proc = subprocess.run(
        [sys.executable, "scripts/wave_gate_check.py", "2"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    combined = f"{proc.stdout}\n{proc.stderr}"
    assert proc.returncode != 2
    assert "inventory not found" not in combined
