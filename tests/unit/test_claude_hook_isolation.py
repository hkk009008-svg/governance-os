from __future__ import annotations

import json
from pathlib import Path


def test_claude_has_no_repo_mutating_lifecycle_hooks(repo_root: Path) -> None:
    """Claude uses native worktree state and explicit verification commands.

    The retired PreToolUse guard bound mutation to an environment variable a
    desktop app cannot set and any process can forge, and it never validated
    review identity — so it was not part of the acceptance gate it appeared to
    protect. Repository lifecycle hooks must not gate mutation, mutate Git
    indexes, presence, cursors, or generated state, and session start must not
    run the full smoke suite.
    """
    settings_path = repo_root / ".claude/settings.json"
    if not settings_path.exists():
        return

    settings = json.loads(settings_path.read_text(encoding="utf-8"))

    assert "hooks" not in settings


def test_retired_claude_hook_scripts_are_absent(repo_root: Path) -> None:
    hook_dir = repo_root / ".claude/hooks"

    assert not (hook_dir / "guard-git-index.sh").exists()
    assert not (hook_dir / "session-smoke.sh").exists()
    assert not (hook_dir / "update-state.sh").exists()
