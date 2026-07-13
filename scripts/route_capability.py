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

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from typing import Any
from pathlib import Path

# Bootstrap sys.path so a bare `python scripts/route_capability.py` imports the
# repo-root `threeway` package regardless of CWD. Mirrors scripts/route_manifest.py.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from threeway.canon import canonicalize  # noqa: E402
import route_lineage  # noqa: E402  — read-only: LineageRoute for supersession currency

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

# Only these two states are consumable. The other four are terminal / non-live:
# ``consumed`` (already spent), ``revoked`` (authority withdrawn), ``expired``
# (packet completed), ``failed`` (side effect errored). consume() refuses any
# capability whose state is not consumable BEFORE any write (fail-closed).
CONSUMABLE_STATES = frozenset({"issued", "activated"})

_CAPABILITY_ID_RE = re.compile(r"^cap-[A-Za-z0-9._-]+$")

# The capability binds exactly the git-push side effect (ADR-016), and
# _command_targets_match models git push's `<repo> <refspec>` argv. "git push" is
# therefore the ONLY supported command class: a grant naming any other verb would
# ride the push-specific target model with WRONG semantics (e.g.
# "git cherry-pick feature main" names two commits, not branch "feature/main"),
# and an embedded flag ("git push --repo=attacker") is not the literal class.
# A future non-push side effect adds its class HERE together with its own
# target-matching semantics (cross-model Codex Lane-V pass-3/4, ADR-019). Enforced
# at the grant boundary in validate_capability.
KNOWN_COMMAND_CLASSES = frozenset({"git push"})

# RFC-8785 (JCS) canonicalizes integers only within the JS safe-integer range;
# |n| > 2**53-1 raises IntegerDomainError at hash time, so reject it at validation.
_JCS_INT_MAX = 2**53 - 1


class CapabilityError(ValueError):
    """A capability object is malformed, unsupported, or fails validation."""


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_utf8_encodable(value: str) -> bool:
    """True iff ``value`` round-trips through UTF-8.

    A lone UTF-16 surrogate (e.g. ``"\\ud800"``) is a valid Python ``str`` but
    is NOT UTF-8 encodable, so it passes every ``isinstance(str)`` check and then
    detonates at ``canonicalize()`` (RFC-8785) with an uncaught exception — after
    a receipt directory may already have been created. Rejecting the whole
    non-encodable class up front keeps the validators and ``consume()`` TOTAL
    (cross-model Codex Lane-V finding, ADR-019).
    """
    try:
        value.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


# Newline / carriage-return in ANY string value is the prose-injection vector
# (mirrors route_manifest): a future Markdown projection would interpolate fields
# unescaped, so a smuggled "\n" could render a second physical line a legacy
# per-line prose parser accepts as authority. Reject the whole class up front.
_CONTROL_CHARS = ("\n", "\r")

# Shell control / chaining / substitution / redirection metacharacters. A
# capability authorizes exactly ONE simple command matching its command class —
# never a shell composition. The command-class prefix match alone
# (`cmd.startswith(allowed + " ")`) would let a COMPOUND command through:
# `git push origin main && git tag unexpected` starts with `git push ` but chains
# an UNAUTHORIZED second command. consume() rejects any evidence command carrying
# one of these operators fail-closed, so a matching prefix can no longer smuggle a
# second command via chaining (; & |), substitution (` $ ( )), or redirection
# (< >). Newline/CR are already rejected by the receipt control-char guard.
_SHELL_CONTROL_CHARS = frozenset(";&|`$<>()")


