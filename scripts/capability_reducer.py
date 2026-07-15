"""Pure, non-authoritative compact transition contracts.

Phase 2A Task 1 defines only the strict route-v2 envelope boundary. The state
reducer entrypoints intentionally stop after validating their envelope inputs;
deterministic shadow reduction is added by Task 2.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from re import fullmatch
from typing import Callable, Iterable

from threeway.canon import canonicalize


SCHEMA_ID = "governance.route/v2"
ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$"
REF_PATTERN = r"^[\x21-\x7e]{1,512}$"
DIGEST_PATTERN = r"^sha256:[0-9a-f]{64}$"
REPOSITORY_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,255}$"
PRINCIPAL_PATTERN = r"^[\x21-\x7e]{1,256}$"
ACTION_PATTERN = r"^[a-z][a-z0-9_.:-]{0,63}$"
LOCK_DOMAIN_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$"
MAX_INT = 2**53 - 1
MAX_COLLECTION_ITEMS = 64
REQUESTED_TRANSITIONS = frozenset(
    {
        "START",
        "UPDATE",
        "BLOCK",
        "REQUEST_REVIEW",
        "REQUEST_CLOSE",
        "CANCEL",
        "SUPERSEDE",
    }
)
ENVELOPE_FIELDS = (
    "schema",
    "work_id",
    "transition_id",
    "route_id",
    "work_revision",
    "unit_id",
    "actor_binding_digest",
    "requested_transition",
    "expected_unit_version",
    "precondition_digest",
    "mutable_scope_ref",
    "mutable_scope_digest",
    "content_digest",
    "dependency_digest",
    "acceptance_digest",
    "evidence_refs",
    "verification_ref",
    "effect_reservation_refs",
    "activation_epoch",
)
ZERO_DIGEST = "sha256:" + ("0" * 64)


class ReducerError(ValueError):
    """A deterministic reducer-boundary failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        ValueError.__init__(self, code)


@dataclass(frozen=True)
class TransitionEnvelope:
    schema: str
    work_id: str
    transition_id: str
    route_id: str | None
    work_revision: int
    unit_id: str | None
    actor_binding_digest: str
    requested_transition: str
    expected_unit_version: int
    precondition_digest: str
    mutable_scope_ref: str
    mutable_scope_digest: str
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_refs: tuple[str, ...]
    verification_ref: str | None
    effect_reservation_refs: tuple[str, ...]
    activation_epoch: int


def _string_schema(pattern: str) -> dict[str, object]:
    return {"type": "string", "pattern": pattern}


def _nullable_string_schema(pattern: str) -> dict[str, object]:
    return {
        "anyOf": [
            _string_schema(pattern),
            {"type": "null"},
        ]
    }


def _integer_schema(minimum: int) -> dict[str, object]:
    return {
        "type": "integer",
        "minimum": minimum,
        "maximum": MAX_INT,
    }


def _ref_array_schema() -> dict[str, object]:
    return {
        "type": "array",
        "items": _string_schema(REF_PATTERN),
        "uniqueItems": True,
        "maxItems": MAX_COLLECTION_ITEMS,
    }


def field_schemas() -> dict[str, dict[str, object]]:
    """Return a fresh complete JSON-Schema property mapping."""

    return {
        "schema": {"const": SCHEMA_ID},
        "work_id": _string_schema(ID_PATTERN),
        "transition_id": _string_schema(ID_PATTERN),
        "route_id": _nullable_string_schema(ID_PATTERN),
        "work_revision": _integer_schema(1),
        "unit_id": _nullable_string_schema(ID_PATTERN),
        "actor_binding_digest": _string_schema(DIGEST_PATTERN),
        "requested_transition": {
            "type": "string",
            "enum": sorted(REQUESTED_TRANSITIONS),
        },
        "expected_unit_version": _integer_schema(0),
        "precondition_digest": _string_schema(DIGEST_PATTERN),
        "mutable_scope_ref": _string_schema(REF_PATTERN),
        "mutable_scope_digest": _string_schema(DIGEST_PATTERN),
        "content_digest": _string_schema(DIGEST_PATTERN),
        "dependency_digest": _string_schema(DIGEST_PATTERN),
        "acceptance_digest": _string_schema(DIGEST_PATTERN),
        "evidence_refs": _ref_array_schema(),
        "verification_ref": _nullable_string_schema(REF_PATTERN),
        "effect_reservation_refs": _ref_array_schema(),
        "activation_epoch": _integer_schema(0),
    }


def _unchecked_transition_mapping(event: TransitionEnvelope) -> dict[str, object]:
    return {
        "schema": event.schema,
        "work_id": event.work_id,
        "transition_id": event.transition_id,
        "route_id": event.route_id,
        "work_revision": event.work_revision,
        "unit_id": event.unit_id,
        "actor_binding_digest": event.actor_binding_digest,
        "requested_transition": event.requested_transition,
        "expected_unit_version": event.expected_unit_version,
        "precondition_digest": event.precondition_digest,
        "mutable_scope_ref": event.mutable_scope_ref,
        "mutable_scope_digest": event.mutable_scope_digest,
        "content_digest": event.content_digest,
        "dependency_digest": event.dependency_digest,
        "acceptance_digest": event.acceptance_digest,
        "evidence_refs": list(event.evidence_refs),
        "verification_ref": event.verification_ref,
        "effect_reservation_refs": list(event.effect_reservation_refs),
        "activation_epoch": event.activation_epoch,
    }


