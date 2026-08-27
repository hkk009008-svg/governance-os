"""Executable inventory for the three desktop-app adapters."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

import codex_protocol_model as protocol_model


ROOT = Path(__file__).resolve().parents[2]
APP_CONFIGS = {
    "codex": (".codex/config.toml", "mcp_servers"),
    "claude": (".mcp.json", "mcpServers"),
    "agy": (".agents/plugins/pipeline-team/mcp_config.json", "mcpServers"),
}
FORBIDDEN_RUNTIME_GLOBS = (
    ".cursor*",
    "pipeline/cursor*.py",
    "coordination/bin/cursor*",
    "pipeline/peer.py",
    "pipeline/peer_backends.py",
    "pipeline/peer_receipt.py",
    "pipeline/*seat*launcher*.py",
    "scripts/*seat*launcher*.py",
    "scripts/claude_task_connector.py",
    "coordination/bin/*-seat",
)
ACTIVE_CLAIM_SURFACES = (
    "pipeline/claim_check.py",
    "coordination/bin/probe-claim",
    ".agents/skills/probe-a-claim/SKILL.md",
    ".claude/skills/probe-a-claim/SKILL.md",
    ".agents/skills/writing-skills/SKILL.md",
    ".claude/agents/amnesiac-prober.md",
    ".codex/agents/amnesiac-prober.toml",
    "docs/protocol/work-modes.md",
)
HEADLESS_PROVIDER_COMMANDS = (
    "codex exec",
    "probe --execute",
    "claim probe --execute",
)


def _load_adapter(root: Path, member: str) -> tuple[dict, dict]:
    relative, table_name = APP_CONFIGS[member]
    text = (root / relative).read_text(encoding="utf-8")
    payload = tomllib.loads(text) if member == "codex" else json.loads(text)
    table = payload[table_name]
    assert set(table) == {"pipeline-team"}, (member, sorted(table))
    return payload, table["pipeline-team"]


def _assert_supported_adapter_inventory(root: Path) -> None:
    for member in APP_CONFIGS:
        _payload, adapter = _load_adapter(root, member)
        assert adapter["args"] == ["team", "serve", "--member", member]
        assert adapter.get("type", "stdio") == "stdio"
        assert adapter.get("cwd", ".") == "."
        assert adapter.get("env") in (None, {})
        assert set(adapter) <= {"type", "command", "args", "cwd", "env"}
        command = adapter["command"].replace("${CLAUDE_PROJECT_DIR:-.}", ".")
        assert command == "./bin/pipeline"


def _assert_forbidden_runtime_surfaces_absent(root: Path) -> None:
    for pattern in FORBIDDEN_RUNTIME_GLOBS:
        matches = sorted(root.glob(pattern))
        assert matches == [], f"forbidden runtime surface matched {pattern}: {matches}"


def _assert_claim_surfaces_do_not_launch_providers(root: Path) -> None:
    for relative in ACTIVE_CLAIM_SURFACES:
        candidate = root / relative
        if not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8").casefold()
        for command in HEADLESS_PROVIDER_COMMANDS:
            assert command not in text, f"{relative} contains {command!r}"


def test_exactly_three_fixed_project_app_adapters_are_configured() -> None:
    _assert_supported_adapter_inventory(ROOT)


def test_claude_approves_only_the_named_project_team_server() -> None:
    settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    assert settings["enabledMcpjsonServers"] == ["pipeline-team"]
    assert settings.get("enableAllProjectMcpServers") is not True


def test_cursor_and_headless_provider_launch_surfaces_are_absent() -> None:
    _assert_forbidden_runtime_surfaces_absent(ROOT)
    _assert_claim_surfaces_do_not_launch_providers(ROOT)


def test_ci_shellcheck_targets_only_live_shell_entrypoints() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for retired in (
        "coordination/bin/consume-events",
        "coordination/bin/claim-lock",
        "coordination/bin/release-lock",
    ):
        assert retired not in workflow
    for active in ("coordination/bin/send-event", "bin/pipeline"):
        assert active in workflow
        assert (ROOT / active).is_file()


def test_adapter_inventory_control_rejects_spoofable_member_identity(
    tmp_path: Path,
) -> None:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".agents/plugins/pipeline-team").mkdir(parents=True)
    (tmp_path / ".codex/config.toml").write_text(
        '[mcp_servers.pipeline-team]\ncommand = "./bin/pipeline"\n'
        'args = ["team", "serve", "--member", "claude"]\n',
        encoding="utf-8",
    )
    (tmp_path / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"pipeline-team": {
            "command": "${CLAUDE_PROJECT_DIR:-.}/bin/pipeline",
            "args": ["team", "serve", "--member", "claude"],
        }}}),
        encoding="utf-8",
    )
    (tmp_path / ".agents/plugins/pipeline-team/mcp_config.json").write_text(
        json.dumps({"mcpServers": {"pipeline-team": {
            "command": "./bin/pipeline",
            "args": ["team", "serve", "--member", "agy"],
            "cwd": ".",
        }}}),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError):
        _assert_supported_adapter_inventory(tmp_path)


@pytest.mark.parametrize(
    "relative_path",
    (
        ".cursor2/settings.json",
        "pipeline/cursorseat.py",
        "coordination/bin/cursor-seat",
        "coordination/bin/codex-seat",
        "pipeline/codex_seat_launcher.py",
        "scripts/claude_task_connector.py",
        "pipeline/peer.py",
    ),
)
def test_runtime_absence_control_rejects_reintroduced_launch_surfaces(
    tmp_path: Path,
    relative_path: str,
) -> None:
    candidate = tmp_path / relative_path
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text("forbidden provider runtime\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_forbidden_runtime_surfaces_absent(tmp_path)


def test_claim_surface_control_rejects_a_reintroduced_provider_command(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "pipeline/claim_check.py"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("codex exec -\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_claim_surfaces_do_not_launch_providers(tmp_path)


def test_app_membership_does_not_widen_formal_model_review() -> None:
    assert protocol_model.CURRENT_REVIEW_FAMILIES == frozenset({"claude", "gpt"})
    assert protocol_model.model_family("Gemini 3.7 Flash (High)") == "gemini"
    assert not protocol_model.models_are_current_review_pair(
        "gpt-5.6-luna", "Gemini 3.7 Flash (High)"
    )
    assert protocol_model.model_family("cursor-xai-grok-4.6") is None
