from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path

import protocol_effectiveness_report as reporter
import pytest


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "scripts/baselines/capability_first_five_profile_v1.json"
EXPECTED_PROFILES = (
    "none",
    "verification_only",
    "coordination_only",
    "effect_only",
    "combined",
)
KERNEL_MIRROR = {
    "epoch": 0,
    "writer": "v1",
    "authority": "declarative_only",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _digest(seed: int) -> str:
    return f"sha256:{seed:064x}"


def _git_sha(seed: int) -> str:
    return f"{seed:040x}"


def _point(ns: int, clock: str = "host-monotonic-v1") -> dict:
    return {"ns": ns, "clock_domain": clock}


def _run(
    contract: dict,
    profile: str,
    ordinal: int,
    *,
    endpoints: dict | None = None,
    accepted_result_digest: str | None = None,
    artifacts: list[dict] | None = None,
    reviews: list[dict] | None = None,
) -> dict:
    profile_contract = next(
        item for item in contract["profiles"] if item["id"] == profile
    )
    if endpoints is None:
        start = ordinal * 1_000
        endpoints = {
            "accepted_input": _point(start),
            "first_tool_callback": _point(start + 100),
        }
        if profile == "combined":
            endpoints.update(
                {
                    "accepted_route": _point(start + 200),
                    "published_go": _point(start + 500),
                }
            )
    return {
        "run_id": f"{profile}-{ordinal}",
        "profile": profile,
        "ordinal": ordinal,
        "host_identity": "opaque-host-a",
        "clock_domain": "host-monotonic-v1",
        "instrumentation_identity": "codex-runtime-endpoints-v1",
        "scenario_input_digest": profile_contract["scenario_input_digest"],
        "accepted_result_digest": accepted_result_digest or _digest(ordinal + 100),
        "endpoints": endpoints,
        "artifacts": artifacts or [],
        "reviews": reviews or [],
    }


def _observations(contract: dict, runs: list[dict], *, kind: str = "runtime_trace") -> dict:
    return {
        "schema_version": "capability-first-baseline-observations/v1",
        "evidence_kind": kind,
        "host_identity": "opaque-host-a",
        "clock_domain": "host-monotonic-v1",
        "instrumentation_identity": "codex-runtime-endpoints-v1",
        "runs": runs,
    }


def _aggregate(
    contract: dict,
    observations: dict,
    *,
    synthetic: bool = False,
    repository_root: Path | None = None,
    verified_provenance: object | None = None,
) -> dict:
    kwargs = {"repository_root": repository_root} if repository_root else {}
    return reporter._aggregate_baseline(
        contract,
        observations,
        kernel_mirror=KERNEL_MIRROR,
        allow_synthetic=synthetic,
        verified_provenance=verified_provenance,
        **kwargs,
    )


def _complete_runs(contract: dict) -> list[dict]:
    return [
        _run(
            contract,
            profile,
            ordinal,
            accepted_result_digest=_digest(profile_index * 10 + ordinal),
        )
        for profile_index, profile in enumerate(EXPECTED_PROFILES, start=1)
        for ordinal in range(1, 6)
    ]


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _provenance(
    contract: dict,
    observations: dict,
) -> reporter.VerifiedBaselineProvenance:
    return reporter.VerifiedBaselineProvenance(
        contract_digest=_canonical_digest(contract),
        observations_digest=_canonical_digest(observations),
        cohort_identity=(
            ("benchmark_id", contract["benchmark_id"]),
            ("host_identity", observations["host_identity"]),
            ("clock_domain", observations["clock_domain"]),
            ("instrumentation_identity", observations["instrumentation_identity"]),
        ),
        collector_identity=f"capability-baseline-runtime@{_digest(2_001)}",
        source_head="a" * 40,
        codex_identity=f"codex-cli/0.144.4@{_digest(2_002)}",
        run_record_digests=tuple(
            (run["run_id"], _digest(1_000 + index))
            for index, run in enumerate(observations["runs"])
        ),
    )


def test_manifest_declares_exact_five_by_five_contract():
    contract = _contract()

    assert reporter._validate_baseline_contract(contract) == []
    assert tuple(item["id"] for item in contract["profiles"]) == EXPECTED_PROFILES
    assert all(item["ordinals"] == [1, 2, 3, 4, 5] for item in contract["profiles"])
    assert len({item["scenario_input_digest"] for item in contract["profiles"]}) == 5
    assert all(
        item["scenario_input_digest"]
        == "sha256:"
        + hashlib.sha256(item["scenario_input"].encode("utf-8")).hexdigest()
        for item in contract["profiles"]
    )
    assert contract["protocol_roots"] == ["coordination", ".codex/runtime", "logs"]
    assert contract["review_identity_fields"] == [
        "base",
        "head",
        "scope_digest",
        "question_digest",
    ]
    assert contract["accepted_result_denominator"] == {
        "field": "accepted_result_digest",
        "identity": "unique_sha256",
    }
    assert set(contract["artifact_classes"]) == {
        "coordination",
        "verification",
        "effect",
        "standby",
        "telemetry",
    }
    assert contract["artifact_classes"]["telemetry"]["protocol_overhead"] is False


def test_contract_rejects_root_class_and_denominator_relabeling():
    contract = _contract()
    relabeled_roots = copy.deepcopy(contract)
    relabeled_roots["protocol_roots"] = ["."]
    relabeled_overhead = copy.deepcopy(contract)
    relabeled_overhead["artifact_classes"]["coordination"]["protocol_overhead"] = False
    relabeled_telemetry = copy.deepcopy(contract)
    relabeled_telemetry["artifact_classes"]["telemetry"]["purposes"] = ["observing"]
    relabeled_denominator = copy.deepcopy(contract)
    relabeled_denominator["accepted_result_denominator"]["identity"] = "per_run"
    relabeled_benchmark = copy.deepcopy(contract)
    relabeled_benchmark["benchmark_id"] = "different-benchmark"
    rewritten_scenario = copy.deepcopy(contract)
    rewritten_scenario["profiles"][0]["scenario_input"] += " Rewritten."
    rewritten_scenario["profiles"][0]["scenario_input_digest"] = (
        "sha256:"
        + hashlib.sha256(
            rewritten_scenario["profiles"][0]["scenario_input"].encode("utf-8")
        ).hexdigest()
    )

    for candidate in (
        relabeled_roots,
        relabeled_overhead,
        relabeled_telemetry,
        relabeled_denominator,
        relabeled_benchmark,
        rewritten_scenario,
    ):
        assert reporter._validate_baseline_contract(candidate)


def test_missing_applicable_endpoints_are_not_observed_not_zero():
    contract = _contract()
    run = _run(contract, "none", 1, endpoints={})

    artifact = _aggregate(contract, _observations(contract, [run]))
    measured = artifact["runs"][0]["metrics"]["time_to_first_tool"]

    assert measured == {"status": "not_observed", "value_ns": None}
    assert artifact["runs"][0]["complete"] is False
    assert artifact["complete"] is False
    assert artifact["status"] == "incomplete"


def test_monotonic_endpoints_are_derived_and_contradictions_are_invalid():
    contract = _contract()
    ordered = _run(
        contract,
        "none",
        1,
        endpoints={
            "accepted_input": _point(10),
            "first_tool_callback": _point(25),
        },
    )
    reversed_run = _run(
        contract,
        "none",
        2,
        endpoints={
            "accepted_input": _point(25),
            "first_tool_callback": _point(10),
        },
    )
    duration_only = _run(contract, "none", 3, endpoints={})
    duration_only["time_to_first_tool_ns"] = 15
    mixed_clock = _run(
        contract,
        "none",
        4,
        endpoints={
            "accepted_input": _point(10),
            "first_tool_callback": _point(25, "other-clock"),
        },
    )

    assert _aggregate(contract, _observations(contract, [ordered]))["runs"][0][
        "metrics"
    ]["time_to_first_tool"] == {"status": "measured", "value_ns": 15}
    for run in (reversed_run, duration_only, mixed_clock):
        artifact = _aggregate(contract, _observations(contract, [run]))
        assert artifact["status"] == "invalid"
        assert artifact["runs"][0]["metrics"]["time_to_first_tool"]["status"] == "invalid"
        assert artifact["runs"][0]["metrics"]["time_to_first_tool"]["value_ns"] is None


def test_present_endpoint_is_validated_even_when_its_pair_is_missing():
    contract = _contract()
    run = _run(
        contract,
        "none",
        1,
        endpoints={"accepted_input": {"ns": "10", "clock_domain": "host-monotonic-v1"}},
    )

    artifact = _aggregate(contract, _observations(contract, [run]))

    assert artifact["status"] == "invalid"
    assert artifact["runs"][0]["metrics"]["time_to_first_tool"] == {
        "status": "invalid",
        "value_ns": None,
    }


def test_run_endpoint_and_point_keys_are_exact():
    contract = _contract()
    unknown_run_key = _run(contract, "none", 1)
    unknown_run_key["claimed_duration"] = 100
    unknown_endpoint = _run(contract, "none", 2)
    unknown_endpoint["endpoints"]["duration"] = _point(20)
    unknown_point_key = _run(contract, "none", 3)
    unknown_point_key["endpoints"]["accepted_input"]["duration_ns"] = 10
    bool_ns = _run(contract, "none", 4)
    bool_ns["endpoints"]["accepted_input"]["ns"] = True

    for run in (unknown_run_key, unknown_endpoint, unknown_point_key, bool_ns):
        artifact = _aggregate(contract, _observations(contract, [run]))
        assert artifact["status"] == "invalid"


def test_route_to_go_is_applicable_only_to_combined():
    contract = _contract()
    none_run = _run(contract, "none", 1)
    combined_run = _run(contract, "combined", 1)

    artifact = _aggregate(contract, _observations(contract, [none_run, combined_run]))
    by_profile = {item["profile"]: item for item in artifact["runs"]}

    assert by_profile["none"]["metrics"]["route_to_go"] == {
        "status": "not_applicable",
        "value_ns": None,
    }
    assert by_profile["combined"]["metrics"]["route_to_go"] == {
        "status": "measured",
        "value_ns": 300,
    }


def test_zero_denominator_is_explicitly_not_observed_in_both_modes():
    contract = _contract()
    artifact = _aggregate(contract, _observations(contract, []))

    assert artifact["metrics"]["protocol_artifacts_per_accepted_result"] == {
        "status": "not_observed",
        "value": None,
        "numerator": 0,
        "denominator": 0,
    }
    assert reporter._ratio_metric(7, 0) == {
        "status": "not_observed",
        "value": None,
        "numerator": 7,
        "denominator": 0,
    }


def test_review_duplicates_use_exact_identity_not_reason_text():
    contract = _contract()
    identity = {
        "base": _git_sha(1),
        "head": _git_sha(2),
        "scope_digest": _digest(3),
        "question_digest": _digest(4),
        "reason": "same prose",
    }
    same_prose_different_tuple = dict(identity, question_digest=_digest(5))
    runs = [
        _run(contract, "verification_only", 1, reviews=[identity]),
        _run(contract, "verification_only", 2, reviews=[copy.deepcopy(identity)]),
        _run(contract, "verification_only", 3, reviews=[same_prose_different_tuple]),
    ]

    artifact = _aggregate(contract, _observations(contract, runs))

    assert artifact["metrics"]["exact_duplicate_review_count"] == 1
    assert artifact["metrics"]["review_identity_status"] == "measured"

    invalid = copy.deepcopy(identity)
    invalid["base"] = _digest(1)
    bad_run = _run(contract, "verification_only", 4, reviews=[invalid])
    assert _aggregate(contract, _observations(contract, [bad_run]))["status"] == "invalid"


def test_artifact_roots_classes_and_standby_purposes_fail_closed():
    contract = _contract()
    valid = _run(
        contract,
        "coordination_only",
        1,
        artifacts=[
            {"path": "coordination/mailbox/sent/route.md", "class": "coordination"},
            {"path": "logs/trace.json", "class": "telemetry"},
            {
                "path": "coordination/presence/standby.json",
                "class": "standby",
                "purpose": "observing",
            },
        ],
    )
    artifact = _aggregate(contract, _observations(contract, [valid]))
    assert artifact["metrics"]["protocol_artifact_count"] == 2
    assert artifact["metrics"]["telemetry_artifact_count"] == 1
    assert artifact["metrics"]["artifact_class_counts"] == {
        "coordination": 1,
        "verification": 0,
        "effect": 0,
        "standby": 1,
        "telemetry": 1,
    }

    invalid_artifacts = (
        {"path": "outside/file.json", "class": "coordination"},
        {"path": "coordination/mailbox/file.json", "class": "mystery"},
        {
            "path": "coordination/presence/file.json",
            "class": "standby",
            "purpose": "blocking",
        },
    )
    for ordinal, invalid in enumerate(invalid_artifacts, start=2):
        run = _run(contract, "coordination_only", ordinal, artifacts=[invalid])
        assert _aggregate(contract, _observations(contract, [run]))["status"] == "invalid"


def test_artifact_class_is_derived_from_fixed_path_policy():
    contract = _contract()
    artifacts = [
        {"path": "logs/trace.json", "class": "telemetry"},
        {
            "path": "coordination/presence/standby.json",
            "class": "standby",
            "purpose": "waiting",
        },
        {"path": ".codex/runtime/effect.json", "class": "effect"},
        {"path": "coordination/verification/report.json", "class": "verification"},
        {
            "path": "coordination/mailbox/sent/x-verification-report.md",
            "class": "verification",
        },
        {"path": "coordination/mailbox/sent/route.md", "class": "coordination"},
    ]
    run = _run(contract, "coordination_only", 1, artifacts=artifacts)

    artifact = _aggregate(contract, _observations(contract, [run]))

    assert artifact["status"] == "incomplete"
    assert artifact["metrics"]["artifact_class_counts"] == {
        "coordination": 1,
        "verification": 2,
        "effect": 1,
        "standby": 1,
        "telemetry": 1,
    }
    assert artifact["metrics"]["protocol_artifact_count"] == 5


def test_artifact_class_and_manifest_keys_fail_closed():
    contract = _contract()
    invalid_artifacts = (
        {"path": "logs/trace.json", "class": "coordination"},
        {"path": "coordination/mailbox/route.md", "class": "coordination", "purpose": "waiting"},
        {"path": "coordination/presence/standby.json", "class": "standby"},
        {
            "path": "coordination/presence/standby.json",
            "class": "standby",
            "purpose": "waiting",
            "extra": True,
        },
    )

    for ordinal, entry in enumerate(invalid_artifacts, start=1):
        run = _run(contract, "coordination_only", ordinal, artifacts=[entry])
        assert _aggregate(contract, _observations(contract, [run]))["status"] == "invalid"


@pytest.mark.parametrize(
    "path",
    (
        "coordination/\x00bad.json",
        "coordination/bad\nname.json",
        "coordination/bad\tname.json",
        "/coordination/absolute.json",
        "coordination/./alias.json",
        "coordination/../escape.json",
    ),
)
def test_artifact_paths_reject_controls_absolute_alias_and_escape(path):
    contract = _contract()
    run = _run(
        contract,
        "coordination_only",
        1,
        artifacts=[{"path": path, "class": "coordination"}],
    )

    assert _aggregate(contract, _observations(contract, [run]))["status"] == "invalid"


def test_artifact_path_resolution_rejects_symlink_escape(tmp_path):
    contract = _contract()
    repository = tmp_path / "repo"
    outside = tmp_path / "outside"
    repository.mkdir()
    outside.mkdir()
    (repository / "coordination").symlink_to(outside, target_is_directory=True)
    run = _run(
        contract,
        "coordination_only",
        1,
        artifacts=[{"path": "coordination/escape.json", "class": "coordination"}],
    )

    artifact = _aggregate(
        contract,
        _observations(contract, [run]),
        repository_root=repository,
    )

    assert artifact["status"] == "invalid"


def test_artifact_path_resolution_cannot_cross_declared_roots(tmp_path):
    contract = _contract()
    repository = tmp_path / "repo"
    (repository / "coordination").mkdir(parents=True)
    (repository / "logs").mkdir()
    (repository / "coordination" / "link").symlink_to(
        repository / "logs", target_is_directory=True
    )
    run = _run(
        contract,
        "coordination_only",
        1,
        artifacts=[{"path": "coordination/link/trace.json", "class": "coordination"}],
    )

    artifact = _aggregate(
        contract,
        _observations(contract, [run]),
        repository_root=repository,
    )

    assert artifact["status"] == "invalid"


def test_artifact_path_resolution_rejects_intra_root_class_disagreement(tmp_path):
    contract = _contract()
    repository = tmp_path / "repo"
    verification = repository / "coordination" / "verification"
    verification.mkdir(parents=True)
    (repository / "coordination" / "alias").symlink_to(
        verification, target_is_directory=True
    )
    run = _run(
        contract,
        "coordination_only",
        1,
        artifacts=[
            {"path": "coordination/alias/report.json", "class": "coordination"}
        ],
    )

    artifact = _aggregate(
        contract,
        _observations(contract, [run]),
        repository_root=repository,
    )

    assert artifact["status"] == "invalid"


def test_mixed_cohort_identity_and_duplicate_run_ids_are_invalid():
    contract = _contract()
    cases: list[list[dict]] = []
    wrong_host = _run(contract, "none", 1)
    wrong_host["host_identity"] = "other-host"
    cases.append([wrong_host])
    wrong_input = _run(contract, "none", 1)
    wrong_input["scenario_input_digest"] = _digest(999)
    cases.append([wrong_input])
    wrong_instrument = _run(contract, "none", 1)
    wrong_instrument["instrumentation_identity"] = "other-instrument"
    cases.append([wrong_instrument])
    duplicate = _run(contract, "none", 1)
    cases.append([duplicate, copy.deepcopy(duplicate)])

    for runs in cases:
        assert _aggregate(contract, _observations(contract, runs))["status"] == "invalid"


def test_wrong_typed_json_values_are_invalid_not_exceptions():
    contract = _contract()
    bad_profile = _run(contract, "none", 1)
    bad_profile["profile"] = []
    bad_class = _run(
        contract,
        "coordination_only",
        2,
        artifacts=[{"path": "coordination/file.json", "class": []}],
    )
    bad_endpoint = _run(contract, "none", 3)
    bad_endpoint["endpoints"]["accepted_input"]["ns"] = "1000"

    for run in (bad_profile, bad_class, bad_endpoint):
        artifact = _aggregate(contract, _observations(contract, [run]))
        assert artifact["status"] == "invalid"


def test_complete_synthetic_contract_fixture_preserves_runs_and_medians():
    contract = _contract()
    runs = _complete_runs(contract)

    artifact = _aggregate(
        contract,
        _observations(contract, runs, kind="synthetic_contract_fixture"),
        synthetic=True,
    )

    assert artifact["status"] == "incomplete"
    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["operational_provenance"] == "not_observed"
    assert artifact["evidence_kind"] == "synthetic_contract_fixture"
    assert artifact["host_identity"] == "opaque-host-a"
    assert artifact["clock_domain"] == "host-monotonic-v1"
    assert artifact["instrumentation_identity"] == "codex-runtime-endpoints-v1"
    assert artifact["contract"] == {
        "schema_version": contract["schema_version"],
        "benchmark_id": contract["benchmark_id"],
        "profiles": contract["profiles"],
        "protocol_roots": contract["protocol_roots"],
        "artifact_classes": contract["artifact_classes"],
        "review_identity_fields": contract["review_identity_fields"],
        "accepted_result_denominator": contract["accepted_result_denominator"],
    }
    assert len(artifact["raw_runs"]) == 25
    assert artifact["metrics"]["time_to_first_tool"]["median_ns"] == 100
    assert artifact["metrics"]["route_to_go"]["median_ns"] == 300
    for profile in EXPECTED_PROFILES:
        profile_metrics = artifact["metrics"]["by_profile"][profile]
        assert profile_metrics["time_to_first_tool"] == {
            "status": "measured",
            "median_ns": 100,
            "measured_count": 5,
        }
        expected_route = (
            {"status": "measured", "median_ns": 300, "measured_count": 5}
            if profile == "combined"
            else {"status": "not_applicable", "median_ns": None, "measured_count": 0}
        )
        assert profile_metrics["route_to_go"] == expected_route


def test_matching_in_memory_provenance_completes_runtime_cohort():
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = _provenance(contract, observations)

    artifact = _aggregate(
        contract,
        observations,
        verified_provenance=provenance,
    )

    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is True
    assert artifact["complete"] is True
    assert artifact["status"] == "complete"
    assert artifact["operational_provenance"] == {
        "kind": "verified_runtime_collector",
        "contract_digest": provenance.contract_digest,
        "observations_digest": provenance.observations_digest,
        "cohort_identity": dict(provenance.cohort_identity),
        "collector_identity": provenance.collector_identity,
        "source_head": provenance.source_head,
        "codex_identity": provenance.codex_identity,
        "run_record_digests": [
            {"run_id": run_id, "digest": digest}
            for run_id, digest in provenance.run_record_digests
        ],
    }


def test_verified_provenance_is_frozen():
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = _provenance(contract, observations)

    with pytest.raises(FrozenInstanceError):
        provenance.source_head = "b" * 40


def test_serialized_or_embedded_provenance_cannot_claim_completion():
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = _provenance(contract, observations)
    embedded = copy.deepcopy(observations)
    embedded["verified_provenance"] = asdict(provenance)

    embedded_artifact = _aggregate(contract, embedded)
    serialized_artifact = _aggregate(
        contract,
        observations,
        verified_provenance=asdict(provenance),
    )

    assert embedded_artifact["structural_complete"] is True
    assert embedded_artifact["operational_complete"] is False
    assert embedded_artifact["status"] == "incomplete"
    assert serialized_artifact["structural_complete"] is True
    assert serialized_artifact["operational_complete"] is False
    assert serialized_artifact["status"] == "invalid"
    assert any(
        "in-memory VerifiedBaselineProvenance" in error
        for error in serialized_artifact["errors"]
    )


def test_mutated_observations_do_not_match_verified_provenance():
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = _provenance(contract, observations)
    mutated = copy.deepcopy(observations)
    mutated["runs"][0]["accepted_result_digest"] = _digest(9_999)

    artifact = _aggregate(
        contract,
        mutated,
        verified_provenance=provenance,
    )

    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["status"] == "invalid"
    assert any("observations digest" in error for error in artifact["errors"])


def test_non_json_observations_cannot_match_a_none_digest():
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = _provenance(contract, observations)
    observations["untrusted_runtime_object"] = object()

    artifact = _aggregate(
        contract,
        observations,
        verified_provenance=replace(provenance, observations_digest=None),
    )

    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["status"] == "invalid"
    assert any("canonical JSON" in error for error in artifact["errors"])


@pytest.mark.parametrize(
    ("field", "replacement", "error_text"),
    (
        ("contract_digest", _digest(7_001), "contract digest"),
        ("observations_digest", None, "observations digest"),
        (
            "cohort_identity",
            (
                ("benchmark_id", "changed-benchmark"),
                ("host_identity", "opaque-host-a"),
                ("clock_domain", "host-monotonic-v1"),
                ("instrumentation_identity", "codex-runtime-endpoints-v1"),
            ),
            "cohort identity",
        ),
        ("collector_identity", "collector-without-digest", "collector identity"),
        ("source_head", "not-a-git-sha", "source HEAD"),
        ("codex_identity", "codex-without-digest", "Codex identity"),
    ),
)
def test_provenance_identity_or_digest_mismatch_is_invalid(
    field,
    replacement,
    error_text,
):
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = replace(_provenance(contract, observations), **{field: replacement})

    artifact = _aggregate(
        contract,
        observations,
        verified_provenance=provenance,
    )

    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["status"] == "invalid"
    assert any(error_text in error for error in artifact["errors"])


def test_run_record_provenance_requires_exact_unique_identity_digest_pairs():
    contract = _contract()
    observations = _observations(contract, _complete_runs(contract))
    provenance = _provenance(contract, observations)
    records = provenance.run_record_digests
    cases = (
        (records[:-1], "exactly 25"),
        (
            (records[0], (records[0][0], records[1][1]), *records[2:]),
            "duplicate run identity",
        ),
        (
            (records[0], (records[1][0], records[0][1]), *records[2:]),
            "duplicate run-record digest",
        ),
        (
            (("changed-run", records[0][1]), *records[1:]),
            "run identities differ",
        ),
        (
            ((records[0][0], ""), *records[1:]),
            "invalid run-record digest",
        ),
    )

    for run_record_digests, error_text in cases:
        artifact = _aggregate(
            contract,
            observations,
            verified_provenance=replace(
                provenance,
                run_record_digests=run_record_digests,
            ),
        )
        assert artifact["structural_complete"] is True
        assert artifact["operational_complete"] is False
        assert artifact["status"] == "invalid"
        assert any(error_text in error for error in artifact["errors"])


def test_synthetic_fixture_cannot_complete_with_runtime_provenance():
    contract = _contract()
    observations = _observations(
        contract,
        _complete_runs(contract),
        kind="synthetic_contract_fixture",
    )

    artifact = _aggregate(
        contract,
        observations,
        synthetic=True,
        verified_provenance=_provenance(contract, observations),
    )

    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["status"] == "invalid"
    assert any("runtime_trace" in error for error in artifact["errors"])


def test_relabelled_runtime_trace_cannot_claim_operational_completion():
    contract = _contract()
    artifact = _aggregate(
        contract,
        _observations(contract, _complete_runs(contract), kind="runtime_trace"),
    )

    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["operational_provenance"] == "not_observed"
    assert artifact["status"] == "incomplete"


def test_cli_writes_incomplete_runtime_artifact_and_exits_one(tmp_path):
    contract = _contract()
    contract_path = tmp_path / "contract.json"
    observations_path = tmp_path / "observations.json"
    output_path = tmp_path / "artifact.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    observations_path.write_text(
        json.dumps(_observations(contract, [_run(contract, "none", 1, endpoints={})])),
        encoding="utf-8",
    )

    result = reporter.main(
        [
            "--baseline-contract",
            str(contract_path),
            "--baseline-observations",
            str(observations_path),
            "--output",
            str(output_path),
        ]
    )

    assert result == 1
    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["status"] == "incomplete"
    assert artifact["complete"] is False
    assert artifact["kernel_mirror"] == KERNEL_MIRROR


