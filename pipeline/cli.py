#!/usr/bin/env python3
"""One small command dispatcher for the desktop-team harness."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
for path in (str(ROOT), str(ROOT / "pipeline")):
    if path not in sys.path:
        sys.path.insert(0, path)


COMMANDS: dict[tuple[str, ...], tuple[str, str, str]] = {
    ("status",): ("status", "main", "current apps, transport, Git, and review state"),
    ("check",): ("governance_verify_all", "main", "proportionate repository checks"),
    ("check", "coordination"): ("check_coordination", "main", "current formal-review state"),
    ("check", "admission"): ("ci_admission_gate", "main", "authority-range admission"),
    ("review", "request"): ("compact_pair_loop", "review_request_main", "compose a request body"),
    ("review", "validate"): ("compact_pair_loop", "review_validate_main", "validate a candidate artifact"),
    ("mail", "send"): ("mailbox_writer", "send_main", "publish a formal artifact"),
    ("team",): ("team", "main", "desktop-app team transport"),
    ("preflight",): ("harness_preflight", "main", "desktop-app integration checks"),
}


def _usage() -> str:
    rows = [(" ".join(command), target[2]) for command, target in COMMANDS.items()]
    width = max(len(name) for name, _ in rows)
    lines = [
        "bin/pipeline — local harness for Codex, Claude, and Antigravity",
        "",
        "Commands:",
    ]
    lines += [f"  {name:<{width}}  {help_text}" for name, help_text in sorted(rows)]
    lines += ["", "Run a command with --help for its arguments."]
    return "\n".join(lines)


def _resolve(argv: list[str]) -> tuple[tuple[str, ...], tuple[str, str, str], list[str]] | None:
    for width in (2, 1):
        key = tuple(argv[:width])
        if key in COMMANDS:
            return key, COMMANDS[key], argv[width:]
    return None


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0
    resolved = _resolve(arguments)
    if resolved is None:
        print(f"bin/pipeline: unknown command {' '.join(arguments[:2])!r}\n", file=sys.stderr)
        print(_usage(), file=sys.stderr)
        return 2
    key, (module_name, entrypoint, _help), rest = resolved
    module = importlib.import_module(module_name)
    sys.argv = [f"bin/pipeline {' '.join(key)}", *rest]
    return int(getattr(module, entrypoint)() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
