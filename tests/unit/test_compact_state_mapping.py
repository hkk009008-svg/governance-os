from __future__ import annotations

from dataclasses import asdict, fields
import inspect
from itertools import product
import json
from pathlib import Path
import re

import pytest

import compact_state_mapping
import protocol_capacity
import route_capability


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/compact_state_mapping/v1.json"
MISUSE_PATH = ROOT / "tests/fixtures/compact_kernel/v1_misuse_vectors.json"
EXPECTED_MISUSE_IDS = {
    "forged_self_asserted_principal",
    "duplicate_transition_id_identical_payload",
    "duplicate_transition_id_changed_payload",
    "stale_unit_version",
    "stale_activation_epoch",
    "relevant_dependency_change",
    "relevant_acceptance_change",
    "relevant_evidence_change",
}
EXPECTED_FUTURE_DECISIONS = {
    "conflict",
    "idempotent",
    "rejected",
    "verification_invalidated",
}
EXPECTED_LOCAL_VERDICTS = {"GO", "NITS", "FAIL", "unable_to_verify"}
EXPECTED_SOURCE_DOMAINS = {
    "capacity",
    "capability",
    "local_verdict",
    "work_result",
}
REMOVED_SOURCE_DOMAINS = {"chatgpt", "opus_receipt", "provider_result"}


def _context_key(
    domain: str,
    value: str,
    context: dict[str, bool | str],
) -> tuple[str, str, tuple[tuple[str, bool | str], ...]]:
    return (domain, value, tuple(sorted(context.items())))


def _producer_values() -> dict[str, list[str]]:
    return {
        "capacity": sorted(protocol_capacity.STATUSES),
        "capability": sorted(route_capability.LIFECYCLE_STATES),
        "local_verdict": sorted(EXPECTED_LOCAL_VERDICTS),
        "work_result": ["cancelled", "failed", "outcome_unknown", "superseded"],
    }


def _finite_context_candidates(
    domain: str,
    value: str,
) -> tuple[dict[str, bool | str], ...]:
    if domain == "capacity" and value == "blocked":
        return tuple(
            {
                "completion_evidence": completion_evidence,
                "verification_required": verification_required,
            }
            for completion_evidence, verification_required in product(
                (False, True), repeat=2
            )
        )
    if domain == "capacity" and value == "done":
        return tuple(
            {
                "verification_required": required,
                "verification_satisfied": satisfied,
                "all_triggered_gates_met": gates_met,
            }
            for required, satisfied, gates_met in product((False, True), repeat=3)
        )
    if domain == "capability" and value == "consumed":
        return tuple(
            {"receipt_outcome": outcome}
            for outcome in ("ok", "failed", "absent")
        )
    if domain == "local_verdict" and value == "GO":
        return (
            {"verification_key_matches": False},
            {"verification_key_matches": True},
        )
    return ({},)


def _accepted_keys_from_finite_producer_candidates() -> set[
    tuple[str, str, tuple[tuple[str, bool | str], ...]]
]:
    accepted: set[
        tuple[str, str, tuple[tuple[str, bool | str], ...]]
    ] = set()
    for domain, values in _producer_values().items():
        for value in values:
            for context in _finite_context_candidates(domain, value):
                try:
                    compact_state_mapping.meaning_for(
                        domain,
                        value,
                        context=context,
                    )
                except compact_state_mapping.StateMappingError:
                    continue
                accepted.add(_context_key(domain, value, context))
    return accepted


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_state_meaning_contains_exact_contract_fields():
    assert tuple(field.name for field in fields(compact_state_mapping.StateMeaning)) == (
        "compact",
        "terminal_scope",
        "next_action",
        "effect_eligibility",
        "advisory_only",
    )


def test_fixture_source_values_match_current_producer_constants_exactly():
    fixture = _load(FIXTURE_PATH)
    assert fixture["source_values"] == {
        "capacity": sorted(protocol_capacity.STATUSES),
        "capability": sorted(route_capability.LIFECYCLE_STATES),
        "local_verdict": sorted(EXPECTED_LOCAL_VERDICTS),
        "work_result": ["cancelled", "failed", "outcome_unknown", "superseded"],
    }


def test_fixture_contains_only_live_provider_neutral_domains() -> None:
    fixture = _load(FIXTURE_PATH)
    assert set(fixture["source_values"]) == EXPECTED_SOURCE_DOMAINS
    assert {row["domain"] for row in fixture["rows"]} == EXPECTED_SOURCE_DOMAINS


@pytest.mark.parametrize("domain", sorted(REMOVED_SOURCE_DOMAINS))
def test_removed_provider_domain_fails_closed(domain: str) -> None:
    with pytest.raises(
        compact_state_mapping.StateMappingError,
        match="unknown domain",
    ):
        compact_state_mapping.meaning_for(domain, "removed", context={})


