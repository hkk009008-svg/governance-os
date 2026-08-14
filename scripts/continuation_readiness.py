#!/usr/bin/env python3
"""Compatibility entrypoint for the compact Codex orientation snapshot.

New callers should use ``scripts/status.py snapshot [seat]`` directly. This
wrapper intentionally adds no doctrine, handoff scan, capacity board, wave
report, or runtime-environment projection.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import protocol_mailbox
import status


ROOT = Path(__file__).resolve().parents[1]


def _run_smoke(root: Path) -> int:
    result = subprocess.run(
        [sys.executable, "scripts/governance_verify_all.py"],
        cwd=root,
        text=True,
        check=False,
    )
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render one compact, read-only Pipeline orientation snapshot."
    )
    parser.add_argument(
        "--seat",
        choices=protocol_mailbox.RECEIVING_SEATS,
        help="Limit unread and request state to one assigned role.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the machine-readable snapshot.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run the explicit completion smoke after rendering the snapshot.",
    )
    args = parser.parse_args(argv)

    status_args = ["snapshot"]
    if args.seat:
        status_args.append(args.seat)
    if args.json:
        status_args.append("--json")
    result = status.main(status_args)
    return _run_smoke(ROOT) if result == 0 and args.smoke else result


if __name__ == "__main__":
    raise SystemExit(main())
