#!/usr/bin/env python3
"""pipeline — the one command surface for a CLI-exclusive kernel.

Before this file the shortest governed invocation was three concepts deep:

    unset GIT_INDEX_FILE
    coordination/bin/pipeline-python pipeline/status.py snapshot

an environment scrub, an interpreter resolver, and a file path, all in front
of the verb.  ``bin/pipeline`` does the scrub and the resolution; this module
turns the remaining file path into a verb:

    pipeline status

Dispatch is deliberately thin.  Each command names an existing module and
calls its ``main`` with ``sys.argv`` already rewritten, so a module keeps
owning its own argument parsing and no option has to be re-declared here.
Modules whose ``main`` takes no argv still work: with ``sys.argv`` set,
``argparse`` reads it the same way it did when the module was run by path.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
for _path in (str(_ROOT), str(_ROOT / "pipeline")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# (module, entrypoint, one-line help). Entrypoint is the callable name so a
# module that never adopted `main` (compact_pair_loop) still routes here.
_MODULE_COMMANDS: dict[tuple[str, ...], tuple[str, str, str]] = {
    ("status",): ("status", "main", "compact current-state snapshot"),
    ("check",): ("governance_verify_all", "main", "full governance aggregate (the completion gate)"),
    ("check", "coordination"): ("check_coordination", "main", "durable coordination state"),
    ("check", "docs"): ("check_doc_claims", "main", "doc-anchor and SHA-reference drift"),
    ("check", "reports"): ("check_go_schema", "main", "frozen and current review-report bytes"),
    ("check", "placeholders"): ("check_placeholders", "main", "unbound adoption placeholders"),
    ("check", "arch"): ("check_arch_freshness", "main", "ARCHITECTURE.md provenance freshness"),
    ("check", "ceremony"): ("check_no_ceremony", "main", "false verification signals and Python growth"),
    ("check", "admission"): ("ci_admission_gate", "main", "authority-surface admission for a range"),
    ("review", "validate"): ("compact_pair_loop", "_main", "validate a request/report pair"),
    ("review", "consume"): ("consume_reviewer_result", "main", "consume a reviewer-result block"),
    ("peer", None): ("peer", "main", "invoke a peer CLI once and record a receipt"),
    ("learn", "index"): ("learning_index", "main", "query the derived episodic index"),
    ("learn", "metrics"): ("learning_metrics", "main", "learning-lifecycle metrics"),
    ("learn", "draft"): ("learning_extract", "main", "draft one learning candidate into scratch"),
    ("checkpoint",): ("draft_checkpoint", "main", "draft one continuity checkpoint into scratch"),
    ("claim",): ("claim_check", "main", "derive the premises a claim's shape demands"),
    ("doctor",): ("protocol_doctor", "main", "read-only protocol validation bundle"),
    ("preflight",): ("harness_preflight", "main", "peer CLI capability preflight"),
    ("target",): ("target_binding", "main", "resolve or check the product target binding"),
    ("metrics",): ("slope_metrics", "main", "execution-health slope over durable events"),
}

# Commands whose implementation is a hardened shell front door. Routing them
# through here keeps one surface without re-implementing the writer fence.
_SHELL_COMMANDS: dict[tuple[str, ...], tuple[str, str]] = {
    ("mail", "send"): ("coordination/bin/send-event", "publish one durable event (body on stdin)"),
    ("mail", "consume"): ("coordination/bin/consume-events", "advance a legacy seat cursor"),
    ("lock", "claim"): ("coordination/bin/claim-lock", "claim a shared lock"),
    ("lock", "release"): ("coordination/bin/release-lock", "release a shared lock"),
    ("probe",): ("coordination/bin/probe-claim", "reduced-context attack on one claim"),
}


# Targets that take no arguments and therefore cannot answer --help
# themselves. Without this, `pipeline check --help` ran the whole governance
# aggregate and exited 0 -- a help request that performs the action instead of
# describing it, while the banner promised "every command accepts its own
# --help".
_ARGLESS = {
    ("check",), ("check", "ceremony"), ("check", "placeholders"), ("check", "arch"),
}


def _usage() -> str:
    lines = ["pipeline — governance kernel for the Claude and Codex CLIs", "", "Commands:"]
    rows: list[tuple[str, str]] = []
    for key, (_module, _entry, blurb) in _MODULE_COMMANDS.items():
        name = " ".join(part for part in key if part)
        rows.append((name + (" <sub>" if key[-1] is None else ""), blurb))
    for key, (_path, blurb) in _SHELL_COMMANDS.items():
        rows.append((" ".join(key), blurb))
    width = max(len(name) for name, _ in rows)
    for name, blurb in sorted(rows):
        lines.append(f"  {name:<{width}}  {blurb}")
    lines += [
        "",
        "Most commands accept their own --help; the argument-less gates",
        "describe themselves instead. bin/pipeline resolves the repository",
        "interpreter and clears GIT_INDEX_FILE before dispatch.",
    ]
    return "\n".join(lines)


def _resolve(argv: list[str]):
    """Longest-prefix match, so `check coordination` beats bare `check`."""

    for width in (2, 1):
        key = tuple(argv[:width])
        if key in _SHELL_COMMANDS:
            return "shell", _SHELL_COMMANDS[key], argv[width:], key
        if key in _MODULE_COMMANDS:
            return "module", _MODULE_COMMANDS[key], argv[width:], key
        # A group declared with a None leaf owns every subcommand under it.
        if width == 2 and (key[0], None) in _MODULE_COMMANDS:
            return "module", _MODULE_COMMANDS[(key[0], None)], argv[1:], (key[0],)
    if len(argv) == 1 and (argv[0], None) in _MODULE_COMMANDS:
        return "module", _MODULE_COMMANDS[(argv[0], None)], [], (argv[0],)
    return None, None, None, None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0
    groups = {key[0] for key in (*_MODULE_COMMANDS, *_SHELL_COMMANDS) if len(key) == 2}
    if len(argv) >= 2 and argv[0] in groups and not argv[1].startswith("-"):
        known = tuple(argv[:2])
        if known not in _MODULE_COMMANDS and known not in _SHELL_COMMANDS:
            subs = sorted(
                key[1] for key in (*_MODULE_COMMANDS, *_SHELL_COMMANDS)
                if len(key) == 2 and key[0] == argv[0] and key[1]
            )
            print(
                f"pipeline {argv[0]}: unknown subcommand {argv[1]!r}; "
                f"expected one of {', '.join(subs)}",
                file=sys.stderr,
            )
            return 2
    kind, spec, rest, key = _resolve(argv)
    if kind is None:
        print(f"pipeline: unknown command {' '.join(argv[:2])!r}\n", file=sys.stderr)
        print(_usage(), file=sys.stderr)
        return 2
    name = " ".join(key)
    if key in _ARGLESS and rest and rest[0] in {"-h", "--help"}:
        blurb = spec[2] if kind == "module" else spec[1]
        print(f"pipeline {name} — {blurb}")
        print("Takes no arguments; run it to perform the check.")
        return 0
    if kind == "shell":
        relative, _blurb = spec
        target = _ROOT / relative
        if not os.access(target, os.X_OK):
            print(f"pipeline {name}: {relative} is not executable", file=sys.stderr)
            return 4
        os.execv(str(target), [str(target), *rest])
    module_name, entry, _blurb = spec
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        print(f"pipeline {name}: {exc}", file=sys.stderr)
        return 4
    sys.argv = [f"pipeline {name}", *rest]
    return int(getattr(module, entry)() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
