from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import subprocess
import sys
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from scripts import capability_reducer as reducer
from scripts import capability_v1_adapter as adapter
from scripts import compact_state_mapping
from threeway.canon import canonicalize


LEGACY_SCHEMA = "compact-kernel-legacy-observation/v1"
LEGACY_FIELDS = (
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
ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "tests/fixtures/compact_kernel/v1_to_v2_replay.json"
MAPPING_FIXTURE = ROOT / "tests/fixtures/compact_state_mapping/v1.json"
MISUSE_FIXTURE = ROOT / "tests/fixtures/compact_kernel/v1_misuse_vectors.json"
REDUCER_REPLAY_FIXTURE = (
    ROOT / "tests/fixtures/compact_kernel/v2_replay_vectors.json"
)
CORPUS_FIELDS = frozenset(
    {
        "schema_version",
        "sources",
        "actors",
        "scopes",
        "case_manifest",
        "cases",
        "phase2_misuse_bindings",
        "deferred_phase3_misuse_ids",
        "reducer_replay_ids",
    }
)
CASE_FIELDS = frozenset(
    {
        "id",
        "case_kind",
        "mapping_row_id",
        "misuse_vector_id",
        "disposition",
        "source_records",
        "record_orders",
        "resolver_mode",
        "expected",
    }
)
PROJECTION_FIELDS = frozenset(
    {
        "disposition",
        "compact",
        "terminal_scope",
        "next_action",
        "effect_eligibility",
        "advisory_only",
    }
)
EXPECTED_PARITY_KINDS = frozenset(
    {
        "match",
        "compact_more_permissive",
        "compact_more_restrictive",
        "authority_semantic_mismatch",
        "non_authority_only",
        "adapter_error",
    }
)


def test_adapter_public_surface_is_exact() -> None:
    assert adapter.__all__ == (
        "LegacyAdapterError",
        "adapt_v1_history",
        "main",
    )


def _digest(character: str) -> str:
    return "sha256:" + (character * 64)


def _canonical_digest(value: object) -> str:
    return "sha256:" + sha256(canonicalize(value)).hexdigest()


def _valid_legacy_record(**updates: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema": LEGACY_SCHEMA,
        "source_id": "capacity:work-1:1",
        "work_id": "work-1",
        "route_id": "route-1",
        "work_revision": 1,
        "unit_id": "unit-1",
        "actor_binding_digest": _digest("1"),
        "domain": "capacity",
        "value": "ready",
        "context": {},
        "mutable_scope_ref": "scope:work-1/unit-1",
        "mutable_scope_digest": _digest("2"),
        "content_digest": _digest("3"),
        "dependency_digest": _digest("4"),
        "acceptance_digest": _digest("5"),
        "evidence_refs": [
            "artifact:one",
            "web:not-interpreted-or-fetched",
        ],
        "verification_ref": None,
        "effect_reservation_refs": [],
    }
    record.update(updates)
    record_without_digest = {
        key: value for key, value in record.items() if key != "source_digest"
    }
    record["source_digest"] = _canonical_digest(record_without_digest)
    return record


def _forbidden_resolver(_value: str) -> object:
    pytest.fail("Task 1 must not call host resolvers")


def _assert_adapter_error(
    code: str,
    records: object,
) -> adapter.LegacyAdapterError:
    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            records,
            resolve_actor=_forbidden_resolver,
            resolve_scope=_forbidden_resolver,
        )
    assert exc_info.value.code == code
    assert str(exc_info.value) == code
    return exc_info.value


def test_empty_history_returns_no_envelopes_without_calling_resolvers() -> None:
    assert adapter.adapt_v1_history(
        [],
        resolve_actor=_forbidden_resolver,
        resolve_scope=_forbidden_resolver,
    ) == ()


def test_valid_specialized_record_finishes_parsing_then_fails_unmapped() -> None:
    _assert_adapter_error(
        "legacy_unmapped",
        [_valid_legacy_record(domain="capability", value="issued")],
    )


@pytest.mark.parametrize(
    "forbidden",
    (
        "transition_id",
        "requested_transition",
        "expected_unit_version",
        "precondition_digest",
        "activation_epoch",
        "principal",
        "actor",
        "verdict",
        "effect_eligible",
        "mode",
        "writer",
    ),
)
def test_legacy_record_rejects_authority_and_derived_fields(
    forbidden: str,
) -> None:
    record = _valid_legacy_record()
    record[forbidden] = "forbidden"

    _assert_adapter_error("legacy_invalid", [record])


@pytest.mark.parametrize("explicit_epoch", (0, 1, False))
def test_legacy_record_rejects_every_explicit_epoch(
    explicit_epoch: object,
) -> None:
    record = _valid_legacy_record()
    record["activation_epoch"] = explicit_epoch

    _assert_adapter_error("legacy_invalid", [record])


@pytest.mark.parametrize("record", (None, "record", [], 1, True))
def test_legacy_record_must_be_an_exact_object(record: object) -> None:
    _assert_adapter_error("legacy_invalid", [record])


