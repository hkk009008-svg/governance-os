from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from re import fullmatch
from typing import Callable

import pytest

from scripts import capability_reducer as reducer
from threeway.canon import canonicalize


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    ROOT / "tests" / "fixtures" / "compact_kernel" / "v2_replay_vectors.json"
)
FIXTURE_FIELDS = frozenset({"schema_version", "actors", "scopes", "vectors"})
ACTOR_FIELDS = frozenset(
    {
        "binding_id",
        "binding_digest",
        "repository",
        "principal",
        "allowed_actions",
        "user_authorized_actions",
        "parent_binding_id",
        "parent_allowed_actions",
        "attested",
        "expired",
        "revoked",
    }
)
SCOPE_FIELDS = frozenset({"repository", "paths", "lock_domains"})
VECTOR_FIELDS = frozenset({"id", "events", "permutations", "expected"})
REPORT_EXPECTED_FIELDS = frozenset(
    {"applied_transition_ids", "idempotent_transition_ids", "units"}
)
UNIT_EXPECTED_FIELDS = frozenset({"work_id", "unit_id", "unit_version"})
ERROR_EXPECTED_FIELDS = frozenset({"error_code"})
STABLE_ERROR_CODES = frozenset(
    {
        "invalid_envelope",
        "state_invalid",
        "actor_binding",
        "actor_ineligible",
        "actor_nondeterministic",
        "activation_epoch",
        "expected_version",
        "precondition",
        "work_revision",
        "route_ambiguity",
        "scope_invalid",
        "scope_digest",
        "scope_nondeterministic",
        "scope_overlap",
        "transition_id_reuse",
    }
)
EXPECTED_VECTOR_IDS = frozenset(
    {
        "independent_order_a",
        "independent_order_b",
        "exact_duplicate_collapses",
        "changed_duplicate_conflicts",
        "stale_expected_version",
        "stale_activation_epoch",
        "actor_cross_binding_replay",
        "disjoint_scopes_merge",
        "ancestor_scope_overlap",
        "lock_domain_overlap",
        "scope_digest_mismatch",
        "same_unit_scope_change_conflicts",
        "route_null_to_named_conflicts",
        "work_revision_gap",
        "nullable_and_string_units_order",
        "changed_dependency_bumps_version",
        "equivalent_ref_order_normalizes",
        "web_research_observation",
        "request_close_is_observation",
    }
)
REPORT_FIELDS = (
    "mode",
    "state_digest",
    "applied_transition_ids",
    "idempotent_transition_ids",
    "units",
)
UNIT_FIELDS = (
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
)
FORBIDDEN_AUTHORITY_NAMES = frozenset(
    {
        "go",
        "done",
        "verdict",
        "terminal",
        "authority",
        "authorized",
        "effect_eligible",
        "effect_eligibility",
    }
)


def _canonical_digest(value: object) -> str:
    return "sha256:" + sha256(canonicalize(value)).hexdigest()


def _require_exact_fields(
    value: object,
    expected: frozenset[str],
    label: str,
) -> dict[str, object]:
    assert type(value) is dict, f"{label} must be an object"
    assert all(type(key) is str for key in value), f"{label} keys must be strings"
    assert set(value) == expected, f"{label} fields must be exact"
    return value


def _require_string_list(value: object, label: str) -> list[str]:
    assert type(value) is list, f"{label} must be a list"
    assert all(type(item) is str for item in value), f"{label} items must be strings"
    assert len(value) == len(set(value)), f"{label} items must be unique"
    assert value == sorted(value), f"{label} must be normalized"
    return value


