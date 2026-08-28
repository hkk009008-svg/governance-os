"""Checked-in desktop-app adapters all launch the same bounded team server."""
from __future__ import annotations

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _configs() -> dict[str, dict]:
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


def test_all_three_apps_have_project_scoped_mcp_adapters() -> None:
    configs = _configs()
    assert set(configs) == {"codex", "claude", "agy"}

    for member, config in configs.items():
        assert config["args"] == ["team", "serve", "--member", member]
        assert Path(config["command"].replace("${CLAUDE_PROJECT_DIR:-.}", ".")).is_absolute() is False
        assert set(config) <= {"type", "command", "args", "cwd", "env"}


def test_no_app_adapter_contains_absolute_machine_specific_paths() -> None:
    texts = [
        (ROOT / ".codex/config.toml").read_text(encoding="utf-8"),
        (ROOT / ".mcp.json").read_text(encoding="utf-8"),
        (ROOT / ".agents/plugins/pipeline-team/mcp_config.json").read_text(encoding="utf-8"),
    ]
    assert all("/Users/" not in text and "/Volumes/" not in text for text in texts)
