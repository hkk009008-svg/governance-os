from __future__ import annotations

import ast
import dataclasses
import inspect
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pytest

from scripts import capability_reducer as reducer
from threeway.canon import canonicalize


PERMITTED_IMPORT_MODULES = (
    "__future__",
    "dataclasses",
    "hashlib",
    "re",
    "typing",
    "threeway.canon",
)
PERMITTED_IMPORTED_CALL_NAMES = ("canonicalize", "dataclass", "fullmatch", "sha256")
PERMITTED_IMPORT_ALIASES: tuple[tuple[str, str | None], ...] = ()
PERMITTED_FROM_IMPORTS = (
    ("__future__", ("annotations",)),
    ("dataclasses", ("dataclass",)),
    ("hashlib", ("sha256",)),
    ("re", ("fullmatch",)),
    ("typing", ("Callable", "Iterable", "Literal")),
    ("threeway.canon", ("canonicalize",)),
)
PERMITTED_IMPORT_BINDINGS = (
    "annotations",
    "dataclass",
    "sha256",
    "fullmatch",
    "Callable",
    "Iterable",
    "Literal",
    "canonicalize",
)
EXPECTED_TOP_LEVEL_CLASS_NAMES = (
    "ReducerError",
    "TransitionEnvelope",
    "ActorContext",
    "ResolvedScope",
    "ActivationState",
    "WorkSnapshot",
    "UnitSnapshot",
    "AppliedTransition",
    "KernelState",
    "KernelReport",
)
EXPECTED_TOP_LEVEL_FUNCTION_NAMES = (
    "_string_schema",
    "_nullable_string_schema",
    "_integer_schema",
    "_ref_array_schema",
    "field_schemas",
    "_unchecked_transition_mapping",
    "_require_string",
    "_require_nullable_string",
    "_require_integer",
    "_require_refs",
    "parse_transition",
    "transition_mapping",
    "transition_bytes",
    "_prefixed_digest",
    "transition_digest",
    "unit_key",
    "transition_key",
    "_require_state_string",
    "_require_state_nullable_string",
    "_require_state_integer",
    "_require_state_string_tuple",
    "_repository_is_safe",
    "_actor_mapping",
    "_validate_actor",
    "_normalize_scope",
    "_scope_mapping",
    "_scope_digest",
    "_evidence_digest",
    "_compute_precondition",
    "_work_mapping",
    "_unit_mapping",
    "_applied_mapping",
    "_state_digest",
    "_validate_activation",
    "_validate_state",
    "_path_components",
    "_path_overlap",
    "_scopes_overlap",
    "apply_transition",
    "reduce_protocol_state",
)
PERMITTED_NAME_CALLS = (
    "ActivationState",
    "ActorContext",
    "AppliedTransition",
    "KernelReport",
    "KernelState",
    "ReducerError",
    "ResolvedScope",
    "TransitionEnvelope",
    "UnitSnapshot",
    "WorkSnapshot",
    "_actor_mapping",
    "_applied_mapping",
    "_compute_precondition",
    "_evidence_digest",
    "_integer_schema",
    "_nullable_string_schema",
    "_normalize_scope",
    "_path_components",
    "_path_overlap",
    "_prefixed_digest",
    "_ref_array_schema",
    "_require_integer",
    "_require_nullable_string",
    "_require_refs",
    "_require_state_integer",
    "_require_state_nullable_string",
    "_require_state_string",
    "_require_state_string_tuple",
    "_require_string",
    "_repository_is_safe",
    "_scope_digest",
    "_scope_mapping",
    "_scopes_overlap",
    "_state_digest",
    "_string_schema",
    "_unchecked_transition_mapping",
    "_unit_mapping",
    "_validate_activation",
    "_validate_actor",
    "_validate_state",
    "_work_mapping",
    "all",
    "any",
    "apply_transition",
    "canonicalize",
    "dataclass",
    "enumerate",
    "frozenset",
    "fullmatch",
    "len",
    "list",
    "parse_transition",
    "range",
    "set",
    "sha256",
    "sorted",
    "transition_bytes",
    "transition_digest",
    "transition_key",
    "transition_mapping",
    "tuple",
    "type",
    "unit_key",
)
PERMITTED_INJECTED_CALL_NAMES = ("resolve_actor", "resolve_scope")
PERMITTED_ATTRIBUTE_CALLS = (
    ("ValueError", "__init__"),
    ("digest", "hexdigest"),
    ("path", "split"),
    ("unique_events", "values"),
    ("value", "split"),
)
PROTECTED_ATTRIBUTE_BASES = ("ValueError", "digest")
DANGEROUS_INTROSPECTION_ATTRIBUTES = (
    "__globals__",
    "__builtins__",
    "__dict__",
    "__subclasses__",
    "__getattribute__",
    "__getattr__",
)
FORBIDDEN_NAME_REFERENCES = ("__import__", "compile", "eval", "exec", "open")


def _is_exact_digest_assignment(
    node: ast.Name, parents: dict[ast.AST, ast.AST]
) -> bool:
    parent = parents.get(node)
    return (
        isinstance(node.ctx, ast.Store)
        and isinstance(parent, ast.Assign)
        and len(parent.targets) == 1
        and parent.targets[0] is node
        and isinstance(parent.value, ast.Call)
        and isinstance(parent.value.func, ast.Name)
        and parent.value.func.id == "sha256"
        and len(parent.value.args) == 1
        and not parent.value.keywords
        and isinstance(parent.value.args[0], ast.Name)
        and parent.value.args[0].id == "value"
    )


