"""The single authoritative cutover (Slice 2.5 §5c): preflight -> sign+append all
carriers in §6 total order -> backfill 6 cursors -> one authority-flip act. On ANY
append/cursor failure, tear down the partial events ref so no reader sees a half bus.

Consumes (never edits) the Slice-2 substrate: preflight_bus_init, RefEventStore,
advance_cursor; and the Phase-B legacy_projector + cursor_backfill. Pure composition.

API seam (verified at exec, diverged from the plan's snapshot): the Phase-B
`legacy_projector.project()` consumes the `sent/` directory DIRECTLY (not a coord
root), while `cursor_backfill` resolves `coordination/mailbox` from a coord root via
`_mailbox_base`. run_cutover takes the coord root and bridges the two: it derives the
sent/ dir from the root with the SAME `_mailbox_base` logic cursor_backfill uses, so
the projector + backfill can never disagree about which mailbox they are migrating.
"""
from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path

from threeway import cursor_backfill, gitcas, keys, legacy_projector
from threeway.gitcas import preflight_bus_init
from threeway.refstore import EVENTS_REF, RefEventStore

# The fixed cursor roster lives in cursor_backfill (single source, ADR-051) — so this
# snapshot/advance loop and the seen/ canonicalization can never disagree about the seats.
_SEATS = cursor_backfill.SEATS


def _cursor_ref(seat: str) -> str:
    # MUST match RefEventStore._cursor_ref (refstore.py:200) EXACTLY — teardown
    # restores/deletes the very refs advance_cursor writes. There is no shared
    # CURSORS_REF_PREFIX constant, so this f-string mirrors that literal by hand;
    # if refstore's cursor-ref scheme ever changes, this must change in lockstep.
    return f"refs/threeway/cursors/{seat}"


@dataclass
class CutoverResult:
    appended: int
    cursors: dict[str, int]
    # Readers use coherent refs rather than a separate marker, so success means
    # this invocation performed the local authority flip. Protected deployment
    # still requires direct post-action proof.
    activated: bool


def _sent_dir(coord_root):
    # SINGLE source of truth for the mailbox location, shared with cursor_backfill, so
    # the projection (this dir) and the backfill (seen/ under the same base) can never
    # diverge across the two layouts (root-containing-coordination OR root-is-coordination).
    return cursor_backfill._mailbox_base(coord_root) / "sent"


def _read_iso_cursors(coord_root) -> dict:
    # ADR-051: canonical, roster-validated seat keys (shared with cursor_backfill.backfill) so
    # a stray/case-variant seen/*.txt can't coin a phantom key or silently drop a real seat.
    return cursor_backfill.canonical_seat_cursors(cursor_backfill._seen_dir(coord_root))


def _snapshot_refs(repo) -> dict:
    # Read-only diagnostic/test helper. Runtime rollback journals the actual
    # predecessor/new OIDs returned by each successful CAS; it does not rely on
    # a pre-run snapshot that could miss an interleaving writer.
    snap = {EVENTS_REF: gitcas.rev_parse(repo, EVENTS_REF)}
    for seat in _SEATS:
        ref = _cursor_ref(seat)
        snap[ref] = gitcas.rev_parse_any(repo, ref)   # cursor refs point at a BLOB, not a commit
    return snap


class TeardownError(RuntimeError):
    """One or more refs could not be restored to their pre-run state during teardown.
    Raised CHAINED from the original cutover failure (`raise ... from original`) so the
    real cause is surfaced, never masked — and only after a best-effort pass over EVERY
    ref, so one stuck ref does not strand the rest (ADR-044)."""


@dataclass
class RefMutation:
    """One contiguous ref mutation chain owned by this cutover invocation."""

    restore_oid: str | None
    expected_oid: str
    contiguous: bool = True


def _record_write(
    written: dict[str, RefMutation],
    ref: str,
    previous_oid: str | None,
    new_oid: str,
) -> None:
    mutation = written.get(ref)
    if mutation is None:
        written[ref] = RefMutation(previous_oid, new_oid)
        return
    if mutation.expected_oid != previous_oid:
        mutation.contiguous = False
    mutation.expected_oid = new_oid


