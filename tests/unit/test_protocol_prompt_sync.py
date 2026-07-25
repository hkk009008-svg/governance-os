from __future__ import annotations

import os
import re
import shutil
import subprocess
import tomllib
from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager, suppress
from pathlib import Path

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
# Directory walks see the filesystem; git's ignore rules live in the index and
# exclude files, so the two never meet on their own. A git worktree checked out
# under `.claude/worktrees/<name>/` is a full second copy of this repo —
# mailbox history and all — and would otherwise be judged as active protocol
# surface. `.claude/worktrees/` is only in machine-local `.git/info/exclude`,
# never in the committed `.gitignore`, so git cannot be the sole authority
# here: this floor holds on a fresh clone where git reports nothing ignored.
UNSWEEPABLE_FALLBACK = frozenset({".claude/worktrees"})


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _git_ignored_paths() -> frozenset[str]:
    """Root-relative posix paths git ignores, collapsed at directory level.

    One `git ls-files` call: `--directory` collapses a wholly-ignored tree to
    its top directory, so a worktree holding thousands of files costs a single
    entry. `GIT_INDEX_FILE` is scrubbed because this repo exports a per-seat
    index — inheriting it would make tracked files read as untracked.
    """
    environment = {
        name: value for name, value in os.environ.items() if name != "GIT_INDEX_FILE"
    }
    try:
        listing = subprocess.run(
            (
                "git",
                "ls-files",
                "-z",
                "--others",
                "--ignored",
                "--directory",
                "--exclude-standard",
            ),
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        return UNSWEEPABLE_FALLBACK
    ignored = {entry.rstrip("/") for entry in listing.split("\0") if entry}
    return frozenset(ignored | UNSWEEPABLE_FALLBACK)


def _sweep_active_files(roots: Iterable[str], suffixes: Iterable[str]) -> list[Path]:
    """Files under *roots* carrying *suffixes*, skipping anything git ignores.

    `os.walk` rather than `rglob` because the prune has to happen *before*
    descending: an ignored worktree must never be walked, not merely filtered
    out afterwards. A root named explicitly is always swept even when ignored —
    naming it is the opt-in.
    """
    wanted = frozenset(suffixes)
    ignored = _git_ignored_paths()

    def is_ignored(path: Path) -> bool:
        return path.relative_to(ROOT).as_posix() in ignored

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
                if name != ".git" and not is_ignored(branch / name)
            )
            found.extend(
                branch / name
                for name in sorted(filenames)
                if (branch / name).suffix in wanted and not is_ignored(branch / name)
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
        # Carries no `.gitignore`, so it is pruned by UNSWEEPABLE_FALLBACK even
        # on a clone where nothing excludes that path.
        f".claude/worktrees/{PROBE_NAME}": False,
        # Ignored by a `.gitignore` it carries itself — ignored on any machine,
        # and absent from UNSWEEPABLE_FALLBACK, so this pins the git lookup
        # rather than the hardcoded floor. Under `.claude/agents` to stay in
        # range of both sweeps, not just the protocol one.
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