def _ast_purity_violations(source: str) -> list[str]:
    tree = ast.parse(source)
    violations: list[str] = []
    actual_from_imports: list[tuple[str, tuple[str, ...]]] = []
    actual_import_bindings: list[str] = []
    imported_names: set[str] = set()
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    actual_class_names = tuple(
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    )
    actual_function_names = tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    if actual_class_names != EXPECTED_TOP_LEVEL_CLASS_NAMES:
        violations.append("top-level class definitions do not match literal contract")
    if actual_function_names != EXPECTED_TOP_LEVEL_FUNCTION_NAMES:
        violations.append(
            "top-level function definitions do not match literal contract"
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                descriptor = (alias.name, alias.asname)
                if descriptor not in PERMITTED_IMPORT_ALIASES:
                    violations.append(f"ast.Import is not permitted: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = tuple(alias.name for alias in node.names)
            actual_from_imports.append((module, names))
            bindings = tuple(alias.asname or alias.name for alias in node.names)
            actual_import_bindings.extend(bindings)
            imported_names.update(bindings)
            if node.level != 0 or module not in PERMITTED_IMPORT_MODULES:
                violations.append(f"from-import module is not permitted: {module}")
            if any(
                alias.asname is not None or alias.name == "*" for alias in node.names
            ):
                violations.append(f"from-import aliases are not permitted: {module}")

    if tuple(actual_from_imports) != PERMITTED_FROM_IMPORTS:
        violations.append("from-import shape does not match the literal contract")
    if tuple(actual_import_bindings) != PERMITTED_IMPORT_BINDINGS:
        violations.append("import bindings do not match the literal contract")

    protected_names = (
        set(PERMITTED_NAME_CALLS)
        | set(PERMITTED_IMPORT_BINDINGS)
        | set(PROTECTED_ATTRIBUTE_BASES)
    )
    permitted_digest_assignments = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.Match):
            violations.append("match statements are not permitted")

        if isinstance(node, ast.Name) and node.id == "__builtins__":
            violations.append("dynamic builtin namespace access is not permitted")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAME_REFERENCES:
            violations.append(
                f"forbidden name reference is not permitted: {node.id}"
            )

        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, (ast.Store, ast.Del))
            and node.id in protected_names
        ):
            if node.id == "digest" and _is_exact_digest_assignment(node, parents):
                permitted_digest_assignments += 1
            else:
                violations.append(
                    f"protected name rebinding is not permitted: {node.id}"
                )

        if isinstance(node, ast.arg) and node.arg in protected_names:
            violations.append(
                f"protected name rebinding is not permitted: {node.arg}"
            )

        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node not in tree.body
            and node.name in protected_names
        ):
            violations.append(
                f"protected name rebinding is not permitted: {node.name}"
            )

        string_binding: str | None = None
        if isinstance(node, ast.ExceptHandler):
            string_binding = node.name
        elif isinstance(node, ast.MatchAs):
            string_binding = node.name
        elif isinstance(node, ast.MatchStar):
            string_binding = node.name
        elif isinstance(node, ast.MatchMapping):
            string_binding = node.rest
        if string_binding in protected_names:
            violations.append(
                "protected string binding is not permitted: "
                f"{string_binding}"
            )

        if (
            isinstance(node, ast.Attribute)
            and node.attr in DANGEROUS_INTROSPECTION_ATTRIBUTES
        ):
            violations.append(
                "dangerous introspection attribute is not permitted: "
                f"{node.attr}"
            )

        if not isinstance(node, ast.Call):
            continue

        function = node.func
        if isinstance(function, ast.Name):
            if (
                function.id not in PERMITTED_NAME_CALLS
                and function.id not in PERMITTED_INJECTED_CALL_NAMES
            ):
                violations.append(f"name call is not permitted: {function.id}")
            if (
                function.id in imported_names
                and function.id not in PERMITTED_IMPORTED_CALL_NAMES
            ):
                violations.append(f"imported call is not permitted: {function.id}")
        elif isinstance(function, ast.Attribute):
            if isinstance(function.value, ast.Call):
                violations.append("call-result callable resolution is not permitted")
            elif not isinstance(function.value, ast.Name):
                violations.append("attribute-call base must be one literal name")
            elif (function.value.id, function.attr) not in PERMITTED_ATTRIBUTE_CALLS:
                violations.append(
                    "attribute call is not permitted: "
                    f"{function.value.id}.{function.attr}"
                )
        elif isinstance(function, ast.Subscript):
            violations.append("subscript callable resolution is not permitted")
        elif isinstance(function, ast.Lambda):
            violations.append("lambda callable resolution is not permitted")
        elif isinstance(function, ast.Call):
            violations.append("call-result callable resolution is not permitted")
        else:
            violations.append(
                f"callable AST shape is not permitted: {type(function).__name__}"
            )

    if permitted_digest_assignments != 1:
        violations.append("exact digest = sha256(value) assignment count must be one")

    return violations


def _assert_reducer_ast_is_pure(source: str) -> None:
    violations = _ast_purity_violations(source)
    assert not violations, "\n".join(violations)


def _digest(character: str) -> str:
    return "sha256:" + (character * 64)


def _valid_payload() -> dict[str, object]:
    return {
        "schema": "governance.route/v2",
        "work_id": "work-1",
        "transition_id": "transition-1",
        "route_id": "route-1",
        "work_revision": 1,
        "unit_id": "unit-1",
        "actor_binding_digest": _digest("1"),
        "requested_transition": "START",
        "expected_unit_version": 0,
        "precondition_digest": _digest("2"),
        "mutable_scope_ref": "scope:work-1/unit-1",
        "mutable_scope_digest": _digest("3"),
        "content_digest": _digest("4"),
        "dependency_digest": _digest("5"),
        "acceptance_digest": _digest("6"),
        "evidence_refs": ["web:https://example.test/source", "artifact:one"],
        "verification_ref": "verification:one",
        "effect_reservation_refs": ["reservation:two", "reservation:one"],
        "activation_epoch": 0,
    }


def _canonical_digest(value: object) -> str:
    return "sha256:" + sha256(canonicalize(value)).hexdigest()


def _actor_context(
    *,
    binding_id: str = "actor-1",
    repository: str = "owner/repository",
    principal: str = "user:principal",
    allowed_actions: frozenset[str] = frozenset({"transition.apply"}),
    user_authorized_actions: frozenset[str] = frozenset({"transition.apply"}),
    parent_binding_id: str | None = None,
    parent_allowed_actions: frozenset[str] | None = None,
    attested: bool = True,
    expired: bool = False,
    revoked: bool = False,
) -> reducer.ActorContext:
    mapping = {
        "binding_id": binding_id,
        "repository": repository,
        "principal": principal,
        "allowed_actions": sorted(allowed_actions),
        "user_authorized_actions": sorted(user_authorized_actions),
        "parent_binding_id": parent_binding_id,
        "parent_allowed_actions": (
            None
            if parent_allowed_actions is None
            else sorted(parent_allowed_actions)
        ),
        "attested": attested,
        "expired": expired,
        "revoked": revoked,
    }
    return reducer.ActorContext(
        binding_id=binding_id,
        binding_digest=_canonical_digest(mapping),
        repository=repository,
        principal=principal,
        allowed_actions=allowed_actions,
        user_authorized_actions=user_authorized_actions,
        parent_binding_id=parent_binding_id,
        parent_allowed_actions=parent_allowed_actions,
        attested=attested,
        expired=expired,
        revoked=revoked,
    )


def _resolved_scope(
    *,
    repository: str = "owner/repository",
    paths: tuple[str, ...] = ("src/unit",),
    lock_domains: tuple[str, ...] = ("lock:unit",),
) -> reducer.ResolvedScope:
    return reducer.ResolvedScope(
        repository=repository,
        paths=paths,
        lock_domains=lock_domains,
    )