def _reject_noncanonical(obj: Any, path: str = "") -> list[str]:
    """Recursively reject values that are structurally valid Python/JSON but that
    ``canonicalize()`` (RFC-8785) cannot encode — so validation, not the later
    hash/write, is where they are refused, keeping the validators + consume() TOTAL.

    Three canonicalize-hostile classes (all found by cross-model Codex Lane-V,
    ADR-019), checked over every nested string/number:
      - newline/CR in a string (the prose-injection vector);
      - a non-UTF-8 string (a lone surrogate — valid ``str``, unencodable);
      - a non-finite float (NaN / +-Inf — ``json.loads`` accepts ``NaN`` by
        default, so a capability file can carry one; canonicalize raises
        FloatDomainError on it).
    ``bool`` is an ``int`` subclass (not ``float``), so it is untouched here.
    """
    issues: list[str] = []
    if isinstance(obj, str):
        if any(ch in obj for ch in _CONTROL_CHARS):
            issues.append(f"control characters rejected in {path or '<root>'}")
        if not _is_utf8_encodable(obj):
            issues.append(f"non-UTF-8 (lone surrogate) string rejected in {path or '<root>'}")
    elif isinstance(obj, bool):
        pass  # bool -> true/false canonicalizes fine (int-currency is checked elsewhere)
    elif isinstance(obj, int):
        if abs(obj) > _JCS_INT_MAX:
            issues.append(f"integer outside canonicalizable range rejected in {path or '<root>'}")
    elif isinstance(obj, float):
        if not math.isfinite(obj):
            issues.append(f"non-finite float (not canonicalizable) rejected in {path or '<root>'}")
    elif isinstance(obj, dict):
        for key in obj:
            child = f"{path}.{key}" if path else str(key)
            issues.extend(_reject_noncanonical(obj[key], child))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            issues.extend(_reject_noncanonical(item, f"{path}[{index}]"))
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
    issues.extend(_reject_noncanonical(obj))
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

    # allowed_command_class must be a SUPPORTED class: the target model in
    # _command_targets_match is git-push-specific, so a non-push class (or one
    # embedding a flag, e.g. "git push --repo=attacker") is refused at the grant
    # boundary rather than riding the push model with wrong semantics.
    command_class = obj["allowed_command_class"]
    if isinstance(command_class, str) and command_class not in KNOWN_COMMAND_CLASSES:
        issues.append(
            "allowed_command_class must be one of the supported side-effect classes: "
            + ", ".join(sorted(KNOWN_COMMAND_CLASSES))
        )

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
# enforced on GO verification-reports by scripts/check_go_schema.py: a real
# `$ <cmd>` + `→ <output>` plus a commit SHA or `logs/` reference.
# validate_receipt rejects the case
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


def _logs_ref_confined(logs_ref: str) -> bool:
    """True iff ``logs_ref`` lexically stays under ``logs/`` — a pure-lexical,
    NO-filesystem confinement check (mirrors scripts/route_compat.py:_confine's
    reject-absolute / reject-``..`` idiom).

    Rejects: an absolute path (leading ``/``); any ``..`` path component (even one
    that would normalize back inside, e.g. ``logs/a/../../b``); an empty component
    (``logs//x``); or a first component that is not ``logs`` (not rooted under
    ``logs/``). ``^logs/\\S+$`` alone matched ``logs/../../etc/passwd`` — this is
    the traversal escape it missed.
    """
    if logs_ref.startswith("/"):
        return False
    parts = logs_ref.split("/")
    if any(part in ("", "..") for part in parts):
        return False
    return parts[0] == "logs"


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
    issues.extend(_reject_noncanonical(obj))
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
    if commit is not None and not has_commit:
        issues.append("commit must be a 7-40 character lowercase hex SHA")
    # logs_ref: shape AND path-traversal confinement. A logs_ref that escapes
    # logs/ (absolute, a ``..`` component, an empty component, or not rooted at
    # logs/) is refused by a pure-lexical check (NO filesystem access) BEFORE it
    # can serve as a valid evidence anchor — otherwise ``logs/../../etc/passwd``
    # would ride the ``^logs/\S+$`` shape check into a valid receipt.
    has_logs = False
    if logs_ref is not None:
        if not isinstance(logs_ref, str):
            issues.append("logs_ref must match ^logs/…")
        elif not _logs_ref_confined(logs_ref):
            issues.append(f"logs_ref escapes logs/: {logs_ref!r}")
        elif not _LOGS_REF_RE.fullmatch(logs_ref):
            issues.append("logs_ref must match ^logs/…")
        else:
            has_logs = True
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


