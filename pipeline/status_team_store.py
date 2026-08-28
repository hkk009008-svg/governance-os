"""Read-only observation of the desktop-team SQLite transport."""

from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
import stat
import tempfile
import urllib.parse
from pathlib import Path
from typing import Optional

import git_runner


TEAM_MEMBERS = ("codex", "claude", "agy")


def _store_path(repo_root: Path) -> Path:
    result = git_runner.run_git(
        repo_root,
        ["rev-parse", "--path-format=absolute", "--git-common-dir"],
        mode="dashboard",
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git rev-parse failed")
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = repo_root / common
    common = common.resolve()
    common_info = common.lstat()
    if common_info.st_uid != os.geteuid():
        raise RuntimeError("Git common directory is not owned by the current user")
    if stat.S_IMODE(common_info.st_mode) & 0o022:
        raise RuntimeError("Git common directory is group/world writable")
    return common / "pipeline-team" / "messages.sqlite3"


def _secure_existing_store(store: Path) -> Optional[str]:
    """Return an error for unsafe state, ``None`` for a safe existing store."""

    try:
        directory_info = store.parent.lstat()
    except FileNotFoundError:
        return "absent"
    if not stat.S_ISDIR(directory_info.st_mode) or stat.S_ISLNK(directory_info.st_mode):
        return "team store directory is not a real directory"
    if directory_info.st_uid != os.geteuid():
        return "team store directory is not owned by the current user"
    if stat.S_IMODE(directory_info.st_mode) & 0o077:
        return "team store directory is group/world accessible"
    try:
        store_info = store.lstat()
    except FileNotFoundError:
        return "absent"
    if not stat.S_ISREG(store_info.st_mode) or stat.S_ISLNK(store_info.st_mode):
        return "team store is not one regular file"
    if store_info.st_uid != os.geteuid():
        return "team store is not owned by the current user"
    if store_info.st_nlink != 1:
        return "team store does not have exactly one filesystem name"
    if stat.S_IMODE(store_info.st_mode) & 0o077:
        return "team store is group/world accessible"
    for suffix in ("-wal", "-shm"):
        sidecar = Path(f"{store}{suffix}")
        try:
            sidecar_info = sidecar.lstat()
        except FileNotFoundError:
            continue
        label = f"team store {suffix[1:]} sidecar"
        if not stat.S_ISREG(sidecar_info.st_mode) or stat.S_ISLNK(
            sidecar_info.st_mode
        ):
            return f"{label} is not one regular file"
        if sidecar_info.st_uid != os.geteuid():
            return f"{label} is not owned by the current user"
        if sidecar_info.st_nlink != 1:
            return f"{label} does not have exactly one filesystem name"
        if stat.S_IMODE(sidecar_info.st_mode) & 0o077:
            return f"{label} is group/world accessible"
    return None


def _query(store: Path, *, immutable: bool) -> dict:
    suffix = "mode=ro&immutable=1" if immutable else "mode=ro"
    uri = f"file:{urllib.parse.quote(str(store), safe='/')}?{suffix}"
    connection = sqlite3.connect(uri, uri=True, timeout=1)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("PRAGMA busy_timeout = 1000")
        identity = connection.execute(
            "SELECT value FROM metadata WHERE key='git_common_dir'"
        ).fetchone()
        members = {
            row["name"]: {
                "instance_id": row["instance_id"],
                "last_seen": row["last_seen"],
            }
            for row in connection.execute(
                "SELECT name,instance_id,last_seen FROM members ORDER BY name"
            )
        }
        pending = {
            member: connection.execute(
                "SELECT count(*) AS n FROM messages m WHERE m.sender!=? "
                "AND (m.recipient=? OR m.recipient='all') AND NOT EXISTS "
                "(SELECT 1 FROM deliveries d "
                "WHERE d.message_id=m.id AND d.member=?)",
                (member, member, member),
            ).fetchone()["n"]
            for member in TEAM_MEMBERS
        }
        queued = connection.execute("SELECT count(*) AS n FROM messages").fetchone()["n"]
        acknowledgements = connection.execute(
            "SELECT count(*) AS n FROM deliveries"
        ).fetchone()["n"]
        replies = connection.execute(
            "SELECT count(*) AS n FROM messages WHERE reply_to IS NOT NULL"
        ).fetchone()["n"]
    finally:
        connection.close()
    return {
        "identity": identity["value"] if identity is not None else None,
        "members": members,
        "pending": pending,
        "queued_messages": queued,
        "acknowledgement_receipts": acknowledgements,
        "reply_messages": replies,
    }


def _fingerprint(path: Path):
    """Return stable file identity plus content digest, or ``None`` if absent."""

    try:
        with path.open("rb", buffering=0) as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ValueError(f"snapshot source is not a regular file: {path}")
            digest = hashlib.file_digest(handle, "sha256").digest()
            after = os.fstat(handle.fileno())
    except FileNotFoundError:
        return None
    stable = lambda item: (
        item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns
    )
    if stable(before) != stable(after):
        raise RuntimeError("team store changed while being fingerprinted")
    return (*stable(after), digest)


def _content(fingerprint):
    return None if fingerprint is None else (fingerprint[2], fingerprint[4])


def _copy_consistent_store(store: Path, snapshot: Path) -> bool:
    """Copy one stable main/WAL pair without touching the shared database."""

    wal, snapshot_wal = Path(f"{store}-wal"), Path(f"{snapshot}-wal")
    for _attempt in range(8):
        try:
            before = (_fingerprint(store), _fingerprint(wal))
            if before[0] is None:
                raise ValueError("team store disappeared during snapshot")
            shutil.copyfile(store, snapshot)
            if before[1] is None:
                snapshot_wal.unlink(missing_ok=True)
            else:
                shutil.copyfile(wal, snapshot_wal)
            copied = (_fingerprint(snapshot), _fingerprint(snapshot_wal))
            after = (_fingerprint(store), _fingerprint(wal))
        except (FileNotFoundError, RuntimeError):
            continue
        if before == after and tuple(map(_content, before)) == tuple(
            map(_content, copied)
        ):
            return before[1] is not None
    raise sqlite3.OperationalError(
        "team store stayed busy during a consistent read-only snapshot"
    )


def _query_live_snapshot(store: Path) -> dict:
    # A read-only SQLite connection can still create or change WAL sidecars.
    # Stabilize and copy the main/WAL byte pair, then query only that disposable
    # snapshot. A checkpoint or writer between copies forces a bounded retry.
    with tempfile.TemporaryDirectory(prefix="pipeline-status-") as scratch:
        snapshot = Path(scratch) / store.name
        has_wal = _copy_consistent_store(store, snapshot)
        return _query(snapshot, immutable=not has_wal)


def collect_team_transport(repo_root: Path) -> dict:
    """Inspect existing transport state without creating or touching it."""

    try:
        store = _store_path(repo_root)
    except Exception as exc:
        return {"state": "unavailable", "detail": str(exc)}
    problem = _secure_existing_store(store)
    if problem == "absent":
        return {
            "state": "absent",
            "store": str(store),
            "detail": "not initialized; status did not create it",
            "members": {},
            "pending": {member: 0 for member in TEAM_MEMBERS},
            "queued_messages": 0,
            "acknowledgement_receipts": 0,
            "reply_messages": 0,
        }
    if problem is not None:
        return {"state": "unavailable", "store": str(store), "detail": problem}
    try:
        result = _query_live_snapshot(store)
        identity = result.pop("identity")
        if identity is None or Path(identity).resolve() != store.parent.parent:
            raise ValueError("team store repository identity is missing or mismatched")
    except (OSError, sqlite3.Error, TypeError, ValueError) as exc:
        return {
            "state": "unavailable",
            "store": str(store),
            "detail": f"existing team store is unreadable: {exc}",
        }
    return {
        "state": "ready",
        "store": str(store),
        "detail": "activity is observational, not liveness or authority",
        **result,
    }
