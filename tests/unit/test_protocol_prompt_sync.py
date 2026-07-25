from __future__ import annotations

import os
import re
import shutil
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
# then to whether that listing was truncated at a record boundary. The prune
# now asks git for a positive statement instead; see `_sweep_active_files`.


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
    directory may be pruned unwalked. A named file may be skipped, but says
    nothing about any tree, so it must never stop a walk from descending.
    """
    entries = _git_listing(
        "--others", "--ignored", "--directory", "--exclude-standard"
    )
    directories = frozenset(entry.rstrip("/") for entry in entries if entry.endswith("/"))
    files = frozenset(entry for entry in entries if not entry.endswith("/"))
    return directories, files


def _sweep_active_files(roots: Iterable[str], suffixes: Iterable[str]) -> list[Path]:
    """Files under *roots* carrying *suffixes*, skipping anything git ignores.

    `os.walk` rather than `rglob` because the prune has to happen *before*
    descending: an ignored worktree must never be walked, not merely filtered
    out afterwards. A root named explicitly is always swept even when ignored —
    naming it is the opt-in.

    A directory is pruned only where git collapsed it, which is git stating
    that nothing tracked lives beneath it. Nothing else prunes: there is no
    pathname this module skips on its own authority, so there is no path where
    a tracked surface can be skipped in silence.

    Every way this can go wrong subtracts. A git that fails, is missing, returns
    nothing, or returns a listing cut short at a record boundary yields fewer
    collapsed entries, so the sweep walks more and any violation it finds is
    reported rather than hidden. The single shape that could add a prune is a
    fragment left by a mid-record cut, and `_git_listing` discards any payload
    carrying one. A guard that inspects too much fails loudly; one that
    inspects too little does not fail at all.
    """
    wanted = frozenset(suffixes)
    prunable_directories, ignored_files = _git_ignored_entries()

    def relative_to_root(path: Path) -> str:
        return path.relative_to(ROOT).as_posix()

    found: list[Path] = []
    for relative in roots:
        root = ROOT / relative
        if root.is_file():
            found.append(root)
            continue
        for parent, directories, filenames in os.walk(root):
            branch = Path(parent)
            directories[:] = sorted(
                name
                for name in directories
                if name != ".git"
                and relative_to_root(branch / name) not in prunable_directories
            )
            found.extend(
                branch / name
                for name in sorted(filenames)
                if (branch / name).suffix in wanted
                and relative_to_root(branch / name) not in ignored_files
            )
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

    assert "mailbox is authoritative unless a live signed-bus event ref" in continuation
    assert "matching seat cursor ref" in continuation
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


def test_project_codex_config_does_not_claim_runtime_permissions() -> None:
    config = tomllib.loads(_read(".codex/config.toml"))

    assert "approval_policy" not in config
    assert "sandbox_mode" not in config
    assert "features" not in config


def test_provider_routers_remain_discoverable() -> None:
    agents = _compact(_read("AGENTS.md"))

    for marker in (
        "docs/protocol/agy/continuation.md",
        ".agents/skills/antigravity-harness/",
        ".agy/agents/",
        "docs/protocol/cursor/continuation.md",
        ".cursor/rules/",
        "docs/protocol/cursor/roles/",
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
    for path in CODEX_ENTRY_SURFACES:
        assert _read(path).count(pointer) == 1, path

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

    Only *relative_root* is ever removed. Its parent may be a live
    `.claude/worktrees/` holding real checkouts, so the parent is rmdir'd — a
    no-op on any non-empty directory — only when this helper created it.
    """
    probe_root = ROOT / relative_root
    parent = probe_root.parent
    parent_existed = parent.is_dir()
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


def _stub_git_stdout(payload: bytes):
    def run(*_arguments: object, **_keywords: object) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess((), 0, stdout=payload, stderr=b"")

    return run


def _stub_git_raising(error: BaseException):
    def run(*_arguments: object, **_keywords: object) -> subprocess.CompletedProcess:
        raise error

    return run


