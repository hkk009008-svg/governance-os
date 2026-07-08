#!/usr/bin/env python3
"""Select the newest canonical handoff for a concrete seat."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import protocol_mailbox


REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_SEATS = frozenset(protocol_mailbox.RECEIVING_SEATS)


@dataclass(frozen=True)
class HandoffSelection:
    seat: str
    pattern: str
    path: Path | None
    warnings: tuple[str, ...]


def canonical_pattern(seat: str) -> str:
    if seat not in VALID_SEATS:
        raise ValueError(f"unknown seat: {seat}")
    token = "coordinator" if seat.startswith("coordinator") else seat
    return f"HANDOFF-{token}-*.md"


def _warning_tokens(seat: str) -> tuple[str, ...]:
    if seat.startswith("coordinator"):
        return ("coordinator", "coordinator2")
    return (seat,)


def _is_near_match(path: Path, seat: str, pattern: str) -> bool:
    if path.name.startswith("HANDOFF-") is False or path.suffix != ".md":
        return False
    if path.match(pattern):
        return False
    tokens = path.stem.split("-")[1:]
    return any(token in tokens for token in _warning_tokens(seat))


def find_latest_handoff(root: Path, seat: str) -> HandoffSelection:
    pattern = canonical_pattern(seat)
    docs_root = root / "docs"
    candidates = sorted(docs_root.glob(pattern))
    selected = max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name), default=None)

    warnings = tuple(
        f"warning: ignored noncanonical same-seat handoff candidate docs/{path.name}; "
        f"expected {pattern}"
        for path in sorted(docs_root.glob("HANDOFF-*.md"))
        if _is_near_match(path, seat, pattern)
    )

    return HandoffSelection(seat=seat, pattern=pattern, path=selected, warnings=warnings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the newest canonical same-seat handoff.")
    parser.add_argument("seat", choices=protocol_mailbox.RECEIVING_SEATS)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    selection = find_latest_handoff(args.root, args.seat)
    for warning in selection.warnings:
        print(warning, file=__import__("sys").stderr)
    if selection.path is None:
        print(
            f"no canonical handoff found for {args.seat} under {args.root / 'docs'} "
            f"(expected {selection.pattern})",
            file=__import__("sys").stderr,
        )
        return 0
    print(selection.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
