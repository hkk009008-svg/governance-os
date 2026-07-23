#!/usr/bin/env python3
"""Interactive Cursor mailbox wrappers that delegate to Pipeline fixed writers.

These wrappers add one thing on top of the canonical ``coordination/bin``
writers: a seat-bound front door for mailbox publish/consume. Readiness-bridge
sessions still require an explicit typed yes on the controlling terminal;
live Cursor dispatch/review seats auto-publish/consume without TTY confirmation. They never reimplement mailbox validation,
fencing, durable replacement, or staging -- every effect is executed by the
existing fixed writer (``send-event`` / ``consume-events``). Publishing a
mailbox event and consuming a seat cursor are separately authorized effects, so
each requires a typed confirmation on the controlling terminal and is denied
from ordinary agent tools by the Cursor seat hook.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from scripts.cursor_auto_relay import live_bound

LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")


class MailboxBindingError(RuntimeError):
    """A Cursor mailbox wrapper cannot proceed without guessing or new authority."""


def resolve_seat(explicit: str | None, environ: Mapping[str, str]) -> str:
    """Resolve the from-seat from an explicit flag, then ``CURSOR_SEAT``."""

    bound = environ.get("CURSOR_SEAT")
    if bound and bound not in LAUNCH_SEATS:
        raise MailboxBindingError(
            f"CURSOR_SEAT is not a live Cursor seat: {bound!r}"
        )
    if explicit and bound and explicit != bound:
        raise MailboxBindingError(
            f"explicit seat {explicit!r} does not match bound CURSOR_SEAT {bound!r}"
        )
    seat = explicit or bound
    if seat not in LAUNCH_SEATS:
        raise MailboxBindingError(
            "resolve the Cursor from-seat via --seat or CURSOR_SEAT "
            f"(one of {', '.join(LAUNCH_SEATS)}); got: {seat!r}"
        )
    return seat


def _writer(root: Path, name: str) -> Path:
    path = root / "coordination" / "bin" / name
    if not path.is_file():
        raise MailboxBindingError(f"fixed writer is unavailable: {path}")
    return path


def build_publish_argv(
    root: Path, *, seat: str, to: str, kind: str, subject: str
) -> list[str]:
    """Compose the exact ``send-event`` argv; validation stays in the writer."""

    if not to or not kind or not subject:
        raise MailboxBindingError("publish requires --to, --kind, and a subject")
    if to == seat:
        raise MailboxBindingError("refusing self-addressed event")
    return [str(_writer(root, "send-event")), seat, to, kind, subject]


def build_consume_argv(root: Path, *, seat: str, extra: Sequence[str]) -> list[str]:
    """Compose the exact ``consume-events`` argv for this seat's cursor."""

    return [str(_writer(root, "consume-events")), seat, *extra]


def _read_tty(prompt: str) -> str:
    try:
        with open("/dev/tty", "r+", encoding="utf-8") as tty:
            tty.write(prompt)
            tty.flush()
            return tty.readline()
    except OSError as exc:
        raise MailboxBindingError(
            "no controlling terminal for interactive confirmation"
        ) from exc


def confirm(
    *,
    action: str,
    detail: str,
    prompt_fn: Callable[[str], str] = _read_tty,
) -> bool:
    """Require a typed ``yes`` on the controlling terminal for an effect."""

    answer = prompt_fn(
        f"{action}: {detail}\n"
        "This performs a separately authorized mailbox effect. Type yes: "
    )
    if answer.strip().casefold() != "yes":
        raise MailboxBindingError(f"{action} was not authorized")
    return True


def _delegate_env() -> dict[str, str]:
    clean = dict(os.environ)
    clean.pop("GIT_INDEX_FILE", None)
    return clean


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cursor-mailbox")
    commands = parser.add_subparsers(dest="command", required=True)

    publish = commands.add_parser("publish")
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--seat")
    publish.add_argument("--to", required=True)
    publish.add_argument("--kind", required=True)
    publish.add_argument("--subject", required=True)

    consume = commands.add_parser("consume")
    consume.add_argument("--dry-run", action="store_true")
    consume.add_argument("--seat")
    consume.add_argument("extra", nargs=argparse.REMAINDER)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    root: Path | None = None,
    stdin_text: str | None = None,
    runner: Callable[..., int] = subprocess.call,
    prompt_fn: Callable[[str], str] = _read_tty,
) -> int:
    args = _parser().parse_args(sys.argv[1:] if argv is None else list(argv))
    repo_root = root if root is not None else Path(__file__).resolve().parents[1]
    try:
        seat = resolve_seat(args.seat, os.environ)
        if args.command == "publish":
            body = sys.stdin.read() if stdin_text is None else stdin_text
            delegate = build_publish_argv(
                repo_root, seat=seat, to=args.to, kind=args.kind, subject=args.subject
            )
            detail = f"{seat} -> {args.to} [{args.kind}] {args.subject}"
            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "operation": "publish",
                            "seat": seat,
                            "argv": delegate,
                            "body_bytes": len(body.encode("utf-8")),
                            "would_confirm": not live_bound(os.environ),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 0
            if not live_bound(os.environ):
                confirm(action="publish", detail=detail, prompt_fn=prompt_fn)
            return runner(delegate, input=body, text=True, env=_delegate_env())
        if args.command == "consume":
            extra = [token for token in (args.extra or []) if token != "--"]
            delegate = build_consume_argv(repo_root, seat=seat, extra=extra)
            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "operation": "consume",
                            "seat": seat,
                            "argv": delegate,
                            "would_confirm": not live_bound(os.environ),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 0
            if not live_bound(os.environ):
                confirm(action="consume", detail=f"advance {seat} cursor", prompt_fn=prompt_fn)
            return runner(delegate, env=_delegate_env())
    except MailboxBindingError as exc:
        print(f"cursor-mailbox: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
