#!/usr/bin/env python3
"""Resolve unread state without confusing an absent bus with an empty bus.

The mailbox remains authoritative until the local signed bus is demonstrably live:
both ``refs/threeway/events`` and the addressed seat's cursor ref must resolve and
their sequence relationship must be coherent.  A scalar ``seen/<seat>.txt`` cursor
without that proof is interpreted against the canonical ordered mailbox projection.
This is the reversible side of the legacy backfill and prevents an absent bus from
silently rendering ``0 unread``.

Design contract:
* LOCAL ONLY — ``RefEventStore(remote=None)`` never ``_sync()``s (every ``_sync`` call site
  guards on ``self._remote is not None``), so a dashboard with a "NEVER hangs" constraint
  (status.py) can call this without a network round-trip.
* The live cursor is ``store.cursor_seq(seat)`` (the ref-bus head the seat advances via
  consume_bus), NOT the frozen ``seen/*.txt`` scalar (a migration-time sentinel that goes
  stale as the seat consumes). Reading the seen scalar would re-over-count everything since.
* A partially materialized bus is ``incoherent``, not live.
* Returns ``None`` on unavailable/corrupt bus reads so callers render a visible
  sentinel.  An empty *proven-live* bus is a real ``0``/``[]``.
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

from threeway import gitcas                               # noqa: E402


_ISO_CURSOR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_EVENT_NAME_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>director2?|operator2?|coordinator2?)-to-"
    r"(?P<recipient>director2?|operator2?|coordinator2?|all)-"
    r"(?P<kind>[a-z0-9-]+)\.md$"
)
_TS_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-")
_EVENTS_REF = "refs/threeway/events"


@dataclass(frozen=True)
class BusAuthority:
    """Local proof state for one seat's signed-bus event/cursor pair."""

    state: str  # absent | live | incoherent
    detail: str
    cursor: int | None = None


@dataclass(frozen=True)
class UnreadResolution:
    """One authoritative unread answer and the transport evidence behind it."""

    count: int | None
    source: str  # mailbox | mailbox-fallback | ref-bus | unavailable
    transport: str  # absent | live | incoherent
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


def bus_authority_state(repo_root, seat: str) -> BusAuthority:
    """Return whether the local event ref and *seat* cursor form a live bus.

    Merely seeing a scalar legacy cursor is not authority proof.  The event ref
    and matching cursor ref must both exist; a cursor above the event index is a
    partial/corrupt cutover and is reported as incoherent.
    """

    root = Path(repo_root)
    try:
        tip = gitcas.rev_parse(root, _EVENTS_REF)
        cursor_ref = f"refs/threeway/cursors/{seat}"
        cursor_oid = gitcas.rev_parse_any(root, cursor_ref)
    except Exception as exc:
        return BusAuthority("incoherent", f"cannot inspect local bus refs: {exc}")
    if tip is None and cursor_oid is None:
        return BusAuthority("absent", "local event and seat cursor refs are absent")
    if tip is None:
        return BusAuthority(
            "incoherent", f"{cursor_ref} exists but {_EVENTS_REF} is absent"
        )
    if cursor_oid is None:
        return BusAuthority(
            "incoherent", f"{_EVENTS_REF} exists but {cursor_ref} is absent"
        )
    try:
        raw = gitcas.read_blob(root, cursor_oid)
        cursor = int(raw.decode("utf-8").strip())
        if cursor < 0:
            raise ValueError("cursor is negative")
        sequences = gitcas.list_index_seqs(root, tip)
    except Exception as exc:
        return BusAuthority("incoherent", f"cannot read bus cursor/index: {exc}")
    if not sequences:
        return BusAuthority("incoherent", f"{_EVENTS_REF} has no indexed events", cursor)
    if sequences != list(range(1, sequences[-1] + 1)):
        return BusAuthority(
            "incoherent", "event index sequence is not contiguous", cursor
        )
    if cursor != 0 and cursor not in sequences:
        return BusAuthority(
            "incoherent",
            f"cursor {cursor} has no matching event sequence",
            cursor,
        )
    if cursor > sequences[-1]:
        return BusAuthority(
            "incoherent",
            f"cursor {cursor} is beyond event head {sequences[-1]}",
            cursor,
        )
    return BusAuthority("live", "local event and seat cursor refs are coherent", cursor)


