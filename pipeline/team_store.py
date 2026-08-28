"""Repository-scoped SQLite primitives for the desktop team transport."""
from __future__ import annotations

import json
import os
import sqlite3
import stat
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


MEMBERS = ("codex", "claude", "agy")
RECIPIENTS = (*MEMBERS, "all")
MAX_BODY_BYTES = 16_384
MAX_IDEMPOTENCY_KEY_BYTES = 128
# MCP clients include JavaScript runtimes, so cursor and reply identifiers must
# remain exact JSON integers as well as valid SQLite INTEGER values.
MAX_MESSAGE_ID = (1 << 53) - 1
MAX_WAIT_SECONDS = 30.0
MAX_READ_LIMIT = 100
IDENTITY_ASSURANCE = "configured member label; not app or model attestation"
CURSOR_SEMANTICS = "messages replay for the same after_id; advancing after_id " \
    "acknowledges addressed messages through that cursor"
CAPABILITIES = {
    "codex": ("parallel-task-orchestration", "isolated-worktrees", "long-running-goals", "workspace-implementation", "tests-and-integrations"),
    "claude": ("large-context-reasoning", "independent-diff-review", "native-claude-session-messaging", "workspace-implementation", "tests-and-visual-review"),
    "agy": ("fast-mapping-and-debugging", "premise-and-evasion-challenge", "isolated-implementation", "browser-and-artifacts", "multi-model-advice"),
}

