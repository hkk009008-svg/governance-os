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
PARITY_ARTIFACT = ROOT / "logs/capability-first/phase2b-shadow-parity.json"
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
CAUSAL_ERROR_PREFIX_CASE_IDS = (
    "history:changed-duplicate-source",
    "history:gapped-work-revision",
    "history:route-ambiguity",
    "history:scope-ambiguity",
    "history:overlapping-unit-scopes",
)
SCOPE_BOUND_AMBIGUITY_CASE_IDS = (
    "history:route-ambiguity",
    "history:scope-ambiguity",
    "history:overlapping-unit-scopes",
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


def _assert_corpus_blocks(corpus: dict[str, object]) -> None:
    try:
        report = adapter._check_corpus(corpus)
    except adapter.LegacyAdapterError:
        return
    assert adapter._report_is_gate_clean(report) is False


def _assert_declared_error_construction_is_blocked(
    corpus: dict[str, object],
    case_id: str,
) -> None:
    case = _case(corpus, case_id)
    actors, scopes = adapter._fixture_runtime(corpus)
    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            case["source_records"],
            resolve_actor=actors.__getitem__,
            resolve_scope=scopes.__getitem__,
        )
    assert exc_info.value.code == case["expected"]["error_code"]
    _assert_corpus_blocks(corpus)


def _refresh_source_digest(record: dict[str, object]) -> None:
    record["source_digest"] = _canonical_digest(
        {
            field: value
            for field, value in record.items()
            if field != "source_digest"
        }
    )


def _declare_expected_error(case: dict[str, object], code: str) -> None:
    case["disposition"] = code
    expected = case["expected"]
    assert type(expected) is dict
    expected["envelope_count"] = 0
    expected["requested_transitions"] = []
    expected["error_code"] = code


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


def test_corpus_guard_rejects_semantically_swapped_replay_bindings() -> None:
    corpus = _load_strict(CORPUS)
    forged = corpus["phase2_misuse_bindings"][
        "forged_self_asserted_principal"
    ]
    duplicate = corpus["phase2_misuse_bindings"][
        "duplicate_transition_id_identical_payload"
    ]
    forged["target_id"], duplicate["target_id"] = (
        duplicate["target_id"],
        forged["target_id"],
    )

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_swapped_case_bound_misuse_associations() -> None:
    corpus = _load_strict(CORPUS)
    dependency_case = _case(corpus, "misuse:dependency-change")
    acceptance_case = _case(corpus, "misuse:acceptance-change")
    dependency_case["misuse_vector_id"], acceptance_case["misuse_vector_id"] = (
        acceptance_case["misuse_vector_id"],
        dependency_case["misuse_vector_id"],
    )
    bindings = corpus["phase2_misuse_bindings"]
    dependency_binding = bindings["relevant_dependency_change"]
    acceptance_binding = bindings["relevant_acceptance_change"]
    dependency_binding["target_id"], acceptance_binding["target_id"] = (
        acceptance_binding["target_id"],
        dependency_binding["target_id"],
    )

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_extra_case_bound_delta_field() -> None:
    corpus = _load_strict(CORPUS)
    dependency_case = _case(corpus, "misuse:dependency-change")
    changed_record = dependency_case["source_records"][1]
    changed_record["acceptance_digest"] = _digest("8")
    changed_record["source_digest"] = _canonical_digest(
        {
            field: value
            for field, value in changed_record.items()
            if field != "source_digest"
        }
    )

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_case_bound_duplicate_source_substitution() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "misuse:dependency-change")
    first, second = case["source_records"]
    second["source_id"] = first["source_id"]
    _refresh_source_digest(second)
    _declare_expected_error(case, "legacy_ambiguous")

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_case_bound_gapped_revision_substitution() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "misuse:dependency-change")
    second = case["source_records"][1]
    second["work_revision"] = 3
    _refresh_source_digest(second)
    _declare_expected_error(case, "legacy_ambiguous")

    _assert_corpus_error(corpus, "legacy_invalid")