def test_git_collapses_only_wholly_untracked_directories() -> None:
    """The fact the prune rests on, measured in a real repository.

    `--directory` may collapse a directory to one entry only when nothing
    inside it is tracked. That is the whole reason a collapsed entry counts as
    evidence, so it is measured here rather than taken from documentation: if
    git ever collapsed a directory holding tracked content, the prune would be
    unsound and this test is what would notice.
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
        (directory / ".gitignore").write_text("untracked/\nmixed/skip.md\n", encoding="utf-8")
        for branch, name in (("untracked", "a.md"), ("mixed", "skip.md"), ("mixed", "kept.md")):
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

    # Wholly untracked: collapsed, and therefore prunable.
    assert "untracked/" in listed
    # Holds a tracked file: never collapsed, so the tree is walked and only the
    # ignored member is named. This is what makes a tracked surface unskippable.
    assert "mixed/" not in listed
    assert "mixed/skip.md" in listed


def test_collapsed_directory_prunes_but_a_named_file_does_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The trailing slash is the entire licence to skip a tree.

    git names an ignored file individually exactly when its directory holds
    tracked content and could not be collapsed. Reading that name as a
    directory decision would prune a tree git explicitly declined to collapse,
    which is the original blind spot in its purest form. Both directions are
    asserted against one planted probe.
    """
    root_relative = f".claude/worktrees/{PROBE_NAME}"
    with _ignored_probe(root_relative, self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()

        monkeypatch.setattr(
            subprocess, "run", _stub_git_stdout(f"{root_relative}\0".encode())
        )
        assert _git_ignored_entries() == (frozenset(), frozenset({root_relative}))
        assert relative in _protocol_sweep_relatives()

        monkeypatch.setattr(
            subprocess, "run", _stub_git_stdout(f"{root_relative}/\0".encode())
        )
        assert _git_ignored_entries() == (frozenset({root_relative}), frozenset())
        assert relative not in _protocol_sweep_relatives()


def test_unavailable_git_prunes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each failure direction yields no prunes at all, so the sweep widens.

    Pins the three safe returns individually. The previous shape had all three
    and no test that would have noticed any of them being removed, which the
    operator established by replacing them with `raise` and watching every
    sweep test stay green.
    """
    failures = (
        _stub_git_raising(FileNotFoundError("git")),
        _stub_git_raising(subprocess.CalledProcessError(128, ("git",))),
        _stub_git_stdout(b"\xff\xfe not utf-8\0"),
    )
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        relative = probe.relative_to(ROOT).as_posix()
        for stub in failures:
            monkeypatch.setattr(subprocess, "run", stub)
            assert _git_ignored_entries() == (frozenset(), frozenset())
            assert relative in _protocol_sweep_relatives()


def test_fragment_payload_is_discarded_whole(monkeypatch: pytest.MonkeyPatch) -> None:
    """A mid-record cut is the one shape that could ADD a prune.

    Cutting `.claude/worktrees-backup/` mid-record leaves `.claude/worktrees`,
    a real directory git never reported as wholly untracked. Salvaging the
    intact records and dropping only the fragment would prune on a path git did
    not name, so a payload carrying one is discarded entirely.
    """
    monkeypatch.setattr(
        subprocess,
        "run",
        _stub_git_stdout(b".claude/hooks/\0.claude/worktrees"),
    )
    assert _git_ignored_entries() == (frozenset(), frozenset())
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        assert probe.relative_to(ROOT).as_posix() in _protocol_sweep_relatives()


def test_boundary_truncated_listing_only_prunes_less(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A listing cut at a record boundary is shorter, never wrong.

    No parser can tell this shape from a complete listing, and it no longer
    needs to: a lost entry removes a prune. The probe's tree is absent from the
    shortened listing, so it is walked rather than skipped, and the surviving
    entry still prunes.
    """
    monkeypatch.setattr(subprocess, "run", _stub_git_stdout(b".claude/hooks/\0"))
    assert _git_ignored_entries() == (frozenset({".claude/hooks"}), frozenset())
    with _ignored_probe(f".claude/worktrees/{PROBE_NAME}", self_ignore=False) as probe:
        assert probe.relative_to(ROOT).as_posix() in _protocol_sweep_relatives()
