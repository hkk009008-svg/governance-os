#!/usr/bin/env python3
"""Canonical scope contracts for receipt-backed Lane V review."""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


SCOPE_SCHEMA_VERSION = "lane-v-scope/v1"
RECEIPT_SCHEMA_VERSION = "opus-review-receipt/v1"
REVIEW_SCHEMA_VERSION = "opus-review/v3"
RECONCILIATION_SCHEMA_VERSION = "opus-reconciliation/v2"
CODEX_MODE = "codex-lane-v"
CODEX_HARNESS = "codex:lane-v-verifier"
CLAUDE_MODE = "claude-lane-v"
CLAUDE_HARNESS = "claude:lane-v-verifier"

_ATTEMPT_KEY_SCHEMA_VERSION = "opus-review-attempt-key/v1"
_DESCRIPTOR_MAX_BYTES = 65_536
_RECEIPT_MAX_BYTES = 1_048_576
_PATH_COLLECTION_MAX_ITEMS = 128
_COMMAND_COLLECTION_MAX_ITEMS = 32
_PATH_MAX_BYTES = 512
_COMMAND_MAX_BYTES = 4_096
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_RECEIPT_ID_RE = re.compile(r"^opr1:[0-9a-f]{64}$")
_QUESTION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_FORBIDDEN_COMMAND_CHARS = frozenset(";&|<>`$(){}\n\r\x00")
_VERIFICATION_COMMAND_PREFIX = ("env", "-u", "GIT_INDEX_FILE")
_DESCRIPTOR_FIELDS = frozenset(
    {
        "schema_version",
        "task_id",
        "question_id",
        "trigger_kind",
        "verification_mode",
        "verification_harness",
        "review_profile",
        "reviewed_base",
        "requirement_paths",
        "allowed_path_roots",
        "verification_commands",
    }
)
_REVIEWED_BASE_FIELDS = frozenset({"policy", "commit"})
_REQUIREMENT_FIELDS = frozenset({"path", "blob_id", "digest"})
_SUPPORTED_VERIFIERS = frozenset(
    {
        (CODEX_MODE, CODEX_HARNESS, CODEX_MODE),
        (CLAUDE_MODE, CLAUDE_HARNESS, CLAUDE_MODE),
    }
)
_CHANGED_STATUSES = frozenset({"A", "D", "M", "T", "U", "X"})
RECEIPT_STATES = ("reserved", "reviewed", "reconciled", "publishing", "published")
RESERVATION_ACTIONS = ("launch", "return", "degrade_uncertain")
_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "receipt_id",
        "attempt_key",
        "scope_digest",
        "scope",
        "state",
        "generation",
        "review",
        "reconciliation",
        "publication",
    }
)
_STATE_MINIMUM_GENERATION = {
    "reserved": 1,
    "reviewed": 2,
    "reconciled": 3,
    "publishing": 4,
    "published": 5,
}


class ReceiptContractError(ValueError):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


