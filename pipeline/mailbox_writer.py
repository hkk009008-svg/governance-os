#!/usr/bin/env python3
"""Atomic writer for the two durable formal-review artifact kinds."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Collection, Iterator

import compact_pair_loop
import protocol_mailbox


ROOT = Path(__file__).resolve().parent.parent
FORMAL_REVIEW_KINDS = frozenset({"verify-request", "verification-report"})
_LOCK_NAME = "pipeline-mailbox-writer.lock"
_GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "LANG": "C",
    "LC_ALL": "C",
    "HOME": "/var/empty",
    "XDG_CONFIG_HOME": "/var/empty",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
}


class MailboxWriterError(RuntimeError):
    pass


def sanitized_git_environment() -> dict[str, str]:
    return dict(_GIT_ENV)


def _git(root: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    import subprocess

    result = subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "--literal-pathspecs",
            "-C",
            str(root),
            *arguments,
        ],
        input=input_bytes,
        capture_output=True,
        check=False,
        env=sanitized_git_environment(),
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise MailboxWriterError(detail or f"git {arguments[0]} failed")
    return result.stdout


@contextlib.contextmanager
def writer_fence(repo_root: Path | str) -> Iterator[None]:
    root = Path(repo_root).resolve(strict=True)
    common = Path(
        _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
        .decode("utf-8", "strict")
        .strip()
    ).resolve(strict=True)
    descriptor = os.open(
        common / _LOCK_NAME,
        os.O_CREAT
        | os.O_RDWR
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        os.fchmod(descriptor, 0o600)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise MailboxWriterError("writer lock is not a regular file")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def new_write_envelope_problem(kind: str, sender: str, recipient: str) -> str | None:
    if kind not in FORMAL_REVIEW_KINDS:
        return "Git mailbox accepts only verify-request and verification-report"
    return protocol_mailbox.formal_review_route_problem(kind, sender, recipient)


def validate_event_envelope_bytes(
    root: Path,
    raw: bytes,
    relative: str,
    *,
    kinds: Collection[str] | None = None,
) -> re.Match[str]:
    match = protocol_mailbox.EVENT_NAME_RE.fullmatch(Path(relative).name)
    if match is None or Path(relative).parent.as_posix() != "coordination/mailbox/sent":
        raise MailboxWriterError("artifact path is not canonical")
    if len(raw) > compact_pair_loop.MAX_EVENT_BYTES or b"\x00" in raw:
        raise MailboxWriterError("artifact is not one bounded text event")
    try:
        lines = raw.decode("utf-8", "strict").splitlines()
    except UnicodeDecodeError as exc:
        raise MailboxWriterError("artifact is not UTF-8") from exc
    allowed = frozenset(kinds) if kinds is not None else protocol_mailbox.load_known_kinds(root)
    if match.group("kind") not in allowed:
        raise MailboxWriterError("artifact kind is not registered")
    stamp = match.group("stamp")
    when = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    sender = match.group("sender")
    recipient = match.group("recipient")
    expected_header = f"# {sender.capitalize()} → {recipient.capitalize()}: "
    expected_envelope_online = f"**When:** {when} · **From:** {sender} (online)"
    expected_envelope_plain = f"**When:** {when} · **From:** {sender}"
    if (
        len(lines) < 5
        or not lines[0].startswith(expected_header)
        or lines[1] != ""
        or (lines[2] != expected_envelope_online and lines[2] != expected_envelope_plain)
        or lines[3] != ""
        or sum(line.startswith("# ") for line in lines) != 1
        or sum(line.startswith("**When:** ") for line in lines) != 1
    ):
        raise MailboxWriterError("artifact envelope does not match filename")
    cursor_lines = sum(line.startswith("Cursor at send: ") for line in lines)
    if cursor_lines > 1:
        raise MailboxWriterError("artifact envelope has duplicate cursor declaration")
    if cursor_lines == 1 and lines[-1] != "Cursor at send: cursorless":
        raise MailboxWriterError("artifact envelope cursor must be cursorless at end")
    return match


def validate_event_candidate_bytes(root: Path, raw: bytes, relative: str) -> None:
    match = validate_event_envelope_bytes(root, raw, relative)
    problem = new_write_envelope_problem(
        match.group("kind"), match.group("sender"), match.group("recipient")
    )
    if problem:
        raise MailboxWriterError(problem)
    try:
        if match.group("kind") == "verify-request":
            request = compact_pair_loop._parse_request_bytes(root, relative, raw, "")
            violations = compact_pair_loop.validate_request_candidate(root, request)
        else:
            report = compact_pair_loop._parse_report_bytes(root, relative, raw)
            violations = compact_pair_loop.validate_report(root, report)
    except compact_pair_loop.CompactPairError as exc:
        raise MailboxWriterError(str(exc)) from exc
    if violations:
        raise MailboxWriterError("; ".join(violations))


def _event_bytes(
    stamp: str, sender: str, recipient: str, subject: str, body: str
) -> bytes:
    when = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    content = (
        f"# {sender.capitalize()} → {recipient.capitalize()}: {subject}\n\n"
        f"**When:** {when} · **From:** {sender} (online)\n\n"
        f"{body.rstrip()}\n\nCursor at send: cursorless\n"
    )
    return content.encode("utf-8")


def publish(
    root: Path,
    *,
    sender: str,
    recipient: str,
    kind: str,
    subject: str,
    body: str,
) -> str:
    root = root.resolve(strict=True)
    if not subject.strip() or subject != subject.strip() or any(ord(char) < 0x20 for char in subject):
        raise MailboxWriterError("subject must be one nonempty line")
    problem = new_write_envelope_problem(kind, sender, recipient)
    if problem:
        raise MailboxWriterError(problem)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    relative = f"coordination/mailbox/sent/{stamp}-{sender}-to-{recipient}-{kind}.md"
    raw = _event_bytes(stamp, sender, recipient, subject, body)
    validate_event_candidate_bytes(root, raw, relative)
    destination = root / relative
    with writer_fence(root):
        if _git(root, "ls-files", "--stage", "--", relative):
            raise MailboxWriterError("artifact path already exists in the index")
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            descriptor = os.open(destination, flags, 0o600)
        except FileExistsError as exc:
            raise MailboxWriterError("timestamp collision; retry in one second") from exc
        try:
            view = memoryview(raw)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise MailboxWriterError("artifact write made no progress")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        try:
            blob = _git(root, "hash-object", "-w", "--stdin", input_bytes=raw).decode().strip()
            if re.fullmatch(r"[0-9a-f]{40,64}", blob) is None:
                raise MailboxWriterError("Git returned an invalid blob ID")
            _git(root, "update-index", "--add", "--cacheinfo", "100644", blob, relative)
        except MailboxWriterError:
            with contextlib.suppress(FileNotFoundError):
                destination.unlink()
            raise
    return relative


def send_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bin/pipeline mail send",
        description="Publish one exact-range review request or report; body on stdin.",
    )
    parser.add_argument("sender")
    parser.add_argument("recipient")
    parser.add_argument("kind", choices=sorted(FORMAL_REVIEW_KINDS))
    parser.add_argument("subject", nargs="+")
    arguments = parser.parse_args(argv)
    try:
        relative = publish(
            ROOT,
            sender=arguments.sender,
            recipient=arguments.recipient,
            kind=arguments.kind,
            subject=" ".join(arguments.subject),
            body=sys.stdin.read(),
        )
    except (MailboxWriterError, OSError, UnicodeError) as exc:
        print(f"mail send failed: {exc}", file=sys.stderr)
        return 4
    print(f"created {relative} (staged; commit with explicit pathspec)")
    return 0


if __name__ == "__main__":
    raise SystemExit(send_main())
