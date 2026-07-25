from __future__ import annotations

from pathlib import Path


def test_codex_has_no_repo_mutating_lifecycle_hooks(repo_root: Path) -> None:
    """Codex uses native worktree state and explicit verification commands.

    Repository lifecycle hooks must not mutate Git indexes, presence, cursors,
    or generated state, and session start must not run the full smoke suite.
    """

    assert not (repo_root / ".codex/hooks.json").exists()


def test_retired_codex_hook_scripts_are_absent(repo_root: Path) -> None:
    hook_dir = repo_root / ".codex/hooks"

    assert not (hook_dir / "guard-git-index.sh").exists()
    assert not (hook_dir / "session-smoke.sh").exists()
    assert not (hook_dir / "update-state.sh").exists()