class ReceiptStateError(RuntimeError):
    """A fail-closed private receipt-store or lifecycle violation."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


def _duplicate_checked_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ReceiptContractError("duplicate_json_key", key)
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise ReceiptContractError("invalid_json", f"non-finite number {value!r}")


def _bounded_json_loads(
    raw: bytes, *, maximum_bytes: int, too_large_reason: str, label: str
) -> Any:
    if not isinstance(raw, bytes):
        raise ReceiptContractError("invalid_json", "input must be bytes")
    if len(raw) > maximum_bytes:
        raise ReceiptContractError(
            too_large_reason,
            f"{label} exceeds {maximum_bytes} bytes",
        )
    try:
        text = raw.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=_duplicate_checked_object,
            parse_constant=_reject_json_constant,
        )
    except ReceiptContractError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReceiptContractError("invalid_json", str(exc)) from exc


def strict_json_loads(raw: bytes) -> Any:
    """Decode bounded descriptor JSON while rejecting duplicate keys/constants."""

    return _bounded_json_loads(
        raw,
        maximum_bytes=_DESCRIPTOR_MAX_BYTES,
        too_large_reason="descriptor_too_large",
        label="descriptor",
    )


def _require_exact_fields(
    value: object, expected: frozenset[str], label: str
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected:
        actual = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        raise ReceiptContractError(
            "invalid_scope_descriptor",
            f"{label} fields must be {sorted(expected)!r}, got {actual!r}",
        )
    return value


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ReceiptContractError(
            "invalid_scope_descriptor", f"{label} must be a string"
        )
    return value


def _full_sha(value: object, label: str, *, reason: str) -> str:
    if not isinstance(value, str) or _FULL_SHA_RE.fullmatch(value) is None:
        raise ReceiptContractError(reason, f"{label} must be a lowercase full SHA")
    return value


def _sha256_text(value: object, label: str, *, reason: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ReceiptContractError(reason, f"{label} must be a canonical SHA-256")
    return value


def _canonical_receipt_id(value: object) -> str:
    if not isinstance(value, str) or _RECEIPT_ID_RE.fullmatch(value) is None:
        raise ReceiptContractError(
            "invalid_receipt_id",
            "receipt_id must be opr1 followed by 64 lowercase hex characters",
        )
    return value


def _canonical_uuid(value: object, *, reason: str) -> str:
    if not isinstance(value, str):
        raise ReceiptContractError(reason, "task_id must be canonical UUID text")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ReceiptContractError(reason, "task_id must be canonical UUID text") from exc
    if str(parsed) != value:
        raise ReceiptContractError(reason, "task_id must be canonical UUID text")
    return value


def _normalize_repo_path(value: object, *, reason: str) -> str:
    if not isinstance(value, str):
        raise ReceiptContractError(reason, "repository path must be a string")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ReceiptContractError(reason, "repository path must be valid UTF-8") from exc
    components = value.split("/")
    if (
        not value
        or len(encoded) > _PATH_MAX_BYTES
        or value.startswith("/")
        or value.endswith("/")
        or "\\" in value
        or "\x00" in value
        or any(character in value for character in "*?[]")
        or any(component in {"", ".", ".."} for component in components)
    ):
        raise ReceiptContractError(reason, f"invalid repository path: {value!r}")
    return value


def _normalized_paths(
    value: object,
    label: str,
    *,
    reason: str,
    require_json_list: bool,
) -> tuple[str, ...]:
    if require_json_list:
        valid_container = isinstance(value, list)
    else:
        valid_container = isinstance(value, (list, tuple))
    if not valid_container:
        raise ReceiptContractError(reason, f"{label} must be an array")
    items = list(value)
    normalized = tuple(
        sorted({_normalize_repo_path(item, reason=reason) for item in items})
    )
    if not 1 <= len(normalized) <= _PATH_COLLECTION_MAX_ITEMS:
        raise ReceiptContractError(
            reason,
            f"{label} must contain 1-{_PATH_COLLECTION_MAX_ITEMS} unique items",
        )
    return normalized


def _validated_command(value: object, *, reason: str) -> str:
    if not isinstance(value, str):
        raise ReceiptContractError(reason, "verification command must be a string")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ReceiptContractError(reason, "verification command must be valid UTF-8") from exc
    if (
        not value
        or value != value.strip()
        or len(encoded) > _COMMAND_MAX_BYTES
        or any(character in value for character in _FORBIDDEN_COMMAND_CHARS)
    ):
        raise ReceiptContractError(reason, f"invalid verification command: {value!r}")
    try:
        arguments = shlex.split(value)
    except ValueError as exc:
        raise ReceiptContractError(
            reason, f"invalid verification command: {value!r}"
        ) from exc
    if (
        len(arguments) < 5
        or tuple(arguments[:3]) != _VERIFICATION_COMMAND_PREFIX
        or any(any(character in token for character in "*?[]") for token in arguments)
    ):
        raise ReceiptContractError(reason, f"invalid verification command: {value!r}")
    return value


def _normalized_commands(
    value: object, *, reason: str, require_json_list: bool
) -> tuple[str, ...]:
    if require_json_list:
        valid_container = isinstance(value, list)
    else:
        valid_container = isinstance(value, (list, tuple))
    if not valid_container:
        raise ReceiptContractError(reason, "verification_commands must be an array")
    items = list(value)
    normalized = tuple(
        sorted({_validated_command(item, reason=reason) for item in items})
    )
    if not 1 <= len(normalized) <= _COMMAND_COLLECTION_MAX_ITEMS:
        raise ReceiptContractError(
            reason,
            "verification_commands must contain "
            f"1-{_COMMAND_COLLECTION_MAX_ITEMS} unique items",
        )
    return normalized


def _validated_verifier(
    mode: object, harness: object, profile: object, *, reason: str
) -> tuple[str, str, str]:
    if (
        not isinstance(mode, str)
        or not isinstance(harness, str)
        or not isinstance(profile, str)
    ):
        raise ReceiptContractError(
            reason,
            "verification mode, harness, and review profile must be strings",
        )
    values = (mode, harness, profile)
    if values not in _SUPPORTED_VERIFIERS:
        raise ReceiptContractError(
            reason,
            "unsupported verification mode, harness, and review profile",
        )
    return mode, harness, profile


@dataclass(frozen=True)
class ScopeDescriptor:
    task_id: str
    question_id: str
    trigger_kind: str
    verification_mode: str
    verification_harness: str
    review_profile: str
    base_policy: str
    base_commit: str
    requirement_paths: tuple[str, ...]
    allowed_path_roots: tuple[str, ...]
    verification_commands: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> ScopeDescriptor:
        reason = "invalid_scope_descriptor"
        mapping = _require_exact_fields(value, _DESCRIPTOR_FIELDS, "descriptor")
        if mapping["schema_version"] != SCOPE_SCHEMA_VERSION:
            raise ReceiptContractError(reason, "unexpected schema_version")
        task_id = _canonical_uuid(mapping["task_id"], reason=reason)
        question_id = _required_string(mapping["question_id"], "question_id")
        if _QUESTION_ID_RE.fullmatch(question_id) is None:
            raise ReceiptContractError(reason, "invalid question_id")
        trigger_kind = _required_string(mapping["trigger_kind"], "trigger_kind")
        if trigger_kind not in {"shipping-commit", "verify-request"}:
            raise ReceiptContractError(reason, "unsupported trigger_kind")
        mode, harness, profile = _validated_verifier(
            mapping["verification_mode"],
            mapping["verification_harness"],
            mapping["review_profile"],
            reason=reason,
        )
        reviewed_base = _require_exact_fields(
            mapping["reviewed_base"], _REVIEWED_BASE_FIELDS, "reviewed_base"
        )
        if reviewed_base["policy"] != "exact":
            raise ReceiptContractError(reason, "reviewed_base policy must be 'exact'")
        base_commit = _full_sha(
            reviewed_base["commit"], "reviewed_base.commit", reason=reason
        )
        return cls(
            task_id=task_id,
            question_id=question_id,
            trigger_kind=trigger_kind,
            verification_mode=mode,
            verification_harness=harness,
            review_profile=profile,
            base_policy="exact",
            base_commit=base_commit,
            requirement_paths=_normalized_paths(
                mapping["requirement_paths"],
                "requirement_paths",
                reason=reason,
                require_json_list=True,
            ),
            allowed_path_roots=_normalized_paths(
                mapping["allowed_path_roots"],
                "allowed_path_roots",
                reason=reason,
                require_json_list=True,
            ),
            verification_commands=_normalized_commands(
                mapping["verification_commands"],
                reason=reason,
                require_json_list=True,
            ),
        )


@dataclass(frozen=True)
class ScopeReference:
    descriptor_path: str
    descriptor_digest: str


@dataclass(frozen=True, order=True)
class ChangedPath:
    status: str
    path: str
    path_bytes: bytes = field(compare=False, repr=False)


@dataclass(frozen=True)
class ReviewScope:
    repository_identity: str
    task_id: str
    question_id: str
    trigger_kind: str
    trigger_identity: str
    trigger_commit: str
    trigger_path: str | None
    trigger_blob_id: str | None
    descriptor_path: str
    descriptor_digest: str
    descriptor_blob_id: str
    review_profile: str
    verification_mode: str
    verification_harness: str
    authorization_identity: str
    reviewed_head: str
    requested_base: str | None
    effective_base: str
    changed_paths: tuple[ChangedPath, ...]
    requirements: tuple[Mapping[str, str], ...]
    allowed_path_roots: tuple[str, ...]
    verification_commands: tuple[str, ...]

    def to_mapping(self) -> dict[str, object]:
        reason = "invalid_review_scope"
        repository_identity = _sha256_text(
            self.repository_identity, "repository_identity", reason=reason
        )
        task_id = _canonical_uuid(self.task_id, reason=reason)
        if _QUESTION_ID_RE.fullmatch(self.question_id) is None:
            raise ReceiptContractError(reason, "invalid question_id")
        mode, harness, profile = _validated_verifier(
            self.verification_mode,
            self.verification_harness,
            self.review_profile,
            reason=reason,
        )
        trigger_commit = _full_sha(
            self.trigger_commit, "trigger_commit", reason=reason
        )
        trigger_identity = canonical_trigger_identity(
            self.trigger_kind, trigger_commit, self.trigger_path
        )
        if trigger_identity != self.trigger_identity:
            raise ReceiptContractError(reason, "trigger_identity does not match trigger")
        if self.trigger_kind == "shipping-commit":
            if self.trigger_blob_id is not None:
                raise ReceiptContractError(reason, "shipping trigger cannot have blob id")
            trigger_blob_id = None
            trigger_path = None
        else:
            trigger_path = _normalize_repo_path(self.trigger_path, reason=reason)
            trigger_blob_id = _full_sha(
                self.trigger_blob_id, "trigger_blob_id", reason=reason
            )
        descriptor_path = _normalize_repo_path(self.descriptor_path, reason=reason)
        descriptor_digest = _sha256_text(
            self.descriptor_digest, "descriptor_digest", reason=reason
        )
        descriptor_blob_id = _full_sha(
            self.descriptor_blob_id, "descriptor_blob_id", reason=reason
        )
        if (
            not isinstance(self.authorization_identity, str)
            or not self.authorization_identity
            or len(self.authorization_identity.encode("utf-8")) > 256
            or any(character.isspace() for character in self.authorization_identity)
            or "\x00" in self.authorization_identity
        ):
            raise ReceiptContractError(reason, "invalid authorization_identity")
        reviewed_head = _full_sha(self.reviewed_head, "reviewed_head", reason=reason)
        requested_base = (
            _full_sha(self.requested_base, "requested_base", reason=reason)
            if self.requested_base is not None
            else None
        )
        effective_base = _full_sha(
            self.effective_base, "effective_base", reason=reason
        )
        changed_paths: set[ChangedPath] = set()
        for changed in self.changed_paths:
            if not isinstance(changed, ChangedPath) or changed.status not in _CHANGED_STATUSES:
                raise ReceiptContractError(reason, "invalid changed path entry")
            try:
                encoded_path = changed.path.encode("utf-8")
            except (AttributeError, UnicodeEncodeError) as exc:
                raise ReceiptContractError(reason, "invalid changed path text") from exc
            if (
                not changed.path
                or not isinstance(changed.path_bytes, bytes)
                or encoded_path != changed.path_bytes
            ):
                raise ReceiptContractError(reason, "changed path bytes do not match text")
            changed_paths.add(changed)
        requirements: set[tuple[str, str, str]] = set()
        for requirement in self.requirements:
            if not isinstance(requirement, Mapping) or set(requirement) != _REQUIREMENT_FIELDS:
                raise ReceiptContractError(reason, "invalid requirement entry")
            requirements.add(
                (
                    _normalize_repo_path(requirement["path"], reason=reason),
                    _full_sha(requirement["blob_id"], "requirement blob_id", reason=reason),
                    _sha256_text(requirement["digest"], "requirement digest", reason=reason),
                )
            )
        if not requirements:
            raise ReceiptContractError(reason, "requirements cannot be empty")
        allowed_path_roots = _normalized_paths(
            self.allowed_path_roots,
            "allowed_path_roots",
            reason=reason,
            require_json_list=False,
        )
        verification_commands = _normalized_commands(
            self.verification_commands,
            reason=reason,
            require_json_list=False,
        )
        return {
            "schema_version": SCOPE_SCHEMA_VERSION,
            "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
            "review_schema_version": REVIEW_SCHEMA_VERSION,
            "reconciliation_schema_version": RECONCILIATION_SCHEMA_VERSION,
            "repository_identity": repository_identity,
            "task_id": task_id,
            "question_id": self.question_id,
            "trigger_kind": self.trigger_kind,
            "trigger_identity": trigger_identity,
            "trigger_commit": trigger_commit,
            "trigger_path": trigger_path,
            "trigger_blob_id": trigger_blob_id,
            "descriptor_path": descriptor_path,
            "descriptor_digest": descriptor_digest,
            "descriptor_blob_id": descriptor_blob_id,
            "review_profile": profile,
            "verification_mode": mode,
            "verification_harness": harness,
            "authorization_identity": self.authorization_identity,
            "reviewed_head": reviewed_head,
            "requested_base": requested_base,
            "effective_base": effective_base,
            "changed_paths": [
                {"status": changed.status, "path": changed.path}
                for changed in sorted(changed_paths)
            ],
            "requirements": [
                {"path": path, "blob_id": blob_id, "digest": digest}
                for path, blob_id, digest in sorted(requirements)
            ],
            "allowed_path_roots": list(allowed_path_roots),
            "verification_commands": list(verification_commands),
        }


def parse_scope_reference(value: str) -> ScopeReference:
    reason = "invalid_scope_reference"
    if not isinstance(value, str):
        raise ReceiptContractError(reason, "scope reference must be a string")
    descriptor_path, separator, descriptor_digest = value.rpartition("@")
    if not separator:
        raise ReceiptContractError(reason, "scope reference must contain '@'")
    try:
        path = _normalize_repo_path(descriptor_path, reason=reason)
        digest = _sha256_text(descriptor_digest, "descriptor digest", reason=reason)
    except ReceiptContractError as exc:
        raise ReceiptContractError(reason, exc.detail) from exc
    return ScopeReference(path, digest)


def canonical_trigger_identity(
    trigger_kind: str, trigger_commit: str, trigger_path: str | None = None
) -> str:
    reason = "invalid_trigger_identity"
    commit = _full_sha(trigger_commit, "trigger commit", reason=reason)
    if trigger_kind == "shipping-commit" and trigger_path is None:
        return f"shipping-commit:{commit}"
    if trigger_kind == "verify-request" and trigger_path is not None:
        path = _normalize_repo_path(trigger_path, reason=reason)
        return f"verify-request:{commit}:{path}"
    raise ReceiptContractError(reason, "trigger kind/path combination is invalid")


def normalize_repo_path(value: str) -> str:
    """Validate a UTF-8 POSIX repository-relative authority path."""

    return _normalize_repo_path(value, reason="invalid_repo_path")


def parse_name_status_z(raw: bytes) -> tuple[ChangedPath, ...]:
    """Parse ``git diff --name-status -z --no-renames`` output exactly."""

    reason = "invalid_name_status"
    if not isinstance(raw, bytes):
        raise ReceiptContractError(reason, "name-status stream must be bytes")
    if raw == b"":
        return ()
    if not raw.endswith(b"\x00"):
        raise ReceiptContractError(reason, "name-status stream is truncated")
    fields = raw.split(b"\x00")[:-1]
    if not fields or len(fields) % 2:
        raise ReceiptContractError(reason, "name-status stream has incomplete records")
    changed_paths: list[ChangedPath] = []
    for index in range(0, len(fields), 2):
        status_bytes = fields[index]
        path_bytes = fields[index + 1]
        if len(status_bytes) != 1 or status_bytes not in {
            b"A",
            b"D",
            b"M",
            b"T",
            b"U",
            b"X",
        }:
            raise ReceiptContractError(reason, f"unsupported status {status_bytes!r}")
        if not path_bytes:
            raise ReceiptContractError(reason, "changed path cannot be empty")
        try:
            path = path_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ReceiptContractError(
                "unsupported_git_path_encoding", repr(path_bytes)
            ) from exc
        changed_paths.append(
            ChangedPath(status_bytes.decode("ascii"), path, path_bytes)
        )
    return tuple(changed_paths)


def assert_changed_path_coverage(
    changed_paths: Sequence[ChangedPath], allowed_path_roots: Sequence[str]
) -> None:
    """Require every changed path to match an allowed root by byte component."""

    if not changed_paths:
        raise ReceiptContractError(
            "empty_changed_paths", "Lane V scope must contain a changed path"
        )
    if isinstance(allowed_path_roots, (str, bytes)):
        raise ReceiptContractError(
            "invalid_repo_path", "allowed roots must be a collection"
        )
    roots = tuple(
        sorted(
            {
                normalize_repo_path(root).encode("utf-8")
                for root in allowed_path_roots
            }
        )
    )
    if not roots:
        raise ReceiptContractError(
            "invalid_repo_path", "allowed roots cannot be empty"
        )
    for changed in changed_paths:
        if (
            not isinstance(changed, ChangedPath)
            or changed.status not in _CHANGED_STATUSES
            or not isinstance(changed.path_bytes, bytes)
        ):
            raise ReceiptContractError(
                "invalid_name_status", "invalid changed path entry"
            )
        if not any(
            changed.path_bytes == root
            or changed.path_bytes.startswith(root + b"/")
            for root in roots
        ):
            raise ReceiptContractError(
                "changed_path_not_allowed",
                f"{changed.status} {changed.path!r} is outside allowed roots",
            )


def canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ReceiptContractError("invalid_canonical_json", str(exc)) from exc


def compute_attempt_key(scope: ReviewScope) -> str:
    mapping = {
        "schema_version": _ATTEMPT_KEY_SCHEMA_VERSION,
        "repository_identity": scope.repository_identity,
        "review_profile": scope.review_profile,
        "task_id": scope.task_id,
        "effective_base": scope.effective_base,
        "reviewed_head": scope.reviewed_head,
    }
    digest = hashlib.sha256(canonical_json_bytes(mapping)).hexdigest()
    return f"opr1:{digest}"


def compute_scope_digest(scope: ReviewScope) -> str:
    digest = hashlib.sha256(canonical_json_bytes(scope.to_mapping())).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True)
class ReceiptRecord:
    receipt_id: str
    attempt_key: str
    scope_digest: str
    scope: Mapping[str, Any]
    state: str
    generation: int
    review: Mapping[str, Any] | None
    reconciliation: Mapping[str, Any] | None
    publication: Mapping[str, Any] | None


@dataclass(frozen=True)
class ReservationDecision:
    action: str
    record: ReceiptRecord


def _state_error_from_contract(exc: ReceiptContractError) -> ReceiptStateError:
    return ReceiptStateError(exc.reason, exc.detail)


def _receipt_mapping(record: ReceiptRecord) -> dict[str, object]:
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_id": record.receipt_id,
        "attempt_key": record.attempt_key,
        "scope_digest": record.scope_digest,
        "scope": dict(record.scope),
        "state": record.state,
        "generation": record.generation,
        "review": dict(record.review) if record.review is not None else None,
        "reconciliation": (
            dict(record.reconciliation)
            if record.reconciliation is not None
            else None
        ),
        "publication": (
            dict(record.publication) if record.publication is not None else None
        ),
    }


def _canonical_receipt_bytes(record: ReceiptRecord) -> bytes:
    raw = canonical_json_bytes(_receipt_mapping(record))
    if len(raw) > _RECEIPT_MAX_BYTES:
        raise ReceiptStateError(
            "receipt_too_large",
            f"complete receipt exceeds {_RECEIPT_MAX_BYTES} bytes",
        )
    return raw


def _receipt_from_bytes(raw: bytes, expected_attempt_key: str) -> ReceiptRecord:
    try:
        value = _bounded_json_loads(
            raw,
            maximum_bytes=_RECEIPT_MAX_BYTES,
            too_large_reason="receipt_too_large",
            label="receipt",
        )
    except ReceiptContractError as exc:
        raise _state_error_from_contract(exc) from exc
    if not isinstance(value, Mapping) or set(value) != _RECEIPT_FIELDS:
        raise ReceiptStateError(
            "invalid_receipt_schema", "receipt fields do not match receipt schema"
        )
    if value["schema_version"] != RECEIPT_SCHEMA_VERSION:
        raise ReceiptStateError(
            "invalid_receipt_schema", "unexpected receipt schema version"
        )
    receipt_id = value["receipt_id"]
    attempt_key = value["attempt_key"]
    if receipt_id != expected_attempt_key or attempt_key != expected_attempt_key:
        raise ReceiptStateError(
            "receipt_attempt_key_mismatch",
            "receipt identity does not match the locked attempt",
        )
    scope = value["scope"]
    if not isinstance(scope, Mapping):
        raise ReceiptStateError("invalid_receipt_schema", "scope must be an object")
    scope_digest = value["scope_digest"]
    try:
        _sha256_text(scope_digest, "scope_digest", reason="invalid_receipt_schema")
        actual_scope_digest = "sha256:" + hashlib.sha256(
            canonical_json_bytes(scope)
        ).hexdigest()
    except ReceiptContractError as exc:
        raise _state_error_from_contract(exc) from exc
    if scope_digest != actual_scope_digest:
        raise ReceiptStateError(
            "receipt_scope_digest_mismatch", "scope digest does not match stored scope"
        )
    state = value["state"]
    generation = value["generation"]
    if state not in RECEIPT_STATES:
        raise ReceiptStateError("invalid_receipt_state", f"unsupported state {state!r}")
    if (
        isinstance(generation, bool)
        or not isinstance(generation, int)
        or generation < _STATE_MINIMUM_GENERATION[state]
    ):
        raise ReceiptStateError(
            "receipt_generation_rollback",
            f"generation {generation!r} is invalid for state {state!r}",
        )
    review = value["review"]
    reconciliation = value["reconciliation"]
    publication = value["publication"]
    if review is not None and not isinstance(review, Mapping):
        raise ReceiptStateError("invalid_receipt_schema", "review must be an object")
    if reconciliation is not None and not isinstance(reconciliation, Mapping):
        raise ReceiptStateError(
            "invalid_receipt_schema", "reconciliation must be an object"
        )
    if publication is not None and not isinstance(publication, Mapping):
        raise ReceiptStateError(
            "invalid_receipt_schema", "publication must be an object"
        )
    if state == "reserved" and any(
        item is not None for item in (review, reconciliation, publication)
    ):
        raise ReceiptStateError(
            "invalid_receipt_schema", "reserved receipt contains later-state data"
        )
    if state == "reviewed" and (
        review is None or reconciliation is not None or publication is not None
    ):
        raise ReceiptStateError(
            "invalid_receipt_schema", "reviewed receipt fields are inconsistent"
        )
    if state == "reconciled" and (
        review is None or reconciliation is None or publication is not None
    ):
        raise ReceiptStateError(
            "invalid_receipt_schema", "reconciled receipt fields are inconsistent"
        )
    if state in {"publishing", "published"} and any(
        item is None for item in (review, reconciliation, publication)
    ):
        raise ReceiptStateError(
            "invalid_receipt_schema", f"{state} receipt fields are inconsistent"
        )
    return ReceiptRecord(
        receipt_id=receipt_id,
        attempt_key=attempt_key,
        scope_digest=scope_digest,
        scope=dict(scope),
        state=state,
        generation=generation,
        review=dict(review) if review is not None else None,
        reconciliation=(
            dict(reconciliation) if reconciliation is not None else None
        ),
        publication=dict(publication) if publication is not None else None,
    )


def _private_directory_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _private_file_flags(base: int) -> int:
    return base | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def _ensure_private_directory(path: Path) -> int:
    missing: list[Path] = []
    cursor = path
    while True:
        try:
            os.lstat(cursor)
            break
        except FileNotFoundError:
            missing.append(cursor)
            if cursor.parent == cursor:
                raise ReceiptStateError(
                    "receipt_directory_missing", f"cannot create {path}"
                )
            cursor = cursor.parent
    for directory in reversed(missing):
        try:
            os.mkdir(directory, 0o700)
        except FileExistsError:
            pass
    try:
        directory_fd = os.open(path, _private_directory_flags())
    except OSError as exc:
        raise ReceiptStateError(
            "receipt_directory_open", f"cannot open private state directory: {exc}"
        ) from exc
    try:
        observed = os.fstat(directory_fd)
        if observed.st_uid != os.getuid():
            raise ReceiptStateError(
                "receipt_directory_owner", "state directory owner is not current uid"
            )
        if not stat.S_ISDIR(observed.st_mode):
            raise ReceiptStateError(
                "receipt_directory_type", "state root is not a directory"
            )
        if stat.S_IMODE(observed.st_mode) != 0o700:
            raise ReceiptStateError(
                "receipt_directory_mode", "state directory mode must be 0700"
            )
    except BaseException:
        os.close(directory_fd)
        raise
    return directory_fd


def _validate_private_file(
    fd: int,
    *,
    label: str,
    stat_fn: Callable[[int], os.stat_result],
) -> None:
    observed = stat_fn(fd)
    if observed.st_uid != os.getuid():
        raise ReceiptStateError(
            "receipt_file_owner", f"{label} owner is not current uid"
        )
    if not stat.S_ISREG(observed.st_mode):
        raise ReceiptStateError("receipt_file_type", f"{label} is not regular")
    if stat.S_IMODE(observed.st_mode) != 0o600:
        raise ReceiptStateError("receipt_file_mode", f"{label} mode must be 0600")
    if observed.st_nlink != 1:
        raise ReceiptStateError(
            "receipt_file_link_count", f"{label} must have exactly one link"
        )


def _write_all(fd: int, raw: bytes) -> None:
    offset = 0
    while offset < len(raw):
        written = os.write(fd, raw[offset:])
        if written <= 0:
            raise ReceiptStateError("receipt_write_failed", "short receipt write")
        offset += written


@dataclass(frozen=True)
class ReceiptStore:
    state_root: Path
    _stat_fn: Callable[[int], os.stat_result] = field(
        default=os.fstat, repr=False, compare=False
    )

    @classmethod
    def for_repo(
        cls,
        repo_root: str | os.PathLike[str],
        *,
        state_root: str | os.PathLike[str] | None = None,
        stat_fn: Callable[[int], os.stat_result] = os.fstat,
    ) -> ReceiptStore:
        if state_root is None:
            environment = {
                key: value
                for key, value in os.environ.items()
                if not key.startswith("GIT_")
            }
            git_common = subprocess.run(
                [
                    "git",
                    "--no-replace-objects",
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-common-dir",
                ],
                cwd=repo_root,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            primary_root = Path(git_common).resolve().parent
            root = primary_root / ".codex/runtime/opus-review-receipts/v1"
        else:
            root = Path(state_root).absolute()
        directory_fd = _ensure_private_directory(root)
        os.close(directory_fd)
        return cls(root, stat_fn)

    def lock_attempt(
        self, scope: ReviewScope, *, blocking: bool = True
    ) -> LockedAttempt:
        return LockedAttempt(self, compute_attempt_key(scope), blocking=blocking)

    def lock_receipt(
        self, receipt_id: str, *, blocking: bool = True
    ) -> LockedAttempt:
        return LockedAttempt(
            self, _canonical_receipt_id(receipt_id), blocking=blocking
        )


class LockedAttempt:
    def __init__(
        self, store: ReceiptStore, attempt_key: str, *, blocking: bool
    ) -> None:
        self._store = store
        self._attempt_key = _canonical_receipt_id(attempt_key)
        key_digest = self._attempt_key.removeprefix("opr1:")
        self._receipt_name = f"{key_digest}.json"
        self._lock_name = f"{key_digest}.lock"
        self._blocking = blocking
        self._directory_fd: int | None = None
        self._lock_fd: int | None = None
        self._current: ReceiptRecord | None = None

    def __enter__(self) -> LockedAttempt:
        if self._directory_fd is not None:
            raise ReceiptStateError("attempt_lock_reentry", "attempt lock is active")
        directory_fd = _ensure_private_directory(self._store.state_root)
        try:
            lock_fd = os.open(
                self._lock_name,
                _private_file_flags(os.O_CREAT | os.O_RDWR),
                0o600,
                dir_fd=directory_fd,
            )
            try:
                _validate_private_file(
                    lock_fd,
                    label="attempt lock",
                    stat_fn=self._store._stat_fn,
                )
                operation = fcntl.LOCK_EX
                if not self._blocking:
                    operation |= fcntl.LOCK_NB
                try:
                    fcntl.flock(lock_fd, operation)
                except OSError as exc:
                    if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK}:
                        raise ReceiptStateError(
                            "attempt_in_progress", "attempt lock is held"
                        ) from exc
                    raise
            except BaseException:
                os.close(lock_fd)
                raise
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
            raise ReceiptStateError("attempt_lock_required", "attempt lock is not held")
        return self._directory_fd

    def _read_receipt(self, *, allow_missing: bool = False) -> ReceiptRecord | None:
        directory_fd = self._require_locked()
        try:
            receipt_fd = os.open(
                self._receipt_name,
                _private_file_flags(os.O_RDONLY | os.O_NONBLOCK),
                dir_fd=directory_fd,
            )
        except FileNotFoundError:
            if allow_missing:
                return None
            raise ReceiptStateError("receipt_missing", "attempt receipt is missing")
        except OSError as exc:
            raise ReceiptStateError(
                "receipt_file_open", f"cannot open attempt receipt: {exc}"
            ) from exc
        try:
            _validate_private_file(
                receipt_fd,
                label="attempt receipt",
                stat_fn=self._store._stat_fn,
            )
            chunks: list[bytes] = []
            remaining = _RECEIPT_MAX_BYTES + 1
            while remaining:
                chunk = os.read(receipt_fd, min(65_536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            raw = b"".join(chunks)
            if len(raw) > _RECEIPT_MAX_BYTES:
                raise ReceiptStateError(
                    "receipt_too_large",
                    f"receipt exceeds {_RECEIPT_MAX_BYTES} bytes",
                )
        finally:
            os.close(receipt_fd)
        return _receipt_from_bytes(raw, self._attempt_key)

    def load_existing(self) -> ReceiptRecord:
        self._require_locked()
        current = self._read_receipt()
        assert current is not None
        self._current = current
        return current

    def _create_initial(self, record: ReceiptRecord) -> None:
        raw = _canonical_receipt_bytes(record)
        directory_fd = self._require_locked()
        receipt_fd: int | None = None
        file_durable = False
        try:
            receipt_fd = os.open(
                self._receipt_name,
                _private_file_flags(os.O_CREAT | os.O_EXCL | os.O_WRONLY),
                0o600,
                dir_fd=directory_fd,
            )
            _validate_private_file(
                receipt_fd,
                label="attempt receipt",
                stat_fn=self._store._stat_fn,
            )
            _write_all(receipt_fd, raw)
            os.fsync(receipt_fd)
            file_durable = True
        except BaseException:
            if not file_durable:
                try:
                    os.unlink(self._receipt_name, dir_fd=directory_fd)
                except FileNotFoundError:
                    pass
            raise
        finally:
            if receipt_fd is not None:
                os.close(receipt_fd)
        os.fsync(directory_fd)

    def _verified_current(self) -> ReceiptRecord:
        if self._current is None:
            raise ReceiptStateError(
                "attempt_not_loaded",
                "reserve_or_load or load_existing must run before a transition",
            )
        observed = self._read_receipt()
        assert observed is not None
        if observed.generation < self._current.generation:
            raise ReceiptStateError(
                "receipt_generation_rollback",
                "stored generation moved behind the locked generation",
            )
        if observed.generation != self._current.generation:
            raise ReceiptStateError(
                "receipt_generation_conflict",
                "stored generation changed during the locked transition",
            )
        if canonical_json_bytes(_receipt_mapping(observed)) != canonical_json_bytes(
            _receipt_mapping(self._current)
        ):
            raise ReceiptStateError(
                "receipt_state_conflict", "stored receipt changed without a generation"
            )
        return observed

    def _atomic_replace(self, record: ReceiptRecord) -> None:
        raw = _canonical_receipt_bytes(record)
        directory_fd = self._require_locked()
        temporary_name = f"{self._receipt_name}.tmp-{uuid.uuid4().hex}"
        temporary_fd: int | None = None
        try:
            temporary_fd = os.open(
                temporary_name,
                _private_file_flags(os.O_CREAT | os.O_EXCL | os.O_WRONLY),
                0o600,
                dir_fd=directory_fd,
            )
            _validate_private_file(
                temporary_fd,
                label="temporary receipt",
                stat_fn=self._store._stat_fn,
            )
            _write_all(temporary_fd, raw)
            os.fsync(temporary_fd)
            os.close(temporary_fd)
            temporary_fd = None
            os.replace(
                temporary_name,
                self._receipt_name,
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
            if isinstance(exc, ReceiptStateError):
                raise
            raise ReceiptStateError(
                "receipt_replace_failed", f"atomic receipt replacement failed: {exc}"
            ) from exc

    @staticmethod
    def _normalized_mapping(value: Mapping[str, Any], label: str) -> dict[str, Any]:
        if not isinstance(value, Mapping):
            raise ReceiptStateError(
                "invalid_receipt_transition", f"{label} must be an object"
            )
        try:
            normalized = _bounded_json_loads(
                canonical_json_bytes(value),
                maximum_bytes=_RECEIPT_MAX_BYTES,
                too_large_reason="receipt_too_large",
                label=label,
            )
        except ReceiptContractError as exc:
            raise _state_error_from_contract(exc) from exc
        if not isinstance(normalized, dict):
            raise ReceiptStateError(
                "invalid_receipt_transition", f"{label} must be an object"
            )
        return normalized

    def reserve_or_load(self, scope: ReviewScope) -> ReservationDecision:
        self._require_locked()
        if compute_attempt_key(scope) != self._attempt_key:
            raise ReceiptStateError(
                "attempt_scope_conflict", "scope belongs to a different attempt"
            )
        scope_mapping = scope.to_mapping()
        scope_digest = compute_scope_digest(scope)
        current = self._read_receipt(allow_missing=True)
        if current is None:
            record = ReceiptRecord(
                receipt_id=self._attempt_key,
                attempt_key=self._attempt_key,
                scope_digest=scope_digest,
                scope=scope_mapping,
                state="reserved",
                generation=1,
                review=None,
                reconciliation=None,
                publication=None,
            )
            self._create_initial(record)
            self._current = record
            return ReservationDecision("launch", record)
        if (
            current.scope_digest != scope_digest
            or canonical_json_bytes(current.scope) != canonical_json_bytes(scope_mapping)
        ):
            raise ReceiptStateError(
                "attempt_scope_conflict", "attempt already has a different scope"
            )
        self._current = current
        action = "degrade_uncertain" if current.state == "reserved" else "return"
        return ReservationDecision(action, current)

    def record_review(self, review: Mapping[str, Any]) -> ReceiptRecord:
        current = self._verified_current()
        if current.state != "reserved":
            raise ReceiptStateError(
                "invalid_receipt_transition",
                f"cannot record review from state {current.state!r}",
            )
        normalized_review = self._normalized_mapping(review, "review")
        updated = ReceiptRecord(
            receipt_id=current.receipt_id,
            attempt_key=current.attempt_key,
            scope_digest=current.scope_digest,
            scope=current.scope,
            state="reviewed",
            generation=current.generation + 1,
            review=normalized_review,
            reconciliation=None,
            publication=None,
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    @staticmethod
    def _validate_reconciliation_dispositions(
        review: Mapping[str, Any], input_mapping: Mapping[str, Any]
    ) -> None:
        status = review.get("status")
        dispositions = input_mapping.get("dispositions")
        if not isinstance(dispositions, Mapping):
            raise ReceiptStateError(
                "invalid_reconciliation_input", "dispositions must be an object"
            )
        if status in {"pass", "unavailable"}:
            if dispositions:
                raise ReceiptStateError(
                    "unexpected_dispositions",
                    "pass and unavailable reviews have no finding dispositions",
                )
            return
        if status != "issues":
            raise ReceiptStateError(
                "invalid_reconciliation_input", "stored review has invalid status"
            )
        findings = review.get("findings")
        if not isinstance(findings, list):
            raise ReceiptStateError(
                "invalid_reconciliation_input", "stored findings must be an array"
            )
        expected_ids: list[str] = []
        for finding in findings:
            if not isinstance(finding, Mapping) or not isinstance(finding.get("id"), str):
                raise ReceiptStateError(
                    "invalid_reconciliation_input", "stored finding has no valid id"
                )
            expected_ids.append(finding["id"])
        if len(expected_ids) != len(set(expected_ids)) or set(dispositions) != set(
            expected_ids
        ):
            raise ReceiptStateError(
                "finding_disposition_mismatch",
                "finding disposition IDs must equal stored review finding IDs",
            )

    def record_reconciliation(
        self,
        input_mapping: Mapping[str, Any],
        result_mapping: Mapping[str, Any],
    ) -> ReceiptRecord:
        current = self._verified_current()
        normalized_input = self._normalized_mapping(
            input_mapping, "reconciliation input"
        )
        normalized_result = self._normalized_mapping(
            result_mapping, "reconciliation result"
        )
        input_digest = "sha256:" + hashlib.sha256(
            canonical_json_bytes(normalized_input)
        ).hexdigest()
        reconciliation = {
            "input": normalized_input,
            "input_digest": input_digest,
            "result": normalized_result,
        }
        if current.state in {"reconciled", "publishing", "published"}:
            if canonical_json_bytes(current.reconciliation) == canonical_json_bytes(
                reconciliation
            ):
                return current
            raise ReceiptStateError(
                "reconciliation_replay_conflict",
                "attempt already has a different reconciliation",
            )
        if current.state != "reviewed":
            raise ReceiptStateError(
                "invalid_receipt_transition",
                f"cannot reconcile from state {current.state!r}",
            )
        assert current.review is not None
        self._validate_reconciliation_dispositions(current.review, normalized_input)
        updated = ReceiptRecord(
            receipt_id=current.receipt_id,
            attempt_key=current.attempt_key,
            scope_digest=current.scope_digest,
            scope=current.scope,
            state="reconciled",
            generation=current.generation + 1,
            review=current.review,
            reconciliation=reconciliation,
            publication=None,
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    @staticmethod
    def _publication_pair(path: str, candidate_digest: str) -> dict[str, str]:
        try:
            normalized_path = normalize_repo_path(path)
            normalized_digest = _sha256_text(
                candidate_digest,
                "candidate_digest",
                reason="invalid_publication",
            )
        except ReceiptContractError as exc:
            raise _state_error_from_contract(exc) from exc
        return {"path": normalized_path, "candidate_digest": normalized_digest}

    def begin_publication(
        self, path: str, candidate_digest: str
    ) -> ReceiptRecord:
        current = self._verified_current()
        publication = self._publication_pair(path, candidate_digest)
        if current.state in {"publishing", "published"}:
            if canonical_json_bytes(current.publication) == canonical_json_bytes(
                publication
            ):
                return current
            raise ReceiptStateError(
                "publication_replay_conflict",
                "attempt already names a different publication",
            )
        if current.state != "reconciled":
            raise ReceiptStateError(
                "invalid_receipt_transition",
                f"cannot begin publication from state {current.state!r}",
            )
        updated = ReceiptRecord(
            receipt_id=current.receipt_id,
            attempt_key=current.attempt_key,
            scope_digest=current.scope_digest,
            scope=current.scope,
            state="publishing",
            generation=current.generation + 1,
            review=current.review,
            reconciliation=current.reconciliation,
            publication=publication,
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    def finish_publication(
        self, path: str, candidate_digest: str
    ) -> ReceiptRecord:
        current = self._verified_current()
        publication = self._publication_pair(path, candidate_digest)
        if current.state == "published":
            if canonical_json_bytes(current.publication) == canonical_json_bytes(
                publication
            ):
                return current
            raise ReceiptStateError(
                "publication_replay_conflict", "published receipt has another target"
            )
        if current.state != "publishing":
            raise ReceiptStateError(
                "invalid_receipt_transition",
                f"cannot finish publication from state {current.state!r}",
            )
        if canonical_json_bytes(current.publication) != canonical_json_bytes(publication):
            raise ReceiptStateError(
                "publication_replay_conflict",
                "publication does not match the planned path and digest",
            )
        updated = ReceiptRecord(
            receipt_id=current.receipt_id,
            attempt_key=current.attempt_key,
            scope_digest=current.scope_digest,
            scope=current.scope,
            state="published",
            generation=current.generation + 1,
            review=current.review,
            reconciliation=current.reconciliation,
            publication=publication,
        )
        self._atomic_replace(updated)
        self._current = updated
        return updated

    def recover_publication(
        self, path: str, observed_digest: str | None
    ) -> str:
        current = self._verified_current()
        try:
            normalized_path = normalize_repo_path(path)
            normalized_observed = (
                _sha256_text(
                    observed_digest,
                    "observed_digest",
                    reason="invalid_publication",
                )
                if observed_digest is not None
                else None
            )
        except ReceiptContractError as exc:
            raise _state_error_from_contract(exc) from exc
        if current.state != "publishing":
            raise ReceiptStateError(
                "invalid_receipt_transition",
                f"cannot recover publication from state {current.state!r}",
            )
        assert current.publication is not None
        planned_path = current.publication.get("path")
        planned_digest = current.publication.get("candidate_digest")
        if normalized_path != planned_path:
            raise ReceiptStateError(
                "publication_replay_conflict", "observed path does not match plan"
            )
        if normalized_observed is None:
            updated = ReceiptRecord(
                receipt_id=current.receipt_id,
                attempt_key=current.attempt_key,
                scope_digest=current.scope_digest,
                scope=current.scope,
                state="reconciled",
                generation=current.generation + 1,
                review=current.review,
                reconciliation=current.reconciliation,
                publication=None,
            )
            self._atomic_replace(updated)
            self._current = updated
            return "clear"
        if normalized_observed == planned_digest:
            return "finalize"
        raise ReceiptStateError(
            "publication_replay_conflict",
            "observed digest does not match publication candidate",
        )
