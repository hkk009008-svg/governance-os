#!/usr/bin/env python3
"""governance.route/v1 — typed route manifest: validate, hash, pair-write, read (ADR-014).

Compatibility layer only: Markdown mailbox routes remain the live authority.
This module provides the canonical typed object + generated projection so route
meaning stops depending on prose formatting. Canonical bytes come from
threeway.canon.canonicalize (RFC 8785) — library reuse; the dormant signed bus
(ADR-010) is NOT activated and refs/threeway/* is never touched.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

# Bootstrap sys.path so a bare `python scripts/route_manifest.py` imports the
# repo-root `threeway` package regardless of CWD. Mirrors scripts/ci_smoke.py.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from threeway.canon import canonicalize  # noqa: E402

SCHEMA_ID = "governance.route/v1"

KNOWN_SEATS = (
    "director",
    "director2",
    "operator",
    "operator2",
    "coordinator",
    "coordinator2",
)

# Every prohibition renders as ONE physical line starting with "no " so the
# legacy per-line negation boundary always sees negation and term together.
PROHIBITION_VOCAB = {
    "remote_ref_update": "No push or remote-ref update by any seat in this cycle.",
    "lock_action": "No lock claim and no lock release in this cycle.",
    "paid_spend": "No paid API spend in this cycle.",
    "pod_action": "No pod action and no pod spend in this cycle.",
    "production_generation": "No production generation in this cycle.",
    "target_checkout_refresh": "No target-repo checkout refresh in this cycle.",
    "cursor_consume": "No cursor consume in this cycle.",
    "route_mutation": "No route mutation by any non-coordinator seat in this cycle.",
    "canonical_database_mutation": "No canonical database mutation in this cycle.",
}

# Field order mirrors scripts/protocol_capacity.py REQUIRED_SIDE_EFFECT_TOKEN_FIELDS.
SIDE_EFFECT_TOKEN_FIELDS = (
    "side_effect_id",
    "executor",
    "target",
    "allowed_command_class",
    "preflight",
    "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck",
    "observer_seats",
    "final_closeout_owner",
    "non_goals",
)

REQUIRED_FIELDS = (
    "schema",
    "route_id",
    "task_board",
    "wave",
    "generation",
    "parent_route_id",
    "expected_control_head",
    "created_at",
    "created_by",
    "target",
    "packet_refs",
    "packet_delta",
    "capability_refs",
    "capacity_split",
    "prohibitions",
    "side_effect_token",
    "join_condition",
    "next_trigger",
)
OPTIONAL_FIELDS = ("extensions",)

_CREATED_AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_HEX_HEAD_RE = re.compile(r"^[0-9a-f]{7,40}$")
_ROUTE_ID_RE = re.compile(r"^[^/\s]+-coordinator-to-all-[^/\s]+$")
# Mirrors protocol_capacity._WEAK_TRIGGER_RE (weak triggers are not authority).
_WEAK_TRIGGER_RE = re.compile(
    r"^(?:none|n/a|not applicable|to be decided|no trigger|same as above)$",
    re.IGNORECASE,
)


class RouteManifestError(ValueError):
    """A route pair (.md + .route.json) is absent, mismatched, or invalid."""


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_route_object(obj: Any) -> list[str]:
    """Strict fail-closed validation of a route/v1 object. Empty list == valid."""
    if not isinstance(obj, dict):
        return ["route object must be a JSON object"]
    if obj.get("schema") != SCHEMA_ID:
        return [f"unsupported schema: {obj.get('schema')!r} (expected {SCHEMA_ID})"]

    issues: list[str] = []
    unknown = sorted(set(obj) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS))
    if unknown:
        issues.append("unknown authority-bearing fields rejected: " + ", ".join(unknown))
    missing = sorted(set(REQUIRED_FIELDS) - set(obj))
    if missing:
        issues.append("missing required fields: " + ", ".join(missing))
        return issues

    if not (_is_nonempty_str(obj["route_id"]) and _ROUTE_ID_RE.fullmatch(obj["route_id"])):
        issues.append("route_id must be a coordinator-to-all mailbox filename stem")
    if not _is_nonempty_str(obj["task_board"]):
        issues.append("task_board must be a non-empty string")
    if not (isinstance(obj["wave"], int) and not isinstance(obj["wave"], bool) and obj["wave"] >= 1):
        issues.append("wave must be an integer >= 1")
    generation = obj["generation"]
    if not (isinstance(generation, int) and not isinstance(generation, bool) and generation >= 1):
        issues.append("generation must be an integer >= 1")
    else:
        parent = obj["parent_route_id"]
        if generation == 1 and parent is not None:
            issues.append("parent_route_id must be null when generation == 1")
        if generation > 1 and not _is_nonempty_str(parent):
            issues.append("parent_route_id is required when generation > 1")
    head = obj["expected_control_head"]
    if head is not None and not (isinstance(head, str) and _HEX_HEAD_RE.fullmatch(head)):
        issues.append("expected_control_head must be null or 7-40 lowercase hex")
    if not (isinstance(obj["created_at"], str) and _CREATED_AT_RE.fullmatch(obj["created_at"])):
        issues.append("created_at must match YYYY-MM-DDTHH:MM:SSZ")
    if obj["created_by"] not in KNOWN_SEATS:
        issues.append("created_by must be a known seat")

    target = obj["target"]
    if target is not None:
        if not isinstance(target, dict) or set(target) != {"repository", "base_commit", "worktree"}:
            issues.append("target must be null or {repository, base_commit, worktree}")
        else:
            if not _is_nonempty_str(target["repository"]):
                issues.append("target.repository must be a non-empty string")
            if not (
                isinstance(target["base_commit"], str)
                and _HEX_HEAD_RE.fullmatch(target["base_commit"])
            ):
                issues.append("target.base_commit must be 7-40 lowercase hex")
            if target["worktree"] is not None and not _is_nonempty_str(target["worktree"]):
                issues.append("target.worktree must be null or a non-empty string")

    refs = obj["packet_refs"]
    if (
        not isinstance(refs, list)
        or not refs
        or not all(_is_nonempty_str(ref) for ref in refs)
        or len(set(refs)) != len(refs)
    ):
        issues.append("packet_refs must be a non-empty list of unique packet ids")
        refs = []
    if obj["packet_delta"] is not None:
        issues.append("packet_delta is reserved (P1.3) and must be null in v1.0")
    if obj["capability_refs"] != []:
        issues.append("capability_refs is reserved (P0.4) and must be [] in v1.0")

    split = obj["capacity_split"]
    if not isinstance(split, dict) or split.get("mode") not in ("single_pair", "dual_pair"):
        issues.append("capacity_split.mode must be single_pair or dual_pair")
    elif split["mode"] == "single_pair":
        if set(split) != {"mode"}:
            issues.append("single_pair capacity_split takes no extra keys")
    else:
        if set(split) != {"mode", "chunk_a", "chunk_b"}:
            issues.append("dual_pair capacity_split requires exactly mode, chunk_a, chunk_b")
        else:
            chunk_a, chunk_b = split["chunk_a"], split["chunk_b"]
            chunks_ok = (
                isinstance(chunk_a, list)
                and isinstance(chunk_b, list)
                and chunk_a
                and chunk_b
                and all(_is_nonempty_str(item) for item in [*chunk_a, *chunk_b])
            )
            if not chunks_ok:
                issues.append("chunk_a and chunk_b must be non-empty lists of packet ids")
            else:
                if set(chunk_a) & set(chunk_b):
                    issues.append("chunk_a and chunk_b must be disjoint")
                if not (set(chunk_a) | set(chunk_b)) <= set(refs):
                    issues.append("chunk packet ids must be members of packet_refs")

    prohibitions = obj["prohibitions"]
    if not isinstance(prohibitions, list) or len(set(map(str, prohibitions))) != len(prohibitions):
        issues.append("prohibitions must be a list of unique keys")
    else:
        bad = sorted(set(map(str, prohibitions)) - set(PROHIBITION_VOCAB))
        if bad:
            issues.append("unknown prohibition keys: " + ", ".join(bad))

    token = obj["side_effect_token"]
    if token is not None:
        if not isinstance(token, dict) or set(token) != set(SIDE_EFFECT_TOKEN_FIELDS):
            issues.append(
                "side_effect_token must carry exactly the 10 required fields"
            )
        else:
            for field in SIDE_EFFECT_TOKEN_FIELDS:
                if not _is_nonempty_str(token[field]):
                    issues.append(f"side_effect_token.{field} must be a non-empty string")
            if token.get("executor") not in KNOWN_SEATS:
                issues.append(
                    "side_effect_token.executor must be exactly one known seat"
                )

    if not _is_nonempty_str(obj["join_condition"]):
        issues.append("join_condition must be a non-empty string")
    trigger = obj["next_trigger"]
    if not _is_nonempty_str(trigger) or _WEAK_TRIGGER_RE.fullmatch(trigger.strip()):
        issues.append("next_trigger must be a non-empty, non-weak trigger")
    if "extensions" in obj and not isinstance(obj["extensions"], dict):
        issues.append("extensions must be an object")
    return issues


HASH_LINE_RE = re.compile(r"(?im)^route_hash:\s*(?P<digest>[0-9a-f]{64})\s*$")


def canonical_route_bytes(obj: dict) -> bytes:
    """RFC 8785 canonical bytes of a VALID route object (these ARE the sidecar bytes)."""
    issues = validate_route_object(obj)
    if issues:
        raise ValueError("cannot canonicalize an invalid route object: " + "; ".join(issues))
    return canonicalize(obj)


def route_hash(obj: dict) -> str:
    return hashlib.sha256(canonical_route_bytes(obj)).hexdigest()


def sidecar_path(md_path: Path) -> Path:
    return md_path.with_suffix(".route.json")


def read_manifest(md_path: Path) -> dict:
    """Load and verify the route pair. Fail-closed: any absence/mismatch raises."""
    try:
        body = md_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RouteManifestError(f"unreadable route projection: {exc}") from exc
    pins = HASH_LINE_RE.findall(body)
    if len(pins) != 1:
        raise RouteManifestError(
            f"{md_path.name}: expected exactly one route_hash pin, found {len(pins)}"
        )
    sidecar = sidecar_path(md_path)
    try:
        raw = sidecar.read_bytes()
    except OSError as exc:
        raise RouteManifestError(f"missing route sidecar {sidecar.name}: {exc}") from exc
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RouteManifestError(f"{sidecar.name}: unparseable JSON: {exc}") from exc
    issues = validate_route_object(obj)
    if issues:
        raise RouteManifestError(f"{sidecar.name}: invalid route object: " + "; ".join(issues))
    if canonicalize(obj) != raw:
        raise RouteManifestError(f"{sidecar.name}: bytes are not canonical (RFC 8785)")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != pins[0]:
        raise RouteManifestError(
            f"{md_path.name}: route_hash pin {pins[0][:12]}... does not match sidecar {digest[:12]}..."
        )
    return obj