@pytest.mark.parametrize("mutation", ("missing", "extra"))
def test_legacy_record_requires_exact_keys(mutation: str) -> None:
    record = _valid_legacy_record()
    assert set(record) == set(LEGACY_FIELDS)
    if mutation == "missing":
        del record["verification_ref"]
    else:
        record["unexpected"] = "value"

    _assert_adapter_error("legacy_invalid", [record])


def test_strict_json_loader_rejects_duplicate_keys_without_raw_content() -> None:
    duplicate = '{"schema":"first","schema":"raw-secret"}'

    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter._strict_json_loads(duplicate)

    assert exc_info.value.code == "legacy_invalid"
    assert str(exc_info.value) == "legacy_invalid"
    assert "raw-secret" not in str(exc_info.value)


def test_strict_json_loader_preserves_one_exact_object() -> None:
    raw = json.dumps(_valid_legacy_record(), separators=(",", ":"))

    assert adapter._strict_json_loads(raw) == _valid_legacy_record()


@pytest.mark.parametrize(
    "work_revision",
    (False, True, 0, -1, reducer.MAX_INT + 1, 1.0, "1"),
)
def test_legacy_record_rejects_bool_as_int_and_invalid_revisions(
    work_revision: object,
) -> None:
    record = _valid_legacy_record()
    record["work_revision"] = work_revision

    _assert_adapter_error("legacy_invalid", [record])


@pytest.mark.parametrize(
    ("field", "invalid"),
    (
        ("source_id", "bad source"),
        ("work_id", "bad work"),
        ("route_id", "bad route"),
        ("route_id", False),
        ("unit_id", "bad unit"),
        ("unit_id", False),
        ("actor_binding_digest", "sha256:1"),
        ("mutable_scope_ref", ""),
        ("mutable_scope_ref", "scope:\nsecret"),
        ("mutable_scope_digest", "sha256:2"),
        ("content_digest", "sha256:3"),
        ("dependency_digest", "sha256:4"),
        ("acceptance_digest", "sha256:5"),
        ("verification_ref", ""),
        ("verification_ref", "verification:\nsecret"),
    ),
)
def test_legacy_record_rejects_invalid_identifier_ref_and_digest_syntax(
    field: str,
    invalid: object,
) -> None:
    _assert_adapter_error("legacy_invalid", [_valid_legacy_record(**{field: invalid})])


@pytest.mark.parametrize(
    ("field", "invalid"),
    (
        ("evidence_refs", "artifact:one"),
        ("evidence_refs", ["artifact:one", "artifact:one"]),
        ("evidence_refs", ["artifact:\nsecret"]),
        ("evidence_refs", [f"artifact:{index}" for index in range(65)]),
        ("effect_reservation_refs", "reservation:one"),
        ("effect_reservation_refs", ["reservation:one", "reservation:one"]),
        ("effect_reservation_refs", ["reservation:\nsecret"]),
        (
            "effect_reservation_refs",
            [f"reservation:{index}" for index in range(65)],
        ),
    ),
)
def test_legacy_record_rejects_invalid_reference_collections(
    field: str,
    invalid: object,
) -> None:
    _assert_adapter_error("legacy_invalid", [_valid_legacy_record(**{field: invalid})])


@pytest.mark.parametrize(
    "schema",
    (
        "compact-kernel-legacy-observation/v2",
        reducer.SCHEMA_ID,
        "governance.route/v1",
        "unknown/v1",
    ),
)
def test_legacy_record_rejects_future_raw_route_and_unknown_schemas(
    schema: str,
) -> None:
    _assert_adapter_error("legacy_version", [_valid_legacy_record(schema=schema)])


def test_legacy_record_rejects_non_string_schema() -> None:
    _assert_adapter_error("legacy_invalid", [_valid_legacy_record(schema=1)])


def test_raw_route_v2_object_is_rejected_at_the_version_boundary() -> None:
    raw_route = {field: None for field in reducer.ENVELOPE_FIELDS}
    raw_route["schema"] = reducer.SCHEMA_ID

    _assert_adapter_error("legacy_version", [raw_route])


@pytest.mark.parametrize(
    ("updates", "code"),
    (
        ({"domain": "unknown"}, "legacy_unmapped"),
        ({"value": "unknown"}, "legacy_unmapped"),
        ({"context": {"unexpected": True}}, "legacy_unmapped"),
        (
            {
                "value": "blocked",
                "context": {
                    "completion_evidence": 1,
                    "verification_required": False,
                },
            },
            "legacy_invalid",
        ),
        ({"domain": 1}, "legacy_invalid"),
        ({"value": 1}, "legacy_invalid"),
        ({"context": []}, "legacy_invalid"),
    ),
)
def test_legacy_record_rejects_unknown_domain_value_and_context(
    updates: dict[str, object],
    code: str,
) -> None:
    _assert_adapter_error(code, [_valid_legacy_record(**updates)])


