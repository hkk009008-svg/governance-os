#!/usr/bin/env python3
"""Fail-closed compact-kernel selector and shared v1 writer fence."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import stat
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal

_REF = "refs/protocol/kernel-activation"
_SCHEMA = "protocol-kernel-selection/v1"
_LOCK_NAME = "protocol-kernel-writer.lock"
_EVENT_RE = re.compile(
    r"^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>director2?|operator2?|coordinator2?)-to-"
    r"(?P<recipient>director2?|operator2?|coordinator2?|all)-"
    r"(?P<kind>[a-z0-9-]+)\.md$"
)
_COLON_ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_DASH_ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z")
_ROLES = {
    "director", "director2", "operator", "operator2", "coordinator", "coordinator2",
}
_GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "LANG": "C",
    "LC_ALL": "C",
    "HOME": "/var/empty",
    "XDG_CONFIG_HOME": "/var/empty",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
}


class KernelSelectionError(RuntimeError):
    """The selector, its mirror, or the repository boundary is invalid."""


@dataclass(frozen=True)
class KernelSelection:
    epoch: int
    writer: Literal["v1", "compact"]
    selector_oid: str | None


def _git_result(root: Path, *arguments: str, input_bytes: bytes | None = None):
    return subprocess.run(
        [
            "/usr/bin/git", "--no-replace-objects", "--literal-pathspecs",
            "-C", str(root), *arguments,
        ],
        input=input_bytes,
        capture_output=True,
        check=False,
        env=_GIT_ENV,
    )


def _git(root: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    completed = _git_result(root, *arguments, input_bytes=input_bytes)
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise KernelSelectionError(f"sanitized Git failed: {detail or arguments[0]}")
    return completed.stdout


def _mirror(root: Path) -> tuple[int, Literal["v1", "compact"]]:
    try:
        parsed = tomllib.loads((root / "governance.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise KernelSelectionError(f"kernel mirror is unavailable: {exc}") from exc
    protocol = parsed.get("protocol")
    table = protocol.get("kernel") if isinstance(protocol, dict) else None
    if not isinstance(table, dict) or set(table) != {"epoch", "writer"}:
        raise KernelSelectionError("kernel mirror must contain only epoch and writer")
    epoch, writer = table["epoch"], table["writer"]
    if type(epoch) is not int or epoch < 0:
        raise KernelSelectionError("kernel mirror epoch must be a non-negative integer")
    if writer not in {"v1", "compact"}:
        raise KernelSelectionError("kernel mirror writer must be v1 or compact")
    return epoch, writer


def _selector_oid(root: Path) -> str | None:
    completed = _git_result(root, "rev-parse", "--verify", "--quiet", _REF)
    if completed.returncode == 1 and not completed.stdout:
        return None
    if completed.returncode != 0:
        raise KernelSelectionError("cannot resolve kernel activation ref")
    oid = completed.stdout.decode("ascii", "strict").strip()
    if not oid or any(character not in "0123456789abcdef" for character in oid):
        raise KernelSelectionError("kernel activation ref did not resolve to one object")
    return oid


def read_selection(repo_root: Path | str) -> KernelSelection:
    """Read and strictly cross-check the authoritative selector and TOML mirror."""
    root = Path(repo_root).resolve(strict=True)
    mirror_epoch, mirror_writer = _mirror(root)
    oid = _selector_oid(root)
    if oid is None:
        if (mirror_epoch, mirror_writer) != (0, "v1"):
            raise KernelSelectionError("missing selector requires mirror epoch 0 writer v1")
        return KernelSelection(0, "v1", None)
    object_type = _git(root, "cat-file", "-t", oid).decode("ascii", "strict").strip()
    if object_type != "blob":
        raise KernelSelectionError("kernel activation ref must name one Git blob")
    raw = _git(root, "cat-file", "blob", oid)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise KernelSelectionError("kernel activation blob is not canonical JSON") from exc
    if not isinstance(value, dict) or set(value) != {"schema", "epoch", "writer"}:
        raise KernelSelectionError("kernel activation blob has an invalid schema shape")
    epoch, writer = value["epoch"], value["writer"]
    if value["schema"] != _SCHEMA:
        raise KernelSelectionError("kernel activation schema is unsupported")
    if type(epoch) is not int or epoch <= 0:
        raise KernelSelectionError("present selector epoch must be a positive integer")
    if writer not in {"v1", "compact"}:
        raise KernelSelectionError("kernel activation writer must be v1 or compact")
    canonical = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if raw != canonical:
        raise KernelSelectionError("kernel activation blob is not canonical JSON")
    if (epoch, writer) != (mirror_epoch, mirror_writer):
        raise KernelSelectionError("kernel activation selector and mirror disagree")
    return KernelSelection(epoch, writer, oid)


def _require_v1_reader(repo_root: Path | str) -> KernelSelection:
    selection = read_selection(repo_root)
    if (selection.epoch, selection.writer) != (0, "v1"):
        raise KernelSelectionError(
            f"reader requires selector 0/v1, observed {selection.epoch}/{selection.writer}"
        )
    return selection


def _reader_guard(repo_root: Path | str, label: str) -> bool:
    try:
        _require_v1_reader(repo_root)
        return True
    except KernelSelectionError as exc:
        print(f"{label}: kernel selector: {exc}", file=sys.stderr)
        return False


@contextlib.contextmanager
def writer_fence(
    repo_root: Path | str,
    expected_epoch: int,
    expected_writer: Literal["v1", "compact"],
) -> Iterator[KernelSelection]:
    """Hold the Git-common-dir writer lock and then reread the exact selector."""
    if type(expected_epoch) is not int or expected_epoch < 0:
        raise KernelSelectionError("expected epoch must be a non-negative integer")
    if expected_writer not in {"v1", "compact"}:
        raise KernelSelectionError("expected writer must be v1 or compact")
    root = Path(repo_root).resolve(strict=True)
    common_raw = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common = Path(common_raw.decode("utf-8", "strict").strip()).resolve(strict=True)
    flags = (
        os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    fd = os.open(common / _LOCK_NAME, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise KernelSelectionError("writer lock is not a regular file")
        fcntl.flock(fd, fcntl.LOCK_EX)
        selection = read_selection(root)
        if (selection.epoch, selection.writer) != (expected_epoch, expected_writer):
            raise KernelSelectionError(
                "writer fence expected "
                f"{expected_epoch}/{expected_writer}, observed "
                f"{selection.epoch}/{selection.writer}"
            )
        yield selection
    finally:
        os.close(fd)


def _stage(root: Path, relative: str, *, force: bool = False) -> None:
    arguments = ["add"]
    if force:
        arguments.append("-f")
    _git(root, *arguments, "--", relative)


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
        raise KernelSelectionError("send-event finalizer received a noncanonical path")
    observed = candidate.lstat()
    if not stat.S_ISREG(observed.st_mode) or stat.S_IMODE(observed.st_mode) != 0o600:
        raise KernelSelectionError("send-event candidate must be one mode-0600 regular file")
    lines = candidate.read_text(encoding="utf-8").splitlines()
    sender, recipient = match.group("sender"), match.group("recipient")
    stamp = _colon(match.group("stamp"))
    kinds = (root / "coordination/mailbox/kinds.txt").read_text(
        encoding="utf-8"
    ).splitlines()
    if (
        match.group("kind") not in kinds
        or len(lines) < 5
        or lines[1]
        or lines[3]
        or not lines[0].startswith(
            f"# {sender.capitalize()} → {recipient.capitalize()}: "
        )
        or lines[2] != f"**When:** {stamp} · **From:** {sender} (online)"
        or not lines[-1].startswith("Cursor at send: ")
    ):
        raise KernelSelectionError("send-event candidate envelope does not match filename")
    final = root / relative
    with writer_fence(root, 0, "v1"):
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
            except KernelSelectionError:
                return False
        finally:
            os.close(directory_fd)
    return True


def _dash(value: str) -> str:
    return value[:11] + value[11:19].replace(":", "-") + "Z"


def _colon(value: str) -> str:
    return value[:11] + value[11:19].replace("-", ":") + "Z"


def _consume_events_finalize(root: Path, role: str, target: str | None) -> str:
    if role not in _ROLES:
        raise KernelSelectionError("consume-events role is invalid")
    sent = root / "coordination" / "mailbox" / "sent"
    seen = root / "coordination" / "mailbox" / "seen"
    cursor = seen / f"{role}.txt"
    with writer_fence(root, 0, "v1"):
        current_raw = cursor.read_bytes()
        if current_raw.count(b"\n") != 1 or not current_raw.endswith(b"\n"):
            raise KernelSelectionError("consume-events cursor is not one canonical line")
        current = current_raw[:-1].decode("ascii", "strict")
        if current.isdigit():
            raise KernelSelectionError(f"{role} is migrated to the signed ref-bus")
        if _COLON_ISO_RE.fullmatch(current) is None:
            raise KernelSelectionError("consume-events current cursor is not colon ISO")
        current_dash = _dash(current)
        addressed = sorted(
            path.name
            for path in sent.iterdir()
            if path.is_file()
            and (match := _EVENT_RE.fullmatch(path.name)) is not None
            and match.group("recipient") in {role, "all"}
        )
        if target is None:
            if not addressed:
                return f"cursor {role}: no addressed events (no-op)"
            target_dash = addressed[-1][:20]
        else:
            if not (
                _COLON_ISO_RE.fullmatch(target) or _DASH_ISO_RE.fullmatch(target)
            ):
                raise KernelSelectionError("consume-events target is not an ISO timestamp")
            target_dash = _dash(target)
            if not any(name.startswith(target_dash + "-") for name in addressed):
                raise KernelSelectionError("consume-events target names no addressed event")
        if target_dash == current_dash:
            return f"cursor {role}: already at {_colon(target_dash)} (no-op)"
        if target_dash < current_dash:
            raise KernelSelectionError("consume-events refuses cursor regression")
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
        return f"cursor {role}: {current} -> {_colon(target_dash)}; unread now: {unread} (staged)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kernel_activation.py")
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
    except (KernelSelectionError, OSError, UnicodeError) as exc:
        print(f"kernel-activation: {exc}", file=sys.stderr)
        return 4
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