class TeamError(ValueError):
    """The request is invalid or would cross the transport boundary."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _repository_identity(repo_root: Path) -> tuple[Path, Path]:
    root = repo_root.resolve()
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    command = [
        "/usr/bin/git", "--no-replace-objects", "-C", str(root), "rev-parse",
        "--show-toplevel", "--path-format=absolute", "--git-common-dir",
    ]
    completed = subprocess.run(
        command,
        env=environment, stdin=subprocess.DEVNULL, capture_output=True, text=True,
        timeout=10, check=False,
    )
    lines = completed.stdout.splitlines()
    if completed.returncode != 0 or len(lines) != 2:
        raise TeamError("repo-root must identify one Git worktree")
    top, common = Path(lines[0]).resolve(), Path(lines[1]).resolve()
    if top != root or not common.is_dir():
        raise TeamError("repo-root must be the exact Git worktree root")
    common_info = common.lstat()
    if common_info.st_uid != os.geteuid():
        raise TeamError("Git common directory must be owned by the current user")
    if stat.S_IMODE(common_info.st_mode) & 0o022:
        raise TeamError("Git common directory must not be group/world writable")
    return top, common


def _secure_store(common_dir: Path) -> Path:
    directory = common_dir / "pipeline-team"
    try:
        info = directory.lstat()
    except FileNotFoundError:
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass
        info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise TeamError("team store directory must be a real directory")
    if info.st_uid != os.geteuid():
        raise TeamError("team store directory must be owned by the current user")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise TeamError("team store directory must not be group/world accessible")
    store = directory / "messages.sqlite3"
    try:
        info = store.lstat()
    except FileNotFoundError:
        try:
            descriptor = os.open(store, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(descriptor)
        info = store.lstat()
    _validate_store_path(common_dir, store)
    return store


def _validate_store_path(common_dir: Path, store: Path) -> tuple[int, int]:
    """Validate static confinement and return the database file identity.

    The owner-only directory protects against other OS users. Inode checks
    also catch ordinary path replacement, but do not attest against the local
    account that owns both the repository and this process.
    """

    directory = store.parent
    info = directory.lstat()
    if directory.parent.resolve() != common_dir or (
        not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
    ):
        raise TeamError("team store directory must be a real repository directory")
    if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise TeamError("team store directory must be owner-only")

    info = store.lstat()
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise TeamError("team store must be one regular file")
    if info.st_uid != os.geteuid():
        raise TeamError("team store must be owned by the current user")
    if info.st_nlink != 1:
        raise TeamError("team store must have one filesystem name")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise TeamError("team store must not be group/world accessible")

    for suffix in ("-wal", "-shm"):
        sidecar = Path(f"{store}{suffix}")
        try:
            sidecar_info = sidecar.lstat()
        except FileNotFoundError:
            continue
        if (
            not stat.S_ISREG(sidecar_info.st_mode)
            or stat.S_ISLNK(sidecar_info.st_mode)
            or sidecar_info.st_uid != os.geteuid()
            or sidecar_info.st_nlink != 1
            or stat.S_IMODE(sidecar_info.st_mode) & 0o077
        ):
            raise TeamError(f"team store {suffix[1:]} sidecar must be owner-only")
    return info.st_dev, info.st_ino


class Store:
    def __init__(self, repo_root: Path | str) -> None:
        self.repo_root, self.common_dir = _repository_identity(Path(repo_root))
        self.path = _secure_store(self.common_dir)
        self._file_identity = _validate_store_path(self.common_dir, self.path)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        observed = _validate_store_path(self.common_dir, self.path)
        if observed != self._file_identity:
            raise TeamError("team store file was replaced after initialization")
        connection = sqlite3.connect(self.path, timeout=10)
        observed_after_open = _validate_store_path(self.common_dir, self.path)
        if observed_after_open != self._file_identity:
            connection.close()
            raise TeamError("team store file changed while opening")
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    @contextmanager
    def session(self):
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        for attempt in range(50):
            try:
                self._initialize_once()
                return
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).casefold() or attempt == 49:
                    raise
                time.sleep(0.02)

    def _initialize_once(self) -> None:
        with self.session() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                f"""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL
                ) WITHOUT ROWID;
                CREATE TABLE IF NOT EXISTS members (
                    name TEXT PRIMARY KEY CHECK (name IN ('codex','claude','agy')),
                    instance_id TEXT NOT NULL, capabilities TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                ) WITHOUT ROWID;
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT
                        CHECK(id <= {MAX_MESSAGE_ID}),
                    idempotency_key TEXT NOT NULL,
                    sender TEXT NOT NULL CHECK (sender IN ('codex','claude','agy')),
                    recipient TEXT NOT NULL CHECK (recipient IN ('codex','claude','agy','all')),
                    body TEXT NOT NULL, reply_to INTEGER REFERENCES messages(id),
                    created_at TEXT NOT NULL, UNIQUE(sender,idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS messages_recipient_id ON messages(recipient,id);
                CREATE INDEX IF NOT EXISTS messages_sender_id ON messages(sender,id);
                CREATE TRIGGER IF NOT EXISTS messages_json_safe_id
                AFTER INSERT ON messages
                WHEN NEW.id > {MAX_MESSAGE_ID}
                BEGIN
                    SELECT RAISE(ABORT, 'message id exceeds JSON-safe range');
                END;
                CREATE TABLE IF NOT EXISTS deliveries (
                    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
                    member TEXT NOT NULL CHECK (member IN ('codex','claude','agy')),
                    delivered_at TEXT NOT NULL, PRIMARY KEY(message_id,member)
                ) WITHOUT ROWID;
                """
            )
            identity = str(self.common_dir)
            connection.execute(
                "INSERT OR IGNORE INTO metadata(key,value) "
                "VALUES('git_common_dir',?)",
                (identity,),
            )
            row = connection.execute(
                "SELECT value FROM metadata WHERE key='git_common_dir'"
            ).fetchone()
            if row is None or row["value"] != identity:
                raise TeamError("team store belongs to a different repository")
            high_water = connection.execute(
                "SELECT COALESCE(MAX(id),0) FROM messages"
            ).fetchone()[0]
            if high_water > MAX_MESSAGE_ID:
                raise TeamError("team store contains a non-portable message id")

    def touch(self, member: str, instance_id: str) -> None:
        with self.session() as connection:
            connection.execute(
                """INSERT INTO members(name,instance_id,capabilities,last_seen)
                VALUES(?,?,?,?) ON CONFLICT(name) DO UPDATE SET
                instance_id=excluded.instance_id, capabilities=excluded.capabilities,
                last_seen=excluded.last_seen""",
                (member, instance_id, json.dumps(CAPABILITIES[member]), now()),
            )

    @staticmethod
    def message_view(connection: sqlite3.Connection, message_id: int) -> dict:
        if (
            isinstance(message_id, bool) or not isinstance(message_id, int)
            or not 1 <= message_id <= MAX_MESSAGE_ID
        ):
            raise TeamError("message id is outside the portable transport range")
        row = connection.execute(
            "SELECT id,idempotency_key,sender,recipient,body,reply_to,created_at "
            "FROM messages WHERE id=?", (message_id,),
        ).fetchone()
        if row is None:
            raise TeamError(f"message {message_id} does not exist")
        acknowledged = [item["member"] for item in connection.execute(
            "SELECT member FROM deliveries WHERE message_id=? ORDER BY member", (message_id,))]
        replies = [item["id"] for item in connection.execute(
            "SELECT id FROM messages WHERE reply_to=? ORDER BY id", (message_id,))]
        return {
            **dict(row), "acknowledged_by": acknowledged, "replies": replies,
            "identity_assurance": IDENTITY_ASSURANCE,
            "grants_authority": False,
        }