def test_legacy_record_rejects_source_digest_mismatch() -> None:
    record = _valid_legacy_record()
    record["source_digest"] = _digest("f")

    _assert_adapter_error("legacy_invalid", [record])


def test_legacy_record_rejects_invalid_source_digest_syntax() -> None:
    record = _valid_legacy_record()
    record["source_digest"] = "sha256:short"

    _assert_adapter_error("legacy_invalid", [record])


@pytest.mark.parametrize(
    ("field", "normalized_refs"),
    (
        ("evidence_refs", ("artifact:one", "web:two")),
        (
            "effect_reservation_refs",
            ("reservation:one", "reservation:two"),
        ),
    ),
)
def test_source_digest_uses_normalized_reference_order(
    field: str,
    normalized_refs: tuple[str, str],
) -> None:
    normalized = _valid_legacy_record(
        domain="capability",
        value="issued",
        **{field: list(normalized_refs)},
    )
    normalized_digest = normalized["source_digest"]

    reversed_with_normalized_digest = dict(normalized)
    reversed_with_normalized_digest[field] = list(reversed(normalized_refs))
    _assert_adapter_error(
        "legacy_unmapped", [reversed_with_normalized_digest]
    )

    reversed_with_raw_digest = _valid_legacy_record(
        domain="capability",
        value="issued",
        **{field: list(reversed(normalized_refs))}
    )
    assert reversed_with_raw_digest["source_digest"] != normalized_digest
    _assert_adapter_error("legacy_invalid", [reversed_with_raw_digest])


def test_opaque_web_reference_is_never_interpreted() -> None:
    record = _valid_legacy_record(
        domain="capability",
        value="issued",
        evidence_refs=["web:not-a-url-and-still-opaque"]
    )

    _assert_adapter_error("legacy_unmapped", [record])


def test_scope_reference_is_validated_as_opaque_syntax_only() -> None:
    record = _valid_legacy_record(
        domain="capability",
        value="issued",
        mutable_scope_ref="/absolute-looking/opaque-scope-ref"
    )

    _assert_adapter_error("legacy_unmapped", [record])


def test_batch_is_fully_parsed_before_the_unmapped_boundary() -> None:
    valid = _valid_legacy_record()
    invalid = _valid_legacy_record(source_id="capacity:work-2:1")
    invalid["source_digest"] = _digest("f")

    _assert_adapter_error("legacy_invalid", [valid, invalid])


def test_external_record_iteration_failure_is_stable_and_sanitized() -> None:
    class RaisingRecords:
        def __iter__(self) -> RaisingRecords:
            return self

        def __next__(self) -> object:
            raise RuntimeError("raw legacy secret")

    error = _assert_adapter_error("legacy_invalid", RaisingRecords())

    assert "raw legacy secret" not in str(error)


@pytest.mark.parametrize(
    "argv",
    (
        [],
        ["--check-corpus"],
        ["--unknown", "value"],
        ["--check-corpus", ""],
        ["--check-corpus", "not-implemented-yet.json"],
    ),
)
def test_task1_cli_fails_closed_without_a_valid_corpus_check(
    argv: list[str],
) -> None:
    assert adapter.main(argv) == 1


def test_adapter_error_codes_are_exact_and_sanitized() -> None:
    expected = {
        "legacy_invalid",
        "legacy_version",
        "legacy_unmapped",
        "legacy_ambiguous",
        "legacy_nondeterministic",
        "parity_divergence",
    }

    assert adapter._LEGACY_ERROR_CODES == frozenset(expected)
    for code in expected:
        error = adapter.LegacyAdapterError(code)
        assert error.code == code
        assert str(error) == code

    error = adapter.LegacyAdapterError("raw external secret")
    assert error.code == "legacy_invalid"
    assert str(error) == "legacy_invalid"


def _load_strict(path: Path) -> dict[str, object]:
    value = adapter._strict_json_loads(path.read_text(encoding="utf-8"))
    assert type(value) is dict
    return value


def _mapping_rows() -> list[dict[str, object]]:
    fixture = _load_strict(MAPPING_FIXTURE)
    rows = fixture["rows"]
    assert type(rows) is list
    assert all(type(row) is dict for row in rows)
    return rows


def _mapping_row_ids() -> list[str]:
    return [row["id"] for row in _mapping_rows()]


def _misuse_ids(phase: int) -> set[str]:
    fixture = _load_strict(MISUSE_FIXTURE)
    vectors = fixture["vectors"]
    assert type(vectors) is list
    return {
        vector["id"]
        for vector in vectors
        if vector["enforcing_phase"] == phase
    }


def _reducer_replay_ids() -> list[str]:
    fixture = _load_strict(REDUCER_REPLAY_FIXTURE)
    vectors = fixture["vectors"]
    assert type(vectors) is list
    return [vector["id"] for vector in vectors]


