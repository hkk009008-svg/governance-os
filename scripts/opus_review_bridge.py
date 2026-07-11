#!/usr/bin/env python3
"""Blind Claude Opus review and deterministic Codex reconciliation."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


SCHEMA_VERSION = "opus-review/v1"
RECONCILIATION_SCHEMA_VERSION = "opus-reconciliation/v1"
VALID_STATUSES = frozenset({"pass", "issues", "unavailable"})
VALID_SEVERITIES = frozenset({"critical", "important", "minor"})
VALID_DISPOSITIONS = frozenset({"confirmed", "disproved", "unresolved"})
VALID_CODEX_VERDICTS = frozenset({"GO", "NITS", "FAIL"})
UNAVAILABLE_REASONS = frozenset(
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
    }
)
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ReviewContractError(ValueError):
    """A stable contract violation suitable for CLI error reporting."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


def _required_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewContractError("invalid_schema", f"{field} must be a non-empty string")
    return value.strip()


def _optional_string(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ReviewContractError("invalid_schema", f"{field} must be a string or null")
    return value


def _full_sha(value: object, field: str) -> str:
    text = _required_string(value, field).lower()
    if not _FULL_SHA_RE.fullmatch(text):
        raise ReviewContractError("invalid_schema", f"{field} must be a full 40-character SHA")
    return text


def is_opus_model(model: str | None) -> bool:
    if model is None:
        return False
    normalized = model.strip().lower()
    return normalized == "opus" or normalized.startswith("claude-opus-")


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    claim: str
    location: str | None
    evidence: str
    reproduction: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Finding":
        finding_id = _required_string(value.get("id"), "findings[].id")
        severity = _required_string(value.get("severity"), "findings[].severity").lower()
        if severity not in VALID_SEVERITIES:
            raise ReviewContractError(
                "invalid_schema",
                f"finding {finding_id} has unsupported severity {severity!r}",
            )
        return cls(
            id=finding_id,
            severity=severity,
            claim=_required_string(value.get("claim"), "findings[].claim"),
            location=_optional_string(value.get("location"), "findings[].location"),
            evidence=_required_string(value.get("evidence"), "findings[].evidence"),
            reproduction=_required_string(
                value.get("reproduction"), "findings[].reproduction"
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "severity": self.severity,
            "claim": self.claim,
            "location": self.location,
            "evidence": self.evidence,
            "reproduction": self.reproduction,
        }


@dataclass(frozen=True)
class OpusReview:
    reviewed_head: str
    reviewed_base: str | None
    effective_model: str | None
    status: str
    findings: tuple[Finding, ...]
    authorization_source: str
    unavailable_reason: str | None

    @classmethod
    def unavailable(
        cls,
        *,
        reviewed_head: str,
        reviewed_base: str | None,
        authorization_source: str,
        reason: str,
    ) -> "OpusReview":
        if reason not in UNAVAILABLE_REASONS:
            raise ReviewContractError("invalid_schema", f"unknown unavailable reason {reason!r}")
        return cls(
            reviewed_head=reviewed_head,
            reviewed_base=reviewed_base,
            effective_model=None,
            status="unavailable",
            findings=(),
            authorization_source=authorization_source,
            unavailable_reason=reason,
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "OpusReview":
        if value.get("schema_version") != SCHEMA_VERSION:
            raise ReviewContractError("invalid_schema", "unexpected schema_version")
        status = _required_string(value.get("status"), "status")
        if status == "unavailable":
            return cls.unavailable(
                reviewed_head=_full_sha(value.get("reviewed_head"), "reviewed_head"),
                reviewed_base=(
                    _full_sha(value.get("reviewed_base"), "reviewed_base")
                    if value.get("reviewed_base") is not None
                    else None
                ),
                authorization_source=_required_string(
                    value.get("authorization_source"), "authorization_source"
                ),
                reason=_required_string(value.get("unavailable_reason"), "unavailable_reason"),
            )
        return parse_structured_review(
            value,
            expected_head=_full_sha(value.get("reviewed_head"), "reviewed_head"),
            expected_base=(
                _full_sha(value.get("reviewed_base"), "reviewed_base")
                if value.get("reviewed_base") is not None
                else None
            ),
            effective_model=_required_string(value.get("effective_model"), "effective_model"),
            authorization_source=_required_string(
                value.get("authorization_source"), "authorization_source"
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "reviewed_head": self.reviewed_head,
            "reviewed_base": self.reviewed_base,
            "effective_model": self.effective_model,
            "status": self.status,
            "findings": [finding.to_dict() for finding in self.findings],
            "authorization_source": self.authorization_source,
            "unavailable_reason": self.unavailable_reason,
        }


def parse_structured_review(
    payload: Mapping[str, Any],
    *,
    expected_head: str,
    expected_base: str | None,
    effective_model: str,
    authorization_source: str,
) -> OpusReview:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ReviewContractError("invalid_schema", "unexpected schema_version")
    reviewed_head = _full_sha(payload.get("reviewed_head"), "reviewed_head")
    reviewed_base = (
        _full_sha(payload.get("reviewed_base"), "reviewed_base")
        if payload.get("reviewed_base") is not None
        else None
    )
    if reviewed_head != expected_head or reviewed_base != expected_base:
        raise ReviewContractError(
            "reviewed_scope_mismatch",
            f"expected {expected_base}..{expected_head}, got {reviewed_base}..{reviewed_head}",
        )
    status = _required_string(payload.get("status"), "status")
    if status not in {"pass", "issues"}:
        raise ReviewContractError("invalid_schema", "model status must be pass or issues")
    raw_findings = payload.get("findings")
    if not isinstance(raw_findings, list):
        raise ReviewContractError("invalid_schema", "findings must be a list")
    findings = tuple(
        Finding.from_mapping(item)
        for item in raw_findings
        if isinstance(item, Mapping)
    )
    if len(findings) != len(raw_findings):
        raise ReviewContractError("invalid_schema", "every finding must be an object")
    if len({finding.id for finding in findings}) != len(findings):
        raise ReviewContractError("invalid_schema", "finding ids must be unique")
    if status == "pass" and findings:
        raise ReviewContractError("invalid_schema", "pass requires zero findings")
    if status == "issues" and not findings:
        raise ReviewContractError("invalid_schema", "issues requires at least one finding")
    if not is_opus_model(effective_model):
        raise ReviewContractError("effective_model_not_opus", effective_model)
    return OpusReview(
        reviewed_head=reviewed_head,
        reviewed_base=reviewed_base,
        effective_model=effective_model,
        status=status,
        findings=findings,
        authorization_source=_required_string(authorization_source, "authorization_source"),
        unavailable_reason=None,
    )


@dataclass(frozen=True)
class FindingDisposition:
    finding_id: str
    disposition: str
    evidence: str


@dataclass(frozen=True)
class Reconciliation:
    codex_verdict: str
    go_allowed: bool
    blocking_finding_ids: tuple[str, ...]
    unresolved_finding_ids: tuple[str, ...]
    confirmed_fail_finding_ids: tuple[str, ...]
    confirmed_nits_finding_ids: tuple[str, ...]
    disproved_finding_ids: tuple[str, ...]
    degraded_cross_model_review: bool
    degraded_reason: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": RECONCILIATION_SCHEMA_VERSION,
            "codex_verdict": self.codex_verdict,
            "go_allowed": self.go_allowed,
            "blocking_finding_ids": list(self.blocking_finding_ids),
            "unresolved_finding_ids": list(self.unresolved_finding_ids),
            "confirmed_fail_finding_ids": list(self.confirmed_fail_finding_ids),
            "confirmed_nits_finding_ids": list(self.confirmed_nits_finding_ids),
            "disproved_finding_ids": list(self.disproved_finding_ids),
            "degraded_cross_model_review": self.degraded_cross_model_review,
            "degraded_reason": self.degraded_reason,
        }


def reconcile(
    codex_verdict: str,
    review: OpusReview,
    dispositions: Iterable[FindingDisposition],
) -> Reconciliation:
    verdict = codex_verdict.upper()
    if verdict not in VALID_CODEX_VERDICTS:
        raise ReviewContractError("invalid_codex_verdict", verdict)
    disposition_list = tuple(dispositions)
    if review.status != "issues" and disposition_list:
        raise ReviewContractError(
            "unexpected_dispositions", "pass and unavailable reviews have no findings"
        )
    if review.status == "unavailable":
        return Reconciliation(
            codex_verdict=verdict,
            go_allowed=verdict == "GO",
            blocking_finding_ids=(),
            unresolved_finding_ids=(),
            confirmed_fail_finding_ids=(),
            confirmed_nits_finding_ids=(),
            disproved_finding_ids=(),
            degraded_cross_model_review=True,
            degraded_reason=review.unavailable_reason,
        )
    if review.status == "pass":
        return Reconciliation(
            codex_verdict=verdict,
            go_allowed=verdict == "GO",
            blocking_finding_ids=(),
            unresolved_finding_ids=(),
            confirmed_fail_finding_ids=(),
            confirmed_nits_finding_ids=(),
            disproved_finding_ids=(),
            degraded_cross_model_review=False,
            degraded_reason=None,
        )

    expected_ids = {finding.id for finding in review.findings}
    by_id = {item.finding_id: item for item in disposition_list}
    if len(by_id) != len(disposition_list) or set(by_id) != expected_ids:
        raise ReviewContractError(
            "disposition_mismatch",
            f"expected dispositions for {sorted(expected_ids)}, got {sorted(by_id)}",
        )

    finding_by_id = {finding.id: finding for finding in review.findings}
    unresolved: list[str] = []
    confirmed_fail: list[str] = []
    confirmed_nits: list[str] = []
    disproved: list[str] = []
    for finding_id in sorted(expected_ids):
        disposition = by_id[finding_id]
        if disposition.disposition not in VALID_DISPOSITIONS:
            raise ReviewContractError(
                "invalid_disposition", f"{finding_id}: {disposition.disposition}"
            )
        if disposition.disposition == "disproved":
            if not disposition.evidence.strip():
                raise ReviewContractError("disproof_evidence_missing", finding_id)
            disproved.append(finding_id)
        elif disposition.disposition == "unresolved":
            unresolved.append(finding_id)
        elif finding_by_id[finding_id].severity in {"critical", "important"}:
            confirmed_fail.append(finding_id)
        else:
            confirmed_nits.append(finding_id)

    blocking = tuple(sorted(unresolved + confirmed_fail + confirmed_nits))
    return Reconciliation(
        codex_verdict=verdict,
        go_allowed=verdict == "GO" and not blocking,
        blocking_finding_ids=blocking,
        unresolved_finding_ids=tuple(unresolved),
        confirmed_fail_finding_ids=tuple(confirmed_fail),
        confirmed_nits_finding_ids=tuple(confirmed_nits),
        disproved_finding_ids=tuple(disproved),
        degraded_cross_model_review=False,
        degraded_reason=None,
    )
