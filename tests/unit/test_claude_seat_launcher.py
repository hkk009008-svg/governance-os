from __future__ import annotations

from pathlib import Path


def test_retired_claude_cli_launcher_is_absent(repo_root: Path) -> None:
    """Claude Code runs as a desktop app; there is no shell launch contract.

    The retired launcher seeded `.git/index-claude-<seat>` and exported
    `GIT_INDEX_FILE` into the session. That made seat identity a property of an
    inherited environment variable, which a desktop app cannot set and any
    process can forge.

    Nothing replaced it, deliberately. Claude has no launcher and no session
    registry — unlike Cursor, whose registry exists to gate in-app effects.
    Claude seat naming is convention; review identity is decided at publication
    by `scripts/compact_pair_loop.py`.
    """
    assert not (repo_root / "scripts/claude_seat_launcher.py").exists()
    assert not (repo_root / "coordination/bin/claude-seat").exists()


def test_claude_guides_never_teach_manual_index_binding(repo_root: Path) -> None:
    """The one assertion worth carrying forward from the launcher era.

    A hand-rolled `export GIT_INDEX_FILE=...` recipe silently rebinds every
    later Git command in the session, including commits, and it follows `cd`
    into unrelated repositories. No Claude guide may reintroduce it.
    """
    guides = [
        repo_root / "CLAUDE.md",
        *sorted((repo_root / "docs/protocol/claude").glob("*.md")),
        *sorted((repo_root / ".claude/skills").glob("*/SKILL.md")),
    ]

    for guide in guides:
        if not guide.exists():
            continue
        text = guide.read_text(encoding="utf-8")
        relative = guide.relative_to(repo_root)
        assert "export GIT_INDEX_FILE=" not in text, relative
        assert "index-claude-" not in text, relative
