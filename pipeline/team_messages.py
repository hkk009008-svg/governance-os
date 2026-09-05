"""Validated message operations over the repository-scoped team store."""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

from team_store import (
    CAPABILITIES, MAX_BODY_BYTES, MAX_IDEMPOTENCY_KEY_BYTES, MAX_READ_LIMIT,
    MAX_MESSAGE_ID, MAX_WAIT_SECONDS, CURSOR_SEMANTICS, IDENTITY_ASSURANCE, MEMBERS,
    RECIPIENTS, Store, TeamError, now,
)


_KEY_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_STATUS_PREVIEW_BYTES = 256


class Team:
    """One configured member label's view of the shared conversation."""

    def __init__(self, repo_root: Path | str, member: str) -> None:
        if member not in MEMBERS:
            raise TeamError(f"member must be one of {', '.join(MEMBERS)}")
        self.member = member
        self.store = Store(repo_root)
        self.repo_root, self.common_dir = self.store.repo_root, self.store.common_dir
        self.store_path = self.store.path
        self.instance_id = uuid.uuid4().hex

    def _touch(self) -> None:
        self.store.touch(self.member, self.instance_id)

    @staticmethod
    def _validate_key(key: str) -> str:
        if not isinstance(key, str) or _KEY_RE.fullmatch(key) is None:
            raise TeamError(
                "idempotency_key must be 1-128 ASCII letters, digits, '.', '_', ':', or '-'"
            )
        if len(key.encode()) > MAX_IDEMPOTENCY_KEY_BYTES:
            raise TeamError("idempotency_key exceeds the byte limit")
        return key

    @staticmethod
    def _validate_body(body: str) -> str:
        if not isinstance(body, str) or not body.strip() or "\x00" in body:
            raise TeamError("body must be nonempty UTF-8 text without NUL bytes")
        try:
            size = len(body.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise TeamError("body must be valid UTF-8 text") from exc
        if size > MAX_BODY_BYTES:
            raise TeamError(f"body exceeds {MAX_BODY_BYTES} UTF-8 bytes")
        return body

    def send(
        self, recipient: str, body: str, *, idempotency_key: str,
        reply_to: int | None = None,
    ) -> dict:
        """Queue one message; queue success is not acknowledgement or a reply."""
        if recipient not in RECIPIENTS:
            raise TeamError(f"recipient must be one of {', '.join(RECIPIENTS)}")
        if recipient == self.member:
            raise TeamError("recipient must be another member or all")
        body, key = self._validate_body(body), self._validate_key(idempotency_key)
        if reply_to is not None and (
            isinstance(reply_to, bool) or not isinstance(reply_to, int)
            or not 1 <= reply_to <= MAX_MESSAGE_ID
        ):
            raise TeamError(
                f"reply_to must be a message id from 1 to {MAX_MESSAGE_ID}"
            )
        with self.store.session() as connection:
            if reply_to is not None:
                original = connection.execute(
                    "SELECT sender,recipient FROM messages WHERE id=?", (reply_to,)
                ).fetchone()
                if original is None:
                    raise TeamError("reply target does not exist")
                if original["sender"] == self.member or original["recipient"] not in {
                    self.member, "all",
                }:
                    raise TeamError("reply target was not addressed to this member")
                if recipient != original["sender"]:
                    raise TeamError("reply recipient must be the original sender")
            cursor = connection.execute(
                "INSERT INTO messages(idempotency_key,sender,recipient,body,reply_to,created_at) "
                "VALUES(?,?,?,?,?,?) ON CONFLICT(sender,idempotency_key) DO NOTHING",
                (key, self.member, recipient, body, reply_to, now()),
            )
            existing = connection.execute(
                "SELECT id,recipient,body,reply_to FROM messages "
                "WHERE sender=? AND idempotency_key=?", (self.member, key),
            ).fetchone()
            assert existing is not None
            if (existing["recipient"], existing["body"], existing["reply_to"]) != (
                recipient, body, reply_to,
            ):
                raise TeamError("idempotency key already names a different message")
            result = self.store.message_view(connection, existing["id"])
            result["state"] = "queued" if cursor.rowcount == 1 else "already-queued"
        self._touch()
        return result

    @staticmethod
    def _validate_read(after_id: int, limit: int, wait_seconds: float) -> None:
        if (
            isinstance(after_id, bool) or not isinstance(after_id, int)
            or not 0 <= after_id <= MAX_MESSAGE_ID
        ):
            raise TeamError(
                f"after_id must be an integer from 0 to {MAX_MESSAGE_ID}"
            )
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_READ_LIMIT:
            raise TeamError(f"limit must be an integer from 1 to {MAX_READ_LIMIT}")
        if isinstance(wait_seconds, bool) or not isinstance(wait_seconds, (int, float)):
            raise TeamError("wait_seconds must be a finite number")
        if not 0 <= float(wait_seconds) <= MAX_WAIT_SECONDS:
            raise TeamError(f"wait_seconds must be between 0 and {MAX_WAIT_SECONDS:g}")

    def wait(
        self, *, after_id: int = 0, limit: int = 50, wait_seconds: float = 0
    ) -> dict:
        """Acknowledge through ``after_id`` and return the later log slice.

        Returned messages remain replayable until a later call advances the
        cursor. This makes client progress, rather than a server-side flush,
        the only acknowledgement signal.
        """

        self._validate_read(after_id, limit, wait_seconds)
        deadline = time.monotonic() + float(wait_seconds)
        first_read = True
        while True:
            with self.store.session() as connection:
                if first_read:
                    high_water = connection.execute(
                        "SELECT COALESCE(MAX(id),0) FROM messages"
                    ).fetchone()[0]
                    if after_id > high_water:
                        raise TeamError("after_id is beyond the current message log")
                    frontier_row = connection.execute(
                        "SELECT message_id FROM cursor_frontiers WHERE member=?",
                        (self.member,),
                    ).fetchone()
                    frontier = frontier_row["message_id"] if frontier_row else 0
                    if after_id > frontier:
                        skipped = connection.execute(
                            "SELECT id FROM messages m WHERE m.id>? AND m.id<=? "
                            "AND m.sender!=? AND (m.recipient=? OR m.recipient='all') "
                            "AND NOT EXISTS (SELECT 1 FROM deliveries d "
                            "WHERE d.message_id=m.id AND d.member=?) "
                            "ORDER BY m.id LIMIT 1",
                            (frontier, after_id, self.member, self.member, self.member),
                        ).fetchone()
                        if skipped is not None:
                            raise TeamError(
                                "after_id would skip unread addressed messages; "
                                "use next_cursor returned by team_wait"
                            )
                        connection.execute(
                            "INSERT INTO cursor_frontiers(member,message_id) VALUES(?,?) "
                            "ON CONFLICT(member) DO UPDATE SET message_id="
                            "MAX(cursor_frontiers.message_id,excluded.message_id)",
                            (self.member, after_id),
                        )
                    if after_id:
                        connection.execute(
                            "INSERT OR IGNORE INTO deliveries(message_id,member,delivered_at) "
                            "SELECT id,?,? FROM messages WHERE id<=? AND sender!=? "
                            "AND (recipient=? OR recipient='all')",
                            (self.member, now(), after_id, self.member, self.member),
                        )
                rows = list(connection.execute(
                    "SELECT id FROM messages WHERE id>? AND sender!=? "
                    "AND (recipient=? OR recipient='all') ORDER BY id LIMIT ?",
                    (after_id, self.member, self.member, limit),
                ))
                if rows:
                    connection.execute(
                        "INSERT INTO cursor_frontiers(member,message_id) VALUES(?,?) "
                        "ON CONFLICT(member) DO UPDATE SET message_id="
                        "MAX(cursor_frontiers.message_id,excluded.message_id)",
                        (self.member, rows[-1]["id"]),
                    )
                    messages = [
                        self.store.message_view(connection, row["id"]) for row in rows
                    ]
                    break
            first_read = False
            if time.monotonic() >= deadline:
                messages = []
                break
            time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
        self._touch()
        return {
            "member": self.member,
            "messages": messages,
            "acknowledged_through": after_id,
            "next_cursor": messages[-1]["id"] if messages else after_id,
            "cursor_semantics": CURSOR_SEMANTICS,
            "identity_assurance": IDENTITY_ASSURANCE,
            "grants_authority": False,
        }

    def status(self, *, message_id: int | None = None) -> dict:
        """Return recent sent previews, or one own sent message in full.

        Read-back does not advance an inbound cursor or acknowledge messages.
        Activity and pending counts are never a liveness or authority claim.
        """
        if message_id is not None and (
            isinstance(message_id, bool) or not isinstance(message_id, int)
            or not 1 <= message_id <= MAX_MESSAGE_ID
        ):
            raise TeamError(f"message_id must be an integer from 1 to {MAX_MESSAGE_ID}")
        self._touch()
        with self.store.session() as connection:
            if message_id is not None and connection.execute(
                "SELECT id FROM messages WHERE id=? AND sender=?",
                (message_id, self.member),
            ).fetchone() is None:
                raise TeamError("message_id is not a message sent by this member")
            observed = {row["name"]: row for row in connection.execute(
                "SELECT name,capabilities,last_seen FROM members"
            )}
            members = []
            for name in MEMBERS:
                row = observed.get(name)
                pending = connection.execute(
                    "SELECT count(*) AS n FROM messages m WHERE m.sender!=? "
                    "AND (m.recipient=? OR m.recipient='all') AND NOT EXISTS "
                    "(SELECT 1 FROM deliveries d WHERE d.message_id=m.id AND d.member=?)",
                    (name, name, name),
                ).fetchone()["n"]
                members.append({
                    "name": name, "last_seen": row["last_seen"] if row else None,
                    "capabilities": json.loads(row["capabilities"]) if row else list(CAPABILITIES[name]),
                    "pending": pending,
                })
            if message_id is not None:
                ids = [message_id]
            else:
                ids = [row["id"] for row in connection.execute(
                    "SELECT id FROM messages WHERE sender=? ORDER BY id DESC LIMIT 50",
                    (self.member,),
                )][::-1]
            sent = [self.store.message_view(connection, item_id) for item_id in ids]
            if message_id is None:
                for item in sent:
                    body = item.pop("body").encode("utf-8")
                    item.update(
                        body_preview=body[:_STATUS_PREVIEW_BYTES].decode(
                            "utf-8", errors="ignore"
                        ),
                        body_bytes=len(body),
                        body_truncated=len(body) > _STATUS_PREVIEW_BYTES,
                    )
        return {
            "member": self.member, "members": members, "sent": sent,
            "store": str(self.store_path),
            "liveness": "last_seen is activity evidence only; it does not prove an app is open",
            "identity_assurance": IDENTITY_ASSURANCE,
            "cursor_semantics": CURSOR_SEMANTICS,
            "grants_authority": False,
        }

    def close(self) -> None:
        """No persistent connection is held; provided for scoped callers."""