def _actor_from_fixture(value: object, label: str) -> reducer.ActorContext:
    raw = _require_exact_fields(value, ACTOR_FIELDS, label)
    for field in (
        "binding_id",
        "binding_digest",
        "repository",
        "principal",
    ):
        assert type(raw[field]) is str, f"{label}.{field} must be a string"
    assert fullmatch(reducer.DIGEST_PATTERN, raw["binding_digest"]) is not None
    allowed_actions = _require_string_list(
        raw["allowed_actions"], f"{label}.allowed_actions"
    )
    user_actions = _require_string_list(
        raw["user_authorized_actions"],
        f"{label}.user_authorized_actions",
    )
    parent_id = raw["parent_binding_id"]
    assert parent_id is None or type(parent_id) is str
    parent_raw = raw["parent_allowed_actions"]
    if parent_raw is None:
        parent_actions = None
    else:
        parent_actions = _require_string_list(
            parent_raw,
            f"{label}.parent_allowed_actions",
        )
    for field in ("attested", "expired", "revoked"):
        assert type(raw[field]) is bool, f"{label}.{field} must be a boolean"

    digest_mapping = {
        "binding_id": raw["binding_id"],
        "repository": raw["repository"],
        "principal": raw["principal"],
        "allowed_actions": allowed_actions,
        "user_authorized_actions": user_actions,
        "parent_binding_id": parent_id,
        "parent_allowed_actions": parent_actions,
        "attested": raw["attested"],
        "expired": raw["expired"],
        "revoked": raw["revoked"],
    }
    assert raw["binding_digest"] == _canonical_digest(digest_mapping), (
        f"{label}.binding_digest must be recomputed from every canonical field"
    )
    return reducer.ActorContext(
        binding_id=raw["binding_id"],
        binding_digest=raw["binding_digest"],
        repository=raw["repository"],
        principal=raw["principal"],
        allowed_actions=frozenset(allowed_actions),
        user_authorized_actions=frozenset(user_actions),
        parent_binding_id=parent_id,
        parent_allowed_actions=(
            None if parent_actions is None else frozenset(parent_actions)
        ),
        attested=raw["attested"],
        expired=raw["expired"],
        revoked=raw["revoked"],
    )


def _scope_from_fixture(value: object, label: str) -> reducer.ResolvedScope:
    raw = _require_exact_fields(value, SCOPE_FIELDS, label)
    assert type(raw["repository"]) is str, f"{label}.repository must be a string"
    paths = _require_string_list(raw["paths"], f"{label}.paths")
    locks = _require_string_list(raw["lock_domains"], f"{label}.lock_domains")
    return reducer.ResolvedScope(
        repository=raw["repository"],
        paths=tuple(paths),
        lock_domains=tuple(locks),
    )


def _load_fixture(path: Path = FIXTURE_PATH) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    fixture = _require_exact_fields(raw, FIXTURE_FIELDS, "fixture")
    assert fixture["schema_version"] == "compact-kernel-replay/v2"

    actor_values = fixture["actors"]
    assert type(actor_values) is dict and actor_values, "actors must be an object"
    actors: dict[str, reducer.ActorContext] = {}
    for lookup_digest, value in actor_values.items():
        assert type(lookup_digest) is str
        assert fullmatch(reducer.DIGEST_PATTERN, lookup_digest) is not None
        actors[lookup_digest] = _actor_from_fixture(
            value,
            f"actors[{lookup_digest!r}]",
        )

    scope_values = fixture["scopes"]
    assert type(scope_values) is dict and scope_values, "scopes must be an object"
    scopes: dict[str, reducer.ResolvedScope] = {}
    for scope_ref, value in scope_values.items():
        assert type(scope_ref) is str and fullmatch(reducer.REF_PATTERN, scope_ref)
        scopes[scope_ref] = _scope_from_fixture(
            value,
            f"scopes[{scope_ref!r}]",
        )

    vector_values = fixture["vectors"]
    assert type(vector_values) is list and vector_values, "vectors must be a list"
    vectors: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for index, value in enumerate(vector_values):
        vector = _require_exact_fields(value, VECTOR_FIELDS, f"vectors[{index}]")
        vector_id = vector["id"]
        assert type(vector_id) is str and fullmatch(reducer.ID_PATTERN, vector_id)
        assert vector_id not in seen_ids, "vector IDs must be unique"
        seen_ids.add(vector_id)

        events = vector["events"]
        assert type(events) is dict and events, f"{vector_id}.events must be an object"
        for event_label, event in events.items():
            assert type(event_label) is str and fullmatch(
                reducer.ID_PATTERN, event_label
            )
            reducer.parse_transition(event)

        permutations = vector["permutations"]
        assert type(permutations) is list and permutations
        for permutation in permutations:
            assert type(permutation) is list and permutation
            assert all(type(label) is str and label in events for label in permutation)
            assert set(permutation) == set(events), (
                f"{vector_id} permutation must cover every declared event"
            )

        expected = vector["expected"]
        assert type(expected) is dict
        if set(expected) == ERROR_EXPECTED_FIELDS:
            assert expected["error_code"] in STABLE_ERROR_CODES
        else:
            _require_exact_fields(
                expected,
                REPORT_EXPECTED_FIELDS,
                f"{vector_id}.expected",
            )
            for field in ("applied_transition_ids", "idempotent_transition_ids"):
                identifiers = _require_string_list(
                    expected[field],
                    f"{vector_id}.expected.{field}",
                )
                assert all(fullmatch(reducer.ID_PATTERN, item) for item in identifiers)
            units = expected["units"]
            assert type(units) is list
            unit_keys: list[tuple[str, int, str]] = []
            for unit_index, unit_value in enumerate(units):
                unit = _require_exact_fields(
                    unit_value,
                    UNIT_EXPECTED_FIELDS,
                    f"{vector_id}.expected.units[{unit_index}]",
                )
                assert type(unit["work_id"]) is str
                assert unit["unit_id"] is None or type(unit["unit_id"]) is str
                assert type(unit["unit_version"]) is int and unit["unit_version"] >= 1
                unit_keys.append(reducer.unit_key(unit["work_id"], unit["unit_id"]))
            assert unit_keys == sorted(unit_keys), "expected units must be ordered"
        vectors.append(vector)

    assert seen_ids == EXPECTED_VECTOR_IDS, "the replay corpus must be complete"
    return {"actors": actors, "scopes": scopes, "vectors": vectors}