def _teardown(
    repo,
    written: dict[str, RefMutation],
    original: BaseException | None = None,
) -> None:
    # NON-DESTRUCTIVE + BEST-EFFORT-PER-REF: restore only refs this run successfully
    # wrote, using the exact written OID as update-ref's expected-old CAS. A ref that
    # did not exist pre-run is deleted; a ref that did exist is restored to its prior
    # OID. If another writer moved a ref after this run, CAS refuses rather than
    # clobbering the concurrent value. A single
    # ref's restore failure (e.g. a concurrent writer holding refs/threeway/events.lock ->
    # git exit 128) MUST NOT abort the loop — every OTHER ref still gets restored — NOR
    # mask the original cutover failure. Failures are aggregated and raised as a
    # TeardownError CHAINED FROM `original`; a fully-successful teardown stays silent so
    # the caller's bare `raise` re-raises the original cause unchanged. A delete of an
    # absent ref stays best-effort (check=False) and never contributes a failure.
    failures = []
    for ref, mutation in written.items():
        if not mutation.contiguous:
            failures.append(
                (ref, RuntimeError("a concurrent ref write interleaved with cutover"))
            )
            continue
        oid = mutation.restore_oid
        expected_written_oid = mutation.expected_oid
        try:
            if oid is None:
                subprocess.run(
                    [
                        "git", "-C", str(repo), "update-ref", "-d", ref,
                        expected_written_oid,
                    ],
                    capture_output=True,
                    env=gitcas._env(),
                    check=True,
                )
            else:
                subprocess.run(
                    [
                        "git", "-C", str(repo), "update-ref", ref, oid,
                        expected_written_oid,
                    ],
                    capture_output=True,
                    env=gitcas._env(),
                    check=True,
                )
        except subprocess.CalledProcessError as exc:
            failures.append((ref, exc))
    if failures:
        refs = ", ".join(ref for ref, _ in failures)
        raise TeardownError(
            f"teardown could not restore {len(failures)} ref(s) to pre-run state: {refs}"
        ) from original