@pytest.mark.parametrize(
    "case_id",
    (
        "misuse:dependency-change",
        "misuse:acceptance-change",
        "misuse:evidence-change",
    ),
)
def test_corpus_guard_requires_successful_case_bound_misuse_execution(
    case_id: str,
) -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, case_id)
    case["resolver_mode"] = "actor_drift"
    _declare_expected_error(case, "legacy_nondeterministic")

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_requires_exact_case_bound_misuse_order() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "misuse:dependency-change")
    case["record_orders"] = [[1, 0]]

    _assert_corpus_error(corpus, "legacy_invalid")


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


def test_corpus_guard_rejects_repeated_order_masking_malformed_mixed_record() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:mixed-v1-v2")
    malformed_v1 = case["source_records"][0]
    malformed_v1["principal"] = "user:spoof"
    _refresh_source_digest(malformed_v1)
    case["record_orders"] = [[1, 0, 1]]

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_rejects_extra_mixed_record_parser_failure() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:mixed-v1-v2")
    malformed_v1 = case["source_records"][0]
    malformed_v1["principal"] = "user:spoof"
    _refresh_source_digest(malformed_v1)

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_requires_each_order_to_cover_every_record() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:mixed-v1-v2")
    case["record_orders"] = [[1], [0, 1]]

    _assert_corpus_error(corpus, "legacy_invalid")


def test_corpus_guard_binds_exact_mixed_record_sequence_and_order() -> None:
    corpus = _load_strict(CORPUS)
    case = _case(corpus, "history:mixed-v1-v2")
    case["source_records"].reverse()
    case["record_orders"] = [[1, 0]]

    _assert_corpus_error(corpus, "legacy_invalid")


def _replace_exact_duplicate_with_route_v2(
    corpus: dict[str, object],
) -> None:
    case = _case(corpus, "history:exact-duplicate-source")
    record = case["source_records"][0]
    record["schema"] = reducer.SCHEMA_ID
    _refresh_source_digest(record)
    _declare_expected_error(case, "legacy_version")


def _separate_mixed_version_source_identities(
    corpus: dict[str, object],
) -> None:
    case = _case(corpus, "history:mixed-v1-v2")
    second = case["source_records"][1]
    second["source_id"] = "history:mixed:v2"
    _refresh_source_digest(second)


def _replace_future_schema_with_route_v2(
    corpus: dict[str, object],
) -> None:
    case = _case(corpus, "history:future-v1-schema")
    record = case["source_records"][0]
    record["schema"] = reducer.SCHEMA_ID
    _refresh_source_digest(record)


def _replace_nonzero_epoch_with_principal(
    corpus: dict[str, object],
) -> None:
    case = _case(corpus, "history:nonzero-epoch-material")
    record = case["source_records"][0]
    del record["activation_epoch"]
    record["principal"] = "user:spoof"
    _refresh_source_digest(record)


def _replace_stale_history_with_gap(corpus: dict[str, object]) -> None:
    stale = _case(corpus, "history:stale-work-revision")
    gap = _case(corpus, "history:gapped-work-revision")
    for field in (
        "mapping_row_id",
        "disposition",
        "source_records",
        "record_orders",
        "resolver_mode",
        "expected",
    ):
        stale[field] = deepcopy(gap[field])


def _swap_actor_and_scope_drift(corpus: dict[str, object]) -> None:
    actor = _case(corpus, "history:actor-resolver-drift")
    scope = _case(corpus, "history:scope-resolver-drift")
    actor["resolver_mode"], scope["resolver_mode"] = (
        scope["resolver_mode"],
        actor["resolver_mode"],
    )


def _replace_route_ambiguity_with_scope_ambiguity(
    corpus: dict[str, object],
) -> None:
    route = _case(corpus, "history:route-ambiguity")
    scope = _case(corpus, "history:scope-ambiguity")
    for field in (
        "mapping_row_id",
        "disposition",
        "source_records",
        "record_orders",
        "resolver_mode",
        "expected",
    ):
        route[field] = deepcopy(scope[field])


def _remove_content_change(corpus: dict[str, object]) -> None:
    case = _case(corpus, "history:content-change")
    first, second = case["source_records"]
    second["content_digest"] = first["content_digest"]
    _refresh_source_digest(second)