def _unit_mapping(unit: reducer.UnitSnapshot) -> dict[str, object]:
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


def _report_mapping(report: reducer.KernelReport) -> dict[str, object]:
    return {
        "mode": report.mode,
        "state_digest": report.state_digest,
        "applied_transition_ids": list(report.applied_transition_ids),
        "idempotent_transition_ids": list(report.idempotent_transition_ids),
        "units": [_unit_mapping(unit) for unit in report.units],
    }


def _resolvers(
    fixture: dict[str, object],
) -> tuple[
    Callable[[str], reducer.ActorContext],
    Callable[[str], reducer.ResolvedScope],
]:
    actors = fixture["actors"]
    scopes = fixture["scopes"]
    assert type(actors) is dict and type(scopes) is dict

    def resolve_actor(binding_digest: str) -> reducer.ActorContext:
        return actors[binding_digest]

    def resolve_scope(scope_ref: str) -> reducer.ResolvedScope:
        return scopes[scope_ref]

    return resolve_actor, resolve_scope


def _vector_by_id(fixture: dict[str, object], vector_id: str) -> dict[str, object]:
    vectors = fixture["vectors"]
    assert type(vectors) is list
    return next(vector for vector in vectors if vector["id"] == vector_id)


def _reduce_labels(
    fixture: dict[str, object],
    vector: dict[str, object],
    labels: list[str],
) -> reducer.KernelReport:
    events = vector["events"]
    assert type(events) is dict
    resolve_actor, resolve_scope = _resolvers(fixture)
    return reducer.reduce_protocol_state(
        [events[label] for label in labels],
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
        activation=reducer.ActivationState(epoch=0),
    )


def _assert_expected_report(
    report: reducer.KernelReport,
    expected: dict[str, object],
) -> None:
    assert report.applied_transition_ids == tuple(expected["applied_transition_ids"])
    assert report.idempotent_transition_ids == tuple(
        expected["idempotent_transition_ids"]
    )
    actual_units = [
        {
            "work_id": unit.work_id,
            "unit_id": unit.unit_id,
            "unit_version": unit.unit_version,
        }
        for unit in report.units
    ]
    assert actual_units == expected["units"]


def _successful_vector_bytes(
    fixture: dict[str, object],
    vector: dict[str, object],
) -> tuple[bytes, ...]:
    expected = vector["expected"]
    permutations = vector["permutations"]
    assert type(expected) is dict and set(expected) == REPORT_EXPECTED_FIELDS
    assert type(permutations) is list
    results: list[bytes] = []
    for labels in permutations:
        report = _reduce_labels(fixture, vector, labels)
        _assert_expected_report(report, expected)
        mapping = _report_mapping(report)
        assert tuple(mapping) == REPORT_FIELDS
        assert tuple(mapping["units"][0]) == UNIT_FIELDS if mapping["units"] else True
        results.append(canonicalize(mapping))
    assert len(set(results)) == 1, f"{vector['id']} permutations diverged"
    return tuple(results)