# --- atomic one-time consumption + supersession-revocation binding -----------
#
# consume() is the security-critical core: it turns a validated capability + real
# evidence into a receipt written EXACTLY ONCE per capability_id, using the
# filesystem itself as the compare-and-swap primitive (temp-file + fsync +
# atomic os.link). This is what makes replay impossible — a second consume of the
# same capability_id refuses — AND durable: the final path never appears with
# partial content, so a failed/killed write cannot brick the capability.
#
# capability_is_current() is revocation-on-supersession: a capability bound to a
# route generation that a newer generation has superseded (or to a different
# route entirely) is no longer current, independent of consumption state.


@dataclass(frozen=True)
class ConsumeResult:
    """Outcome of a consume() attempt. ``receipt_path`` is set only on success."""

    ok: bool
    reason: str
    receipt_path: str | None


def _validate_evidence(evidence: Any) -> list[str]:
    """Structural validation of a consume() evidence mapping — NEVER raises.

    Returns a list of issues (empty == structurally well-formed). This is what
    makes consume() TOTAL: an arbitrary or malformed evidence object (a non-dict,
    or a dict missing ``result``/``command``/``output`` or carrying non-string
    values) yields a typed refusal here instead of a KeyError/AttributeError
    downstream. Non-vacuity (a ``commit`` or ``logs_ref`` anchor) is enforced
    separately by validate_receipt, not here.
    """
    if not isinstance(evidence, dict):
        return [f"evidence must be a JSON object, got {type(evidence).__name__}"]
    issues: list[str] = []
    for field in ("result", "command", "output"):
        if field not in evidence:
            issues.append(f"missing required evidence field: {field}")
        elif not isinstance(evidence[field], str):
            issues.append(f"evidence field {field!r} must be a string")
        elif not _is_utf8_encodable(evidence[field]):
            issues.append(f"evidence field {field!r} must be UTF-8 encodable (no lone surrogates)")
    for field in ("commit", "logs_ref"):
        if field in evidence:
            if not isinstance(evidence[field], str):
                issues.append(f"evidence field {field!r} must be a string when present")
            elif not _is_utf8_encodable(evidence[field]):
                issues.append(f"evidence field {field!r} must be UTF-8 encodable (no lone surrogates)")
    return issues


# Argument separators in a POSIX shell command line are ASCII space and tab
# ONLY. Every other Unicode "whitespace" (NBSP U+00A0, line/para separators
# U+2028/U+2029, em space U+2003, …) is a NORMAL character to a shell: it stays
# glued to its argument token and does NOT split argv. Tokenizing on this class
# (not Python's str.split(), which splits them all) is what makes the target
# check semantically equivalent to git's own argv parsing.
_ASCII_ARG_WS_RE = re.compile(r"[ \t]+")


def _command_targets_match(command: str, allowed_command_class: str, target: str) -> bool:
    """True iff the command's git argument vector, after the verified command-class
    prefix, is EXACTLY ``<repo> <refspec>`` for the capability's ``target``.

    git parses ``git push [<repository> [<refspec>...]]``: the repository is ONE
    argv token and each refspec is ONE token. The capability's ``target`` is
    ``"<repo>/<refspec>"`` where the refspec may itself contain ``/`` (a branch
    like ``feature/main``). So the ONLY command that acts on exactly the target
    is ``<class> <repo> <refspec>`` — two whitespace-separated tokens, the
    refspec kept whole.

    Fail-closed hardening (ADR-019; closes the cross-model Codex Lane-V battery):

      (1) Tokenize on ASCII space/tab ONLY — the whitespace a shell splits argv
          on. Any other Unicode "whitespace" (NBSP, line/para separator, em
          space) is a normal character, so it stays inside its token and makes
          the token not match, rather than being silently split or stripped. The
          caller must NOT have str.strip()-ed the command with the default
          (all-whitespace) strip, or a trailing NBSP would vanish before this.
      (2) Reject flags entirely. A capability authorizes its class acting on its
          target — no options. Some are attacker-controllable
          (``--receive-pack`` / ``--exec`` run a program on the REMOTE, ``--repo``
          overrides it) and ``--force`` violates the token non_goals.
      (3) The token vector must EQUAL ``[repo, refspec]`` exactly. A missing/empty
          target, extra tokens, a different ref, the slash form
          (``git push origin/main`` is a single ``<repository>`` token to git,
          not remote+ref), and a split refspec (``git push origin feature main``
          is two refspecs, not branch ``feature/main``) all return False.
    """
    rest = command[len(allowed_command_class):]  # class prefix already verified by the command-class check
    # (1) ASCII-only tokenization: non-ASCII "whitespace" stays inside its token.
    tokens = [tok for tok in _ASCII_ARG_WS_RE.split(rest) if tok]
    # (2) no flags — a capability authorizes exactly its class acting on its target.
    if any(tok.startswith("-") for tok in tokens):
        return False
    # (3) target -> exactly (repo, refspec); the refspec keeps any internal '/'.
    repo, sep, refspec = target.partition("/")
    if not sep or not repo or not refspec:
        return False
    return tokens == [repo, refspec]