def _scope_digest(scope: reducer.ResolvedScope) -> str:
    return _canonical_digest(
        {
            "repository": scope.repository,
            "paths": sorted(set(scope.paths)),
            "lock_domains": sorted(set(scope.lock_domains)),
        }
    )


def _evidence_digest(refs: tuple[str, ...] | list[str]) -> str:
    return _canonical_digest(sorted(refs))


def _precondition_digest(
    *,
    work_id: str,
    unit_id: str | None,
    unit_version: int,
    mutable_scope_digest: str,
    content_digest: str,
    dependency_digest: str,
    acceptance_digest: str,
    evidence_digest: str,
) -> str:
    return _canonical_digest(
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


def _event_payload(
    *,
    actor: reducer.ActorContext,
    scope: reducer.ResolvedScope,
    work_id: str = "work-1",
    transition_id: str = "transition-1",
    route_id: str | None = "route-1",
    work_revision: int = 1,
    unit_id: str | None = "unit-1",
    requested_transition: str = "START",
    expected_unit_version: int = 0,
    precondition_digest: str | None = None,
    mutable_scope_ref: str = "scope:work-1/unit-1",
    content_digest: str = _digest("4"),
    dependency_digest: str = _digest("5"),
    acceptance_digest: str = _digest("6"),
    evidence_refs: tuple[str, ...] = (),
    verification_ref: str | None = None,
    effect_reservation_refs: tuple[str, ...] = (),
    activation_epoch: int = 0,
) -> dict[str, object]:
    if precondition_digest is None:
        precondition_digest = _precondition_digest(
            work_id=work_id,
            unit_id=unit_id,
            unit_version=0,
            mutable_scope_digest=reducer.ZERO_DIGEST,
            content_digest=reducer.ZERO_DIGEST,
            dependency_digest=reducer.ZERO_DIGEST,
            acceptance_digest=reducer.ZERO_DIGEST,
            evidence_digest=reducer.ZERO_DIGEST,
        )
    return {
        "schema": reducer.SCHEMA_ID,
        "work_id": work_id,
        "transition_id": transition_id,
        "route_id": route_id,
        "work_revision": work_revision,
        "unit_id": unit_id,
        "actor_binding_digest": actor.binding_digest,
        "requested_transition": requested_transition,
        "expected_unit_version": expected_unit_version,
        "precondition_digest": precondition_digest,
        "mutable_scope_ref": mutable_scope_ref,
        "mutable_scope_digest": _scope_digest(scope),
        "content_digest": content_digest,
        "dependency_digest": dependency_digest,
        "acceptance_digest": acceptance_digest,
        "evidence_refs": list(evidence_refs),
        "verification_ref": verification_ref,
        "effect_reservation_refs": list(effect_reservation_refs),
        "activation_epoch": activation_epoch,
    }


def _apply(
    state: reducer.KernelState,
    payload: object,
    *,
    actor: reducer.ActorContext,
    scope: reducer.ResolvedScope,
    activation: reducer.ActivationState | None = None,
) -> reducer.KernelState:
    active = reducer.ActivationState(epoch=0) if activation is None else activation
    return reducer.apply_transition(
        state,
        payload,
        actor=actor,
        activation=active,
        resolve_scope=lambda _ref: scope,
    )


def _second_payload(
    state: reducer.KernelState,
    *,
    actor: reducer.ActorContext,
    scope: reducer.ResolvedScope,
    transition_id: str = "transition-2",
    requested_transition: str = "UPDATE",
    **updates: object,
) -> dict[str, object]:
    unit = state.units[0]
    work = state.works[0]
    payload = _event_payload(
        actor=actor,
        scope=scope,
        work_id=unit.work_id,
        transition_id=transition_id,
        route_id=work.route_id,
        work_revision=work.work_revision + 1,
        unit_id=unit.unit_id,
        requested_transition=requested_transition,
        expected_unit_version=unit.unit_version,
        precondition_digest=unit.precondition_digest,
        mutable_scope_ref=unit.mutable_scope_ref,
        content_digest=unit.content_digest,
        dependency_digest=unit.dependency_digest,
        acceptance_digest=unit.acceptance_digest,
        evidence_refs=(),
    )
    payload.update(updates)
    return payload


def _assert_reducer_error(code: str, call: object) -> None:
    with pytest.raises(reducer.ReducerError) as exc_info:
        call()
    assert exc_info.value.code == code


def _assert_invalid(value: object) -> None:
    with pytest.raises(reducer.ReducerError) as exc_info:
        reducer.parse_transition(value)
    assert exc_info.value.code == "invalid_envelope"


def test_parse_normalizes_refs_and_canonical_helpers_use_explicit_mapping() -> None:
    parsed = reducer.parse_transition(_valid_payload())

    assert parsed.evidence_refs == (
        "artifact:one",
        "web:https://example.test/source",
    )
    assert parsed.effect_reservation_refs == (
        "reservation:one",
        "reservation:two",
    )

    mapping = reducer.transition_mapping(parsed)
    assert tuple(mapping) == reducer.ENVELOPE_FIELDS
    assert mapping["evidence_refs"] == [
        "artifact:one",
        "web:https://example.test/source",
    ]
    assert mapping["effect_reservation_refs"] == [
        "reservation:one",
        "reservation:two",
    ]
    assert reducer.transition_bytes(parsed) == canonicalize(mapping)
    assert reducer.transition_digest(parsed) == (
        "sha256:" + sha256(canonicalize(mapping)).hexdigest()
    )


def test_transition_envelope_and_public_callable_shapes_are_exact() -> None:
    assert tuple(
        field.name for field in dataclasses.fields(reducer.TransitionEnvelope)
    ) == reducer.ENVELOPE_FIELDS

    positional = inspect.Parameter.POSITIONAL_OR_KEYWORD
    keyword_only = inspect.Parameter.KEYWORD_ONLY
    expected = (
        (reducer.parse_transition, (("value", positional),)),
        (reducer.transition_mapping, (("value", positional),)),
        (reducer.transition_bytes, (("value", positional),)),
        (reducer.transition_digest, (("value", positional),)),
        (
            reducer.apply_transition,
            (
                ("state", positional),
                ("event", positional),
                ("actor", keyword_only),
                ("activation", keyword_only),
                ("resolve_scope", keyword_only),
            ),
        ),
        (
            reducer.reduce_protocol_state,
            (
                ("events", positional),
                ("resolve_actor", keyword_only),
                ("resolve_scope", keyword_only),
                ("activation", keyword_only),
            ),
        ),
    )

    for function, expected_parameters in expected:
        actual = tuple(
            (name, parameter.kind)
            for name, parameter in inspect.signature(function).parameters.items()
        )
        assert actual == expected_parameters


def test_parse_rejects_non_object_missing_unknown_wrong_typed_and_wrong_schema() -> None:
    for value in (None, True, 1, "object", [], (), object()):
        _assert_invalid(value)

    for field in reducer.ENVELOPE_FIELDS:
        value = _valid_payload()
        del value[field]
        _assert_invalid(value)

    value = _valid_payload()
    value["unknown"] = "field"
    _assert_invalid(value)

    value = _valid_payload()
    value["schema"] = "governance.route/v1"
    _assert_invalid(value)

    wrong_types = {
        "schema": 1,
        "work_id": 1,
        "transition_id": [],
        "route_id": True,
        "work_revision": "1",
        "unit_id": {},
        "actor_binding_digest": None,
        "requested_transition": 1,
        "expected_unit_version": 0.0,
        "precondition_digest": [],
        "mutable_scope_ref": 1,
        "mutable_scope_digest": {},
        "content_digest": False,
        "dependency_digest": None,
        "acceptance_digest": 1,
        "evidence_refs": (),
        "verification_ref": 1,
        "effect_reservation_refs": "reservation:one",
        "activation_epoch": 0.0,
    }
    for field, wrong_value in wrong_types.items():
        value = _valid_payload()
        value[field] = wrong_value
        _assert_invalid(value)

    for field in ("work_revision", "expected_unit_version", "activation_epoch"):
        value = _valid_payload()
        value[field] = True
        _assert_invalid(value)

        value = _valid_payload()
        value[field] = reducer.MAX_INT + 1
        _assert_invalid(value)

    for field, below_minimum in (
        ("work_revision", 0),
        ("expected_unit_version", -1),
        ("activation_epoch", -1),
    ):
        value = _valid_payload()
        value[field] = below_minimum
        _assert_invalid(value)

    for field in (
        "actor_binding_digest",
        "precondition_digest",
        "mutable_scope_digest",
        "content_digest",
        "dependency_digest",
        "acceptance_digest",
    ):
        value = _valid_payload()
        value[field] = "sha256:" + ("A" * 64)
        _assert_invalid(value)

    value = _valid_payload()
    value["requested_transition"] = "GO"
    _assert_invalid(value)

    for field in ("evidence_refs", "effect_reservation_refs"):
        value = _valid_payload()
        value[field] = ["duplicate:ref", "duplicate:ref"]
        _assert_invalid(value)

        value = _valid_payload()
        value[field] = [f"ref:{index}" for index in range(65)]
        _assert_invalid(value)

    for field in ("work_id", "transition_id"):
        value = _valid_payload()
        value[field] = ""
        _assert_invalid(value)

    for field in ("route_id", "unit_id"):
        value = _valid_payload()
        value[field] = "contains space"
        _assert_invalid(value)

    for field in ("mutable_scope_ref", "verification_ref"):
        value = _valid_payload()
        value[field] = "contains space"
        _assert_invalid(value)

    for field in ("evidence_refs", "effect_reservation_refs"):
        value = _valid_payload()
        value[field] = ["contains space"]
        _assert_invalid(value)

    nullable = _valid_payload()
    nullable["route_id"] = None
    nullable["unit_id"] = None
    nullable["verification_ref"] = None
    assert reducer.parse_transition(nullable).route_id is None
    assert reducer.parse_transition(nullable).unit_id is None
    assert reducer.parse_transition(nullable).verification_ref is None

    exact_boundaries = _valid_payload()
    exact_boundaries["work_id"] = "w" * 128
    exact_boundaries["mutable_scope_ref"] = "r" * 512
    exact_boundaries["work_revision"] = reducer.MAX_INT
    exact_boundaries["expected_unit_version"] = reducer.MAX_INT
    exact_boundaries["activation_epoch"] = reducer.MAX_INT
    exact_boundaries["evidence_refs"] = [f"ref:{index}" for index in range(64)]
    parsed_boundary = reducer.parse_transition(exact_boundaries)
    assert reducer.MAX_INT == 2**53 - 1
    assert parsed_boundary.work_revision == reducer.MAX_INT
    assert reducer.transition_bytes(parsed_boundary)
    assert reducer.transition_digest(parsed_boundary).startswith("sha256:")

    for field, overlong in (
        ("work_id", "w" * 129),
        ("mutable_scope_ref", "r" * 513),
    ):
        value = _valid_payload()
        value[field] = overlong
        _assert_invalid(value)


@pytest.mark.parametrize(
    "field", ("work_revision", "expected_unit_version", "activation_epoch")
)
def test_parse_rejects_integer_above_rfc8785_safe_max(field: str) -> None:
    value = _valid_payload()
    value[field] = 2**53
    _assert_invalid(value)


def test_parse_rejects_payload_principal_and_effect_action_fields() -> None:
    for field in ("principal", "actor", "effect_action", "effect_eligible"):
        value = _valid_payload()
        value[field] = "attacker-controlled"
        _assert_invalid(value)


def test_direct_envelope_construction_cannot_bypass_validation() -> None:
    valid = reducer.parse_transition(_valid_payload())
    invalid = replace(valid, work_id="")

    for call in (
        lambda: reducer.parse_transition(invalid),
        lambda: reducer.transition_mapping(invalid),
        lambda: reducer.transition_bytes(invalid),
        lambda: reducer.transition_digest(invalid),
        lambda: reducer.apply_transition(
            object(),
            invalid,
            actor=object(),
            activation=object(),
            resolve_scope=lambda _ref: object(),
        ),
        lambda: reducer.reduce_protocol_state(
            [invalid],
            resolve_actor=lambda _digest: object(),
            resolve_scope=lambda _ref: object(),
            activation=object(),
        ),
    ):
        with pytest.raises(reducer.ReducerError) as exc_info:
            call()
        assert exc_info.value.code == "invalid_envelope"

    invalid_refs = replace(valid, evidence_refs=("duplicate:ref", "duplicate:ref"))
    _assert_invalid(invalid_refs)

    for invalid_container in (
        replace(valid, evidence_refs="ab"),
        replace(valid, effect_reservation_refs="xy"),
        replace(valid, evidence_refs=["ref:one"]),
    ):
        _assert_invalid(invalid_container)


def test_reducer_ast_has_only_pure_import_and_call_boundaries() -> None:
    source = Path(reducer.__file__).read_text(encoding="utf-8")
    _assert_reducer_ast_is_pure(source)


@pytest.mark.parametrize(
    ("mutation", "expected_violations"),
    (
        (
            'import hashlib\nhashlib.md5(b"payload")',
            ("ast.Import is not permitted", "attribute call is not permitted"),
        ),
        (
            'getattr(__builtins__, "open")("secret")',
            (
                "dynamic builtin namespace access is not permitted",
                "name call is not permitted: getattr",
                "call-result callable resolution is not permitted",
            ),
        ),
        (
            '__builtins__["__import__"]("os").getenv("TOKEN")',
            (
                "dynamic builtin namespace access is not permitted",
                "subscript callable resolution is not permitted",
                "call-result callable resolution is not permitted",
            ),
        ),
        (
            "(lambda: None)()",
            ("lambda callable resolution is not permitted",),
        ),
        (
            "callables[0]()",
            ("subscript callable resolution is not permitted",),
        ),
        (
            'list = open\nlist("secret")',
            (
                "protected name rebinding is not permitted: list",
                "forbidden name reference is not permitted: open",
            ),
        ),
        (
            'sha256 = __import__\nsha256("os")',
            (
                "protected name rebinding is not permitted: sha256",
                "forbidden name reference is not permitted: __import__",
            ),
        ),
        (
            'canonicalize = dataclass.__globals__["sys"].modules["os"].getenv\n'
            'canonicalize("HOME")',
            (
                "protected name rebinding is not permitted: canonicalize",
                "dangerous introspection attribute is not permitted: __globals__",
            ),
        ),
        (
            "match dataclass.__getattribute__:\n"
            "    case canonicalize:\n"
            '        match canonicalize("__globals__")["sys"].modules["os"].getenv:\n'
            "            case canonicalize:\n"
            '                canonicalize("HOME")',
            (
                "match statements are not permitted",
                "dangerous introspection attribute is not permitted: "
                "__getattribute__",
                "protected string binding is not permitted: canonicalize",
            ),
        ),
        (
            "try:\n"
            "    raise ValueError\n"
            "except ValueError as canonicalize:\n"
            '    canonicalize("HOME")',
            ("protected string binding is not permitted: canonicalize",),
        ),
    ),
)
def test_reducer_ast_purity_guards_reject_dynamic_call_mutations(
    mutation: str, expected_violations: tuple[str, ...]
) -> None:
    source = Path(reducer.__file__).read_text(encoding="utf-8")
    with pytest.raises(AssertionError) as exc_info:
        _assert_reducer_ast_is_pure(source + "\n" + mutation + "\n")

    message = str(exc_info.value)
    for expected in expected_violations:
        assert expected in message


def test_every_output_dataclass_has_exact_non_authority_fields() -> None:
    expected = {
        reducer.WorkSnapshot: (
            "work_id",
            "route_id",
            "work_revision",
        ),
        reducer.UnitSnapshot: (
            "work_id",
            "unit_id",
            "unit_version",
            "mutable_scope_ref",
            "scope_repository",
            "scope_paths",
            "scope_lock_domains",
            "mutable_scope_digest",
            "content_digest",
            "dependency_digest",
            "acceptance_digest",
            "evidence_digest",
            "precondition_digest",
        ),
        reducer.AppliedTransition: (
            "transition_id",
            "event_digest",
            "work_id",
            "unit_id",
            "work_revision",
            "resulting_unit_version",
            "mutable_scope_digest",
        ),
        reducer.KernelState: ("works", "units", "transitions"),
        reducer.KernelReport: (
            "mode",
            "state_digest",
            "applied_transition_ids",
            "idempotent_transition_ids",
            "units",
        ),
    }
    forbidden = (
        "go",
        "done",
        "verdict",
        "terminal",
        "authority",
        "authorized",
        "effect_eligible",
        "effect_eligibility",
    )

    for data_type, fields in expected.items():
        actual = tuple(field.name for field in dataclasses.fields(data_type))
        assert actual == fields
        assert all(token not in name.lower() for name in actual for token in forbidden)


def test_public_boundary_dataclasses_are_validated() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    payload = _event_payload(actor=actor, scope=scope)
    state = _apply(reducer.KernelState(), payload, actor=actor, scope=scope)

    malformed_states = (
        reducer.KernelState(
            works=list(state.works),
            units=state.units,
            transitions=state.transitions,
        ),
        replace(
            state,
            works=(replace(state.works[0], work_id=""),),
        ),
        replace(
            state,
            units=(replace(state.units[0], unit_version=0),),
        ),
        replace(
            state,
            transitions=(replace(state.transitions[0], event_digest="bad"),),
        ),
    )
    for malformed in malformed_states:
        _assert_reducer_error(
            "state_invalid",
            lambda malformed=malformed: reducer.apply_transition(
                malformed,
                payload,
                actor=actor,
                activation=reducer.ActivationState(epoch=0),
                resolve_scope=lambda _ref: scope,
            ),
        )

    malformed_actor = replace(actor, allowed_actions=("transition.apply",))
    _assert_reducer_error(
        "actor_binding",
        lambda: reducer.apply_transition(
            reducer.KernelState(),
            payload,
            actor=malformed_actor,
            activation=reducer.ActivationState(epoch=0),
            resolve_scope=lambda _ref: scope,
        ),
    )
    malformed_scope = replace(scope, paths=["src/unit"])
    _assert_reducer_error(
        "scope_invalid",
        lambda: reducer.apply_transition(
            reducer.KernelState(),
            payload,
            actor=actor,
            activation=reducer.ActivationState(epoch=0),
            resolve_scope=lambda _ref: malformed_scope,
        ),
    )


def test_activation_state_is_shadow_only() -> None:
    assert reducer.ActivationState(epoch=0).mode == "shadow"
    for kwargs in (
        {"epoch": True},
        {"epoch": -1},
        {"epoch": reducer.MAX_INT + 1},
        {"epoch": 0, "mode": "active"},
    ):
        _assert_reducer_error(
            "activation_epoch",
            lambda kwargs=kwargs: reducer.ActivationState(**kwargs),
        )

    actor = _actor_context()
    scope = _resolved_scope()
    stale = _event_payload(actor=actor, scope=scope, activation_epoch=1)
    _assert_reducer_error(
        "activation_epoch",
        lambda: _apply(
            reducer.KernelState(),
            stale,
            actor=actor,
            scope=scope,
            activation=reducer.ActivationState(epoch=0),
        ),
    )


def test_actor_is_resolved_out_of_band_and_canonical_digest_must_match() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    payload = _event_payload(actor=actor, scope=scope)

    report = reducer.reduce_protocol_state(
        [payload],
        resolve_actor=lambda digest: actor if digest == actor.binding_digest else None,
        resolve_scope=lambda _ref: scope,
        activation=reducer.ActivationState(epoch=0),
    )
    assert report.applied_transition_ids == ("transition-1",)

    _assert_reducer_error(
        "actor_binding",
        lambda: _apply(
            reducer.KernelState(),
            payload,
            actor=replace(actor, binding_digest=_digest("f")),
            scope=scope,
        ),
    )
    other_repository_actor = _actor_context(repository="owner/other")
    other_payload = _event_payload(actor=other_repository_actor, scope=scope)
    _assert_reducer_error(
        "actor_binding",
        lambda: _apply(
            reducer.KernelState(),
            other_payload,
            actor=other_repository_actor,
            scope=scope,
        ),
    )


@pytest.mark.parametrize(
    "updates",
    (
        {"revoked": True},
        {"expired": True},
        {"attested": False},
        {
            "allowed_actions": frozenset(),
            "user_authorized_actions": frozenset(),
        },
    ),
)
def test_revoked_expired_unattested_or_actionless_actor_is_ineligible(
    updates: dict[str, object],
) -> None:
    actor = _actor_context(**updates)
    scope = _resolved_scope()
    payload = _event_payload(actor=actor, scope=scope)
    _assert_reducer_error(
        "actor_ineligible",
        lambda: _apply(
            reducer.KernelState(), payload, actor=actor, scope=scope
        ),
    )


def test_user_actions_cannot_be_broadened_and_child_actions_are_a_proper_subset() -> None:
    scope = _resolved_scope()
    broadened = _actor_context(
        allowed_actions=frozenset({"transition.apply", "transition.close"}),
        user_authorized_actions=frozenset({"transition.apply"}),
    )
    broadened_payload = _event_payload(actor=broadened, scope=scope)
    _assert_reducer_error(
        "actor_ineligible",
        lambda: _apply(
            reducer.KernelState(),
            broadened_payload,
            actor=broadened,
            scope=scope,
        ),
    )

    child = _actor_context(
        binding_id="child-1",
        allowed_actions=frozenset({"transition.apply"}),
        user_authorized_actions=frozenset(
            {"transition.apply", "transition.close", "transition.review"}
        ),
        parent_binding_id="parent-1",
        parent_allowed_actions=frozenset(
            {"transition.apply", "transition.close"}
        ),
    )
    child_payload = _event_payload(actor=child, scope=scope)
    assert _apply(
        reducer.KernelState(), child_payload, actor=child, scope=scope
    ).units[0].unit_version == 1

    parent_broadened = _actor_context(
        binding_id="child-2",
        allowed_actions=frozenset({"transition.apply", "transition.close"}),
        user_authorized_actions=frozenset(
            {"transition.apply", "transition.close"}
        ),
        parent_binding_id="parent-1",
        parent_allowed_actions=frozenset({"transition.apply"}),
    )
    parent_payload = _event_payload(actor=parent_broadened, scope=scope)
    _assert_reducer_error(
        "actor_ineligible",
        lambda: _apply(
            reducer.KernelState(),
            parent_payload,
            actor=parent_broadened,
            scope=scope,
        ),
    )


def test_child_binding_rejects_equal_action_set_and_self_parent() -> None:
    scope = _resolved_scope()
    for actor in (
        _actor_context(
            binding_id="child-1",
            parent_binding_id="parent-1",
            parent_allowed_actions=frozenset({"transition.apply"}),
        ),
        _actor_context(
            binding_id="child-1",
            parent_binding_id="child-1",
            parent_allowed_actions=frozenset(
                {"transition.apply", "transition.close"}
            ),
        ),
    ):
        payload = _event_payload(actor=actor, scope=scope)
        _assert_reducer_error(
            "actor_ineligible",
            lambda actor=actor, payload=payload: _apply(
                reducer.KernelState(), payload, actor=actor, scope=scope
            ),
        )


def test_actor_and_scope_string_grammars_are_exact() -> None:
    valid_scope = _resolved_scope()
    invalid_actors = (
        _actor_context(binding_id=""),
        _actor_context(principal=""),
        _actor_context(principal="principal\ncontrol"),
        _actor_context(principal="p" * 257),
        _actor_context(repository="owner//repository"),
        _actor_context(repository="owner/../repository"),
        _actor_context(repository="r" * 257),
        _actor_context(allowed_actions=frozenset({"UPPER"})),
        _actor_context(allowed_actions=frozenset({"a" * 65})),
        _actor_context(
            allowed_actions=frozenset(
                {f"action.{index}" for index in range(65)}
            ),
            user_authorized_actions=frozenset(
                {f"action.{index}" for index in range(65)}
            ),
        ),
    )
    for actor in invalid_actors:
        payload = _event_payload(actor=actor, scope=valid_scope)
        _assert_reducer_error(
            "actor_binding",
            lambda actor=actor, payload=payload: _apply(
                reducer.KernelState(), payload, actor=actor, scope=valid_scope
            ),
        )

    valid_actor = _actor_context()
    invalid_scopes = (
        _resolved_scope(repository="owner//repository"),
        _resolved_scope(repository="owner/./repository"),
        _resolved_scope(repository="r" * 257),
        _resolved_scope(paths=("",)),
        _resolved_scope(paths=("/absolute",)),
        _resolved_scope(paths=("src\\windows",)),
        _resolved_scope(paths=("src//double",)),
        _resolved_scope(paths=("src/./dot",)),
        _resolved_scope(paths=("src/../parent",)),
        _resolved_scope(paths=("src/trailing/",)),
        _resolved_scope(paths=("contains space",)),
        _resolved_scope(paths=tuple(f"src/{index}" for index in range(65))),
        _resolved_scope(lock_domains=("",)),
        _resolved_scope(lock_domains=("contains space",)),
        _resolved_scope(lock_domains=("l" * 129,)),
        _resolved_scope(
            paths=(),
            lock_domains=tuple(f"lock:{index}" for index in range(65)),
        ),
        _resolved_scope(paths=(), lock_domains=()),
    )
    for scope in invalid_scopes:
        payload = _event_payload(actor=valid_actor, scope=scope)
        _assert_reducer_error(
            "scope_invalid",
            lambda scope=scope, payload=payload: _apply(
                reducer.KernelState(), payload, actor=valid_actor, scope=scope
            ),
        )


def test_same_event_replayed_under_other_actor_is_rejected() -> None:
    actor = _actor_context(binding_id="actor-1")
    other = _actor_context(binding_id="actor-2")
    scope = _resolved_scope()
    payload = _event_payload(actor=actor, scope=scope)
    _assert_reducer_error(
        "actor_binding",
        lambda: _apply(
            reducer.KernelState(), payload, actor=other, scope=scope
        ),
    )


def test_actor_resolver_must_repeat_exactly() -> None:
    first = _actor_context(binding_id="actor-1")
    second = _actor_context(binding_id="actor-2")
    scope = _resolved_scope()
    payload = _event_payload(actor=first, scope=scope)
    answers = [first, second]

    _assert_reducer_error(
        "actor_nondeterministic",
        lambda: reducer.reduce_protocol_state(
            [payload],
            resolve_actor=lambda _digest: answers.pop(0),
            resolve_scope=lambda _ref: scope,
            activation=reducer.ActivationState(epoch=0),
        ),
    )


def test_actor_and_scope_resolvers_must_repeat_exactly() -> None:
    actor = _actor_context()
    first = _resolved_scope(paths=("src/unit",), lock_domains=())
    second = _resolved_scope(paths=("src/other",), lock_domains=())
    payload = _event_payload(actor=actor, scope=first)
    answers = [first, second]

    _assert_reducer_error(
        "scope_nondeterministic",
        lambda: reducer.reduce_protocol_state(
            [payload],
            resolve_actor=lambda _digest: actor,
            resolve_scope=lambda _ref: answers.pop(0),
            activation=reducer.ActivationState(epoch=0),
        ),
    )


def test_apply_exact_duplicate_returns_before_resolvers_and_changed_duplicate_conflicts() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    payload = _event_payload(actor=actor, scope=scope)
    state = _apply(reducer.KernelState(), payload, actor=actor, scope=scope)
    calls = 0

    def forbidden_scope(_ref: str) -> reducer.ResolvedScope:
        nonlocal calls
        calls += 1
        raise AssertionError("scope resolver must not run")

    replayed = reducer.apply_transition(
        state,
        payload,
        actor=object(),
        activation=reducer.ActivationState(epoch=0),
        resolve_scope=forbidden_scope,
    )
    assert replayed is state
    assert calls == 0

    changed = dict(payload)
    changed["content_digest"] = _digest("a")
    _assert_reducer_error(
        "transition_id_reuse",
        lambda: reducer.apply_transition(
            state,
            changed,
            actor=object(),
            activation=reducer.ActivationState(epoch=0),
            resolve_scope=forbidden_scope,
        ),
    )
    assert calls == 0


def test_reduce_exact_duplicate_is_idempotent_but_changed_duplicate_conflicts() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    payload = _event_payload(actor=actor, scope=scope)
    actor_calls = 0
    scope_calls = 0

    def resolve_actor(_digest: str) -> reducer.ActorContext:
        nonlocal actor_calls
        actor_calls += 1
        return actor

    def resolve_scope(_ref: str) -> reducer.ResolvedScope:
        nonlocal scope_calls
        scope_calls += 1
        return scope

    report = reducer.reduce_protocol_state(
        [payload, dict(payload)],
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
        activation=reducer.ActivationState(epoch=0),
    )
    assert report.applied_transition_ids == ("transition-1",)
    assert report.idempotent_transition_ids == ("transition-1",)
    assert actor_calls == 2
    assert scope_calls == 2

    changed = dict(payload)
    changed["content_digest"] = _digest("a")
    actor_calls = 0
    scope_calls = 0
    _assert_reducer_error(
        "transition_id_reuse",
        lambda: reducer.reduce_protocol_state(
            [payload, changed],
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
            activation=reducer.ActivationState(epoch=0),
        ),
    )
    assert actor_calls == 0
    assert scope_calls == 0


def test_stale_unit_version_precondition_and_contiguous_work_revision_fail_closed() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    first = _event_payload(actor=actor, scope=scope)
    state = _apply(reducer.KernelState(), first, actor=actor, scope=scope)

    stale_version = _second_payload(state, actor=actor, scope=scope)
    stale_version["expected_unit_version"] = 0
    _assert_reducer_error(
        "expected_version",
        lambda: _apply(state, stale_version, actor=actor, scope=scope),
    )

    stale_precondition = _second_payload(state, actor=actor, scope=scope)
    stale_precondition["precondition_digest"] = _digest("f")
    _assert_reducer_error(
        "precondition",
        lambda: _apply(state, stale_precondition, actor=actor, scope=scope),
    )

    revision_gap = _second_payload(state, actor=actor, scope=scope)
    revision_gap["work_revision"] = 3
    _assert_reducer_error(
        "work_revision",
        lambda: _apply(state, revision_gap, actor=actor, scope=scope),
    )

    first_revision_gap = _event_payload(
        actor=actor,
        scope=scope,
        transition_id="transition-gap",
        work_revision=2,
    )
    _assert_reducer_error(
        "work_revision",
        lambda: _apply(
            reducer.KernelState(), first_revision_gap, actor=actor, scope=scope
        ),
    )


@pytest.mark.parametrize(
    ("first_route", "second_route"),
    ((None, "route-1"), ("route-1", None)),
)
def test_route_identity_including_null_cannot_change(
    first_route: str | None, second_route: str | None
) -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    first = _event_payload(actor=actor, scope=scope, route_id=first_route)
    state = _apply(reducer.KernelState(), first, actor=actor, scope=scope)
    changed = _second_payload(state, actor=actor, scope=scope)
    changed["route_id"] = second_route
    _assert_reducer_error(
        "route_ambiguity",
        lambda: _apply(state, changed, actor=actor, scope=scope),
    )


@pytest.mark.parametrize(
    ("unit_id", "route_id"),
    ((None, "route-1"), ("unit-1", None)),
)
def test_post_state_precondition_is_recomputed_for_sequential_transitions(
    unit_id: str | None, route_id: str | None
) -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    first = _event_payload(
        actor=actor,
        scope=scope,
        unit_id=unit_id,
        route_id=route_id,
    )
    state = _apply(reducer.KernelState(), first, actor=actor, scope=scope)
    second = _second_payload(state, actor=actor, scope=scope)
    second_state = _apply(state, second, actor=actor, scope=scope)

    assert second_state.units[0].unit_version == 1
    assert second_state.units[0].precondition_digest == _precondition_digest(
        work_id="work-1",
        unit_id=unit_id,
        unit_version=1,
        mutable_scope_digest=_scope_digest(scope),
        content_digest=_digest("4"),
        dependency_digest=_digest("5"),
        acceptance_digest=_digest("6"),
        evidence_digest=_evidence_digest(()),
    )


@pytest.mark.parametrize(
    "changed_field",
    ("content_digest", "dependency_digest", "acceptance_digest", "evidence_refs"),
)
def test_relevant_digest_change_alone_bumps_unit_version(changed_field: str) -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    first = _event_payload(actor=actor, scope=scope)
    state = _apply(reducer.KernelState(), first, actor=actor, scope=scope)
    changed_value: object = (
        ["artifact:changed"] if changed_field == "evidence_refs" else _digest("a")
    )
    second = _second_payload(
        state,
        actor=actor,
        scope=scope,
        **{changed_field: changed_value},
    )
    changed_state = _apply(state, second, actor=actor, scope=scope)
    assert changed_state.units[0].unit_version == 2

    label_only = _second_payload(
        state,
        actor=actor,
        scope=scope,
        requested_transition="BLOCK",
    )
    label_state = _apply(state, label_only, actor=actor, scope=scope)
    assert label_state.units[0].unit_version == 1


def test_scope_digest_and_repository_binding_are_required() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    bad_digest = _event_payload(actor=actor, scope=scope)
    bad_digest["mutable_scope_digest"] = _digest("f")
    _assert_reducer_error(
        "scope_digest",
        lambda: _apply(
            reducer.KernelState(), bad_digest, actor=actor, scope=scope
        ),
    )

    other_scope = _resolved_scope(repository="owner/other")
    repository_mismatch = _event_payload(actor=actor, scope=other_scope)
    _assert_reducer_error(
        "actor_binding",
        lambda: _apply(
            reducer.KernelState(),
            repository_mismatch,
            actor=actor,
            scope=other_scope,
        ),
    )


def test_scope_is_immutable_for_one_unit() -> None:
    actor = _actor_context()
    scope = _resolved_scope(paths=("src/unit",), lock_domains=("lock:unit",))
    first = _event_payload(actor=actor, scope=scope)
    state = _apply(reducer.KernelState(), first, actor=actor, scope=scope)
    changed_scope = _resolved_scope(
        paths=("src/other",), lock_domains=("lock:other",)
    )
    second = _second_payload(
        state,
        actor=actor,
        scope=changed_scope,
        mutable_scope_ref="scope:work-1/other",
        mutable_scope_digest=_scope_digest(changed_scope),
    )
    _assert_reducer_error(
        "scope_invalid",
        lambda: _apply(state, second, actor=actor, scope=changed_scope),
    )


def test_component_ancestry_redundancy_and_lock_overlap_fail() -> None:
    actor = _actor_context()
    redundant = _resolved_scope(
        paths=("src/a", "src/a/file.py"), lock_domains=()
    )
    redundant_payload = _event_payload(actor=actor, scope=redundant)
    _assert_reducer_error(
        "scope_invalid",
        lambda: _apply(
            reducer.KernelState(), redundant_payload, actor=actor, scope=redundant
        ),
    )

    first_scope = _resolved_scope(paths=("src/a",), lock_domains=("lock:a",))
    first = _event_payload(actor=actor, scope=first_scope)
    state = _apply(reducer.KernelState(), first, actor=actor, scope=first_scope)

    ancestor_scope = _resolved_scope(
        paths=("src/a/file.py",), lock_domains=("lock:b",)
    )
    ancestor = _event_payload(
        actor=actor,
        scope=ancestor_scope,
        work_id="work-2",
        transition_id="transition-2",
        route_id="route-2",
        unit_id="unit-2",
        mutable_scope_ref="scope:work-2/unit-2",
    )
    _assert_reducer_error(
        "scope_overlap",
        lambda: _apply(state, ancestor, actor=actor, scope=ancestor_scope),
    )

    sibling_scope = _resolved_scope(
        paths=("src/ab",), lock_domains=("lock:a",)
    )
    sibling = _event_payload(
        actor=actor,
        scope=sibling_scope,
        work_id="work-2",
        transition_id="transition-3",
        route_id="route-2",
        unit_id="unit-2",
        mutable_scope_ref="scope:work-2/unit-2",
    )
    _assert_reducer_error(
        "scope_overlap",
        lambda: _apply(state, sibling, actor=actor, scope=sibling_scope),
    )

    disjoint_scope = _resolved_scope(
        paths=("src/ab",), lock_domains=("lock:b",)
    )
    disjoint = _event_payload(
        actor=actor,
        scope=disjoint_scope,
        work_id="work-2",
        transition_id="transition-4",
        route_id="route-2",
        unit_id="unit-2",
        mutable_scope_ref="scope:work-2/unit-2",
    )
    merged = _apply(state, disjoint, actor=actor, scope=disjoint_scope)
    assert tuple(unit.work_id for unit in merged.units) == ("work-1", "work-2")


def test_nullable_and_string_units_have_total_order() -> None:
    actor = _actor_context()
    null_scope = _resolved_scope(paths=("src/null",), lock_domains=("lock:null",))
    named_scope = _resolved_scope(
        paths=("src/named",), lock_domains=("lock:named",)
    )
    null_payload = _event_payload(
        actor=actor,
        scope=null_scope,
        unit_id=None,
        mutable_scope_ref="scope:work-1/null",
    )
    null_state = _apply(
        reducer.KernelState(), null_payload, actor=actor, scope=null_scope
    )
    named_payload = _event_payload(
        actor=actor,
        scope=named_scope,
        transition_id="transition-2",
        work_revision=2,
        unit_id="unit-1",
        expected_unit_version=0,
        mutable_scope_ref="scope:work-1/unit-1",
    )
    named_state = _apply(
        null_state, named_payload, actor=actor, scope=named_scope
    )
    assert tuple(unit.unit_id for unit in named_state.units) == (None, "unit-1")
    assert reducer.unit_key("work-1", None) < reducer.unit_key("work-1", "unit-1")


def test_request_close_verification_and_effect_refs_remain_observations() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    payload = _event_payload(
        actor=actor,
        scope=scope,
        requested_transition="REQUEST_CLOSE",
        verification_ref="verification:review-1",
        effect_reservation_refs=("reservation:one", "reservation:two"),
    )
    report = reducer.reduce_protocol_state(
        [payload],
        resolve_actor=lambda _digest: actor,
        resolve_scope=lambda _ref: scope,
        activation=reducer.ActivationState(epoch=0),
    )
    assert report.mode == "shadow"
    assert report.applied_transition_ids == ("transition-1",)
    assert tuple(field.name for field in dataclasses.fields(report)) == (
        "mode",
        "state_digest",
        "applied_transition_ids",
        "idempotent_transition_ids",
        "units",
    )


def test_web_research_reference_is_opaque_observation_only() -> None:
    actor = _actor_context()
    scope = _resolved_scope()
    source = "web:https://example.test/source@2026-07-15"
    payload = _event_payload(
        actor=actor,
        scope=scope,
        evidence_refs=(source,),
    )
    report = reducer.reduce_protocol_state(
        [payload],
        resolve_actor=lambda _digest: actor,
        resolve_scope=lambda _ref: scope,
        activation=reducer.ActivationState(epoch=0),
    )
    assert report.units[0].evidence_digest == _evidence_digest((source,))
    assert source not in repr(report)
    assert report.mode == "shadow"
