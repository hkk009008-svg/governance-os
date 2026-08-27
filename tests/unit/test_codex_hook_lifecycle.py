"""Codex uses one project MCP adapter and no repository lifecycle hooks."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest


def _assert_codex_hook_surface_absent(root: Path) -> None:
    assert not (root / ".codex/hooks.json").exists()
    assert not (root / ".codex/hooks").exists()


def test_codex_has_one_fixed_project_team_adapter(repo_root: Path) -> None:
    config = tomllib.loads(
        (repo_root / ".codex/config.toml").read_text(encoding="utf-8")
    )
    servers = config["mcp_servers"]
    assert set(servers) == {"pipeline-team"}
    assert servers["pipeline-team"] == {
        "command": "./bin/pipeline",
        "args": ["team", "serve", "--member", "codex"],
    }


def test_codex_has_no_repo_mutating_lifecycle_hooks(repo_root: Path) -> None:
    _assert_codex_hook_surface_absent(repo_root)


def test_no_hooks_control_rejects_an_arbitrary_hook_surface(tmp_path: Path) -> None:
    hook_dir = tmp_path / ".codex/hooks"
    hook_dir.mkdir(parents=True)
    (hook_dir / "evil.sh").write_text("#!/bin/sh\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        _assert_codex_hook_surface_absent(tmp_path)
