from __future__ import annotations

import itertools
import os
import re
import shutil
import string
import subprocess
import tempfile
import tomllib
from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager, suppress
from pathlib import Path

import pytest

import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]

CODEX_ENTRY_SURFACES = (
    "AGENTS.md",
    "docs/protocol/codex/continuation.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
)
NUMBERED_AGENT_FILES = tuple(
    f".codex/agents/agent{number:02}.toml" for number in range(1, 5)
)
CORE_CODEX_AGENTS = {
    "amnesiac-prober",
    "lane-v-verifier",
    "money-gate-reviewer",
    "protocol-coordinator",
    "protocol-director",
    "protocol-operator",
    "readiness-bridge",
}
ACTIVE_INSTRUCTION_ROOTS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/skills",
    ".claude/agents",
    ".claude/skills",
    ".codex/agents",
    "docs/protocol/agents",
    "docs/protocol/claude",
    "docs/protocol/codex",
)
ACTIVE_PROTOCOL_ROOTS = (
    "docs/PROGRAM-MANUAL.md",
    ".agents",
    ".claude",
    ".codex",
    "docs/protocol",
    "scripts",
)
MANDATORY_SUPERPOWERS_RE = re.compile(
    r"\bsuperpowers:[a-z0-9][a-z0-9-]*\b",
    re.IGNORECASE,
)
EXACT_NEXT_TRIGGER = "Exact Next Trigger"
# There is deliberately no hardcoded prune list here. Directory walks see the
# filesystem while git's ignore rules live in the index and exclude files, and
# the obvious bridge — naming the paths a walk should skip — is a claim about
# pathnames that knows nothing about their content. A tracked protocol surface
# under such a name is skipped in silence, and every attempt to guard that
# hardcoded claim only moved the same gap one layer down: first to whether git
# reported the path ignored, then to whether a tracked listing arrived whole,
# then to whether that listing was truncated at a record boundary, then to
# whether a NUL could be inserted mid-record to forge one. A parsed stream was
# never going to settle it. The listing now only proposes candidates, and each
# is confirmed against git by exit code at walk time; see `_sweep_active_files`
# and `_git_confirms_prunable`.


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _git_listing(*arguments: str) -> tuple[str, ...]:
    """Entries from one NUL-framed `git ls-files` call; empty if unavailable.

    Every caller uses this to *add* prunes, so a short answer is safe and only
    a wrong entry is dangerous. That is why nothing here reports whether the
    listing was complete: an entry that never arrived prunes nothing, while an
    entry that arrived corrupt could prune a directory git never named.

    `-z` is what makes a corrupt entry detectable. Git terminates every path
    with NUL, so a non-empty payload not ending in one was cut mid-record, and
    its tail is a fragment — and a fragment is precisely the dangerous shape,
    because truncating `.claude/worktrees-backup/` yields `.claude/worktrees`,
    a real directory git never reported. Such a payload is discarded whole.
    Framing also stops a path containing a newline from forging entries.

    `GIT_INDEX_FILE` is scrubbed because this repo exports a per-seat index —
    inheriting it would make tracked files read as untracked.
    """
    environment = {
        name: value for name, value in os.environ.items() if name != "GIT_INDEX_FILE"
    }
    try:
        payload = subprocess.run(
            ("git", "ls-files", "-z", *arguments),
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return ()
    if payload and not payload.endswith(b"\0"):
        return ()
    try:
        listing = payload.decode("utf-8")
    except UnicodeDecodeError:
        return ()
    return tuple(entry for entry in listing.split("\0") if entry)


def _git_ignored_entries() -> tuple[frozenset[str], frozenset[str]]:
    """Ignored paths git named, split into (whole directories, single files).

    `--directory` collapses a directory to one `dir/` entry only when
    everything inside it is untracked; a directory holding even one tracked
    file is never collapsed, and git lists its untracked members individually
    instead. A trailing slash is therefore git's own statement that nothing
    tracked lives beneath that path — exactly the fact a prune needs, and the
    one a hardcoded list can never supply.

    The two are kept apart because they license different things. A collapsed
    directory may be *proposed* for pruning. A named file may be skipped, but
    says nothing about any tree, so it must never stop a walk descending.

    Nothing here decides a prune. A listing is a stream, and a stream can be
    corrupted into naming a path git never reported: one NUL inserted into
    `.claude/worktrees-backup/` yields `.claude/worktrees/`, and no parser can
    tell the two apart. Candidates are therefore confirmed against git again,
    by exit code, in `_git_confirms_prunable`.
    """
    entries = _git_listing(
        "--others", "--ignored", "--directory", "--exclude-standard"
    )
    directories = frozenset(
        entry.rstrip("/") for entry in entries if entry.endswith("/")
    )
    files = frozenset(entry for entry in entries if not entry.endswith("/"))
    return directories, files


NO_PATHSPEC_MATCH = 1
# Pathspec magic is introduced by a leading colon and by nothing else — the
# long form `:(top)`, and the short forms `:!`, `:^`, `:/`. A candidate
# carrying one would be answered as a pattern rooted somewhere else rather than
# as the directory literally bearing that name, so a forged `:(top)foo` could
# win a confirmation about a path git never examined. `--` ends option parsing
# and leaves magic alive. `--literal-pathspecs` disables it, but `git
# check-ignore` rejects that flag outright, so the flag cannot be the defence
# on both calls and refusing the colon is. Since every magic form starts here,
# that refusal is complete, and the flag would be unreachable belt-and-braces
# no test could keep honest.
PATHSPEC_MAGIC_PREFIX = ":"


def _git_exit_code(*arguments: str) -> int:
    """Exit status of one git call; -1 when git cannot be run at all."""
    environment = {
        name: value for name, value in os.environ.items() if name != "GIT_INDEX_FILE"
    }
    try:
        return subprocess.run(
            ("git", *arguments),
            cwd=ROOT,
            env=environment,
            capture_output=True,
        ).returncode
    except (OSError, subprocess.SubprocessError):
        return -1


def _git_ignore_record(
    relative: str, root: Path = ROOT
) -> tuple[str, str, str] | None:
    """The `(source, line, pattern)` git reports for *relative*; None if none.

    A 0 exit says the path is ignored. It does not say the repository is what
    ignores it. `$GIT_DIR/info/exclude` is untracked, lives in the common git
    dir every worktree shares, and on at least one machine here carries
    `.claude/worktrees/` a second time, so a control resting on the exit code
    alone keeps passing after the committed rule is deleted — machine state
    answering in the repository's name, which is the same class of defect as
    reading one checkout's layout as a fact about the repository.

    Framed with NUL rather than split on a delimiter that can occur inside the
    data. `-v` prints `<source>:<line>:<pattern>\\t<pathname>`, and a source may
    contain a colon: `core.excludesFile=.gitignore:shadow` is answered as
    `.gitignore:shadow:1:…`, whose first field up to a colon is `.gitignore`.
    Splitting there reports an untracked file under a tracked file's name,
    which is a forged provenance rather than a wrong one. `-z` removes the
    ambiguity and requires `--stdin`, so the path is fed that way. The echoed
    pathname is checked against the question, because a reply about another
    path is not an answer to this one.
    """
    environment = {
        name: value for name, value in os.environ.items() if name != "GIT_INDEX_FILE"
    }
    try:
        completed = subprocess.run(
            ("git", "check-ignore", "-v", "-z", "--stdin"),
            cwd=root,
            env=environment,
            input=f"{relative}\0".encode(),
            capture_output=True,
        )
    except (OSError, subprocess.SubprocessError, UnicodeEncodeError):
        return None
    if completed.returncode != 0:
        return None
    fields = completed.stdout.split(b"\0")
    # `<source>\0<line>\0<pattern>\0<pathname>\0`, so a complete record leaves
    # at least four fields plus the empty tail of the final terminator.
    if len(fields) < 5 or fields[3] != relative.encode():
        return None
    try:
        return (
            fields[0].decode("utf-8"),
            fields[1].decode("utf-8"),
            fields[2].decode("utf-8"),
        )
    except UnicodeDecodeError:
        return None


def _git_committed_lines(path: str, root: Path = ROOT) -> list[str] | None:
    """Lines of *path* as committed at HEAD; None when it is not committed."""
    environment = {
        name: value for name, value in os.environ.items() if name != "GIT_INDEX_FILE"
    }
    try:
        completed = subprocess.run(
            ("git", "show", f"HEAD:{path}"),
            cwd=root,
            env=environment,
            capture_output=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    try:
        return completed.stdout.decode("utf-8").split("\n")
    except UnicodeDecodeError:
        return None


def _committed_pattern(line: str) -> str:
    """One committed exclude line reduced the way git reports its pattern.

    Exactly one trailing carriage return is removed, never more. Splitting a
    committed blob on newlines leaves one CR on a CRLF file and git strips one
    the same way, but a line ending `\\r\\r` is a pattern *ending in a carriage
    return* and does not match what a bare pattern matches. Stripping every
    trailing CR would let such a line authenticate a machine-local rule it does
    not correspond to, which is the masking this check exists to catch,
    reintroduced by the comparison rather than by the lookup.

    Unescaped trailing spaces are removed because git removes them before
    reporting: a committed `target/   ` is reported as `target/`, and comparing
    raw would reject a rule that is genuinely committed.

    A trailing space escaped by a backslash is kept, which matches git rather
    than merely erring against it: `one\\ ` is reported as `one\\ `, so keeping
    it is what makes such a rule compare equal and be accepted. The reduction is
    deliberately not carried further. A line mixing the two, `two\\  `, is
    reduced by git to `two\\ ` and is left here as `two\\  `, so it compares
    unequal and is refused. That is the safe direction — a loud refusal on a
    pattern shape this repository does not use, never a silent acceptance — but
    it is a refusal of something genuinely committed, so it is a limit of this
    comparison rather than a property worth relying on.
    """
    if line.endswith("\r"):
        line = line[:-1]
    without_spaces = line.rstrip(" ")
    if without_spaces.endswith("\\"):
        return line
    return without_spaces


def _git_ignore_rule_is_committed(relative: str, root: Path = ROOT) -> bool:
    """Whether the rule that ignored *relative* is committed, bytes and all.

    Trackedness of the answering file is not enough, and asserting its name is
    both too strict and too weak. Too strict because `.gitignore` and a nested
    `.claude/.gitignore` are equally committed and either may answer depending
    on precedence. Too weak because `core.excludesFile` may select a *tracked*
    path whose working copy carries the rule while the committed copy does not:
    the index then confirms a pathname while the rule that actually matched
    exists only on this machine, which is the masking this check exists to
    catch, one level in from where it was first found.

    So the whole record is used. Git reports the source, the line number and the
    pattern together, and the committed blob is read at that path and that line
    and required to be that pattern. A source outside the repository, or one
    whose committed bytes differ, has no such line and fails.
    """
    record = _git_ignore_record(relative, root)
    if record is None:
        return False
    source, line, pattern = record
    committed = _git_committed_lines(source, root)
    if committed is None:
        return False
    try:
        index = int(line) - 1
    except ValueError:
        return False
    if not 0 <= index < len(committed):
        return False
    return _committed_pattern(committed[index]) == pattern


def _git_confirms_prunable(relative: str) -> bool:
    """Whether git, asked directly about this exact path, sanctions skipping it.

    Decided on exit codes, never on parsed output, because the forgery this
    defends against is a parse: an exit code carries no path to forge. Both
    questions must agree — the tree is ignored, and no tracked file matches it.

    A candidate carrying pathspec magic is refused before either question, so
    neither is ever asked about a path other than the one being skipped.

    Each answer is required to be the specific one that means what it must,
    never merely non-zero. `--error-unmatch` exits exactly 1 when a pathspec
    matched nothing; every other non-zero exit is an error, and an error is not
    evidence that a directory is empty of tracked content. Reading any non-zero
    as "nothing tracked" turned a broken call into permission to skip.

    Asked immediately before descending into the directory, not in advance for
    a whole set of siblings, so no other confirmation runs in between. Two
    residues remain and are carried rather than claimed closed: these are two
    calls, so the tree can stop being ignored between them, which risks
    skipping untracked content in a directory that just became live; and
    anything committed between the second answer and the descent below it is
    missed. No procedure that reads repository state and then acts on it closes
    that second one.
    """
    if relative.startswith(PATHSPEC_MAGIC_PREFIX):
        return False
    if _git_exit_code("check-ignore", "-q", "--", relative) != 0:
        return False
    tracked = _git_exit_code("ls-files", "--cached", "--error-unmatch", "--", relative)
    return tracked == NO_PATHSPEC_MATCH


def _sweep_active_files(roots: Iterable[str], suffixes: Iterable[str]) -> list[Path]:
    """Files under *roots* carrying *suffixes*, skipping anything git ignores.

    A hand-written descent rather than `os.walk`, because `os.walk` requires
    the whole sibling list to be filtered before it enters the first of them.
    That made every sibling's confirmation older than the descent it governed,
    and the staleness grew with the number of siblings. Here each directory is
    confirmed and then immediately entered, so nothing runs in between.

    A directory is skipped only when the collapsed listing proposes it *and*
    git, asked again about that exact path an instant earlier, confirms it.
    Nothing is skipped on this module's own authority, nothing on a parsed
    pathname alone, and a root named in *roots* is always swept — naming it is
    the opt-in.

    Every way this can go wrong subtracts. A git that fails, is missing,
    returns nothing, or returns a listing cut at a record boundary yields fewer
    candidates; a listing corrupted into inventing one is refused at
    confirmation; a confirmation that errors leaves the tree walked. A guard
    that inspects too much fails loudly; one that inspects too little does not
    fail at all.

    Symlinked *directories* are not followed, matching the previous walk and
    keeping the descent free of cycles. A symlink to a *file* is read like any
    other file: it is a live instruction surface at a path under an active
    root, and whether its bytes live elsewhere changes nothing about that. A
    broken symlink is neither, and is skipped because it has no content to
    sweep rather than because it is a link.
    """
    wanted = frozenset(suffixes)
    candidate_directories, ignored_files = _git_ignored_entries()
    found: list[Path] = []

    def relative_of(path: Path) -> str:
        return path.relative_to(ROOT).as_posix()

    def descend(branch: Path) -> None:
        # A directory that cannot be listed is deliberately not caught. Swallowing
        # the error would drop its whole subtree with no signal, which is the
        # silent-narrowing failure this module exists to prevent; raising says
        # plainly that the sweep could not cover something.
        children = sorted(branch.iterdir())
        for child in children:
            relative = relative_of(child)
            if child.is_dir():
                # Symlinked directories are not followed, matching `os.walk`:
                # the tree behind one is reached by its real path, and following
                # it invites cycles. The test is made *inside* the directory
                # branch on purpose — a symlink to a file is a different thing
                # entirely and must still be read.
                if child.is_symlink():
                    continue
                if child.name == ".git":
                    continue
                if relative in candidate_directories and _git_confirms_prunable(
                    relative
                ):
                    continue
                descend(child)
            elif (
                child.is_file()
                and child.suffix in wanted
                and relative not in ignored_files
            ):
                found.append(child)

    for relative in roots:
        root = ROOT / relative
        if root.is_file():
            found.append(root)
        elif root.is_dir():
            descend(root)
    return found


def test_codex_entry_surfaces_reference_executable_seams_not_renderers() -> None:
    copied_host_mechanics = (
        "wait_threads",
        "read_thread(turnLimit",
        "supported scoped execution profile",
        "at most one discovery refresh",
        "Capacity Split Default:",
        "2-cycle escalation limit",
    )
    for path in CODEX_ENTRY_SURFACES:
        text = _compact(_read(path).replace("`", ""))
        assert "scripts/codex_protocol_model.py" in text
        assert "render_" not in text
        for copied_detail in copied_host_mechanics:
            assert copied_detail not in text, (path, copied_detail)


def test_codex_surface_budgets_prevent_doctrine_regrowth() -> None:
    budgets = {
        "AGENTS.md": 140,
        "docs/protocol/codex/continuation.md": 90,
        ".agents/skills/four-seat-protocol/SKILL.md": 60,
        ".codex/agents/README.md": 25,
    }
    for path, maximum in budgets.items():
        assert len(_read(path).splitlines()) <= maximum, path


def test_numbered_agent_extensions_are_removed() -> None:
    for path in NUMBERED_AGENT_FILES:
        assert not (ROOT / path).exists(), path

    readme = _read(".codex/agents/README.md")
    assert "agentNN" not in readme
    assert not re.search(r"\bagent0[1-4]\b", readme)


def test_codex_agent_catalog_contains_only_named_role_deltas() -> None:
    configs = {
        path.stem: tomllib.loads(path.read_text(encoding="utf-8"))
        for path in (ROOT / ".codex/agents").glob("*.toml")
    }
    assert set(configs) == CORE_CODEX_AGENTS
    assert {config["name"] for config in configs.values()} == CORE_CODEX_AGENTS

    readme = _read(".codex/agents/README.md")
    for name in CORE_CODEX_AGENTS:
        assert f"`{name}`" in readme
    assert "only role-specific deltas" in readme


def test_codex_owned_surfaces_use_native_worktree_git() -> None:
    for path in CODEX_ENTRY_SURFACES:
        text = _read(path)
        assert "GIT_INDEX_FILE" not in text, path
        assert "native" in text.casefold(), path

    agents = _read("AGENTS.md")
    assert "per-seat indexes" in agents
    assert "do not create or share" in agents


def test_continuation_keeps_transport_and_fixed_interface_boundaries() -> None:
    continuation = _compact(_read("docs/protocol/codex/continuation.md"))

    assert "mailbox is the configured coordination transport" in continuation
    assert "governance.toml" in continuation
    assert "explicit reviewed transport change" in continuation
    assert "fails closed" in continuation
    assert "transport ambiguity fails visibly" in continuation
    assert "coordination/bin/send-event" in continuation
    assert "coordination/bin/consume-events" in continuation
    assert "never raw event or cursor edits" in continuation
    assert "coordinator has no cursor" in continuation


def test_four_seat_skill_keeps_role_and_helper_boundaries() -> None:
    skill = _compact(_read(".agents/skills/four-seat-protocol/SKILL.md"))

    for boundary in (
        "Do not infer a live role",
        "never reviews authored work",
        "without becoming a production author or approval gate",
        "reports state without claiming work",
        "do not publish live-role events or verdicts",
        "External effects remain separately authorized",
    ):
        assert boundary.casefold() in skill.casefold(), boundary


def test_pipeline_policy_is_execution_first_and_proportional() -> None:
    agents = _compact(_read("AGENTS.md"))

    for concept in (
        "accepted exact task",
        "failing behavior test",
        "root cause",
        "smallest-sufficient verification",
        "strict xfail pin",
        "Delegation is optional and owner-chosen",
        "ordinary reversible local work",
        "material behavior changes",
        "different-model actual-diff review",
        "abuse-class analysis",
        "non-author review",
        "separate exact authority",
    ):
        assert concept.casefold() in agents.casefold(), concept

    assert "skill presence alone is not a trigger" in agents
    assert "task-count or line-count mandate" not in agents


def test_checkpoint_contract_is_pinned_across_provider_surfaces() -> None:
    """Durable-continuation obligations must not silently vanish or fork.

    The checkpoint record is the mechanism behind AGENTS.md universal
    contract item 7; every provider adapter carries the same boundary
    trigger, draft tool, resume shape, and advisory-recall posture. The
    Lessons pin keeps the anti-sediment answer (`none-considered`) legal on
    every surface that names the mechanism.
    """

    agents = _compact(_read("AGENTS.md"))
    for phrase in (
        "scripts/draft_checkpoint.py",
        "none-considered",
        "Durable shared state beats chat memory",
        "newest campaign checkpoint",
        "recalled state is advisory",
    ):
        assert phrase in agents, phrase

    for path in (
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
    ):
        adapter = _compact(_read(path))
        for phrase in (
            "scripts/draft_checkpoint.py",
            "none-considered",
            "newest campaign checkpoint",
            "unread backlog is not an orientation debt",
            "committed state outranks it",
        ):
            assert phrase in adapter, (path, phrase)
        # Anti-regrowth: recall stays optional and advisory; no surface may
        # convert the checkpoint or the index into a mandatory startup
        # ritual or an authority source.
        assert "must query the index" not in adapter, path
        assert "mandatory checkpoint" not in adapter, path

    modes = _compact(_read("docs/protocol/work-modes.md"))
    assert "scripts/draft_checkpoint.py" in modes
    assert "newest campaign checkpoint" in modes


def test_claude_routes_new_lessons_through_learning_candidates() -> None:
    for path in ("CLAUDE.md",):
        text = _compact(_read(path))
        for required in (
            "finish the scoped task",
            "learning-candidate",
            "truthful provider scope",
            "no canonical skill creation or edit solely because a lesson arose",
            "separately accepted, risk-classed Compact Pair",
            "stop relying on it",
            "record the conflict",
            "current accepted task authorizes",
            "review completes",
            "current code and higher-priority instructions remain controlling",
        ):
            assert required.casefold() in text.casefold(), (path, required)
        for retired in (
            "then write the skill",
            "write the skill in the same session",
            "correct that file in the same session",
        ):
            assert retired.casefold() not in text.casefold(), (path, retired)


def test_project_codex_config_does_not_claim_runtime_permissions() -> None:
    config = tomllib.loads(_read(".codex/config.toml"))

    assert "approval_policy" not in config
    assert "sandbox_mode" not in config
    assert "features" not in config


def test_provider_routers_remain_discoverable() -> None:
    agents = _compact(_read("AGENTS.md"))

    for marker in (
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
    ):
        assert marker in agents


def test_active_instruction_surfaces_have_no_superpowers_invocation() -> None:
    violations = {
        path.relative_to(ROOT).as_posix(): sorted(
            set(MANDATORY_SUPERPOWERS_RE.findall(path.read_text(encoding="utf-8")))
        )
        for path in _sweep_active_files(ACTIVE_INSTRUCTION_ROOTS, {".md", ".toml"})
        if MANDATORY_SUPERPOWERS_RE.search(path.read_text(encoding="utf-8"))
    }
    assert violations == {}


def test_chatgpt_consultation_is_an_optional_pointer_not_model_policy() -> None:
    pointer = (
        "Optional ChatGPT Pro consultation is parent-only and advisory: follow "
        ".agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol "
        "or side-effect authority."
    )
    assert (ROOT / ".agents/skills/chatgpt-pro-consultation/SKILL.md").is_file()
    # The pointer lives on load-on-trigger surfaces only; the always-loaded
    # router carries no consultation routing (context-pruning PR 2).
    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
    ):
        assert _read(path).count(pointer) == 1, path
    assert "ChatGPT" not in _read("AGENTS.md")

    source = _read("scripts/codex_protocol_model.py")
    assert "render_" "chatgpt_pro_consultation" not in source
    assert "chatgpt_pro_" "consultation_default" not in source


def test_reviewer_template_keeps_machine_readable_result_schema() -> None:
    text = _read("docs/templates/agents/reviewer.md")

    assert "schema_version" in text
    assert "reviewer-result/1" in text
    assert "reviewed_head != reviewed_commit" in text
    assert "working_tree_clean=false" in text
    assert "never invent trigger" in text
    assert "authority" in text


def test_claude_stub_targets_exist() -> None:
    """Every .claude reference stub points at a canonical body that exists.

    A renamed or deleted canonical `.agents` body must not silently empty a
    Claude skill behind a green suite (ADR-067 Stage 3).
    """

    stubs = 0
    for skill in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        if "canonical body of this skill is" not in text.casefold():
            continue
        stubs += 1
        target = ROOT / ".agents/skills" / skill.parent.name / "SKILL.md"
        assert target.is_file(), f"{skill} points at a missing body: {target}"
        assert f".agents/skills/{skill.parent.name}/SKILL.md" in text, (
            f"{skill} does not name its own canonical path"
        )
    assert stubs >= 6, "ADR-067 stubs plus writing-skills must be present"


def test_verification_report_templates_remain_identical() -> None:
    agent = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude = ROOT / ".claude/skills/seat-operator/verification-report-format.md"

    assert agent.read_bytes() == claude.read_bytes()
    text = agent.read_text(encoding="utf-8")
    for field in (
        "Verification request:",
        "Reviewed repository:",
        "Reviewed head:",
        "Reviewed base:",
        "Reviewer seat:",
        "Reviewer model:",
        "Verification harness:",
        "Verification context:",
    ):
        assert field in text


def test_active_protocol_surfaces_do_not_prescribe_exact_next_trigger() -> None:
    violations = {
        path.relative_to(ROOT).as_posix()
        for path in _sweep_active_files(ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"})
        if EXACT_NEXT_TRIGGER in path.read_text(encoding="utf-8")
    }
    assert violations == set()


PROBE_NAME = "pytest-ignored-sweep-probe"
PROBE_NESTED_FILE = "coordination/mailbox/sent/2026-01-01T00-00-00Z-probe.md"
PROBE_BODY = f"{EXACT_NEXT_TRIGGER}: run superpowers:brainstorming next.\n"


@contextmanager
def _ignored_probe(relative_root: str, *, self_ignore: bool) -> Iterator[Path]:
    """Plant a forbidden-string file in a nested tree under a git-ignored path.

    Cleanup removes *relative_root* whole, so the root has to be one this
    helper created. It is a fixed name under `.claude/worktrees/`, which is
    exactly where live checkouts are parked, and an unlucky name or a probe
    left by an interrupted run would otherwise be deleted by a passing test.
    Scoping a delete to one path was never the same as knowing that path is
    ours.

    An exclusive `mkdir` is what knows, rather than a prior `exists()` test:
    asking and then creating leaves a window in which content arriving between
    the two answers is adopted and then deleted, so the check has to be the
    creation. Cleanup is reached only on the far side of it.

    The parent may be a live `.claude/worktrees/` holding real checkouts, so it
    is rmdir'd — a no-op on any non-empty directory — only when this helper
    created it.
    """
    probe_root = ROOT / relative_root
    parent = probe_root.parent
    parent_existed = parent.is_dir()
    try:
        probe_root.mkdir(parents=True)
    except FileExistsError as exc:
        raise AssertionError(
            f"refusing to plant a probe over existing content at {probe_root}: "
            "cleanup would delete it. Confirm by hand that it is not a live "
            "checkout, then remove it."
        ) from exc
    probe = probe_root / PROBE_NESTED_FILE
    try:
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text(PROBE_BODY, encoding="utf-8")
        if self_ignore:
            (probe_root / ".gitignore").write_text("*\n", encoding="utf-8")
        yield probe
    finally:
        shutil.rmtree(probe_root, ignore_errors=True)
        if not parent_existed:
            with suppress(OSError):
                parent.rmdir()


def test_active_surface_sweeps_skip_git_ignored_trees() -> None:
    probe_roots = {
        # The reported failure: a worktree checkout under `.claude/worktrees/`.
        # Carries no `.gitignore` of its own, so it is the committed rule that
        # excludes it here, and git collapses the tree because nothing under it
        # is tracked. This is the end-to-end case against real ignore rules;
        # what a collapsed entry means is pinned by
        # test_git_collapses_only_wholly_untracked_directories.
        f".claude/worktrees/{PROBE_NAME}": False,
        # Ignored by a `.gitignore` it carries itself, so it is excluded on any
        # machine regardless of what the committed rules say. Under
        # `.claude/agents` to stay in range of both sweeps, not just the
        # protocol one.
        f".claude/agents/{PROBE_NAME}": True,
    }
    with ExitStack() as stack:
        probes = [
            stack.enter_context(_ignored_probe(relative, self_ignore=self_ignore))
            for relative, self_ignore in probe_roots.items()
        ]
        # Guard the guard: a probe that lost its forbidden strings would let
        # this test pass while proving nothing.
        for probe in probes:
            body = probe.read_text(encoding="utf-8")
            assert EXACT_NEXT_TRIGGER in body, probe
            assert MANDATORY_SUPERPOWERS_RE.search(body), probe

        swept = {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(ACTIVE_INSTRUCTION_ROOTS, {".md", ".toml"})
        } | {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(
                ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"}
            )
        }
        assert [
            path
            for path in sorted(swept)
            if any(path.startswith(f"{root}/") for root in probe_roots)
        ] == []

        test_active_instruction_surfaces_have_no_superpowers_invocation()
        test_active_protocol_surfaces_do_not_prescribe_exact_next_trigger()

    for relative in probe_roots:
        assert not (ROOT / relative).exists(), relative


def _protocol_sweep_relatives() -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in _sweep_active_files(ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"})
    }


def _stub_git(
    listing: bytes = b"",
    *,
    ignored: bool = True,
    tracked: bool = False,
    confirm_error: BaseException | None = None,
):
    """Replace git entirely.

    *listing* answers the ignored-entries query. *ignored* and *tracked* drive
    the two confirmations independently, because each half of that conjunction
    has to be defeatable on its own for a test to pin it. *confirm_error* makes
    only the confirmations fail, which is unreachable by failing the listing.
    """

    def run(arguments, *_a, **_k) -> subprocess.CompletedProcess:
        argv = tuple(arguments)
        if "check-ignore" in argv:
            if confirm_error is not None:
                raise confirm_error
            return subprocess.CompletedProcess(argv, 0 if ignored else 1)
        if "--error-unmatch" in argv:
            if confirm_error is not None:
                raise confirm_error
            return subprocess.CompletedProcess(argv, 0 if tracked else 1)
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr=b"")

    return run


def _stub_listing_only(listing: bytes):
    """Forge only the ignored-entries listing; let confirmations reach real git."""
    real = subprocess.run

    def run(arguments, *a, **k) -> subprocess.CompletedProcess:
        argv = tuple(arguments)
        if "--others" in argv:
            return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr=b"")
        return real(arguments, *a, **k)

    return run


