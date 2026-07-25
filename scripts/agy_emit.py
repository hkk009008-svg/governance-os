#!/usr/bin/env python3
"""Streamlined CLI mailbox event emitter for Antigravity (AGY).

Constructs schema-compliant mailbox events, invokes coordination/bin/send-event,
and commits the generated event with an explicit git pathspec.

Usage:
    .venv/bin/python scripts/agy_emit.py --to all --kind coordination --subject "Subject" --body "Body..."
    cat body.txt | .venv/bin/python scripts/agy_emit.py --to director --kind discussion --subject "Subject"
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _clean_git_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"LANG": "C", "LC_ALL": "C"})
    return env


def emit_event(
    *,
    sender: str = "agy",
    recipient: str,
    kind: str,
    subject: str,
    body: str,
    root: Path | None = None,
) -> Path:
    repo_root = (root or _REPO_ROOT).resolve()
    send_event_bin = repo_root / "coordination" / "bin" / "send-event"
    if not send_event_bin.exists():
        raise RuntimeError(f"send-event binary not found at {send_event_bin}")

    cmd = [str(send_event_bin), sender, recipient, kind, subject]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        input=body.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        err_msg = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"send-event failed (code {proc.returncode}): {err_msg}")

    stdout = proc.stdout.decode("utf-8", errors="replace").strip()
    match = re.search(r"created\s+(coordination/mailbox/sent/[^\s]+\.md)", stdout)
    if not match:
        raise RuntimeError(f"Could not parse created event file path from output: {stdout}")

    relative_path = match.group(1)
    full_path = repo_root / relative_path

    # Commit event with explicit pathspec
    commit_msg = f"coord({sender}): {subject}"
    commit_proc = subprocess.run(
        ["git", "commit", "-m", commit_msg, "--", relative_path],
        cwd=repo_root,
        env=_clean_git_env(),
        capture_output=True,
        check=False,
    )
    if commit_proc.returncode != 0:
        err_msg = commit_proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git commit failed for {relative_path}: {err_msg}")

    return full_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Streamlined AGY mailbox event emitter + explicit git commit."
    )
    parser.add_argument("--from", "-f", dest="sender", default="agy", help="Sender seat (default: agy)")
    parser.add_argument("--to", "-t", required=True, help="Recipient seat or 'all'")
    parser.add_argument("--kind", "-k", default="coordination", help="Mailbox kind (default: coordination)")
    parser.add_argument("--subject", "-s", required=True, help="Event subject")
    parser.add_argument("--body", "-b", help="Event body string (reads stdin if omitted)")
    parser.add_argument("--root", help="Repository root directory")

    parser.add_argument(
        "--dispatch",
        action="store_true",
        default=True,
        help="Automatically trigger next seat dispatch (default: True)",
    )
    parser.add_argument(
        "--no-dispatch",
        action="store_false",
        dest="dispatch",
        help="Disable automatic seat dispatch",
    )

    args = parser.parse_args(argv)

    if args.body is not None:
        body_text = args.body
    else:
        if sys.stdin.isatty():
            print("Error: --body omitted and stdin is a TTY.", file=sys.stderr)
            return 1
        body_text = sys.stdin.read()

    if not body_text.endswith("\n"):
        body_text += "\n"

    repo_root = Path(args.root) if args.root else _REPO_ROOT

    try:
        created_path = emit_event(
            sender=args.sender,
            recipient=args.to,
            kind=args.kind,
            subject=args.subject,
            body=body_text,
            root=repo_root,
        )
        print(f"OK — emitted and committed event: {created_path.as_posix()}")

        # AGY Automatic Seat Routing
        valid_seats = {"director", "director2", "operator", "operator2", "coordinator"}
        if args.dispatch and args.to in valid_seats:
            dispatch_cmd = f".venv/bin/python scripts/agy_seat_launcher.py {args.to}"
            print(f"[AGY AUTO-ROUTING] Target seat '{args.to}' dispatched: {dispatch_cmd}")

        return 0
    except Exception as exc:
        print(f"AGY EMIT FAIL — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
