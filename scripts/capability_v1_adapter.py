#!/usr/bin/env python3
"""Strict read-only boundary for host-normalized v1 observations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json
from re import fullmatch
import sys

from threeway.canon import canonicalize

if __package__:
    from scripts import capability_reducer, compact_state_mapping
else:
    import capability_reducer
    import compact_state_mapping


__all__ = ("LegacyAdapterError", "adapt_v1_history", "main")

_LEGACY_SCHEMA = "compact-kernel-legacy-observation/v1"
_LEGACY_RECORD_FIELDS = (
    "schema",
    "source_id",
    "source_digest",
    "work_id",
    "route_id",
    "work_revision",
    "unit_id",
    "actor_binding_digest",
    "domain",
    "value",
    "context",
    "mutable_scope_ref",
    "mutable_scope_digest",
    "content_digest",
    "dependency_digest",
    "acceptance_digest",
    "evidence_refs",
    "verification_ref",
    "effect_reservation_refs",
)
_LEGACY_ERROR_CODES = frozenset(
    {
        "legacy_invalid",
        "legacy_version",
        "legacy_unmapped",
        "legacy_ambiguous",
        "legacy_nondeterministic",
        "parity_divergence",
    }
)


class LegacyAdapterError(ValueError):
    """A stable, sanitized v1 adapter-boundary failure."""

    code: str

    def __init__(self, code: str) -> None:
        safe_code = code if code in _LEGACY_ERROR_CODES else "legacy_invalid"
        self.code = safe_code
        ValueError.__init__(self, safe_code)


@dataclass(frozen=True)
class _LegacyRecord:
    schema: str
    source_id: str
    source_digest: str
    work_id: str
    route_id: str | None
    work_revision: int
    unit_id: str | None
    actor_binding_digest: str
    domain: str
    value: str
    context: tuple[tuple[str, bool | str], ...]
    mutable_scope_ref: str
    mutable_scope_digest: str
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_refs: tuple[str, ...]
    verification_ref: str | None
    effect_reservation_refs: tuple[str, ...]


def _legacy_invalid() -> LegacyAdapterError:
    return LegacyAdapterError("legacy_invalid")


def _require_string(value: object, pattern: str) -> str:
    if type(value) is not str or fullmatch(pattern, value) is None:
        raise _legacy_invalid()
    return value


def _require_nullable_string(value: object, pattern: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, pattern)


def _require_integer(value: object, minimum: int) -> int:
    if (
        type(value) is not int
        or not minimum <= value <= capability_reducer.MAX_INT
    ):
        raise _legacy_invalid()
    return value


def _require_refs(value: object) -> tuple[str, ...]:
    if (
        type(value) is not list
        or len(value) > capability_reducer.MAX_COLLECTION_ITEMS
    ):
        raise _legacy_invalid()
    refs = tuple(
        _require_string(item, capability_reducer.REF_PATTERN) for item in value
    )
    if len(set(refs)) != len(refs):
        raise _legacy_invalid()
    return tuple(sorted(refs))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise _legacy_invalid()
        value[key] = item
    return value


def _reject_json_constant(_value: str) -> object:
    raise _legacy_invalid()


def _strict_json_loads(value: object) -> object:
    """Parse JSON while rejecting duplicate keys and non-standard constants."""

    if type(value) is not str:
        raise _legacy_invalid()
    try:
        return json.loads(
            value,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except LegacyAdapterError:
        raise
    except Exception:
        raise _legacy_invalid() from None


def _source_digest(value: dict[str, object]) -> str:
    without_digest = {
        field: value[field]
        for field in _LEGACY_RECORD_FIELDS
        if field != "source_digest"
    }
    try:
        return "sha256:" + sha256(canonicalize(without_digest)).hexdigest()
    except Exception:
        raise _legacy_invalid() from None


def _parse_legacy_record(value: object) -> _LegacyRecord:
    if type(value) is not dict or any(type(key) is not str for key in value):
        raise _legacy_invalid()

    schema = value.get("schema")
    if type(schema) is not str:
        raise _legacy_invalid()
    if schema != _LEGACY_SCHEMA:
        raise LegacyAdapterError("legacy_version")
    if set(value) != set(_LEGACY_RECORD_FIELDS):
        raise _legacy_invalid()

    source_id = _require_string(value["source_id"], capability_reducer.ID_PATTERN)
    source_digest = _require_string(
        value["source_digest"], capability_reducer.DIGEST_PATTERN
    )
    work_id = _require_string(value["work_id"], capability_reducer.ID_PATTERN)
    route_id = _require_nullable_string(
        value["route_id"], capability_reducer.ID_PATTERN
    )
    work_revision = _require_integer(value["work_revision"], 1)
    unit_id = _require_nullable_string(
        value["unit_id"], capability_reducer.ID_PATTERN
    )
    actor_binding_digest = _require_string(
        value["actor_binding_digest"], capability_reducer.DIGEST_PATTERN
    )
    domain = _require_string(value["domain"], capability_reducer.ID_PATTERN)
    state_value = _require_string(value["value"], capability_reducer.ID_PATTERN)

    context = value["context"]
    if type(context) is not dict or any(type(key) is not str for key in context):
        raise _legacy_invalid()
    if any(type(item) not in (bool, str) for item in context.values()):
        raise _legacy_invalid()

    mutable_scope_ref = _require_string(
        value["mutable_scope_ref"], capability_reducer.REF_PATTERN
    )
    mutable_scope_digest = _require_string(
        value["mutable_scope_digest"], capability_reducer.DIGEST_PATTERN
    )
    content_digest = _require_string(
        value["content_digest"], capability_reducer.DIGEST_PATTERN
    )
    dependency_digest = _require_string(
        value["dependency_digest"], capability_reducer.DIGEST_PATTERN
    )
    acceptance_digest = _require_string(
        value["acceptance_digest"], capability_reducer.DIGEST_PATTERN
    )
    evidence_refs = _require_refs(value["evidence_refs"])
    verification_ref = _require_nullable_string(
        value["verification_ref"], capability_reducer.REF_PATTERN
    )
    effect_reservation_refs = _require_refs(value["effect_reservation_refs"])

    if source_digest != _source_digest(value):
        raise _legacy_invalid()

    try:
        compact_state_mapping.meaning_for(domain, state_value, context=context)
    except compact_state_mapping.StateMappingError:
        raise LegacyAdapterError("legacy_unmapped") from None
    except Exception:
        raise _legacy_invalid() from None

    return _LegacyRecord(
        schema=schema,
        source_id=source_id,
        source_digest=source_digest,
        work_id=work_id,
        route_id=route_id,
        work_revision=work_revision,
        unit_id=unit_id,
        actor_binding_digest=actor_binding_digest,
        domain=domain,
        value=state_value,
        context=tuple(sorted(context.items())),
        mutable_scope_ref=mutable_scope_ref,
        mutable_scope_digest=mutable_scope_digest,
        content_digest=content_digest,
        dependency_digest=dependency_digest,
        acceptance_digest=acceptance_digest,
        evidence_refs=evidence_refs,
        verification_ref=verification_ref,
        effect_reservation_refs=effect_reservation_refs,
    )


def adapt_v1_history(
    records: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> tuple[capability_reducer.TransitionEnvelope, ...]:
    """Validate Task-1 input without mapping or emitting a route-v2 event."""

    try:
        raw_records = tuple(records)
    except Exception:
        raise _legacy_invalid() from None
    if not raw_records:
        return ()

    tuple(_parse_legacy_record(record) for record in raw_records)
    raise LegacyAdapterError("legacy_unmapped")


def main(argv: list[str] | None = None) -> int:
    """Fail closed until Task 2 supplies the committed corpus checker."""

    try:
        arguments = tuple(sys.argv[1:] if argv is None else argv)
    except Exception:
        return 1
    if (
        len(arguments) != 2
        or arguments[0] != "--check-corpus"
        or type(arguments[1]) is not str
        or not arguments[1]
    ):
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
