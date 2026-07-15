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
    ("typing", ("Callable", "Iterable")),
    ("threeway.canon", ("canonicalize",)),
)
PERMITTED_NAME_CALLS = (
    "NotImplementedError",
    "ReducerError",
    "TransitionEnvelope",
    "_integer_schema",
    "_nullable_string_schema",
    "_ref_array_schema",
    "_require_integer",
    "_require_nullable_string",
    "_require_refs",
    "_require_string",
    "_string_schema",
    "_unchecked_transition_mapping",
    "any",
    "canonicalize",
    "dataclass",
    "frozenset",
    "fullmatch",
    "len",
    "list",
    "parse_transition",
    "set",
    "sha256",
    "sorted",
    "transition_bytes",
    "transition_mapping",
    "tuple",
    "type",
)
PERMITTED_ATTRIBUTE_CALLS = (
    ("ValueError", "__init__"),
    ("digest", "hexdigest"),
)


def _ast_purity_violations(source: str) -> list[str]:
    tree = ast.parse(source)
    violations: list[str] = []
    actual_from_imports: list[tuple[str, tuple[str, ...]]] = []
    imported_names: set[str] = set()

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
            imported_names.update(alias.asname or alias.name for alias in node.names)
            if node.level != 0 or module not in PERMITTED_IMPORT_MODULES:
                violations.append(f"from-import module is not permitted: {module}")
            if any(
                alias.asname is not None or alias.name == "*" for alias in node.names
            ):
                violations.append(f"from-import aliases are not permitted: {module}")

    if tuple(actual_from_imports) != PERMITTED_FROM_IMPORTS:
        violations.append("from-import shape does not match the literal contract")

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "__builtins__":
            violations.append("dynamic builtin namespace access is not permitted")
        if not isinstance(node, ast.Call):
            continue

        function = node.func
        if isinstance(function, ast.Name):
            if function.id not in PERMITTED_NAME_CALLS:
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
