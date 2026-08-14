"""Model-family data is trust-granting schema input: pinned, fail-closed."""

from __future__ import annotations

import sys
import subprocess
import tomllib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import ci_admission_gate  # noqa: E402
import codex_protocol_model as model  # noqa: E402

# Frozen migration snapshot: the registry as it lived in policy code at the
# relocation commit. Additions are free (subset assertion); silently dropping
# or re-familying one of these entries is exactly the abuse the relocation
# must not enable.
_MIGRATION_SNAPSHOT = {
    "claude-fable-5": "claude", "claude-opus-5": "claude",
    "claude-sonnet-5": "claude", "claude-sonnet-4-6": "claude",
    "claude-opus-4-6-thinking": "claude",
    "gpt-5": "gpt", "gpt-5-codex": "gpt", "gpt-5.6-sol": "gpt",
    "gpt-5.6-terra": "gpt", "chatgpt-4o": "gpt", "o1": "gpt", "o3": "gpt",
    "o3-mini": "gpt", "o4": "gpt", "gpt-oss-120b": "gpt",
    "gpt-oss-120b-medium": "gpt",
    "gemini-3.6": "gemini", "gemini-3.6-flash": "gemini",
    "gemini-3.6-flash-high": "gemini", "gemini-3.6-flash-medium": "gemini",
    "gemini-3.6-flash-low": "gemini", "gemini-3.5-flash-high": "gemini",
    "gemini-3.5-flash-medium": "gemini", "gemini-3.5-flash-low": "gemini",
    "gemini-3.1-pro-high": "gemini", "gemini-3.1-pro-low": "gemini",
    "grok-4": "grok", "grok-4.5": "grok",
}


def test_migration_snapshot_is_a_subset_of_the_loaded_registry() -> None:
    for model_id, family in _MIGRATION_SNAPSHOT.items():
        assert model.MODEL_ID_REGISTRY.get(model_id) == family, model_id
    assert model.MODEL_PROVIDER_FAMILIES == {
        "anthropic-": "claude", "openai-": "gpt",
        "google-": "gemini", "xai-": "grok",
    }
    assert model.CURRENT_REVIEW_FAMILIES == frozenset({"claude", "gpt"})
    assert model.CURRENT_REVIEW_FAMILY_CUTOVER == (
        "edc2cbe8528620ba22a5cb657bddbbf7c4820d4f"
    )


def test_unknown_model_ids_never_satisfy_a_different_family_claim() -> None:
    assert model.model_family("some-future-frontier-model") is None
    assert model.models_are_independent("some-future-frontier-model", "gpt-5") is False
    assert model.models_are_independent("gpt-5", "some-future-frontier-model") is False
    assert model.models_are_independent("gpt-5.6-sol", "gemini-3.6-flash-high") is True
    assert model.models_are_independent("gpt-5.6-sol", "gpt-5") is False
    assert model.models_are_current_review_pair("gpt-5.6-sol", "claude-opus-5")
    assert not model.models_are_current_review_pair(
        "gpt-5.6-sol", "gemini-3.6-flash-high"
    )
    assert not model.models_are_current_review_pair("grok-4.5", "claude-opus-5")


@pytest.mark.parametrize(
    "content",
    [
        None,  # missing file
        "{not toml",
        'schema_version = 2\n[provider_prefixes]\n"openai-" = "gpt"\n',
        'schema_version = 1\n[provider_prefixes]\n"openai-" = "gpt"\n',  # tables missing
        (
            'schema_version = 1\n[provider_prefixes]\n"openai-" = "gpt"\n'
            '[families]\n"x-model" = "mystery"\n[display_aliases]\n"X" = "x-model"\n'
        ),  # family with no provider prefix
    ],
    ids=["missing", "unparsable", "wrong-version", "missing-tables", "unknown-family"],
)
def test_loader_fails_closed(tmp_path: Path, content: str | None) -> None:
    config = tmp_path / "model-families.toml"
    if content is not None:
        config.write_text(content, encoding="utf-8")
    with pytest.raises(RuntimeError):
        model.load_model_families(config)


def test_config_is_an_authority_surface_at_the_admission_gate() -> None:
    assert "config/" in ci_admission_gate.AUTHORITY_SURFACES
    payload = tomllib.loads(
        (_REPO_ROOT / "config/model-families.toml").read_text(encoding="utf-8")
    )
    assert payload["schema_version"] == 1
    assert "high-risk-control" in (
        _REPO_ROOT / "config/model-families.toml"
    ).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "admission",
    (
        "",
        '[review_admission]\nactive_families = ["gpt"]\n',
        (
            '[review_admission]\nactive_families = ["gpt", "mystery"]\n'
            'historical_cutover = "' + "a" * 40 + '"\n'
        ),
        (
            '[review_admission]\nactive_families = ["gpt", "gpt"]\n'
            'historical_cutover = "' + "a" * 40 + '"\n'
        ),
    ),
)
def test_current_review_admission_fails_closed(
    tmp_path: Path, admission: str
) -> None:
    config = tmp_path / "model-families.toml"
    config.write_text(
        (
            'schema_version = 1\n[provider_prefixes]\n"openai-" = "gpt"\n'
            '[families]\n"gpt-5" = "gpt"\n'
            '[display_aliases]\n"GPT-5" = "gpt-5"\n'
            + admission
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError):
        model.load_review_admission(config)


def test_retired_registry_entries_remain_historically_parseable_only() -> None:
    """Historical labels parse, but cannot grant current review authority."""

    assert model.model_family("xai-grok-4.6-xhigh-fast") == "grok"
    assert model.model_family("claude-opus-5-thinking-high") == "claude"
    assert model.models_are_independent(
        "xai-grok-4.6-xhigh-fast", "claude-opus-5-thinking-high"
    ) is True
    assert model.models_are_current_review_pair(
        "xai-grok-4.6-xhigh-fast", "claude-opus-5-thinking-high"
    ) is False
    # Existing IDs keep their families; this addition does not re-family them.
    assert model.model_family("grok-4.5") == "grok"
    assert model.model_family("claude-opus-5") == "claude"


def test_configured_historical_cutover_resolves_and_is_ancestor_of_head() -> None:
    completed = subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "-C",
            str(_REPO_ROOT),
            "merge-base",
            "--is-ancestor",
            model.CURRENT_REVIEW_FAMILY_CUTOVER,
            "HEAD",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
        check=False,
    )
    assert completed.returncode == 0


def test_review_admission_rejects_valid_shaped_unreachable_cutover(
    tmp_path: Path,
) -> None:
    config = tmp_path / "config/model-families.toml"
    config.parent.mkdir()
    config.write_text(
        'schema_version = 1\n'
        '[review_admission]\n'
        'active_families = ["claude", "gpt"]\n'
        'historical_cutover = "' + "a" * 40 + '"\n'
        '[provider_prefixes]\n'
        '"anthropic-" = "claude"\n'
        '"openai-" = "gpt"\n'
        '[families]\n'
        '"claude-opus-5" = "claude"\n'
        '"gpt-5" = "gpt"\n'
        '[display_aliases]\n'
        '"GPT-5" = "gpt-5"\n',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="ancestor of HEAD"):
        model.load_review_admission(config)
