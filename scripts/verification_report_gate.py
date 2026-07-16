#!/usr/bin/env python3
"""Strict public structure checks for Lane V verification reports."""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import sys
import tempfile
import threading
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Callable

import opus_review_receipts as receipts


REPORT_SCHEMA_VERSION = "lane-v-report/v2"
LEGACY_MANIFEST_SCHEMA_VERSION = "lane-v-report-v1-baseline/v1"
TASK_PUBLICATION_SCHEMA_VERSION = "lane-v-task-publication/v1"
ATTESTATION_MAX_BYTES = 65_536
ATTESTATION_LINE_MAX_BYTES = 49_152
TASK_PUBLICATION_MAX_BYTES = 16_384

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
_GIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
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
_RECEIPT_BACKEND = "receipt"
_TASK_BACKEND = "task"
_RECEIPT_BACKED_MODES = frozenset({receipts.CODEX_MODE})
_TASK_BACKED_MODES = frozenset(
    {receipts.CLAUDE_MODE, receipts.CODEX_PROVIDER_FREE_MODE}
)
_BRIDGE_GIT_ADAPTER_LOCK = threading.Lock()


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


@dataclass(frozen=True)
class TaskPublicationRecord:
    task_id: str
    authority_digest: str
    state: str
    generation: int
    path: str | None
    candidate_digest: str | None
    candidate_name: str | None
    candidate_device: int | None
    candidate_inode: int | None
    index_blob_oid: str | None
    index_mode: str | None
    index_stage: int | None


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


def _canonical_receipt_id(value: str) -> str:
    try:
        return receipts.canonical_receipt_id(value)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError(exc.reason, exc.detail) from exc


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


def _validate_provider_free_codex_fields(fields: Mapping[str, str]) -> None:
    if fields["Verification harness"] != receipts.CODEX_HARNESS:
        _fail(
            "invalid_attestation_value",
            "provider-free Codex harness does not match",
        )
    if fields["Review profile"] != receipts.CODEX_PROVIDER_FREE_MODE:
        _fail(
            "invalid_attestation_value",
            "provider-free Codex profile does not match",
        )
    for label in ATTESTATION_FIELDS[9:]:
        if fields[label] != "not-applicable":
            _fail("invalid_attestation_value", f"{label} must be not-applicable")


def _publication_backend(mode: str) -> str:
    if mode in _RECEIPT_BACKED_MODES:
        return _RECEIPT_BACKEND
    if mode in _TASK_BACKED_MODES:
        return _TASK_BACKEND
    _fail("invalid_attestation_value", "unsupported Verification mode")


def _identifier_backend(
    receipt_id: str | None,
    task_id: str | None,
    *,
    reason: str,
) -> str:
    if (receipt_id is None) == (task_id is None):
        _fail(reason, "choose exactly one receipt or task ID")
    return _RECEIPT_BACKEND if receipt_id is not None else _TASK_BACKEND


def _committed_report_profile(descriptor: receipts.ScopeDescriptor) -> str:
    mode = descriptor.verification_mode
    _publication_backend(mode)
    if mode == receipts.CLAUDE_MODE:
        return "not-applicable"
    if mode in {receipts.CODEX_MODE, receipts.CODEX_PROVIDER_FREE_MODE}:
        return descriptor.review_profile
    _fail("invalid_scope_descriptor", "unsupported committed review profile")


def _validate_fields(fields: Mapping[str, str]) -> None:
    if fields["Verification schema"] != REPORT_SCHEMA_VERSION:
        _fail("invalid_attestation_value", "unexpected Verification schema")
    mode = fields["Verification mode"]
    _publication_backend(mode)
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
    if mode == receipts.CODEX_PROVIDER_FREE_MODE:
        _validate_provider_free_codex_fields(fields)
        return
    assert mode == receipts.CLAUDE_MODE
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
    try:
        with tempfile.TemporaryDirectory(prefix="lane-v-git-", dir="/tmp") as name:
            private_root = Path(name)
            os.chmod(private_root, 0o700)
            home = private_root / "home"
            xdg = private_root / "xdg"
            home.mkdir(mode=0o700)
            xdg.mkdir(mode=0o700)
            return subprocess.run(
                [
                    "/usr/bin/git",
                    "--no-replace-objects",
                    "--literal-pathspecs",
                    *args,
                ],
                cwd=root,
                env={
                    "PATH": "/usr/bin:/bin",
                    "LANG": "C",
                    "LC_ALL": "C",
                    "HOME": str(home),
                    "XDG_CONFIG_HOME": str(xdg),
                },
                capture_output=True,
                text=text,
                check=False,
            )
    except OSError as exc:
        raise ReportGateError("git_unavailable", str(exc)) from exc


