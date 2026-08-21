#!/usr/bin/env python3
"""One-shot peer invocation: the CLI-exclusive replacement for the bridge.

The mechanism this replaces was a persistent Agent-SDK peer started over MCP
and addressed through Claude Desktop's cross-session plane. It was bound to a
desktop host, held a per-instance budget open, and -- by its own contract --
"reports no delivery ack": a send could succeed and leave delivery unknown.

Here the peer is a child process. The verb is one verb, the direction is
whichever terminal you are sitting in, and the child's exit code and captured
output ARE the acknowledgement the bridge never had.

Every invocation writes a receipt under coordination/peer/<task>/ recording
the argv hash, the prompt hash, the exit code, the duration, and the model the
peer's OWN output reported -- not the model the caller asked for. Review
identity in this repository has always been DECLARED by the author ("a
configured model name is runtime evidence, not cryptographic provider
attestation"). A receipt is still not attestation -- whoever can write the
file can forge it -- but it is evidence the author did not simply type.

Running this spends provider budget. The command prints the exact argv before
launching, and --dry-run prints it without launching at all.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field, replace
from pathlib import Path

from peer_backends import AGY_ROLES, BACKENDS, PeerError, Spec, build, reported_result
from peer_receipt import RECEIPTS, next_seq, receipt_path, validate_task, write_receipt

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUT_S = 900
DEFAULT_MAX_USD = 1.00


@dataclass
class Outcome:
    side: str
    role: str
    task: str
    argv: list[str]
    exit_code: int
    duration_s: float
    prompt_sha256: str
    result: str = ""
    model_reported: str | None = None
    cost_usd: float | None = None
    advisory: bool = False
    notes: list[str] = field(default_factory=list)


def _read_last_message(message: Path) -> tuple[str, str | None]:
    """Read only a regular file this child created, never through a symlink.

    A unique name stopped the ordinary stale-reuse case. It did not stop the
    class: `is_file()` and `read_text()` both follow symlinks, so pointing the
    generated path at a prior answer made that answer this run's result. Open
    with O_NOFOLLOW so the kernel refuses the indirection, and treat every
    refusal as absence rather than as content.
    """

    try:
        handle = os.open(message, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return "", "codex wrote no last-message file; this run produced no result"
    except OSError as exc:
        return "", f"refusing to read the last-message path ({exc}); no result"
    try:
        with os.fdopen(handle, "r", encoding="utf-8") as opened:
            return opened.read(), None
    finally:
        message.unlink(missing_ok=True)


def run(spec: Spec, prompt: str, *, runner=None) -> Outcome:
    runner = runner if runner is not None else subprocess.run
    # The id is settled by the caller BEFORE the argv is built and shown. A
    # default is filled here only for direct library callers who never printed
    # anything; main() always supplies one, so what it prints is what runs.
    if spec.invocation_id == "0":
        spec = replace(spec, invocation_id=uuid.uuid4().hex)
    invocation = build(spec)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    began = time.monotonic()
    try:
        completed = runner(
            invocation.argv,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=spec.timeout_s,
            cwd=str(spec.cwd),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Outcome(
            spec.side, spec.role, spec.task, invocation.argv, 124,
            time.monotonic() - began,
            hashlib.sha256(prompt.encode()).hexdigest(),
            advisory=invocation.advisory,
            notes=[f"peer exceeded --timeout {spec.timeout_s}s; no result"],
        )
    stdout = completed.stdout or ""
    model, cost, result, notes = reported_result(spec.side, stdout)
    if invocation.last_message_file:
        result, message_note = _read_last_message(Path(invocation.last_message_file))
        if message_note:
            notes.append(message_note)
    if completed.returncode != 0 and completed.stderr:
        notes.append(f"stderr: {completed.stderr.strip()[:400]}")
    return Outcome(
        spec.side, spec.role, spec.task, invocation.argv, completed.returncode,
        time.monotonic() - began,
        hashlib.sha256(prompt.encode()).hexdigest(),
        result=result, model_reported=model, cost_usd=cost,
        advisory=invocation.advisory, notes=notes,
    )


def _read_prompt(args) -> str:
    if args.prompt is not None:
        return args.prompt
    if args.prompt_file == "-":
        return sys.stdin.read()
    return Path(args.prompt_file).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pipeline peer", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="invoke one peer once and record a receipt")
    ask.add_argument("side", choices=sorted(BACKENDS))
    ask.add_argument("--task", required=True, help="work-unit id; receipts group under it")
    ask.add_argument("--role", default="peer", help="claude/codex: free label. agy: one of " + ", ".join(AGY_ROLES))
    group = ask.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt")
    group.add_argument("--prompt-file", help="path, or - for stdin")
    ask.add_argument("--model", default=None)
    ask.add_argument("--cwd", default=str(ROOT))
    ask.add_argument("--write", action="store_true", help="allow the peer to edit files")
    ask.add_argument("--max-usd", type=float, default=DEFAULT_MAX_USD)
    ask.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    ask.add_argument("--dry-run", action="store_true", help="print the argv and exit without launching")

    listing = sub.add_parser("receipts", help="list recorded peer invocations")
    listing.add_argument("--task", default=None)

    args = parser.parse_args(argv)
    if args.command == "receipts":
        try:
            base = (
                ROOT / RECEIPTS / validate_task(args.task)
                if args.task
                else ROOT / RECEIPTS
            )
        except PeerError as exc:
            print(f"pipeline peer: {exc}", file=sys.stderr)
            return 2
        if not base.exists():
            print(f"no peer receipts under {base.relative_to(ROOT)}")
            return 0
        for path in sorted(base.rglob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            print(
                f"{path.relative_to(ROOT)}  {payload['side']:<6} {payload['role']:<10} "
                f"exit={payload['exit_code']} model={payload['model_reported']}"
            )
        return 0

    try:
        validate_task(args.task)
    except PeerError as exc:
        print(f"pipeline peer: {exc}", file=sys.stderr)
        return 2
    scratch = Path(os.environ.get("TMPDIR", "/tmp"))
    spec = Spec(
        side=args.side, role=args.role, task=args.task,
        cwd=Path(args.cwd).resolve(), scratch=scratch, model=args.model,
        read_only=not args.write, max_usd=args.max_usd, timeout_s=args.timeout,
        # Settled here, before build() and before the argv is printed, so the
        # proposed invocation and the executed one are the same bytes.
        invocation_id=uuid.uuid4().hex,
    )
    try:
        invocation = build(spec)
    except PeerError as exc:
        print(f"pipeline peer: {exc}", file=sys.stderr)
        return 2
    print("$ " + " ".join(invocation.argv), file=sys.stderr)
    if args.dry_run:
        print("dry run: nothing launched", file=sys.stderr)
        return 0
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    outcome = run(spec, _read_prompt(args))
    path = write_receipt(ROOT, outcome, started)
    print(f"receipt: {path.relative_to(ROOT)}", file=sys.stderr)
    if outcome.result:
        print(outcome.result)
    for note in outcome.notes:
        print(f"note: {note}", file=sys.stderr)
    return 0 if outcome.exit_code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
