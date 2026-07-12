#!/usr/bin/env python3
"""Orthogonal packet-state derivation from legacy capacity-packet fields (ADR-017).

The capacity-packet ``status`` field overloads work-lifecycle, seat-capacity,
and verification into one string. This module DERIVES the orthogonal
``work_state`` and ``verification_state`` dimensions from the legacy
``status`` / ``packet_type`` / ``done_evidence`` / ``verify_request`` fields.
It is READ-ONLY: it writes no packet, adds no field, and changes no gate. The
gate remap (Part B) is deferred (see ADR-017).

The load-bearing insight: a packet at ``status="blocked"`` that carries
completion ``done_evidence`` is work-COMPLETE but held at ``blocked`` to
satisfy G1 coverage — ``derive_work_state`` reports it as ``completed``, making
the overloading visible.
"""
from __future__ import annotations

import re

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
