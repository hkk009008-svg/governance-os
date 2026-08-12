#!/usr/bin/env python3
"""Cursor app mailbox front door delegating every effect to fixed writers."""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import codex_protocol_model
import compact_pair_loop
import protocol_mailbox
from cursor_app_binding import (
    DIRECTOR_SEATS,
    OPERATOR_SEATS,
    AppBindingError,
    AppSessionBinding,
    resolve_registered_session,
)

CURSOR_SEATS = frozenset(protocol_mailbox.SEATS)
_MAILBOX_SENT = "coordination/mailbox/sent/"


def _requires_app_approval(seat: str) -> bool:
    """Bound Director/Operator wrappers inherit the seat-start mailbox grant."""

    return seat not in DIRECTOR_SEATS and seat not in OPERATOR_SEATS


class MailboxBindingError(RuntimeError):
    """A Cursor mailbox operation cannot proceed without a proven app seat."""


def _writer(root: Path, name: str) -> Path:
    path = root / "coordination" / "bin" / name
    if not path.is_file():
        raise MailboxBindingError(f"fixed writer is unavailable: {path}")
    return path


def build_publish_argv(
    root: Path, *, seat: str, to: str, kind: str, subject: str
) -> list[str]:
    if not to or not kind or not subject:
        raise MailboxBindingError("publish requires --to, --kind, and --subject")
    if to == seat:
        raise MailboxBindingError("refusing self-addressed event")
    return [str(_writer(root, "send-event")), seat, to, kind, subject]


def validate_publish_model_binding(kind: str, body: str, model_id: str) -> None:
    """Bind Compact Pair model identity to the registered Cursor session."""

    label = {
        "verify-request": "Author model",
        "verification-report": "Reviewer model",
    }.get(kind)
    if label is None:
        return
    occurrences = compact_pair_loop.normalized_field_occurrences(
        body.splitlines(), label
    )
    if len(occurrences) != 1:
        state = "missing" if not occurrences else "duplicate"
        raise MailboxBindingError(f"{state} {label}")
    prefix = f"{label}: "
    line = occurrences[0]
    if not line.startswith(prefix):
        raise MailboxBindingError(f"invalid {label}")
    value = line[len(prefix) :]
    if not value or value != value.strip():
        raise MailboxBindingError(f"invalid {label}")
    if value != model_id:
        raise MailboxBindingError(
            f"{label} must exactly match the registered app model_id"
        )


def build_consume_argv(root: Path, *, seat: str, extra: Sequence[str]) -> list[str]:
    if seat not in CURSOR_SEATS:
        raise MailboxBindingError(f"{seat} holds no mailbox cursor")
    return [str(_writer(root, "consume-events")), seat, *extra]