def _stub_git_raising(error: BaseException):
    def run(*_a, **_k) -> subprocess.CompletedProcess:
        raise error

    return run


def test_git_collapses_only_wholly_untracked_directories() -> None:
    """The fact the prune rests on, measured in a real repository.

    `--directory` may collapse a directory to one entry only when nothing
    inside it is tracked. That is the whole reason a collapsed entry is worth
    proposing, so it is measured here rather than taken from documentation: if
    git ever collapsed a directory holding tracked content, the candidate set
    would be wrong at its source and this test is what would notice.
    """
    directory = Path(tempfile.mkdtemp(prefix="sweep-collapse-"))

    def git(*arguments: str) -> str:
        return subprocess.run(
            ("git", *arguments),
            cwd=directory,
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"},
        ).stdout.decode("utf-8")

    try:
        git("init", "-q")
        git("config", "user.email", "sweep@example.invalid")
        git("config", "user.name", "sweep")
        (directory / ".gitignore").write_text(
            "untracked/\nmixed/skip.md\n", encoding="utf-8"
        )
        for branch, name in (
            ("untracked", "a.md"),
            ("mixed", "skip.md"),
            ("mixed", "kept.md"),
        ):
            (directory / branch).mkdir(exist_ok=True)
            (directory / branch / name).write_text("x\n", encoding="utf-8")
        git("add", ".gitignore", "mixed/kept.md")
        git("commit", "-qm", "seed")

        listed = [
            entry
            for entry in git(
                "ls-files", "-z", "--others", "--ignored", "--directory",
                "--exclude-standard",
            ).split("\0")
            if entry
        ]
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    assert "untracked/" in listed
    # Holds a tracked file: never collapsed, so the tree is walked and only the
    # ignored member is named. This is what makes a tracked surface unskippable.
    assert "mixed/" not in listed
    assert "mixed/skip.md" in listed


