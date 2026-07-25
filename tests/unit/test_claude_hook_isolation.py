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


def test_live_guides_do_not_present_the_retired_state_hook_as_live(
    repo_root: Path,
) -> None:
    """Asserting the script is absent was never enough on its own.

    Both files below went on describing the retired hook in the present tense —
    as the thing regenerating STATE.md, stamping presence freshness every tool
    call, and fast-forwarding a per-seat Git index — long after
    `test_retired_claude_hook_scripts_are_absent` started asserting it was
    gone. A seat reading those sections would assume freshness and index
    maintenance it does not get.

    Scoped to live instruction surfaces. Historical records under
    `docs/superpowers/` and `docs/HANDOFF-*` legitimately still name the hook,
    so a repository-wide needle would be wrong here.
    """
    for relative in (
        "coordination/README.md",
        "docs/protocol/agents/director-operator.md",
    ):
        guide = repo_root / relative
        assert guide.exists(), relative
        text = guide.read_text(encoding="utf-8")
        assert "update-state.sh" not in text, relative
        # Banning the script name alone was not enough. The first attempt left
        # the expanded rule body still telling readers to consult STATE.md and
        # calling it a "hook-derived snapshot" — active instructions toward a
        # file that is never generated — while the same document declared it
        # retired a few hundred lines away. Ban the artifact and the phrase.
        assert "hook-derived" not in text, relative

    # STATE.md is banned outright in the rule body: a live instruction surface
    # must not name a file nothing generates, in any tense. coordination/README
    # is exempt because it owns the one section that documents the retirement,
    # which is the single place the name still earns its keep. Historical
    # records under docs/superpowers/, docs/HANDOFF-*, and
    # docs/PROTOCOL-RULES-LOG.md keep their provenance untouched.
    rule_body = repo_root / "docs/protocol/agents/director-operator.md"
    assert "STATE.md" not in rule_body.read_text(encoding="utf-8"), (
        "docs/protocol/agents/director-operator.md names STATE.md"
    )
