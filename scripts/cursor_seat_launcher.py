#!/usr/bin/env python3
"""Read-only diagnostics for Cursor Desktop app seats.

Live seats are pinned top-level chats in linked worktrees. This module remains
only as a compatibility diagnostic for the former ``cursor-seat`` command; it
never launches a provider process or changes a binding.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from cursor_app_binding import APP_SEATS, DEFAULT_REGISTRY_PATH, load_registry
from cursor_protocol_model import render_runtime_env_contract


def status_document(registry_path: Path = DEFAULT_REGISTRY_PATH) -> dict[str, object]:
    document = load_registry(registry_path)
    bindings = document["bindings"]
    assert isinstance(bindings, dict)
    return {
        seat: (
            {
                **record,
                "bound": True,
                "worktree_exists": (
                    isinstance(record.get("root"), str)
                    and Path(record["root"]).is_dir()
                ),
            }
            if isinstance((record := bindings.get(seat)), dict)
            else {"bound": False}
        )
        for seat in APP_SEATS
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cursor-seat",
        description=(
            "Read-only Cursor app seat diagnostics. "
            "Open pinned Agents Window worktrees to run seats."
        ),
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("command", choices=("readiness", "status"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(sys.argv[1:] if argv is None else list(argv))
    if args.command == "readiness":
        print(render_runtime_env_contract({}))
        return 0
    try:
        print(json.dumps(status_document(args.registry), indent=2, sort_keys=True))
    except Exception as exc:
        print(f"cursor-seat: cannot read app seat registry: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