def _case(corpus: dict[str, object], case_id: str) -> dict[str, object]:
    cases = corpus["cases"]
    assert type(cases) is list
    return next(item for item in cases if item["id"] == case_id)


def _actor_from_corpus(corpus: dict[str, object]) -> reducer.ActorContext:
    actors = corpus["actors"]
    assert type(actors) is dict and len(actors) == 1
    raw = next(iter(actors.values()))
    assert type(raw) is dict
    return reducer.ActorContext(
        binding_id=raw["binding_id"],
        binding_digest=raw["binding_digest"],
        repository=raw["repository"],
        principal=raw["principal"],
        allowed_actions=frozenset(raw["allowed_actions"]),
        user_authorized_actions=frozenset(raw["user_authorized_actions"]),
        parent_binding_id=raw["parent_binding_id"],
        parent_allowed_actions=(
            None
            if raw["parent_allowed_actions"] is None
            else frozenset(raw["parent_allowed_actions"])
        ),
        attested=raw["attested"],
        expired=raw["expired"],
        revoked=raw["revoked"],
    )


def _scope_resolver(corpus: dict[str, object]):
    scopes = corpus["scopes"]
    assert type(scopes) is dict

    def resolve(ref: str) -> reducer.ResolvedScope:
        raw = scopes[ref]
        assert type(raw) is dict
        return reducer.ResolvedScope(
            repository=raw["repository"],
            paths=tuple(raw["paths"]),
            lock_domains=tuple(raw["lock_domains"]),
        )

    return resolve


def _stable_resolvers(corpus: dict[str, object]):
    actor = _actor_from_corpus(corpus)
    return (lambda _digest: actor), _scope_resolver(corpus)


def _assert_corpus_error(corpus: dict[str, object], code: str) -> None:
    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter._check_corpus(corpus)
    assert exc_info.value.code == code
    assert str(exc_info.value) == code


def test_corpus_has_no_missing_extra_duplicate_or_silently_skipped_case() -> None:
    corpus = _load_strict(CORPUS)
    assert set(corpus) == CORPUS_FIELDS
    assert corpus["schema_version"] == "compact-kernel-v1-shadow-replay/v1"

    sources = corpus["sources"]
    assert type(sources) is dict
    expected_sources = {
        str(MAPPING_FIXTURE.relative_to(ROOT)),
        str(MISUSE_FIXTURE.relative_to(ROOT)),
        str(REDUCER_REPLAY_FIXTURE.relative_to(ROOT)),
    }
    assert set(sources) == expected_sources
    for relative_path, expected_digest in sources.items():
        assert type(relative_path) is str
        assert expected_digest == _canonical_file_digest(ROOT / relative_path)

    cases = corpus["cases"]
    assert type(cases) is list and cases
    assert all(type(item) is dict and set(item) == CASE_FIELDS for item in cases)
    case_ids = [item["id"] for item in cases]
    assert corpus["case_manifest"] == case_ids
    assert len(case_ids) == len(set(case_ids))

    mapping_cases = [item for item in cases if item["case_kind"] == "mapping"]
    assert [item["mapping_row_id"] for item in mapping_cases] == _mapping_row_ids()
    assert all(item["misuse_vector_id"] is None for item in mapping_cases)
    for item in cases:
        assert item["case_kind"] in {"mapping", "history", "misuse"}
        assert (item["mapping_row_id"] is None) != (
            item["misuse_vector_id"] is None
        )
        expected = item["expected"]
        assert type(expected) is dict
        projections = expected["projections"]
        assert type(projections) is list and projections
        assert all(
            type(projected) is dict and set(projected) == PROJECTION_FIELDS
            for projected in projections
        )
        records = item["source_records"]
        assert type(records) is list
        for source_record in records:
            assert type(source_record) is dict
            without_digest = {
                key: value
                for key, value in source_record.items()
                if key != "source_digest"
            }
            assert source_record["source_digest"] == _canonical_digest(
                without_digest
            )

    bindings = corpus["phase2_misuse_bindings"]
    assert type(bindings) is dict
    assert set(bindings) == _misuse_ids(2)
    assert not (set(bindings) & set(corpus["deferred_phase3_misuse_ids"]))
    targets: list[tuple[str, str]] = []
    for binding in bindings.values():
        assert type(binding) is dict
        assert set(binding) == {"target_kind", "target_id"}
        target = (binding["target_kind"], binding["target_id"])
        targets.append(target)
        if binding["target_kind"] == "case":
            target_case = _case(corpus, binding["target_id"])
            assert target_case["case_kind"] in {"history", "misuse"}
            assert target_case["source_records"]
        else:
            assert binding["target_kind"] == "reducer_replay"
            assert binding["target_id"] in corpus["reducer_replay_ids"]
    assert len(targets) == len(set(targets))
    assert set(corpus["deferred_phase3_misuse_ids"]) == _misuse_ids(3)
    assert corpus["reducer_replay_ids"] == _reducer_replay_ids()


