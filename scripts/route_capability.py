#!/usr/bin/env python3
"""governance.capability/v1 — consumable side-effect capability: validate, hash (ADR-016).

A capability is a typed, single-use grant that binds ONE side-effect authority
(the inherited 10-field side-effect token) to a specific route generation and a
subject seat, expiring on packet completion. This slice provides the canonical
typed object plus a strict fail-closed validator and its content hash; later
slices append receipts, consumption, and a CLI.

Canonical bytes come from threeway.canon.canonicalize (RFC 8785) — library reuse.
The strict validator is hand-rolled (no jsonschema dep); the sibling JSON Schema
in schemas/capability-v1.schema.json is documentation of the same contract.
"""
from __future__ import annotations

import hashlib
import re
import sys
from typing import Any
from pathlib import Path

# Bootstrap sys.path so a bare `python scripts/route_capability.py` imports the
# repo-root `threeway` package regardless of CWD. Mirrors scripts/route_manifest.py.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from threeway.canon import canonicalize  # noqa: E402

SCHEMA_ID = "governance.capability/v1"

KNOWN_SEATS = (
    "director",
    "director2",
    "operator",
    "operator2",
    "coordinator",
    "coordinator2",
)

# The 10 non-empty string fields — bound_route_id plus the 9 string members of
# the inherited side-effect token (route/v1's executor becomes the enum `subject`
# here, so it is seat-validated separately, not counted among these strings).
TOKEN_FIELDS = (
    "bound_route_id",
    "side_effect_id",
    "allowed_command_class",
    "target",
    "preflight",
    "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck",
    "observer_seats",
    "final_closeout_owner",
    "non_goals",
)

REQUIRED_FIELDS = (
    "schema",
    "capability_id",
    "issuer",
    "subject",
    "bound_route_id",
    "bound_generation",
    "side_effect_id",
    "allowed_command_class",
    "target",
    "preflight",
    "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck",
    "observer_seats",
    "final_closeout_owner",
    "non_goals",
    "expires_on",
    "state",
)
OPTIONAL_FIELDS = ("extensions",)

LIFECYCLE_STATES = ("issued", "activated", "consumed", "revoked", "expired", "failed")

_CAPABILITY_ID_RE = re.compile(r"^cap-[A-Za-z0-9._-]+$")


class CapabilityError(ValueError):
    """A capability object is malformed, unsupported, or fails validation."""


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


# Newline / carriage-return in ANY string value is the prose-injection vector
# (mirrors route_manifest): a future Markdown projection would interpolate fields
# unescaped, so a smuggled "\n" could render a second physical line a legacy
# per-line prose parser accepts as authority. Reject the whole class up front.
_CONTROL_CHARS = ("\n", "\r")


def _reject_control_chars(obj: Any, path: str = "") -> list[str]:
    """Recursively reject newline/CR in every string value (all fields, nested)."""
    issues: list[str] = []
    if isinstance(obj, str):
        if any(ch in obj for ch in _CONTROL_CHARS):
            issues.append(f"control characters rejected in {path or '<root>'}")
    elif isinstance(obj, dict):
        for key in obj:
            child = f"{path}.{key}" if path else str(key)
            issues.extend(_reject_control_chars(obj[key], child))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            issues.extend(_reject_control_chars(item, f"{path}[{index}]"))
    return issues