def consume(capability: dict, evidence: dict, *, store_dir, authoritative=None) -> ConsumeResult:
    """Atomically consume a capability EXACTLY ONCE, writing an evidence receipt.

    This is a filesystem compare-and-swap: the COMPLETE, fsynced receipt is
    ``os.link``-ed into ``store_dir/<capability_id>.receipt.json`` from a temp
    file, so the OS guarantees at most one successful link per ``capability_id``
    even under concurrent callers AND the canonical path never appears with
    partial content. A second consume of the same capability_id refuses with
    ``already_consumed`` — this is the replay refusal, the core security property
    of the slice.

    Durability (why link, not O_EXCL-create-then-write): if a content write fails
    (ENOSPC) or the process is killed between an O_EXCL create and its write, an
    empty/partial receipt is stranded at the final path, and a legitimate retry
    then gets ``already_consumed`` against unparseable evidence — the capability is
    permanently BRICKED. Writing to a temp file, fsyncing, then linking makes the
    final path appear ONLY with complete content; a crash before the link leaves a
    temp file a retry ignores.

    Fail-closed ordering (NOTHING is written until every check passes):
      0. Evidence totality: malformed evidence (a non-dict, or missing/non-string
         result/command/output) is refused ``malformed evidence`` up front, so
         consume() is TOTAL — it never raises on any input.
      1. ``validate_capability`` — a malformed grant is refused, no write.
      1a. Lifecycle: only an ``issued``/``activated`` capability is consumable; a
         terminal state (``consumed``/``revoked``/``expired``/``failed``) is
         refused ``not_consumable_state``, no write. (Dynamic ``expires_on``
         enforcement needs a packet-completion signal consume() lacks and is
         deferred; the terminal ``expired`` STATE is refused here.)
      2. Revocation-on-supersession (only when ``authoritative`` is supplied): the
         capability must be current against the authoritative route — a grant
         bound to a superseded generation (or a different route) is refused
         ``stale_capability``, no write. ``authoritative=None`` skips this check
         (backward-compatible: callers with no lineage context are unaffected).
      3. Command-class enforcement: the executed evidence command must be a
         SINGLE simple command (no shell control/chaining/substitution/redirection
         metacharacter — ``; & | ` $ < > ( )``) matching the capability's
         ``allowed_command_class`` — the exact literal or a ``<literal> …``
         prefix-extension. A grant for ``git push`` cannot be spent recording a
         ``git tag`` that ran, NOR a compound ``git push … && git tag …`` whose
         prefix would otherwise match; a mismatch is refused
         ``command_class_mismatch``, no write.
      3a. Target enforcement: the command's non-flag argument components must
         reference EXACTLY the capability's ``target`` — a grant for
         ``origin/main`` cannot be spent recording ``git push attacker/main``; a
         mismatch is refused ``target_mismatch``, no write.
      4. ``build_receipt`` + ``validate_receipt`` — the receipt is built FROM the
         capability (binding capability_hash by construction, never trusting a
         caller-supplied one) and its evidence is validated for non-vacuity
         (a commit SHA or logs/ anchor) and logs_ref confinement. Vacuous or
         traversing evidence is refused, no write.
      5. Only then is the receipt written to a temp file, fsynced, and atomically
         linked into place (the link is the one-time CAS).

    A consumed capability is NECESSARY-NOT-SUFFICIENT: consumption records that the
    single side effect ran, but it never substitutes for the user push gate — the
    user still authorizes the side effect itself (ADR-012). No capability state
    grants authority the principal did not.
    """
    # 0. Totality: refuse malformed evidence up front so consume() NEVER raises on
    # any input (a non-dict, or missing/non-string result/command/output). This
    # runs before every other check so the raw evidence accesses below are safe.
    evidence_issues = _validate_evidence(evidence)
    if evidence_issues:
        return ConsumeResult(
            ok=False,
            reason="malformed evidence: " + "; ".join(evidence_issues),
            receipt_path=None,
        )

    # 1. Fail-closed on a malformed capability — write nothing.
    cap_issues = validate_capability(capability)
    if cap_issues:
        return ConsumeResult(
            ok=False,
            reason="invalid capability: " + "; ".join(cap_issues),
            receipt_path=None,
        )

    # 1a. Lifecycle enforcement: only an issued/activated capability is
    # consumable. A terminal/non-live state (consumed/revoked/expired/failed) is
    # refused BEFORE any write. Dynamic ``expires_on`` enforcement additionally
    # needs a packet-completion signal consume() does not receive and is deferred;
    # the terminal ``expired`` STATE is refused here.
    state = capability["state"]
    if state not in CONSUMABLE_STATES:
        return ConsumeResult(
            ok=False,
            reason=f"not_consumable_state: {state}",
            receipt_path=None,
        )

    # 1b. Revocation-on-supersession at the enforcement point. When an
    # authoritative route is supplied, a capability bound to a superseded
    # generation (or a different route) is stale — refuse it BEFORE any write.
    # authoritative=None keeps the historical behavior (currency not enforced).
    if authoritative is not None and not capability_is_current(capability, authoritative):
        return ConsumeResult(
            ok=False,
            reason="stale_capability: bound route/generation is not the authoritative route",
            receipt_path=None,
        )

    # 1c. Command-class enforcement. The executed evidence command must match the
    # capability's allowed_command_class — the exact literal or a `<literal> …`
    # prefix-extension — so a grant for one command cannot be spent recording a
    # different command that ran. Fail-closed BEFORE any write.
    allowed = capability["allowed_command_class"].strip()
    # Strip ONLY ASCII space/tab, not the default all-whitespace strip: a bare
    # .strip() removes a trailing/leading NBSP (U+00A0.isspace() is True), so
    # `git push origin main ` would lose its NBSP before _command_targets_match
    # could reject the token differential (cross-model Codex Lane-V CHECK-1).
    cmd = str(evidence.get("command", "")).strip(" \t")
    # A capability authorizes exactly ONE simple command — never a shell
    # composition. Reject any shell control/chaining/substitution/redirection
    # metacharacter BEFORE the prefix match, so a matching prefix
    # (`git push origin main && git tag x`) cannot smuggle a chained second
    # command past the class check.
    if any(ch in _SHELL_CONTROL_CHARS for ch in cmd):
        return ConsumeResult(
            ok=False,
            reason="command_class_mismatch: evidence command contains a shell control operator",
            receipt_path=None,
        )
    if not (cmd == allowed or cmd.startswith(allowed + " ")):
        return ConsumeResult(
            ok=False,
            reason=f"command_class_mismatch: evidence command does not match allowed_command_class {allowed!r}",
            receipt_path=None,
        )

    # 1d. Target enforcement. The command class matching is NOT enough: a grant for
    # ``git push`` at target ``origin/main`` must not be spent recording
    # ``git push attacker/main``. The command's non-flag argument components must
    # reference EXACTLY the authorized target, nothing more — fail-closed BEFORE
    # any write.
    if not _command_targets_match(cmd, allowed, capability["target"]):
        return ConsumeResult(
            ok=False,
            reason=f"target_mismatch: evidence command does not act on the authorized target {capability['target']!r}",
            receipt_path=None,
        )

    # 2. Build the receipt FROM the capability (binds capability_hash by
    # construction) and validate its evidence BEFORE any write — vacuous
    # evidence is refused fail-closed, so no receipt file is ever created.
    receipt = build_receipt(
        capability,
        result=evidence["result"],
        command=evidence["command"],
        output=evidence["output"],
        commit=evidence.get("commit"),
        logs_ref=evidence.get("logs_ref"),
    )
    receipt_issues = validate_receipt(receipt)
    if receipt_issues:
        return ConsumeResult(
            ok=False,
            reason="evidence: " + "; ".join(receipt_issues),
            receipt_path=None,
        )

    # 3. Durable atomic one-time create. Write the COMPLETE receipt to a temp file,
    # fsync it to disk, THEN os.link() it into place. os.link is the compare-and-swap:
    # it raises FileExistsError iff the final path already exists, so exactly one
    # consumer wins the replay race (the O_EXCL one-time semantics are preserved) —
    # AND it guarantees the canonical path only ever appears carrying fully-written,
    # fsynced content. A crash or ENOSPC before the link strands only a temp file
    # that a retry ignores, and the finally always removes it. This is what makes a
    # failed content write NON-BRICKING: contrast a create-then-write, which leaves a
    # zero-byte/partial receipt at the final path and then refuses every legitimate
    # retry with already_consumed against unparseable evidence.
    store_path = Path(store_dir)
    store_path.mkdir(parents=True, exist_ok=True)
    path = store_path / f"{capability['capability_id']}.receipt.json"
    payload = canonicalize(receipt)
    fd, tmp = tempfile.mkstemp(
        dir=store_path, prefix=f"{capability['capability_id']}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            return ConsumeResult(ok=False, reason="already_consumed", receipt_path=None)
        return ConsumeResult(ok=True, reason="consumed", receipt_path=str(path))
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def capability_is_current(capability: dict, authoritative: "route_lineage.LineageRoute") -> bool:
    """True iff the capability is bound to the authoritative route's current tip.

    Revocation-on-supersession: a capability is current only when BOTH its
    ``bound_route_id`` equals the authoritative route's ``route_id`` AND its
    ``bound_generation`` equals that route's ``lineage.generation``. A capability
    bound to a superseded generation (a newer generation is now authoritative) or
    to a different route is stale — its authority is revoked, independent of
    whether it has been consumed.

    Defense-in-depth: a ``None`` generation on EITHER side (an invalid capability
    with ``bound_generation=None``, or a legacy no-generation route) is treated as
    NOT current, so a generationless grant can never ride a legacy route into
    "current" and inherit authority it never had.
    """
    bound_generation = capability["bound_generation"]
    route_generation = authoritative.lineage.generation
    # int-only currency: a bool generation (``True``/``False``) or a ``None``
    # generation on EITHER side is NOT current. ``type(...) is int`` (not
    # ``isinstance``) rejects bool, since ``True == 1`` — a boolean grant must
    # never ride an int-1 route into "current" and inherit authority it never had.
    if type(bound_generation) is not int or type(route_generation) is not int:
        return False
    return (
        capability["bound_route_id"] == authoritative.route_id
        and bound_generation == route_generation
    )


# --- CLI: the mechanical enforcement point (accept-a-token, refuse-replay) ----
#
# main() is the general form of the operator2 BLOCKER: "a script that accepts a
# token at execution time and refuses replay." It is a thin stdlib-only argparse
# shell over validate_capability + consume — the security logic lives in those
# functions; the CLI only maps their results to process exit codes so a shell
# caller (a git-push wrapper, a CI step) can gate a side effect on the exit code.
#
# Exit-code contract:
#   validate: 0 valid; 1 invalid / unreadable / unparseable.
#   consume:  0 first consume; 3 already_consumed (the replay refusal);
#             4 stale_capability (bound generation superseded) OR --route-root was
#               supplied but the route set has no lineage generation to check
#               currency against (fail-closed);
#             2 any other refusal (invalid capability, vacuous evidence,
#               command_class_mismatch, or an unreadable/unparseable capability
#               file).
#
# --route-root (optional): when supplied, the CLI resolves the authoritative
# route via route_lineage.resolve_authoritative and enforces currency — a stale
# capability is refused (exit 4). When omitted, currency is NOT enforced.


def _load_capability_json(path: str) -> tuple[Any, str | None]:
    """Read and JSON-parse the file at ``path``.

    Returns ``(obj, None)`` on success or ``(None, message)`` if the file cannot
    be read or parsed — the CLI turns a message into a fail-closed exit code
    rather than raising, so a malformed file is refused, never trusted.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except OSError as exc:
        return None, f"cannot read capability file {path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"cannot parse capability file {path}: {exc}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and consume governance.capability/v1 tokens (ADR-016).",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_validate = sub.add_parser(
        "validate", help="strict fail-closed validation of a capability/v1 JSON file"
    )
    p_validate.add_argument(
        "--capability", required=True, help="path to a capability/v1 JSON file"
    )

    p_consume = sub.add_parser(
        "consume",
        help="consume a capability EXACTLY ONCE, writing an evidence receipt (refuses replay)",
    )
    p_consume.add_argument("--capability", required=True, help="path to a capability/v1 JSON file")
    p_consume.add_argument("--store", required=True, help="receipt store directory")
    p_consume.add_argument("--result", required=True, choices=("ok", "failed"))
    p_consume.add_argument("--command", required=True, help="the side-effect command that ran")
    p_consume.add_argument("--output", required=True, help="the command's output")
    p_consume.add_argument("--commit", default=None, help="commit SHA anchoring the evidence (7-40 hex)")
    p_consume.add_argument(
        "--logs-ref", default=None, dest="logs_ref", help="logs/ artifact anchoring the evidence"
    )
    p_consume.add_argument(
        "--route-root",
        default=None,
        dest="route_root",
        help="repo root whose coordinator routes establish the authoritative "
        "lineage; when given, currency is enforced (a stale capability -> exit 4)",
    )

    args = parser.parse_args(argv)

    capability, load_error = _load_capability_json(args.capability)
    if load_error is not None:
        print(load_error)
        # validate treats an unreadable file as invalid (1); consume as a refusal (2).
        return 1 if args.subcommand == "validate" else 2

    if args.subcommand == "validate":
        issues = validate_capability(capability)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print(f"capability valid: {capability['capability_id']}")
        return 0

    # consume: build the evidence dict from the args, then let consume() enforce
    # fail-closed validation + one-time atomic write. Only anchors the caller
    # actually supplied are included (an absent commit/logs_ref stays absent, so
    # consume()'s non-vacuity check refuses genuinely vacuous evidence).
    evidence: dict[str, Any] = {
        "result": args.result,
        "command": args.command,
        "output": args.output,
    }
    if args.commit is not None:
        evidence["commit"] = args.commit
    if args.logs_ref is not None:
        evidence["logs_ref"] = args.logs_ref

    # Optional currency enforcement. --route-root resolves the authoritative
    # route so consume() can refuse a superseded (stale) capability. If the route
    # set has no lineage generation (legacy/empty, or a tip-less cycle), there is
    # nothing to establish supersession against — the user asked for a currency
    # check that cannot be performed, so fail closed with exit 4.
    authoritative = None
    if args.route_root is not None:
        routes = route_lineage.load_routes(Path(args.route_root))
        res = route_lineage.resolve_authoritative(routes)
        if res.mode == "lineage" and res.winner:
            authoritative = next((r for r in routes if r.route_id == res.winner), None)
        else:
            print(
                "no authoritative lineage generation to check currency against "
                f"(route resolution mode={res.mode}); refusing (fail-closed)"
            )
            return 4

    result = consume(capability, evidence, store_dir=Path(args.store), authoritative=authoritative)
    if result.ok:
        print(f"consumed: {result.receipt_path}")
        return 0
    # Map the refusal reason (by prefix) to the process exit code.
    print(result.reason)
    if result.reason.startswith("already_consumed"):
        return 3
    if result.reason.startswith("stale_capability"):
        return 4
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
