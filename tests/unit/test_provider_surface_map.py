"""Executable inventory for the supported host-provider surface.

Pipeline supports exactly the Codex and Claude adapters.  The glob-based
checks are deliberate: a retired adapter must not be able to return under a
new filename without changing this high-risk-control test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import codex_protocol_model as protocol_model


ROOT = Path(__file__).resolve().parents[2]

ADVISORS = (
    "amnesiac-prober",
    "lane-v-verifier",
    "money-gate-reviewer",
    "readiness-bridge",
)

PROVIDERS = {
    "codex": {
        "adapter": "docs/protocol/codex/continuation.md",
        "agents_dir": ".codex/agents",
        "agent_suffix": ".toml",
        "launcher": "coordination/bin/codex-seat",
    },
    "claude": {
        "adapter": "docs/protocol/claude/continuation.md",
        "agents_dir": ".claude/agents",
        "agent_suffix": ".md",
        "launcher": None,
    },
}


def _assert_supported_adapter_inventory(root: Path) -> None:
    discovered = {
        path.parent.name
        for path in (root / "docs/protocol").glob("*/continuation.md")
    }

    assert discovered == set(PROVIDERS)


def _assert_retired_runtime_surfaces_absent(root: Path) -> None:
    assert not (root / ".cursor").exists()
    assert not (root / ".agents/agents").exists()
    assert not (root / ".agents/workflows").exists()
    assert list((root / "scripts").glob("agy_*.py")) == []
    assert list((root / "scripts").glob("cursor_*.py")) == []
    assert list((root / "coordination/bin").glob("agy-*")) == []
    assert list((root / "coordination/bin").glob("cursor-*")) == []


def test_supported_provider_adapters_are_exactly_codex_and_claude() -> None:
    _assert_supported_adapter_inventory(ROOT)


def test_every_supported_provider_has_its_adapter_and_advisor_catalog() -> None:
    for provider, surfaces in PROVIDERS.items():
        assert (ROOT / surfaces["adapter"]).is_file(), provider
        agents_dir = ROOT / surfaces["agents_dir"]
        assert agents_dir.is_dir(), provider
        for advisor in ADVISORS:
            candidate = agents_dir / f"{advisor}{surfaces['agent_suffix']}"
            assert candidate.is_file(), f"{provider} lacks advisor {advisor}"


def test_provider_launchers_exist_exactly_where_declared() -> None:
    declared = {
        Path(surfaces["launcher"]).name
        for surfaces in PROVIDERS.values()
        if surfaces["launcher"] is not None
    }
    discovered = {
        path.name for path in (ROOT / "coordination/bin").glob("*-seat")
    }

    assert discovered == declared


def test_retired_provider_runtime_surfaces_are_absent() -> None:
    _assert_retired_runtime_surfaces_absent(ROOT)


def test_adapter_inventory_control_rejects_a_renamed_third_side(
    tmp_path: Path,
) -> None:
    for provider in (*PROVIDERS, "renamed-side"):
        path = tmp_path / "docs/protocol" / provider / "continuation.md"
        path.parent.mkdir(parents=True)
        path.write_text("adapter\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_supported_adapter_inventory(tmp_path)


def test_runtime_absence_control_rejects_a_reintroduced_side(
    tmp_path: Path,
) -> None:
    (tmp_path / ".cursor").mkdir()

    with pytest.raises(AssertionError):
        _assert_retired_runtime_surfaces_absent(tmp_path)


def test_retired_harness_labels_cannot_grant_current_model_identity() -> None:
    assert protocol_model.MODEL_HARNESS_PREFIXES == ("codex-", "claude-code-")
    for model_id in (
        "antigravity-gemini-3.6",
        "agy-google-gemini-3.1-pro-high",
        "cursor-xai-grok-4.6",
    ):
        assert protocol_model.model_family(model_id) is None, model_id


def test_consultation_skill_names_only_supported_sides() -> None:
    text = (
        ROOT / ".agents/skills/chatgpt-pro-consultation/SKILL.md"
    ).read_text(encoding="utf-8")
    for side in ("Codex", "Claude"):
        assert side in text, f"consultation skill dropped the {side} mapping"


def test_cross_provider_mailbox_contract_is_stated_once() -> None:
    text = (ROOT / "docs/protocol/agents/orchestration.md").read_text(
        encoding="utf-8"
    )
    assert "One mailbox across provider sides" in text
    assert "provider-agnostic identities" in text
