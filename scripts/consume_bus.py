#!/usr/bin/env python3
"""consume_bus.py — read signed-bus events addressed to a seat past its cursor and advance the
seat's LOCAL cursor. The bus analog of coordination/bin/consume-events. Raw read: signature
verification is the gate's job, not the consume path (SP2 spec §3.1)."""
import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:                      # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))

from threeway.refstore import (                          # noqa: E402
    CursorContentionExceeded, CursorCorruptionError, RefEventStore,
)
import protocol_mailbox  # noqa: E402

# Only production/review seats own cursors. Coordinators observe and reconcile without
# consuming state, so accepting them here would manufacture authority the role does not have.
SEATS = protocol_mailbox.SEATS


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read bus events addressed to a seat; advance its cursor.")
    ap.add_argument("seat", choices=SEATS)
    ap.add_argument("--kinds", default=None, help="comma-separated kind allowlist")
    ap.add_argument("--no-advance", action="store_true")
    ap.add_argument("--repo-dir", default=".")
    ap.add_argument("--remote", default="origin")
    ap.add_argument(
        "--bus-id",
        default=None,
        help="optional bus filter; filtered reads require --no-advance",
    )
    a = ap.parse_args(argv)
    if a.kinds is not None and not a.no_advance:
        print("REFUSING: --kinds requires --no-advance; a filtered view cannot safely "
              "advance past events it did not show.", file=sys.stderr)
        return 2
    if a.bus_id is not None and not a.no_advance:
        print("REFUSING: --bus-id requires --no-advance; the cursor is shared "
              "across bus IDs and cannot advance past events it did not show.", file=sys.stderr)
        return 2
    remote = (a.remote or None)                          # "" -> None (local); RefEventStore checks `is not None`
    seat = a.seat
    store = RefEventStore(Path(a.repo_dir), remote=remote)
    try:
        cursor = store.cursor_seq(seat)
        if remote is None:
            # Local mode: read only blobs past the cursor (O(unread)), matching
            # bus_unread. Every event with seq > cursor is included regardless
            # of recipient, so its max is still the global tip; an empty result
            # leaves tip == cursor (a monotonic no-op advance).
            events = list(store.iter_events_since(cursor))
            tip = max((ev.seq for ev in events), default=cursor)
        else:
            # Remote mode must sync authority first; iter_events_since is
            # local-only by contract, so the remote path keeps the full read.
            events = list(store.iter_events())
            tip = max((ev.seq for ev in events), default=0)
    except CursorCorruptionError as e:
        print(f"cursor blob corrupt for {seat}: {e}", file=sys.stderr)
        return 1
    kinds = set(a.kinds.split(",")) if a.kinds else None
    shown = [
        ev for ev in events
        if ev.seq > cursor and (a.bus_id is None or ev.bus_id == a.bus_id)
        and ev.recipient in (seat, "all")
        and (kinds is None or ev.kind in kinds)
    ]
    for ev in shown:
        ref = ev.candidate_id or ev.brief_id or "-"
        ssha = (ev.subject_sha or "")[:12] or "-"
        print(f"{ev.seq}\t{ev.kind}\t{ev.sender}\t{ref}\t{ssha}")
    if not a.no_advance:
        try:
            store.advance_cursor(seat, tip)             # local CAS; monotonic no-op for seq<=cur
        except (CursorContentionExceeded, CursorCorruptionError) as e:   # advance re-reads the cursor blob
            print(f"cursor advance failed for {seat}: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