def _remove_disjoint_reverse_order(corpus: dict[str, object]) -> None:
    case = _case(corpus, "history:disjoint-order-permutations")
    case["record_orders"] = [[0, 1]]


def _valid_wrong_scope_digest(
    corpus: dict[str, object],
    current_digest: str,
) -> str:
    resolve_scope = _scope_resolver(corpus)
    for scope_ref in sorted(corpus["scopes"]):
        try:
            normalized = reducer._normalize_scope(resolve_scope(scope_ref))
        except reducer.ReducerError:
            continue
        candidate = reducer._scope_digest(normalized)
        if candidate != current_digest:
            return candidate
    raise AssertionError("fixture lacks a distinct valid scope digest")


def _add_actor_bound_to_another_repository(
    corpus: dict[str, object],
) -> reducer.ActorContext:
    actor = dataclasses.replace(
        _actor_from_corpus(corpus),
        binding_id="actor-other-repository",
        repository="other/repository",
    )
    actor = dataclasses.replace(
        actor,
        binding_digest=_canonical_digest(reducer._actor_mapping(actor)),
    )
    corpus["actors"][actor.binding_digest] = {
        "binding_id": actor.binding_id,
        "binding_digest": actor.binding_digest,
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
    return actor


@pytest.mark.parametrize(
    "mutation",
    (
        _replace_exact_duplicate_with_route_v2,
        _separate_mixed_version_source_identities,
        _replace_future_schema_with_route_v2,
        _replace_nonzero_epoch_with_principal,
        _replace_stale_history_with_gap,
        _swap_actor_and_scope_drift,
        _replace_route_ambiguity_with_scope_ambiguity,
        _remove_content_change,
        _remove_disjoint_reverse_order,
    ),
)
def test_history_semantic_oracle_rejects_case_construction_substitution(
    mutation,
) -> None:
    corpus = _load_strict(CORPUS)
    mutation(corpus)

    _assert_corpus_error(corpus, "legacy_invalid")


def test_history_semantic_oracle_keys_equal_exact_history_case_set() -> None:
    corpus = _load_strict(CORPUS)
    history_case_ids = {
        case["id"] for case in corpus["cases"] if case["case_kind"] == "history"
    }

    assert set(getattr(adapter, "_HISTORY_CASE_ORACLE", ())) == history_case_ids


def test_stale_and_gap_histories_pin_distinct_revision_constructions() -> None:
    corpus = _load_strict(CORPUS)
    stale = _case(corpus, "history:stale-work-revision")
    gap = _case(corpus, "history:gapped-work-revision")

    assert tuple(
        record["work_revision"] for record in stale["source_records"]
    ) == (1, 1)
    assert tuple(
        record["work_revision"] for record in gap["source_records"]
    ) == (1, 3)


@pytest.mark.parametrize("case_id", SCOPE_BOUND_AMBIGUITY_CASE_IDS)
def test_scope_bound_ambiguity_rejects_same_source_identity(case_id: str) -> None:
    corpus = _load_strict(CORPUS)
    first, second = _case(corpus, case_id)["source_records"]
    second["source_id"] = first["source_id"]
    _refresh_source_digest(second)

    _assert_declared_error_construction_is_blocked(corpus, case_id)


@pytest.mark.parametrize("case_id", SCOPE_BOUND_AMBIGUITY_CASE_IDS)
def test_scope_bound_ambiguity_rejects_second_actor_from_other_repository(
    case_id: str,
) -> None:
    corpus = _load_strict(CORPUS)
    other_actor = _add_actor_bound_to_another_repository(corpus)
    second = _case(corpus, case_id)["source_records"][1]
    second["actor_binding_digest"] = other_actor.binding_digest
    _refresh_source_digest(second)

    _assert_declared_error_construction_is_blocked(corpus, case_id)


@pytest.mark.parametrize(
    ("case_id", "record_index"),
    tuple(
        (case_id, record_index)
        for case_id in (
            "history:scope-ambiguity",
            "history:overlapping-unit-scopes",
        )
        for record_index in (0, 1)
    ),
)
def test_scope_bound_ambiguity_rejects_valid_but_wrong_scope_digest(
    case_id: str,
    record_index: int,
) -> None:
    corpus = _load_strict(CORPUS)
    record = _case(corpus, case_id)["source_records"][record_index]
    record["mutable_scope_digest"] = _valid_wrong_scope_digest(
        corpus,
        record["mutable_scope_digest"],
    )
    _refresh_source_digest(record)

    _assert_declared_error_construction_is_blocked(corpus, case_id)


def test_route_ambiguity_rejects_shared_valid_but_wrong_scope_digest() -> None:
    corpus = _load_strict(CORPUS)
    case_id = "history:route-ambiguity"
    records = _case(corpus, case_id)["source_records"]
    wrong_digest = _valid_wrong_scope_digest(
        corpus,
        records[0]["mutable_scope_digest"],
    )
    for record in records:
        record["mutable_scope_digest"] = wrong_digest
        _refresh_source_digest(record)

    _assert_declared_error_construction_is_blocked(corpus, case_id)


def test_scope_ambiguity_rejects_missing_second_scope_lookup() -> None:
    corpus = _load_strict(CORPUS)
    case_id = "history:scope-ambiguity"
    second = _case(corpus, case_id)["source_records"][1]
    second["mutable_scope_ref"] = "scope:missing"
    _refresh_source_digest(second)

    _assert_declared_error_construction_is_blocked(corpus, case_id)


def test_scope_ambiguity_rejects_exact_scope_from_other_repository() -> None:
    corpus = _load_strict(CORPUS)
    case_id = "history:scope-ambiguity"
    case = _case(corpus, case_id)
    first, second = case["source_records"]
    other_scope_ref = "scope:other-repository-unit"
    other_scope = deepcopy(corpus["scopes"][second["mutable_scope_ref"]])
    other_scope["repository"] = "other/repository"
    corpus["scopes"][other_scope_ref] = other_scope
    actors, scopes = adapter._fixture_runtime(corpus)
    normalized = reducer._normalize_scope(scopes[other_scope_ref])
    second["mutable_scope_ref"] = other_scope_ref
    second["mutable_scope_digest"] = reducer._scope_digest(normalized)
    _refresh_source_digest(second)

    prefix = adapter.adapt_v1_history(
        (first,),
        resolve_actor=actors.__getitem__,
        resolve_scope=scopes.__getitem__,
    )
    assert tuple(event.requested_transition for event in prefix) == ("START",)
    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            case["source_records"],
            resolve_actor=actors.__getitem__,
            resolve_scope=scopes.__getitem__,
        )
    assert exc_info.value.code == "legacy_ambiguous"

    _assert_corpus_blocks(corpus)