def test_replay_fixture_is_strict_complete_and_every_vector_is_stable() -> None:
    fixture = _load_fixture()
    vectors = fixture["vectors"]
    assert type(vectors) is list

    for vector in vectors:
        expected = vector["expected"]
        permutations = vector["permutations"]
        assert type(expected) is dict and type(permutations) is list
        if set(expected) == ERROR_EXPECTED_FIELDS:
            for labels in permutations:
                report = None
                with pytest.raises(reducer.ReducerError) as exc_info:
                    report = _reduce_labels(fixture, vector, labels)
                assert report is None
                assert exc_info.value.code == expected["error_code"]
        else:
            _successful_vector_bytes(fixture, vector)


def test_independent_reversed_vectors_have_identical_report_bytes() -> None:
    fixture = _load_fixture()
    left = _vector_by_id(fixture, "independent_order_a")
    right = _vector_by_id(fixture, "independent_order_b")

    assert _successful_vector_bytes(fixture, left)[0] == (
        _successful_vector_bytes(fixture, right)[0]
    )


@pytest.mark.parametrize(
    "layer",
    ("fixture", "vector", "expected"),
)
def test_loader_rejects_unknown_fields_and_authority_smuggling(
    tmp_path: Path,
    layer: str,
) -> None:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    mutated = deepcopy(raw)
    if layer == "fixture":
        mutated["authority"] = "GO"
    elif layer == "vector":
        mutated["vectors"][0]["verdict"] = "GO"
    else:
        mutated["vectors"][0]["expected"]["effect_eligible"] = True
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(mutated), encoding="utf-8")

    with pytest.raises(AssertionError, match="fields must be exact"):
        _load_fixture(path)


def test_web_research_observation_changes_only_observational_unit_state() -> None:
    fixture = _load_fixture()
    vector = _vector_by_id(fixture, "web_research_observation")
    events = vector["events"]
    assert type(events) is dict
    initial = events["initial"]
    update = events["web_update"]
    assert type(initial) is dict and type(update) is dict
    assert update["evidence_refs"] == [
        "web:https://example.test/source@2026-07-15"
    ]
    for field in (
        "actor_binding_digest",
        "mutable_scope_ref",
        "mutable_scope_digest",
        "content_digest",
        "dependency_digest",
        "acceptance_digest",
    ):
        assert update[field] == initial[field]

    first_report = _reduce_labels(fixture, vector, ["initial"])
    final_report = _reduce_labels(fixture, vector, ["initial", "web_update"])
    first_unit = _unit_mapping(first_report.units[0])
    final_unit = _unit_mapping(final_report.units[0])
    assert final_unit["unit_version"] == first_unit["unit_version"] + 1
    assert final_unit["evidence_digest"] != first_unit["evidence_digest"]
    assert final_unit["precondition_digest"] != first_unit["precondition_digest"]
    for field in set(UNIT_FIELDS) - {
        "unit_version",
        "evidence_digest",
        "precondition_digest",
    }:
        assert final_unit[field] == first_unit[field]
    assert "web:https://example.test/source@2026-07-15" not in repr(final_report)
    assert not (set(_report_mapping(final_report)) & FORBIDDEN_AUTHORITY_NAMES)


def test_request_close_vector_remains_observation_only() -> None:
    fixture = _load_fixture()
    vector = _vector_by_id(fixture, "request_close_is_observation")
    events = vector["events"]
    permutations = vector["permutations"]
    assert type(events) is dict and type(permutations) is list
    event = events["request_close"]
    assert event["requested_transition"] == "REQUEST_CLOSE"
    assert event["verification_ref"] == "verification:review-1"
    assert event["effect_reservation_refs"] == ["reservation:one"]

    report = _reduce_labels(fixture, vector, permutations[0])
    mapping = _report_mapping(report)
    assert tuple(mapping) == REPORT_FIELDS
    assert mapping["mode"] == "shadow"
    assert "REQUEST_CLOSE" not in repr(report)
    assert "verification:review-1" not in repr(report)
    assert "reservation:one" not in repr(report)
    assert not (set(mapping) & FORBIDDEN_AUTHORITY_NAMES)
