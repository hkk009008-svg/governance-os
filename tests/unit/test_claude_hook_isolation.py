"""Claude uses one approved project MCP adapter and no repository hooks."""

from __future__ import annotations

import json
from pathlib import Path


def test_claude_settings_keep_security_and_approve_only_team(repo_root: Path) -> None:
    settings = json.loads(
        (repo_root / ".claude/settings.json").read_text(encoding="utf-8")
    )

    assert "hooks" not in settings
    assert set(settings) == {"$comment", "enabledMcpjsonServers"}
    assert settings["enabledMcpjsonServers"] == ["pipeline-team"]
    assert settings.get("enableAllProjectMcpServers") is not True


def test_claude_project_adapter_fixes_member_identity(repo_root: Path) -> None:
    payload = json.loads((repo_root / ".mcp.json").read_text(encoding="utf-8"))
    assert set(payload["mcpServers"]) == {"pipeline-team"}
    assert payload["mcpServers"]["pipeline-team"] == {
        "type": "stdio",
        "command": "${CLAUDE_PROJECT_DIR:-.}/bin/pipeline",
        "args": ["team", "serve", "--member", "claude"],
    }


def test_claude_has_no_repo_mutating_lifecycle_hooks(repo_root: Path) -> None:
    assert not (repo_root / ".claude/hooks").exists()