def test_cli_reserves_exit_zero_until_runtime_provenance_verifier_exists(tmp_path):
    contract = _contract()
    contract_path = tmp_path / "contract.json"
    observations_path = tmp_path / "observations.json"
    output_path = tmp_path / "artifact.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    observations_path.write_text(
        json.dumps(
            _observations(contract, _complete_runs(contract), kind="runtime_trace")
        ),
        encoding="utf-8",
    )

    result = reporter.main(
        [
            "--baseline-contract",
            str(contract_path),
            "--baseline-observations",
            str(observations_path),
            "--output",
            str(output_path),
        ]
    )

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert result == 1
    assert artifact["structural_complete"] is True
    assert artifact["operational_complete"] is False
    assert artifact["operational_provenance"] == "not_observed"
    assert artifact["status"] == "incomplete"


def test_cli_help_says_operational_exit_zero_is_currently_unavailable(capsys):
    with pytest.raises(SystemExit) as exc_info:
        reporter.main(["--help"])

    assert exc_info.value.code == 0
    assert "exit 0 is reserved and currently unavailable" in capsys.readouterr().out


def test_cli_writes_semantically_invalid_evidence_and_exits_two(tmp_path):
    contract = _contract()
    run = _run(contract, "none", 1)
    run["host_identity"] = "other-host"
    contract_path = tmp_path / "contract.json"
    observations_path = tmp_path / "observations.json"
    output_path = tmp_path / "artifact.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    observations_path.write_text(
        json.dumps(_observations(contract, [run])), encoding="utf-8"
    )

    result = reporter.main(
        [
            "--baseline-contract",
            str(contract_path),
            "--baseline-observations",
            str(observations_path),
            "--output",
            str(output_path),
        ]
    )

    assert result == 2
    assert json.loads(output_path.read_text(encoding="utf-8"))["status"] == "invalid"