def test_forged_candidate_is_refused_at_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A listing that names a directory git never collapsed cannot prune it.

    One NUL inserted into a genuine record turns `.claude/worktrees-backup/`
    into `.claude/worktrees/`, and the result is well-formed: no parser can
    reject it. So the listing only proposes. Here the forged candidate is
    `.claude/skills/`, a directory full of tracked protocol surface; only the
    listing is stubbed, so both confirmations reach real git, which refuses it
    because tracked files match. Without confirmation the whole tree would
    vanish from the sweep in silence.
    """
    monkeypatch.setattr(subprocess, "run", _stub_listing_only(b".claude/skills/\0"))
    swept = _protocol_sweep_relatives()
    assert any(path.startswith(".claude/skills/") for path in swept)


def test_confirmation_still_prunes_a_genuinely_ignored_tree(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Confirmation must not defeat the prune it exists to police.

    The counterpart to the forgery test: a candidate git really does collapse,
    checked against real git, is still skipped. Without this a confirmation
    that always refused would look identical to a correct one.
    """
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()
        assert _git_confirms_prunable(".claude/worktrees") is True
        assert relative not in _protocol_sweep_relatives()

        # And a tree holding tracked content is refused by the same call.
        assert _git_confirms_prunable(".claude/skills") is False


def test_collapsed_directory_proposes_but_a_named_file_does_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The trailing slash is the entire licence to propose skipping a tree.

    git names an ignored file individually exactly when its directory holds
    tracked content and could not be collapsed. Reading that name as a
    directory decision would propose pruning a tree git explicitly declined to
    collapse. Both directions are asserted against one planted probe, with
    confirmation stubbed to agree so that only the parse is under test.
    """
    root_relative = f".claude/worktrees/{PROBE_NAME}"
    with _ignored_probe(root_relative, self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()

        monkeypatch.setattr(subprocess, "run", _stub_git(f"{root_relative}\0".encode()))
        assert _git_ignored_entries() == (frozenset(), frozenset({root_relative}))
        assert relative in _protocol_sweep_relatives()

        monkeypatch.setattr(
            subprocess, "run", _stub_git(f"{root_relative}/\0".encode())
        )
        assert _git_ignored_entries() == (frozenset({root_relative}), frozenset())
        assert relative not in _protocol_sweep_relatives()


def test_unavailable_git_prunes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each failure direction yields no prunes at all, so the sweep widens.

    Pins the safe returns in both the listing parser and the exit-code helper.
    The listing shape previously had three such returns and no test that would
    notice any being removed, which the operator established by replacing them
    with `raise` and watching every sweep test stay green.
    """
    failures = (
        _stub_git_raising(FileNotFoundError("git")),
        _stub_git_raising(subprocess.CalledProcessError(128, ("git",))),
        _stub_git(b"\xff\xfe not utf-8\0"),
    )
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()
        for stub in failures:
            monkeypatch.setattr(subprocess, "run", stub)
            assert _git_ignored_entries() == (frozenset(), frozenset())
            assert relative in _protocol_sweep_relatives()

    # A listing that arrives but is refused at confirmation is walked too.
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()
        monkeypatch.setattr(
            subprocess, "run", _stub_git(b".claude/worktrees/\0", ignored=False)
        )
        assert relative in _protocol_sweep_relatives()