def run_cutover(repo, coord_root, importer_key, *, force: bool = False) -> CutoverResult:
    """Operator note: at live scale (~768 events) the append loop is O(n^2) — RefEventStore
    re-scans every prior event for idempotency on EACH append — so it runs ~50 min with NO
    progress output. That is EXPECTED, not a hang; do not abort it as stuck."""
    # (1) FAIL-CLOSED pre-check: refuses over any pre-existing refs/threeway/*, never
    #     deletes. force=True is an explicit operator acknowledgement (gitcas:243-244).
    preflight_bus_init(repo, force=force)

    # (1b) Journal each successful CAS's actual predecessor/new OIDs. Teardown
    #      restores only one contiguous mutation chain owned by this invocation.
    written: dict[str, RefMutation] = {}

    # (2) project the legacy bus into carrier event_sent Events in §6 total order. The
    #     projector reads the sent/ dir directly + already returns events total-ordered.
    sent_dir = _sent_dir(coord_root)
    carriers = legacy_projector.project(sent_dir)

    store = RefEventStore(repo)
    appended = 0
    try:
        # (3) sign + append every carrier in order (importer key needs NO registry
        #     entry: event_sent is not load-bearing -> gate skips its signature).
        for ev in carriers:
            store.append(
                ev,
                importer_key,
                _on_commit=lambda previous, oid: _record_write(
                    written, EVENTS_REF, previous, oid
                ),
            )
            appended += 1
    except BaseException as original:
        # (5) on ANY append failure, restore every ref to its actual predecessor.
        #     _teardown surfaces any restore failure CHAINED from `original` (never masks).
        _teardown(repo, written, original)
        raise

    # (4) backfill all 6 seats' cursors from the §6 ISO->seq map. total_order over the
    #     carrier filenames validates totality (raises on a non-event filename) before we
    #     advance any cursor; iso_to_seq_map recomputes the same order internally from the
    #     raw names + the seat ISO cursors (its real Phase-B signature).
    #     These validation/seq-map steps run AFTER the bus has been appended over, so they
    #     MUST sit inside the teardown guard too (ADR-045, a Rule-13 sibling of ADR-044):
    #     a total_order ValueError (bad carrier name) or a _read_iso_cursors OSError
    #     (unreadable seen/*.txt) would otherwise strand the half-built events ref with no
    #     restore. cursors={} stays outside (a pure init that cannot raise).
    cursors = {}
    try:
        carrier_names = [ev.payload["source_filename"] for ev in carriers]
        cursor_backfill.total_order(carrier_names)        # validates totality (raises on a bad name)
        # ADR-049: on a force=True RE-RUN after a prior run reached step 5b, seen/*.txt hold
        # SCALAR seqs (the prior backfill rewrote them) — re-deriving via iso_to_seq_map would
        # lexicographically over-advance the cursor refs past unread events. If the prior run
        # archived the ISO->seq map (manifest exists), source the authoritative seqs from it;
        # else (first run) compute from the still-ISO seen cursors.
        if cursor_backfill._manifest_path(coord_root).exists():
            seq_map = cursor_backfill.archived_seq_map(coord_root)
        else:
            seq_map = cursor_backfill.iso_to_seq_map(carrier_names, _read_iso_cursors(coord_root))
        for seat in _SEATS:
            # ADR-051: a roster seat MISSING from the seq map means its seen/<seat>.txt was
            # absent — refuse loudly rather than seq_map.get(seat, 0), which would set cursor 0
            # and silently re-process the ENTIRE migrated bus. (An explicit empty seen/<seat>.txt
            # is present-with-value-"" -> seq 0, the legitimate "this seat starts at 0" assertion.)
            if seat not in seq_map:
                raise cursor_backfill.SeatCursorError(
                    f"seat {seat!r} has no cursor in the backfill seq map; refusing to silently "
                    f"set cursor 0 and re-process the entire migrated bus (ADR-051). Create an "
                    f"explicit empty seen/{seat}.txt to assert cursor 0, or restore its cursor.")
            seq = seq_map[seat]                            # seq==0 allowed (refstore:236-240)
            store.advance_cursor(
                seat,
                seq,
                _on_commit=lambda previous, oid, ref=_cursor_ref(seat): _record_write(
                    written, ref, previous, oid
                ),
            )
            cursors[seat] = store.cursor_seq(seat)
    except BaseException as original:
        _teardown(repo, written, original)
        raise

    # (5b) ALSO rewrite the legacy seen/*.txt to scalar + archive the reversible manifest.
    #      This remains part of the all-or-not-ready cutover boundary: if filesystem
    #      backfill fails, restore every signed-bus ref to its actual predecessor. The
    #      backfill itself is archive-once/idempotent, so any completed filesystem writes
    #      remain retryable while no partial ref bus is left visible.
    try:
        cursor_backfill.backfill(coord_root)
    except BaseException as original:
        _teardown(repo, written, original)
        raise

    # (6) AUTHORITY FLIP: readers define a coherent event+cursor ref set as live;
    #     no separate executable marker exists. This separately authorized cutover
    #     invocation is therefore the local flip, followed by direct state proof.
    return CutoverResult(appended=appended, cursors=cursors, activated=True)


def main(argv=None) -> int:
    """CLI entry: `python -m threeway.cutover --repo . --coord-root . --yes`.

    The single authority-flip cutover is IRREVERSIBLE (DECISIONS.md ADR-045): it REFUSES without an
    explicit --yes, so even an accidental `python -m threeway.cutover` cannot fire it. The importer
    key is EPHEMERAL — `event_sent` carriers are not load-bearing, so the gate never reads their
    signature (a registry entry is intentionally unnecessary; see run_cutover step 3)."""
    ap = argparse.ArgumentParser(
        description="Execute the Slice 2.5 legacy->signed-bus cutover (IRREVERSIBLE).")
    ap.add_argument("--repo", default=".", help="git repo holding refs/threeway/*")
    ap.add_argument("--coord-root", default=".",
                    help="root containing coordination/ (or the coordination dir itself)")
    ap.add_argument("--force", action="store_true",
                    help="acknowledge a pre-existing refs/threeway/* (documented force re-run)")
    ap.add_argument("--yes", action="store_true",
                    help="REQUIRED: confirm the irreversible authority flip")
    args = ap.parse_args(argv)
    if not args.yes:
        print("REFUSING: the legacy->signed-bus cutover is IRREVERSIBLE (ADR-045). "
              "Re-run with --yes to confirm.")
        return 2
    importer, _ = keys.generate_keypair()   # ephemeral: event_sent is not load-bearing
    res = run_cutover(Path(args.repo), Path(args.coord_root), importer, force=args.force)
    print(f"Cutover complete: appended {res.appended} carrier events; "
          f"cursors backfilled for {len(res.cursors)} seats; activated={res.activated}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