def test_typed_but_malformed_contract_is_invalid_not_an_exception():
    contract = _contract()
    contract["artifact_classes"]["telemetry"] = "not-an-object"

    artifact = _aggregate(contract, _observations(contract, []))

    assert artifact["status"] == "invalid"
    assert any("telemetry" in error for error in artifact["errors"])


@pytest.mark.parametrize(
    "payload",
    (
        '{"value": 1, "value": 2}',
        '{"value": NaN}',
        '{"value": Infinity}',
        '{"value": -Infinity}',
        '{"value": 1e999}',
        '{"value": -1e999}',
    ),
)
def test_baseline_json_loader_rejects_duplicate_keys_and_nonfinite_values(
    tmp_path, payload
):
    path = tmp_path / "input.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(ValueError):
        reporter._read_json(path)


def test_artifact_writer_rejects_nonfinite_values_before_write(tmp_path):
    path = tmp_path / "artifact.json"

    with pytest.raises(ValueError):
        reporter.write_artifact(path, {"value": float("nan")})

    assert not path.exists()


@pytest.mark.parametrize("overflow", ("1e999", "-1e999"))
def test_cli_rejects_json_exponent_overflow_without_writing(tmp_path, overflow):
    contract_path = tmp_path / "contract.json"
    observations_path = tmp_path / "observations.json"
    output_path = tmp_path / "artifact.json"
    contract_path.write_text(json.dumps(_contract()), encoding="utf-8")
    observations_path.write_text(f'{{"overflow": {overflow}}}', encoding="utf-8")

    result = reporter.main(
        [
            "--baseline-contract",
            str(contract_path),
            "--baseline-observations",
            str(observations_path),
            "--output",
            str(output_path),
        ]
    )

    assert result == 2
    assert not output_path.exists()


def test_cli_rejects_synthetic_contract_fixture(tmp_path):
    contract = _contract()
    contract_path = tmp_path / "contract.json"
    observations_path = tmp_path / "observations.json"
    output_path = tmp_path / "artifact.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    observations_path.write_text(
        json.dumps(
            _observations(
                contract,
                [_run(contract, "none", 1)],
                kind="synthetic_contract_fixture",
            )
        ),
        encoding="utf-8",
    )

    result = reporter.main(
        [
            "--baseline-contract",
            str(contract_path),
            "--baseline-observations",
            str(observations_path),
            "--output",
            str(output_path),
        ]
    )

    assert result == 2
    assert json.loads(output_path.read_text(encoding="utf-8"))["status"] == "invalid"


def test_legacy_wave_mode_remains_callable(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(reporter, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(reporter, "collect_report", lambda *args: {"legacy": True})
    monkeypatch.setattr(reporter, "render_summary", lambda report, output: "legacy summary")

    assert reporter.main(["--wave", "2", "--stdout-only"]) == 0
    assert capsys.readouterr().out.strip() == "legacy summary"