def _require_repository(root: Path) -> Path:
    try:
        resolved = receipts.require_pipeline_root(root)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_repository", exc.detail) from exc
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in str(resolved)):
        _fail("invalid_repository", "root path contains control characters")
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
    canonical_references = [
        line.removeprefix("Lane-V-Scope: ")
        for line in lines
        if line.startswith("Lane-V-Scope: ")
    ]
    if len(canonical_references) != 1:
        _fail(
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
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
    if references[0] != canonical_references[0]:
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
        "review profile": (
            _committed_report_profile(descriptor),
            report.fields["Review profile"],
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


def _live_report_shape(report: LaneVReport) -> None:
    if not isinstance(report, LaneVReport):
        _fail("invalid_live_report", "report must be a parsed LaneVReport")
    if report.sender not in {"operator", "operator2"}:
        _fail("invalid_report_sender", "only operator seats may publish reports")
    if tuple(report.fields) != ATTESTATION_FIELDS:
        _fail("invalid_live_report", "report attestation fields are incomplete")


def _validate_codex_record(
    root: Path,
    report: LaneVReport,
    authority: StructuralAuthority,
    record: receipts.ReceiptRecord,
) -> None:
    if record.state not in {"reconciled", "publishing", "published"}:
        _fail(
            "invalid_receipt_state",
            "Codex receipt is not reconciled for report publication",
        )
    if (
        record.receipt_id != report.fields["Opus receipt ID"]
        or record.scope_digest != report.fields["Opus scope digest"]
    ):
        _fail("receipt_binding_mismatch", "report receipt identity does not match")

    try:
        scope = receipts.review_scope_from_mapping(record.scope)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError(
            "invalid_live_receipt", "stored receipt scope is malformed"
        ) from exc
    expected_scope = {
        "repository_identity": _repository_identity(root),
        "task_id": authority.descriptor.task_id,
        "question_id": authority.descriptor.question_id,
        "trigger_kind": authority.trigger_kind,
        "trigger_identity": authority.trigger_identity,
        "trigger_commit": authority.trigger_commit,
        "trigger_path": authority.trigger_path,
        "descriptor_path": authority.reference.descriptor_path,
        "descriptor_digest": authority.reference.descriptor_digest,
        "review_profile": authority.descriptor.review_profile,
        "verification_mode": authority.descriptor.verification_mode,
        "verification_harness": authority.descriptor.verification_harness,
        "reviewed_head": report.fields["Reviewed head"],
        "requested_base": report.fields["Reviewed base"],
        "effective_base": report.fields["Reviewed base"],
    }
    for key, expected in expected_scope.items():
        if getattr(scope, key) != expected:
            _fail("receipt_scope_mismatch", f"stored receipt {key} does not match")

    try:
        # Deliberately lazy: publication is the only report-gate path that needs
        # the provider bridge, and all three normalizers run while the receipt
        # lock is held. Raw receipt mappings never authorize report prose.
        import opus_review_bridge as bridge

        stored_review = bridge.stored_review_from_record(record)
        stored_reconciliation = bridge.stored_reconciliation_from_record(record)
        # Task 5's public validator owns the scope semantics, while Task 6 owns
        # the stronger child-process policy. Its private runner has the same
        # call signature, so adapt it only for this bounded public call. The
        # lock makes the temporary module binding process-thread safe.
        with _BRIDGE_GIT_ADAPTER_LOCK:
            original_git_process = bridge._git_process
            bridge._git_process = _git_process
            try:
                scoped_reconciliation = bridge.validated_report_reconciliation_scope(
                    root,
                    record,
                    report.fields["Reviewed head"],
                    report.fields["Reviewed base"],
                )
            finally:
                bridge._git_process = original_git_process
    except Exception as exc:
        reason = getattr(exc, "reason", "invalid_receipt")
        raise ReportGateError(
            "invalid_live_receipt", f"receipt normalization failed: {reason}"
        ) from exc

    if receipts.canonical_json_bytes(
        stored_reconciliation.to_dict()
    ) != receipts.canonical_json_bytes(scoped_reconciliation.to_dict()):
        _fail("receipt_scope_mismatch", "scoped reconciliation changed authority")
    if (
        stored_review.authorization_source
        != report.fields["Authorization identity"]
    ):
        _fail("receipt_binding_mismatch", "authorization identity does not match")

    reconciliation = scoped_reconciliation.reconciliation
    # The verdict check intentionally precedes every go_allowed check. A NITS
    # or FAIL report may not substitute for the exact stored Codex verdict.
    if report.verdict != reconciliation.codex_verdict:
        _fail("verdict_mismatch", "report verdict does not match reconciliation")

    for label in _OPUS_SPECIFIC_FIELDS:
        if report.fields[label] != scoped_reconciliation.report_fields.get(label):
            _fail("receipt_binding_mismatch", f"{label} does not match receipt")

    guard = _strict_json_value(
        report.fields["Reconciliation guard"], "Reconciliation guard"
    )
    assert isinstance(guard, Mapping)
    report_go_allowed = guard.get("go_allowed")
    if report_go_allowed != reconciliation.go_allowed:
        _fail("go_allowed_mismatch", "report guard does not match reconciliation")
    if (report.verdict == "GO") != report_go_allowed:
        _fail("go_allowed_mismatch", "GO alone requires go_allowed true")

    if (
        authority.verify_request_recipient is not None
        and report.sender != authority.verify_request_recipient
    ):
        _fail(
            "verify_request_recipient_mismatch",
            "report sender is not the verify-request operator recipient",
        )


_TASK_PUBLICATION_FIELDS = frozenset(
    {
        "schema_version",
        "task_id",
        "authority_digest",
        "state",
        "generation",
        "path",
        "candidate_digest",
        "candidate_name",
        "candidate_device",
        "candidate_inode",
        "index_blob_oid",
        "index_mode",
        "index_stage",
    }
)
_TASK_WITNESS_FIELDS = (
    "path",
    "candidate_digest",
    "candidate_name",
    "candidate_device",
    "candidate_inode",
    "index_blob_oid",
    "index_mode",
    "index_stage",
)
_TASK_STATE_MINIMUM_GENERATION = {"ready": 1, "publishing": 2, "published": 3}
_TASK_STATE_GENERATION_PARITY = {"ready": 1, "publishing": 0, "published": 1}


def _task_record_mapping(record: TaskPublicationRecord) -> dict[str, object]:
    return {
        "schema_version": TASK_PUBLICATION_SCHEMA_VERSION,
        "task_id": record.task_id,
        "authority_digest": record.authority_digest,
        "state": record.state,
        "generation": record.generation,
        "path": record.path,
        "candidate_digest": record.candidate_digest,
        "candidate_name": record.candidate_name,
        "candidate_device": record.candidate_device,
        "candidate_inode": record.candidate_inode,
        "index_blob_oid": record.index_blob_oid,
        "index_mode": record.index_mode,
        "index_stage": record.index_stage,
    }


def _task_witness_from_values(
    path: object,
    candidate_digest: object,
    candidate_name: object,
    candidate_device: object,
    candidate_inode: object,
    index_blob_oid: object,
    index_mode: object,
    index_stage: object,
) -> dict[str, object]:
    try:
        return receipts._publication_witness_from_values(
            path,
            candidate_digest,
            candidate_name,
            candidate_device,
            candidate_inode,
            index_blob_oid,
            index_mode,
            index_stage,
        )
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_task_publication", exc.detail) from exc


def _task_record_from_bytes(raw: bytes, expected_task_id: str) -> TaskPublicationRecord:
    if len(raw) > TASK_PUBLICATION_MAX_BYTES:
        _fail("invalid_task_publication", "task publication record is too large")
    try:
        value = receipts.strict_json_loads(raw)
    except receipts.ReceiptContractError as exc:
        raise ReportGateError("invalid_task_publication", exc.detail) from exc
    if not isinstance(value, Mapping) or set(value) != _TASK_PUBLICATION_FIELDS:
        _fail("invalid_task_publication", "task publication fields do not match")
    if value["schema_version"] != TASK_PUBLICATION_SCHEMA_VERSION:
        _fail("invalid_task_publication", "unexpected task publication schema")
    task_id = value["task_id"]
    if not isinstance(task_id, str) or _canonical_uuid(task_id) != expected_task_id:
        _fail("invalid_task_publication", "task publication identity does not match")
    authority_digest = value["authority_digest"]
    if not isinstance(authority_digest, str) or _SHA256_RE.fullmatch(
        authority_digest
    ) is None:
        _fail("invalid_task_publication", "authority_digest is not canonical")
    state = value["state"]
    if state not in _TASK_STATE_MINIMUM_GENERATION:
        _fail("invalid_task_publication", "task publication state is invalid")
    generation = value["generation"]
    if (
        isinstance(generation, bool)
        or not isinstance(generation, int)
        or generation < _TASK_STATE_MINIMUM_GENERATION[state]
        or generation % 2 != _TASK_STATE_GENERATION_PARITY[state]
    ):
        _fail("invalid_task_publication", "task publication generation is invalid")
    witness_values = tuple(value[field] for field in _TASK_WITNESS_FIELDS)
    if state == "ready":
        if any(item is not None for item in witness_values):
            _fail("invalid_task_publication", "ready task retains a witness")
        witness: dict[str, object] = {field: None for field in _TASK_WITNESS_FIELDS}
    else:
        witness = _task_witness_from_values(*witness_values)
    return TaskPublicationRecord(
        task_id=task_id,
        authority_digest=authority_digest,
        state=state,
        generation=generation,
        **witness,
    )


@dataclass(frozen=True)
class TaskPublicationStore:
    state_root: Path

    @classmethod
    def for_repo(
        cls,
        repo_root: str | os.PathLike[str],
        *,
        state_root: str | os.PathLike[str] | None = None,
    ) -> TaskPublicationStore:
        if state_root is None:
            root = _require_repository(Path(repo_root))
            result = _git_process(
                root,
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            )
            if result.returncode != 0 or not isinstance(result.stdout, str):
                _fail("invalid_repository", "could not resolve Git common directory")
            common = Path(result.stdout.strip()).resolve()
            publication_root = (
                common.parent / ".codex/runtime/lane-v-report-publications/v1"
            )
        else:
            publication_root = Path(state_root).absolute()
        directory_fd = receipts._ensure_private_directory(publication_root)
        os.close(directory_fd)
        return cls(publication_root)

    def lock_task(self, task_id: str, *, blocking: bool = True) -> LockedTask:
        return LockedTask(self, _canonical_uuid(task_id), blocking=blocking)


class LockedTask:
    def __init__(
        self, store: TaskPublicationStore, task_id: str, *, blocking: bool
    ) -> None:
        self._store = store
        self._task_id = task_id
        self._record_name = f"{task_id}.json"
        self._lock_name = f"{task_id}.lock"
        self._blocking = blocking
        self._directory_fd: int | None = None
        self._lock_fd: int | None = None
        self._current: TaskPublicationRecord | None = None

    def __enter__(self) -> LockedTask:
        if self._directory_fd is not None:
            _fail("task_lock_reentry", "task publication lock is already active")
        directory_fd = receipts._ensure_private_directory(self._store.state_root)
        try:
            lock_fd = os.open(
                self._lock_name,
                receipts._private_file_flags(os.O_CREAT | os.O_RDWR),
                0o600,
                dir_fd=directory_fd,
            )
            try:
                receipts._validate_private_file(
                    lock_fd, label="task publication lock", stat_fn=os.fstat
                )
                operation = fcntl.LOCK_EX
                if not self._blocking:
                    operation |= fcntl.LOCK_NB
                fcntl.flock(lock_fd, operation)
            except BaseException:
                os.close(lock_fd)
                raise
        except OSError as exc:
            os.close(directory_fd)
            if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK}:
                raise ReportGateError(
                    "task_publication_in_progress", "task lock is held"
                ) from exc
            raise ReportGateError("task_lock_failed", str(exc)) from exc
        except BaseException:
            os.close(directory_fd)
            raise
        self._directory_fd = directory_fd
        self._lock_fd = lock_fd
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        lock_fd = self._lock_fd
        directory_fd = self._directory_fd
        self._lock_fd = None
        self._directory_fd = None
        self._current = None
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            finally:
                os.close(lock_fd)
        if directory_fd is not None:
            os.close(directory_fd)

    def _require_locked(self) -> int:
        if self._directory_fd is None or self._lock_fd is None:
            _fail("task_lock_required", "task publication lock is not held")
        return self._directory_fd

    def _read_record(
        self, *, allow_missing: bool = False
    ) -> TaskPublicationRecord | None:
        directory_fd = self._require_locked()
        try:
            record_fd = os.open(
                self._record_name,
                receipts._private_file_flags(os.O_RDONLY | os.O_NONBLOCK),
                dir_fd=directory_fd,
            )
        except FileNotFoundError:
            if allow_missing:
                return None
            _fail("task_publication_missing", "task publication record is missing")
        except OSError as exc:
            raise ReportGateError("task_publication_open_failed", str(exc)) from exc
        try:
            receipts._validate_private_file(
                record_fd, label="task publication record", stat_fn=os.fstat
            )
            chunks: list[bytes] = []
            remaining = TASK_PUBLICATION_MAX_BYTES + 1
            while remaining:
                chunk = os.read(record_fd, min(65_536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
        finally:
            os.close(record_fd)
        return _task_record_from_bytes(b"".join(chunks), self._task_id)

    def load_existing(self) -> TaskPublicationRecord:
        current = self._read_record()
        assert current is not None
        self._current = current
        return current

    def _verified_current(self) -> TaskPublicationRecord:
        if self._current is None:
            _fail("task_publication_not_loaded", "task record must be loaded first")
        observed = self._read_record()
        assert observed is not None
        if receipts.canonical_json_bytes(
            _task_record_mapping(observed)
        ) != receipts.canonical_json_bytes(_task_record_mapping(self._current)):
            _fail("task_publication_conflict", "task record changed while locked")
        return observed

    def _atomic_replace(self, record: TaskPublicationRecord) -> None:
        raw = receipts.canonical_json_bytes(_task_record_mapping(record))
        if len(raw) > TASK_PUBLICATION_MAX_BYTES:
            _fail("invalid_task_publication", "task publication record is too large")
        directory_fd = self._require_locked()
        temporary_name = f"{self._record_name}.tmp-{uuid.uuid4().hex}"
        temporary_fd: int | None = None
        try:
            temporary_fd = os.open(
                temporary_name,
                receipts._private_file_flags(os.O_CREAT | os.O_EXCL | os.O_WRONLY),
                0o600,
                dir_fd=directory_fd,
            )
            receipts._validate_private_file(
                temporary_fd, label="temporary task record", stat_fn=os.fstat
            )
            receipts._write_all(temporary_fd, raw)
            os.fsync(temporary_fd)
            os.close(temporary_fd)
            temporary_fd = None
            os.replace(
                temporary_name,
                self._record_name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
            )
            os.fsync(directory_fd)
        except BaseException as exc:
            if temporary_fd is not None:
                os.close(temporary_fd)
            try:
                os.unlink(temporary_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
            if isinstance(exc, ReportGateError):
                raise
            raise ReportGateError("task_publication_replace_failed", str(exc)) from exc

    def load_or_create(self, authority_digest: str) -> TaskPublicationRecord:
        if _SHA256_RE.fullmatch(authority_digest) is None:
            _fail("invalid_task_authority", "authority digest is not canonical")
        current = self._read_record(allow_missing=True)
        if current is None:
            current = TaskPublicationRecord(
                task_id=self._task_id,
                authority_digest=authority_digest,
                state="ready",
                generation=1,
                **{field: None for field in _TASK_WITNESS_FIELDS},
            )
            self._atomic_replace(current)
        elif current.authority_digest != authority_digest:
            _fail("task_authority_conflict", "task already has different authority")
        self._current = current
        return current

    def _witness(
        self,
        path: str,
        candidate_digest: str,
        candidate_name: str,
        candidate_device: int,
        candidate_inode: int,
        index_blob_oid: str,
        index_mode: str,
        index_stage: int,
    ) -> dict[str, object]:
        return _task_witness_from_values(
            path,
            candidate_digest,
            candidate_name,
            candidate_device,
            candidate_inode,
            index_blob_oid,
            index_mode,
            index_stage,
        )

    def begin_publication(
        self,
        path: str,
        candidate_digest: str,
        candidate_name: str,
        candidate_device: int,
        candidate_inode: int,
        index_blob_oid: str,
        index_mode: str,
        index_stage: int,
    ) -> TaskPublicationRecord:
        current = self._verified_current()
        witness = self._witness(
            path,
            candidate_digest,
            candidate_name,
            candidate_device,
            candidate_inode,
            index_blob_oid,
            index_mode,
            index_stage,
        )
        if current.state in {"publishing", "published"}:
            if all(getattr(current, key) == value for key, value in witness.items()):
                return current
            _fail("publication_replay_conflict", "task names another publication")
        if current.state != "ready":
            _fail("invalid_task_transition", "publication cannot begin")
        updated = TaskPublicationRecord(
            task_id=current.task_id,
            authority_digest=current.authority_digest,
            state="publishing",
            generation=current.generation + 1,
            **witness,
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    def finish_publication(
        self,
        path: str,
        candidate_digest: str,
        candidate_name: str,
        candidate_device: int,
        candidate_inode: int,
        index_blob_oid: str,
        index_mode: str,
        index_stage: int,
    ) -> TaskPublicationRecord:
        current = self._verified_current()
        witness = self._witness(
            path,
            candidate_digest,
            candidate_name,
            candidate_device,
            candidate_inode,
            index_blob_oid,
            index_mode,
            index_stage,
        )
        if current.state == "published":
            if all(getattr(current, key) == value for key, value in witness.items()):
                return current
            _fail("publication_replay_conflict", "published task names another target")
        if current.state != "publishing" or any(
            getattr(current, key) != value for key, value in witness.items()
        ):
            _fail("publication_replay_conflict", "publication witness changed")
        updated = TaskPublicationRecord(
            task_id=current.task_id,
            authority_digest=current.authority_digest,
            state="published",
            generation=current.generation + 1,
            **witness,
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    def cancel_publication(
        self,
        path: str,
        candidate_digest: str,
        candidate_name: str,
        candidate_device: int,
        candidate_inode: int,
        index_blob_oid: str,
        index_mode: str,
        index_stage: int,
        expected_generation: int,
    ) -> TaskPublicationRecord:
        current = self._verified_current()
        witness = self._witness(
            path,
            candidate_digest,
            candidate_name,
            candidate_device,
            candidate_inode,
            index_blob_oid,
            index_mode,
            index_stage,
        )
        if (
            current.state != "publishing"
            or isinstance(expected_generation, bool)
            or not isinstance(expected_generation, int)
            or current.generation != expected_generation
            or any(getattr(current, key) != value for key, value in witness.items())
        ):
            _fail("publication_replay_conflict", "cancellation witness changed")
        updated = TaskPublicationRecord(
            task_id=current.task_id,
            authority_digest=current.authority_digest,
            state="ready",
            generation=current.generation + 1,
            **{field: None for field in _TASK_WITNESS_FIELDS},
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    def recover_publication(
        self,
        path: str,
        observed_digest: str | None,
        observed_device: int | None,
        observed_inode: int | None,
    ) -> str:
        current = self._verified_current()
        if current.state != "publishing":
            _fail("invalid_task_transition", "only publishing may recover")
        try:
            normalized_path = receipts._publication_path(path)
        except receipts.ReceiptContractError as exc:
            raise ReportGateError("invalid_task_publication", exc.detail) from exc
        if normalized_path != current.path:
            _fail("publication_replay_conflict", "recovery path changed")
        if observed_digest is None:
            if observed_device is not None or observed_inode is not None:
                _fail("invalid_task_publication", "absent witness must be all null")
            updated = TaskPublicationRecord(
                task_id=current.task_id,
                authority_digest=current.authority_digest,
                state="ready",
                generation=current.generation + 1,
                **{field: None for field in _TASK_WITNESS_FIELDS},
            )
            self._atomic_replace(updated)
            self._current = updated
            return "clear"
        if (
            isinstance(observed_device, bool)
            or not isinstance(observed_device, int)
            or observed_device < 0
            or isinstance(observed_inode, bool)
            or not isinstance(observed_inode, int)
            or observed_inode <= 0
        ):
            _fail(
                "invalid_task_publication",
                "observed device and inode must be exact integers",
            )
        if (
            observed_digest == current.candidate_digest
            and observed_device == current.candidate_device
            and observed_inode == current.candidate_inode
        ):
            return "finalize"
        _fail("publication_replay_conflict", "recovery witness changed")


def _repository_identity(root: Path) -> str:
    result = _git_process(
        root, "rev-parse", "--path-format=absolute", "--git-common-dir"
    )
    if result.returncode != 0 or not isinstance(result.stdout, str):
        _fail("invalid_repository", "could not resolve repository identity")
    common = Path(result.stdout.strip()).resolve()
    return "sha256:" + hashlib.sha256(str(common).encode("utf-8")).hexdigest()


def _task_authority_digest(
    root: Path, report: LaneVReport, authority: StructuralAuthority
) -> str:
    authority_mapping = {
        "repository_identity": _repository_identity(root),
        "task_id": authority.descriptor.task_id,
        "verification_mode": report.fields["Verification mode"],
        "verification_harness": report.fields["Verification harness"],
        "descriptor_path": authority.reference.descriptor_path,
        "descriptor_digest": authority.reference.descriptor_digest,
        "trigger_identity": authority.trigger_identity,
        "reviewed_head": report.fields["Reviewed head"],
        "reviewed_base": report.fields["Reviewed base"],
        "authorized_operator_recipient": report.sender,
    }
    return "sha256:" + hashlib.sha256(
        receipts.canonical_json_bytes(authority_mapping)
    ).hexdigest()


def _publication_cli_command(
    root: Path,
    operation: str,
    *,
    receipt_id: str | None = None,
    task_id: str | None = None,
) -> str:
    if operation not in {"resume", "status"} or (receipt_id is None) == (
        task_id is None
    ):
        _fail("invalid_publication_command", "publication command is incomplete")
    common_result = _git_process(
        root, "rev-parse", "--path-format=absolute", "--git-common-dir"
    )
    if common_result.returncode != 0 or not isinstance(common_result.stdout, str):
        _fail("invalid_repository", "could not resolve primary publication runtime")
    primary = Path(common_result.stdout.strip()).resolve().parent
    argv = [
        "/usr/bin/env",
        "-i",
        "PATH=/usr/bin:/bin",
        "LANG=C",
        "LC_ALL=C",
        str(primary / ".venv/bin/python"),
        "-E",
        "-s",
        "-S",
        "-B",
        str(primary / "scripts/verification_report_gate.py"),
        operation,
        "--repo-root",
        str(root),
        "--receipt-id" if receipt_id is not None else "--task-id",
        receipt_id if receipt_id is not None else str(task_id),
    ]
    return " ".join(shlex.quote(argument) for argument in argv)


def _validate_non_codex_record(
    record: TaskPublicationRecord,
    expected_authority_digest: str,
) -> None:
    if record.authority_digest != expected_authority_digest:
        _fail("task_authority_conflict", "task authority digest does not match")
    if record.state not in {"ready", "publishing", "published"}:
        _fail("invalid_task_publication", "task publication state is invalid")


def validate_live_report(
    repo_root: str | os.PathLike[str],
    report: LaneVReport,
    *,
    receipt_store_factory: Callable[[Path], receipts.ReceiptStore] = (
        receipts.ReceiptStore.for_repo
    ),
    task_store_factory: Callable[[Path], object] | None = None,
) -> StructuralAuthority:
    """Bind parsed report claims to committed authority and current private state."""

    _live_report_shape(report)
    root = _require_repository(Path(repo_root))
    backend = _publication_backend(report.fields["Verification mode"])
    authority = validate_structural_authority(root, report)
    if backend == _TASK_BACKEND:
        factory = task_store_factory or TaskPublicationStore.for_repo
        try:
            store = factory(root)
            authority_digest = _task_authority_digest(root, report, authority)
            with store.lock_task(
                authority.descriptor.task_id, blocking=True
            ) as task:
                record = task.load_or_create(authority_digest)
                _validate_non_codex_record(record, authority_digest)
        except ReportGateError:
            raise
        except Exception as exc:
            reason = getattr(exc, "reason", "task_publication_access_failed")
            raise ReportGateError(
                "invalid_task_publication", f"task state access failed: {reason}"
            ) from exc
        return authority
    receipt_id = _canonical_receipt_id(report.fields["Opus receipt ID"])
    try:
        store = receipt_store_factory(root)
        with store.lock_receipt(receipt_id, blocking=True) as attempt:
            record = attempt.load_existing()
            _validate_codex_record(root, report, authority, record)
    except ReportGateError:
        raise
    except Exception as exc:
        reason = getattr(exc, "reason", "receipt_access_failed")
        raise ReportGateError(
            "invalid_live_receipt", f"receipt access failed: {reason}"
        ) from exc
    return authority


class _SanitizedGit:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._temporary: tempfile.TemporaryDirectory[str] | None = None
        self._environment: dict[str, str] | None = None

    def __enter__(self) -> _SanitizedGit:
        temporary = tempfile.TemporaryDirectory(prefix="lane-v-git-", dir="/tmp")
        private_root = Path(temporary.name)
        os.chmod(private_root, 0o700)
        home = private_root / "home"
        xdg = private_root / "xdg"
        home.mkdir(mode=0o700)
        xdg.mkdir(mode=0o700)
        self._temporary = temporary
        self._environment = {
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C",
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(xdg),
        }
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        temporary = self._temporary
        self._temporary = None
        self._environment = None
        if temporary is not None:
            temporary.cleanup()

    def run(
        self,
        *args: str,
        input_bytes: bytes | None = None,
        label: str,
    ) -> bytes:
        if self._environment is None:
            _fail("git_runtime_inactive", "sanitized Git runtime is not active")
        try:
            completed = subprocess.run(
                [
                    "/usr/bin/git",
                    "--no-replace-objects",
                    "--literal-pathspecs",
                    "-C",
                    str(self._root),
                    *args,
                ],
                env=self._environment,
                input=input_bytes,
                capture_output=True,
                check=False,
            )
        except OSError as exc:
            raise ReportGateError("git_unavailable", f"{label} failed") from exc
        if completed.returncode != 0:
            _fail("git_publication_failed", f"{label} failed")
        return completed.stdout


@dataclass(frozen=True)
class _CapturedCandidate:
    fd: int
    name: str
    raw: bytes
    digest: str
    device: int
    inode: int


@dataclass(frozen=True)
class _PublishedReportResult:
    path: Path
    receipt_id: str | None
    task_id: str | None


def _publication_checkpoint(label: str) -> None:
    """Fault-injection seam for crash-boundary regression tests."""


def _directory_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _file_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )


def _open_sent_directory(root: Path) -> int:
    descriptors: list[int] = []
    try:
        current = os.open(root, _directory_flags())
        descriptors.append(current)
        for component in ("coordination", "mailbox", "sent"):
            current = os.open(component, _directory_flags(), dir_fd=current)
            descriptors.append(current)
        sent_fd = descriptors.pop()
        return sent_fd
    except OSError as exc:
        raise ReportGateError(
            "invalid_mailbox_directory", "cannot open canonical sent directory"
        ) from exc
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _read_regular_file(
    fd: int,
    *,
    expected_device: int | None = None,
    expected_inode: int | None = None,
    expected_nlink: int | None = None,
    label: str,
) -> tuple[bytes, os.stat_result]:
    before = os.fstat(fd)
    if (
        before.st_uid != os.getuid()
        or not stat.S_ISREG(before.st_mode)
        or stat.S_IMODE(before.st_mode) != 0o600
        or (expected_device is not None and before.st_dev != expected_device)
        or (expected_inode is not None and before.st_ino != expected_inode)
        or (expected_nlink is not None and before.st_nlink != expected_nlink)
    ):
        _fail("unsafe_publication_file", f"{label} metadata is not authoritative")
    chunks: list[bytes] = []
    remaining = 1_048_577
    while remaining:
        chunk = os.read(fd, min(65_536, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    raw = b"".join(chunks)
    if len(raw) > 1_048_576:
        _fail("publication_file_too_large", f"{label} exceeds 1048576 bytes")
    after = os.fstat(fd)
    stable_fields = (
        "st_dev",
        "st_ino",
        "st_uid",
        "st_mode",
        "st_nlink",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
    )
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
        _fail("publication_file_changed", f"{label} changed while read")
    return raw, after


def _capture_candidate(
    root: Path, candidate_path: Path, sent_fd: int
) -> _CapturedCandidate:
    expected_parent = root / "coordination/mailbox/sent"
    candidate_text = str(candidate_path)
    if (
        not candidate_path.is_absolute()
        or candidate_text != os.path.normpath(candidate_text)
        or candidate_path.parent != expected_parent
        or candidate_path.name in {"", ".", ".."}
    ):
        _fail(
            "unsafe_candidate_path",
            "candidate must be an absolute canonical direct child of sent",
        )
    try:
        candidate_fd = os.open(candidate_path.name, _file_flags(), dir_fd=sent_fd)
    except OSError as exc:
        raise ReportGateError("unsafe_candidate", "candidate cannot be opened") from exc
    try:
        raw, observed = _read_regular_file(
            candidate_fd, expected_nlink=1, label="candidate"
        )
        return _CapturedCandidate(
            fd=candidate_fd,
            name=candidate_path.name,
            raw=raw,
            digest="sha256:" + hashlib.sha256(raw).hexdigest(),
            device=observed.st_dev,
            inode=observed.st_ino,
        )
    except BaseException:
        os.close(candidate_fd)
        raise


def _require_candidate_name(candidate: _CapturedCandidate, sent_fd: int) -> None:
    try:
        observed = os.stat(candidate.name, dir_fd=sent_fd, follow_symlinks=False)
    except OSError as exc:
        raise ReportGateError("candidate_changed", "candidate name disappeared") from exc
    if (
        observed.st_dev != candidate.device
        or observed.st_ino != candidate.inode
        or observed.st_nlink != 1
    ):
        _fail("candidate_changed", "candidate name no longer identifies held inode")


def _revalidate_candidate_basename(
    sent_fd: int,
    name: str,
    *,
    raw: bytes,
    digest: str,
    device: int,
    inode: int,
    expected_nlink: int,
) -> None:
    try:
        descriptor = os.open(name, _file_flags(), dir_fd=sent_fd)
    except OSError as exc:
        raise ReportGateError(
            "candidate_changed", "candidate basename cannot be reopened"
        ) from exc
    try:
        observed_raw, _ = _read_regular_file(
            descriptor,
            expected_device=device,
            expected_inode=inode,
            expected_nlink=expected_nlink,
            label="candidate basename",
        )
        if observed_raw != raw or "sha256:" + hashlib.sha256(
            observed_raw
        ).hexdigest() != digest:
            _fail("candidate_changed", "candidate basename bytes changed")
    except ReportGateError as exc:
        raise ReportGateError(
            "candidate_changed", "candidate basename witness changed"
        ) from exc
    finally:
        os.close(descriptor)


def _cleanup_unbound_candidate(
    candidate: _CapturedCandidate, sent_fd: int
) -> None:
    """Remove only the exact held candidate when no publication owns it."""

    try:
        _revalidate_candidate_basename(
            sent_fd,
            candidate.name,
            raw=candidate.raw,
            digest=candidate.digest,
            device=candidate.device,
            inode=candidate.inode,
            expected_nlink=1,
        )
        os.unlink(candidate.name, dir_fd=sent_fd)
        os.fsync(sent_fd)
    except (OSError, ReportGateError):
        # A changed or uncertain basename is not ours to remove.
        return


def _open_witnessed_final(
    sent_fd: int,
    final_name: str,
    *,
    raw: bytes,
    digest: str,
    device: int,
    inode: int,
    expected_nlink: int | None,
) -> int:
    try:
        final_fd = os.open(final_name, _file_flags(), dir_fd=sent_fd)
    except OSError as exc:
        raise ReportGateError("publication_recovery_mismatch", "final cannot be opened") from exc
    try:
        observed_raw, _ = _read_regular_file(
            final_fd,
            expected_device=device,
            expected_inode=inode,
            expected_nlink=expected_nlink,
            label="final report",
        )
        if observed_raw != raw or "sha256:" + hashlib.sha256(
            observed_raw
        ).hexdigest() != digest:
            _fail("publication_recovery_mismatch", "final bytes do not match witness")
        return final_fd
    except BaseException:
        os.close(final_fd)
        raise


def _parse_index_entry(raw: bytes, expected_path: str) -> tuple[str, str, int]:
    records = raw.split(b"\0")
    if records[-1:] == [b""]:
        records.pop()
    if len(records) != 1:
        _fail("index_witness_mismatch", "expected exactly one index entry")
    metadata, separator, path_bytes = records[0].partition(b"\t")
    parts = metadata.split(b" ")
    if not separator or len(parts) != 3:
        _fail("index_witness_mismatch", "index entry is malformed")
    try:
        mode = parts[0].decode("ascii")
        oid = parts[1].decode("ascii")
        stage_text = parts[2].decode("ascii")
        path = path_bytes.decode("utf-8")
        stage = int(stage_text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReportGateError("index_witness_mismatch", "index entry is invalid") from exc
    if (
        mode != "100644"
        or _GIT_OBJECT_ID_RE.fullmatch(oid) is None
        or stage != 0
        or path != expected_path
    ):
        _fail("index_witness_mismatch", "index entry does not match publication")
    return mode, oid, stage


def _index_entry(git: _SanitizedGit, path: str) -> tuple[str, str, int] | None:
    raw = git.run(
        "ls-files", "--stage", "-z", "--", path, label="index inspection"
    )
    if raw == b"":
        return None
    return _parse_index_entry(raw, path)


def _expected_blob_oid(git: _SanitizedGit, raw: bytes) -> str:
    output = git.run(
        "hash-object",
        "--no-filters",
        "--stdin",
        input_bytes=raw,
        label="blob identity computation",
    )
    try:
        oid = output.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise ReportGateError("invalid_blob_oid", "Git returned a non-ASCII OID") from exc
    if _GIT_OBJECT_ID_RE.fullmatch(oid) is None:
        _fail("invalid_blob_oid", "Git returned an invalid object ID")
    return oid


def _write_blob(git: _SanitizedGit, raw: bytes, expected_oid: str) -> None:
    output = git.run(
        "hash-object",
        "-w",
        "--no-filters",
        "--stdin",
        input_bytes=raw,
        label="exact blob write",
    )
    try:
        actual_oid = output.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise ReportGateError("invalid_blob_oid", "Git returned a non-ASCII OID") from exc
    if actual_oid != expected_oid:
        _fail("blob_witness_mismatch", "written object ID changed")


def _verify_blob(git: _SanitizedGit, raw: bytes, digest: str, oid: str) -> None:
    observed = git.run("cat-file", "blob", oid, label="blob verification")
    if observed != raw or "sha256:" + hashlib.sha256(observed).hexdigest() != digest:
        _fail("blob_witness_mismatch", "staged blob bytes changed")


def _stage_or_verify_index(
    git: _SanitizedGit,
    path: str,
    oid: str,
    *,
    allow_existing_exact: bool,
) -> None:
    existing = _index_entry(git, path)
    exact = ("100644", oid, 0)
    if existing is not None:
        if allow_existing_exact and existing == exact:
            return
        _fail("index_entry_conflict", "publication path already has an index entry")
    git.run(
        "update-index",
        "--add",
        "--cacheinfo",
        f"100644,{oid},{path}",
        label="exact index update",
    )
    if _index_entry(git, path) != exact:
        _fail("index_witness_mismatch", "staged index entry changed")


def _fsync_index(git: _SanitizedGit) -> None:
    output = git.run(
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        "index",
        label="index path resolution",
    )
    try:
        index_text = output.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ReportGateError("index_path_invalid", "index path is not UTF-8") from exc
    index_path = Path(index_text)
    if not index_path.is_absolute() or str(index_path) != os.path.normpath(str(index_path)):
        _fail("index_path_invalid", "Git index path is not canonical absolute")
    try:
        index_fd = os.open(index_path, _file_flags())
        try:
            observed = os.fstat(index_fd)
            if (
                observed.st_uid != os.getuid()
                or not stat.S_ISREG(observed.st_mode)
                or observed.st_nlink != 1
            ):
                _fail("index_path_invalid", "Git index metadata is unsafe")
            _publication_checkpoint("before_index_file_fsync")
            os.fsync(index_fd)
            _publication_checkpoint("after_index_file_fsync")
        finally:
            os.close(index_fd)
        parent_fd = os.open(index_path.parent, _directory_flags())
        try:
            _publication_checkpoint("before_index_directory_fsync")
            os.fsync(parent_fd)
            _publication_checkpoint("after_index_directory_fsync")
        finally:
            os.close(parent_fd)
    except OSError as exc:
        raise ReportGateError("index_durability_failed", "cannot fsync Git index") from exc


def _last_pre_publish_guard(
    *,
    sent_fd: int,
    candidate_name: str,
    final_name: str,
    final_relative: str,
    raw: bytes,
    digest: str,
    device: int,
    inode: int,
    expected_oid: str,
    git: _SanitizedGit,
) -> None:
    if _stored_name_exists(sent_fd, candidate_name):
        _fail(
            "candidate_changed",
            "candidate basename reappeared before publication completion",
        )
    final_fd = _open_witnessed_final(
        sent_fd,
        final_name,
        raw=raw,
        digest=digest,
        device=device,
        inode=inode,
        expected_nlink=1,
    )
    os.close(final_fd)
    if _index_entry(git, final_relative) != ("100644", expected_oid, 0):
        _fail("index_witness_mismatch", "final index witness changed")
    _verify_blob(git, raw, digest, expected_oid)


def _retain_post_replace_candidate(
    attempt: object,
    witness: tuple[str, str, str, int, int, str, str, int],
    set_candidate_ownership: Callable[[bool], None],
) -> None:
    """Retain a candidate only for an exact publishing witness reloaded from disk."""

    try:
        observed = attempt.load_existing()
        if getattr(observed, "state", None) != "publishing":
            return
        stored = _stored_publication_witness(observed)
    except BaseException:
        # Recovery evidence must never replace the original begin failure.
        return
    if tuple(stored[field] for field in _TASK_WITNESS_FIELDS) == witness:
        set_candidate_ownership(True)


def _locked_publish_new(
    *,
    attempt: object,
    record: object,
    root: Path,
    final_relative: str,
    candidate: _CapturedCandidate,
    sent_fd: int,
    git: _SanitizedGit,
    set_candidate_ownership: Callable[[bool], None],
) -> Path:
    state = getattr(record, "state", None)
    if state == "published":
        _fail("publication_already_published", "task is already published")
    if state == "publishing":
        _fail(
            "publication_resume_required",
            "interrupted publication requires explicit resume by stored identifier",
        )
    if state not in {"reconciled", "ready"}:
        _fail("invalid_publication_state", "task is not ready to publish")

    expected_oid = _expected_blob_oid(git, candidate.raw)
    if _index_entry(git, final_relative) is not None:
        _fail("index_entry_conflict", "fresh publication path is already staged")
    witness = (
        final_relative,
        candidate.digest,
        candidate.name,
        candidate.device,
        candidate.inode,
        expected_oid,
        "100644",
        0,
    )
    _publication_checkpoint("before_publishing")
    try:
        publishing = attempt.begin_publication(*witness)
    except BaseException:
        _retain_post_replace_candidate(
            attempt, witness, set_candidate_ownership
        )
        raise
    set_candidate_ownership(True)
    _publication_checkpoint("after_publishing")
    _require_candidate_name(candidate, sent_fd)
    try:
        _publication_checkpoint("before_candidate_fsync")
        os.fsync(candidate.fd)
    except OSError as exc:
        raise ReportGateError(
            "publication_durability_failed", "candidate fsync failed"
        ) from exc
    _publication_checkpoint("after_candidate_fsync")

    final_name = PurePosixPath(final_relative).name
    try:
        _publication_checkpoint("before_link")
        _revalidate_candidate_basename(
            sent_fd,
            candidate.name,
            raw=candidate.raw,
            digest=candidate.digest,
            device=candidate.device,
            inode=candidate.inode,
            expected_nlink=1,
        )
        os.link(
            candidate.name,
            final_name,
            src_dir_fd=sent_fd,
            dst_dir_fd=sent_fd,
            follow_symlinks=False,
        )
    except FileExistsError as exc:
        attempt.cancel_publication(*witness, publishing.generation)
        set_candidate_ownership(False)
        raise ReportGateError(
            "publication_path_exists", "final report already exists"
        ) from exc
    except OSError as exc:
        raise ReportGateError("publication_link_failed", "hard link failed") from exc
    _publication_checkpoint("after_link")

    final_fd = _open_witnessed_final(
        sent_fd,
        final_name,
        raw=candidate.raw,
        digest=candidate.digest,
        device=candidate.device,
        inode=candidate.inode,
        expected_nlink=2,
    )
    try:
        _publication_checkpoint("before_linked_final_fsync")
        os.fsync(final_fd)
    except OSError as exc:
        raise ReportGateError(
            "publication_durability_failed", "linked final fsync failed"
        ) from exc
    finally:
        os.close(final_fd)
    _publication_checkpoint("after_linked_final_fsync")
    try:
        _publication_checkpoint("before_link_directory_fsync")
        os.fsync(sent_fd)
    except OSError as exc:
        raise ReportGateError(
            "publication_durability_failed", "sent directory fsync failed"
        ) from exc
    _publication_checkpoint("after_link_directory_fsync")

    _publication_checkpoint("before_object_write")
    _write_blob(git, candidate.raw, expected_oid)
    _publication_checkpoint("after_object_write")
    _publication_checkpoint("before_index_update")
    _stage_or_verify_index(
        git,
        final_relative,
        expected_oid,
        allow_existing_exact=False,
    )
    _publication_checkpoint("after_index_update")
    _publication_checkpoint("before_stage_verification")
    if _index_entry(git, final_relative) != ("100644", expected_oid, 0):
        _fail("index_witness_mismatch", "stage-0 witness changed")
    _publication_checkpoint("after_stage_verification")
    _verify_blob(git, candidate.raw, candidate.digest, expected_oid)

    _publication_checkpoint("before_final_revalidation")
    final_fd = _open_witnessed_final(
        sent_fd,
        final_name,
        raw=candidate.raw,
        digest=candidate.digest,
        device=candidate.device,
        inode=candidate.inode,
        expected_nlink=2,
    )
    os.close(final_fd)
    _publication_checkpoint("after_final_revalidation")
    candidate_after_link = os.fstat(candidate.fd)
    if (
        candidate_after_link.st_dev != candidate.device
        or candidate_after_link.st_ino != candidate.inode
        or candidate_after_link.st_nlink != 2
    ):
        _fail("candidate_changed", "candidate inode changed after linking")
    try:
        _publication_checkpoint("before_candidate_unlink")
        _revalidate_candidate_basename(
            sent_fd,
            candidate.name,
            raw=candidate.raw,
            digest=candidate.digest,
            device=candidate.device,
            inode=candidate.inode,
            expected_nlink=2,
        )
        os.unlink(candidate.name, dir_fd=sent_fd)
        _publication_checkpoint("after_candidate_unlink")
        _publication_checkpoint("before_cleanup_directory_fsync")
        os.fsync(sent_fd)
        _publication_checkpoint("after_cleanup_directory_fsync")
    except OSError as exc:
        raise ReportGateError(
            "publication_cleanup_failed", "candidate cleanup durability failed"
        ) from exc
    _publication_checkpoint("after_candidate_cleanup")

    final_fd = _open_witnessed_final(
        sent_fd,
        final_name,
        raw=candidate.raw,
        digest=candidate.digest,
        device=candidate.device,
        inode=candidate.inode,
        expected_nlink=1,
    )
    try:
        _publication_checkpoint("before_completed_final_fsync")
        os.fsync(final_fd)
        _publication_checkpoint("after_completed_final_fsync")
    except OSError as exc:
        raise ReportGateError(
            "publication_durability_failed", "final report fsync failed"
        ) from exc
    finally:
        os.close(final_fd)
    if _index_entry(git, final_relative) != ("100644", expected_oid, 0):
        _fail("index_witness_mismatch", "index changed before completion")
    _verify_blob(git, candidate.raw, candidate.digest, expected_oid)
    _publication_checkpoint("before_index_fsync")
    _fsync_index(git)
    _publication_checkpoint("after_index_fsync")
    _publication_checkpoint("before_published")
    _last_pre_publish_guard(
        sent_fd=sent_fd,
        candidate_name=candidate.name,
        final_name=final_name,
        final_relative=final_relative,
        raw=candidate.raw,
        digest=candidate.digest,
        device=candidate.device,
        inode=candidate.inode,
        expected_oid=expected_oid,
        git=git,
    )
    attempt.finish_publication(*witness)
    _publication_checkpoint("after_published")
    return root / final_relative


def _publish_candidate_result(
    *,
    repo_root: str | os.PathLike[str],
    candidate_path: str | os.PathLike[str],
    final_relative: str,
    receipt_store_factory: Callable[[Path], receipts.ReceiptStore] = (
        receipts.ReceiptStore.for_repo
    ),
    task_store_factory: Callable[[Path], TaskPublicationStore] = (
        TaskPublicationStore.for_repo
    ),
) -> _PublishedReportResult:
    """Validate, durably publish, and stage one exact Lane V report."""

    root = _require_repository(Path(repo_root))
    sent_fd = _open_sent_directory(root)
    candidate: _CapturedCandidate | None = None
    publication_owns_candidate = False
    preserve_unowned_candidate = False

    def set_candidate_ownership(owned: bool) -> None:
        nonlocal publication_owns_candidate
        publication_owns_candidate = owned

    try:
        candidate = _capture_candidate(root, Path(candidate_path), sent_fd)
        report = parse_lane_v_report(final_relative, candidate.raw)
        if report.relative_path != final_relative:
            _fail("invalid_publication_path", "final report path is not canonical")
        _live_report_shape(report)
        backend = _publication_backend(report.fields["Verification mode"])
        authority = validate_structural_authority(root, report)
        with _SanitizedGit(root) as git:
            try:
                if backend == _RECEIPT_BACKEND:
                    store = receipt_store_factory(root)
                    with store.lock_receipt(
                        report.fields["Opus receipt ID"], blocking=True
                    ) as attempt:
                        record = attempt.load_existing()
                        _validate_codex_record(root, report, authority, record)
                        preserve_unowned_candidate = _candidate_is_stored(record, candidate)
                        try:
                            published = _locked_publish_new(
                                attempt=attempt,
                                record=record,
                                root=root,
                                final_relative=final_relative,
                                candidate=candidate,
                                sent_fd=sent_fd,
                                git=git,
                                set_candidate_ownership=set_candidate_ownership,
                            )
                            return _PublishedReportResult(
                                path=published,
                                receipt_id=record.receipt_id,
                                task_id=None,
                            )
                        except BaseException as exc:
                            observed = attempt.load_existing()
                            resume_instruction = _publication_cli_command(
                                root, "resume", receipt_id=record.receipt_id
                            )
                            if record.state == "publishing":
                                if isinstance(exc, ReportGateError):
                                    raise ReportGateError(
                                        exc.reason,
                                        f"{exc.detail}; run: {resume_instruction}",
                                    ) from exc
                                raise
                            if observed.state == "publishing":
                                raise ReportGateError(
                                    "publication_resumable",
                                    f"publication interrupted; run: {resume_instruction}",
                                ) from exc
                            if observed.state == "published":
                                status_instruction = _publication_cli_command(
                                    root, "status", receipt_id=record.receipt_id
                                )
                                raise ReportGateError(
                                    "publication_status_required",
                                    "publication is already published; "
                                    f"run: {status_instruction}",
                                ) from exc
                            raise
                store = task_store_factory(root)
                authority_digest = _task_authority_digest(root, report, authority)
                with store.lock_task(
                    authority.descriptor.task_id, blocking=True
                ) as task:
                    record = task.load_or_create(authority_digest)
                    _validate_non_codex_record(record, authority_digest)
                    preserve_unowned_candidate = _candidate_is_stored(record, candidate)
                    try:
                        published = _locked_publish_new(
                            attempt=task,
                            record=record,
                            root=root,
                            final_relative=final_relative,
                            candidate=candidate,
                            sent_fd=sent_fd,
                            git=git,
                            set_candidate_ownership=set_candidate_ownership,
                        )
                        return _PublishedReportResult(
                            path=published,
                            receipt_id=None,
                            task_id=record.task_id,
                        )
                    except BaseException as exc:
                        observed = task.load_existing()
                        resume_instruction = _publication_cli_command(
                            root, "resume", task_id=record.task_id
                        )
                        if record.state == "publishing":
                            if isinstance(exc, ReportGateError):
                                raise ReportGateError(
                                    exc.reason,
                                    f"{exc.detail}; run: {resume_instruction}",
                                ) from exc
                            raise
                        if observed.state == "publishing":
                            raise ReportGateError(
                                "publication_resumable",
                                f"publication interrupted; run: {resume_instruction}",
                            ) from exc
                        if observed.state == "published":
                            status_instruction = _publication_cli_command(
                                root, "status", task_id=record.task_id
                            )
                            raise ReportGateError(
                                "publication_status_required",
                                "publication is already published; "
                                f"run: {status_instruction}",
                            ) from exc
                        raise
            except ReportGateError:
                raise
            except Exception as exc:
                reason = getattr(exc, "reason", "publication_failed")
                raise ReportGateError("publication_failed", str(reason)) from exc
    except BaseException:
        if (
            candidate is not None
            and not publication_owns_candidate
            and not preserve_unowned_candidate
        ):
            _cleanup_unbound_candidate(candidate, sent_fd)
        raise
    finally:
        if candidate is not None:
            os.close(candidate.fd)
        os.close(sent_fd)


def publish_candidate(
    *,
    repo_root: str | os.PathLike[str],
    candidate_path: str | os.PathLike[str],
    final_relative: str,
    receipt_store_factory: Callable[[Path], receipts.ReceiptStore] = (
        receipts.ReceiptStore.for_repo
    ),
    task_store_factory: Callable[[Path], TaskPublicationStore] = (
        TaskPublicationStore.for_repo
    ),
) -> Path:
    """Validate, durably publish, and stage one exact Lane V report."""

    return _publish_candidate_result(
        repo_root=repo_root,
        candidate_path=candidate_path,
        final_relative=final_relative,
        receipt_store_factory=receipt_store_factory,
        task_store_factory=task_store_factory,
    ).path


def _candidate_is_stored(record: object, candidate: _CapturedCandidate) -> bool:
    """Match a captured file to the candidate fields of a valid stored witness."""

    if getattr(record, "state", None) != "publishing":
        return False
    witness = _stored_publication_witness(record)
    fields = _TASK_WITNESS_FIELDS[1:5]
    return tuple(witness[field] for field in fields) == (
        candidate.digest,
        candidate.name,
        candidate.device,
        candidate.inode,
    )


def _stored_publication_witness(record: object) -> dict[str, object]:
    publication = getattr(record, "publication", None)
    if isinstance(publication, Mapping):
        witness = dict(publication)
    else:
        witness = {field: getattr(record, field, None) for field in _TASK_WITNESS_FIELDS}
    if set(witness) != set(_TASK_WITNESS_FIELDS):
        _fail("invalid_publication_witness", "stored witness fields do not match")
    return _task_witness_from_values(*(witness[field] for field in _TASK_WITNESS_FIELDS))


def _open_stored_name(
    sent_fd: int,
    name: str,
    witness: Mapping[str, object],
    *,
    label: str,
) -> tuple[int, bytes, os.stat_result] | None:
    try:
        descriptor = os.open(name, _file_flags(), dir_fd=sent_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ReportGateError(
            "publication_recovery_mismatch", f"{label} cannot be opened"
        ) from exc
    try:
        raw, observed = _read_regular_file(
            descriptor,
            expected_device=int(witness["candidate_device"]),
            expected_inode=int(witness["candidate_inode"]),
            label=label,
        )
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        if digest != witness["candidate_digest"]:
            _fail("publication_recovery_mismatch", f"{label} digest changed")
        return descriptor, raw, observed
    except ReportGateError as exc:
        os.close(descriptor)
        raise ReportGateError(
            "publication_recovery_mismatch", f"{label} witness changed"
        ) from exc
    except BaseException:
        os.close(descriptor)
        raise


def _stored_name_exists(sent_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=sent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise ReportGateError(
            "publication_recovery_mismatch",
            "stored publication name could not be rechecked",
        ) from exc
    return True


def _resume_locked(
    *,
    attempt: object,
    record: object,
    root: Path,
    sent_fd: int,
    git: _SanitizedGit,
    validate_report: Callable[[LaneVReport, StructuralAuthority], None],
) -> Path:
    if getattr(record, "state", None) == "published":
        _fail("publication_already_published", "published state cannot be resumed")
    if getattr(record, "state", None) != "publishing":
        _fail("publication_not_resumable", "only publishing state may resume")
    witness = _stored_publication_witness(record)
    final_relative = str(witness["path"])
    final_name = PurePosixPath(final_relative).name
    candidate_name = str(witness["candidate_name"])
    if candidate_name == final_name:
        _fail("invalid_publication_witness", "candidate and final names must differ")

    final_opened = _open_stored_name(
        sent_fd, final_name, witness, label="stored final"
    )
    candidate_opened = _open_stored_name(
        sent_fd, candidate_name, witness, label="stored candidate"
    )
    try:
        if final_opened is None and candidate_opened is None:
            if _index_entry(git, final_relative) is not None:
                _fail(
                    "index_entry_conflict",
                    "absent file witnesses cannot clear while an index entry remains",
                )
            try:
                _publication_checkpoint("resume_before_absent_directory_fsync")
                os.fsync(sent_fd)
                _publication_checkpoint("resume_after_absent_directory_fsync")
            except OSError as exc:
                raise ReportGateError(
                    "publication_durability_failed",
                    "absent recovery directory fsync failed",
                ) from exc
            if _stored_name_exists(sent_fd, candidate_name) or _stored_name_exists(
                sent_fd, final_name
            ):
                _fail(
                    "publication_recovery_mismatch",
                    "stored publication name appeared before reservation clear",
                )
            if _index_entry(git, final_relative) is not None:
                _fail(
                    "index_entry_conflict",
                    "index entry appeared before reservation clear",
                )
            attempt.recover_publication(final_relative, None, None, None)
            _fail(
                "publication_witness_cleared",
                "both stored candidate and final were absent; reservation cleared",
            )

        source = final_opened or candidate_opened
        assert source is not None
        raw = source[1]
        if final_opened is not None and candidate_opened is not None:
            if final_opened[1] != candidate_opened[1]:
                _fail(
                    "publication_recovery_mismatch",
                    "stored candidate and final bytes differ",
                )
            if (
                final_opened[2].st_dev != candidate_opened[2].st_dev
                or final_opened[2].st_ino != candidate_opened[2].st_ino
            ):
                _fail(
                    "publication_recovery_mismatch",
                    "stored candidate and final are different inodes",
                )

        report = parse_lane_v_report(final_relative, raw)
        _live_report_shape(report)
        authority = validate_structural_authority(root, report)
        validate_report(report, authority)
        expected_oid = _expected_blob_oid(git, raw)
        if expected_oid != witness["index_blob_oid"]:
            _fail("blob_witness_mismatch", "stored object ID does not match bytes")

        if final_opened is None:
            assert candidate_opened is not None
            if candidate_opened[2].st_nlink != 1:
                _fail(
                    "publication_recovery_mismatch",
                    "candidate-only recovery requires one link",
                )
            try:
                _publication_checkpoint("resume_before_candidate_fsync")
                os.fsync(candidate_opened[0])
                _publication_checkpoint("resume_after_candidate_fsync")
                _publication_checkpoint("resume_before_link")
                _revalidate_candidate_basename(
                    sent_fd,
                    candidate_name,
                    raw=raw,
                    digest=str(witness["candidate_digest"]),
                    device=int(witness["candidate_device"]),
                    inode=int(witness["candidate_inode"]),
                    expected_nlink=1,
                )
                os.link(
                    candidate_name,
                    final_name,
                    src_dir_fd=sent_fd,
                    dst_dir_fd=sent_fd,
                    follow_symlinks=False,
                )
            except OSError as exc:
                raise ReportGateError(
                    "publication_recovery_failed", "could not restore final link"
                ) from exc
            _publication_checkpoint("resume_after_link")
            final_opened = _open_stored_name(
                sent_fd, final_name, witness, label="restored final"
            )
            assert final_opened is not None

        assert final_opened is not None
        attempt.recover_publication(
            final_relative,
            str(witness["candidate_digest"]),
            int(witness["candidate_device"]),
            int(witness["candidate_inode"]),
        )
        try:
            _publication_checkpoint("resume_before_final_fsync")
            os.fsync(final_opened[0])
            _publication_checkpoint("resume_after_final_file_fsync")
            _publication_checkpoint("resume_before_directory_fsync")
            os.fsync(sent_fd)
            _publication_checkpoint("resume_after_directory_fsync")
        except OSError as exc:
            raise ReportGateError(
                "publication_durability_failed", "recovered final fsync failed"
            ) from exc
        _publication_checkpoint("resume_after_final_fsync")

        _publication_checkpoint("resume_before_object_write")
        _write_blob(git, raw, expected_oid)
        _publication_checkpoint("resume_after_object_write")
        _publication_checkpoint("resume_before_index_update")
        _stage_or_verify_index(
            git,
            final_relative,
            expected_oid,
            allow_existing_exact=True,
        )
        _publication_checkpoint("resume_after_index_update")
        _publication_checkpoint("resume_before_stage_verification")
        if _index_entry(git, final_relative) != ("100644", expected_oid, 0):
            _fail("index_witness_mismatch", "resumed index entry changed")
        _verify_blob(
            git, raw, str(witness["candidate_digest"]), expected_oid
        )
        _publication_checkpoint("resume_before_final_revalidation")
        final_check = _open_stored_name(
            sent_fd, final_name, witness, label="revalidated final"
        )
        assert final_check is not None
        os.close(final_check[0])
        _publication_checkpoint("resume_after_final_revalidation")

        if candidate_opened is not None:
            current_candidate = os.fstat(candidate_opened[0])
            if current_candidate.st_nlink != 2:
                _fail(
                    "publication_recovery_mismatch",
                    "linked candidate must have exactly two names",
                )
            try:
                _publication_checkpoint("resume_before_candidate_unlink")
                _revalidate_candidate_basename(
                    sent_fd,
                    candidate_name,
                    raw=raw,
                    digest=str(witness["candidate_digest"]),
                    device=int(witness["candidate_device"]),
                    inode=int(witness["candidate_inode"]),
                    expected_nlink=2,
                )
                os.unlink(candidate_name, dir_fd=sent_fd)
                _publication_checkpoint("resume_after_candidate_unlink")
            except OSError as exc:
                raise ReportGateError(
                    "publication_cleanup_failed",
                    "recovered candidate could not be removed",
                ) from exc
        try:
            _publication_checkpoint("resume_before_cleanup_directory_fsync")
            os.fsync(sent_fd)
            _publication_checkpoint("resume_after_cleanup_directory_fsync")
        except OSError as exc:
            raise ReportGateError(
                "publication_durability_failed",
                "recovery cleanup directory fsync failed",
            ) from exc
        final_check = _open_stored_name(
            sent_fd, final_name, witness, label="completed final"
        )
        assert final_check is not None
        try:
            if final_check[2].st_nlink != 1:
                _fail(
                    "publication_recovery_mismatch",
                    "completed final must have one link",
                )
            _publication_checkpoint("resume_before_completed_final_fsync")
            os.fsync(final_check[0])
            _publication_checkpoint("resume_after_completed_final_fsync")
        finally:
            os.close(final_check[0])
        if _index_entry(git, final_relative) != ("100644", expected_oid, 0):
            _fail("index_witness_mismatch", "index changed before resumed finish")
        _verify_blob(git, raw, str(witness["candidate_digest"]), expected_oid)
        _publication_checkpoint("resume_before_index_fsync")
        _fsync_index(git)
        _publication_checkpoint("resume_after_index_fsync")
        _publication_checkpoint("resume_before_published")
        _last_pre_publish_guard(
            sent_fd=sent_fd,
            candidate_name=candidate_name,
            final_name=final_name,
            final_relative=final_relative,
            raw=raw,
            digest=str(witness["candidate_digest"]),
            device=int(witness["candidate_device"]),
            inode=int(witness["candidate_inode"]),
            expected_oid=expected_oid,
            git=git,
        )
        attempt.finish_publication(
            *(witness[field] for field in _TASK_WITNESS_FIELDS)
        )
        _publication_checkpoint("resume_after_published")
        return root / final_relative
    finally:
        if final_opened is not None:
            os.close(final_opened[0])
        if candidate_opened is not None:
            os.close(candidate_opened[0])


def resume_publication(
    *,
    repo_root: str | os.PathLike[str],
    receipt_id: str | None = None,
    task_id: str | None = None,
    receipt_store_factory: Callable[[Path], receipts.ReceiptStore] = (
        receipts.ReceiptStore.for_repo
    ),
    task_store_factory: Callable[[Path], TaskPublicationStore] = (
        TaskPublicationStore.for_repo
    ),
) -> Path:
    backend = _identifier_backend(
        receipt_id,
        task_id,
        reason="invalid_resume_identifier",
    )
    canonical_receipt_id = (
        _canonical_receipt_id(receipt_id) if receipt_id is not None else None
    )
    root = _require_repository(Path(repo_root))
    sent_fd = _open_sent_directory(root)
    try:
        with _SanitizedGit(root) as git:
            try:
                if backend == _RECEIPT_BACKEND:
                    assert canonical_receipt_id is not None
                    store = receipt_store_factory(root)
                    with store.lock_receipt(
                        canonical_receipt_id, blocking=True
                    ) as attempt:
                        record = attempt.load_existing()

                        def validate_codex(
                            report: LaneVReport, authority: StructuralAuthority
                        ) -> None:
                            if (
                                _publication_backend(
                                    report.fields["Verification mode"]
                                )
                                != _RECEIPT_BACKEND
                            ):
                                _fail(
                                    "receipt_mode_mismatch",
                                    "receipt resume requires Codex mode",
                                )
                            _validate_codex_record(root, report, authority, record)

                        try:
                            return _resume_locked(
                                attempt=attempt,
                                record=record,
                                root=root,
                                sent_fd=sent_fd,
                                git=git,
                                validate_report=validate_codex,
                            )
                        except BaseException as exc:
                            observed = attempt.load_existing()
                            if record.state != "published" and observed.state == "published":
                                status_instruction = _publication_cli_command(
                                    root,
                                    "status",
                                    receipt_id=canonical_receipt_id,
                                )
                                raise ReportGateError(
                                    "publication_status_required",
                                    "publication completed before interruption; "
                                    f"run: {status_instruction}",
                                ) from exc
                            raise
                assert task_id is not None
                store = task_store_factory(root)
                with store.lock_task(task_id, blocking=True) as task:
                    record = task.load_existing()

                    def validate_task(
                        report: LaneVReport, authority: StructuralAuthority
                    ) -> None:
                        if (
                            _publication_backend(report.fields["Verification mode"])
                            != _TASK_BACKEND
                        ):
                            _fail(
                                "task_mode_mismatch",
                                "task resume requires non-Codex mode",
                            )
                        digest = _task_authority_digest(root, report, authority)
                        _validate_non_codex_record(record, digest)

                    try:
                        return _resume_locked(
                            attempt=task,
                            record=record,
                            root=root,
                            sent_fd=sent_fd,
                            git=git,
                            validate_report=validate_task,
                        )
                    except BaseException as exc:
                        observed = task.load_existing()
                        if record.state != "published" and observed.state == "published":
                            status_instruction = _publication_cli_command(
                                root, "status", task_id=task_id
                            )
                            raise ReportGateError(
                                "publication_status_required",
                                "publication completed before interruption; "
                                f"run: {status_instruction}",
                            ) from exc
                        raise
            except ReportGateError:
                raise
            except Exception as exc:
                reason = getattr(exc, "reason", "publication_resume_failed")
                raise ReportGateError("publication_resume_failed", str(reason)) from exc
    finally:
        os.close(sent_fd)


def _status_locked(
    *,
    record: object,
    sent_fd: int | None,
    git: _SanitizedGit,
) -> dict[str, object]:
    state = getattr(record, "state", None)
    if state in {"ready", "reconciled"}:
        return {
            "state": state,
            "path": None,
            "file_witness_match": False,
            "index_blob_oid": None,
            "staged_blob_match": False,
        }
    if state not in {"publishing", "published"}:
        _fail("invalid_publication_state", "stored publication state is invalid")
    if sent_fd is None:
        _fail("invalid_mailbox_directory", "publication state requires sent directory")
    witness = _stored_publication_witness(record)
    path = str(witness["path"])
    final_name = PurePosixPath(path).name
    candidate_name = str(witness["candidate_name"])
    final_opened = _open_stored_name(
        sent_fd, final_name, witness, label="status final"
    )
    candidate_opened = _open_stored_name(
        sent_fd, candidate_name, witness, label="status candidate"
    )
    try:
        file_match = final_opened is not None
        if state == "published" and (
            candidate_opened is not None
            or final_opened is None
            or final_opened[2].st_nlink != 1
        ):
            _fail(
                "published_witness_divergence",
                "published state requires one final name and no candidate name",
            )
        existing = _index_entry(git, path)
        expected_index = (
            str(witness["index_mode"]),
            str(witness["index_blob_oid"]),
            int(witness["index_stage"]),
        )
        if existing is not None and existing != expected_index:
            _fail("index_witness_mismatch", "status found a divergent index entry")
        staged_blob_match = False
        if existing == expected_index:
            try:
                blob = git.run(
                    "cat-file",
                    "blob",
                    str(witness["index_blob_oid"]),
                    label="status blob verification",
                )
            except ReportGateError:
                if state == "published":
                    raise
            else:
                staged_blob_match = (
                    "sha256:" + hashlib.sha256(blob).hexdigest()
                    == witness["candidate_digest"]
                )
                if not staged_blob_match:
                    _fail("blob_witness_mismatch", "status found divergent blob bytes")
        if state == "published" and not (file_match and staged_blob_match):
            _fail(
                "published_witness_missing",
                "published state lacks its exact file/index/blob witness",
            )
        return {
            "state": state,
            "path": path,
            "file_witness_match": file_match,
            "index_blob_oid": witness["index_blob_oid"],
            "staged_blob_match": staged_blob_match,
        }
    finally:
        if final_opened is not None:
            os.close(final_opened[0])
        if candidate_opened is not None:
            os.close(candidate_opened[0])


def publication_status(
    *,
    repo_root: str | os.PathLike[str],
    receipt_id: str | None = None,
    task_id: str | None = None,
    receipt_store_factory: Callable[[Path], receipts.ReceiptStore] = (
        receipts.ReceiptStore.for_repo
    ),
    task_store_factory: Callable[[Path], TaskPublicationStore] = (
        TaskPublicationStore.for_repo
    ),
) -> dict[str, object]:
    backend = _identifier_backend(
        receipt_id,
        task_id,
        reason="invalid_status_identifier",
    )
    canonical_receipt_id = (
        _canonical_receipt_id(receipt_id) if receipt_id is not None else None
    )
    root = _require_repository(Path(repo_root))
    sent_fd: int | None = None
    try:
        with _SanitizedGit(root) as git:
            if backend == _RECEIPT_BACKEND:
                assert canonical_receipt_id is not None
                store = receipt_store_factory(root)
                with store.lock_receipt(
                    canonical_receipt_id, blocking=True
                ) as attempt:
                    record = attempt.load_existing()
                    if record.state in {"publishing", "published"}:
                        sent_fd = _open_sent_directory(root)
                    return _status_locked(
                        record=record, sent_fd=sent_fd, git=git
                    )
            assert task_id is not None
            store = task_store_factory(root)
            with store.lock_task(task_id, blocking=True) as task:
                record = task.load_existing()
                if record.state in {"publishing", "published"}:
                    sent_fd = _open_sent_directory(root)
                return _status_locked(
                    record=record, sent_fd=sent_fd, git=git
                )
    except ReportGateError:
        raise
    except Exception as exc:
        reason = getattr(exc, "reason", "publication_status_failed")
        raise ReportGateError("publication_status_failed", str(reason)) from exc
    finally:
        if sent_fd is not None:
            os.close(sent_fd)


def _identifier_arguments(parser: argparse.ArgumentParser) -> None:
    identifiers = parser.add_mutually_exclusive_group(required=True)
    identifiers.add_argument("--receipt-id")
    identifiers.add_argument("--task-id")


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="verification_report_gate.py")
    commands = parser.add_subparsers(dest="command", required=True)
    publish = commands.add_parser("publish")
    publish.add_argument("--repo-root", required=True)
    publish.add_argument("--candidate", required=True)
    publish.add_argument("--final-relative", required=True)
    resume = commands.add_parser("resume")
    resume.add_argument("--repo-root", required=True)
    _identifier_arguments(resume)
    status = commands.add_parser("status")
    status.add_argument("--repo-root", required=True)
    _identifier_arguments(status)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _argument_parser().parse_args(argv)
    status_instruction: str | None = None
    try:
        if arguments.command == "publish":
            root = _require_repository(Path(arguments.repo_root))
            result = _publish_candidate_result(
                repo_root=root,
                candidate_path=arguments.candidate,
                final_relative=arguments.final_relative,
            )
            published = result.path
            output = published.relative_to(root).as_posix()
            status_instruction = _publication_cli_command(
                root,
                "status",
                receipt_id=result.receipt_id,
                task_id=result.task_id,
            )
        elif arguments.command == "resume":
            root = _require_repository(Path(arguments.repo_root))
            status_instruction = _publication_cli_command(
                root,
                "status",
                receipt_id=arguments.receipt_id,
                task_id=arguments.task_id,
            )
            published = resume_publication(
                repo_root=root,
                receipt_id=arguments.receipt_id,
                task_id=arguments.task_id,
            )
            output = published.relative_to(root).as_posix()
        else:
            result = publication_status(
                repo_root=arguments.repo_root,
                receipt_id=arguments.receipt_id,
                task_id=arguments.task_id,
            )
            output = receipts.canonical_json_bytes(result).decode("utf-8")
    except ReportGateError as exc:
        print(f"verification-report-gate: {exc.reason}: {exc.detail}", file=sys.stderr)
        if exc.reason == "publication_resumable":
            return 5
        if exc.reason == "publication_status_required":
            return 6
        return 4
    try:
        _publication_checkpoint("before_stdout")
        print(output)
        _publication_checkpoint("after_stdout")
    except Exception:
        if status_instruction is None:
            raise
        print(
            "verification-report-gate: publication_status_required: "
            f"publication output was interrupted; run: {status_instruction}",
            file=sys.stderr,
        )
        return 6
    return 0


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


if __name__ == "__main__":
    raise SystemExit(main())
