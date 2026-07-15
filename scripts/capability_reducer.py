"""Pure, deterministic, non-authoritative compact shadow reduction."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from re import fullmatch
from typing import Callable, Iterable, Literal

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


@dataclass(frozen=True)
class ActorContext:
    binding_id: str
    binding_digest: str
    repository: str
    principal: str
    allowed_actions: frozenset[str]
    user_authorized_actions: frozenset[str]
    parent_binding_id: str | None
    parent_allowed_actions: frozenset[str] | None
    attested: bool
    expired: bool
    revoked: bool


@dataclass(frozen=True)
class ResolvedScope:
    repository: str
    paths: tuple[str, ...]
    lock_domains: tuple[str, ...]


@dataclass(frozen=True)
class ActivationState:
    epoch: int
    mode: Literal["shadow"] = "shadow"

    def __post_init__(self) -> None:
        if (
            type(self.epoch) is not int
            or not 0 <= self.epoch <= MAX_INT
            or type(self.mode) is not str
            or self.mode != "shadow"
        ):
            raise ReducerError("activation_epoch")


@dataclass(frozen=True)
class WorkSnapshot:
    work_id: str
    route_id: str | None
    work_revision: int


@dataclass(frozen=True)
class UnitSnapshot:
    work_id: str
    unit_id: str | None
    unit_version: int
    mutable_scope_ref: str
    scope_repository: str
    scope_paths: tuple[str, ...]
    scope_lock_domains: tuple[str, ...]
    mutable_scope_digest: str
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_digest: str
    precondition_digest: str


@dataclass(frozen=True)
class AppliedTransition:
    transition_id: str
    event_digest: str
    work_id: str
    unit_id: str | None
    work_revision: int
    resulting_unit_version: int
    resulting_relevant_digest: str
    resulting_precondition_digest: str
    mutable_scope_digest: str


@dataclass(frozen=True)
class KernelState:
    works: tuple[WorkSnapshot, ...] = ()
    units: tuple[UnitSnapshot, ...] = ()
    transitions: tuple[AppliedTransition, ...] = ()


@dataclass(frozen=True)
class KernelReport:
    mode: Literal["shadow"]
    state_digest: str
    applied_transition_ids: tuple[str, ...]
    idempotent_transition_ids: tuple[str, ...]
    units: tuple[UnitSnapshot, ...]


ActorBindingResolver = Callable[[str], ActorContext]
ScopeResolver = Callable[[str], ResolvedScope]


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


def _prefixed_digest(value: bytes) -> str:
    digest = sha256(value)
    return "sha256:" + digest.hexdigest()


def transition_digest(value: object) -> str:
    """Return the canonical prefixed SHA-256 digest for one transition."""

    try:
        return _prefixed_digest(transition_bytes(value))
    except ReducerError:
        raise
    except Exception as exc:
        raise ReducerError("invalid_envelope") from exc


def unit_key(work_id: str, unit_id: str | None) -> tuple[str, int, str]:
    """Return the total key where the work-level null lane sorts first."""

    return (work_id, 0, "") if unit_id is None else (work_id, 1, unit_id)


def transition_key(
    item: AppliedTransition,
) -> tuple[str, int, str, int, str]:
    """Return the canonical applied-transition ordering key."""

    work, tag, unit = unit_key(item.work_id, item.unit_id)
    return (work, tag, unit, item.work_revision, item.transition_id)


def _require_state_string(value: object, pattern: str, code: str) -> str:
    if type(value) is not str or fullmatch(pattern, value) is None:
        raise ReducerError(code)
    return value


def _require_state_nullable_string(
    value: object, pattern: str, code: str
) -> str | None:
    if value is None:
        return None
    return _require_state_string(value, pattern, code)


def _require_state_integer(
    value: object, minimum: int, code: str
) -> int:
    if type(value) is not int or not minimum <= value <= MAX_INT:
        raise ReducerError(code)
    return value


def _require_state_string_tuple(
    value: object,
    pattern: str,
    code: str,
) -> tuple[str, ...]:
    if type(value) is not tuple or len(value) > MAX_COLLECTION_ITEMS:
        raise ReducerError(code)
    items = tuple(_require_state_string(item, pattern, code) for item in value)
    return tuple(sorted(set(items)))


def _repository_is_safe(value: str) -> bool:
    parts = tuple(value.split("/"))
    return all(part not in ("", ".", "..") for part in parts)


def _actor_mapping(actor: ActorContext) -> dict[str, object]:
    return {
        "binding_id": actor.binding_id,
        "repository": actor.repository,
        "principal": actor.principal,
        "allowed_actions": sorted(actor.allowed_actions),
        "user_authorized_actions": sorted(actor.user_authorized_actions),
        "parent_binding_id": actor.parent_binding_id,
        "parent_allowed_actions": (
            None
            if actor.parent_allowed_actions is None
            else sorted(actor.parent_allowed_actions)
        ),
        "attested": actor.attested,
        "expired": actor.expired,
        "revoked": actor.revoked,
    }


def _validate_actor(actor: object) -> tuple[ActorContext, bytes]:
    code = "actor_binding"
    if type(actor) is not ActorContext:
        raise ReducerError(code)
    _require_state_string(actor.binding_id, ID_PATTERN, code)
    _require_state_string(actor.binding_digest, DIGEST_PATTERN, code)
    repository = _require_state_string(actor.repository, REPOSITORY_PATTERN, code)
    if not _repository_is_safe(repository):
        raise ReducerError(code)
    _require_state_string(actor.principal, PRINCIPAL_PATTERN, code)
    if (
        type(actor.allowed_actions) is not frozenset
        or type(actor.user_authorized_actions) is not frozenset
        or len(actor.allowed_actions) > MAX_COLLECTION_ITEMS
        or len(actor.user_authorized_actions) > MAX_COLLECTION_ITEMS
    ):
        raise ReducerError(code)
    for action in actor.allowed_actions:
        _require_state_string(action, ACTION_PATTERN, code)
    for action in actor.user_authorized_actions:
        _require_state_string(action, ACTION_PATTERN, code)
    if type(actor.attested) is not bool:
        raise ReducerError(code)
    if type(actor.expired) is not bool or type(actor.revoked) is not bool:
        raise ReducerError(code)

    if actor.parent_binding_id is None:
        if actor.parent_allowed_actions is not None:
            raise ReducerError(code)
    else:
        _require_state_string(actor.parent_binding_id, ID_PATTERN, code)
        if (
            type(actor.parent_allowed_actions) is not frozenset
            or len(actor.parent_allowed_actions) > MAX_COLLECTION_ITEMS
        ):
            raise ReducerError(code)
        for action in actor.parent_allowed_actions:
            _require_state_string(action, ACTION_PATTERN, code)

    normalized_bytes = canonicalize(_actor_mapping(actor))
    if actor.binding_digest != _prefixed_digest(normalized_bytes):
        raise ReducerError(code)
    if (
        not actor.allowed_actions
        or not actor.user_authorized_actions
        or not actor.attested
        or actor.expired
        or actor.revoked
    ):
        raise ReducerError("actor_ineligible")
    if (
        "transition.apply" not in actor.allowed_actions
        or "transition.apply" not in actor.user_authorized_actions
        or (
            actor.parent_allowed_actions is not None
            and "transition.apply" not in actor.parent_allowed_actions
        )
    ):
        raise ReducerError("actor_ineligible")
    if not actor.allowed_actions <= actor.user_authorized_actions:
        raise ReducerError("actor_ineligible")
    if actor.parent_binding_id is not None:
        if (
            not actor.parent_allowed_actions
            or actor.parent_binding_id == actor.binding_id
            or not actor.allowed_actions < actor.parent_allowed_actions
        ):
            raise ReducerError("actor_ineligible")
    return actor, normalized_bytes


def _normalize_scope(value: object) -> ResolvedScope:
    code = "scope_invalid"
    if type(value) is not ResolvedScope:
        raise ReducerError(code)
    repository = _require_state_string(value.repository, REPOSITORY_PATTERN, code)
    if not _repository_is_safe(repository):
        raise ReducerError(code)
    paths = _require_state_string_tuple(value.paths, REF_PATTERN, code)
    lock_domains = _require_state_string_tuple(
        value.lock_domains, LOCK_DOMAIN_PATTERN, code
    )
    if not paths and not lock_domains:
        raise ReducerError(code)
    for path in paths:
        if (
            path[0] == "/"
            or path[-1] == "/"
            or "\\" in path
            or "//" in path
        ):
            raise ReducerError(code)
        components = _path_components(path)
        if any(component in ("", ".", "..") for component in components):
            raise ReducerError(code)
    for index, path in enumerate(paths):
        for other in paths[index + 1 :]:
            if _path_overlap(path, other):
                raise ReducerError(code)
    return ResolvedScope(
        repository=repository,
        paths=paths,
        lock_domains=lock_domains,
    )


def _scope_mapping(scope: ResolvedScope) -> dict[str, object]:
    return {
        "repository": scope.repository,
        "paths": list(scope.paths),
        "lock_domains": list(scope.lock_domains),
    }


def _scope_digest(scope: ResolvedScope) -> str:
    return _prefixed_digest(canonicalize(_scope_mapping(scope)))


def _evidence_digest(refs: tuple[str, ...]) -> str:
    return _prefixed_digest(canonicalize(list(sorted(refs))))


def _compute_relevant_digest(
    content_digest: str,
    dependency_digest: str,
    acceptance_digest: str,
    evidence_digest: str,
) -> str:
    return _prefixed_digest(
        canonicalize(
            {
                "content_digest": content_digest,
                "dependency_digest": dependency_digest,
                "acceptance_digest": acceptance_digest,
                "evidence_digest": evidence_digest,
            }
        )
    )


def _compute_precondition(
    work_id: str,
    unit_id: str | None,
    unit_version: int,
    mutable_scope_digest: str,
    content_digest: str,
    dependency_digest: str,
    acceptance_digest: str,
    evidence_digest: str,
) -> str:
    return _prefixed_digest(
        canonicalize(
            {
                "work_id": work_id,
                "unit_id": unit_id,
                "unit_version": unit_version,
                "mutable_scope_digest": mutable_scope_digest,
                "content_digest": content_digest,
                "dependency_digest": dependency_digest,
                "acceptance_digest": acceptance_digest,
                "evidence_digest": evidence_digest,
            }
        )
    )


def _work_mapping(work: WorkSnapshot) -> dict[str, object]:
    return {
        "work_id": work.work_id,
        "route_id": work.route_id,
        "work_revision": work.work_revision,
    }


def _unit_mapping(unit: UnitSnapshot) -> dict[str, object]:
    return {
        "work_id": unit.work_id,
        "unit_id": unit.unit_id,
        "unit_version": unit.unit_version,
        "mutable_scope_ref": unit.mutable_scope_ref,
        "scope_repository": unit.scope_repository,
        "scope_paths": list(unit.scope_paths),
        "scope_lock_domains": list(unit.scope_lock_domains),
        "mutable_scope_digest": unit.mutable_scope_digest,
        "content_digest": unit.content_digest,
        "dependency_digest": unit.dependency_digest,
        "acceptance_digest": unit.acceptance_digest,
        "evidence_digest": unit.evidence_digest,
        "precondition_digest": unit.precondition_digest,
    }


def _applied_mapping(item: AppliedTransition) -> dict[str, object]:
    return {
        "transition_id": item.transition_id,
        "event_digest": item.event_digest,
        "work_id": item.work_id,
        "unit_id": item.unit_id,
        "work_revision": item.work_revision,
        "resulting_unit_version": item.resulting_unit_version,
        "resulting_relevant_digest": item.resulting_relevant_digest,
        "resulting_precondition_digest": item.resulting_precondition_digest,
        "mutable_scope_digest": item.mutable_scope_digest,
    }


def _state_digest(state: KernelState) -> str:
    return _prefixed_digest(
        canonicalize(
            {
                "works": [_work_mapping(work) for work in state.works],
                "units": [_unit_mapping(unit) for unit in state.units],
                "transitions": [
                    _applied_mapping(item) for item in state.transitions
                ],
            }
        )
    )


def _validate_activation(value: object) -> ActivationState:
    if (
        type(value) is not ActivationState
        or type(value.epoch) is not int
        or not 0 <= value.epoch <= MAX_INT
        or type(value.mode) is not str
        or value.mode != "shadow"
    ):
        raise ReducerError("activation_epoch")
    return value


def _validate_state(value: object) -> KernelState:
    code = "state_invalid"
    if type(value) is not KernelState:
        raise ReducerError(code)
    if (
        type(value.works) is not tuple
        or type(value.units) is not tuple
        or type(value.transitions) is not tuple
    ):
        raise ReducerError(code)

    for work in value.works:
        if type(work) is not WorkSnapshot:
            raise ReducerError(code)
        _require_state_string(work.work_id, ID_PATTERN, code)
        _require_state_nullable_string(work.route_id, ID_PATTERN, code)
        _require_state_integer(work.work_revision, 1, code)
    if value.works != tuple(sorted(value.works, key=lambda item: item.work_id)):
        raise ReducerError(code)
    if len({work.work_id for work in value.works}) != len(value.works):
        raise ReducerError(code)

    for unit in value.units:
        if type(unit) is not UnitSnapshot:
            raise ReducerError(code)
        _require_state_string(unit.work_id, ID_PATTERN, code)
        _require_state_nullable_string(unit.unit_id, ID_PATTERN, code)
        _require_state_integer(unit.unit_version, 1, code)
        _require_state_string(unit.mutable_scope_ref, REF_PATTERN, code)
        _require_state_string(unit.scope_repository, REPOSITORY_PATTERN, code)
        if not _repository_is_safe(unit.scope_repository):
            raise ReducerError(code)
        _require_state_string(unit.mutable_scope_digest, DIGEST_PATTERN, code)
        _require_state_string(unit.content_digest, DIGEST_PATTERN, code)
        _require_state_string(unit.dependency_digest, DIGEST_PATTERN, code)
        _require_state_string(unit.acceptance_digest, DIGEST_PATTERN, code)
        _require_state_string(unit.evidence_digest, DIGEST_PATTERN, code)
        _require_state_string(unit.precondition_digest, DIGEST_PATTERN, code)
        try:
            normalized_scope = _normalize_scope(
                ResolvedScope(
                    repository=unit.scope_repository,
                    paths=unit.scope_paths,
                    lock_domains=unit.scope_lock_domains,
                )
            )
        except ReducerError as exc:
            raise ReducerError(code) from exc
        if (
            normalized_scope.paths != unit.scope_paths
            or normalized_scope.lock_domains != unit.scope_lock_domains
            or _scope_digest(normalized_scope) != unit.mutable_scope_digest
        ):
            raise ReducerError(code)
        expected_precondition = _compute_precondition(
            unit.work_id,
            unit.unit_id,
            unit.unit_version,
            unit.mutable_scope_digest,
            unit.content_digest,
            unit.dependency_digest,
            unit.acceptance_digest,
            unit.evidence_digest,
        )
        if unit.precondition_digest != expected_precondition:
            raise ReducerError(code)
    if value.units != tuple(
        sorted(value.units, key=lambda item: unit_key(item.work_id, item.unit_id))
    ):
        raise ReducerError(code)
    unit_keys = tuple(unit_key(unit.work_id, unit.unit_id) for unit in value.units)
    if len(set(unit_keys)) != len(unit_keys):
        raise ReducerError(code)

    for item in value.transitions:
        if type(item) is not AppliedTransition:
            raise ReducerError(code)
        _require_state_string(item.transition_id, ID_PATTERN, code)
        _require_state_string(item.event_digest, DIGEST_PATTERN, code)
        _require_state_string(item.work_id, ID_PATTERN, code)
        _require_state_nullable_string(item.unit_id, ID_PATTERN, code)
        _require_state_integer(item.work_revision, 1, code)
        _require_state_integer(item.resulting_unit_version, 1, code)
        _require_state_string(item.resulting_relevant_digest, DIGEST_PATTERN, code)
        _require_state_string(
            item.resulting_precondition_digest, DIGEST_PATTERN, code
        )
        _require_state_string(item.mutable_scope_digest, DIGEST_PATTERN, code)
    if value.transitions != tuple(sorted(value.transitions, key=transition_key)):
        raise ReducerError(code)
    if len({item.transition_id for item in value.transitions}) != len(
        value.transitions
    ):
        raise ReducerError(code)

    work_ids = {work.work_id for work in value.works}
    for unit in value.units:
        if unit.work_id not in work_ids:
            raise ReducerError(code)
    for item in value.transitions:
        if item.work_id not in work_ids:
            raise ReducerError(code)
        matching_units = tuple(
            unit
            for unit in value.units
            if unit.work_id == item.work_id and unit.unit_id == item.unit_id
        )
        if len(matching_units) != 1:
            raise ReducerError(code)
        if (
            item.resulting_unit_version > matching_units[0].unit_version
            or item.mutable_scope_digest
            != matching_units[0].mutable_scope_digest
        ):
            raise ReducerError(code)

    for work in value.works:
        revisions = tuple(
            sorted(
                item.work_revision
                for item in value.transitions
                if item.work_id == work.work_id
            )
        )
        if len(revisions) != work.work_revision:
            raise ReducerError(code)
        for index, revision in enumerate(revisions, 1):
            if revision != index:
                raise ReducerError(code)
    for unit in value.units:
        history = tuple(
            item
            for item in value.transitions
            if item.work_id == unit.work_id and item.unit_id == unit.unit_id
        )
        unit_relevant_digest = _compute_relevant_digest(
            unit.content_digest,
            unit.dependency_digest,
            unit.acceptance_digest,
            unit.evidence_digest,
        )
        if (
            not history
            or history[0].resulting_unit_version != 1
        ):
            raise ReducerError(code)
        for index, item in enumerate(history[1:], 1):
            previous = history[index - 1]
            expected_version = (
                previous.resulting_unit_version
                if item.resulting_relevant_digest
                == previous.resulting_relevant_digest
                else previous.resulting_unit_version + 1
            )
            if item.resulting_unit_version != expected_version:
                raise ReducerError(code)
        final = history[-1]
        if (
            final.resulting_unit_version != unit.unit_version
            or final.resulting_relevant_digest != unit_relevant_digest
            or final.resulting_precondition_digest != unit.precondition_digest
        ):
            raise ReducerError(code)

    for index, unit in enumerate(value.units):
        for other in value.units[index + 1 :]:
            if _scopes_overlap(unit, other):
                raise ReducerError(code)
    return value


def _path_components(path: str) -> tuple[str, ...]:
    return tuple(path.split("/"))


def _path_overlap(left: str, right: str) -> bool:
    left_parts = _path_components(left)
    right_parts = _path_components(right)
    return (
        left_parts == right_parts[: len(left_parts)]
        or right_parts == left_parts[: len(right_parts)]
    )


def _scopes_overlap(left: UnitSnapshot, right: UnitSnapshot) -> bool:
    if left.scope_repository != right.scope_repository:
        return False
    if set(left.scope_lock_domains) & set(right.scope_lock_domains):
        return True
    return any(
        _path_overlap(left_path, right_path)
        for left_path in left.scope_paths
        for right_path in right.scope_paths
    )


def apply_transition(
    state: object,
    event: object,
    *,
    actor: object,
    activation: object,
    resolve_scope: ScopeResolver,
) -> KernelState:
    """Apply one validated transition to pure in-memory shadow state."""

    parsed = parse_transition(event)
    active = _validate_activation(activation)
    current = _validate_state(state)
    if parsed.activation_epoch != active.epoch:
        raise ReducerError("activation_epoch")

    event_digest = transition_digest(parsed)
    existing = tuple(
        item
        for item in current.transitions
        if item.transition_id == parsed.transition_id
    )
    if existing:
        stored = existing[0]
        if stored.event_digest != event_digest:
            raise ReducerError("transition_id_reuse")
        matching_work = tuple(
            work for work in current.works if work.work_id == parsed.work_id
        )
        matching_unit = tuple(
            unit
            for unit in current.units
            if unit.work_id == parsed.work_id and unit.unit_id == parsed.unit_id
        )
        if (
            stored.work_id != parsed.work_id
            or stored.unit_id != parsed.unit_id
            or stored.work_revision != parsed.work_revision
            or stored.mutable_scope_digest != parsed.mutable_scope_digest
            or len(matching_work) != 1
            or matching_work[0].route_id != parsed.route_id
            or len(matching_unit) != 1
            or matching_unit[0].mutable_scope_ref != parsed.mutable_scope_ref
        ):
            raise ReducerError("state_invalid")

        unit_history = tuple(
            item
            for item in current.transitions
            if item.work_id == parsed.work_id and item.unit_id == parsed.unit_id
        )
        stored_positions = tuple(
            index
            for index, item in enumerate(unit_history)
            if item.transition_id == stored.transition_id
        )
        if len(stored_positions) != 1:
            raise ReducerError("state_invalid")
        position = stored_positions[0]
        predecessor = None if position == 0 else unit_history[position - 1]
        required_version = (
            0 if predecessor is None else predecessor.resulting_unit_version
        )
        consumed_precondition = (
            _compute_precondition(
                parsed.work_id,
                parsed.unit_id,
                0,
                ZERO_DIGEST,
                ZERO_DIGEST,
                ZERO_DIGEST,
                ZERO_DIGEST,
                ZERO_DIGEST,
            )
            if predecessor is None
            else predecessor.resulting_precondition_digest
        )
        evidence_digest = _evidence_digest(parsed.evidence_refs)
        relevant_digest = _compute_relevant_digest(
            parsed.content_digest,
            parsed.dependency_digest,
            parsed.acceptance_digest,
            evidence_digest,
        )
        resulting_precondition = _compute_precondition(
            parsed.work_id,
            parsed.unit_id,
            stored.resulting_unit_version,
            parsed.mutable_scope_digest,
            parsed.content_digest,
            parsed.dependency_digest,
            parsed.acceptance_digest,
            evidence_digest,
        )
        if (
            parsed.expected_unit_version != required_version
            or parsed.precondition_digest != consumed_precondition
            or stored.resulting_relevant_digest != relevant_digest
            or stored.resulting_precondition_digest != resulting_precondition
        ):
            raise ReducerError("state_invalid")
        return current

    validated_actor, _actor_bytes = _validate_actor(actor)
    if parsed.actor_binding_digest != validated_actor.binding_digest:
        raise ReducerError("actor_binding")

    try:
        first_scope_value = resolve_scope(parsed.mutable_scope_ref)
    except Exception as exc:
        raise ReducerError("scope_invalid") from exc
    first_scope = _normalize_scope(first_scope_value)
    try:
        second_scope_value = resolve_scope(parsed.mutable_scope_ref)
    except Exception as exc:
        raise ReducerError("scope_invalid") from exc
    second_scope = _normalize_scope(second_scope_value)
    if first_scope != second_scope:
        raise ReducerError("scope_nondeterministic")
    scope = first_scope
    if validated_actor.repository != scope.repository:
        raise ReducerError("actor_binding")
    if parsed.mutable_scope_digest != _scope_digest(scope):
        raise ReducerError("scope_digest")

    matching_works = tuple(
        work for work in current.works if work.work_id == parsed.work_id
    )
    work = matching_works[0] if matching_works else None
    if work is None:
        if parsed.work_revision != 1:
            raise ReducerError("work_revision")
    else:
        if parsed.work_revision != work.work_revision + 1:
            raise ReducerError("work_revision")
        if parsed.route_id != work.route_id:
            raise ReducerError("route_ambiguity")

    matching_units = tuple(
        unit
        for unit in current.units
        if unit.work_id == parsed.work_id and unit.unit_id == parsed.unit_id
    )
    unit = matching_units[0] if matching_units else None
    if unit is not None and (
        parsed.mutable_scope_ref != unit.mutable_scope_ref
        or scope.repository != unit.scope_repository
        or scope.paths != unit.scope_paths
        or scope.lock_domains != unit.scope_lock_domains
        or parsed.mutable_scope_digest != unit.mutable_scope_digest
    ):
        raise ReducerError("scope_invalid")

    for other in current.units:
        if other.work_id == parsed.work_id and other.unit_id == parsed.unit_id:
            continue
        candidate = UnitSnapshot(
            work_id=parsed.work_id,
            unit_id=parsed.unit_id,
            unit_version=1,
            mutable_scope_ref=parsed.mutable_scope_ref,
            scope_repository=scope.repository,
            scope_paths=scope.paths,
            scope_lock_domains=scope.lock_domains,
            mutable_scope_digest=parsed.mutable_scope_digest,
            content_digest=parsed.content_digest,
            dependency_digest=parsed.dependency_digest,
            acceptance_digest=parsed.acceptance_digest,
            evidence_digest=_evidence_digest(parsed.evidence_refs),
            precondition_digest=ZERO_DIGEST,
        )
        if _scopes_overlap(candidate, other):
            raise ReducerError("scope_overlap")

    previous_version = 0 if unit is None else unit.unit_version
    if parsed.expected_unit_version != previous_version:
        raise ReducerError("expected_version")
    previous_scope_digest = ZERO_DIGEST if unit is None else unit.mutable_scope_digest
    previous_content_digest = ZERO_DIGEST if unit is None else unit.content_digest
    previous_dependency_digest = (
        ZERO_DIGEST if unit is None else unit.dependency_digest
    )
    previous_acceptance_digest = (
        ZERO_DIGEST if unit is None else unit.acceptance_digest
    )
    previous_evidence_digest = ZERO_DIGEST if unit is None else unit.evidence_digest
    expected_precondition = _compute_precondition(
        parsed.work_id,
        parsed.unit_id,
        previous_version,
        previous_scope_digest,
        previous_content_digest,
        previous_dependency_digest,
        previous_acceptance_digest,
        previous_evidence_digest,
    )
    if parsed.precondition_digest != expected_precondition:
        raise ReducerError("precondition")

    evidence_digest = _evidence_digest(parsed.evidence_refs)
    relevant_digest = _compute_relevant_digest(
        parsed.content_digest,
        parsed.dependency_digest,
        parsed.acceptance_digest,
        evidence_digest,
    )
    if unit is None:
        resulting_version = 1
    else:
        previous_relevant_digest = _compute_relevant_digest(
            unit.content_digest,
            unit.dependency_digest,
            unit.acceptance_digest,
            unit.evidence_digest,
        )
        relevant_changed = relevant_digest != previous_relevant_digest
        if relevant_changed and unit.unit_version == MAX_INT:
            raise ReducerError("expected_version")
        resulting_version = unit.unit_version + 1 if relevant_changed else unit.unit_version

    post_precondition = _compute_precondition(
        parsed.work_id,
        parsed.unit_id,
        resulting_version,
        parsed.mutable_scope_digest,
        parsed.content_digest,
        parsed.dependency_digest,
        parsed.acceptance_digest,
        evidence_digest,
    )
    new_unit = UnitSnapshot(
        work_id=parsed.work_id,
        unit_id=parsed.unit_id,
        unit_version=resulting_version,
        mutable_scope_ref=parsed.mutable_scope_ref,
        scope_repository=scope.repository,
        scope_paths=scope.paths,
        scope_lock_domains=scope.lock_domains,
        mutable_scope_digest=parsed.mutable_scope_digest,
        content_digest=parsed.content_digest,
        dependency_digest=parsed.dependency_digest,
        acceptance_digest=parsed.acceptance_digest,
        evidence_digest=evidence_digest,
        precondition_digest=post_precondition,
    )
    units = tuple(
        sorted(
            (
                tuple(
                    existing_unit
                    for existing_unit in current.units
                    if not (
                        existing_unit.work_id == parsed.work_id
                        and existing_unit.unit_id == parsed.unit_id
                    )
                )
                + (new_unit,)
            ),
            key=lambda item: unit_key(item.work_id, item.unit_id),
        )
    )

    new_work = WorkSnapshot(
        work_id=parsed.work_id,
        route_id=parsed.route_id if work is None else work.route_id,
        work_revision=parsed.work_revision,
    )
    works = tuple(
        sorted(
            tuple(
                existing_work
                for existing_work in current.works
                if existing_work.work_id != parsed.work_id
            )
            + (new_work,),
            key=lambda item: item.work_id,
        )
    )
    applied = AppliedTransition(
        transition_id=parsed.transition_id,
        event_digest=event_digest,
        work_id=parsed.work_id,
        unit_id=parsed.unit_id,
        work_revision=parsed.work_revision,
        resulting_unit_version=resulting_version,
        resulting_relevant_digest=relevant_digest,
        resulting_precondition_digest=post_precondition,
        mutable_scope_digest=parsed.mutable_scope_digest,
    )
    transitions = tuple(
        sorted(current.transitions + (applied,), key=transition_key)
    )
    return _validate_state(
        KernelState(works=works, units=units, transitions=transitions)
    )


def reduce_protocol_state(
    events: Iterable[object],
    *,
    resolve_actor: ActorBindingResolver,
    resolve_scope: ScopeResolver,
    activation: object,
) -> KernelReport:
    """Reduce a batch into one deterministic observational shadow report."""

    try:
        raw_events = tuple(events)
    except Exception as exc:
        raise ReducerError("invalid_envelope") from exc
    parsed_events = tuple(parse_transition(event) for event in raw_events)
    active = _validate_activation(activation)

    unique_events: dict[str, tuple[TransitionEnvelope, str]] = {}
    idempotent_ids: dict[str, None] = {}
    for parsed in parsed_events:
        event_digest = transition_digest(parsed)
        if parsed.transition_id in unique_events:
            if unique_events[parsed.transition_id][1] != event_digest:
                raise ReducerError("transition_id_reuse")
            idempotent_ids[parsed.transition_id] = None
        else:
            unique_events[parsed.transition_id] = (parsed, event_digest)

    ordered_events = tuple(
        sorted(
            (item[0] for item in unique_events.values()),
            key=lambda item: (item.work_id, item.work_revision, item.transition_id),
        )
    )
    actors: dict[str, ActorContext] = {}
    current = KernelState()
    for parsed in ordered_events:
        if parsed.actor_binding_digest not in actors:
            try:
                first_actor_value = resolve_actor(parsed.actor_binding_digest)
            except Exception as exc:
                raise ReducerError("actor_binding") from exc
            first_actor, first_bytes = _validate_actor(first_actor_value)
            try:
                second_actor_value = resolve_actor(parsed.actor_binding_digest)
            except Exception as exc:
                raise ReducerError("actor_binding") from exc
            second_actor, second_bytes = _validate_actor(second_actor_value)
            if first_bytes != second_bytes:
                raise ReducerError("actor_nondeterministic")
            actors[parsed.actor_binding_digest] = first_actor

        try:
            first_scope_value = resolve_scope(parsed.mutable_scope_ref)
        except Exception as exc:
            raise ReducerError("scope_invalid") from exc
        first_resolved_scope = _normalize_scope(first_scope_value)
        try:
            second_scope_value = resolve_scope(parsed.mutable_scope_ref)
        except Exception as exc:
            raise ReducerError("scope_invalid") from exc
        second_resolved_scope = _normalize_scope(second_scope_value)
        if first_resolved_scope != second_resolved_scope:
            raise ReducerError("scope_nondeterministic")

        def resolved_scope(_ref: str) -> ResolvedScope:
            return first_resolved_scope

        current = apply_transition(
            current,
            parsed,
            actor=actors[parsed.actor_binding_digest],
            activation=active,
            resolve_scope=resolved_scope,
        )

    return KernelReport(
        mode="shadow",
        state_digest=_state_digest(current),
        applied_transition_ids=tuple(
            sorted(item.transition_id for item in current.transitions)
        ),
        idempotent_transition_ids=tuple(sorted(idempotent_ids)),
        units=current.units,
    )