def _canonical_file_digest(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def test_corpus_guard_rejects_missing_extra_or_unmanifested_cases() -> None:
    missing = _load_strict(CORPUS)
    missing["cases"].pop()
    _assert_corpus_error(missing, "legacy_invalid")

    extra = _load_strict(CORPUS)
    clone = deepcopy(extra["cases"][-1])
    clone["id"] = "history:unmanifested-extra"
    extra["cases"].append(clone)
    _assert_corpus_error(extra, "legacy_invalid")


def test_corpus_guard_rejects_vacuous_or_shared_misuse_targets() -> None:
    vacuous = _load_strict(CORPUS)
    target = vacuous["phase2_misuse_bindings"]["relevant_dependency_change"]
    _case(vacuous, target["target_id"])["source_records"] = []
    _assert_corpus_error(vacuous, "legacy_invalid")

    shared = _load_strict(CORPUS)
    shared["phase2_misuse_bindings"]["relevant_acceptance_change"] = deepcopy(
        shared["phase2_misuse_bindings"]["relevant_dependency_change"]
    )
    _assert_corpus_error(shared, "legacy_invalid")


def test_corpus_guard_rejects_changed_source_digest() -> None:
    corpus = _load_strict(CORPUS)
    _case(corpus, "mapping:capacity-ready")["source_records"][0][
        "source_digest"
    ] = _digest("f")
    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_top_level_disposition_contradiction() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "mapping:capacity-ready")
    assert case["expected"]["projections"][0]["disposition"] == "route_event"
    assert case["expected"]["envelope_count"] == 1
    case["disposition"] = "no_route_event"

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_binds_primary_mapping_case_to_declared_row() -> None:
    corpus = _load_strict(CORPUS)
    target = _case(corpus, "mapping:capacity-ready")
    donor = _case(corpus, "mapping:work-cancelled")
    for field in (
        "source_records",
        "record_orders",
        "resolver_mode",
        "disposition",
        "expected",
    ):
        target[field] = deepcopy(donor[field])
    assert target["mapping_row_id"] == "capacity-ready"

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_binds_history_case_to_final_observation() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:sequential-update")
    assert case["mapping_row_id"] == "capacity-active"
    case["mapping_row_id"] = "capability-issued"

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_binds_history_case_to_replay_terminal() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:sequential-update")
    case["source_records"].reverse()
    case["record_orders"] = [[1, 0]]
    case["mapping_row_id"] = "capacity-ready"

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_falsy_non_list_record_order() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "mapping:capability-issued")
    assert case["source_records"] == []
    case["record_orders"] = [{}]

    _assert_corpus_error(corpus, "legacy_invalid")


def test_complete_corpus_is_gate_clean_and_executes_every_case() -> None:
    corpus = _load_strict(CORPUS)
    report = adapter._check_corpus(corpus)

    assert adapter._report_is_gate_clean(report) is True
    assert report.specialized_event_ids == ()
    assert {item.kind for item in report.divergences} <= {"match"}
    assert set(report.executed_case_ids) == set(corpus["case_manifest"])


def test_corpus_pins_every_required_history_dimension() -> None:
    corpus = _load_strict(CORPUS)
    required_cases = {
        "history:sequential-update",
        "history:exact-duplicate-source",
        "history:changed-duplicate-source",
        "history:disjoint-order-permutations",
        "history:stale-work-revision",
        "history:gapped-work-revision",
        "history:actor-resolver-drift",
        "history:scope-resolver-drift",
        "history:route-ambiguity",
        "history:scope-ambiguity",
        "history:overlapping-unit-scopes",
        "history:content-change",
        "misuse:dependency-change",
        "misuse:acceptance-change",
        "misuse:evidence-change",
        "history:absolute-resolved-path",
        "history:redundant-resolved-scope",
        "history:mixed-v1-v2",
        "history:future-v1-schema",
        "history:nonzero-epoch-material",
    }
    assert required_cases <= set(corpus["case_manifest"])

    records = [
        record
        for case in corpus["cases"]
        for record in case["source_records"]
    ]
    assert {record["route_id"] is None for record in records} == {False, True}
    assert {record["unit_id"] is None for record in records} == {False, True}
    assert any(
        ref.startswith("web:")
        for record in records
        for ref in record["evidence_refs"]
    )

    mixed = _case(corpus, "history:mixed-v1-v2")["source_records"]
    assert len(mixed) == 2
    assert mixed[0]["source_id"] == mixed[1]["source_id"]
    assert {record["schema"] for record in mixed} == {
        LEGACY_SCHEMA,
        reducer.SCHEMA_ID,
    }


def test_specialized_states_never_emit_route_events() -> None:
    report = adapter._check_corpus(_load_strict(CORPUS))
    assert report.specialized_event_ids == ()