def test_canonical_ambiguity_cases_pin_raw_reducer_causes(monkeypatch) -> None:
    corpus = _load_strict(CORPUS)
    actors, scopes = adapter._fixture_runtime(corpus)
    real_map = adapter._mapped_reducer_error
    raw_causes: list[str] = []

    def capture_raw_cause(error: reducer.ReducerError) -> adapter.LegacyAdapterError:
        raw_causes.append(error.code)
        return real_map(error)

    monkeypatch.setattr(adapter, "_mapped_reducer_error", capture_raw_cause)
    for case_id, expected_raw_cause in (
        ("history:route-ambiguity", "route_ambiguity"),
        ("history:scope-ambiguity", "scope_invalid"),
        ("history:overlapping-unit-scopes", "scope_overlap"),
    ):
        raw_causes.clear()
        case = _case(corpus, case_id)
        prefix = adapter.adapt_v1_history(
            case["source_records"][:1],
            resolve_actor=actors.__getitem__,
            resolve_scope=scopes.__getitem__,
        )
        assert tuple(event.requested_transition for event in prefix) == ("START",)
        with pytest.raises(adapter.LegacyAdapterError) as exc_info:
            adapter.adapt_v1_history(
                case["source_records"],
                resolve_actor=actors.__getitem__,
                resolve_scope=scopes.__getitem__,
            )
        assert exc_info.value.code == "legacy_ambiguous"
        assert raw_causes == [expected_raw_cause]


