#!/usr/bin/env python3
"""Resolve unread state against the mailbox, the only coordination transport.

The signed ref-bus this module used to hedge against is gone: it was dormant
on two independent axes (``governance.toml`` declared ``transport = "mailbox"``
and ``refs/threeway/*`` held zero refs), so every probe of it was already
short-circuited.  With one transport there is no authority to prove and no
"unconsulted bus mistaken for an empty one" failure mode to defend against.

What survives is the part that was always load-bearing: a scalar cursor is
interpreted against the canonical ordered mailbox projection, so a legacy
cursor can never silently render ``0 unread``.  An invalid cursor or an
unorderable corpus resolves to ``unavailable``, never to zero.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:                      # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))

import protocol_mailbox  # noqa: E402

_ISO_CURSOR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_EVENT_NAME_RE = protocol_mailbox.EVENT_NAME_RE
_TS_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-")


@dataclass(frozen=True)
class UnreadResolution:
    """One authoritative unread answer and the evidence behind it."""

    count: int | None
    source: str  # mailbox | mailbox-fallback | unavailable
    transport: str  # mailbox | incoherent
    detail: str


def is_migrated_cursor(cursor) -> bool:
    """True iff *cursor* is a scalar ``seq`` (post-cutover sentinel), not an ISO ts or
    an "(unavailable)" string. Tolerates surrounding whitespace; "" / blank are False."""
    return bool(cursor) and str(cursor).strip().isdigit()


def _is_iso_cursor(cursor: str) -> bool:
    if _ISO_CURSOR_RE.fullmatch(cursor) is None:
        return False
    try:
        datetime.strptime(cursor, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def ordered_mailbox_events(event_filenames) -> list[str]:
    """Return the canonical total order for mailbox event names."""

    events: list[str] = []
    for name in event_filenames:
        if _EVENT_NAME_RE.fullmatch(name):
            events.append(name)
        elif name.endswith(".md") and _TS_PREFIX_RE.match(name):
            raise ValueError(
                f"mailbox filename looks like an event but is malformed: {name!r}"
            )
    return sorted(
        events,
        key=lambda name: (_EVENT_NAME_RE.fullmatch(name).group("stamp"), name),
    )


def mailbox_events_after_scalar(cursor, event_filenames) -> list[str]:
    """Map a legacy scalar cursor back onto the canonical mailbox projection.

    ``cursor == 0`` means before the first carrier.  A value beyond the corpus is
    incoherent and must not be treated as an empty inbox.
    """

    if not is_migrated_cursor(cursor):
        raise ValueError("mailbox scalar cursor is not a non-negative integer")
    ordered = ordered_mailbox_events(event_filenames)
    position = int(str(cursor).strip())
    if position > len(ordered):
        raise ValueError(
            f"scalar cursor {position} is beyond mailbox corpus {len(ordered)}"
        )
    return ordered[position:]


def _addressed(names: list[str], seat: str) -> list[str]:
    return [
        name
        for name in names
        if f"-to-{seat}-" in name or "-to-all-" in name
    ]


def resolve_unread(
    repo_root,
    seat: str,
    cursor,
    event_filenames,
    **_ignored,
) -> UnreadResolution:
    """Resolve unread against the mailbox projection.

    ISO cursors are native mailbox cursors.  Legacy scalar cursors are applied
    to the canonical mailbox carrier order rather than to a bus that no longer
    exists.
    """

    raw = str(cursor).strip()
    names = list(event_filenames)
    if _is_iso_cursor(raw):
        try:
            ordered = ordered_mailbox_events(names)
        except Exception as exc:
            return UnreadResolution(
                None, "unavailable", "incoherent", f"mailbox order invalid: {exc}"
            )
        dash = raw.replace(":", "-")
        count = sum(
            name[:20] > dash
            for name in _addressed(ordered, seat)
        )
        return UnreadResolution(count, "mailbox", "mailbox", "ISO mailbox cursor")
    if not is_migrated_cursor(raw):
        return UnreadResolution(
            None, "unavailable", "incoherent", f"invalid cursor {raw!r}"
        )
    try:
        remaining = mailbox_events_after_scalar(raw, names)
    except Exception as exc:
        return UnreadResolution(
            None, "unavailable", "incoherent", f"mailbox projection failed: {exc}"
        )
    return UnreadResolution(
        len(_addressed(remaining, seat)),
        "mailbox-fallback",
        "mailbox",
        "legacy scalar cursor read against the canonical mailbox order",
    )
