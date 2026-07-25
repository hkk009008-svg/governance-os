from __future__ import annotations

from pathlib import Path


def test_claude_does_not_embed_a_cursor_compatibility_guard(repo_root: Path) -> None:
    """Claude must not re-host Cursor's hook policy inside its own guard.

    The retired `.claude/hooks/guard-git-index.sh` evaluated Cursor's policy and
    then exited 0 unconditionally — printing a `deny` decision while returning
    the exit status Claude Code reads as *allow*. Cursor's guard is fail-open
    advisory over its own host; Claude's was fail-closed authorization. Copying
    one provider's disposition into another provider's contract is what turned a
    denial into an approval.

    Each host now enforces its own boundary in its own runtime. This test keeps
    the cross-host alias from reappearing.
    """
    assert not (repo_root / ".claude/hooks/guard-git-index.sh").exists()

    for relative in (".cursor/hooks/seat-policy", "scripts/cursor_hook_policy.py"):
        source = repo_root / relative
        if not source.exists():
            continue
        assert "CLAUDE_SEAT" not in source.read_text(encoding="utf-8")