def test_causal_error_histories_execute_prefix_then_full_history(
    monkeypatch,
) -> None:
    corpus = _load_strict(CORPUS)
    first_source_to_case = {
        _case(corpus, case_id)["source_records"][0]["source_id"]: case_id
        for case_id in CAUSAL_ERROR_PREFIX_CASE_IDS
    }
    observed_lengths = {case_id: [] for case_id in CAUSAL_ERROR_PREFIX_CASE_IDS}
    real_adapt = adapter.adapt_v1_history

    def trace_causal_errors(raw_history, *, resolve_actor, resolve_scope):
        records = tuple(raw_history)
        if records:
            case_id = first_source_to_case.get(records[0]["source_id"])
            if case_id is not None:
                observed_lengths[case_id].append(len(records))
        return real_adapt(
            records,
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    monkeypatch.setattr(adapter, "adapt_v1_history", trace_causal_errors)
    adapter._check_corpus(corpus)

    assert observed_lengths == {
        case_id: [1, 2] for case_id in CAUSAL_ERROR_PREFIX_CASE_IDS
    }


def test_stale_history_executes_accepted_prefix_before_rejection(
    monkeypatch,
) -> None:
    corpus = _load_strict(CORPUS)
    stale_records = _case(corpus, "history:stale-work-revision")["source_records"]
    stale_work_id = stale_records[0]["work_id"]
    observed_lengths: list[int] = []
    real_adapt = adapter.adapt_v1_history

    def trace_stale(raw_history, *, resolve_actor, resolve_scope):
        records = tuple(raw_history)
        if records and records[0]["work_id"] == stale_work_id:
            observed_lengths.append(len(records))
        return real_adapt(
            records,
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    monkeypatch.setattr(adapter, "adapt_v1_history", trace_stale)
    adapter._check_corpus(corpus)

    assert observed_lengths == [1, 2]


def test_case_bound_misuse_oracle_still_executes_public_adapter(
    monkeypatch,
) -> None:
    expected_case_ids = {
        "misuse:dependency-change",
        "misuse:acceptance-change",
        "misuse:evidence-change",
    }
    observed_case_ids: set[str] = set()
    real_adapt = adapter.adapt_v1_history

    def suppress_case_bound_execution(raw_history, *, resolve_actor, resolve_scope):
        records = tuple(raw_history)
        if len(records) == 2:
            source_id = records[0]["source_id"]
            case_id = source_id.rsplit(":", 1)[0]
            if case_id in expected_case_ids:
                observed_case_ids.add(case_id)
                return ()
        return real_adapt(
            records,
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    monkeypatch.setattr(adapter, "adapt_v1_history", suppress_case_bound_execution)
    report = adapter._check_corpus(_load_strict(CORPUS))

    assert observed_case_ids == expected_case_ids
    assert adapter._report_is_gate_clean(report) is False
    assert {
        item.case_id
        for item in report.divergences
        if item.kind == "authority_semantic_mismatch"
    } >= expected_case_ids


def test_complete_corpus_is_gate_clean_and_executes_every_case() -> None:
    corpus = _load_strict(CORPUS)
    report = adapter._check_corpus(corpus)

    assert adapter._report_is_gate_clean(report) is True
    assert report.specialized_event_ids == ()
    assert {item.kind for item in report.divergences} <= {"match"}
    assert set(report.executed_case_ids) == set(corpus["case_manifest"])


def test_report_mapping_domain_count_is_derived_from_mapping_rows() -> None:
    report = adapter._check_corpus(_load_strict(CORPUS))
    expected_domains = {row["domain"] for row in _mapping_rows()}

    assert dict(report.set_counts)["mapping_domains"] == len(expected_domains)


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


def test_every_specialized_mapping_key_reaches_public_adapter_probe(
    monkeypatch,
) -> None:
    expected_keys = {
        key
        for key, rule in adapter._ADAPTER_RULES
        if rule.requested_transition is None
    }
    expected_domains = {key[0] for key in expected_keys}
    expected_axes = {
        (key, route_is_null, unit_is_null)
        for key in expected_keys
        for route_is_null in (False, True)
        for unit_is_null in (False, True)
    }
    observed_axes: list[
        tuple[
            tuple[str, str, tuple[tuple[str, bool | str], ...]],
            bool,
            bool,
        ]
    ] = []
    observed_source_ids: set[str] = set()
    observed_work_ids: set[str] = set()
    real_adapt = adapter.adapt_v1_history

    def traced_adapt(raw_history, *, resolve_actor, resolve_scope):
        records = tuple(raw_history)
        if len(records) == 1:
            record = records[0]
            key = (
                record["domain"],
                record["value"],
                tuple(sorted(record["context"].items())),
            )
            if key in expected_keys:
                observed_axes.append(
                    (key, record["route_id"] is None, record["unit_id"] is None)
                )
                observed_source_ids.add(record["source_id"])
                observed_work_ids.add(record["work_id"])
                assert record["source_digest"] == _canonical_digest(
                    {
                        field: value
                        for field, value in record.items()
                        if field != "source_digest"
                    }
                )
        return real_adapt(
            records,
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    monkeypatch.setattr(adapter, "adapt_v1_history", traced_adapt)
    report = adapter._check_corpus(_load_strict(CORPUS))

    assert adapter._report_is_gate_clean(report) is True
    assert set(observed_axes) == expected_axes
    assert len(observed_axes) == len(expected_axes)
    assert len(observed_source_ids) == len(expected_axes)
    assert len(observed_work_ids) == len(expected_axes)
    assert {key[0] for key, _, _ in observed_axes} == expected_domains


def test_specialized_domain_fallback_success_blocks_gate(monkeypatch) -> None:
    expected_event_ids = {
        f"mapping:{row['id']}"
        for row in _mapping_rows()
        if row["domain"] == "capability"
    }
    real_adapt = adapter.adapt_v1_history

    def capability_fallback(raw_history, *, resolve_actor, resolve_scope):
        records = tuple(raw_history)
        if records[0]["domain"] == "capability":
            return (object(),)
        return real_adapt(
            records,
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    monkeypatch.setattr(adapter, "adapt_v1_history", capability_fallback)
    report = adapter._check_corpus(_load_strict(CORPUS))

    assert adapter._report_is_gate_clean(report) is False
    assert set(report.specialized_event_ids) == expected_event_ids
    assert "adapter_error" in {item.kind for item in report.divergences}


def test_named_specialized_fallback_success_blocks_gate(monkeypatch) -> None:
    target_key = ("provider_result", "pass", ())
    target_event_id = "mapping:provider-pass"
    real_adapt = adapter.adapt_v1_history

    def named_provider_fallback(raw_history, *, resolve_actor, resolve_scope):
        records = tuple(raw_history)
        record = records[0]
        key = (
            record["domain"],
            record["value"],
            tuple(sorted(record["context"].items())),
        )
        if (
            key == target_key
            and record["route_id"] is not None
            and record["unit_id"] is not None
        ):
            return (object(),)
        return real_adapt(
            records,
            resolve_actor=resolve_actor,
            resolve_scope=resolve_scope,
        )

    monkeypatch.setattr(adapter, "adapt_v1_history", named_provider_fallback)
    report = adapter._check_corpus(_load_strict(CORPUS))

    assert adapter._report_is_gate_clean(report) is False
    assert target_event_id in report.specialized_event_ids
    assert (target_event_id, "adapter_error") in {
        (item.case_id, item.kind) for item in report.divergences
    }


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
    corpus = _load_strict(CORPUS)
    rows = _mapping_rows()
    fixture_keys = {
        (
            row["domain"],
            row["value"],
            tuple(sorted(row["context"].items())),
        )
        for row in rows
    }
    row_by_id = {row["id"]: row for row in rows}
    mapping_case_keys = {
        (
            row_by_id[case["mapping_row_id"]]["domain"],
            row_by_id[case["mapping_row_id"]]["value"],
            tuple(
                sorted(row_by_id[case["mapping_row_id"]]["context"].items())
            ),
        )
        for case in corpus["cases"]
        if case["case_kind"] == "mapping"
    }
    rule_keys = [key for key, _rule in adapter._ADAPTER_RULES]
    accepted_keys = set(compact_state_mapping._accepted_context_keys())

    assert accepted_keys == fixture_keys == set(rule_keys) == mapping_case_keys
    assert len(rule_keys) == len(set(rule_keys))


def test_gate_blocks_one_valid_adapter_rule_omission(monkeypatch) -> None:
    omitted_key = (
        "capacity",
        "blocked",
        (("completion_evidence", False), ("verification_required", False)),
    )
    monkeypatch.setattr(
        adapter,
        "_ADAPTER_RULES",
        tuple(
            (key, rule)
            for key, rule in adapter._ADAPTER_RULES
            if key != omitted_key
        ),
    )

    _assert_corpus_blocks(_load_strict(CORPUS))


def test_chatgpt_failure_rules_are_producer_derived_and_oracle_independent() -> None:
    source = inspect.getsource(adapter._chatgpt_failure_rules)
    tree = ast.parse(source)
    names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    generated_keys = {
        key for key, _rule in adapter._chatgpt_failure_rules()
    }
    accepted_failure_keys = {
        key
        for key in compact_state_mapping._accepted_context_keys()
        if key[:2] == ("chatgpt", "failed")
    }

    assert "meaning_for" not in source
    forbidden_reads = {"open", "load", "loads", "read_text", "read_bytes"}
    assert not (forbidden_reads & names)
    assert not (forbidden_reads & attributes)
    assert generated_keys == accepted_failure_keys


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
    changed_actor = dataclasses.replace(actor, principal="user:drift")
    changed_actor = dataclasses.replace(
        changed_actor,
        binding_digest=_canonical_digest(reducer._actor_mapping(changed_actor)),
    )
    scope = _scope_resolver(corpus)
    actor_calls = 0
    scope_calls = 0

    def drift_actor(_digest: str) -> reducer.ActorContext:
        nonlocal actor_calls
        actor_calls += 1
        return actor if actor_calls == 1 else changed_actor

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


def test_second_actor_equality_spoof_is_rejected_before_comparison() -> None:
    corpus = _load_strict(CORPUS)
    record_value = _case(corpus, "mapping:capacity-ready")["source_records"]
    actor = _actor_from_corpus(corpus)
    actor_calls = 0

    class EqualitySpoof:
        def __eq__(self, _other: object) -> bool:
            return True

    def resolve_actor(_digest: str) -> object:
        nonlocal actor_calls
        actor_calls += 1
        return actor if actor_calls == 1 else EqualitySpoof()

    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            record_value,
            resolve_actor=resolve_actor,
            resolve_scope=_scope_resolver(corpus),
        )

    assert exc_info.value.code == "legacy_invalid"
    assert str(exc_info.value) == "legacy_invalid"


def test_actor_comparison_never_invokes_hostile_equality_or_truth() -> None:
    corpus = _load_strict(CORPUS)
    record_value = _case(corpus, "mapping:capacity-ready")["source_records"]
    actor = _actor_from_corpus(corpus)
    calls = {"actor": 0, "equality": 0, "truth": 0}

    class HostileTruth:
        def __bool__(self) -> bool:
            calls["truth"] += 1
            raise RuntimeError("raw-truth-secret")

    class HostileEquality:
        def __eq__(self, _other: object) -> object:
            calls["equality"] += 1
            return HostileTruth()

    def resolve_actor(_digest: str) -> object:
        calls["actor"] += 1
        return actor if calls["actor"] == 1 else HostileEquality()

    with pytest.raises(adapter.LegacyAdapterError) as exc_info:
        adapter.adapt_v1_history(
            record_value,
            resolve_actor=resolve_actor,
            resolve_scope=_scope_resolver(corpus),
        )

    assert exc_info.value.code == "legacy_invalid"
    assert str(exc_info.value) == "legacy_invalid"
    assert calls == {"actor": 2, "equality": 0, "truth": 0}


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


def test_committed_parity_artifact_matches_fresh_canonical_report() -> None:
    assert PARITY_ARTIFACT.is_file()
    report = adapter._check_corpus(_load_strict(CORPUS))
    rendered = canonicalize(adapter._report_mapping(report)) + b"\n"

    assert PARITY_ARTIFACT.read_bytes() == rendered


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
