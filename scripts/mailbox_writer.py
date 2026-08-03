#!/usr/bin/env python3
"""Fixed, fail-closed mailbox event and cursor writer."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import os
import re
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterator

import hashlib

import bus_unread
import compact_pair_loop
import protocol_mailbox

_LOCK_NAME = "protocol-kernel-writer.lock"
_EVENT_RE = re.compile(
    r"^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>director2?|operator2?|coordinator2?)-to-"
    r"(?P<recipient>director2?|operator2?|coordinator2?|all)-"
    r"(?P<kind>[a-z0-9-]+)\.md$"
)
_COLON_ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_DASH_ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z")
_ROLES = {"director", "director2", "operator", "operator2"}
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
    """The fixed mailbox writer or repository boundary is invalid."""


def _git(root: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    completed = subprocess.run(
        [
            "/usr/bin/git", "--no-replace-objects", "--literal-pathspecs",
            "-C", str(root), *arguments,
        ],
        input=input_bytes,
        capture_output=True,
        check=False,
        env=_GIT_ENV,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise MailboxWriterError(f"sanitized Git failed: {detail or arguments[0]}")
    return completed.stdout


@contextlib.contextmanager
def writer_fence(repo_root: Path | str) -> Iterator[None]:
    """Serialize mailbox writers through the repository's Git-common-dir lock."""
    root = Path(repo_root).resolve(strict=True)
    common_raw = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common = Path(common_raw.decode("utf-8", "strict").strip()).resolve(strict=True)
    flags = (
        os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    # Keep the established lock filename so old and new worktree shims cannot
    # split the writer lock during the local cutover.
    fd = os.open(common / _LOCK_NAME, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise MailboxWriterError("writer lock is not a regular file")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _stage(root: Path, relative: str, *, force: bool = False) -> None:
    arguments = ["add"]
    if force:
        arguments.append("-f")
    _git(root, *arguments, "--", relative)


def validate_event_envelope(
    root: Path,
    candidate: Path,
    relative: str,
) -> re.Match[str]:
    """Validate one event's canonical carrier envelope.

    This intentionally does not validate the kind-specific payload.  Committed
    historical events use the canonical committed-artifact parser for that
    step, while new candidates use :func:`validate_event_candidate`.
    """

    return validate_event_envelope_bytes(root, candidate.read_bytes(), relative)


def validate_event_envelope_bytes(
    root: Path,
    raw: bytes,
    relative: str,
) -> re.Match[str]:
    """Validate canonical event bytes without materializing a scratch file."""

    match = _EVENT_RE.fullmatch(Path(relative).name)
    if (
        match is None
        or Path(relative).parent.as_posix() != "coordination/mailbox/sent"
    ):
        raise MailboxWriterError("send-event candidate path is not canonical")
    if len(raw) > compact_pair_loop.MAX_EVENT_BYTES or b"\x00" in raw:
        raise MailboxWriterError("send-event candidate is not one bounded text event")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise MailboxWriterError("send-event candidate is not UTF-8") from exc
    sender, recipient = match.group("sender"), match.group("recipient")
    stamp = _colon(match.group("stamp"))
    kinds = (root / "coordination/mailbox/kinds.txt").read_text(
        encoding="utf-8"
    ).splitlines()
    h1_lines = [line for line in lines if line.startswith("# ")]
    envelope_lines = [
        line
        for line in lines
        if line.startswith("**When:** ") or line.startswith("**From:** ")
    ]
    cursor_lines = [line for line in lines if line.startswith("Cursor at send: ")]
    if len(h1_lines) != 1:
        raise MailboxWriterError("send-event candidate has missing or duplicate H1 envelope")
    if len(envelope_lines) != 1:
        raise MailboxWriterError(
            "send-event candidate has missing or duplicate When/From envelope"
        )
    if len(cursor_lines) != 1:
        raise MailboxWriterError("send-event candidate has missing or duplicate cursor footer")
    cursor_value = cursor_lines[0].removeprefix("Cursor at send: ")
    if sender in {"coordinator", "coordinator2"}:
        if cursor_value != "cursorless":
            raise MailboxWriterError(
                "coordinator send-event candidate must use the cursorless marker"
            )
    elif cursor_value == "cursorless":
        raise MailboxWriterError(
            "pair-seat send-event candidate cannot use the cursorless marker"
        )
    if (
        match.group("kind") not in kinds
        or len(lines) < 5
        or lines[1]
        or lines[3]
        or h1_lines[0] != lines[0]
        or not lines[0].startswith(
            f"# {sender.capitalize()} → {recipient.capitalize()}: "
        )
        or envelope_lines[0] != lines[2]
        or lines[2] != f"**When:** {stamp} · **From:** {sender} (online)"
        or cursor_lines[0] != lines[-1]
    ):
        raise MailboxWriterError("send-event candidate envelope does not match filename")
    return match


_PSEUDO_COMMIT = "0" * 40


def _typed_candidate_event(
    candidate: Path, relative: str
) -> protocol_mailbox.CommittedEventRef:
    """Type an uncommitted candidate's exact bytes with the committed parser.

    The pseudo commit marks "not committed yet"; every check that needs repo
    state resolves against HEAD explicitly, never through this placeholder.
    """

    return protocol_mailbox.parse_committed_event_text(
        f"{relative}@{_PSEUDO_COMMIT}",
        candidate.read_text(encoding="utf-8"),
    )


def _validate_learning_candidate_payload(
    root: Path, candidate: Path, relative: str
) -> None:
    """Stage 2b: the learning-candidate refusals bind at publication.

    Refuses malformed payloads, unresolvable path@sha source refs and
    Supersedes, and duplicate Candidate IDs against the committed scan at
    HEAD. ``sha256:`` digest refs are shape-only by construction — they name
    content, not a committed object, so resolution cannot be demanded.
    """

    try:
        statement = protocol_mailbox.parse_learning_candidate_statement(
            _typed_candidate_event(candidate, relative)
        )
    except ValueError as exc:
        raise MailboxWriterError(
            f"learning-candidate candidate is invalid: {exc}"
        ) from exc
    for reference in statement.source_refs:
        if "@" not in reference:
            continue
        try:
            protocol_mailbox.load_committed_event_ref(root, reference)
        except ValueError as exc:
            raise MailboxWriterError(
                f"learning-candidate source ref does not resolve: {reference}"
            ) from exc
    if statement.supersedes is not None:
        try:
            protocol_mailbox.load_learning_candidate_statement(
                root, statement.supersedes
            )
        except ValueError as exc:
            raise MailboxWriterError(
                f"learning-candidate Supersedes does not resolve: "
                f"{statement.supersedes}"
            ) from exc
    try:
        committed = protocol_mailbox.committed_learning_candidate_ids(root, "HEAD")
    except ValueError as exc:
        raise MailboxWriterError(
            f"learning-candidate dedup scan failed: {exc}"
        ) from exc
    existing = committed.get(statement.candidate_id)
    if existing is not None:
        raise MailboxWriterError(
            "learning-candidate duplicates committed candidate "
            f"{existing} (byte-idempotent; use Supersedes to replace)"
        )


def _validate_learning_disposition_payload(
    root: Path, candidate: Path, relative: str
) -> None:
    """Stage 2b: disposition refusals bind at publication.

    A ``decision`` event is a learning disposition exactly when it names a
    canonical learning-candidate ref on a ``Candidate:`` line AND carries a
    ``Disposition:`` line — the same fields the read-side parser grants
    meaning to. Every other decision publishes exactly as before: free prose
    that merely contains ``Candidate:`` (a hiring note, a list item) never
    enters disposition parsing (round-one FAIL: the earlier any-line sniff
    refused such events — an availability regression on a historical kind).
    An event that quotes a real ref without a Disposition line is prose to
    readers too, so it publishes; one that quotes both is exactly what a
    reader would parse as a disposition, so validating it is correct.
    Self-approval (disposer == producer) is refused for every disposition,
    strictest reading of the contract — a producer replaces its own candidate
    via Supersedes, it does not dispose it. The acceptance-only refusals
    (ASSUMED provenance, governance-rule below the high-risk-control floor,
    stale target base hash) evaluate against HEAD at publication — the parent
    of the disposition's own commit; a reader re-verifying later evaluates at
    the disposition commit itself and must agree unless the same commit
    changed the target, which the fixed writer never does.
    """

    lines = candidate.read_text(encoding="utf-8").splitlines()
    named_refs = [
        line[len("Candidate:") :].strip()
        for line in lines
        if line.startswith("Candidate:")
    ]
    names_learning_candidate = any(
        protocol_mailbox.immutable_reference_is_canonical(value)
        and value.rsplit("@", 1)[0].endswith("-learning-candidate.md")
        for value in named_refs
    )
    if not names_learning_candidate or not any(
        line.startswith("Disposition:") for line in lines
    ):
        return
    try:
        disposition = protocol_mailbox.parse_learning_disposition_statement(
            _typed_candidate_event(candidate, relative)
        )
    except ValueError as exc:
        raise MailboxWriterError(
            f"decision disposition is invalid: {exc}"
        ) from exc
    try:
        statement = protocol_mailbox.load_learning_candidate_statement(
            root, disposition.candidate_ref
        )
    except ValueError as exc:
        raise MailboxWriterError(
            "decision Candidate does not resolve to a committed "
            f"learning-candidate: {exc}"
        ) from exc
    if disposition.disposer_seat == statement.producer_seat:
        raise MailboxWriterError(
            "decision disposer equals candidate producer (self-approval)"
        )
    if disposition.disposition == "accepted":
        if statement.evidence_provenance == "ASSUMED":
            raise MailboxWriterError(
                "ASSUMED-provenance candidate may not be accepted"
            )
        if (
            statement.category == "governance-rule"
            and statement.risk_class != "high-risk-control"
        ):
            raise MailboxWriterError(
                "governance-rule candidate below the high-risk-control "
                "floor may not be accepted"
            )
        if statement.target is not None:
            try:
                data = _git(root, "cat-file", "blob", f"HEAD:{statement.target}")
            except MailboxWriterError as exc:
                raise MailboxWriterError(
                    "decision target is absent at the publication commit: "
                    f"{statement.target}"
                ) from exc
            digest = "sha256:" + hashlib.sha256(data).hexdigest()
            if digest != statement.target_base_hash:
                raise MailboxWriterError(
                    "decision target base hash is stale at the publication "
                    "commit (CAS)"
                )


def validate_event_candidate(
    root: Path,
    candidate: Path,
    relative: str,
    *,
    validate_range: bool = True,
) -> None:
    """Validate one new event's canonical envelope and kind-specific structure."""

    match = validate_event_envelope(root, candidate, relative)
    if match.group("kind") == "verify-request":
        try:
            request = compact_pair_loop.parse_verify_request_candidate(
                root, candidate, relative
            )
            violations = (
                compact_pair_loop.validate_request_candidate(root, request)
                if validate_range
                else []
            )
        except compact_pair_loop.CompactPairError as exc:
            raise MailboxWriterError(f"verify-request candidate is invalid: {exc}") from exc
        if violations:
            raise MailboxWriterError(
                "verify-request candidate is invalid: " + "; ".join(violations)
            )
    elif match.group("kind") == "verification-report":
        try:
            report = compact_pair_loop.parse_verification_report_candidate(
                root, candidate, relative
            )
            violations = (
                compact_pair_loop.validate_report(root, report)
                if validate_range
                else compact_pair_loop.validate_report_structure(root, report)
            )
        except compact_pair_loop.CompactPairError as exc:
            raise MailboxWriterError(
                f"verification-report candidate is invalid: {exc}"
            ) from exc
        if violations:
            raise MailboxWriterError(
                "verification-report candidate is invalid: "
                + "; ".join(violations)
            )
    elif match.group("kind") == "learning-candidate":
        _validate_learning_candidate_payload(root, candidate, relative)
    elif match.group("kind") == "decision":
        _validate_learning_disposition_payload(root, candidate, relative)


def _send_event_finalize(root: Path, candidate: Path, relative: str) -> bool:
    match = _EVENT_RE.fullmatch(Path(relative).name)
    sent = root / "coordination" / "mailbox" / "sent"
    if (
        match is None
        or Path(relative).parent.as_posix() != "coordination/mailbox/sent"
        or candidate.parent.resolve(strict=True) != sent.resolve(strict=True)
        or not candidate.name.startswith(f".{Path(relative).stem}.")
        or not candidate.name.endswith(".tmp")
    ):
        raise MailboxWriterError("send-event finalizer received a noncanonical path")
    observed = candidate.lstat()
    if not stat.S_ISREG(observed.st_mode) or stat.S_IMODE(observed.st_mode) != 0o600:
        raise MailboxWriterError("send-event candidate must be one mode-0600 regular file")
    validate_event_candidate(root, candidate, relative)
    final = root / relative
    with writer_fence(root):
        directory_fd = os.open(sent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.link(
                candidate.name,
                final.name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
            final_fd = os.open(
                final.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory_fd,
            )
            try:
                os.fsync(final_fd)
            finally:
                os.close(final_fd)
            os.fsync(directory_fd)
            os.unlink(candidate.name, dir_fd=directory_fd)
            os.fsync(directory_fd)
            try:
                _stage(root, relative, force=True)
            except MailboxWriterError:
                return False
        finally:
            os.close(directory_fd)
    return True


def _dash(value: str) -> str:
    return value[:11] + value[11:19].replace(":", "-") + "Z"


def _colon(value: str) -> str:
    return value[:11] + value[11:19].replace("-", ":") + "Z"


def _valid_colon_iso(value: str) -> bool:
    if _COLON_ISO_RE.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def _valid_dash_iso(value: str) -> bool:
    if _DASH_ISO_RE.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H-%M-%SZ")
    except ValueError:
        return False
    return True


def _consume_events_finalize(root: Path, role: str, target: str | None) -> str:
    if role not in _ROLES:
        raise MailboxWriterError("consume-events role is invalid")
    sent = root / "coordination" / "mailbox" / "sent"
    seen = root / "coordination" / "mailbox" / "seen"
    cursor = seen / f"{role}.txt"
    with writer_fence(root):
        current_raw = cursor.read_bytes()
        if current_raw.count(b"\n") != 1 or not current_raw.endswith(b"\n"):
            raise MailboxWriterError("consume-events cursor is not one canonical line")
        current = current_raw[:-1].decode("ascii", "strict")
        scalar_fallback = False
        if current.isdigit():
            authority = bus_unread.bus_authority_state(root, role)
            if authority.state == "live":
                raise MailboxWriterError(
                    f"{role} has a live signed ref-bus; use its cursor consumer"
                )
            if authority.state == "incoherent":
                raise MailboxWriterError(
                    f"{role} transport is incoherent: {authority.detail}"
                )
            scalar_fallback = True
        elif not _valid_colon_iso(current):
            raise MailboxWriterError("consume-events current cursor is not colon ISO")
        event_names = [
            path.name
            for path in sent.iterdir()
            if path.is_file() and path.name.endswith(".md")
        ]
        try:
            canonical = bus_unread.ordered_mailbox_events(event_names)
        except ValueError as exc:
            raise MailboxWriterError(f"mailbox event order is invalid: {exc}") from exc
        if scalar_fallback:
            try:
                remaining = bus_unread.mailbox_events_after_scalar(
                    current, canonical
                )
            except ValueError as exc:
                raise MailboxWriterError(str(exc)) from exc
            addressed = [
                name
                for name in remaining
                if (
                    (match := _EVENT_RE.fullmatch(name)) is not None
                    and match.group("recipient") in {role, "all"}
                )
            ]
            current_dash = None
        else:
            current_dash = _dash(current)
            addressed = [
                name
                for name in canonical
                if (
                    (match := _EVENT_RE.fullmatch(name)) is not None
                    and match.group("recipient") in {role, "all"}
                )
            ]
        if target is None:
            if not addressed:
                suffix = " via mailbox fallback" if scalar_fallback else ""
                return f"cursor {role}: no addressed events{suffix} (no-op)"
            target_dash = addressed[-1][:20]
        else:
            if not (
                _valid_colon_iso(target) or _valid_dash_iso(target)
            ):
                raise MailboxWriterError("consume-events target is not an ISO timestamp")
            target_dash = _dash(target)
            if not any(name.startswith(target_dash + "-") for name in addressed):
                raise MailboxWriterError("consume-events target names no addressed event")
        if current_dash is not None and target_dash == current_dash:
            return f"cursor {role}: already at {_colon(target_dash)} (no-op)"
        if current_dash is not None and target_dash < current_dash:
            raise MailboxWriterError("consume-events refuses cursor regression")
        updated = (_colon(target_dash) + "\n").encode("ascii")
        temporary = seen / f".{role}.{os.getpid()}.tmp"
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(temporary, flags, 0o600)
        try:
            os.write(fd, updated)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(temporary, cursor)
        directory_fd = os.open(seen, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
            _stage(root, f"coordination/mailbox/seen/{role}.txt")
        except Exception:
            rollback = seen / f".{role}.{os.getpid()}.rollback"
            rollback.write_bytes(current_raw)
            rollback.chmod(0o600)
            os.replace(rollback, cursor)
            os.fsync(directory_fd)
            raise
        finally:
            os.close(directory_fd)
        unread = sum(name[:20] > target_dash for name in addressed)
        mode = "mailbox fallback; " if scalar_fallback else ""
        return (
            f"cursor {role}: {current} -> {_colon(target_dash)}; unread now: "
            f"{unread} ({mode}staged)"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mailbox_writer.py")
    commands = parser.add_subparsers(dest="command", required=True)
    send = commands.add_parser("send-event-finalize")
    send.add_argument("--repo-root", required=True)
    send.add_argument("--candidate", required=True)
    send.add_argument("--final-relative", required=True)
    consume = commands.add_parser("consume-events", prog="consume-events")
    consume.add_argument("--repo-root", required=True)
    consume.add_argument("role", choices=sorted(_ROLES))
    consume.add_argument("--to")
    arguments = parser.parse_args(argv)
    try:
        root = Path(arguments.repo_root).resolve(strict=True)
        if arguments.command == "send-event-finalize":
            staged = _send_event_finalize(
                root, Path(arguments.candidate), arguments.final_relative
            )
            output = ("staged:" if staged else "unstaged:") + arguments.final_relative
        else:
            output = _consume_events_finalize(root, arguments.role, arguments.to)
    except (MailboxWriterError, OSError, UnicodeError) as exc:
        print(f"mailbox-writer: {exc}", file=sys.stderr)
        return 4
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
