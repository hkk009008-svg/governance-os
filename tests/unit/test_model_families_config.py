from __future__ import annotations

import tomllib
from pathlib import Path

import ci_admission_gate
import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]


def test_config_is_loaded_and_is_an_authority_surface() -> None:
    payload = tomllib.loads(
        (ROOT / "config/model-families.toml").read_text(encoding="utf-8")
    )
    assert payload["schema_version"] == 1
    assert "config/" in ci_admission_gate.AUTHORITY_SURFACES
    assert model.CURRENT_REVIEW_FAMILIES == {"claude", "gpt"}


def test_every_current_model_is_registered() -> None:
    current = model.CURRENT_AUTHOR_MODEL_IDS | model.CURRENT_REVIEWER_MODEL_IDS
    assert current <= set(model.MODEL_ID_REGISTRY)
    assert {model.MODEL_ID_REGISTRY[item] for item in model.CURRENT_REVIEWER_MODEL_IDS} == {
        "claude",
        "gpt",
    }


def test_unadmitted_registered_models_do_not_gain_review_authority() -> None:
    assert model.model_family("grok-4.6") == "grok"
    assert not model.model_is_current_author("grok-4.6")
    assert not model.model_is_current_reviewer("grok-4.6")
