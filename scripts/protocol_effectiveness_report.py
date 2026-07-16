#!/usr/bin/env python3
"""Read-only protocol effectiveness report for the four-seat process.

The command observes durable protocol evidence and emits a coordinator-facing
summary plus a structured JSON artifact. It never consumes mailbox cursors,
sends mailbox events, edits inventory, claims locks, or performs git writes.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from statistics import median
from typing import Any

INVENTORY_COLS = (
    "id",
    "subsystem",
    "file:line",
    "severity",
    "priority",
    "fail-mode",
    "repro",
    "xfail-pin",
    "lane-owner",
    "shared-lock",
    "wave",
    "status",
    "verifier",
    "notes",
)
CLASSIFICATIONS = {
    "verified_progress",
    "blocked_progress",
    "coordination_only",
    "no_op_evidence",
    "stale_or_conflicted",
    "unknown",
}
MAILBOX_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>[A-Za-z0-9_]+)-to-(?P<recipient>[A-Za-z0-9_]+)-"
    r"(?P<kind>.+)\.md$"
)
GO_RE = re.compile(r"\bGO\b|verification-report.*\bPASS\b", re.IGNORECASE | re.DOTALL)
VERDICT_RE = re.compile(r"^\s*(?:VERDICT|Verdict)\s*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
FAIL_RE = re.compile(r"\bFAIL\b|\bNO[- ]GO\b|\bBLOCKED\b|\bNITS\b", re.IGNORECASE)
NO_OP_RE = re.compile(r"\b(no[- ]op|idle|standby|no current work|correctly idle)\b", re.IGNORECASE)
STALE_RE = re.compile(r"\b(stale|conflict|contradict|drift|race|unread split)\b", re.IGNORECASE)
EVIDENCE_RE = re.compile(
    r"\b(passed|xfailed|verification-report|evidence|operator\d?\s+GO|Lane V GO|impl.?verifier)\b",
    re.IGNORECASE,
)
BASELINE_PROFILES = (
    "none",
    "verification_only",
    "coordination_only",
    "effect_only",
    "combined",
)
BASELINE_METRIC_STATUSES = {
    "measured",
    "not_observed",
    "not_applicable",
    "invalid",
}
BASELINE_STANDBY_PURPOSES = {
    "waiting",
    "observing",
    "utilization",
    "no_op_readiness",
}
BASELINE_REVIEW_IDENTITY = (
    "base",
    "head",
    "scope_digest",
    "question_digest",
)
BASELINE_KERNEL_MIRROR = {
    "epoch": 0,
    "writer": "v1",
    "authority": "declarative_only",
}
BASELINE_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
BASELINE_DIGESTED_IDENTITY_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}@sha256:[0-9a-f]{64}$"
)
BASELINE_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BASELINE_CONTRACT_SHA256 = "c75306c0d62f58fb08edd9df45fce4eec8c2c85be60bd4ae41fb0d52ba9fe3da"
BASELINE_PROTOCOL_ROOTS = ["coordination", ".codex/runtime", "logs"]
BASELINE_CLASS_RULES = {
    "coordination": {"protocol_overhead": True},
    "verification": {"protocol_overhead": True},
    "effect": {"protocol_overhead": True},
    "standby": {
        "protocol_overhead": True,
        "purposes": ["waiting", "observing", "utilization", "no_op_readiness"],
    },
    "telemetry": {"protocol_overhead": False},
}
BASELINE_DENOMINATOR = {
    "field": "accepted_result_digest",
    "identity": "unique_sha256",
}
BASELINE_RUN_KEYS = {
    "run_id",
    "profile",
    "ordinal",
    "host_identity",
    "clock_domain",
    "instrumentation_identity",
    "scenario_input_digest",
    "accepted_result_digest",
    "endpoints",
    "artifacts",
    "reviews",
}
BASELINE_TIME_ENDPOINTS = {"accepted_input", "first_tool_callback"}
BASELINE_ROUTE_ENDPOINTS = {"accepted_route", "published_go"}
BASELINE_POINT_KEYS = {"ns", "clock_domain"}


@dataclass(frozen=True)
class MailboxFilename:
    filename: str
    timestamp: str
    sender: str
    recipient: str
    kind: str
    parse_error: str | None = None


@dataclass(frozen=True)
class Classification:
    category: str
    source: str
    id: str
    reason: str
    confidence: str = "medium"
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class VerifiedBaselineProvenance:
    """Typed handoff from the trusted collector to the in-process reporter.

    This rejects serialized or malformed evidence. It is not a security
    boundary against arbitrary code already executing in the trusted parent
    process.
    """

    contract_digest: str
    observations_digest: str
    cohort_identity: tuple[tuple[str, str], ...]
    collector_identity: str
    source_head: str
    codex_identity: str
    run_record_digests: tuple[tuple[str, str], ...]


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_json_digest(value: object) -> str | None:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        return None
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _baseline_cohort_identity(
    contract: dict[str, object],
    observations: dict[str, object],
) -> tuple[tuple[str, object], ...]:
    return (
        ("benchmark_id", contract.get("benchmark_id")),
        ("host_identity", observations.get("host_identity")),
        ("clock_domain", observations.get("clock_domain")),
        ("instrumentation_identity", observations.get("instrumentation_identity")),
    )


def _verified_baseline_provenance_errors(
    provenance: object,
    contract: dict[str, object],
    observations: dict[str, object],
    raw_runs: list[object],
    evidence_kind: object,
) -> list[str]:
    if type(provenance) is not VerifiedBaselineProvenance:
        return ["operational completion requires an in-memory VerifiedBaselineProvenance"]

    errors: list[str] = []
    if evidence_kind != "runtime_trace":
        errors.append("verified provenance is valid only for runtime_trace evidence")

    contract_digest = _canonical_json_digest(contract)
    if contract_digest is None:
        errors.append("verified provenance contract is not canonical JSON")
    elif (
        not isinstance(provenance.contract_digest, str)
        or not BASELINE_DIGEST_RE.fullmatch(provenance.contract_digest)
        or provenance.contract_digest != contract_digest
    ):
        errors.append("verified provenance contract digest does not match")
    observations_digest = _canonical_json_digest(observations)
    if observations_digest is None:
        errors.append("verified provenance observations are not canonical JSON")
    elif (
        not isinstance(provenance.observations_digest, str)
        or not BASELINE_DIGEST_RE.fullmatch(provenance.observations_digest)
        or provenance.observations_digest != observations_digest
    ):
        errors.append("verified provenance observations digest does not match")

    expected_cohort = _baseline_cohort_identity(contract, observations)
    if provenance.cohort_identity != expected_cohort:
        errors.append("verified provenance cohort identity does not match")
    if (
        not isinstance(provenance.collector_identity, str)
        or not BASELINE_DIGESTED_IDENTITY_RE.fullmatch(provenance.collector_identity)
    ):
        errors.append("verified provenance collector identity must bind a sha256 digest")
    if not isinstance(provenance.source_head, str) or not BASELINE_GIT_SHA_RE.fullmatch(
        provenance.source_head
    ):
        errors.append("verified provenance source HEAD must be a full Git SHA")
    if (
        not isinstance(provenance.codex_identity, str)
        or not BASELINE_DIGESTED_IDENTITY_RE.fullmatch(provenance.codex_identity)
    ):
        errors.append("verified provenance Codex identity must bind a sha256 digest")

    records = provenance.run_record_digests
    if type(records) is not tuple or len(records) != 25:
        errors.append("verified provenance must contain exactly 25 run-record digests")

    record_ids: list[str] = []
    record_digests: list[str] = []
    if isinstance(records, tuple):
        for record in records:
            if type(record) is not tuple or len(record) != 2:
                errors.append("verified provenance run-record entry must be an identity/digest pair")
                continue
            run_id, digest = record
            if not _nonempty_string(run_id):
                errors.append("verified provenance has an invalid run identity")
            else:
                record_ids.append(run_id)
            if not isinstance(digest, str) or not BASELINE_DIGEST_RE.fullmatch(digest):
                errors.append("verified provenance has an invalid run-record digest")
            else:
                record_digests.append(digest)

    if len(record_ids) != len(set(record_ids)):
        errors.append("verified provenance has a duplicate run identity")
    if len(record_digests) != len(set(record_digests)):
        errors.append("verified provenance has a duplicate run-record digest")

    observed_run_ids = tuple(
        raw.get("run_id") if isinstance(raw, dict) else None for raw in raw_runs
    )
    if tuple(record_ids) != observed_run_ids:
        errors.append("verified provenance run identities differ from observations")
    return errors


def _canonical_relative_path(value: object) -> PurePosixPath | None:
    if not _nonempty_string(value):
        return None
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return None
    path = PurePosixPath(str(value))
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        return None
    return path


def _resolved_artifact_path(
    value: object,
    repository_root: Path,
    declared_roots: list[PurePosixPath],
) -> tuple[PurePosixPath, Path] | None:
    relative = _canonical_relative_path(value)
    if relative is None:
        return None
    matching_roots = [
        root for root in declared_roots if relative == root or relative.is_relative_to(root)
    ]
    if len(matching_roots) != 1:
        return None
    try:
        root = repository_root.resolve(strict=False)
        declared_root = (root / Path(*matching_roots[0].parts)).resolve(strict=False)
        candidate = (root / Path(*relative.parts)).resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None
    if (
        not declared_root.is_relative_to(root)
        or not candidate.is_relative_to(root)
        or not candidate.is_relative_to(declared_root)
    ):
        return None
    return relative, candidate


def _derived_artifact_class(path: PurePosixPath) -> str | None:
    parts = path.parts
    if parts and parts[0] == "logs":
        return "telemetry"
    if parts[:2] == ("coordination", "presence"):
        return "standby"
    if parts[:2] == (".codex", "runtime"):
        return "effect"
    if parts[:2] == ("coordination", "verification"):
        return "verification"
    if (
        parts[:2] == ("coordination", "mailbox")
        and path.name.endswith("-verification-report.md")
    ):
        return "verification"
    if parts and parts[0] == "coordination":
        return "coordination"
    return None


def _validate_baseline_contract(contract: object) -> list[str]:
    """Validate the fixed five-profile intake contract without side effects."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["baseline contract must be a JSON object"]
    canonical = json.dumps(
        contract, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != BASELINE_CONTRACT_SHA256:
        errors.append("contract content differs from the fixed Phase-1 v1 benchmark")
    if contract.get("schema_version") != "capability-first-five-profile-contract/v1":
        errors.append("unsupported baseline contract schema_version")
    if not _nonempty_string(contract.get("benchmark_id")):
        errors.append("benchmark_id must be a non-empty string")

    profiles = contract.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != len(BASELINE_PROFILES):
        errors.append("profiles must contain exactly the five fixed profiles")
    else:
        ids = [item.get("id") if isinstance(item, dict) else None for item in profiles]
        if tuple(ids) != BASELINE_PROFILES:
            errors.append("profile IDs or order differ from the fixed five-profile contract")
        digests: list[str] = []
        for item in profiles:
            if not isinstance(item, dict):
                continue
            profile = item.get("id", "(unknown)")
            if item.get("ordinals") != [1, 2, 3, 4, 5]:
                errors.append(f"profile {profile} must declare ordinals 1 through 5")
            digest = item.get("scenario_input_digest")
            scenario_input = item.get("scenario_input")
            derived_digest = (
                "sha256:" + hashlib.sha256(scenario_input.encode("utf-8")).hexdigest()
                if isinstance(scenario_input, str)
                else None
            )
            if not isinstance(digest, str) or not BASELINE_DIGEST_RE.fullmatch(digest):
                errors.append(f"profile {profile} has an invalid scenario input digest")
            elif derived_digest != digest:
                errors.append(f"profile {profile} scenario input digest is not reproducible")
            else:
                digests.append(digest)
            expected_route = "applicable" if profile == "combined" else "not_applicable"
            if item.get("metrics") != {
                "time_to_first_tool": "applicable",
                "route_to_go": expected_route,
            }:
                errors.append(f"profile {profile} has an invalid metric applicability map")
        if len(set(digests)) != len(BASELINE_PROFILES):
            errors.append("scenario input digests must be unique per profile")

    roots = contract.get("protocol_roots")
    if roots != BASELINE_PROTOCOL_ROOTS:
        errors.append("protocol_roots differ from the fixed runtime roots")
    elif any(_canonical_relative_path(root) is None for root in roots):
        errors.append("protocol_roots must be canonical repository-relative paths")

    classes = contract.get("artifact_classes")
    if classes != BASELINE_CLASS_RULES:
        errors.append(
            "artifact class semantics differ from fixed overhead, standby, or telemetry rules"
        )

    if contract.get("review_identity_fields") != list(BASELINE_REVIEW_IDENTITY):
        errors.append("review identity fields differ from the exact four-field tuple")
    if contract.get("accepted_result_denominator") != BASELINE_DENOMINATOR:
        errors.append("accepted-result denominator must use unique accepted result digests")
    if contract.get("kernel_mirror") != BASELINE_KERNEL_MIRROR:
        errors.append("kernel mirror contract must remain epoch 0 / writer v1 / declarative_only")
    return errors


def _metric(status: str, value_ns: int | None = None) -> dict[str, object]:
    if status not in BASELINE_METRIC_STATUSES:
        raise ValueError(f"unknown metric status: {status}")
    return {"status": status, "value_ns": value_ns if status == "measured" else None}


def _duration_metric(
    endpoints: object,
    start_name: str,
    end_name: str,
    clock_domain: object,
) -> tuple[dict[str, object], list[str]]:
    if not isinstance(endpoints, dict):
        return _metric("invalid"), ["endpoints must be an object"]
    errors: list[str] = []
    for name in (start_name, end_name):
        if name not in endpoints:
            continue
        point = endpoints[name]
        if not isinstance(point, dict):
            errors.append(f"{name} must be a raw monotonic endpoint object")
            continue
        if set(point) != BASELINE_POINT_KEYS:
            errors.append(f"{name} must contain exactly ns and clock_domain")
            continue
        ns = point.get("ns")
        domain = point.get("clock_domain")
        if type(ns) is not int or ns < 0:
            errors.append(f"{name}.ns must be a non-negative integer")
        if not _nonempty_string(domain) or domain != clock_domain:
            errors.append(f"{name} is outside the declared monotonic clock domain")
    if errors:
        return _metric("invalid"), errors
    if start_name not in endpoints or end_name not in endpoints:
        return _metric("not_observed"), []
    start_ns = endpoints[start_name]["ns"]
    end_ns = endpoints[end_name]["ns"]
    if end_ns < start_ns:
        return _metric("invalid"), [f"{end_name} precedes {start_name}"]
    return _metric("measured", end_ns - start_ns), []


def _ratio_metric(numerator: int, denominator: int) -> dict[str, object]:
    if denominator < 0 or numerator < 0:
        return {
            "status": "invalid",
            "value": None,
            "numerator": numerator,
            "denominator": denominator,
        }
    if denominator == 0:
        return {
            "status": "not_observed",
            "value": None,
            "numerator": numerator,
            "denominator": denominator,
        }
    return {
        "status": "measured",
        "value": numerator / denominator,
        "numerator": numerator,
        "denominator": denominator,
    }


def _path_under_roots(path: PurePosixPath, roots: list[PurePosixPath]) -> bool:
    return any(path == root or path.is_relative_to(root) for root in roots)


def _aggregate_baseline(
    contract: object,
    observations: object,
    *,
    kernel_mirror: dict[str, object],
    allow_synthetic: bool = False,
    repository_root: Path | None = None,
    verified_provenance: VerifiedBaselineProvenance | None = None,
) -> dict[str, Any]:
    """Validate and aggregate supplied monotonic observations; never sample time."""
    contract_errors = _validate_baseline_contract(contract)
    contract_dict = contract if isinstance(contract, dict) else {}
    observation_dict = observations if isinstance(observations, dict) else {}
    raw_runs = observation_dict.get("runs", [])
    if not isinstance(raw_runs, list):
        raw_runs = []
        contract_errors.append("observation runs must be a list")
    evidence_kind = observation_dict.get("evidence_kind")
    root_path = repository_root or Path(__file__).resolve().parent.parent
    artifact: dict[str, Any] = {
        "artifact_kind": "capability-first-five-profile-baseline",
        "schema_version": "capability-first-five-profile-artifact/v1",
        "benchmark_id": contract_dict.get("benchmark_id"),
        "evidence_kind": evidence_kind,
        "host_identity": observation_dict.get("host_identity"),
        "clock_domain": observation_dict.get("clock_domain"),
        "instrumentation_identity": observation_dict.get("instrumentation_identity"),
        "contract": {
            key: contract_dict.get(key)
            for key in (
                "schema_version",
                "benchmark_id",
                "profiles",
                "protocol_roots",
                "artifact_classes",
                "review_identity_fields",
                "accepted_result_denominator",
            )
        },
        "kernel_mirror": {
            key: kernel_mirror.get(key) for key in ("epoch", "writer", "authority")
        },
        "status": "invalid",
        "complete": False,
        "structural_complete": False,
        "operational_complete": False,
        "operational_provenance": "not_observed",
        "errors": list(contract_errors),
        "raw_runs": raw_runs,
        "runs": [],
        "metrics": {},
    }
    if kernel_mirror != BASELINE_KERNEL_MIRROR:
        artifact["errors"].append(
            "runtime kernel mirror is not epoch 0 / writer v1 / declarative_only"
        )
    if observation_dict.get("schema_version") != "capability-first-baseline-observations/v1":
        artifact["errors"].append("unsupported observation schema_version")
    if evidence_kind not in {"runtime_trace", "synthetic_contract_fixture"}:
        artifact["errors"].append("unsupported evidence_kind")
    if evidence_kind == "synthetic_contract_fixture" and not allow_synthetic:
        artifact["errors"].append("synthetic_contract_fixture is test-call only")

    cohort_identity: dict[str, object] = {}
    for field in ("host_identity", "clock_domain", "instrumentation_identity"):
        value = observation_dict.get(field)
        cohort_identity[field] = value
        if not _nonempty_string(value):
            artifact["errors"].append(f"cohort {field} must be a non-empty string")

    if contract_errors:
        artifact["metrics"] = {
            "protocol_artifacts_per_accepted_result": _ratio_metric(0, 0),
        }
        return artifact

    profile_contracts = {
        item["id"]: item for item in contract_dict["profiles"]
    }
    roots = [PurePosixPath(root) for root in contract_dict["protocol_roots"]]
    class_rules = contract_dict["artifact_classes"]
    processed_runs: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    pairs: set[tuple[str, int]] = set()
    valid_accepted_results: set[str] = set()
    valid_reviews: list[tuple[str, str, str, str]] = []
    protocol_artifact_count = 0
    telemetry_artifact_count = 0
    artifact_class_counts = {name: 0 for name in BASELINE_CLASS_RULES}

    for index, raw in enumerate(raw_runs):
        run_errors: list[str] = []
        if not isinstance(raw, dict):
            artifact["errors"].append(f"run {index + 1} must be an object")
            processed_runs.append(
                {
                    "run_id": None,
                    "profile": None,
                    "ordinal": None,
                    "status": "invalid",
                    "complete": False,
                    "errors": ["run must be an object"],
                    "metrics": {
                        "time_to_first_tool": _metric("invalid"),
                        "route_to_go": _metric("invalid"),
                    },
                }
            )
            continue
        run_id = raw.get("run_id")
        profile = raw.get("profile")
        ordinal = raw.get("ordinal")
        run_keys_valid = set(raw) == BASELINE_RUN_KEYS
        if not run_keys_valid:
            missing = sorted(BASELINE_RUN_KEYS - set(raw))
            unknown = sorted(set(raw) - BASELINE_RUN_KEYS)
            run_errors.append(
                "run keys differ from contract"
                + (f"; missing={missing}" if missing else "")
                + (f"; unknown={unknown}" if unknown else "")
            )
        if not _nonempty_string(run_id):
            run_errors.append("run_id must be a non-empty string")
        elif run_id in run_ids:
            run_errors.append("duplicate run_id")
        else:
            run_ids.add(run_id)
        profile_contract = profile_contracts.get(profile) if isinstance(profile, str) else None
        if profile_contract is None:
            run_errors.append("unknown profile")
        if type(ordinal) is not int or ordinal not in {1, 2, 3, 4, 5}:
            run_errors.append("ordinal must be an integer from 1 through 5")
        elif profile_contract is not None:
            pair = (profile, ordinal)
            if pair in pairs:
                run_errors.append("duplicate profile/ordinal pair")
            else:
                pairs.add(pair)
        for field, expected in cohort_identity.items():
            if raw.get(field) != expected:
                run_errors.append(f"run {field} differs from cohort")
        if profile_contract is not None and raw.get("scenario_input_digest") != profile_contract[
            "scenario_input_digest"
        ]:
            run_errors.append("scenario input digest differs from contract")
        accepted_digest = raw.get("accepted_result_digest")
        if not isinstance(accepted_digest, str) or not BASELINE_DIGEST_RE.fullmatch(
            accepted_digest
        ):
            run_errors.append("accepted_result_digest must be a sha256 digest")

        endpoints = raw.get("endpoints", {})
        if isinstance(endpoints, dict):
            allowed_endpoints = set(BASELINE_TIME_ENDPOINTS)
            if profile == "combined":
                allowed_endpoints.update(BASELINE_ROUTE_ENDPOINTS)
            unknown_endpoints = sorted(set(endpoints) - allowed_endpoints)
            if unknown_endpoints:
                run_errors.append(f"unknown endpoint name(s): {unknown_endpoints}")
        time_metric, time_errors = _duration_metric(
            endpoints,
            "accepted_input",
            "first_tool_callback",
            cohort_identity["clock_domain"],
        )
        if not run_keys_valid:
            time_metric = _metric("invalid")
        run_errors.extend(time_errors)

        if profile == "combined":
            route_metric, route_errors = _duration_metric(
                endpoints,
                "accepted_route",
                "published_go",
                cohort_identity["clock_domain"],
            )
        else:
            route_metric, route_errors = _metric("not_applicable"), []
            if isinstance(endpoints, dict) and any(
                key in endpoints for key in ("accepted_route", "published_go")
            ):
                route_metric = _metric("invalid")
                route_errors.append("route endpoints are contradictory outside combined")
        if profile == "combined" and not run_keys_valid:
            route_metric = _metric("invalid")
        run_errors.extend(route_errors)

        artifacts = raw.get("artifacts")
        valid_artifacts: list[tuple[str, bool]] = []
        if not isinstance(artifacts, list):
            run_errors.append("artifacts must be a list")
        else:
            for entry in artifacts:
                if not isinstance(entry, dict):
                    run_errors.append("artifact manifest entry must be an object")
                    continue
                resolved = _resolved_artifact_path(entry.get("path"), root_path, roots)
                if resolved is None:
                    run_errors.append("artifact path is outside declared protocol roots")
                    continue
                path, resolved_path = resolved
                if not _path_under_roots(path, roots):
                    run_errors.append("artifact path is outside declared protocol roots")
                    continue
                derived_class = _derived_artifact_class(path)
                try:
                    resolved_relative = PurePosixPath(
                        resolved_path.relative_to(root_path.resolve(strict=False)).as_posix()
                    )
                except (OSError, ValueError):
                    run_errors.append("resolved artifact path is outside repository root")
                    continue
                resolved_class = _derived_artifact_class(resolved_relative)
                if derived_class is None or resolved_class is None:
                    run_errors.append("artifact path has no fixed class")
                    continue
                if derived_class != resolved_class:
                    run_errors.append("lexical and resolved artifact classes disagree")
                    continue
                required_keys = (
                    {"path", "class", "purpose"}
                    if derived_class == "standby"
                    else {"path", "class"}
                )
                if set(entry) != required_keys:
                    run_errors.append("artifact manifest keys differ from fixed class policy")
                    continue
                if entry.get("class") != derived_class:
                    run_errors.append("declared artifact class differs from fixed path policy")
                    continue
                purpose = entry.get("purpose")
                if derived_class == "standby" and (
                    not isinstance(purpose, str) or purpose not in BASELINE_STANDBY_PURPOSES
                ):
                    run_errors.append("standby artifact purpose is outside the narrow vocabulary")
                    continue
                valid_artifacts.append(
                    (derived_class, bool(class_rules[derived_class]["protocol_overhead"]))
                )

        reviews = raw.get("reviews")
        run_reviews: list[tuple[str, str, str, str]] = []
        if not isinstance(reviews, list):
            run_errors.append("reviews must be a list")
        else:
            for review in reviews:
                if not isinstance(review, dict):
                    run_errors.append("review lacks the exact four-field identity")
                    continue
                if not all(
                    isinstance(review.get(field), str)
                    and BASELINE_GIT_SHA_RE.fullmatch(review[field])
                    for field in ("base", "head")
                ) or not all(
                    isinstance(review.get(field), str)
                    and BASELINE_DIGEST_RE.fullmatch(review[field])
                    for field in ("scope_digest", "question_digest")
                ):
                    run_errors.append("review identity fields have invalid digest formats")
                    continue
                run_reviews.append(tuple(review[field] for field in BASELINE_REVIEW_IDENTITY))

        applicable_metrics = [time_metric]
        if profile == "combined":
            applicable_metrics.append(route_metric)
        complete = not run_errors and all(
            metric["status"] == "measured" for metric in applicable_metrics
        )
        run_status = "invalid" if run_errors else ("complete" if complete else "incomplete")
        processed = {
            "run_id": run_id,
            "profile": profile,
            "ordinal": ordinal,
            "status": run_status,
            "complete": complete,
            "errors": run_errors,
            "metrics": {
                "time_to_first_tool": time_metric,
                "route_to_go": route_metric,
            },
        }
        processed_runs.append(processed)
        if run_errors:
            artifact["errors"].extend(f"run {run_id or index + 1}: {err}" for err in run_errors)
            continue
        if isinstance(accepted_digest, str):
            valid_accepted_results.add(accepted_digest)
        valid_reviews.extend(run_reviews)
        protocol_artifact_count += sum(1 for _, overhead in valid_artifacts if overhead)
        telemetry_artifact_count += sum(1 for name, _ in valid_artifacts if name == "telemetry")
        for class_name, _ in valid_artifacts:
            artifact_class_counts[class_name] += 1

    artifact["runs"] = processed_runs
    expected_pairs = {
        (profile, ordinal) for profile in BASELINE_PROFILES for ordinal in range(1, 6)
    }
    time_values = [
        run["metrics"]["time_to_first_tool"]["value_ns"]
        for run in processed_runs
        if run["status"] != "invalid"
        and run["metrics"]["time_to_first_tool"]["status"] == "measured"
    ]
    route_values = [
        run["metrics"]["route_to_go"]["value_ns"]
        for run in processed_runs
        if run["status"] != "invalid"
        and run["metrics"]["route_to_go"]["status"] == "measured"
    ]
    by_profile: dict[str, dict[str, dict[str, object]]] = {}
    for profile in BASELINE_PROFILES:
        profile_runs = [
            run
            for run in processed_runs
            if run["profile"] == profile and run["status"] != "invalid"
        ]
        profile_time_values = [
            run["metrics"]["time_to_first_tool"]["value_ns"]
            for run in profile_runs
            if run["metrics"]["time_to_first_tool"]["status"] == "measured"
        ]
        profile_route_values = [
            run["metrics"]["route_to_go"]["value_ns"]
            for run in profile_runs
            if run["metrics"]["route_to_go"]["status"] == "measured"
        ]
        by_profile[profile] = {
            "time_to_first_tool": {
                "status": "measured" if profile_time_values else "not_observed",
                "median_ns": median(profile_time_values) if profile_time_values else None,
                "measured_count": len(profile_time_values),
            },
            "route_to_go": (
                {
                    "status": "measured" if profile_route_values else "not_observed",
                    "median_ns": median(profile_route_values) if profile_route_values else None,
                    "measured_count": len(profile_route_values),
                }
                if profile == "combined"
                else {
                    "status": "not_applicable",
                    "median_ns": None,
                    "measured_count": 0,
                }
            ),
        }
    review_counts: dict[tuple[str, str, str, str], int] = {}
    for identity in valid_reviews:
        review_counts[identity] = review_counts.get(identity, 0) + 1
    duplicate_reviews = sum(max(0, count - 1) for count in review_counts.values())
    artifact["metrics"] = {
        "time_to_first_tool": {
            "status": "measured" if time_values else "not_observed",
            "median_ns": median(time_values) if time_values else None,
            "measured_count": len(time_values),
        },
        "route_to_go": {
            "status": "measured" if route_values else "not_observed",
            "median_ns": median(route_values) if route_values else None,
            "measured_count": len(route_values),
        },
        "by_profile": by_profile,
        "accepted_result_count": len(valid_accepted_results),
        "protocol_artifact_count": protocol_artifact_count,
        "telemetry_artifact_count": telemetry_artifact_count,
        "artifact_class_counts": artifact_class_counts,
        "protocol_artifacts_per_accepted_result": _ratio_metric(
            protocol_artifact_count, len(valid_accepted_results)
        ),
        "exact_duplicate_review_count": duplicate_reviews,
        "review_identity_status": "measured",
    }

    structural_complete = (
        not artifact["errors"]
        and len(raw_runs) == 25
        and len(run_ids) == 25
        and pairs == expected_pairs
        and all(run["complete"] for run in processed_runs)
    )
    artifact["structural_complete"] = structural_complete
    provenance_errors: list[str] = []
    if verified_provenance is not None:
        if not structural_complete:
            provenance_errors.append(
                "verified provenance requires an error-free structurally complete cohort"
            )
        provenance_errors.extend(
            _verified_baseline_provenance_errors(
                verified_provenance,
                contract_dict,
                observation_dict,
                raw_runs,
                evidence_kind,
            )
        )
    artifact["errors"].extend(provenance_errors)

    operational_complete = (
        structural_complete
        and verified_provenance is not None
        and not provenance_errors
    )
    artifact["complete"] = operational_complete
    artifact["operational_complete"] = operational_complete
    if operational_complete:
        provenance = verified_provenance
        artifact["operational_provenance"] = {
            "kind": "verified_runtime_collector",
            "contract_digest": provenance.contract_digest,
            "observations_digest": provenance.observations_digest,
            "cohort_identity": dict(provenance.cohort_identity),
            "collector_identity": provenance.collector_identity,
            "source_head": provenance.source_head,
            "codex_identity": provenance.codex_identity,
            "run_record_digests": [
                {"run_id": run_id, "digest": digest}
                for run_id, digest in provenance.run_record_digests
            ],
        }
    artifact["status"] = (
        "complete"
        if operational_complete
        else ("invalid" if artifact["errors"] else "incomplete")
    )
    return artifact


def run(cmd: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
    """Run a command with the shared index, returning output without raising."""
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except Exception as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def repo_root() -> Path:
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"], Path.cwd())
    if code == 0 and out:
        return Path(out)
    return Path(__file__).resolve().parent.parent


def now_local() -> datetime:
    return datetime.now().astimezone()


def normalize_ts(ts: str) -> str:
    """Normalize ISO-ish mailbox timestamps to filename dash form."""
    return ts.strip().replace(":", "-")


def parse_mailbox_filename(filename: str) -> MailboxFilename:
    """Parse a mailbox event filename, failing closed on unexpected shape."""
    name = Path(filename).name
    match = MAILBOX_RE.match(name)
    if not match:
        return MailboxFilename(name, "", "", "", "unknown", "unparsable mailbox filename")
    return MailboxFilename(
        filename=name,
        timestamp=match.group("ts"),
        sender=match.group("sender"),
        recipient=match.group("recipient"),
        kind=match.group("kind"),
    )


def addressed_to(event: MailboxFilename, seat: str) -> bool:
    return event.recipient in (seat, "all")


def parse_mailbox_event(filename: str, text: str) -> Classification:
    """Classify one mailbox event from filename + body text."""
    from protocol_mailbox import COORDINATION_KINDS

    event = parse_mailbox_filename(filename)
    if event.parse_error:
        return Classification("unknown", "mailbox", event.filename, event.parse_error, "high")

    body = text or ""
    ident = event.filename
    details = {
        "timestamp": event.timestamp,
        "sender": event.sender,
        "recipient": event.recipient,
        "kind": event.kind,
    }
    if event.kind == "verification-report":
        verdict = verification_report_verdict(body)
        if verdict == "go":
            return Classification(
                "verified_progress",
                "mailbox",
                ident,
                "operator verification-report contains a GO/PASS signal",
                "high",
                details,
            )
        if verdict == "blocked":
            return Classification(
                "blocked_progress",
                "mailbox",
                ident,
                "verification-report contains FAIL/NITS/BLOCKED evidence",
                "high",
                details,
            )
        return Classification(
            "unknown",
            "mailbox",
            ident,
            "verification-report lacks an unambiguous GO or FAIL signal",
            "high",
            details,
        )
    if STALE_RE.search(body):
        return Classification(
            "stale_or_conflicted",
            "mailbox",
            ident,
            "event body reports stale, drift, conflict, race, or unread split evidence",
            "medium",
            details,
        )
    if event.kind == "verify-request":
        return Classification(
            "blocked_progress",
            "mailbox",
            ident,
            "verify-request indicates work is pending operator GO",
            "medium",
            details,
        )
    if event.kind == "status" and NO_OP_RE.search(body):
        return Classification(
            "no_op_evidence",
            "mailbox",
            ident,
            "status event reports no-op, idle, or standby evidence",
            "medium",
            details,
        )
    if NO_OP_RE.search(body):
        return Classification(
            "no_op_evidence",
            "mailbox",
            ident,
            "event body reports no-op, idle, or standby evidence",
            "low",
            details,
        )
    if event.kind in COORDINATION_KINDS or event.kind.startswith("verify-"):
        return Classification(
            "coordination_only",
            "mailbox",
            ident,
            f"mailbox kind '{event.kind}' is coordination/status evidence, not correctness proof",
            "medium",
            details,
        )
    return Classification(
        "unknown",
        "mailbox",
        ident,
        f"mailbox kind '{event.kind}' is not classified",
        "high",
        details,
    )


def verification_report_verdict(text: str) -> str:
    """Return go, blocked, or unknown for a verification-report body."""
    for match in VERDICT_RE.finditer(text or ""):
        value = match.group("value").strip().lower()
        if re.search(r"\b(no[- ]go|fail|blocked|nits)\b", value):
            return "blocked"
        if re.search(r"\b(go|pass)\b", value):
            return "go"
    if FAIL_RE.search(text or ""):
        return "blocked"
    if GO_RE.search(text or ""):
        return "go"
    return "unknown"


def parse_inventory_rows(text: str) -> tuple[list[dict[str, str]], list[str]]:
    """Parse remediation inventory Markdown rows with fail-closed errors."""
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells == list(INVENTORY_COLS) or set(cells[0] or "-") <= {"-"}:
            continue
        if len(cells) != len(INVENTORY_COLS):
            if len(cells) > 1:
                errors.append(f"line {lineno}: expected {len(INVENTORY_COLS)} cells, got {len(cells)}")
            continue
        row = dict(zip(INVENTORY_COLS, cells))
        if not row["id"] or row["id"] == "id":
            continue
        rows.append(row)
    return rows, errors


def classify_inventory_row(row: dict[str, str]) -> Classification:
    """Classify a row without treating status=verified alone as proof."""
    row_id = row.get("id", "(missing-id)")
    status = row.get("status", "").lower()
    verifier = row.get("verifier", "")
    notes = row.get("notes", "")
    evidence_text = f"{verifier}\n{notes}"
    details = {
        "wave": row.get("wave"),
        "status": row.get("status"),
        "severity": row.get("severity"),
        "lane_owner": row.get("lane-owner"),
    }

    if status == "verified":
        verdict = verification_report_verdict(evidence_text)
        if verdict == "blocked":
            return Classification(
                "blocked_progress",
                "inventory",
                row_id,
                "verified row includes NO-GO/FAIL/BLOCKED evidence",
                "high",
                details,
            )
        if verdict == "go" and EVIDENCE_RE.search(evidence_text):
            return Classification(
                "verified_progress",
                "inventory",
                row_id,
                "verified row includes operator GO and evidence signals",
                "medium",
                details,
            )
        return Classification(
            "unknown",
            "inventory",
            row_id,
            "status=verified without sufficient operator GO/evidence signal",
            "high",
            details,
        )
    if status in {"open", "fixing", "fixed", "provisional", "attested"}:
        reason = {
            "open": "row remains open",
            "fixing": "row is in-flight",
            "fixed": "row is fixed but missing operator GO",
            "provisional": "provisional row is not gate-clearable",
            "attested": "attested row needs explicit exemption before gate success",
        }.get(status, "row is not verified")
        return Classification("blocked_progress", "inventory", row_id, reason, "medium", details)
    return Classification(
        "unknown",
        "inventory",
        row_id,
        f"inventory status '{row.get('status', '')}' is unrecognized",
        "high",
        details,
    )


def parse_gate_output(stdout: str, stderr: str, exit_code: int) -> dict[str, Any]:
    """Parse scripts/wave_gate_check.py output into conservative counters."""
    text = "\n".join(part for part in (stdout, stderr) if part)
    report: dict[str, Any] = {
        "exit_code": exit_code,
        "verdict": "UNKNOWN",
        "counts": {},
        "gate_rows": None,
        "executable_selectors": None,
        "product_oracle_blockers": [],
        "pytest_exit": None,
        "pytest_command": "",
        "failed_tests": [],
        "parse_errors": [],
        "raw_tail": "\n".join(text.splitlines()[-40:]),
    }
    first = re.search(r"Wave\s+\d+\s+gate:\s+(?P<verdict>\w+)\s+counts=(?P<counts>\{.*?\})", text)
    if first:
        report["verdict"] = first.group("verdict")
        try:
            counts = ast.literal_eval(first.group("counts"))
            if isinstance(counts, dict):
                report["counts"] = counts
            else:
                report["parse_errors"].append("gate counts did not parse to a dict")
        except (SyntaxError, ValueError) as exc:
            report["parse_errors"].append(f"could not parse gate counts: {exc}")
    else:
        report["parse_errors"].append("could not parse gate verdict line")

    shape = re.search(r"gate rows:\s+(?P<rows>\d+);\s+executable selectors:\s+(?P<selectors>\d+)", text)
    if shape:
        report["gate_rows"] = int(shape.group("rows"))
        report["executable_selectors"] = int(shape.group("selectors"))
    for match in re.finditer(r"PRODUCT ORACLE BLOCKER:\s+(?P<msg>.+)", text):
        report["product_oracle_blockers"].append(match.group("msg").strip())
    pytest_match = re.search(r"PYTEST:\s+exit=(?P<exit>\d+)\s+command=(?P<command>.+)", text)
    if pytest_match:
        report["pytest_exit"] = int(pytest_match.group("exit"))
        report["pytest_command"] = pytest_match.group("command").strip()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("FAILED "):
            report["failed_tests"].append(stripped)
    return report


def classify_gate_report(report: dict[str, Any], wave: int) -> list[Classification]:
    classes: list[Classification] = []
    details = {
        "wave": wave,
        "exit_code": report.get("exit_code"),
        "verdict": report.get("verdict"),
    }
    if report.get("parse_errors"):
        for err in report["parse_errors"]:
            classes.append(Classification("unknown", "gate", f"wave-{wave}", err, "high", details))
    if report.get("product_oracle_blockers"):
        classes.append(
            Classification(
                "blocked_progress",
                "gate",
                f"wave-{wave}-product-oracle",
                "wave gate reports missing or invalid product-oracle artifact",
                "high",
                {"blockers": report["product_oracle_blockers"]},
            )
        )
    if report.get("pytest_exit") not in (None, 0):
        classes.append(
            Classification(
                "blocked_progress",
                "gate",
                f"wave-{wave}-pytest",
                "wave gate executable pin suite is still red",
                "high",
                {
                    "pytest_exit": report.get("pytest_exit"),
                    "failed_tests": report.get("failed_tests", [])[:20],
                },
            )
        )
    if report.get("verdict") == "MET":
        classes.append(
            Classification(
                "verified_progress",
                "gate",
                f"wave-{wave}",
                "wave gate reports MET; still requires protocol evidence for row-level claims",
                "medium",
                details,
            )
        )
    elif report.get("verdict") == "UNMET" and not classes:
        classes.append(
            Classification(
                "blocked_progress",
                "gate",
                f"wave-{wave}",
                "wave gate reports UNMET",
                "medium",
                details,
            )
        )
    return classes


def parse_commit(raw: str) -> dict[str, Any]:
    """Parse a NUL-separated git log line."""
    parts = raw.split("\x00")
    if len(parts) != 3:
        return {"hash": "", "timestamp": None, "subject": raw, "parse_error": "unparsable git log line"}
    short, epoch, subject = parts
    try:
        timestamp = datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat()
    except ValueError:
        timestamp = None
    return {"hash": short, "timestamp": timestamp, "subject": subject, "parse_error": None}


def classify_commit(commit: dict[str, Any]) -> Classification:
    subject = str(commit.get("subject", ""))
    ident = str(commit.get("hash") or subject or "(unknown-commit)")
    details = {"subject": subject, "timestamp": commit.get("timestamp")}
    if commit.get("parse_error"):
        return Classification("unknown", "git", ident, str(commit["parse_error"]), "high", details)
    lowered = subject.lower()
    if lowered.startswith("fix("):
        return Classification(
            "blocked_progress",
            "git",
            ident,
            "fix commit is attempted progress; row remains unproven until operator GO/gate evidence",
            "low",
            details,
        )
    if lowered.startswith("coord(verify)") or "verification-report" in lowered:
        return Classification(
            "coordination_only",
            "git",
            ident,
            "verification-related commit subject is coordination evidence, not operator GO proof",
            "medium",
            details,
        )
    if lowered.startswith("docs(handoff)") or "handoff" in lowered or lowered.startswith("coord("):
        return Classification(
            "coordination_only",
            "git",
            ident,
            "commit subject is handoff/coordination protocol movement",
            "medium",
            details,
        )
    if lowered.startswith("docs(spec)") or lowered.startswith("docs("):
        return Classification(
            "coordination_only",
            "git",
            ident,
            "documentation/spec commit is planning context, not verified row progress",
            "medium",
            details,
        )
    return Classification("unknown", "git", ident, "commit subject not classified", "low", details)


def mailbox_cursor_unread(
    seat: str,
    cursor: str,
    events: list[MailboxFilename],
    repo_root: Path | None = None,
) -> tuple[int, list[str]]:
    """Return unread count and filenames without mutating the cursor.

    For a migrated (scalar) cursor, unread lives on the signed ref-bus, not the legacy
    ISO filenames (the lexical `event.timestamp > cursor` compare mis-counts a scalar).
    With *repo_root* given, return the REAL ref-bus unread (count + descriptors) — ADR-062;
    without it (pure call) return (0, []), the legacy empty. A bus ERROR also yields (0, [])
    here: the report's authoritative 'reported_unread' (from status) carries the sentinel.
    """
    if cursor and cursor.strip().isdigit():
        if repo_root is None:
            return 0, []
        import bus_unread

        evs = bus_unread.bus_unread_events(repo_root, seat)
        if evs is None:
            return 0, []
        return len(evs), [bus_unread.format_unread(ev) for ev in evs]
    cursor_norm = normalize_ts(cursor)
    unread = [
        event.filename
        for event in events
        if not event.parse_error and addressed_to(event, seat) and event.timestamp > cursor_norm
    ]
    return len(unread), unread


def classify_seat_utilization(
    seat: str,
    unread_count: int,
    recent_sent: list[Classification],
    heartbeat_age_seconds: float | None,
) -> dict[str, Any]:
    """Conservatively classify one seat's current utilization from evidence."""
    seat_sent = [
        item
        for item in recent_sent
        if item.details and item.details.get("sender") == seat
    ]
    latest_category = seat_sent[-1].category if seat_sent else "unknown"
    if heartbeat_age_seconds is not None and heartbeat_age_seconds > 15 * 60:
        state = "stale"
    elif unread_count > 0:
        state = "unread"
    elif latest_category == "verified_progress":
        state = "verification"
    elif latest_category == "no_op_evidence":
        state = "no-op"
    elif latest_category == "coordination_only":
        state = "routing-only"
    else:
        state = "unknown"
    return {
        "seat": seat,
        "state": state,
        "unread": unread_count,
        "heartbeat_age_seconds": heartbeat_age_seconds,
        "latest_sent_category": latest_category,
    }


def classify_unknown(source: str, ident: str, reason: str) -> Classification:
    """Small pure helper for fail-closed unknown classifications."""
    return Classification("unknown", source, ident, reason, "high")


def safe_read(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except OSError as exc:
        return "", str(exc)


def recent_mailbox_events(root: Path, limit: int) -> list[tuple[MailboxFilename, str]]:
    sent = root / "coordination" / "mailbox" / "sent"
    if not sent.exists():
        return []
    paths = sorted(p for p in sent.glob("*.md") if p.is_file())[-limit:]
    out: list[tuple[MailboxFilename, str]] = []
    for path in paths:
        text, err = safe_read(path)
        parsed = parse_mailbox_filename(path.name)
        if err:
            parsed = MailboxFilename(path.name, "", "", "", "unknown", err)
        out.append((parsed, text))
    return out


def heartbeat_age(root: Path, seat: str, generated_at: datetime) -> float | None:
    path = root / "coordination" / "presence" / f"{seat}-heartbeat.ts"
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    except OSError:
        return None
    return max(0.0, (generated_at - mtime).total_seconds())


def collect_locks(root: Path) -> list[str]:
    lock_dir = root / "coordination" / "locks"
    if not lock_dir.exists():
        return []
    return sorted(p.name for p in lock_dir.glob("*") if p.is_file() and p.name != ".gitkeep")


def collect_handoff_drafts(root: Path) -> dict[str, Any]:
    committed_code, committed_out, _ = run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "docs"],
        root,
    )
    committed = [
        line
        for line in committed_out.splitlines()
        if Path(line).name.startswith("HANDOFF-") and line.endswith(".md")
    ] if committed_code == 0 else []
    status_code, status_out, _ = run(["git", "status", "--short", "--", "docs"], root)
    dirty = [
        line
        for line in status_out.splitlines()
        if "HANDOFF-" in line
    ] if status_code == 0 else []
    return {"committed_count": len(committed), "dirty": dirty}


def route_to_go_seconds(events: list[tuple[MailboxFilename, str]]) -> list[dict[str, Any]]:
    """Measure request/route to GO report latency where evidence is pairable."""
    requests: list[MailboxFilename] = []
    samples: list[dict[str, Any]] = []
    for event, text in events:
        if event.parse_error:
            continue
        if event.kind == "verify-request" or (
            event.sender == "coordinator" and event.kind == "coordination"
        ):
            requests.append(event)
            continue
        if event.kind != "verification-report" or verification_report_verdict(text) != "go":
            continue
        candidates = [
            req
            for req in requests
            if req.timestamp < event.timestamp
            and (req.recipient in (event.sender, "all") or req.sender == "coordinator")
        ]
        if not candidates:
            continue
        start = candidates[-1]
        start_dt = mailbox_ts_to_datetime(start.timestamp)
        end_dt = mailbox_ts_to_datetime(event.timestamp)
        if not start_dt or not end_dt:
            continue
        samples.append(
            {
                "request": start.filename,
                "report": event.filename,
                "seconds": int((end_dt - start_dt).total_seconds()),
            }
        )
    return samples


def mailbox_ts_to_datetime(ts: str) -> datetime | None:
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def category_counts(classifications: list[Classification]) -> dict[str, int]:
    counts = {name: 0 for name in sorted(CLASSIFICATIONS)}
    for item in classifications:
        counts[item.category] = counts.get(item.category, 0) + 1
    return counts


def blocked_reason_counts(classifications: list[Classification]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in classifications:
        reason = item.reason.lower()
        if item.category == "unknown":
            key = "parse error"
        elif "product-oracle" in reason or "product oracle" in reason:
            key = "product oracle"
        elif "pin" in reason or "pytest" in reason or "gate" in reason:
            key = "open pins"
        elif "missing operator go" in reason or "pending operator go" in reason:
            key = "missing GO"
        elif re.search(r"\block\b", reason):
            key = "lock"
        elif "push" in reason:
            key = "push"
        elif "spend" in reason:
            key = "spend"
        elif "unread split" in reason or "unread" in reason:
            key = "unread split"
        elif item.category == "blocked_progress":
            key = "blocked progress"
        else:
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts


def build_recommendations(metrics: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    recs: list[str] = []
    blocked = metrics.get("blocked_reason_counts", {})
    seat_states = {
        item["seat"]: item["state"]
        for item in metrics.get("seat_utilization", [])
    }
    if blocked.get("product oracle", 0) or gate.get("product_oracle_blockers"):
        recs.append("Route product-oracle artifact work before more status-only handoffs.")
    if blocked.get("open pins", 0):
        recs.append("Prioritize the red executable pin clusters before declaring gate movement.")
    if any(state == "unread" for state in seat_states.values()):
        recs.append("Resolve unread splits before claiming all seats received the latest route.")
    if metrics.get("duplicate_verification_reason_heuristic_count", 0):
        recs.append("Avoid another verification pass unless it states a genuinely new question.")
    if metrics.get("verified_rows_delta", 0) == 0 and metrics.get("mailbox_events_per_verified_row", 0):
        recs.append("Reduce coordination churn by routing one concrete blocker per active seat.")
    if not recs:
        recs.append("Use the latest verified blocker mix to build the next capacity board.")
    return recs


def duplicate_verification_count(classifications: list[Classification]) -> int:
    """Return only the legacy reason-text repetition heuristic, never exact identity."""
    reports: dict[str, int] = {}
    for item in classifications:
        if item.source != "mailbox" or not item.details:
            continue
        if item.details.get("kind") != "verification-report":
            continue
        text_key = item.reason
        reports[text_key] = reports.get(text_key, 0) + 1
    return sum(max(0, count - 1) for count in reports.values())


def collect_report(root: Path, wave: int, commit_limit: int, event_limit: int, gate_timeout: int) -> dict[str, Any]:
    from protocol_mailbox import SEATS
    from status import collect_mailbox

    generated = now_local()
    generated_at = generated.isoformat(timespec="seconds")
    code, head, _ = run(["git", "log", "-1", "--format=%h %s"], root)
    if code != 0 or not head:
        head = "(unknown)"

    mailbox_pairs = recent_mailbox_events(root, event_limit)
    mailbox_classifications = [
        parse_mailbox_event(event.filename, text) if not event.parse_error else classify_unknown("mailbox", event.filename, event.parse_error)
        for event, text in mailbox_pairs
    ]

    inventory_text, inventory_error = safe_read(root / "docs" / "REMEDIATION-INVENTORY.md")
    inventory_rows, inventory_errors = parse_inventory_rows(inventory_text) if not inventory_error else ([], [inventory_error])
    wave_rows = [row for row in inventory_rows if row.get("wave") == str(wave)]
    inventory_classifications = [classify_inventory_row(row) for row in wave_rows]
    inventory_classifications.extend(
        classify_unknown("inventory", f"parse-error-{idx}", err)
        for idx, err in enumerate(inventory_errors, start=1)
    )

    gate_code, gate_out, gate_err = run(
        [sys.executable, "scripts/wave_gate_check.py", str(wave)],
        root,
        timeout=gate_timeout,
    )
    gate = parse_gate_output(gate_out, gate_err, gate_code)
    gate["command"] = shlex.join([sys.executable, "scripts/wave_gate_check.py", str(wave)])
    gate_classifications = classify_gate_report(gate, wave)

    log_code, log_out, log_err = run(
        ["git", "log", f"-{commit_limit}", "--format=%h%x00%ct%x00%s"],
        root,
    )
    commits = [parse_commit(line) for line in log_out.splitlines()] if log_code == 0 else [
        {"hash": "", "timestamp": None, "subject": log_err or "git log failed", "parse_error": "git log failed"}
    ]
    commit_classifications = [classify_commit(commit) for commit in commits]

    classifications = (
        mailbox_classifications
        + inventory_classifications
        + gate_classifications
        + commit_classifications
    )
    counts = category_counts(classifications)
    verified_progress = max(
        0,
        sum(1 for item in inventory_classifications if item.category == "verified_progress"),
    )
    mailbox_event_count = len(mailbox_pairs)
    handoffs = collect_handoff_drafts(root)
    mailbox_data = collect_mailbox(root)
    parsed_events = [event for event, _ in mailbox_pairs]
    unread_splits: dict[str, Any] = {}
    seat_utilization: list[dict[str, Any]] = []
    for seat in SEATS:
        cursor = str(mailbox_data.get(f"mailbox_{seat}_cursor", ""))
        computed_unread, unread_names = mailbox_cursor_unread(seat, cursor, parsed_events, repo_root=root)
        reported_unread = mailbox_data.get(f"mailbox_{seat}_unread", computed_unread)
        unread_splits[seat] = {
            "cursor": cursor,
            "reported_unread": reported_unread,
            "sampled_unread": computed_unread,
            "sampled_unread_events": unread_names,
        }
        try:
            unread_count = int(reported_unread)
        except (TypeError, ValueError):
            unread_count = computed_unread
        seat_utilization.append(
            classify_seat_utilization(
                seat,
                unread_count,
                mailbox_classifications,
                heartbeat_age(root, seat, generated),
            )
        )

    route_samples = route_to_go_seconds(mailbox_pairs)
    avg_route_to_go = (
        sum(sample["seconds"] for sample in route_samples) / len(route_samples)
        if route_samples
        else None
    )
    blocked_counts = blocked_reason_counts(classifications)
    locks = collect_locks(root)
    if locks:
        blocked_counts["lock"] = blocked_counts.get("lock", 0) + len(locks)

    mailbox_ratio = _ratio_metric(mailbox_event_count, verified_progress)
    handoff_ratio = _ratio_metric(handoffs["committed_count"], verified_progress)
    reason_duplicate_heuristic = duplicate_verification_count(classifications)

    metrics: dict[str, Any] = {
        "verified_rows_delta": verified_progress,
        "wave_gate_blocker_delta": None,
        "route_to_go_seconds": route_samples,
        "route_to_go_seconds_avg": avg_route_to_go,
        "mailbox_events_per_verified_row": mailbox_ratio["value"],
        "mailbox_events_per_verified_row_status": mailbox_ratio["status"],
        "mailbox_events_per_verified_row_denominator": mailbox_ratio["denominator"],
        "handoff_commits_per_verified_row": handoff_ratio["value"],
        "handoff_commits_per_verified_row_status": handoff_ratio["status"],
        "handoff_commits_per_verified_row_denominator": handoff_ratio["denominator"],
        "seat_utilization": seat_utilization,
        "duplicate_verification_count": None,
        "duplicate_verification_count_status": "not_observed",
        "duplicate_verification_reason_heuristic_count": reason_duplicate_heuristic,
        "stale_claim_count": counts.get("stale_or_conflicted", 0),
        "blocked_reason_counts": blocked_counts,
        "classification_counts": counts,
        "unread_splits": unread_splits,
        "active_locks": locks,
        "handoffs": handoffs,
    }
    headline = (
        f"{verified_progress} Wave {wave} rows have operator-GO evidence in inventory sample; "
        f"{counts.get('coordination_only', 0)} coordination-only classifications; "
        f"Wave {wave} gate {gate.get('verdict', 'UNKNOWN')}."
    )
    summary = {
        "headline": headline,
        "gate_verdict": gate.get("verdict", "UNKNOWN"),
        "classification_counts": counts,
        "top_blockers": blocked_counts,
    }
    return {
        "artifact_kind": "protocol-effectiveness",
        "wave": wave,
        "generated_at": generated_at,
        "head": head,
        "summary": summary,
        "metrics": metrics,
        "classifications": [asdict(item) for item in classifications],
        "recommendations": build_recommendations(metrics, gate),
        "evidence": {
            "gate": gate,
            "recent_commits": commits,
            "mailbox_event_limit": event_limit,
            "inventory_rows_for_wave": len(wave_rows),
        },
    }


def artifact_path(root: Path, generated_at: str) -> Path:
    stamp = generated_at.replace(":", "-")
    return root / "logs" / f"protocol-effectiveness-{stamp}.json"


def write_artifact(path: Path, report: dict[str, Any]) -> None:
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded, encoding="utf-8")


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _strict_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON number: {value}")
    return parsed


def _read_json(path: Path) -> object:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
            parse_float=_strict_json_float,
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"{path}: could not parse JSON: {exc}") from exc


def _render_baseline_summary(artifact: dict[str, Any], output: Path) -> str:
    return "\n".join(
        [
            "# Capability-First Five-Profile Baseline",
            f"- status: {artifact['status']}",
            f"- evidence_kind: {artifact.get('evidence_kind')}",
            f"- runs: {len(artifact.get('raw_runs', []))}",
            f"- structural_complete: {artifact['structural_complete']}",
            f"- operational_complete: {artifact['operational_complete']}",
            f"- operational_provenance: {artifact['operational_provenance']}",
            "- exit 0: reserved; unavailable until trusted runtime provenance exists",
            f"- artifact: {output}",
        ]
    )


def render_summary(report: dict[str, Any], output: Path | None) -> str:
    summary = report["summary"]
    metrics = report["metrics"]
    lines = [
        "# Protocol Effectiveness Report",
        f"- wave: {report['wave']}",
        f"- generated_at: {report['generated_at']}",
        f"- head: {report['head']}",
        f"- artifact: {output if output else '(stdout-only; no artifact written)'}",
        f"- headline: {summary['headline']}",
        f"- blockers: {json.dumps(metrics['blocked_reason_counts'], sort_keys=True)}",
        "- seat utilization:",
    ]
    for seat in metrics["seat_utilization"]:
        lines.append(f"  - {seat['seat']}: {seat['state']} (unread={seat['unread']})")
    lines.append("- recommendations:")
    for rec in report["recommendations"]:
        lines.append(f"  - {rec}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a read-only protocol effectiveness report.",
        epilog=(
            "Baseline exit 0 is reserved and currently unavailable until trusted "
            "runtime provenance exists."
        ),
    )
    parser.add_argument("--wave", type=int, default=2)
    parser.add_argument("--commits", type=int, default=25)
    parser.add_argument("--mailbox-events", type=int, default=120)
    parser.add_argument("--gate-timeout", type=int, default=300)
    parser.add_argument(
        "--stdout-only",
        action="store_true",
        help="Print the Markdown summary without writing the JSON artifact.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON artifact path. Ignored when --stdout-only is set.",
    )
    parser.add_argument(
        "--baseline-contract",
        type=Path,
        help="Fixed five-profile baseline contract JSON.",
    )
    parser.add_argument(
        "--baseline-observations",
        type=Path,
        help=(
            "Runtime monotonic endpoint observations JSON; structural evidence only "
            "until a trusted provenance verifier exists."
        ),
    )
    args = parser.parse_args(argv)

    root = repo_root()
    baseline_mode = bool(args.baseline_contract or args.baseline_observations)
    if baseline_mode:
        if not args.baseline_contract or not args.baseline_observations or not args.output:
            print(
                "BASELINE — FAIL: --baseline-contract, --baseline-observations, "
                "and --output are all required",
                file=sys.stderr,
            )
            return 2
        if args.stdout_only:
            print("BASELINE — FAIL: --stdout-only is unavailable in baseline mode", file=sys.stderr)
            return 2
        try:
            contract = _read_json(args.baseline_contract)
            observations = _read_json(args.baseline_observations)
        except ValueError as exc:
            print(f"BASELINE — FAIL: {exc}", file=sys.stderr)
            return 2
        binding_error: str | None = None
        try:
            from target_binding import BindingError, load_kernel_mirror

            loaded_mirror = load_kernel_mirror(root)
            mirror = {
                "epoch": loaded_mirror.epoch,
                "writer": loaded_mirror.writer,
                "authority": loaded_mirror.authority,
            }
        except BindingError as exc:
            mirror = {"epoch": None, "writer": None, "authority": None}
            binding_error = str(exc)
        report = _aggregate_baseline(
            contract,
            observations,
            kernel_mirror=mirror,
            allow_synthetic=False,
            repository_root=root,
        )
        if binding_error:
            report["errors"].append(f"kernel mirror validation failed: {binding_error}")
            report["status"] = "invalid"
            report["complete"] = False
            report["operational_complete"] = False
        output = args.output if args.output.is_absolute() else root / args.output
        write_artifact(output, report)
        print(_render_baseline_summary(report, output))
        return {"complete": 0, "incomplete": 1, "invalid": 2}[report["status"]]

    report = collect_report(root, args.wave, args.commits, args.mailbox_events, args.gate_timeout)
    output: Path | None = None
    if not args.stdout_only:
        output = args.output if args.output else artifact_path(root, report["generated_at"])
        if not output.is_absolute():
            output = root / output
        write_artifact(output, report)
    print(render_summary(report, output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