def read_body_file(root: Path, value: Path) -> str:
    """Read one regular, non-symlink scratch body with a bounded size."""

    candidate = value.expanduser()
    raw_path = candidate if candidate.is_absolute() else root / candidate
    path = Path(os.path.abspath(raw_path))
    scratch = (root / ".pytest-verify-tmp").resolve()
    try:
        relative = path.relative_to(scratch)
        path.resolve(strict=False).relative_to(scratch)
    except ValueError as exc:
        raise MailboxBindingError("--body-file must be under .pytest-verify-tmp") from exc
    current = scratch
    try:
        for component in relative.parts[:-1]:
            current = current / component
            if current.is_symlink():
                raise MailboxBindingError(
                    "--body-file must not traverse a symlink"
                )
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(
            os, "O_NOFOLLOW", 0
        )
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise MailboxBindingError(
            "--body-file must be a regular non-symlink file"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise MailboxBindingError(
                "--body-file must be a regular non-symlink file"
            )
        if opened.st_size > 1024 * 1024:
            raise MailboxBindingError("--body-file exceeds the 1 MiB limit")
        raw = os.read(descriptor, opened.st_size + 1)
        if len(raw) != opened.st_size:
            raise MailboxBindingError("--body-file changed while reading")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MailboxBindingError("--body-file is not UTF-8") from exc
    finally:
        os.close(descriptor)


def _clean_git_env(environ: Mapping[str, str]) -> dict[str, str]:
    return {key: value for key, value in environ.items() if not key.startswith("GIT_")}


def _git(root: Path, environ: Mapping[str, str], *args: str) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), *args],
        env=_clean_git_env(environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise MailboxBindingError(detail or f"git {' '.join(args)} failed")
    return result.stdout


def _mailbox_tips(root: Path, environ: Mapping[str, str]) -> list[str]:
    output = _git(
        root,
        environ,
        "for-each-ref",
        "--format=%(objectname)",
        "refs/heads/cursor-seat/",
    )
    tips = {line for line in output.splitlines() if len(line) == 40}
    head = _git(root, environ, "rev-parse", "HEAD").strip()
    if len(head) == 40:
        tips.add(head)
    return sorted(tips)


def _committed_mailbox_events(
    root: Path, environ: Mapping[str, str]
) -> list[tuple[str, str]]:
    events: dict[str, str] = {}
    for tip in _mailbox_tips(root, environ):
        output = _git(
            root,
            environ,
            "ls-tree",
            "-r",
            "--name-only",
            tip,
            "--",
            "coordination/mailbox/sent",
        )
        for line in output.splitlines():
            if not line.startswith(_MAILBOX_SENT) or not line.endswith(".md"):
                continue
            commit = _introduction_commit(root, environ, line, tip=tip)
            previous = events.get(line)
            if previous is not None and previous != commit:
                raise MailboxBindingError(
                    f"mailbox path has conflicting introduction commits: {line}"
                )
            events[line] = commit
    return sorted(events.items(), reverse=True)


def _introduction_commit(
    root: Path,
    environ: Mapping[str, str],
    path: str,
    *,
    tip: str,
) -> str:
    commit = _git(
        root,
        environ,
        "log",
        "--diff-filter=A",
        "--format=%H",
        "-1",
        tip,
        "--",
        path,
    ).strip()
    if len(commit) != 40:
        raise MailboxBindingError(f"cannot resolve introduction commit for {path}")
    return commit


def _reported_request_refs(
    root: Path,
    environ: Mapping[str, str],
    events: Sequence[tuple[str, str]],
) -> frozenset[str]:
    """Collect request refs suppressed only by valid canonical reports.

    Malformed reports and reports that fail structural validation are skipped.
    They must neither abort next-review nor mark a request as already reviewed.
    A verdict a later valid report supersedes is dead: it suppresses nothing,
    though its own supersession still counts.
    """
    valid: list[tuple[str, str, compact_pair_loop.VerificationReport]] = []
    scratch = root / ".pytest-verify-tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    for path, commit in events:
        if not path.endswith("-verification-report.md"):
            continue
        text = _git(root, environ, "show", f"{commit}:{path}")
        temporary_name = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix=".cursor-report.",
                suffix=".md",
                dir=scratch,
                delete=False,
            ) as temporary:
                temporary.write(text)
                temporary_name = temporary.name
            try:
                report = compact_pair_loop.parse_verification_report_candidate(
                    root,
                    temporary_name,
                    path,
                )
            except compact_pair_loop.CompactPairError:
                continue
            violations = compact_pair_loop.validate_report_structure(root, report)
            if violations:
                continue
            valid.append((path, commit, report))
        finally:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)
    superseded = {
        f"{path}@{commit}"
        for _, _, report in valid
        if report.supersedes is not None
        for path, commit in (report.supersedes,)
    }
    return frozenset(
        f"{report.request_path}@{report.request_commit}"
        for path, commit, report in valid
        if f"{path}@{commit}" not in superseded
    )


def next_verify_request(
    root: Path,
    *,
    seat: str,
    environ: Mapping[str, str],
) -> compact_pair_loop.VerifyRequest:
    if seat not in OPERATOR_SEATS:
        raise MailboxBindingError("next-review is available only to Operator seats")
    events = _committed_mailbox_events(root, environ)
    reported = _reported_request_refs(root, environ, events)
    marker = f"-to-{seat}-verify-request.md"
    for path, commit in events:
        if not path.endswith(marker):
            continue
        ref = f"{path}@{commit}"
        if ref in reported:
            continue
        try:
            request = compact_pair_loop.parse_verify_request(root, path, commit)
        except compact_pair_loop.CompactPairError as exc:
            raise MailboxBindingError(f"latest pending verify-request is invalid: {exc}") from exc
        if request.assigned_operator != seat:
            raise MailboxBindingError("verify-request recipient does not match assigned Operator")
        return request
    raise MailboxBindingError(f"no pending committed verify-request for {seat}")