def _require_string(value: object, pattern: str) -> str:
    if type(value) is not str or fullmatch(pattern, value) is None:
        raise ReducerError("invalid_envelope")
    return value


def _require_nullable_string(value: object, pattern: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, pattern)


def _require_integer(value: object, minimum: int) -> int:
    if type(value) is not int or not minimum <= value <= MAX_INT:
        raise ReducerError("invalid_envelope")
    return value


def _require_refs(value: object) -> tuple[str, ...]:
    if type(value) is not list or len(value) > MAX_COLLECTION_ITEMS:
        raise ReducerError("invalid_envelope")
    refs = tuple(_require_string(item, REF_PATTERN) for item in value)
    if len(set(refs)) != len(refs):
        raise ReducerError("invalid_envelope")
    return tuple(sorted(refs))


def parse_transition(value: object) -> TransitionEnvelope:
    """Parse an exact route-v2 object, including direct envelope round trips."""

    try:
        if type(value) is TransitionEnvelope:
            if (
                type(value.evidence_refs) is not tuple
                or type(value.effect_reservation_refs) is not tuple
            ):
                raise ReducerError("invalid_envelope")
            raw = _unchecked_transition_mapping(value)
        elif type(value) is dict:
            raw = value
        else:
            raise ReducerError("invalid_envelope")

        if any(type(key) is not str for key in raw) or set(raw) != set(ENVELOPE_FIELDS):
            raise ReducerError("invalid_envelope")
        if type(raw["schema"]) is not str or raw["schema"] != SCHEMA_ID:
            raise ReducerError("invalid_envelope")

        requested_transition = _require_string(raw["requested_transition"], ID_PATTERN)
        if requested_transition not in REQUESTED_TRANSITIONS:
            raise ReducerError("invalid_envelope")

        return TransitionEnvelope(
            schema=SCHEMA_ID,
            work_id=_require_string(raw["work_id"], ID_PATTERN),
            transition_id=_require_string(raw["transition_id"], ID_PATTERN),
            route_id=_require_nullable_string(raw["route_id"], ID_PATTERN),
            work_revision=_require_integer(raw["work_revision"], 1),
            unit_id=_require_nullable_string(raw["unit_id"], ID_PATTERN),
            actor_binding_digest=_require_string(
                raw["actor_binding_digest"], DIGEST_PATTERN
            ),
            requested_transition=requested_transition,
            expected_unit_version=_require_integer(raw["expected_unit_version"], 0),
            precondition_digest=_require_string(
                raw["precondition_digest"], DIGEST_PATTERN
            ),
            mutable_scope_ref=_require_string(raw["mutable_scope_ref"], REF_PATTERN),
            mutable_scope_digest=_require_string(
                raw["mutable_scope_digest"], DIGEST_PATTERN
            ),
            content_digest=_require_string(raw["content_digest"], DIGEST_PATTERN),
            dependency_digest=_require_string(
                raw["dependency_digest"], DIGEST_PATTERN
            ),
            acceptance_digest=_require_string(
                raw["acceptance_digest"], DIGEST_PATTERN
            ),
            evidence_refs=_require_refs(raw["evidence_refs"]),
            verification_ref=_require_nullable_string(
                raw["verification_ref"], REF_PATTERN
            ),
            effect_reservation_refs=_require_refs(raw["effect_reservation_refs"]),
            activation_epoch=_require_integer(raw["activation_epoch"], 0),
        )
    except ReducerError:
        raise
    except Exception as exc:
        raise ReducerError("invalid_envelope") from exc


def transition_mapping(value: object) -> dict[str, object]:
    """Return one explicit JSON mapping in envelope-field order."""

    return _unchecked_transition_mapping(parse_transition(value))


def transition_bytes(value: object) -> bytes:
    """Return RFC 8785 bytes for one validated transition."""

    try:
        return canonicalize(transition_mapping(value))
    except ReducerError:
        raise
    except Exception as exc:
        raise ReducerError("invalid_envelope") from exc


def transition_digest(value: object) -> str:
    """Return the canonical prefixed SHA-256 digest for one transition."""

    try:
        digest = sha256(transition_bytes(value))
        return "sha256:" + digest.hexdigest()
    except ReducerError:
        raise
    except Exception as exc:
        raise ReducerError("invalid_envelope") from exc


def apply_transition(
    state: object,
    event: object,
    *,
    actor: object,
    activation: object,
    resolve_scope: Callable[[str], object],
) -> object:
    """Validate the Task-1 event boundary before the Task-2 implementation."""

    parse_transition(event)
    raise NotImplementedError("shadow reduction is Phase 2A Task 2")


def reduce_protocol_state(
    events: Iterable[object],
    *,
    resolve_actor: Callable[[str], object],
    resolve_scope: Callable[[str], object],
    activation: object,
) -> object:
    """Validate Task-1 event boundaries before the Task-2 implementation."""

    for event in events:
        parse_transition(event)
    raise NotImplementedError("shadow reduction is Phase 2A Task 2")