def test_fixture_is_a_total_row_oracle():
    fixture = _load(FIXTURE_PATH)
    rows = fixture["rows"]
    assert isinstance(rows, list)
    assert len({row["id"] for row in rows}) == len(rows)
    covered = {domain: set() for domain in fixture["source_values"]}
    for row in rows:
        actual = compact_state_mapping.meaning_for(
            row["domain"], row["value"], context=row["context"]
        )
        assert asdict(actual) == row["expected"], row["id"]
        covered[row["domain"]].add(row["value"])
    assert covered == {
        domain: set(values) for domain, values in fixture["source_values"].items()
    }


def test_accepted_context_manifest_matches_exhaustive_producer_candidates():
    fixture = _load(FIXTURE_PATH)
    fixture_keys = {
        _context_key(row["domain"], row["value"], row["context"])
        for row in fixture["rows"]
    }

    assert set(compact_state_mapping._accepted_context_keys()) == (
        _accepted_keys_from_finite_producer_candidates()
    )
    assert fixture_keys == set(compact_state_mapping._accepted_context_keys())


def test_accepted_context_manifest_does_not_call_meaning_for(monkeypatch):
    source = inspect.getsource(compact_state_mapping._accepted_context_keys)
    expected = compact_state_mapping._accepted_context_keys()

    def forbidden_meaning(*_args, **_kwargs):
        raise AssertionError("accepted-context manifest called meaning_for")

    monkeypatch.setattr(compact_state_mapping, "meaning_for", forbidden_meaning)

    assert "meaning_for" not in source
    assert compact_state_mapping._accepted_context_keys() == expected


def test_fixture_validator_rejects_one_valid_context_omission():
    fixture = _load(FIXTURE_PATH)
    fixture["rows"] = [
        row for row in fixture["rows"] if row["id"] != "capacity-blocked-wait"
    ]

    with pytest.raises(
        compact_state_mapping.StateMappingError,
        match="accepted context",
    ):
        compact_state_mapping._fixture_result(fixture)


def test_effect_eligibility_vocabulary_is_closed():
    fixture = _load(FIXTURE_PATH)
    assert {row["expected"]["effect_eligibility"] for row in fixture["rows"]} == {
        "never",
        "separate_current_grant",
        "all_other_gates",
    }


def test_unable_to_verify_is_a_provider_neutral_nonterminal_local_verdict():
    assert compact_state_mapping.meaning_for(
        "local_verdict", "unable_to_verify", context={}
    ) == compact_state_mapping.StateMeaning(
        compact="UNABLE_TO_VERIFY",
        terminal_scope="nonterminal",
        next_action="redispatch_or_escalate",
        effect_eligibility="never",
        advisory_only=False,
    )

@pytest.mark.parametrize(
    ("domain", "value", "context"),
    [
        ("unknown", "ready", {}),
        ("capacity", "queued", {}),
        (1, "ready", {}),
        ("capacity", None, {}),
        ("capacity", "ready", []),
        ("capacity", "ready", {"unexpected": False}),
        ("capacity", "blocked", {"completion_evidence": False}),
        (
            "capacity",
            "blocked",
            {"completion_evidence": 0, "verification_required": False},
        ),
        (
            "capacity",
            "done",
            {
                "verification_required": True,
                "verification_satisfied": False,
                "all_triggered_gates_met": True,
            },
        ),
        (
            "capacity",
            "done",
            {
                "verification_required": False,
                "verification_satisfied": True,
                "all_triggered_gates_met": True,
            },
        ),
        (
            "capacity",
            "done",
            {
                "verification_required": True,
                "verification_satisfied": True,
                "all_triggered_gates_met": False,
            },
        ),
        ("capability", "consumed", {}),
        ("capability", "consumed", {"receipt_outcome": "unknown"}),
        ("local_verdict", "GO", {"verification_key_matches": False}),
    ],
)
def test_unknown_incomplete_wrong_typed_or_contradictory_inputs_fail_closed(
    domain, value, context
):
    with pytest.raises(compact_state_mapping.StateMappingError):
        compact_state_mapping.meaning_for(domain, value, context=context)


def test_cli_validates_the_fixture_without_writing(capsys):
    before = FIXTURE_PATH.read_bytes()
    fixture = _load(FIXTURE_PATH)
    rc = compact_state_mapping.main(["--check-fixture", str(FIXTURE_PATH)])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.err == ""
    assert captured.out == (
        f"validated {len(fixture['rows'])} mappings across "
        f"{len(fixture['source_values'])} domains\n"
    )
    assert FIXTURE_PATH.read_bytes() == before


def test_cli_rejects_source_set_drift(tmp_path, capsys):
    fixture = _load(FIXTURE_PATH)
    fixture["source_values"]["capacity"].append("future")
    path = tmp_path / "drift.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    assert compact_state_mapping.main(["--check-fixture", str(path)]) == 1
    assert "source-set parity" in capsys.readouterr().err


def _assert_json_safe(value: object) -> None:
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, list):
        for item in value:
            _assert_json_safe(item)
        return
    if isinstance(value, dict):
        assert all(isinstance(key, str) for key in value)
        for item in value.values():
            _assert_json_safe(item)
        return
    pytest.fail(f"non-deterministic JSON value type: {type(value).__name__}")


