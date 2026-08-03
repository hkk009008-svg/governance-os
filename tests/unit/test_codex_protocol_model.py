"""Closed Codex runtime identity and derived-policy regressions."""

from __future__ import annotations

import pytest

from scripts import codex_protocol_model as model


@pytest.mark.parametrize(
    ("model_id", "family"),
    (
        ("claude-fable-5", "claude"),
        ("claude-opus-5", "claude"),
        ("anthropic-claude-opus-5", "claude"),
        ("claude-code-anthropic-claude-sonnet-5", "claude"),
        ("gpt-5", "gpt"),
        ("gpt-5.6-sol", "gpt"),
        ("gpt-5.6-terra", "gpt"),
        ("codex-gpt-5.6-terra", "gpt"),
        ("openai-gpt-5.6-sol", "gpt"),
        ("GPT-5 Codex", "gpt"),
        ("chatgpt-4o", "gpt"),
        ("o1", "gpt"),
        ("o3-mini", "gpt"),
        ("o4", "gpt"),
        ("gpt-oss-120b", "gpt"),
        ("gpt-oss-120b-medium", "gpt"),
        ("codex-cursor-openai-gpt-5.6-terra", "gpt"),
        ("antigravity-gemini-3.6", "gemini"),
        ("google-gemini-3.1-pro-high", "gemini"),
        ("gemini-3.6-flash", "gemini"),
        ("gemini-3.6-flash-high", "gemini"),
        ("gemini-3.6-flash-medium", "gemini"),
        ("gemini-3.6-flash-low", "gemini"),
        ("gemini-3.5-flash-high", "gemini"),
        ("gemini-3.5-flash-medium", "gemini"),
        ("gemini-3.5-flash-low", "gemini"),
        ("gemini-3.1-pro-low", "gemini"),
        ("claude-sonnet-4-6", "claude"),
        ("claude-opus-4-6-thinking", "claude"),
        ("Gemini 3.1 Pro (High)", "gemini"),
        ("cursor-agy-google-gemini-3.1-pro-high", "gemini"),
        ("grok-4.5", "grok"),
        ("xai-grok-4", "grok"),
    ),
)
def test_model_family_recognizes_only_registered_model_ids(
    model_id: str, family: str,
) -> None:
    assert model.model_family(model_id) == family


@pytest.mark.parametrize(
    "model_id",
    (
        "",
        "   ",
        "-gpt-5",
        ".claude-opus-5",
        "_gemini-3.1",
        "composer-2.5",
        "fixture",
        "claudex-5",
        "claude-mystery-5",
        "gem-3.1-pro",
        "gemini-pro",
        "gpt-forged",
        "gpt-5-forged",
        "chatgpt-4o-counterfeit",
        "o3-counterfeit",
        "gpt-oss-forged",
        "gpt-oss-120x",
        "claude-opus-5-forged",
        "gemini-3.1-forged",
        "grok-beta",
        "grok-4-forged",
        "openai-claude-opus-5",
        "anthropic-gpt-5",
        "google-grok-4",
        "xai-gemini-3.1",
        "openai-openai-gpt-5",
        "gpt--5",
        "gpt_5",
        "gpt/5",
        "antigravity",
        "claude",
        "gpt",
        "chatgpt",
        "gpt-oss",
        "gemini",
        "grok",
        " gpt-5",
        "gpt-5 ",
        "\tgpt-5",
        "gpt-5\n",
        " Gemini 3.1 Pro (High) ",
        "gpt-\x1f5",
        "gpt-5-999999",
        "claude-opus-5-999999",
        "gemini-3-999999",
        "grok-4-999999",
        "gpt-5-sol-terra",
        "gpt-5-preview-preview",
        "gpt-5-mini-sol",
        "gemini-3.1-pro-flash",
        "gemini-3.1-high-low",
        "gpt-999",
        "chatgpt-999",
        "claude-opus-999",
        "gemini-999",
        "grok-999",
        "gpt-5 codex",
        "gemini 3.1 pro (high)",
    ),
)
def test_model_family_rejects_unknown_invented_or_malformed_labels(
    model_id: str,
) -> None:
    assert model.model_family(model_id) is None


@pytest.mark.parametrize(
    ("left", "right"),
    (
        ("claude-opus-5", "anthropic-claude-sonnet-5"),
        ("gpt-5.6-sol", "openai-gpt-5.6-terra"),
        ("gemini-3.1-pro-high", "google-gemini-3.6-flash"),
        ("grok-4", "xai-grok-4.5"),
        ("invented-a", "claude-opus-5"),
        ("gpt-5", "invented-b"),
        ("invented-a", "invented-b"),
    ),
)
def test_model_independence_fails_conservatively(
    left: str, right: str,
) -> None:
    assert model.models_are_independent(left, right) is False


def test_model_independence_requires_two_recognized_distinct_families() -> None:
    assert model.models_are_independent("claude-opus-5", "openai-gpt-5") is True


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
