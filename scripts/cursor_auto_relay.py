#!/usr/bin/env python3
"""Cursor-only auto-relay for live seat outbox results."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
LIVE_OPERATIONS = frozenset({"dispatch", "review"})
_FOREIGN_ENV_PREFIXES = ("AGY_", "CODEX_", "CLAUDE_", "ANTIGRAVITY_")
_FENCE = chr(96) * 3
_RELAY_FENCE = re.compile(_FENCE + r"cursor-relay\s*\n(.*?)\n" + _FENCE, re.DOTALL)
_RELAY_REQUIRED = frozenset({"to", "kind", "subject"})


class RelayError(RuntimeError):
    """Auto-relay cannot proceed without guessing or new authority."""


def live_bound(environ: Mapping[str, str]) -> bool:
    seat = environ.get("CURSOR_SEAT", "")
    if seat not in LAUNCH_SEATS:
        return False
    if environ.get("CURSOR_OPERATION") not in LIVE_OPERATIONS:
        return False
    index = environ.get("GIT_INDEX_FILE", "")
    return bool(index) and index.endswith("index-cursor-" + seat)


def may_auto_publish(environ: Mapping[str, str]) -> bool:
    return live_bound(environ) or environ.get("CURSOR_RELAY_CHAIN") == "1"


def parse_relay_directive(text: str) -> dict[str, object]:
    match = _RELAY_FENCE.search(text)
    if not match:
        raise RelayError("no cursor-relay fence found in text")
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise RelayError("cursor-relay fence is not valid JSON: " + str(exc)) from exc
    if not isinstance(payload, dict):
        raise RelayError("cursor-relay payload must be a JSON object")
    missing = sorted(key for key in _RELAY_REQUIRED if not payload.get(key))
    if missing:
        raise RelayError("cursor-relay missing required fields: " + ", ".join(missing))
    return payload


def _writer(root: Path, name: str) -> Path:
    path = root / "coordination" / "bin" / name
    if not path.is_file():
        raise RelayError("fixed writer is unavailable: " + str(path))
    return path


def build_publish_argv(root: Path, *, seat: str, to: str, kind: str, subject: str) -> list[str]:
    if seat not in LAUNCH_SEATS:
        raise RelayError("unsupported from-seat: " + repr(seat))
    if not to or not kind or not subject:
        raise RelayError("publish requires to, kind, and subject")
    if to == seat:
        raise RelayError("refusing self-addressed relay publish")
    return [str(_writer(root, "send-event")), seat, to, kind, subject]


def _delegate_env(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    clean = dict(environ or os.environ)
    clean.pop("GIT_INDEX_FILE", None)
    return clean


def publish(
    root: Path,
    *,
    seat: str,
    to: str,
    kind: str,
    subject: str,
    body: str,
    environ: Mapping[str, str] | None = None,
    runner: Callable[..., int] = subprocess.call,
) -> int:
    env = dict(environ or os.environ)
    if not may_auto_publish(env):
        raise RelayError(
            "relay publish requires a live Cursor seat binding or CURSOR_RELAY_CHAIN=1"
        )
    argv = build_publish_argv(root, seat=seat, to=to, kind=kind, subject=subject)
    return runner(argv, input=body, text=True, env=_delegate_env(env))


def wake_operation(*, to: str, kind: str) -> str:
    if to in {"operator", "operator2"} and kind == "verify-request":
        return "review"
    return "dispatch"


def build_wake_argv(
    root: Path,
    *,
    operation: str,
    seat: str,
    directive: Mapping[str, object],
) -> list[str]:
    if seat not in LAUNCH_SEATS:
        raise RelayError("unsupported wake seat: " + repr(seat))
    argv = [str(_writer(root, "cursor-seat")), operation, seat]
    if operation == "review":
        ref = directive.get("verify_request") or directive.get("trigger_ref")
        if not ref:
            raise RelayError("review wake requires verify_request or trigger_ref")
        argv.extend(["--verify-request", str(ref)])
    else:
        ref = directive.get("trigger_ref")
        if not ref:
            raise RelayError("dispatch wake requires trigger_ref")
        argv.extend(["--trigger-ref", str(ref)])
    route_revision = directive.get("route_revision")
    if route_revision is not None:
        argv.extend(["--route-revision", str(route_revision)])
    return argv


def _clean_child_env(environ: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in environ.items()
        if not key.startswith(_FOREIGN_ENV_PREFIXES)
    }


def wake_seat(
    root: Path,
    *,
    directive: Mapping[str, object],
    environ: Mapping[str, str] | None = None,
    runner: Callable[..., int] = subprocess.call,
    dry_run: bool = False,
) -> tuple[list[str], int]:
    env = dict(environ or os.environ)
    to = str(directive["to"])
    kind = str(directive["kind"])
    operation = wake_operation(to=to, kind=kind)
    argv = build_wake_argv(root, operation=operation, seat=to, directive=directive)
    if dry_run:
        return argv, 0
    child = _clean_child_env(env)
    child["CURSOR_RELAY_CHAIN"] = "1"
    return argv, runner(argv, env=child)


def _load_outbox(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RelayError("cannot read outbox artifact " + str(path) + ": " + str(exc)) from exc
    if not isinstance(payload, dict):
        raise RelayError("outbox artifact must be a JSON object")
    return payload


def _directive_from_outbox(payload: Mapping[str, object]) -> dict[str, object]:
    relay = payload.get("relay")
    if isinstance(relay, dict):
        directive = dict(relay)
    else:
        result = payload.get("result")
        if not isinstance(result, str):
            raise RelayError("outbox has no relay key or string result")
        directive = parse_relay_directive(result)
    missing = sorted(key for key in _RELAY_REQUIRED if not directive.get(key))
    if missing:
        raise RelayError("relay directive missing required fields: " + ", ".join(missing))
    return directive


def write_last_relay(
    root: Path,
    *,
    seat: str,
    outbox_path: Path,
    directive: Mapping[str, object],
    published: bool,
    woke: bool,
) -> Path:
    relay_dir = root / ".cursor" / "runtime" / "relay"
    relay_dir.mkdir(parents=True, exist_ok=True)
    path = relay_dir / "last-relay.json"
    payload = {
        "seat": seat,
        "outbox": str(outbox_path),
        "to": directive.get("to"),
        "kind": directive.get("kind"),
        "subject": directive.get("subject"),
        "published": published,
        "woke": woke,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def relay_from_outbox(
    root: Path,
    *,
    outbox_path: Path,
    environ: Mapping[str, str] | None = None,
    wake: bool = True,
    dry_run: bool = False,
    runner: Callable[..., int] = subprocess.call,
) -> dict[str, object]:
    env = dict(environ or os.environ)
    if not may_auto_publish(env):
        raise RelayError(
            "relay from outbox requires a live Cursor seat binding or CURSOR_RELAY_CHAIN=1"
        )
    payload = _load_outbox(outbox_path)
    seat = str(payload.get("seat") or env.get("CURSOR_SEAT") or "")
    if seat not in LAUNCH_SEATS:
        raise RelayError("outbox seat is not a live Cursor seat")
    directive = _directive_from_outbox(payload)
    body = str(directive.get("body") or payload.get("result") or "")
    publish_argv = build_publish_argv(
        root,
        seat=seat,
        to=str(directive["to"]),
        kind=str(directive["kind"]),
        subject=str(directive["subject"]),
    )
    wake_argv = None
    published = False
    woke = False
    if dry_run:
        if wake and directive.get("wake", True):
            wake_argv = build_wake_argv(
                root,
                operation=wake_operation(
                    to=str(directive["to"]), kind=str(directive["kind"])
                ),
                seat=str(directive["to"]),
                directive=directive,
            )
        return {
            "seat": seat,
            "publish_argv": publish_argv,
            "wake_argv": wake_argv,
            "body_bytes": len(body.encode("utf-8")),
        }
    rc = publish(
        root,
        seat=seat,
        to=str(directive["to"]),
        kind=str(directive["kind"]),
        subject=str(directive["subject"]),
        body=body,
        environ=env,
        runner=runner,
    )
    if rc != 0:
        raise RelayError("send-event failed with exit code " + str(rc))
    published = True
    if wake and directive.get("wake", True):
        wake_argv, wake_rc = wake_seat(
            root, directive=directive, environ=env, runner=runner, dry_run=False
        )
        if wake_rc != 0:
            raise RelayError("cursor-seat wake failed with exit code " + str(wake_rc))
        woke = True
    last = write_last_relay(
        root,
        seat=seat,
        outbox_path=outbox_path,
        directive=directive,
        published=published,
        woke=woke,
    )
    return {
        "seat": seat,
        "publish_argv": publish_argv,
        "wake_argv": wake_argv,
        "last_relay": str(last),
        "published": published,
        "woke": woke,
    }


def maybe_auto_relay(
    root: Path,
    *,
    outbox_path: Path,
    environ: Mapping[str, str] | None = None,
    runner: Callable[..., int] = subprocess.call,
) -> dict[str, object] | None:
    env = dict(environ or os.environ)
    if not live_bound(env):
        return None
    try:
        payload = _load_outbox(outbox_path)
        if isinstance(payload.get("relay"), dict):
            directive = _directive_from_outbox(payload)
        else:
            result = payload.get("result")
            if not isinstance(result, str) or _RELAY_FENCE.search(result) is None:
                return None
            directive = parse_relay_directive(result)
    except RelayError:
        return None
    return relay_from_outbox(
        root,
        outbox_path=outbox_path,
        environ=env,
        wake=bool(directive.get("wake", True)),
        dry_run=False,
        runner=runner,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cursor-relay")
    commands = parser.add_subparsers(dest="command", required=True)
    publish = commands.add_parser("publish")
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--seat")
    publish.add_argument("--to", required=True)
    publish.add_argument("--kind", required=True)
    publish.add_argument("--subject", required=True)
    outbox = commands.add_parser("from-outbox")
    outbox.add_argument("--dry-run", action="store_true")
    outbox.add_argument("--wake", action="store_true", default=True)
    outbox.add_argument("--no-wake", action="store_false", dest="wake")
    outbox.add_argument("outbox", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(sys.argv[1:] if argv is None else list(argv))
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == "publish":
            body = sys.stdin.read()
            seat = args.seat or os.environ.get("CURSOR_SEAT", "")
            if seat not in LAUNCH_SEATS:
                raise RelayError("resolve from-seat via --seat or CURSOR_SEAT")
            argv_publish = build_publish_argv(
                root, seat=seat, to=args.to, kind=args.kind, subject=args.subject
            )
            if args.dry_run:
                print(json.dumps({
                    "operation": "publish",
                    "seat": seat,
                    "argv": argv_publish,
                    "body_bytes": len(body.encode("utf-8")),
                    "would_auto_publish": may_auto_publish(os.environ),
                }, indent=2, sort_keys=True))
                return 0
            return publish(
                root,
                seat=seat,
                to=args.to,
                kind=args.kind,
                subject=args.subject,
                body=body,
            )
        if args.command == "from-outbox":
            result = relay_from_outbox(
                root, outbox_path=args.outbox, wake=args.wake, dry_run=args.dry_run
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
    except RelayError as exc:
        print("cursor-relay: " + str(exc), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
