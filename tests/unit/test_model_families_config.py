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

_CURRENT_DESKTOP_MODELS = {
    "gpt": set("gpt-5.6-sol gpt-5.6-terra gpt-5.6-luna gpt-5.5 gpt-5.4 "
               "gpt-5.4-mini gpt-5.3-codex-spark gpt-oss-120b-medium".split()),
    "claude": {
        "claude-opus-5", "claude-fable-5",
        "claude-opus-4-7", "claude-sonnet-5", "claude-sonnet-4-6",
        "claude-opus-4-6-thinking",
    },
    "gemini": set(
        "gemini-3.7-flash-high gemini-3.7-flash-medium gemini-3.7-flash-low "
        "gemini-3.6-flash-high gemini-3.6-flash-medium gemini-3.6-flash-low "
        "gemini-3.5-flash-high gemini-3.5-flash-medium gemini-3.5-flash-low "
        "gemini-3.1-pro-high gemini-3.1-pro-low".split()
    ),
}

_CURRENT_DESKTOP_DISPLAY_ALIASES = {
    "opus": "claude-opus-4-7", "opus[1m]": "claude-opus-4-7",
    "claude-opus-4-7[1m]": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6", "sonnet[1m]": "claude-sonnet-4-6",
    "claude-sonnet-4-6[1m]": "claude-sonnet-4-6",
    **{
        f"Gemini {version} Flash ({level.title()})": f"gemini-{version}-flash-{level}"
        for version in ("3.7", "3.6", "3.5")
        for level in ("high", "medium", "low")
    },
    "Gemini 3.1 Pro (High)": "gemini-3.1-pro-high",
    "Gemini 3.1 Pro (Low)": "gemini-3.1-pro-low",
    "Claude Sonnet 4.6 (Thinking)": "claude-sonnet-4-6",
    "Claude Opus 4.6 (Thinking)": "claude-opus-4-6-thinking",
    "GPT-OSS 120B (Medium)": "gpt-oss-120b-medium",
}


def test_migration_snapshot_is_a_subset_of_the_loaded_registry() -> None:
    for model_id, family in _MIGRATION_SNAPSHOT.items():
        assert model.MODEL_ID_REGISTRY.get(model_id) == family, model_id
    assert model.MODEL_PROVIDER_FAMILIES == {
        "anthropic-": "claude", "openai-": "gpt",
        "google-": "gemini", "xai-": "grok",
    }
    assert model.CURRENT_REVIEW_FAMILIES == frozenset({"claude", "gpt"})
    expected = {
        model_id: family
        for family, model_ids in _CURRENT_DESKTOP_MODELS.items()
        for model_id in model_ids
    }
    assert model.CURRENT_AUTHOR_MODEL_IDS == frozenset(expected)
    non_reviewers = _CURRENT_DESKTOP_MODELS["gemini"] | {"gpt-oss-120b-medium"}
    assert model.CURRENT_REVIEWER_MODEL_IDS == frozenset(expected) - non_reviewers
    assert model.CURRENT_REVIEW_FAMILY_CUTOVER == (
        "b1390a244d2368e89bb65d65a148e55bac0d8df0"
    )


def test_current_desktop_model_surface_is_parseable_without_widening_review() -> None:
    for family, model_ids in _CURRENT_DESKTOP_MODELS.items():
        for model_id in model_ids:
            assert model.MODEL_ID_REGISTRY.get(model_id) == family, model_id
            assert model.model_family(model_id) == family, model_id
    for display, model_id in _CURRENT_DESKTOP_DISPLAY_ALIASES.items():
        assert model.MODEL_DISPLAY_ALIASES.get(display) == model_id, display
        assert model.model_family(display) == model.model_family(model_id), display

    pairs = (
        ("gpt-5.6-luna", "Gemini 3.7 Flash (High)", False),
        ("Gemini 3.7 Flash (High)", "opus[1m]", True),
        ("gpt-5.6-luna", "opus[1m]", True),
        ("codex-gpt-5.3-codex-spark", "anthropic-claude-sonnet-4-6", True),
    )
    assert all(model.models_are_current_review_pair(a, b) is result
               for a, b, result in pairs)


def test_current_author_and_reviewer_admission_are_explicit() -> None:
    assert tuple(map(model.model_is_current_author, (
        "gpt-5.6-sol", "Gemini 3.7 Flash (High)",
        "claude-opus-5-thinking-high", "some-future-frontier-model",
    ))) == (True, True, False, False)
    assert tuple(map(model.model_is_current_reviewer, (
        "gpt-5.6-terra", "opus[1m]", "Gemini 3.7 Flash (High)",
        "claude-opus-5-thinking-high",
    ))) == (True, True, False, False)
    # The two primary current Claude desktop models are admitted for both
    # responsibilities; a retired sibling ID next to them is not.
    assert tuple(map(model.model_is_current_author, (
        "claude-opus-5", "claude-fable-5",
    ))) == (True, True)
    assert tuple(map(model.model_is_current_reviewer, (
        "claude-opus-5", "claude-fable-5",
    ))) == (True, True)


def test_unknown_model_ids_never_satisfy_a_different_family_claim() -> None:
    assert model.model_family("some-future-frontier-model") is None
    assert model.models_are_independent("some-future-frontier-model", "gpt-5") is False
    assert model.models_are_independent("gpt-5", "some-future-frontier-model") is False
    assert model.models_are_independent("gpt-5.6-sol", "gemini-3.6-flash-high") is True
    assert model.models_are_independent("gpt-5.6-sol", "gpt-5") is False
    assert not model.models_are_current_review_pair(
        "gpt-5.6-sol", "claude-opus-5-thinking-high"
    )
    assert model.models_are_current_review_pair("gpt-5.6-sol", "claude-opus-5")
    assert model.model_family("claude-opus-4-7") == "claude"
    assert model.models_are_current_review_pair("gpt-5.6-sol", "claude-opus-4-7")
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


def _admission(
    families: tuple[str, ...] = ("gpt",),
    authors: tuple[str, ...] = ("gpt-5",),
    reviewers: tuple[str, ...] = ("gpt-5",),
) -> str:
    return (
        "[review_admission]\n"
        f"active_families = {list(families)!r}\n"
        f"active_author_models = {list(authors)!r}\n"
        f"active_reviewer_models = {list(reviewers)!r}\n"
        f'historical_cutover = {"a" * 40!r}\n'
    )


@pytest.mark.parametrize(
    "admission",
    (
        "",
        '[review_admission]\nactive_families = ["gpt"]\n',
        _admission(("gpt", "mystery")),
        _admission(("gpt", "gpt")),
        _admission(reviewers=("gpt-5", "gpt-5")),
        _admission(authors=("gpt-future",)),
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
        'active_author_models = ["claude-opus-5", "gpt-5"]\n'
        'active_reviewer_models = ["claude-opus-5", "gpt-5"]\n'
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