def test_independent_input_orders_return_one_canonical_envelope_tuple() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:disjoint-order-permutations")
    left, right = case["source_records"]
    resolve_actor, resolve_scope = _stable_resolvers(corpus)

    forward = adapter.adapt_v1_history(
        [left, right], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    )
    reverse = adapter.adapt_v1_history(
        [right, left], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    )

    assert forward == reverse


def _mutate_projection(
    corpus: dict[str, object], case_id: str, **updates: object
) -> dict[str, object]:
    projection_value = _case(corpus, case_id)["expected"]["projections"][0]
    projection_value.update(updates)
    return corpus


def _make_compact_more_permissive(corpus: dict[str, object]) -> dict[str, object]:
    case = _case(corpus, "mapping:capability-issued")
    _mutate_projection(corpus, case["id"], disposition="route_event")
    case["disposition"] = "route_event"
    case["expected"]["envelope_count"] = 1
    case["expected"]["requested_transitions"] = ["START"]
    return corpus


def _make_compact_more_restrictive(corpus: dict[str, object]) -> dict[str, object]:
    case = _case(corpus, "mapping:capacity-ready")
    _mutate_projection(corpus, case["id"], disposition="no_route_event")
    case["disposition"] = "no_route_event"
    case["expected"]["envelope_count"] = 0
    case["expected"]["requested_transitions"] = []
    return corpus


def _make_effect_more_permissive(corpus: dict[str, object]) -> dict[str, object]:
    return _mutate_projection(
        corpus,
        "mapping:capacity-blocked-wait",
        effect_eligibility="all_other_gates",
    )


def _make_effect_more_restrictive(corpus: dict[str, object]) -> dict[str, object]:
    return _mutate_projection(
        corpus,
        "mapping:capacity-blocked-complete",
        effect_eligibility="never",
    )


@pytest.mark.parametrize(
    ("mutation", "expected_kind"),
    (
        (_make_compact_more_permissive, "compact_more_permissive"),
        (_make_compact_more_restrictive, "compact_more_restrictive"),
        (_make_effect_more_permissive, "compact_more_permissive"),
        (_make_effect_more_restrictive, "compact_more_restrictive"),
    ),
)
def test_both_parity_directions_block(mutation, expected_kind: str) -> None:
    report = adapter._check_corpus(mutation(_load_strict(CORPUS)))
    assert expected_kind in {item.kind for item in report.divergences}
    assert adapter._report_is_gate_clean(report) is False


def test_non_authority_compact_label_difference_is_reported_but_not_blocking() -> None:
    corpus = _mutate_projection(
        _load_strict(CORPUS), "mapping:capacity-ready", compact="RUN_ALIAS"
    )
    report = adapter._check_corpus(corpus)

    assert "non_authority_only" in {item.kind for item in report.divergences}
    assert adapter._report_is_gate_clean(report) is True


def test_parity_kind_set_and_effect_order_are_closed() -> None:
    assert adapter._PARITY_KINDS == EXPECTED_PARITY_KINDS
    assert adapter._EFFECT_ORDER == {
        "never": 0,
        "separate_current_grant": 1,
        "all_other_gates": 2,
    }


def test_adapter_rule_table_is_closed_over_every_mapping_row() -> None:
    expected_keys = {
        (
            row["domain"],
            row["value"],
            tuple(sorted(row["context"].items())),
        )
        for row in _mapping_rows()
    }
    actual_keys = [key for key, _rule in adapter._ADAPTER_RULES]

    assert set(actual_keys) == expected_keys
    assert len(actual_keys) == len(set(actual_keys))


def test_compact_projection_is_independent_of_v1_oracle_and_fixtures() -> None:
    source = inspect.getsource(adapter._compact_projection)
    tree = ast.parse(source)
    names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }

    assert "meaning_for" not in source
    assert not ({"open", "load", "loads", "read_text", "read_bytes"} & names)
    assert not ({"open", "load", "loads", "read_text", "read_bytes"} & attributes)


def _mutated_rules(**updates: object):
    rules = list(adapter._ADAPTER_RULES)
    for index, (key, rule) in enumerate(rules):
        if key == ("capacity", "ready", ()):
            rules[index] = (key, dataclasses.replace(rule, **updates))
            return tuple(rules)
    raise AssertionError("capacity-ready adapter rule missing")


def test_transition_rule_mutation_makes_gate_fail(monkeypatch) -> None:
    monkeypatch.setattr(
        adapter,
        "_ADAPTER_RULES",
        _mutated_rules(requested_transition="BLOCK"),
    )
    report = adapter._check_corpus(_load_strict(CORPUS))

    assert adapter._report_is_gate_clean(report) is False
    assert {item.kind for item in report.divergences} - {"match"}


def test_semantic_rule_mutation_makes_gate_fail(monkeypatch) -> None:
    monkeypatch.setattr(
        adapter,
        "_ADAPTER_RULES",
        _mutated_rules(next_action="wait_for_unbound_authority"),
    )
    report = adapter._check_corpus(_load_strict(CORPUS))

    assert adapter._report_is_gate_clean(report) is False
    assert "authority_semantic_mismatch" in {
        item.kind for item in report.divergences
    }


