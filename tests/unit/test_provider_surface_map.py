"""Drift pin for the per-provider surface map (audit P1, bounded form).

One executable statement of which host surfaces each provider side owns, so a
capability change that forgets a side fails here instead of drifting silently.
The expectations mirror the ARCHITECTURE.md provider-surfaces table; this test
is the alarm, not a second runtime map.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# The read-only advisor catalog every side carries in its host-native format.
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
        "lifecycle_hook": None,
    },
    "cursor": {
        "adapter": "docs/protocol/cursor/continuation.md",
        "agents_dir": ".cursor/agents",
        "agent_suffix": ".md",
        "launcher": "coordination/bin/cursor-seat",
        "lifecycle_hook": ".cursor/hooks/seat-policy",
    },
    "claude": {
        "adapter": "docs/protocol/claude/continuation.md",
        "agents_dir": ".claude/agents",
        "agent_suffix": ".md",
        "launcher": None,
        "lifecycle_hook": None,
    },
    "agy": {
        "adapter": "docs/protocol/agy/continuation.md",
        "agents_dir": ".agy/agents",
        "agent_suffix": ".toml",
        "launcher": "coordination/bin/agy-seat",
        "lifecycle_hook": None,
    },
}


def test_every_side_has_its_adapter_and_advisor_catalog() -> None:
    for provider, surfaces in PROVIDERS.items():
        assert (ROOT / surfaces["adapter"]).is_file(), provider
        agents_dir = ROOT / surfaces["agents_dir"]
        assert agents_dir.is_dir(), provider
        for advisor in ADVISORS:
            candidate = agents_dir / f"{advisor}{surfaces['agent_suffix']}"
            assert candidate.is_file(), f"{provider} lacks advisor {advisor}"


def test_launchers_exist_exactly_where_declared() -> None:
    for provider, surfaces in PROVIDERS.items():
        launcher = surfaces["launcher"]
        if launcher is None:
            assert not (
                ROOT / "coordination" / "bin" / f"{provider}-seat"
            ).exists(), f"{provider} declares no launcher but one exists"
        else:
            assert (ROOT / launcher).is_file(), provider


def test_lifecycle_hooks_exist_only_on_cursor() -> None:
    for provider, surfaces in PROVIDERS.items():
        hook = surfaces["lifecycle_hook"]
        if hook is not None:
            assert (ROOT / hook).is_file(), provider
        prefix = f".{provider}"
        assert not (ROOT / prefix / "hooks.json").exists() or provider == "cursor", (
            f"{provider} grew a hooks.json the surface map does not declare"
        )


def test_consultation_skill_names_every_side() -> None:
    text = (
        ROOT / ".agents/skills/chatgpt-pro-consultation/SKILL.md"
    ).read_text(encoding="utf-8")
    for side in ("Codex", "Claude", "Cursor", "AGY"):
        assert side in text, f"consultation skill dropped the {side} mapping"


def test_cross_provider_mailbox_contract_is_stated_once() -> None:
    text = (ROOT / "docs/protocol/agents/orchestration.md").read_text(
        encoding="utf-8"
    )
    assert "One mailbox across provider sides" in text
    assert "provider-agnostic identities" in text
