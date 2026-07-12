#!/usr/bin/env python3
"""Orthogonal packet-state derivation from legacy capacity-packet fields (ADR-017).

The capacity-packet ``status`` field overloads work-lifecycle, seat-capacity,
and verification into one string. This module DERIVES the orthogonal
``work_state`` and ``verification_state`` dimensions from the legacy
``status`` / ``packet_type`` / ``done_evidence`` fields.
It is READ-ONLY: it writes no packet, adds no field, and changes no gate. The
gate remap (Part B) is deferred (see ADR-017).

The load-bearing insight: a packet at ``status="blocked"`` that carries
completion ``done_evidence`` is work-COMPLETE but held at ``blocked`` to
satisfy G1 coverage — ``derive_work_state`` reports it as ``completed``, making
the overloading visible.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WORK_STATES = (
    "queued", "ready", "running", "blocked",
    "completed", "failed", "superseded", "cancelled",
)
VERIFICATION_STATES = (
    "not_required", "pending", "go", "nits", "fail", "unable_to_verify",
)

# Allowed work_state transitions (Part-B gate validation will consume this).
WORK_TRANSITIONS: dict[str, frozenset[str]] = {
    "queued": frozenset({"ready", "cancelled", "superseded"}),
    "ready": frozenset({"running", "cancelled", "superseded"}),
    "running": frozenset({"blocked", "completed", "failed", "cancelled", "superseded"}),
    "blocked": frozenset({"running", "cancelled", "superseded"}),
    "completed": frozenset({"superseded"}),
    "failed": frozenset({"ready", "superseded", "cancelled"}),
    "superseded": frozenset(),
    "cancelled": frozenset(),
}

# Packet types that are not subject to independent (operator) verification.
NON_VERIFIED_TYPES = frozenset({
    "coordinator-route", "coordinator-join", "coordinator-reconcile",
    "director-brief", "director-cosign", "director-preflight",
    "operator-preflight", "operator-doc-sync", "receipt-only",
    "idle", "blocked",
})

_GO_RE = re.compile(r"\bGO\b")
_NITS_RE = re.compile(r"\bNITS\b")
_FAIL_RE = re.compile(r"\bFAIL\b")


def is_valid_work_transition(src: str, dst: str) -> bool:
    """True iff dst is a permitted work_state successor of src."""
    return dst in WORK_TRANSITIONS.get(src, frozenset())


def _has_evidence(packet: dict) -> bool:
    evidence = packet.get("done_evidence") or []
    return bool([item for item in evidence if str(item).strip()])


def derive_work_state(packet: dict) -> str:
    """Derive the work-lifecycle dimension from the legacy status field."""
    status = str(packet.get("status", "")).strip()
    if status == "ready":
        return "ready"
    if status == "active":
        return "running"
    if status == "done":
        return "completed"
    if status == "excepted":
        return "completed"
    if status == "blocked":
        # The overloading: completion evidence at blocked == work-complete, held.
        return "completed" if _has_evidence(packet) else "blocked"
    return "queued"


def derive_verification_state(packet: dict) -> str:
    """Derive whether the result has been independently accepted."""
    packet_type = str(packet.get("packet_type", "")).strip()
    evidence = " ".join(str(item) for item in (packet.get("done_evidence") or [])).upper()
    if packet_type == "operator-verification":
        if _FAIL_RE.search(evidence):
            return "fail"
        if _NITS_RE.search(evidence):
            return "nits"
        if _GO_RE.search(evidence):
            return "go"
        # Completed verification packet with no parseable verdict: honestly unknown.
        return "unable_to_verify" if derive_work_state(packet) == "completed" else "pending"
    if packet_type in NON_VERIFIED_TYPES:
        return "not_required"
    # Implementation-class packets are subject to independent verification.
    work = derive_work_state(packet)
    if work == "failed":
        return "fail"
    if work == "completed":
        return "pending"  # completed impl awaits the operator packet's verdict
    return "not_required"


# --- read-only --report CLI (make the overloading visible) ---------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PACKETS_GLOB = "coordination/capacity/packets/*.json"


def load_packets(root: Path, wave: int) -> list[dict]:
    """Load wave-scoped capacity packets under ``root``.

    Globs ``<root>/coordination/capacity/packets/*.json``, keeps only packets
    whose ``wave`` matches, and is tolerant of unreadable/unparseable files
    (they are skipped, never raised) — a diagnostic must never crash on a
    single bad packet.
    """
    packets: list[dict] = []
    for path in sorted(Path(root).glob(_PACKETS_GLOB)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # unreadable or unparseable — skip, stay diagnostic
        if not isinstance(data, dict):
            continue
        if data.get("wave") == wave:
            packets.append(data)
    return packets


def build_report(packets: list[dict]) -> dict:
    """Build the per-packet derived-state report.

    Each row carries the legacy ``status`` alongside the derived work and
    verification states, plus ``overloaded`` — True exactly when a packet held
    at legacy ``blocked`` has derived ``completed`` work (the ADR-017 thesis:
    work-complete but pinned at ``blocked`` for G1 coverage).
    """
    rows: list[dict] = []
    for packet in packets:
        legacy_status = str(packet.get("status", "")).strip()
        work_state = derive_work_state(packet)
        rows.append({
            "id": packet.get("id"),
            "cycle": packet.get("cycle"),
            "legacy_status": legacy_status,
            "work_state": work_state,
            "verification_state": derive_verification_state(packet),
            "overloaded": legacy_status == "blocked" and work_state == "completed",
        })
    return {"packets": rows}


def _format_table(report: dict) -> str:
    rows = report["packets"]
    headers = ("id", "cycle", "legacy_status", "work_state", "verification_state", "overloaded")
    display: list[tuple[str, ...]] = [headers]
    for row in rows:
        display.append((
            str(row.get("id", "")),
            str(row.get("cycle", "")),
            str(row.get("legacy_status", "")),
            str(row.get("work_state", "")),
            str(row.get("verification_state", "")),
            "OVERLOADED" if row.get("overloaded") else "",
        ))
    widths = [max(len(r[i]) for r in display) for i in range(len(headers))]
    lines = ["  ".join(cell.ljust(widths[i]) for i, cell in enumerate(r)).rstrip()
             for r in display]
    lines.insert(1, "  ".join("-" * widths[i] for i in range(len(headers))))
    overloaded = sum(1 for row in rows if row.get("overloaded"))
    lines.append("")
    lines.append(f"{len(rows)} packet(s); {overloaded} overloaded (blocked -> completed).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Print the read-only derived-state report. Returns 0 UNCONDITIONALLY.

    This is a diagnostic view, never a gate: it must not fail a pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Read-only report of derived packet work/verification state (ADR-017).",
    )
    parser.add_argument("--root", default=str(_REPO_ROOT),
                        help="repo root containing coordination/capacity/packets/ (default: repo root)")
    parser.add_argument("--wave", type=int, default=2,
                        help="capacity wave to report on (default: 2)")
    args = parser.parse_args(argv)

    packets = load_packets(Path(args.root), args.wave)
    report = build_report(packets)
    print(f"Packet-state report — root={args.root} wave={args.wave}")
    print(_format_table(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
