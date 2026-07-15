from __future__ import annotations

import ast
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
    assert reducer.parse_transition(exact_boundaries).work_revision == reducer.MAX_INT

    for field, overlong in (
        ("work_id", "w" * 129),
        ("mutable_scope_ref", "r" * 513),
    ):
        value = _valid_payload()
        value[field] = overlong
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
    tree = ast.parse(source)
    imported_names: dict[str, str] = {}
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
                imported_names[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_modules.add(module)
            for alias in node.names:
                imported_names[alias.asname or alias.name] = module

    assert imported_modules <= set(PERMITTED_IMPORT_MODULES)

    imported_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in imported_names
    }
    assert imported_calls <= set(PERMITTED_IMPORTED_CALL_NAMES)

    forbidden_dynamic_calls = {"open", "exec", "eval", "compile", "__import__"}
    assert not {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id in forbidden_dynamic_calls
    }
    assert not {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in forbidden_dynamic_calls
    }
