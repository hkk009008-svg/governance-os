from __future__ import annotations

import re
from pathlib import Path


def test_retired_claude_cli_launcher_is_absent(repo_root: Path) -> None:
    """Claude Code runs as a desktop app; there is no shell launch contract.

    The retired launcher seeded `.git/index-claude-<seat>` and exported
    `GIT_INDEX_FILE` into the session. That made seat identity a property of an
    inherited environment variable, which a desktop app cannot set and any
    process can forge.

    Nothing replaced it, deliberately. Pipeline has no Claude launcher or
    governance-seat registry. Claude Desktop's host session registry and relay
    are convenience surfaces, not authority gates. Claude seat naming is convention; review identity is
    decided at publication by `scripts/compact_pair_loop.py`.
    """
    assert not (repo_root / "scripts/claude_seat_launcher.py").exists()
    assert not (repo_root / "coordination/bin/claude-seat").exists()


def test_claude_guides_never_teach_manual_index_binding(repo_root: Path) -> None:
    """The one assertion worth carrying forward from the launcher era.

    A hand-rolled `export GIT_INDEX_FILE=...` recipe silently rebinds every
    later Git command in the session, including commits, and it follows `cd`
    into unrelated repositories. No Claude guide may reintroduce it.
    """
    # coordination/README.md is named explicitly because it is where the recipe
    # actually survived: it taught all four seats to export a per-seat index
    # long after the mechanism was retired. Named files are asserted present
    # rather than skipped, so a rename drops the file loudly instead of
    # silently dropping its coverage.
    named = [repo_root / "CLAUDE.md", repo_root / "coordination/README.md"]
    for path in named:
        assert path.exists(), f"expected guide to exist: {path.relative_to(repo_root)}"

    guides = [
        *named,
        *sorted((repo_root / "docs/protocol/claude").rglob("*.md")),
        *sorted((repo_root / ".claude/skills").rglob("*.md")),
    ]

    for guide in guides:
        text = guide.read_text(encoding="utf-8")
        relative = guide.relative_to(repo_root)
        assert "export GIT_INDEX_FILE=" not in text, relative
        assert "index-claude-" not in text, relative


_CONTINUATION = re.compile(r"\\\s*\n\s*")
_LEADING_DOT_SLASH = re.compile(r"(?<![\w.$/-])\./")


def _normalized_recipe_text(text: str) -> str:
    """Normalize only the observed equivalent spellings, not shell syntax."""
    text = _CONTINUATION.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return _LEADING_DOT_SLASH.sub("", text)


# Repo-relative program tokens a Claude guide can hand a session to run.
# `.venv/bin/*` is listed because it is the interpreter that is NOT there: a
# linked worktree carries no .venv, so a guide naming it hands the reader a
# command that exits 127. Omitting it is what let the evasion through.
_RUNNABLE = re.compile(
    r"(?<![\w./-])(?:"
    r"\.venv/bin/[\w.-]+"
    r"|coordination/bin/[\w.-]+"
    r"|scripts/[\w.-]+\.py"
    r")"
)

# Every active Claude-owned instruction surface, enumerated by walking rather
# than by hand. The first version of this pin listed three files literally and
# a gpt-5 operator review failed it: `.claude/skills/` was outside the list, so
# `.claude/skills/four-seat-protocol/SKILL.md` kept a `.venv/bin/python`
# orientation command that exits 127 in a linked worktree while this test
# stayed green. A hand-maintained allowlist decides coverage by what its author
# remembered; a walk decides it by what is actually on disk, so a new guide
# file is covered the day it lands instead of the day someone updates a tuple.
_CLAUDE_GUIDE_ROOTS = (".claude/agents", ".claude/skills", "docs/protocol/claude")
_CLAUDE_GUIDE_FILES = ("CLAUDE.md",)


def _claude_guides(repo_root: Path) -> list[Path]:
    guides = [repo_root / name for name in _CLAUDE_GUIDE_FILES]
    for root in _CLAUDE_GUIDE_ROOTS:
        base = repo_root / root
        assert base.is_dir(), root
        guides.extend(sorted(base.rglob("*.md")))
    for guide in guides:
        assert guide.exists(), guide
    return guides


def test_claude_guides_only_name_programs_that_exist_on_this_branch(
    repo_root: Path,
) -> None:
    """A runnable command in a live guide must be runnable from this checkout.

    Every other pin in this module bans a recipe that used to work. This one
    bans two recipes that do not work here.

    The first is a command that does not work *yet*: during the 2026-08-14
    two-provider alignment the Claude adapter was asked to route its snapshot
    through `coordination/bin/pipeline-python` while that wrapper existed only
    on another branch, which would have told every session here to run a
    missing file.

    The second is a command that never worked in a linked worktree and looked
    fine because it works in the primary checkout: `.venv/bin/python`. Worktrees
    carry no `.venv`. This is the exact evasion a gpt-5 operator review found
    against the first version of this pin — the guard was intact and green, and
    the broken instruction sat in a live authority surface anyway, because the
    pin's file list and its token grammar both stopped short.

    Both failures are the same defect: a live guide naming a program the reader
    cannot run. So the rule is about resolvability, not about any one spelling,
    and it is enforced over every Claude-owned guide rather than a chosen few.
    Scanning whole files rather than fenced blocks is deliberate — these
    documents give commands in prose as often as in fences, and the reader who
    copied one does not care which it was.
    """
    missing: list[str] = []
    for guide in _claude_guides(repo_root):
        relative = guide.relative_to(repo_root).as_posix()
        text = _normalized_recipe_text(guide.read_text("utf-8"))
        for token in sorted(set(_RUNNABLE.findall(text))):
            if not (repo_root / token).exists():
                missing.append(f"{relative} names {token}")

    assert missing == [], (
        "Claude guides name programs that do not exist on this branch; a "
        "session copying these runs nothing:\n  " + "\n  ".join(missing)
    )