def _delegate_env(environ: Mapping[str, str]) -> dict[str, str]:
    clean = dict(environ)
    clean.pop("GIT_INDEX_FILE", None)
    return clean


def _returncode(result: object) -> int:
    if isinstance(result, int):
        return result
    value = getattr(result, "returncode", None)
    if not isinstance(value, int):
        raise MailboxBindingError("mailbox delegate returned no exit status")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cursor-mailbox")
    commands = parser.add_subparsers(dest="command", required=True)

    publish = commands.add_parser("publish")
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--to", required=True)
    publish.add_argument("--kind", required=True)
    publish.add_argument("--subject", required=True)
    publish.add_argument("--body-file", required=True, type=Path)

    consume = commands.add_parser("consume")
    consume.add_argument("--dry-run", action="store_true")
    consume.add_argument("extra", nargs=argparse.REMAINDER)

    commands.add_parser("next-review")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    root: Path | None = None,
    environ: Mapping[str, str] | None = None,
    runner: Callable[..., object] = subprocess.run,
    binding_resolver: Callable[[Path, Mapping[str, str]], AppSessionBinding] = (
        resolve_registered_session
    ),
) -> int:
    args = _parser().parse_args(sys.argv[1:] if argv is None else list(argv))
    repo_root = (root if root is not None else Path(__file__).resolve().parents[1]).resolve()
    env = os.environ if environ is None else environ
    try:
        try:
            binding = binding_resolver(repo_root, env)
        except AppBindingError as exc:
            raise MailboxBindingError(str(exc)) from exc
        if args.command == "publish":
            body = read_body_file(repo_root, args.body_file)
            validate_publish_model_binding(args.kind, body, binding.model_id)
            delegate = build_publish_argv(
                repo_root,
                seat=binding.seat,
                to=args.to,
                kind=args.kind,
                subject=args.subject,
            )
            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "operation": "publish",
                            "seat": binding.seat,
                            "model_id": binding.model_id,
                            "conversation_id": binding.conversation_id,
                            "argv": delegate,
                            "body_file": str(args.body_file),
                            "body_bytes": len(body.encode("utf-8")),
                            "requires_app_approval": _requires_app_approval(
                                binding.seat
                            ),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 0
            return _returncode(
                runner(
                    delegate,
                    input=body,
                    text=True,
                    env=_delegate_env(env),
                    check=False,
                )
            )
        if args.command == "consume":
            extra = [token for token in (args.extra or []) if token != "--"]
            delegate = build_consume_argv(
                repo_root, seat=binding.seat, extra=extra
            )
            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "operation": "consume",
                            "seat": binding.seat,
                            "conversation_id": binding.conversation_id,
                            "argv": delegate,
                            "requires_app_approval": _requires_app_approval(
                                binding.seat
                            ),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 0
            return _returncode(
                runner(delegate, env=_delegate_env(env), check=False)
            )
        if args.command == "next-review":
            request = next_verify_request(
                repo_root, seat=binding.seat, environ=env
            )
            author_family = codex_protocol_model.model_family(request.author_model)
            reviewer_family = codex_protocol_model.model_family(binding.model_id)
            model_independence = codex_protocol_model.models_are_independent(
                request.author_model, binding.model_id
            )
            profile = codex_protocol_model.review_profile_for(request.risk_class)
            if profile.requires_different_model and not model_independence:
                raise MailboxBindingError(
                    "high-risk review requires recognized independent model families"
                )
            print(
                json.dumps(
                    {
                        "verify_request": f"{request.path}@{request.trigger_commit}",
                        "reviewed_repository": request.reviewed_repository,
                        "reviewed_base": request.reviewed_base,
                        "reviewed_head": request.reviewed_head,
                        "author_seat": request.author_seat,
                        "author_model": request.author_model,
                        "author_model_family": author_family,
                        "assigned_operator": request.assigned_operator,
                        "reviewer_model": binding.model_id,
                        "reviewer_model_family": reviewer_family,
                        "model_independence": model_independence,
                        "outcome": request.outcome,
                        "finding_refs": list(request.finding_refs),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
    except MailboxBindingError as exc:
        print(f"cursor-mailbox: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
