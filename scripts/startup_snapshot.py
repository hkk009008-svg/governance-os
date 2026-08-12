#!/usr/bin/env python3
"""Typed, read-only Git and mailbox state used during seat startup."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import bus_unread
import git_runner


@dataclass(frozen=True)
class GitPathState:
    status: str
    path: str
    original_path: str | None = None


@dataclass(frozen=True)
class GitSnapshot:
    root: Path
    head: str | None
    branch: str | None
    recent_commits: tuple[str, ...]
    dirty_paths: tuple[GitPathState, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class MailboxSnapshot:
    seat: str
    cursor: str | None
    unread_refs: tuple[str, ...]
    unavailable_reason: str | None


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="surrogateescape")


def _run_git(root: Path, args: list[str], label: str) -> tuple[bytes | None, str | None]:
    try:
        # dashboard_env pins discovery to ``root``: a non-repository root
        # answers "unavailable" instead of reporting an enclosing checkout.
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            env=git_runner.dashboard_env(root),
            capture_output=True,
            timeout=120,
            check=False,
        )
    except Exception as exc:
        return None, f"{label} unavailable: {exc}"
    if completed.returncode != 0:
        detail = _decode(completed.stderr or completed.stdout).strip()
        suffix = f": {detail}" if detail else ""
        return (
            None,
            f"{label} unavailable: git exited {completed.returncode}{suffix}",
        )
    return completed.stdout, None


def _parse_porcelain(raw: bytes) -> tuple[tuple[GitPathState, ...], str | None]:
    records = raw.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    states: list[GitPathState] = []
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 3 or record[2:3] != b" ":
            return tuple(states), "dirty paths parse error: malformed porcelain record"
        status = _decode(record[:2])
        path = _decode(record[3:])
        original_path = None
        if "R" in status or "C" in status:
            index += 1
            if index >= len(records):
                return tuple(states), "dirty paths parse error: rename source missing"
            original_path = _decode(records[index])
        states.append(GitPathState(status, path, original_path))
        index += 1
    return tuple(states), None


def collect_git_snapshot(root: Path, *, commits: int = 5) -> GitSnapshot:
    """Describe local Git state without refreshing the index or changing refs.

    ``root`` must itself be the repository (toplevel or linked worktree).
    A root that is not a repository reports every fact as unavailable; the
    snapshot never substitutes an enclosing repository discovered above it.
    """
    root = Path(root).resolve()
    errors: list[str] = []

    head_raw, error = _run_git(root, ["rev-parse", "--verify", "HEAD"], "HEAD")
    if error:
        errors.append(error)
    head = _decode(head_raw).strip() if head_raw is not None else None

    branch_raw, error = _run_git(
        root,
        ["rev-parse", "--abbrev-ref", "HEAD"],
        "branch",
    )
    if error:
        errors.append(error)
    branch = _decode(branch_raw).strip() if branch_raw is not None else None
    if branch == "HEAD":
        branch = None

    log_raw, error = _run_git(
        root,
        ["log", "--oneline", "-n", str(max(0, commits))],
        "recent commits",
    )
    if error:
        errors.append(error)
    recent_commits = (
        tuple(_decode(log_raw).splitlines()) if log_raw is not None else ()
    )

    status_raw, error = _run_git(
        root,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        "dirty paths",
    )
    if error:
        errors.append(error)
        dirty_paths: tuple[GitPathState, ...] = ()
    else:
        dirty_paths, parse_error = _parse_porcelain(status_raw or b"")
        if parse_error:
            errors.append(parse_error)

    return GitSnapshot(
        root=root,
        head=head,
        branch=branch,
        recent_commits=recent_commits,
        dirty_paths=dirty_paths,
        errors=tuple(errors),
    )


def _parse_cursor(cursor: str) -> datetime | None:
    try:
        return datetime.strptime(cursor, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def _filename_time(name: str) -> datetime | None:
    timestamp = name[:20]
    if len(timestamp) != 20 or timestamp[10] != "T" or timestamp[19] != "Z":
        return None
    return _parse_cursor(f"{timestamp[:13]}:{timestamp[14:16]}:{timestamp[17:]}")


def collect_mailbox_snapshot(root: Path, seat: str) -> MailboxSnapshot:
    """Describe unread mailbox references without advancing either cursor path."""
    root = Path(root).resolve()
    cursor_path = root / "coordination" / "mailbox" / "seen" / f"{seat}.txt"
    try:
        lines = cursor_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return MailboxSnapshot(seat, None, (), "cursor")
    cursor = lines[0].strip() if lines else ""
    if not cursor:
        return MailboxSnapshot(seat, cursor, (), "cursor")

    if bus_unread.is_migrated_cursor(cursor):
        try:
            events = bus_unread.bus_unread_events(root, seat)
        except Exception:
            return MailboxSnapshot(seat, cursor, (), "ref-bus")
        if events is None:
            return MailboxSnapshot(seat, cursor, (), "ref-bus")
        try:
            unread_refs = tuple(bus_unread.format_unread(event) for event in events)
        except Exception:
            return MailboxSnapshot(seat, cursor, (), "ref-bus formatting")
        return MailboxSnapshot(seat, cursor, unread_refs, None)

    cursor_time = _parse_cursor(cursor)
    if cursor_time is None:
        return MailboxSnapshot(seat, cursor, (), "cursor format")
    sent = root / "coordination" / "mailbox" / "sent"
    try:
        addressed = sorted(
            path.name
            for path in sent.iterdir()
            if path.is_file()
            and path.name.endswith(".md")
            and (f"-to-{seat}-" in path.name or "-to-all-" in path.name)
        )
    except Exception:
        return MailboxSnapshot(seat, cursor, (), "legacy mailbox")

    unread_refs = tuple(
        name
        for name in addressed
        if (event_time := _filename_time(name)) is not None
        and event_time > cursor_time
    )
    return MailboxSnapshot(seat, cursor, unread_refs, None)
