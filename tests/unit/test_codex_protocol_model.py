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
        ("Gemini 3.7 Flash (High)", "gemini"),
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
    assert model.model_is_current_author("gemini-3.7-flash-high")
    assert not model.model_is_current_reviewer("gemini-3.7-flash-high")
    assert model.model_is_current_reviewer("claude-opus-5")
    assert model.model_is_current_reviewer("gpt-5.6-sol")


def test_high_risk_pair_requires_current_different_families() -> None:
    assert model.models_are_current_review_pair("gpt-5.6-sol", "claude-opus-5")
    assert not model.models_are_current_review_pair("gpt-5.6-sol", "gpt-5.6-terra")
    assert not model.models_are_current_review_pair(
        "gpt-5.6-sol", "gemini-3.7-flash-high"
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
