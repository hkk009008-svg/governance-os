"""Desktop membership, model identity, and governance authority stay separate."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import codex_protocol_model as protocol_model


ROOT = Path(__file__).resolve().parents[2]


def _adapters() -> dict[str, dict]:
    codex = tomllib.loads((ROOT / ".codex/config.toml").read_text(encoding="utf-8"))[
        "mcp_servers"
    ]["pipeline-team"]
    claude = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))[
        "mcpServers"
    ]["pipeline-team"]
    agy = json.loads((ROOT / ".agents/plugins/pipeline-team/mcp_config.json").read_text(encoding="utf-8"))[
        "mcpServers"
    ]["pipeline-team"]
    return {"codex": codex, "claude": claude, "agy": agy}


def test_each_app_identity_is_fixed_by_argv_not_environment() -> None:
    for member, adapter in _adapters().items():
        assert adapter["args"] == ["team", "serve", "--member", member]
        assert adapter.get("env") in (None, {})
        assert all("${" not in argument for argument in adapter["args"])


def test_project_adapters_carry_no_role_or_effect_authority() -> None:
    for adapter in _adapters().values():
        serialized = json.dumps(adapter, sort_keys=True).casefold()
        assert "seat" not in serialized
        assert "role" not in serialized
        assert "approval" not in serialized
        assert "sandbox" not in serialized
        assert "spend" not in serialized


def test_agy_models_may_author_but_not_issue_the_accepting_review() -> None:
    assert protocol_model.model_family("gemini-3.8-flash-high") == "gemini"
    assert protocol_model.model_family("gemini-3.7-flash-high") == "gemini"
    assert protocol_model.models_are_independent(
        "gpt-5.6-luna", "gemini-3.8-flash-high"
    )
    assert not protocol_model.models_are_current_review_pair(
        "gpt-5.6-luna", "gemini-3.8-flash-high"
    )
    assert protocol_model.models_are_current_review_pair(
        "gemini-3.8-flash-high", "claude-opus-4-7"
    )


def test_formal_review_pair_remains_claude_and_gpt_only() -> None:
    assert protocol_model.CURRENT_REVIEW_FAMILIES == frozenset({"claude", "gpt"})
    assert protocol_model.models_are_current_review_pair(
        "gpt-5.6-luna", "opus[1m]"
    )
