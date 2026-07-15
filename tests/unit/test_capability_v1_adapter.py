from __future__ import annotations

import json
from hashlib import sha256

import pytest

from scripts import capability_reducer as reducer
from scripts import capability_v1_adapter as adapter
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


def test_valid_current_record_finishes_strict_parsing_then_fails_unmapped() -> None:
    _assert_adapter_error("legacy_unmapped", [_valid_legacy_record()])


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
    normalized = _valid_legacy_record(**{field: list(normalized_refs)})
    normalized_digest = normalized["source_digest"]

    reversed_with_normalized_digest = dict(normalized)
    reversed_with_normalized_digest[field] = list(reversed(normalized_refs))
    _assert_adapter_error(
        "legacy_unmapped", [reversed_with_normalized_digest]
    )

    reversed_with_raw_digest = _valid_legacy_record(
        **{field: list(reversed(normalized_refs))}
    )
    assert reversed_with_raw_digest["source_digest"] != normalized_digest
    _assert_adapter_error("legacy_invalid", [reversed_with_raw_digest])


def test_opaque_web_reference_is_never_interpreted() -> None:
    record = _valid_legacy_record(
        evidence_refs=["web:not-a-url-and-still-opaque"]
    )

    _assert_adapter_error("legacy_unmapped", [record])


def test_scope_reference_is_validated_as_opaque_syntax_only() -> None:
    record = _valid_legacy_record(
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
