from __future__ import annotations

from pathlib import Path

import pytest

import codex_protocol_model as model


@pytest.mark.parametrize(
    ("model_id", "family"),
    [
        ("gpt-5.6-sol", "gpt"),
        ("codex-openai-gpt-5.6-terra", "gpt"),
        ("claude-opus-5", "claude"),
        ("anthropic-claude-sonnet-5", "claude"),
        ("Gemini 3.8 Flash (High)", "gemini"),
        ("xai-grok-4.6", "grok"),
    ],
)
def test_registered_models_normalize_to_provider_family(
    model_id: str, family: str
) -> None:
    assert model.model_family(model_id) == family


@pytest.mark.parametrize(
    "model_id", ["", "future-model", " gpt-5.6-sol", "openai-claude-opus-5"]
)
def test_unknown_or_malformed_models_fail_closed(model_id: str) -> None:
    assert model.model_family(model_id) is None
    assert not model.model_is_current_reviewer(model_id)


def test_review_admission_distinguishes_author_and_reviewer() -> None:
    assert model.model_is_current_author("gemini-3.8-flash-high")
    assert not model.model_is_current_reviewer("gemini-3.8-flash-high")
    for retired in (
        "gemini-3.7-flash-high",
        "Gemini 3.7 Flash (High)",
        "codex-google-gemini-3.7-flash-high",
        "gemini-3.1-pro-high",
    ):
        assert not model.model_is_current_author(retired)
    assert model.model_is_current_reviewer("claude-opus-5")
    assert model.model_is_current_reviewer("gpt-5.6-sol")


def test_high_risk_pair_requires_current_different_families() -> None:
    assert model.models_are_current_review_pair("gpt-5.6-sol", "claude-opus-5")
    assert not model.models_are_current_review_pair("gpt-5.6-sol", "gpt-5.6-terra")
    assert not model.models_are_current_review_pair(
        "gpt-5.6-sol", "gemini-3.8-flash-high"
    )


def test_risk_profiles_are_small_and_proportional() -> None:
    assert not model.review_profile_for("ordinary-local").requires_non_author_review
    assert model.review_profile_for("material-behavior").requires_exact_range
    high = model.review_profile_for("high-risk-control")
    assert high.requires_different_model and high.requires_abuse_class_assessment
    assert model.review_profile_for("external-effect").requires_live_authorization
    with pytest.raises(ValueError, match="unknown review risk class"):
        model.review_profile_for("invented")


def test_configuration_loader_fails_closed(tmp_path: Path) -> None:
    bad = tmp_path / "models.toml"
    bad.write_text("schema_version = 2\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        model.load_model_families(bad)


def test_unregistered_point_release_may_author_but_never_review() -> None:
    assert "claude-fable-5-2" not in model.MODEL_ID_REGISTRY
    assert model.model_family("claude-fable-5-2") == "claude"
    assert model.model_family_matches_member("claude-fable-5-2", "claude")
    assert model.model_is_current_author("claude-fable-5-2")
    assert not model.model_is_current_reviewer("claude-fable-5-2")
    assert model.models_are_current_review_pair("claude-fable-5-2", "gpt-5.6-sol")
    assert not model.models_are_current_review_pair("claude-fable-5-2", "claude-opus-5")
    assert not model.models_are_current_review_pair("gpt-5.6-sol", "claude-fable-5-2")
    assert model.model_is_current_author("gemini-9-pro-high")
    assert model.model_is_current_author("codex-openai-gpt-7-nova")


def test_prefix_admission_revives_nothing_and_admits_no_foreign_family() -> None:
    assert not model.model_is_current_author("gemini-3.7-flash-high")  # registered, retired
    assert not model.model_is_current_author("grok-5")  # family with no active author
    assert not model.model_is_current_author("openai-claude-9")  # provider conflicts
    assert model.model_family("openai-claude-9") is None
    for bare in ("claude-", "gpt-", "claudette-1", "CLAUDE-FABLE-5-2 "):
        assert not model.model_is_current_author(bare), bare


def test_family_prefix_table_fails_closed(tmp_path: Path) -> None:
    for body in (
        'schema_version = 1\n[provider_prefixes]\n"anthropic-" = "claude"\n',
        'schema_version = 1\n[provider_prefixes]\n"anthropic-" = "claude"\n'
        '[family_prefixes]\n"claude-" = "mystery"\n',
        'schema_version = 1\n[provider_prefixes]\n"anthropic-" = "claude"\n'
        '[family_prefixes]\n"claude" = "claude"\n',
    ):
        bad = tmp_path / "models.toml"
        bad.write_text(body, encoding="utf-8")
        with pytest.raises(RuntimeError, match="family_prefixes"):
            model.load_family_prefixes(bad)