# `env` wrapping the interpreter directly. Claude's Bash tool refuses `env` as
# soon as a dash-prefixed token follows the variable list, because it cannot
# verify what `env` wraps, so this exact prefix stops working the moment the
# wrapped command grows an option.
_ENV_WRAPPED_INTERPRETER = "env -u GIT_INDEX_FILE coordination/bin/pipeline-python"


def test_claude_guides_do_not_wrap_the_interpreter_in_env(repo_root: Path) -> None:
    """Ban the prefix outright rather than only where it currently breaks.

    Observed on 2026-08-14 against the Claude Bash tool in a linked worktree:

        env -u GIT_INDEX_FILE coordination/bin/pipeline-python \\
            scripts/status.py snapshot director      -> runs
        env -u GIT_INDEX_FILE coordination/bin/pipeline-python \\
            scripts/target_binding.py --target ...   -> refused
        unset GIT_INDEX_FILE; coordination/bin/pipeline-python \\
            scripts/target_binding.py --target ...   -> runs

    So the prefix is not broken, it is *conditionally* broken — it works until
    the wrapped command takes an option. A conditional rule is the wrong shape
    for a guide: the condition changes when someone adds a flag to a command
    that has always been fine, and nothing connects that edit to this one. The
    author of the flag will not be reading this file.

    Ordinary Git keeps its `env -u GIT_INDEX_FILE` prefix, which is verified to
    run; the ban is narrow, covering only `env` wrapped directly around the
    interpreter. Guides use a preceding `unset GIT_INDEX_FILE` line instead,
    which gives the same isolation unconditionally.
    """
    offenders = [
        guide.relative_to(repo_root).as_posix()
        for guide in _claude_guides(repo_root)
        if _ENV_WRAPPED_INTERPRETER
        in _normalized_recipe_text(guide.read_text("utf-8"))
    ]

    assert offenders == [], (
        "Claude guides wrap the interpreter in `env`, which the Bash tool "
        "refuses once the command takes options; precede the command with an "
        "`unset GIT_INDEX_FILE` line instead:\n  " + "\n  ".join(offenders)
    )


# `git -C` aimed at a shell variable. The quoted expansion is what makes this a
# discriminator: it only appears in a command someone means to run, never in
# prose explaining why the form is avoided — and that prose has to keep naming
# `git -C` and `TARGET_ROOT` to be worth reading.
_CROSS_REPO_GIT = 'git -C "$'


def test_claude_guides_do_not_route_git_at_another_repo_by_variable(
    repo_root: Path,
) -> None:
    """Evidence a guide asks for must be collectable by the task it asks.

    The ledger bridge told an isolated handoff author to paste output from
    `env -u GIT_INDEX_FILE git -C "$TARGET_ROOT" log -1 --oneline` in the same
    document that had just explained `git -C` at another repository is refused
    from an isolated worktree. Both halves were individually true and the
    document as a whole asked for something impossible, which is the failure
    mode a per-line review does not catch.

    The fix is structural rather than syntactic: each side's evidence is
    collected in the task rooted at that side, so neither needs `-C` nor a
    captured path. This pin keeps the executable shape from returning while
    leaving the prose free to name it — a rule that forbade the words would
    force the guide to stop explaining itself, which costs more than it saves.
    """
    offenders = [
        guide.relative_to(repo_root).as_posix()
        for guide in _claude_guides(repo_root)
        if _CROSS_REPO_GIT in _normalized_recipe_text(guide.read_text("utf-8"))
    ]

    assert offenders == [], (
        "Claude guides run git at another repository through a variable; an "
        "isolated session cannot, so collect each side's evidence in the task "
        "rooted at that side:\n  " + "\n  ".join(offenders)
    )


_STALE_PYTEST_ENV_GUIDANCE = (
    "Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest",
    "Use `env -u GIT_INDEX_FILE` for ordinary Git/pytest",
    "Prefix every ordinary cross-repo git and pytest command with "
    "`env -u GIT_INDEX_FILE`",
)


def _contains_stale_pytest_env_guidance(text: str) -> bool:
    normalized = _normalized_recipe_text(text)
    return any(recipe in normalized for recipe in _STALE_PYTEST_ENV_GUIDANCE)


def test_claude_guides_do_not_apply_env_prefix_to_pytest(repo_root: Path) -> None:
    """Pin the three observed stale wordings; this is not a shell parser."""
    offenders = [
        guide.relative_to(repo_root).as_posix()
        for guide in _claude_guides(repo_root)
        if _contains_stale_pytest_env_guidance(guide.read_text("utf-8"))
    ]

    assert offenders == [], "stale Claude pytest guidance: " + ", ".join(offenders)


def test_recipe_normalization_covers_observed_evasions() -> None:
    assert ".venv/bin/python" in _normalized_recipe_text("./.venv/bin/python")
    assert _ENV_WRAPPED_INTERPRETER in _normalized_recipe_text(
        "env -u GIT_INDEX_FILE \\\n          coordination/bin/pipeline-python"
    )
    assert _CROSS_REPO_GIT in _normalized_recipe_text(
        'git -C \\\n          "$TARGET_ROOT" status --short'
    )
    for recipe in _STALE_PYTEST_ENV_GUIDANCE:
        assert _contains_stale_pytest_env_guidance(recipe)