def validate_capability(obj: Any) -> list[str]:
    """Strict fail-closed validation of a capability/v1 object. Empty list == valid.

    Does not mutate the input.
    """
    if not isinstance(obj, dict):
        return ["capability object must be a JSON object"]
    if obj.get("schema") != SCHEMA_ID:
        return [f"unsupported schema: {obj.get('schema')!r} (expected {SCHEMA_ID})"]

    issues: list[str] = []
    issues.extend(_reject_control_chars(obj))
    unknown = sorted(set(obj) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS))
    if unknown:
        issues.append("unknown authority-bearing fields rejected: " + ", ".join(unknown))
    missing = sorted(set(REQUIRED_FIELDS) - set(obj))
    if missing:
        issues.append("missing required fields: " + ", ".join(missing))
        return issues

    cap_id = obj["capability_id"]
    if not (isinstance(cap_id, str) and _CAPABILITY_ID_RE.fullmatch(cap_id)):
        issues.append("capability_id must match ^cap-[A-Za-z0-9._-]+$")
    if obj["issuer"] not in KNOWN_SEATS:
        issues.append("issuer must be a known seat")
    if obj["subject"] not in KNOWN_SEATS:
        issues.append("subject must be a known seat")

    generation = obj["bound_generation"]
    if not (isinstance(generation, int) and not isinstance(generation, bool) and generation >= 1):
        issues.append("bound_generation must be an integer >= 1")

    for field in TOKEN_FIELDS:
        if not _is_nonempty_str(obj[field]):
            issues.append(f"{field} must be a non-empty string")

    expires = obj["expires_on"]
    if (
        not isinstance(expires, dict)
        or set(expires) != {"event", "packet_id"}
        or expires.get("event") != "packet_completed"
        or not _is_nonempty_str(expires.get("packet_id"))
    ):
        issues.append(
            "expires_on must be {event: 'packet_completed', packet_id: non-empty string}"
        )

    if obj["state"] not in LIFECYCLE_STATES:
        issues.append("state must be one of: " + ", ".join(LIFECYCLE_STATES))

    if "extensions" in obj and not isinstance(obj["extensions"], dict):
        issues.append("extensions must be an object")
    return issues


def canonical_capability_bytes(obj: dict) -> bytes:
    """RFC 8785 canonical bytes of a VALID capability object.

    Validates first and raises CapabilityError (a ValueError) if invalid, so
    invalid objects can never be hashed or persisted.
    """
    issues = validate_capability(obj)
    if issues:
        raise CapabilityError(
            "cannot canonicalize an invalid capability object: " + "; ".join(issues)
        )
    return canonicalize(obj)


def capability_hash(obj: dict) -> str:
    """SHA-256 hex digest of the canonical capability bytes (raises on invalid)."""
    return hashlib.sha256(canonical_capability_bytes(obj)).hexdigest()


# --- governance.capability-receipt/v1 (evidence-bearing, non-vacuous) --------
#
# A receipt records that a capability's single side-effect was executed. The key
# security property is NON-VACUITY: a receipt that carries only a command + its
# output is ceremony — it proves nothing durable. So the receipt MUST anchor to
# either a commit SHA or a logs/ artifact, mirroring the R-GATE-EVIDENCE shape
# enforced on GO verification-reports by scripts/check_go_schema.py
# (check_go_schema.py:49-70: a real `$ <cmd>` + `→ <output>` PLUS a commit SHA
# `[0-9a-f]{7,40}` OR a `logs/` reference). validate_receipt rejects the case
# where NEITHER commit nor logs_ref is present.

RECEIPT_SCHEMA_ID = "governance.capability-receipt/v1"

RECEIPT_REQUIRED_FIELDS = (
    "schema",
    "capability_id",
    "capability_hash",
    "result",
    "command",
    "output",
    "subject",
    "target",
)
# At least one of these must be present + well-formed (the non-vacuous evidence).
RECEIPT_EVIDENCE_FIELDS = ("commit", "logs_ref")

RECEIPT_RESULTS = ("ok", "failed")

# 64-char lowercase hex — the SHA-256 hexdigest shape produced by capability_hash.
_CAPABILITY_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
# Commit SHA: 7-40 lowercase hex (mirrors check_go_schema's _SHA_H1_RE class).
_COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
# logs/ artifact reference (mirrors check_go_schema's _LOGS_REF_RE class).
_LOGS_REF_RE = re.compile(r"^logs/\S+$")


