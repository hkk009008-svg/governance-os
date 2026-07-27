"""Closed Codex runtime identity and derived-policy regressions."""

from __future__ import annotations

import pytest

from scripts import codex_protocol_model as model


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        (
            {},
            model.RuntimeIdentity(
                mode="readiness-bridge",
                seat=None,
                role="readiness-bridge",
                behavior_source=None,
            ),
        ),
        (
            {"CODEX_SEAT": "director2"},
            model.RuntimeIdentity(
                mode="live-seat",
                seat="director2",
                role="director2",
                behavior_source="director",
            ),
        ),
        (
            {"CODEX_AGENT_ROLE": "operator"},
            model.RuntimeIdentity(
                mode="live-seat",
                seat="operator",
                role="operator",
                behavior_source="operator2",
            ),
        ),
        (
            {
                "CODEX_AGENT_MODE": "coordinator",
                "CODEX_AGENT_ROLE": "coordinator2",
            },
            model.RuntimeIdentity(
                mode="coordinator",
                seat="coordinator2",
                role="coordinator2",
                behavior_source=None,
            ),
        ),
        (
            {"CODEX_AGENT_ROLE": "lane-v-verifier"},
            model.RuntimeIdentity(
                mode="subagent",
                seat=None,
                role="lane-v-verifier",
                behavior_source=None,
            ),
        ),
    ],
)
def test_runtime_identity_closes_each_supported_combination(
    environ: dict[str, str],
    expected: model.RuntimeIdentity,
) -> None:
    assert model.RuntimeIdentity.from_environ(environ) == expected


@pytest.mark.parametrize(
    "environ",
    [
        {"CODEX_AGENT_MODE": "unknown"},
        {"CODEX_SEAT": "unknown"},
        {"CODEX_AGENT_ROLE": "unknown"},
        {"CODEX_AGENT_MODE": "live-seat"},
        {"CODEX_AGENT_MODE": "coordinator"},
        {
            "CODEX_AGENT_MODE": "live-seat",
            "CODEX_SEAT": "operator",
            "CODEX_AGENT_ROLE": "director",
        },
        {
            "CODEX_AGENT_MODE": "subagent",
            "CODEX_SEAT": "operator",
            "CODEX_AGENT_ROLE": "lane-v-verifier",
        },
        {
            "CODEX_SEAT": "director",
            "CODEX_BEHAVIOR_SOURCE": "operator2",
        },
    ],
)
def test_runtime_identity_rejects_unknown_incomplete_or_contradictory_inputs(
    environ: dict[str, str],
) -> None:
    with pytest.raises(model.RuntimeIdentityError):
        model.RuntimeIdentity.from_environ(environ)


def test_runtime_identity_carries_launcher_selected_model_without_env_authority() -> None:
    identity = model.RuntimeIdentity.for_seat("operator2", model="gpt-reviewer")

    assert identity.model == "gpt-reviewer"
    assert identity.as_env() == {
        "CODEX_AGENT_MODE": "live-seat",
        "CODEX_AGENT_ROLE": "operator2",
        "CODEX_SEAT": "operator2",
        "CODEX_BEHAVIOR_SOURCE": "operator2",
    }


def test_ambient_policy_and_git_index_cannot_override_derived_contract() -> None:
    baseline = model.infer_runtime_env({"CODEX_SEAT": "operator2"})
    overridden = model.infer_runtime_env(
        {
            "CODEX_SEAT": "operator2",
            "CODEX_CAPABILITY_MODE": "capacity-max",
            "CODEX_MUTATION_SCOPE": "all",
            "CODEX_AUTHORITY_SCOPE": "all",
            "CODEX_MAILBOX_POLICY": "consume-all",
            "CODEX_GIT_POLICY": "ambient-index",
            "CODEX_VERIFICATION_POLICY": "self-go",
            "CODEX_CONTEXT_SOURCES": "anything",
            "CODEX_OUTPUT_CONTRACT": "anything",
            "CODEX_DECISION_BOUNDARY": "anything",
            "CODEX_NEXT_ACTION_POLICY": "anything",
            "CODEX_SIDE_EFFECT_POLICY": "pre-authorized",
            "GIT_INDEX_FILE": "/ambient/index",
        }
    )

    assert overridden == baseline
    assert overridden["CODEX_GIT_POLICY"] == "native-worktree-index"
    assert "GIT_INDEX_FILE" not in overridden


def test_review_profiles_are_closed_and_risk_proportional() -> None:
    ordinary = model.review_profile_for("ordinary-local")
    material = model.review_profile_for("material-behavior")
    high_risk = model.review_profile_for("high-risk-control")
    external = model.review_profile_for("external-effect")

    assert ordinary.focused_verification
    assert not ordinary.requires_non_author_review
    assert material.requires_non_author_review
    assert material.requires_exact_range
    assert not material.requires_different_model
    assert high_risk.requires_non_author_review
    assert high_risk.requires_exact_range
    assert high_risk.requires_different_model
    assert high_risk.requires_abuse_class_assessment
    assert external.requires_live_authorization

    with pytest.raises(ValueError, match="unknown Codex review risk class"):
        model.review_profile_for("invented")


def test_work_modes_are_closed_and_phase_proportional() -> None:
    explore = model.work_profile_for("explore")
    validate = model.work_profile_for("validate")
    promote = model.work_profile_for("promote")

    assert explore.rerun_policy == "recorded-reruns-allowed"
    assert explore.canonical_mutation_policy == "forbidden"
    assert explore.review_policy == "none-until-transfer-or-phase-change"
    assert explore.claim_policy == "phase-transition-claims-only"
    assert explore.record_policy == (
        "one-campaign-brief-plus-automatic-attempt-log"
    )
    assert not explore.requires_frozen_inputs
    assert not explore.requires_non_author_review
    assert not explore.requires_rollback_point

    assert validate.rerun_policy == "frozen-input-reproduction"
    assert validate.canonical_mutation_policy == "forbidden"
    assert validate.review_policy == "one-non-author-candidate-review"
    assert validate.claim_policy == "load-bearing-candidate-claims"
    assert validate.record_policy == "frozen-report-plus-generated-manifest"
    assert validate.requires_frozen_inputs
    assert validate.requires_non_author_review
    assert not validate.requires_rollback_point

    assert promote.rerun_policy == "reviewed-candidate-only"
    assert promote.canonical_mutation_policy == "separately-authorized"
    assert promote.review_policy == "reviewed-candidate-plus-effect-authority"
    assert promote.claim_policy == (
        "load-bearing-claims-plus-independent-review"
    )
    assert promote.record_policy == "rollback-record-plus-approval-evidence"
    assert promote.requires_frozen_inputs
    assert promote.requires_non_author_review
    assert promote.requires_rollback_point

    with pytest.raises(ValueError, match="unknown Codex work mode"):
        model.work_profile_for("invented")


def test_explore_profile_cannot_be_presented_as_promote() -> None:
    explore = model.work_profile_for("explore")
    promote = model.work_profile_for("promote")

    assert explore.work_mode == "explore"
    assert promote.work_mode == "promote"
    assert explore.canonical_mutation_policy != promote.canonical_mutation_policy
    assert explore.review_policy != promote.review_policy
    assert not explore.requires_rollback_point
    assert promote.requires_rollback_point