def test_route_record_resolves_actor_and_scope_exactly_twice() -> None:
    corpus = _load_strict(CORPUS)
    record_value = _case(corpus, "mapping:capacity-ready")["source_records"][0]
    actor = _actor_from_corpus(corpus)
    stable_scope = _scope_resolver(corpus)
    counts = {"actor": 0, "scope": 0}

    def resolve_actor(_digest: str) -> reducer.ActorContext:
        counts["actor"] += 1
        return actor

    def resolve_scope(ref: str) -> reducer.ResolvedScope:
        counts["scope"] += 1
        return stable_scope(ref)

    result = adapter.adapt_v1_history(
        [record_value], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    )

    assert len(result) == 1
    assert counts == {"actor": 2, "scope": 2}


def test_exact_replay_reuses_envelope_before_cursor_or_resolver() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:exact-duplicate-source")
    record_value = case["source_records"][0]
    actor = _actor_from_corpus(corpus)
    stable_scope = _scope_resolver(corpus)
    counts = {"actor": 0, "scope": 0}

    def resolve_actor(_digest: str) -> reducer.ActorContext:
        counts["actor"] += 1
        return actor

    def resolve_scope(ref: str) -> reducer.ResolvedScope:
        counts["scope"] += 1
        return stable_scope(ref)

    result = adapter.adapt_v1_history(
        [record_value, record_value],
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
    )

    assert len(result) == 2
    assert result[0] is result[1]
    assert counts == {"actor": 2, "scope": 2}


@pytest.mark.parametrize(
    ("case_id", "code"),
    (
        ("history:changed-duplicate-source", "legacy_ambiguous"),
        ("history:stale-work-revision", "legacy_ambiguous"),
        ("history:gapped-work-revision", "legacy_ambiguous"),
        ("history:route-ambiguity", "legacy_ambiguous"),
        ("history:scope-ambiguity", "legacy_ambiguous"),
        ("history:overlapping-unit-scopes", "legacy_ambiguous"),
        ("history:absolute-resolved-path", "legacy_ambiguous"),
        ("history:redundant-resolved-scope", "legacy_ambiguous"),
        ("history:mixed-v1-v2", "legacy_version"),
        ("history:future-v1-schema", "legacy_version"),
        ("history:nonzero-epoch-material", "legacy_invalid"),
    ),
)
def test_corpus_error_cases_are_stable_and_return_no_partial_tuple(
    case_id: str, code: str
) -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, case_id)
    resolve_actor, resolve_scope = _stable_resolvers(corpus)

    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            case["source_records"],
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    assert exc_info.value.code == code
    assert str(exc_info.value) == code


def test_reversing_causal_history_is_rejected_not_repaired() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:sequential-update")
    resolve_actor, resolve_scope = _stable_resolvers(corpus)

    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            list(reversed(case["source_records"])),
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    assert exc_info.value.code == "legacy_ambiguous"


def test_actor_and_scope_resolver_drift_are_deterministic_failures() -> None:
    corpus = _load_strict(CORPUS)
    actor = _actor_from_corpus(corpus)
    scope = _scope_resolver(corpus)
    actor_calls = 0
    scope_calls = 0

    def drift_actor(_digest: str) -> reducer.ActorContext:
        nonlocal actor_calls
        actor_calls += 1
        return actor if actor_calls == 1 else dataclasses.replace(
            actor, principal="user:drift"
        )

    actor_record = _case(corpus, "history:actor-resolver-drift")[
        "source_records"
    ]
    with pytest.raises(adapter.LegacyAdapterError) as actor_exc:
        adapter.adapt_v1_history(
            actor_record,
            resolve_actor=drift_actor,
            resolve_scope=scope,
        )
    assert actor_exc.value.code == "legacy_nondeterministic"

    def drift_scope(ref: str) -> reducer.ResolvedScope:
        nonlocal scope_calls
        scope_calls += 1
        return scope(ref) if scope_calls == 1 else scope("scope:unit-b")

    scope_record = _case(corpus, "history:scope-resolver-drift")[
        "source_records"
    ]
    with pytest.raises(adapter.LegacyAdapterError) as scope_exc:
        adapter.adapt_v1_history(
            scope_record,
            resolve_actor=lambda _digest: actor,
            resolve_scope=drift_scope,
        )
    assert scope_exc.value.code == "legacy_nondeterministic"


def test_external_resolver_exception_is_sanitized() -> None:
    corpus = _load_strict(CORPUS)
    record_value = _case(corpus, "mapping:capacity-ready")["source_records"]

    def explode(_digest: str) -> reducer.ActorContext:
        raise RuntimeError("raw resolver secret")

    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            record_value,
            resolve_actor=explode,
            resolve_scope=_scope_resolver(corpus),
        )

    assert exc_info.value.code == "legacy_invalid"
    assert "raw resolver secret" not in str(exc_info.value)


