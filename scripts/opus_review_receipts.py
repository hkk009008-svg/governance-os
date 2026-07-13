#!/usr/bin/env python3
"""Canonical scope contracts for receipt-backed Lane V review."""

from __future__ import annotations

import hashlib
import json
import re
import shlex
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


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
_PATH_COLLECTION_MAX_ITEMS = 128
_COMMAND_COLLECTION_MAX_ITEMS = 32
_PATH_MAX_BYTES = 512
_COMMAND_MAX_BYTES = 4_096
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
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


class ReceiptContractError(ValueError):
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


def strict_json_loads(raw: bytes) -> Any:
    """Decode bounded UTF-8 JSON while rejecting duplicate keys and constants."""

    if not isinstance(raw, bytes):
        raise ReceiptContractError("invalid_json", "input must be bytes")
    if len(raw) > _DESCRIPTOR_MAX_BYTES:
        raise ReceiptContractError(
            "descriptor_too_large",
            f"descriptor exceeds {_DESCRIPTOR_MAX_BYTES} bytes",
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