def validate_receipt(obj: Any) -> list[str]:
    """Strict fail-closed validation of a capability-receipt/v1 object.

    Empty list == valid. Does not mutate the input. The central security check is
    the non-vacuous evidence rule: a receipt with neither a commit SHA nor a logs/
    artifact is rejected (the anti-ceremony property, mirroring check_go_schema).
    """
    if not isinstance(obj, dict):
        return ["receipt object must be a JSON object"]
    if obj.get("schema") != RECEIPT_SCHEMA_ID:
        return [f"unsupported schema: {obj.get('schema')!r} (expected {RECEIPT_SCHEMA_ID})"]

    issues: list[str] = []
    issues.extend(_reject_control_chars(obj))
    allowed = set(RECEIPT_REQUIRED_FIELDS) | set(RECEIPT_EVIDENCE_FIELDS)
    unknown = sorted(set(obj) - allowed)
    if unknown:
        issues.append("unknown authority-bearing fields rejected: " + ", ".join(unknown))
    missing = sorted(set(RECEIPT_REQUIRED_FIELDS) - set(obj))
    if missing:
        issues.append("missing required fields: " + ", ".join(missing))
        return issues

    cap_id = obj["capability_id"]
    if not (isinstance(cap_id, str) and _CAPABILITY_ID_RE.fullmatch(cap_id)):
        issues.append("capability_id must match ^cap-[A-Za-z0-9._-]+$")

    cap_hash = obj["capability_hash"]
    if not (isinstance(cap_hash, str) and _CAPABILITY_HASH_RE.fullmatch(cap_hash)):
        issues.append("capability_hash must be a 64-character lowercase hex digest")

    if obj["result"] not in RECEIPT_RESULTS:
        issues.append("result must be one of: " + ", ".join(RECEIPT_RESULTS))

    for field in ("command", "output", "subject", "target"):
        if not _is_nonempty_str(obj[field]):
            issues.append(f"{field} must be a non-empty string")

    # Non-vacuous evidence rule. Validate the shape of whichever evidence field is
    # present, then require at least one WELL-FORMED anchor (commit or logs_ref).
    commit = obj.get("commit")
    logs_ref = obj.get("logs_ref")
    has_commit = isinstance(commit, str) and bool(_COMMIT_RE.fullmatch(commit))
    has_logs = isinstance(logs_ref, str) and bool(_LOGS_REF_RE.fullmatch(logs_ref))
    if commit is not None and not has_commit:
        issues.append("commit must be a 7-40 character lowercase hex SHA")
    if logs_ref is not None and not has_logs:
        issues.append("logs_ref must match ^logs/…")
    if not (has_commit or has_logs):
        issues.append(
            "vacuous evidence rejected: at least one of commit (7-40 hex SHA) or "
            "logs_ref (logs/…) is required — a command + output alone is ceremony "
            "(mirrors check_go_schema R-GATE-EVIDENCE)"
        )
    return issues


def build_receipt(
    capability: dict,
    *,
    result: str,
    command: str,
    output: str,
    commit: str | None = None,
    logs_ref: str | None = None,
) -> dict:
    """Build a capability-receipt/v1 from a VALID capability plus real evidence.

    Validates the source capability first and raises CapabilityError (a
    ValueError) if it is invalid — a receipt can never be minted against a
    malformed grant. Binds capability_id + capability_hash from the source and
    copies subject/target. The caller supplies commit OR logs_ref (or both); the
    returned receipt is only accepted by validate_receipt when it carries at
    least one well-formed anchor. Does not mutate the input capability.
    """
    issues = validate_capability(capability)
    if issues:
        raise CapabilityError(
            "cannot build a receipt from an invalid capability: " + "; ".join(issues)
        )
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA_ID,
        "capability_id": capability["capability_id"],
        "capability_hash": capability_hash(capability),
        "result": result,
        "command": command,
        "output": output,
        "subject": capability["subject"],
        "target": capability["target"],
    }
    if commit is not None:
        receipt["commit"] = commit
    if logs_ref is not None:
        receipt["logs_ref"] = logs_ref
    return receipt