def ordered_mailbox_events(event_filenames) -> list[str]:
    """Return the cutover's canonical total order for mailbox event names."""

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
        key=lambda name: (_EVENT_NAME_RE.fullmatch(name).group("ts"), name),
    )


def mailbox_events_after_scalar(cursor, event_filenames) -> list[str]:
    """Map a backfilled scalar cursor back onto the canonical mailbox projection.

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
    *,
    bus_id: str = "prod",
) -> UnreadResolution:
    """Resolve unread through the proven authority, with a mailbox fallback.

    ISO cursors are native mailbox cursors.  Scalar cursors use the ref-bus only
    when :func:`bus_authority_state` is ``live``; otherwise the same scalar is
    applied to the canonical mailbox carrier order.
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
        return UnreadResolution(count, "mailbox", "absent", "ISO mailbox cursor")
    if not is_migrated_cursor(raw):
        return UnreadResolution(
            None, "unavailable", "incoherent", f"invalid cursor {raw!r}"
        )

    authority = bus_authority_state(repo_root, seat)
    if authority.state == "live":
        events = bus_unread_events(repo_root, seat, bus_id=bus_id)
        if events is None:
            return UnreadResolution(
                None,
                "unavailable",
                "incoherent",
                "live bus proof succeeded but unread read failed",
            )
        return UnreadResolution(
            len(events), "ref-bus", "live", authority.detail
        )

    try:
        remaining = mailbox_events_after_scalar(raw, names)
    except Exception as exc:
        return UnreadResolution(
            None,
            "unavailable",
            "incoherent",
            f"{authority.detail}; mailbox fallback failed: {exc}",
        )
    return UnreadResolution(
        len(_addressed(remaining, seat)),
        "mailbox-fallback",
        authority.state,
        authority.detail,
    )


def bus_unread_events(repo_root, seat: str, *, bus_id: str = "prod") -> list | None:
    """Signed-bus events addressed to *seat* past its LIVE ref-bus cursor, LOCAL refs only.

    Mirrors consume_bus.py's filter (seq > cursor ∧ bus_id ∧ recipient ∈ {seat, "all"}).
    Returns ``None`` if the bus is unavailable/corrupt (caller degrades to a sentinel);
    an empty list means a reachable-but-empty bus.
    """
    if bus_authority_state(repo_root, seat).state != "live":
        return None
    try:
        # Lazy import keeps the fixed mailbox writer's ``python -S`` path
        # stdlib-only.  The signed-event reader is needed only after live bus
        # authority has already been proven.
        from threeway.refstore import RefEventStore

        store = RefEventStore(Path(repo_root), remote=None)   # remote=None => no _sync => LOCAL ONLY
        cursor = store.cursor_seq(seat)
        # O(unread): read only the blobs past the cursor, NOT the whole bus. all_events()
        # over the live bus is ~14s (subprocess git per blob); a dashboard calls this once
        # per seat, so the seq>cursor floor (iter_events_since) is load-bearing for the
        # "status.py NEVER hangs" contract. The seq gate lives in iter_events_since (pinned
        # non-vacuous in tests/unit/test_threeway_activation_scripts.py::
        # test_bus_unread_script); here we apply only the bus_id+addressee domain filters.
        events = list(store.iter_events_since(cursor))
    except Exception:
        # Dashboard never-crash + silent-degradation guard: a corrupt cursor blob or a
        # non-bus repo surfaces as None, never a traceback and never a misleading 0.
        return None
    return [ev for ev in events if ev.bus_id == bus_id and ev.recipient in (seat, "all")]


def bus_unread_count(repo_root, seat: str, *, bus_id: str = "prod") -> int | None:
    """Count of :func:`bus_unread_events`; ``None`` propagates the unavailable signal."""
    evs = bus_unread_events(repo_root, seat, bus_id=bus_id)
    return None if evs is None else len(evs)


def format_unread(ev) -> str:
    """Compact one-line descriptor for an unread bus event — there is no legacy filename
    to surface for a migrated seat, so dashboards print this instead."""
    ref = ev.candidate_id or ev.brief_id or "-"
    base = f"seq{ev.seq}:{ev.kind}:{ev.sender}->{ev.recipient}"
    return base if ref == "-" else f"{base}:{ref}"