def test_misuse_vectors_are_replay_shaped_without_claiming_enforcement():
    fixture = _load(MISUSE_PATH)
    assert set(fixture) == {"schema_version", "vectors"}
    assert fixture["schema_version"] == "compact-kernel-misuse-vectors/v1"
    vectors = fixture["vectors"]
    vector_ids = [row["id"] for row in vectors]
    assert len(vector_ids) == 8
    assert len(vector_ids) == len(set(vector_ids))
    assert set(vector_ids) == EXPECTED_MISUSE_IDS
    for row in vectors:
        assert set(row) == {
            "id",
            "enforcing_phase",
            "expected_invariant",
            "phase_1_non_enforcement_reason",
            "stimulus",
            "expected_future_outcome",
        }
        assert row["enforcing_phase"] == 2
        assert row["expected_invariant"].strip()
        assert "Phase 1" in row["phase_1_non_enforcement_reason"]
        assert "mapping API" in row["phase_1_non_enforcement_reason"]
        assert row["stimulus"]
        assert [step["step"] for step in row["stimulus"]] == list(
            range(1, len(row["stimulus"]) + 1)
        )
        for step in row["stimulus"]:
            assert set(step) == {"step", "event_kind", "facts"}
            assert re.fullmatch(r"[a-z][a-z0-9_.]*", step["event_kind"])
            assert isinstance(step["facts"], dict) and step["facts"]
            _assert_json_safe(step)

        outcome = row["expected_future_outcome"]
        assert set(outcome) == {
            "decision",
            "transitions_applied",
            "effect_attempts",
            "provider_attempts",
        }
        assert outcome["decision"] in EXPECTED_FUTURE_DECISIONS
        for count_name in (
            "transitions_applied",
            "effect_attempts",
            "provider_attempts",
        ):
            assert type(outcome[count_name]) is int
            assert outcome[count_name] >= 0
        _assert_json_safe(outcome)

    canonical = json.dumps(fixture, allow_nan=False, sort_keys=True, separators=(",", ":"))
    assert json.loads(canonical) == fixture


def test_misuse_vectors_pin_future_replay_semantics():
    vectors = {row["id"]: row for row in _load(MISUSE_PATH)["vectors"]}
    expected = {
        "forged_self_asserted_principal": (
            ["transition.requested"],
            "rejected",
            0,
            0,
            0,
        ),
        "duplicate_transition_id_identical_payload": (
            ["transition.requested", "transition.requested"],
            "idempotent",
            1,
            0,
            0,
        ),
        "duplicate_transition_id_changed_payload": (
            ["transition.requested", "transition.requested"],
            "conflict",
            1,
            0,
            0,
        ),
        "stale_unit_version": (["transition.requested"], "rejected", 0, 0, 0),
        "stale_activation_epoch": (["transition.requested"], "rejected", 0, 0, 0),
        "relevant_dependency_change": (
            ["verification.dependency_changed"],
            "verification_invalidated",
            1,
            0,
            0,
        ),
        "relevant_acceptance_change": (
            ["verification.acceptance_changed"],
            "verification_invalidated",
            1,
            0,
            0,
        ),
        "relevant_evidence_change": (
            ["verification.evidence_changed"],
            "verification_invalidated",
            1,
            0,
            0,
        ),
    }
    for vector_id, (events, decision, transitions, effects, providers) in expected.items():
        vector = vectors[vector_id]
        assert [step["event_kind"] for step in vector["stimulus"]] == events
        assert vector["expected_future_outcome"] == {
            "decision": decision,
            "transitions_applied": transitions,
            "effect_attempts": effects,
            "provider_attempts": providers,
        }


def test_misuse_vectors_encode_the_adversarial_facts_needed_for_replay():
    vectors = {row["id"]: row for row in _load(MISUSE_PATH)["vectors"]}

    forged = vectors["forged_self_asserted_principal"]["stimulus"][0]["facts"]
    assert forged["asserted_principal"] != forged["host_principal"]

    identical = vectors["duplicate_transition_id_identical_payload"]["stimulus"]
    assert identical[0]["facts"] == identical[1]["facts"]
    changed = vectors["duplicate_transition_id_changed_payload"]["stimulus"]
    assert changed[0]["facts"]["transition_id"] == changed[1]["facts"]["transition_id"]
    assert changed[0]["facts"]["payload_digest"] != changed[1]["facts"]["payload_digest"]

    stale_unit = vectors["stale_unit_version"]["stimulus"][0]["facts"]
    assert stale_unit["event_unit_version"] < stale_unit["current_unit_version"]
    stale_epoch = vectors["stale_activation_epoch"]["stimulus"][0]["facts"]
    assert stale_epoch["event_epoch"] < stale_epoch["active_epoch"]

    for vector_id, digest_name in (
        ("relevant_dependency_change", "dependency_digest"),
        ("relevant_acceptance_change", "acceptance_digest"),
        ("relevant_evidence_change", "evidence_digest"),
    ):
        facts = vectors[vector_id]["stimulus"][0]["facts"]
        assert facts["prior_decision"] == "GO"
        assert facts[f"prior_{digest_name}"] != facts[f"current_{digest_name}"]