def test_confirmation_requires_both_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ignored and untracked are each necessary; neither alone is sufficient.

    A tree git ignores but which holds tracked content must still be walked, or
    the original blind spot returns by another door. A tree with nothing tracked
    that git does not ignore must be walked too, or the sweep starts skipping
    live surface on the strength of a candidate list alone. Each half is
    defeated separately here, because a test that only ever sees them agree
    cannot tell a conjunction from either of its halves.
    """
    root_relative = f".claude/worktrees/{PROBE_NAME}"
    listing = f"{root_relative}/\0".encode()
    with _ignored_probe(root_relative, self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()

        monkeypatch.setattr(
            subprocess, "run", _stub_git(listing, ignored=True, tracked=True)
        )
        assert _git_confirms_prunable(root_relative) is False
        assert relative in _protocol_sweep_relatives()

        monkeypatch.setattr(
            subprocess, "run", _stub_git(listing, ignored=False, tracked=False)
        )
        assert _git_confirms_prunable(root_relative) is False
        assert relative in _protocol_sweep_relatives()

        monkeypatch.setattr(
            subprocess, "run", _stub_git(listing, ignored=True, tracked=False)
        )
        assert _git_confirms_prunable(root_relative) is True
        assert relative not in _protocol_sweep_relatives()


def test_unconfirmable_candidate_is_walked(monkeypatch: pytest.MonkeyPatch) -> None:
    """A candidate whose confirmation cannot run is walked, not pruned.

    The listing arrives intact, so the candidate exists and the confirmation is
    actually reached. Failing the listing instead would return no candidates at
    all and leave this path unexercised, which is why the failure is injected
    into the confirmations alone.
    """
    root_relative = f".claude/worktrees/{PROBE_NAME}"
    listing = f"{root_relative}/\0".encode()
    with _ignored_probe(root_relative, self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()
        monkeypatch.setattr(
            subprocess,
            "run",
            _stub_git(listing, confirm_error=FileNotFoundError("git")),
        )
        assert _git_exit_code("check-ignore", "-q", "--", root_relative) == -1
        assert _git_confirms_prunable(root_relative) is False
        assert relative in _protocol_sweep_relatives()


def test_fragment_payload_is_discarded_whole(monkeypatch: pytest.MonkeyPatch) -> None:
    """A mid-record cut yields a fragment, and fragments are never salvaged.

    Cutting `.claude/worktrees-backup/` mid-record leaves `.claude/worktrees`,
    a real directory. Confirmation would now catch that, but the parser refuses
    it first: keeping intact records and dropping only the fragment would make
    the candidate set depend on where a stream happened to stop.
    """
    monkeypatch.setattr(
        subprocess, "run", _stub_git(b".claude/hooks/\0.claude/worktrees")
    )
    assert _git_ignored_entries() == (frozenset(), frozenset())


def test_symlinked_file_is_swept_and_symlinked_directory_is_not_followed() -> None:
    """A link to a file is active surface; a link to a directory is a duplicate.

    `os.walk` emitted symlinked files as filenames and scanned them, so a
    depth-first replacement that discards every symlink before telling a file
    from a directory silently narrows the sweep. A symlink under an active root
    is a live instruction surface whatever its bytes are stored as. A symlinked
    directory is a second route to a tree the walk already reaches by its real
    path, so following it duplicates work and invites cycles.
    """
    base = ROOT / ".claude/agents"
    target_root = Path(tempfile.mkdtemp(prefix="sweep-symlink-"))
    file_link = base / f"{PROBE_NAME}-link.md"
    directory_link = base / f"{PROBE_NAME}-dirlink"
    try:
        target = target_root / "carried.md"
        target.write_text(f"{EXACT_NEXT_TRIGGER}\n", encoding="utf-8")
        (target_root / "inside.md").write_text("x\n", encoding="utf-8")
        file_link.symlink_to(target)
        directory_link.symlink_to(target_root, target_is_directory=True)

        swept = {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(
                ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"}
            )
        }
        link_relative = file_link.relative_to(ROOT).as_posix()
        directory_relative = directory_link.relative_to(ROOT).as_posix()
    finally:
        file_link.unlink(missing_ok=True)
        directory_link.unlink(missing_ok=True)
        shutil.rmtree(target_root, ignore_errors=True)

    assert link_relative in swept
    assert f"{directory_relative}/inside.md" not in swept
    assert not any(path.startswith(f"{directory_relative}/") for path in swept)


def test_only_regular_files_are_swept() -> None:
    """A matching suffix is not enough — the entry has to be a regular file.

    A FIFO or a device node named `x.md` under an active root matches on
    suffix, and the guards open every path this returns. Reading a FIFO with no
    writer blocks forever, so admitting one would hang the sweep rather than
    fail it, and a device node would return bytes that are not the file's.
    Neither is an instruction surface.

    The regular file planted alongside them is the control: without it this
    test would also pass on a sweep that returned nothing at all.
    """
    base = ROOT / ".claude/agents"
    fifo = base / f"{PROBE_NAME}-fifo.md"
    device = base / f"{PROBE_NAME}-device.md"
    regular = base / f"{PROBE_NAME}-regular.md"
    try:
        os.mkfifo(fifo)
        device.symlink_to(Path("/dev/null"))
        regular.write_text("ordinary\n", encoding="utf-8")

        swept = {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(
                ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"}
            )
        }
        relatives = {
            name: path.relative_to(ROOT).as_posix()
            for name, path in (("fifo", fifo), ("device", device), ("regular", regular))
        }
    finally:
        fifo.unlink(missing_ok=True)
        device.unlink(missing_ok=True)
        regular.unlink(missing_ok=True)

    assert relatives["regular"] in swept
    assert relatives["fifo"] not in swept
    assert relatives["device"] not in swept


def test_a_nested_git_directory_is_never_swept() -> None:
    """`.git` is repository plumbing, not instruction surface.

    A nested checkout or submodule under an active root brings its own `.git`,
    whose contents are neither authored nor read as protocol text. Nothing in
    the ignore listing excludes it — git does not report its own directory as
    ignored — so the skip is by name and needs its own test.
    """
    repository = ROOT / ".claude/agents" / f"{PROBE_NAME}-nested"
    plumbing = repository / ".git"
    try:
        plumbing.mkdir(parents=True)
        (plumbing / "config.toml").write_text("x\n", encoding="utf-8")
        (repository / "kept.md").write_text("ordinary\n", encoding="utf-8")

        swept = {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(
                ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"}
            )
        }
        kept = (repository / "kept.md").relative_to(ROOT).as_posix()
        buried = (plumbing / "config.toml").relative_to(ROOT).as_posix()
    finally:
        shutil.rmtree(repository, ignore_errors=True)

    # The control: the tree itself is walked, so the skip below is specific.
    assert kept in swept
    assert buried not in swept


def test_explicitly_named_file_roots_are_swept() -> None:
    """A root named as a file is admitted because it was named, not found.

    `AGENTS.md` and `CLAUDE.md` are roots rather than directories, so no walk
    ever reaches them and `root.is_file()` is their only admission path. Losing
    it would drop two of the most load-bearing instruction surfaces in the
    repository with no directory-level symptom to notice.
    """
    swept = {
        path.relative_to(ROOT).as_posix()
        for path in _sweep_active_files(ACTIVE_INSTRUCTION_ROOTS, {".md", ".toml"})
    }
    for named in ("AGENTS.md", "CLAUDE.md"):
        assert named in ACTIVE_INSTRUCTION_ROOTS
        assert (ROOT / named).is_file()
        assert named in swept


def test_only_configured_suffixes_are_swept() -> None:
    """The suffix set decides what counts as surface, so it needs its own test.

    Widening it does not hide anything — it scans more — but it is still an
    independent scope control, and a guard that quietly began reading every
    file under an active root would report violations in material that was
    never instruction text.
    """
    base = ROOT / ".claude/agents"
    wanted = base / f"{PROBE_NAME}-wanted.md"
    unwanted = base / f"{PROBE_NAME}-unwanted.txt"
    try:
        wanted.write_text("ordinary\n", encoding="utf-8")
        unwanted.write_text("ordinary\n", encoding="utf-8")
        swept = {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"})
        }
        wanted_relative = wanted.relative_to(ROOT).as_posix()
        unwanted_relative = unwanted.relative_to(ROOT).as_posix()
    finally:
        wanted.unlink(missing_ok=True)
        unwanted.unlink(missing_ok=True)

    assert wanted_relative in swept
    assert unwanted_relative not in swept


def test_an_individually_named_ignored_file_is_not_swept() -> None:
    """The file half of the ignore listing has to actually exclude something.

    git names an ignored file individually exactly when its directory holds
    tracked content and so could not be collapsed — which is why the probe goes
    under `.claude/agents`, a directory with tracked files, rather than into a
    throwaway tree that git would collapse whole. The visible file beside it is
    the control: without it this would also pass on a sweep returning nothing.
    """
    base = ROOT / ".claude/agents"
    rules = base / ".gitignore"
    hidden = base / f"{PROBE_NAME}-ignored.md"
    visible = base / f"{PROBE_NAME}-visible.md"
    try:
        rules.write_text(f"{hidden.name}\n", encoding="utf-8")
        hidden.write_text("ordinary\n", encoding="utf-8")
        visible.write_text("ordinary\n", encoding="utf-8")

        hidden_relative = hidden.relative_to(ROOT).as_posix()
        visible_relative = visible.relative_to(ROOT).as_posix()
        _, ignored_files = _git_ignored_entries()
        # Pin the precondition: git must be naming it as a file, not collapsing
        # its directory, or this test would prove nothing about that branch.
        assert hidden_relative in ignored_files

        swept = {
            path.relative_to(ROOT).as_posix()
            for path in _sweep_active_files(ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"})
        }
    finally:
        rules.unlink(missing_ok=True)
        hidden.unlink(missing_ok=True)
        visible.unlink(missing_ok=True)

    assert visible_relative in swept
    assert hidden_relative not in swept


def test_an_unlistable_directory_fails_loudly() -> None:
    """A directory the sweep cannot list must raise, not disappear.

    Catching the error would drop that whole subtree with no signal — the same
    silent narrowing that a hardcoded prune list produced, arriving through an
    exception handler instead. Failing loudly says plainly that the sweep could
    not cover something, which is the one direction this module never regrets.
    """
    blocked = ROOT / ".claude/agents" / f"{PROBE_NAME}-blocked"
    try:
        blocked.mkdir(parents=True)
        (blocked / "hidden.md").write_text("x\n", encoding="utf-8")
        blocked.chmod(0o000)
        try:
            list(blocked.iterdir())
        except PermissionError:
            pass
        else:  # pragma: no cover - depends on filesystem and privilege
            pytest.skip("this filesystem lets the owner list a 0o000 directory")

        with pytest.raises(OSError):
            _sweep_active_files(ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"})
    finally:
        with suppress(OSError):
            blocked.chmod(0o755)
        shutil.rmtree(blocked, ignore_errors=True)


# The magic signature space. Three review rounds each named a form the previous
# list omitted — `:/` beside `:(top)`, then `:x` and `::x`, then two-character
# signatures such as `://x` — so the list is generated from the grammar rather
# than extended one discovery at a time: a leading colon, zero or more signature
# symbols, optionally closed by a colon.
MAGIC_SIGNATURE_SYMBOLS = string.punctuation
MAGIC_SIGNATURES = (
    "",
    "(top)",
    "(top,literal)",
    *MAGIC_SIGNATURE_SYMBOLS,
    *("".join(pair) for pair in itertools.product(MAGIC_SIGNATURE_SYMBOLS, repeat=2)),
)

# The floor the sweep rests on: signatures measured to win both confirmations on
# git 2.50.1 against a planted ignored directory. Membership is what makes the
# refusal sweep non-vacuous, so it is measured rather than assumed — but only
# for these, because each measurement costs two subprocesses while a refusal
# costs none, which is what lets the sweep above be wide and this list short.
# Asserted by equality: a change here is git moving under this module and is
# worth a loud re-measurement rather than a threshold loose enough to absorb it.
WINNABLE_MAGIC_SIGNATURES = frozenset({"", "(top)", "/", ":", "//"})


def test_pathspec_magic_candidate_is_refused_before_git_is_asked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A candidate carrying pathspec magic never becomes a prune.

    `--` ends option parsing but leaves magic alive, so `:(top)x` and `:/x` are
    answered as patterns rooted at the top of the repository rather than as
    directories literally bearing those names. Both confirmations would then be
    about a path that is not the one being skipped. `--literal-pathspecs` fixes
    this for `ls-files` but `git check-ignore` rejects that flag outright, so
    the magic is refused at the door instead.

    The refusal is worth asserting only if git would otherwise have answered
    yes, so that answer is measured. Four things are needed before the
    measurement means what it claims, and each of them was missing once:

    A generated signature space rather than the forms someone remembered, and
    every candidate in it refused. Naming forms let a guard narrowed to `:(`
    pass while `:/` won, then a guard narrowed to four prefixes pass while `:x`
    and `::x` won, then a one-character sweep pass while `://x` won. What no
    finite sweep can exclude is a carve-out aimed at exactly the shape it does
    not generate, so the sweep is paired with the property it approximates: the
    leading colon decides, and the same path without it is not refused at all.
    Beyond that the completeness of the refusal rests on git's grammar, in which
    magic is introduced by a leading colon and by nothing else, and that is an
    argument rather than a measurement here.

    An answer whose rule is committed, bytes and all. A bare exit code cannot
    tell `.gitignore` from `$GIT_DIR/info/exclude`, and trackedness of the
    answering *file* is not enough either, because `core.excludesFile` can
    select a tracked path whose working copy carries the rule while the
    committed copy does not. Git reports source, line and pattern together, so
    the committed blob is read at that line and required to be that pattern.

    A query that does not depend on the checkout. `.claude/worktrees/` is
    directory-only, and `check-ignore` applies a directory-only rule to a bare
    path only where it can see a directory, so a bare query is answered 0 in
    the main checkout and 1 from a linked worktree. Naming a path *under* the
    ignored directory is what removes that dependency, because the same rule
    matches a descendant whether or not the parent exists on disk. The probe is
    planted for other reasons — the sweep below needs a real file, and a
    candidate reaching `_git_confirms_prunable` in production always names
    something git just listed off disk — and not to make these exits hold.

    Git actually left unasked. That is this test's name, and nothing pinned it:
    a guard that refused only after consulting git would satisfy every
    assertion above. Stubbing git to fail cannot pin it either, because
    `_git_exit_code` maps a failure to -1 and the conjunction then refuses for
    the wrong reason. So git is stubbed to *grant* both confirmations, and the
    calls are counted.
    """
    root_relative = f".claude/worktrees/{PROBE_NAME}"
    with _ignored_probe(root_relative, self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()

        # The floor. Without at least one form that would otherwise win, every
        # refusal below is satisfied by git rather than by the guard.
        winnable: set[str] = set()
        for signature in sorted(WINNABLE_MAGIC_SIGNATURES):
            forged = f":{signature}{root_relative}"
            # The literal path is pinned absent: that is what makes any 0 here
            # an answer about some other path, which is the hazard the guard
            # closes rather than a coincidence about this one.
            assert not (ROOT / forged).exists(), forged
            ignored = _git_exit_code("check-ignore", "-q", "--", forged)
            tracked = _git_exit_code(
                "ls-files", "--cached", "--error-unmatch", "--", forged
            )
            # Both halves are pinned separately, because
            # `_git_confirms_prunable` needs both and a False from either one
            # is indistinguishable from the refusal under test.
            if ignored == 0 and tracked == NO_PATHSPEC_MATCH:
                winnable.add(signature)
                assert _git_ignore_rule_is_committed(forged), forged
        assert winnable == WINNABLE_MAGIC_SIGNATURES

        # Refusal over the whole generated space. Cheap, because a refused
        # candidate never reaches a subprocess.
        for signature in MAGIC_SIGNATURES:
            forged = f":{signature}{root_relative}"
            assert _git_confirms_prunable(forged) is False, forged

        # The property the enumeration only approximates: the leading colon is
        # what decides, and nothing further along. The same path without it is
        # not refused here at all — it reaches git and is answered on its
        # merits — so a guard keyed on any longer prefix has to disagree with
        # one of these two lines.
        assert _git_confirms_prunable(root_relative) is True

        granting = _stub_git(ignored=True, tracked=False)
        asked: list[tuple[str, ...]] = []

        def counting(arguments, *a, **k) -> subprocess.CompletedProcess:
            asked.append(tuple(arguments))
            return granting(arguments, *a, **k)

        with monkeypatch.context() as scoped:
            scoped.setattr(subprocess, "run", counting)
            for signature in MAGIC_SIGNATURES:
                candidate = f":{signature}{root_relative}"
                assert _git_confirms_prunable(candidate) is False, candidate
        assert asked == []

        forged = f":(top){root_relative}"
        monkeypatch.setattr(subprocess, "run", _stub_listing_only(f"{forged}/\0".encode()))
        assert relative in _protocol_sweep_relatives()


def test_ignore_provenance_requires_a_committed_rule() -> None:
    """An exclude rule that is not committed may not answer for the repository.

    Built in a throwaway repository rather than in this one. Every earlier shape
    of this test planted fixed-name fixtures in the reviewed checkout, and one
    rewrote a tracked file and restored it from a snapshot: a concurrent reader
    could observe that file empty or modified, a crash mid-test would leave it
    so, and a concurrent writer's change would be lost to the restore. This
    repository has concurrent sessions in it. A test that needs a repository in
    a particular state should build one.

    Four sources answer the same query, and only one is a rule the repository
    carries. Each defeats a different version of this check that has already
    been shipped and found wanting:

    - an untracked file whose name up to its first colon spells a tracked one,
      which defeats a parser that splits there;
    - a *tracked* file whose working copy carries the rule while its committed
      copy does not, which defeats a check that asks only whether the source
      pathname is in the index;
    - a file whose committed line ends in two carriage returns while its working
      line ends in none. Git answers from the working bytes; the committed line
      is a pattern ending in a carriage return and matches nothing the bare
      pattern matches. This defeats a comparison that strips every trailing CR
      instead of the single one a CRLF file leaves behind.

    The committed rule is then required to be accepted, carrying the trailing
    spaces git strips before reporting, so the check is pinned in the direction
    that would otherwise fail a rule the repository really does carry.
    """
    repository = Path(tempfile.mkdtemp(prefix="ignore-provenance-"))
    environment = {
        name: value for name, value in os.environ.items() if name != "GIT_INDEX_FILE"
    }

    def git(*arguments: str) -> None:
        subprocess.run(
            ("git", *arguments),
            cwd=repository,
            check=True,
            capture_output=True,
            env={**environment, "GIT_CONFIG_GLOBAL": "/dev/null"},
        )

    def rule_is_committed(excludes: str | None) -> bool:
        if excludes is None:
            return _git_ignore_rule_is_committed(TARGET, repository)
        with pytest.MonkeyPatch.context() as scoped:
            scoped.setenv("GIT_CONFIG_COUNT", "1")
            scoped.setenv("GIT_CONFIG_KEY_0", "core.excludesFile")
            scoped.setenv("GIT_CONFIG_VALUE_0", excludes)
            return _git_ignore_rule_is_committed(TARGET, repository)

    TARGET = "ignored-by-probe"
    try:
        git("init", "-q", ".")
        git("config", "user.email", "probe@example.invalid")
        git("config", "user.name", "probe")
        (repository / TARGET).mkdir()

        # Committed carrying the trailing spaces git strips before reporting.
        (repository / ".gitignore").write_text(f"{TARGET}/   \n", encoding="utf-8")
        # Tracked, and committed with no rule in it at all.
        (repository / "tracked.txt").write_text("nothing here\n", encoding="utf-8")
        # Committed as a pattern ending in a carriage return.
        (repository / "crlf.txt").write_bytes(f"{TARGET}/\r\r\n".encode())
        git("add", ".gitignore", "tracked.txt", "crlf.txt")
        git("commit", "-qm", "probe")

        # The committed rule answers, is reported with its spaces removed, and
        # is accepted. Without this the three refusals below could all be a
        # check that never says yes to anything.
        record = _git_ignore_record(TARGET, repository)
        assert record is not None, "the committed rule did not answer"
        assert record[0] == ".gitignore", record
        assert record[2] == f"{TARGET}/", record
        assert rule_is_committed(None) is True

        # Move the committed rule out of the way so the shadows are what answer.
        (repository / ".gitignore").write_text("unrelated/\n", encoding="utf-8")
        assert _git_ignore_record(TARGET, repository) is None

        shadow = ".gitignore:shadow"
        (repository / shadow).write_text(f"{TARGET}/\n", encoding="utf-8")
        assert shadow.split(":", 1)[0] == ".gitignore"
        assert rule_is_committed(shadow) is False

        (repository / "tracked.txt").write_text(
            f"nothing here\n{TARGET}/\n", encoding="utf-8"
        )
        assert (
            _git_exit_code(
                "--literal-pathspecs", "-C", str(repository), "ls-files", "--cached",
                "--error-unmatch", "--", "tracked.txt",
            )
            == 0
        ), "the tracked-source case needs its source to really be tracked"
        assert rule_is_committed("tracked.txt") is False

        (repository / "crlf.txt").write_bytes(f"{TARGET}/\n".encode())
        assert rule_is_committed("crlf.txt") is False
    finally:
        shutil.rmtree(repository, ignore_errors=True)

    assert _committed_pattern(f"{TARGET}/\r\r") == f"{TARGET}/\r"
    assert _committed_pattern(f"{TARGET}/\r") == f"{TARGET}/"
    assert _committed_pattern(f"{TARGET}/   ") == f"{TARGET}/"
    # An escaped trailing space is kept because git keeps it, so such a rule is
    # accepted. Mixing the two is where this comparison stops following git: it
    # reduces `x\  ` to `x\ ` and this does not, so the rule is refused. Both
    # are pinned so the docstring cannot drift from either again.
    assert _committed_pattern(f"{TARGET}/\\ ") == f"{TARGET}/\\ "
    assert _committed_pattern(f"{TARGET}/\\  ") == f"{TARGET}/\\  "
def test_only_an_exact_no_match_exit_confirms_nothing_tracked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An errored `ls-files` is not evidence that a directory is empty.

    `--error-unmatch` exits exactly 1 when the pathspec matched nothing. Every
    other non-zero exit is a failure to answer, and reading any non-zero as
    "nothing tracked" turned a broken call into permission to skip a tree.
    """
    root_relative = f".claude/worktrees/{PROBE_NAME}"
    listing = f"{root_relative}/\0".encode()

    def stub_with_tracked_exit(code: int):
        def run(arguments, *_a, **_k) -> subprocess.CompletedProcess:
            argv = tuple(arguments)
            if "check-ignore" in argv:
                return subprocess.CompletedProcess(argv, 0)
            if "--error-unmatch" in argv:
                return subprocess.CompletedProcess(argv, code)
            return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr=b"")

        return run

    with _ignored_probe(root_relative, self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()
        for code in (128, 129, -1):
            monkeypatch.setattr(subprocess, "run", stub_with_tracked_exit(code))
            assert _git_confirms_prunable(root_relative) is False, code
            assert relative in _protocol_sweep_relatives(), code

        monkeypatch.setattr(subprocess, "run", stub_with_tracked_exit(NO_PATHSPEC_MATCH))
        assert _git_confirms_prunable(root_relative) is True
        assert relative not in _protocol_sweep_relatives()


def test_each_candidate_is_confirmed_immediately_before_its_own_descent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Confirmations follow the descent, rather than running a level ahead of it.

    `os.walk` requires a parent's whole sibling list to be filtered before it
    enters the first sibling, so every candidate's answer aged by one
    confirmation for each later sibling, and the operator measured that as a
    widening of the race. The two layouts are distinguishable by order alone: a
    nested candidate under an earlier sibling is confirmed *before* a later
    top-level sibling only if the descent is depth-first and lazy.
    """
    outer = ROOT / ".claude/agents" / f"aaa-{PROBE_NAME}"
    nested = outer / "inner"
    later = ROOT / ".claude/agents" / f"zzz-{PROBE_NAME}"
    order: list[str] = []

    def recording(relative: str) -> bool:
        order.append(relative)
        return False

    try:
        nested.mkdir(parents=True)
        (nested / ".gitignore").write_text("*\n", encoding="utf-8")
        (nested / "probe.md").write_text("x\n", encoding="utf-8")
        later.mkdir(parents=True)
        (later / ".gitignore").write_text("*\n", encoding="utf-8")
        (later / "probe.md").write_text("x\n", encoding="utf-8")

        directories, _ = _git_ignored_entries()
        assert nested.relative_to(ROOT).as_posix() in directories
        assert later.relative_to(ROOT).as_posix() in directories

        monkeypatch.setattr(f"{__name__}._git_confirms_prunable", recording)
        _sweep_active_files((".claude/agents",), {".md"})
    finally:
        shutil.rmtree(outer, ignore_errors=True)
        shutil.rmtree(later, ignore_errors=True)

    assert order.index(nested.relative_to(ROOT).as_posix()) < order.index(
        later.relative_to(ROOT).as_posix()
    ), order


def test_boundary_truncated_listing_only_prunes_less(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A listing cut at a record boundary is shorter, never wrong.

    No parser can tell this shape from a complete listing, and it no longer
    needs to: a lost entry removes a candidate. The probe's tree is absent from
    the shortened listing, so it is walked, while the surviving entry is still
    proposed.
    """
    monkeypatch.setattr(subprocess, "run", _stub_git(b".claude/hooks/\0"))
    assert _git_ignored_entries() == (frozenset({".claude/hooks"}), frozenset())
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        assert probe.relative_to(ROOT).as_posix() in _protocol_sweep_relatives()