def test_opaque_web_evidence_changes_only_relevant_shadow_digests() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "misuse:evidence-change")
    first, with_web = case["source_records"]
    without_web = deepcopy(with_web)
    without_web["source_id"] = "misuse:evidence-change:without-web"
    without_web["evidence_refs"] = ["artifact:one"]
    without_web["source_digest"] = _canonical_digest(
        {key: value for key, value in without_web.items() if key != "source_digest"}
    )
    resolve_actor, resolve_scope = _stable_resolvers(corpus)

    changed_events = adapter.adapt_v1_history(
        [first, with_web],
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
    )
    stable_events = adapter.adapt_v1_history(
        [first, without_web],
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
    )
    changed_report = reducer.reduce_protocol_state(
        changed_events,
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
        activation=reducer.ActivationState(epoch=0),
    )
    stable_report = reducer.reduce_protocol_state(
        stable_events,
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
        activation=reducer.ActivationState(epoch=0),
    )

    changed_unit = changed_report.units[0]
    stable_unit = stable_report.units[0]
    differing_fields = {
        field.name
        for field in dataclasses.fields(reducer.UnitSnapshot)
        if getattr(changed_unit, field.name) != getattr(stable_unit, field.name)
    }
    assert differing_fields == {
        "unit_version",
        "evidence_digest",
        "precondition_digest",
    }
    forbidden = {"verdict", "effect_eligible", "effect_eligibility", "writer"}
    assert forbidden.isdisjoint(reducer.KernelReport.__dataclass_fields__)
    assert forbidden.isdisjoint(reducer.UnitSnapshot.__dataclass_fields__)


def test_reordered_opaque_web_refs_produce_identical_envelope() -> None:
    corpus = _load_strict(CORPUS)
    source = deepcopy(
        _case(corpus, "mapping:capacity-ready")["source_records"][0]
    )
    source["evidence_refs"] = ["artifact:one", "web:opaque-observation"]
    source["source_digest"] = _canonical_digest(
        {key: value for key, value in source.items() if key != "source_digest"}
    )
    reordered = deepcopy(source)
    reordered["evidence_refs"] = list(reversed(source["evidence_refs"]))
    resolve_actor, resolve_scope = _stable_resolvers(corpus)

    assert adapter.adapt_v1_history(
        [source], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    ) == adapter.adapt_v1_history(
        [reordered], resolve_actor=resolve_actor, resolve_scope=resolve_scope
    )


def test_route_output_contains_no_payload_authority_or_writer_fields() -> None:
    corpus = _load_strict(CORPUS)
    resolve_actor, resolve_scope = _stable_resolvers(corpus)
    event = adapter.adapt_v1_history(
        _case(corpus, "mapping:capacity-ready")["source_records"],
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
    )[0]

    assert event.activation_epoch == 0
    assert {
        "principal",
        "actor",
        "verdict",
        "effect_eligible",
        "effect_eligibility",
        "writer",
        "mode",
    }.isdisjoint(event.__dataclass_fields__)


def test_cli_prints_one_canonical_sanitized_gate_report(capsys) -> None:
    assert adapter.main(["--check-corpus", str(CORPUS)]) == 0
    output = capsys.readouterr()
    report = json.loads(output.out)

    assert output.err == ""
    assert output.out == canonicalize(report).decode("utf-8") + "\n"
    assert set(report) == {
        "schema",
        "mode",
        "source_digests",
        "set_counts",
        "corpus_digest",
        "report_digest",
        "case_ids_by_divergence_class",
        "specialized_event_ids",
        "deferred_phase3_misuse_ids",
    }
    assert report["schema"] == "compact-kernel-v1-shadow-parity-report/v1"
    assert report["mode"] == "shadow"
    assert all(
        report["case_ids_by_divergence_class"][kind] == []
        for kind in EXPECTED_PARITY_KINDS - {"match"}
    )
    assert "user:principal" not in output.out
    assert "web:" not in output.out
    assert "source_records" not in output.out


def test_script_entrypoint_runs_corpus_cli_from_repository_root() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/capability_v1_adapter.py"),
            "--check-corpus",
            str(CORPUS),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    report = json.loads(completed.stdout)
    assert report["schema"] == "compact-kernel-v1-shadow-parity-report/v1"
    assert completed.stdout == canonicalize(report).decode("utf-8") + "\n"


def test_cli_fails_closed_on_changed_corpus_without_leaking(capsys, tmp_path) -> None:
    corpus = _load_strict(CORPUS)
    _case(corpus, "mapping:capacity-ready")["expected"]["projections"][0][
        "effect_eligibility"
    ] = "all_other_gates"
    changed = tmp_path / "changed-corpus.json"
    changed.write_text(json.dumps(corpus), encoding="utf-8")

    assert adapter.main(["--check-corpus", str(changed)]) == 1
    output = capsys.readouterr()
    assert output.err == ""
    assert "source_records" not in output.out
    assert "user:principal" not in output.out
