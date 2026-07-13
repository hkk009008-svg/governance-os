#!/usr/bin/env python3
"""Strict public structure checks for Lane V verification reports."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

import opus_review_receipts as receipts


REPORT_SCHEMA_VERSION = "lane-v-report/v2"
LEGACY_MANIFEST_SCHEMA_VERSION = "lane-v-report-v1-baseline/v1"
ATTESTATION_MAX_BYTES = 65_536
ATTESTATION_LINE_MAX_BYTES = 49_152

ATTESTATION_FIELDS = (
    "Verification schema",
    "Verification mode",
    "Verification harness",
    "Verification task ID",
    "Scope authority",
    "Trigger identity",
    "Reviewed head",
    "Reviewed base",
    "Review profile",
    "Authorization identity",
    "Opus receipt ID",
    "Opus scope digest",
    "Cross-model review",
    "Effective Opus model",
    "Opus finding dispositions",
    "Reconciliation guard",
    "Degraded reason",
)

_REPORT_BASENAME_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>operator2?)-to-(?P<recipient>[a-z][a-z0-9]*)-"
    r"verification-report\.md$"
)
_LEGACY_REPORT_BASENAME_RE = re.compile(r"^.+-verification-report\.md$")
_VERIFY_REQUEST_BASENAME_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>[a-z][a-z0-9]*)-to-"
    r"(?P<recipient>operator2?)-verify-request\.md$"
)
_ENVELOPE_RE = re.compile(
    r"\*\*When:\*\* (?P<when>[^ ]+) · \*\*From:\*\* "
    r"(?P<sender>[a-z][a-z0-9]*) \(online\)"
)
_H1_RE = re.compile(
    r"# (?P<sender>Operator2?) → (?P<recipient>[A-Z][A-Za-z0-9]*): "
    r".+ commit `(?P<head>[0-9a-f]{40})`"
)
_VERDICT_RE = re.compile(r"VERDICT: (?P<verdict>GO|NITS|FAIL)")
_VERDICT_CANDIDATE_RE = re.compile(
    r"^[ \t]*(?:(?:>[ \t]*)+|(?:#{1,6}|[-+*]|\d+[.)])[ \t]+)*"
    r"(?:[`*_~]{1,3}[ \t]*)*VERDICT:"
)
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_RAW_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_RECEIPT_ID_RE = re.compile(r"^opr1:[0-9a-f]{64}$")
_AUTHORIZATION_RE = re.compile(
    r"^(?:user-task|verify-request):[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$"
)
_FINDING_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_EXACT_H2_RE = re.compile(r"## [^#\s].*")
_SHIPPING_SUBJECT_RE = re.compile(
    r"^(?:feat|fix|refactor)(?:\([^\n()]+\))?!?: .+"
)
_CODEX_UNAVAILABLE_REASONS = frozenset(
    {
        "authorization_missing",
        "claude_not_found",
        "authentication_failed",
        "timeout",
        "process_failed",
        "invalid_json",
        "invalid_schema",
        "reviewed_scope_mismatch",
        "effective_model_missing",
        "effective_model_not_opus",
        "sandbox_unavailable",
        "output_limit",
        "attempt_state_uncertain",
    }
)
_OPUS_SPECIFIC_FIELDS = ATTESTATION_FIELDS[8:]


class ReportGateError(ValueError):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class LaneVReport:
    relative_path: str
    sender: str
    verdict: str
    h1_head: str
    fields: Mapping[str, str]
    body_digest: str


@dataclass(frozen=True)
class StructuralAuthority:
    descriptor: receipts.ScopeDescriptor
    reference: receipts.ScopeReference
    trigger_kind: str
    trigger_commit: str
    trigger_path: str | None
    trigger_identity: str
    verify_request_recipient: str | None


def _fail(reason: str, detail: str) -> None:
    raise ReportGateError(reason, detail)


def _strict_json_value(value: str, label: str) -> Any:
    try:
        parsed = receipts.strict_json_loads(value.encode("utf-8"))
        rendered = receipts.canonical_json_bytes(parsed).decode("utf-8")
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_attestation_value", f"{label}: {exc}") from exc
    if rendered != value:
        _fail("noncanonical_attestation_json", label)
    return parsed


def _canonical_uuid(value: str) -> str:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ReportGateError(
            "invalid_attestation_value", "Verification task ID must be canonical UUID text"
        ) from exc
    if str(parsed) != value:
        _fail(
            "invalid_attestation_value",
            "Verification task ID must be canonical UUID text",
        )
    return value


def _full_sha(value: str, label: str, *, allow_none: bool = False) -> str:
    if allow_none and value == "none":
        return value
    if _FULL_SHA_RE.fullmatch(value) is None:
        _fail("invalid_attestation_value", f"{label} must be a lowercase full SHA")
    return value


def _sha256(value: str, label: str) -> str:
    if _SHA256_RE.fullmatch(value) is None:
        _fail("invalid_attestation_value", f"{label} must be a canonical SHA-256")
    return value


def _validate_trigger_identity(value: str) -> None:
    try:
        if value.startswith("shipping-commit:"):
            commit = value.removeprefix("shipping-commit:")
            canonical = receipts.canonical_trigger_identity("shipping-commit", commit)
        elif value.startswith("verify-request:"):
            remainder = value.removeprefix("verify-request:")
            commit, separator, path = remainder.partition(":")
            if not separator:
                _fail("invalid_attestation_value", "Trigger identity is incomplete")
            canonical = receipts.canonical_trigger_identity(
                "verify-request", commit, path
            )
        else:
            _fail("invalid_attestation_value", "unsupported Trigger identity")
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_attestation_value", str(exc)) from exc
    if canonical != value:
        _fail("invalid_attestation_value", "Trigger identity is not canonical")


def _trigger_parts(value: str) -> tuple[str, str, str | None]:
    if value.startswith("shipping-commit:"):
        return "shipping-commit", value.removeprefix("shipping-commit:"), None
    if value.startswith("verify-request:"):
        remainder = value.removeprefix("verify-request:")
        commit, separator, path = remainder.partition(":")
        if separator:
            return "verify-request", commit, path
    _fail("invalid_trigger_identity", "report trigger identity is malformed")


def _validate_dispositions(value: str, status: str) -> None:
    if value == "none":
        if status == "issues":
            _fail(
                "invalid_attestation_value",
                "issues requires Opus finding dispositions",
            )
        return
    if status != "issues":
        _fail(
            "invalid_attestation_value",
            "only issues may carry Opus finding dispositions",
        )
    parsed = _strict_json_value(value, "Opus finding dispositions")
    if not isinstance(parsed, Mapping) or not parsed:
        _fail(
            "invalid_attestation_value",
            "Opus finding dispositions must be a non-empty object",
        )
    for finding_id, disposition in parsed.items():
        if not isinstance(finding_id, str) or _FINDING_ID_RE.fullmatch(finding_id) is None:
            _fail("invalid_attestation_value", "invalid Opus finding ID")
        if not isinstance(disposition, Mapping) or set(disposition) != {
            "disposition",
            "evidence",
            "evidence_digest",
        }:
            _fail(
                "invalid_attestation_value",
                f"{finding_id} disposition fields are invalid",
            )
        disposition_value = disposition["disposition"]
        evidence = disposition["evidence"]
        evidence_digest = disposition["evidence_digest"]
        if disposition_value not in {"confirmed", "disproved", "unresolved"}:
            _fail("invalid_attestation_value", f"{finding_id} disposition is invalid")
        if not isinstance(evidence, str) or not isinstance(evidence_digest, str):
            _fail(
                "invalid_attestation_value",
                f"{finding_id} evidence values must be strings",
            )
        expected_digest = (
            "none"
            if not evidence
            else "sha256:" + hashlib.sha256(evidence.encode("utf-8")).hexdigest()
        )
        if evidence_digest != expected_digest:
            _fail(
                "invalid_attestation_value",
                f"{finding_id} evidence digest does not match",
            )


def _validate_guard(value: str) -> None:
    parsed = _strict_json_value(value, "Reconciliation guard")
    if (
        not isinstance(parsed, Mapping)
        or list(parsed) != ["digest", "go_allowed"]
        or not isinstance(parsed.get("go_allowed"), bool)
        or not isinstance(parsed.get("digest"), str)
    ):
        _fail(
            "invalid_attestation_value",
            "Reconciliation guard fields must be digest then go_allowed",
        )
    _sha256(parsed["digest"], "Reconciliation guard digest")


def _validate_codex_fields(fields: Mapping[str, str]) -> None:
    if fields["Verification harness"] != receipts.CODEX_HARNESS:
        _fail("invalid_attestation_value", "Codex verification harness does not match")
    if fields["Review profile"] != receipts.CODEX_MODE:
        _fail("invalid_attestation_value", "Codex review profile does not match")
    authorization = fields["Authorization identity"]
    if authorization not in {
        "standing-policy:codex-lane-v-opus-v1",
        "missing",
    } and _AUTHORIZATION_RE.fullmatch(authorization) is None:
        _fail("invalid_attestation_value", "invalid Authorization identity")
    if _RECEIPT_ID_RE.fullmatch(fields["Opus receipt ID"]) is None:
        _fail("invalid_attestation_value", "invalid Opus receipt ID")
    _sha256(fields["Opus scope digest"], "Opus scope digest")
    status = fields["Cross-model review"]
    if status not in {"pass", "issues", "unavailable"}:
        _fail("invalid_attestation_value", "invalid Cross-model review status")
    model = fields["Effective Opus model"]
    reason = fields["Degraded reason"]
    if status == "unavailable":
        if model != "not-available" or reason not in _CODEX_UNAVAILABLE_REASONS:
            _fail(
                "invalid_attestation_value",
                "unavailable requires not-available model and exact degraded reason",
            )
        if (reason == "authorization_missing") != (authorization == "missing"):
            _fail(
                "invalid_attestation_value",
                "authorization_missing and missing identity must agree",
            )
    else:
        if not (model == "opus" or model.startswith("claude-opus-")) or reason != "none":
            _fail(
                "invalid_attestation_value",
                "pass/issues requires verified Opus model and no degraded reason",
            )
        if authorization == "missing":
            _fail("invalid_attestation_value", "successful review cannot lack authorization")
    _validate_dispositions(fields["Opus finding dispositions"], status)
    _validate_guard(fields["Reconciliation guard"])


def _validate_fields(fields: Mapping[str, str]) -> None:
    if fields["Verification schema"] != REPORT_SCHEMA_VERSION:
        _fail("invalid_attestation_value", "unexpected Verification schema")
    mode = fields["Verification mode"]
    if mode not in {receipts.CODEX_MODE, receipts.CLAUDE_MODE}:
        _fail("invalid_attestation_value", "unsupported Verification mode")
    _canonical_uuid(fields["Verification task ID"])
    try:
        receipts.parse_scope_reference(fields["Scope authority"])
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_attestation_value", str(exc)) from exc
    _validate_trigger_identity(fields["Trigger identity"])
    _full_sha(fields["Reviewed head"], "Reviewed head")
    _full_sha(fields["Reviewed base"], "Reviewed base", allow_none=True)
    if mode == receipts.CODEX_MODE:
        _validate_codex_fields(fields)
        return
    if fields["Verification harness"] != receipts.CLAUDE_HARNESS:
        _fail("invalid_attestation_value", "Claude verification harness does not match")
    for label in _OPUS_SPECIFIC_FIELDS:
        if fields[label] != "not-applicable":
            _fail("invalid_attestation_value", f"{label} must be not-applicable")


def parse_lane_v_report(
    relative_path: str, raw: bytes, *, decoded_text: str | None = None
) -> LaneVReport:
    """Parse one report from strict raw bytes without consulting private state."""

    try:
        normalized_path = receipts.normalize_repo_path(relative_path)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_report_path", exc.detail) from exc
    pure_path = PurePosixPath(normalized_path)
    if pure_path.parent.as_posix() != "coordination/mailbox/sent":
        _fail("invalid_report_path", "verification report must be a sent mailbox event")
    basename = pure_path.name
    filename = _REPORT_BASENAME_RE.fullmatch(basename)
    if filename is None:
        _fail("invalid_report_path", "verification-report filename is not canonical")
    if not isinstance(raw, bytes):
        _fail("invalid_report_encoding", "report body must be raw bytes")
    if b"\r" in raw or b"\x00" in raw:
        _fail("invalid_report_encoding", "carriage return and NUL are forbidden")
    if decoded_text is None:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ReportGateError(
                "invalid_report_encoding", "report must be UTF-8"
            ) from exc
    else:
        if not isinstance(decoded_text, str):
            _fail("invalid_report_encoding", "decoded report must be text")
        try:
            matches_raw = decoded_text.encode("utf-8") == raw
        except UnicodeEncodeError as exc:
            raise ReportGateError(
                "invalid_report_encoding", "decoded report must be UTF-8"
            ) from exc
        if not matches_raw:
            _fail("invalid_report_encoding", "decoded report does not match raw bytes")
        text = decoded_text

    raw_lines = raw.split(b"\n")
    lines = text.split("\n")
    envelope_lines = [line for line in lines if line.startswith("**When:**")]
    if len(envelope_lines) != 1:
        _fail("invalid_report_envelope", "report requires one envelope")
    envelope = _ENVELOPE_RE.fullmatch(envelope_lines[0])
    if envelope is None:
        _fail("invalid_report_envelope", "report envelope is malformed")
    timestamp = filename.group("timestamp")
    expected_when = timestamp[:11] + timestamp[11:-1].replace("-", ":") + "Z"
    sender = filename.group("sender")
    recipient = filename.group("recipient")
    if envelope.group("when") != expected_when or envelope.group("sender") != sender:
        _fail("invalid_report_envelope", "filename and envelope do not agree")

    h1_lines = [line for line in lines if line.startswith("# ")]
    if len(h1_lines) != 1:
        _fail("invalid_report_h1", "report requires one H1")
    h1 = _H1_RE.fullmatch(h1_lines[0])
    if h1 is None:
        _fail("invalid_report_h1", "report H1 identity and full SHA are not canonical")
    if h1.group("sender").lower() != sender or h1.group("recipient").lower() != recipient:
        _fail("invalid_report_h1", "filename and H1 sender/recipient do not agree")

    verdict_lines = [line for line in lines if _VERDICT_CANDIDATE_RE.match(line)]
    if len(verdict_lines) != 1:
        _fail("invalid_report_verdict", "report requires exactly one verdict line")
    verdict_match = _VERDICT_RE.fullmatch(verdict_lines[0])
    if verdict_match is None:
        _fail("invalid_report_verdict", "report verdict line is not canonical")

    heading = "## Verification Attestation"
    heading_indexes = [index for index, line in enumerate(lines) if line == heading]
    if len(heading_indexes) != 1:
        _fail("invalid_attestation_section", "report requires exactly one attestation")
    heading_index = heading_indexes[0]
    field_start = heading_index + 2
    field_end = field_start + len(ATTESTATION_FIELDS)
    if heading_index + 1 >= len(lines) or lines[heading_index + 1] != "":
        _fail("invalid_attestation_section", "attestation requires one framing blank")
    if field_end > len(lines):
        _fail("invalid_attestation_section", "attestation fields are incomplete")

    measured_lines = raw_lines[heading_index:field_end]
    if any(len(line) > ATTESTATION_LINE_MAX_BYTES for line in measured_lines):
        _fail("attestation_line_too_large", "attestation line exceeds byte limit")
    section_span = b"\n".join(measured_lines)
    if len(section_span) > ATTESTATION_MAX_BYTES:
        _fail("attestation_too_large", "attestation section exceeds byte limit")

    parsed_fields: dict[str, str] = {}
    for expected, line in zip(ATTESTATION_FIELDS, lines[field_start:field_end]):
        prefix = f"{expected}: "
        if not line.startswith(prefix) or line == prefix:
            _fail(
                "invalid_attestation_field",
                f"expected consecutive field {expected!r}",
            )
        parsed_fields[expected] = line[len(prefix) :]

    remaining = lines[field_end:]
    if remaining == [""]:
        remaining = []
    if remaining:
        if (
            len(remaining) < 2
            or remaining[0] != ""
            or _EXACT_H2_RE.fullmatch(remaining[1]) is None
        ):
            _fail(
                "invalid_attestation_termination",
                "attestation must end at EOF or before one exact H2",
            )

    _validate_fields(parsed_fields)
    h1_head = h1.group("head")
    if h1_head != parsed_fields["Reviewed head"]:
        _fail("reviewed_head_mismatch", "H1 SHA does not equal Reviewed head")
    return LaneVReport(
        relative_path=normalized_path,
        sender=sender,
        verdict=verdict_match.group("verdict"),
        h1_head=h1_head,
        fields=MappingProxyType(parsed_fields),
        body_digest="sha256:" + hashlib.sha256(raw).hexdigest(),
    )


def _git_process(
    root: Path, *args: str, text: bool = True
) -> subprocess.CompletedProcess[Any]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    try:
        return subprocess.run(
            ["git", "--no-replace-objects", *args],
            cwd=root,
            env=environment,
            capture_output=True,
            text=text,
            check=False,
        )
    except OSError as exc:
        raise ReportGateError("git_unavailable", str(exc)) from exc


def _require_repository(root: Path) -> Path:
    resolved = root.resolve()
    result = _git_process(resolved, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        _fail("invalid_repository", "root is not a Git worktree")
    try:
        top = Path(result.stdout.strip()).resolve()
    except (AttributeError, OSError) as exc:
        raise ReportGateError("invalid_repository", "could not resolve root") from exc
    if top != resolved:
        _fail("invalid_repository", "root must be the Git worktree root")
    return resolved


def _require_commit(root: Path, commit: str, label: str) -> None:
    result = _git_process(root, "cat-file", "-e", f"{commit}^{{commit}}")
    if result.returncode != 0:
        _fail("invalid_structural_authority", f"{label} is not a committed object")


def _require_strict_ancestor(root: Path, base: str, head: str, label: str) -> None:
    if base == head:
        _fail("invalid_structural_authority", f"{label} must be a strict ancestor")
    result = _git_process(root, "merge-base", "--is-ancestor", base, head)
    if result.returncode != 0:
        _fail("invalid_structural_authority", f"{label} must be an ancestor")


def _committed_blob(
    root: Path, commit: str, path: str, label: str, *, maximum_bytes: int = 65_536
) -> bytes:
    try:
        normalized = receipts.normalize_repo_path(path)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_structural_authority", exc.detail) from exc
    result = _git_process(root, "show", f"{commit}:{normalized}", text=False)
    if result.returncode != 0 or not isinstance(result.stdout, bytes):
        _fail(
            "invalid_structural_authority",
            f"committed {label} is missing at {commit}:{normalized}",
        )
    if len(result.stdout) > maximum_bytes:
        _fail(
            "authority_blob_too_large",
            f"committed {label} exceeds {maximum_bytes} bytes",
        )
    return result.stdout


def _one_prefixed_value(lines: list[str], prefix: str, label: str) -> str:
    values = [line[len(prefix) :] for line in lines if line.startswith(prefix)]
    if len(values) != 1 or not values[0]:
        _fail(
            "invalid_verify_request",
            f"committed verify-request requires one exact {label}",
        )
    return values[0]


def _verify_request_scope(
    root: Path,
    report: LaneVReport,
    trigger_commit: str,
    trigger_path: str,
) -> tuple[receipts.ScopeReference, str]:
    pure_path = PurePosixPath(trigger_path)
    if pure_path.parent.as_posix() != "coordination/mailbox/sent":
        _fail(
            "invalid_verify_request",
            "verify-request must be a sent mailbox event",
        )
    filename = _VERIFY_REQUEST_BASENAME_RE.fullmatch(pure_path.name)
    if filename is None:
        _fail("invalid_verify_request", "verify-request filename is not canonical")
    raw = _committed_blob(
        root, trigger_commit, trigger_path, "verify-request"
    )
    if b"\r" in raw or b"\x00" in raw:
        _fail("invalid_verify_request", "verify-request contains forbidden bytes")
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReportGateError(
            "invalid_verify_request", "verify-request must be UTF-8"
        ) from exc
    lines = body.split("\n")
    h1_lines = [line for line in lines if line.startswith("# ")]
    if len(h1_lines) != 1:
        _fail("invalid_verify_request", "verify-request requires one H1")
    h1 = re.fullmatch(
        r"# ([A-Za-z][A-Za-z0-9]*) → ([A-Za-z][A-Za-z0-9]*): .+",
        h1_lines[0],
    )
    envelope_lines = [line for line in lines if line.startswith("**When:**")]
    if h1 is None or len(envelope_lines) != 1:
        _fail("invalid_verify_request", "verify-request envelope is malformed")
    envelope = _ENVELOPE_RE.fullmatch(envelope_lines[0])
    if envelope is None:
        _fail("invalid_verify_request", "verify-request envelope is malformed")
    timestamp = filename.group("timestamp")
    expected_when = timestamp[:11] + timestamp[11:-1].replace("-", ":") + "Z"
    sender = filename.group("sender")
    recipient = filename.group("recipient")
    if (
        envelope.group("when") != expected_when
        or envelope.group("sender") != sender
        or h1.group(1).lower() != sender
        or h1.group(2).lower() != recipient
    ):
        _fail(
            "invalid_verify_request",
            "verify-request filename, H1, and envelope do not agree",
        )
    if _one_prefixed_value(lines, "Event type: ", "Event type") != "verify-request":
        _fail("invalid_verify_request", "event type must be verify-request")
    if _one_prefixed_value(lines, "Reviewed head: ", "Reviewed head") != report.fields[
        "Reviewed head"
    ]:
        _fail("invalid_verify_request", "Reviewed head does not agree")
    if _one_prefixed_value(lines, "Reviewed base: ", "Reviewed base") != report.fields[
        "Reviewed base"
    ]:
        _fail("invalid_verify_request", "Reviewed base does not agree")
    scope_text = _one_prefixed_value(lines, "Lane-V-Scope: ", "Lane-V-Scope")
    if scope_text != report.fields["Scope authority"]:
        _fail("invalid_verify_request", "Scope authority does not agree")
    if report.sender != recipient:
        _fail(
            "invalid_verify_request",
            "verify-request recipient must equal report sender",
        )
    try:
        return receipts.parse_scope_reference(scope_text), recipient
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_verify_request", exc.detail) from exc


def _terminal_git_trailers(message: str) -> tuple[str, ...]:
    lines = message.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    separator = next(
        (
            index
            for index in range(len(lines) - 1, -1, -1)
            if not lines[index].strip()
        ),
        None,
    )
    if separator is None:
        return ()
    block = tuple(lines[separator + 1 :])
    if not block or any(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*: .+", line) is None
        for line in block
    ):
        return ()
    return block


def _shipping_scope(
    root: Path, report: LaneVReport, trigger_commit: str
) -> receipts.ScopeReference:
    if trigger_commit != report.fields["Reviewed head"]:
        _fail(
            "invalid_shipping_trigger",
            "shipping trigger must equal Reviewed head",
        )
    result = _git_process(root, "show", "-s", "--format=%B", trigger_commit, text=False)
    if result.returncode != 0 or not isinstance(result.stdout, bytes):
        _fail("invalid_shipping_trigger", "could not read shipping commit")
    if len(result.stdout) > 65_536:
        _fail("authority_blob_too_large", "shipping commit message exceeds 65536 bytes")
    try:
        message = result.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReportGateError(
            "invalid_shipping_trigger", "shipping message must be UTF-8"
        ) from exc
    lines = message.splitlines()
    if not lines or _SHIPPING_SUBJECT_RE.fullmatch(lines[0]) is None:
        _fail(
            "invalid_shipping_trigger",
            "shipping subject must be feat, fix, or refactor",
        )
    references = [
        line.removeprefix("Lane-V-Scope: ")
        for line in _terminal_git_trailers(message)
        if line.startswith("Lane-V-Scope: ")
    ]
    if references != [report.fields["Scope authority"]]:
        _fail(
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        )
    try:
        return receipts.parse_scope_reference(references[0])
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_shipping_trigger", exc.detail) from exc


def validate_structural_authority(
    repo_root: Path, report: LaneVReport
) -> StructuralAuthority:
    """Bind report structure to committed provider-neutral scope authority."""

    if not isinstance(report, LaneVReport):
        _fail("invalid_structural_authority", "report must be a LaneVReport")
    root = _require_repository(repo_root)
    trigger_kind, trigger_commit, trigger_path = _trigger_parts(
        report.fields["Trigger identity"]
    )
    _require_commit(root, trigger_commit, "trigger commit")
    head = report.fields["Reviewed head"]
    base = report.fields["Reviewed base"]
    if base == "none":
        _fail(
            "invalid_structural_authority",
            "committed scope authority requires an exact Reviewed base",
        )
    _require_commit(root, head, "Reviewed head")
    _require_commit(root, base, "Reviewed base")
    _require_strict_ancestor(root, base, head, "Reviewed base")
    if trigger_kind == "shipping-commit":
        reference = _shipping_scope(root, report, trigger_commit)
        recipient = None
    else:
        assert trigger_path is not None
        _require_strict_ancestor(
            root, head, trigger_commit, "verify-request trigger commit"
        )
        reference, recipient = _verify_request_scope(
            root, report, trigger_commit, trigger_path
        )
    raw = _committed_blob(
        root,
        trigger_commit,
        reference.descriptor_path,
        "scope descriptor",
    )
    actual_digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    if actual_digest != reference.descriptor_digest:
        _fail(
            "scope_digest_mismatch",
            "committed descriptor digest does not agree",
        )
    try:
        mapping = receipts.strict_json_loads(raw)
        if not isinstance(mapping, Mapping):
            _fail("invalid_scope_descriptor", "descriptor must be an object")
        descriptor = receipts.ScopeDescriptor.from_mapping(mapping)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError(exc.reason, exc.detail) from exc
    expected_path = f"coordination/verification/scopes/{descriptor.task_id}.json"
    if reference.descriptor_path != expected_path:
        _fail("invalid_scope_descriptor", "descriptor path must equal its task ID")
    comparisons = {
        "trigger kind": (descriptor.trigger_kind, trigger_kind),
        "verification mode": (
            descriptor.verification_mode,
            report.fields["Verification mode"],
        ),
        "verification harness": (
            descriptor.verification_harness,
            report.fields["Verification harness"],
        ),
        "verification task ID": (
            descriptor.task_id,
            report.fields["Verification task ID"],
        ),
        "reviewed base": (descriptor.base_commit, base),
    }
    for label, (committed, claimed) in comparisons.items():
        if committed != claimed:
            _fail(
                "structural_authority_mismatch",
                f"committed {label} does not equal report field",
            )
    if report.fields["Scope authority"] != (
        f"{reference.descriptor_path}@{reference.descriptor_digest}"
    ):
        _fail(
            "structural_authority_mismatch",
            "Scope authority is not canonical",
        )
    expected_trigger = receipts.canonical_trigger_identity(
        trigger_kind, trigger_commit, trigger_path
    )
    if report.fields["Trigger identity"] != expected_trigger:
        _fail(
            "structural_authority_mismatch",
            "Trigger identity does not equal committed trigger",
        )
    return StructuralAuthority(
        descriptor=descriptor,
        reference=reference,
        trigger_kind=trigger_kind,
        trigger_commit=trigger_commit,
        trigger_path=trigger_path,
        trigger_identity=expected_trigger,
        verify_request_recipient=recipient,
    )


def legacy_manifest_violations(
    manifest: object, report_paths: list[str] | tuple[str, ...]
) -> list[str]:
    """Validate the exact legacy manifest and report any missing history."""

    violations: list[str] = []
    if not isinstance(manifest, Mapping) or set(manifest) != {
        "schema_version",
        "reports",
    }:
        return ["legacy manifest: expected exact schema_version/reports fields"]
    if manifest["schema_version"] != LEGACY_MANIFEST_SCHEMA_VERSION:
        violations.append("legacy manifest: unexpected schema_version")
    reports = manifest["reports"]
    if not isinstance(reports, list):
        violations.append("legacy manifest: reports must be a list")
        return violations
    paths: list[str] = []
    digests: list[str] = []
    for index, entry in enumerate(reports):
        label = f"legacy manifest reports[{index}]"
        if not isinstance(entry, Mapping) or set(entry) != {"path", "sha256"}:
            violations.append(f"{label}: expected exact path/sha256 fields")
            continue
        path = entry["path"]
        digest = entry["sha256"]
        if not isinstance(path, str):
            violations.append(f"{label}: path must be a string")
        else:
            try:
                normalized = receipts.normalize_repo_path(path)
            except receipts.ReceiptContractError:
                violations.append(f"{label}: path is not canonical")
            else:
                pure_path = PurePosixPath(normalized)
                if (
                    pure_path.parent.as_posix() != "coordination/mailbox/sent"
                    or _LEGACY_REPORT_BASENAME_RE.fullmatch(pure_path.name) is None
                ):
                    violations.append(
                        f"{label}: path is not a canonical verification report"
                    )
                paths.append(normalized)
        if not isinstance(digest, str) or _RAW_SHA256_RE.fullmatch(digest) is None:
            violations.append(f"{label}: sha256 must be 64 lowercase hex")
        else:
            digests.append(digest)
    if len(set(paths)) != len(paths):
        violations.append("legacy manifest: duplicate report path")
    if len(set(digests)) != len(digests):
        violations.append("legacy manifest: duplicate report digest")
    if paths != sorted(paths):
        violations.append("legacy manifest: reports must be sorted by path")
    if violations:
        return violations
    try:
        current_paths = {receipts.normalize_repo_path(path) for path in report_paths}
    except receipts.ReceiptContractError as exc:
        return [f"current report path: {exc.detail}"]
    for path in paths:
        if path not in current_paths:
            violations.append(f"{path}: missing historical baseline report")
    return violations
