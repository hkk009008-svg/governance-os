from __future__ import annotations

import re
import subprocess
import tomllib
from collections.abc import Iterable
from pathlib import Path

import git_runner


ROOT = Path(__file__).resolve().parents[2]
CODEX_ENTRY_SURFACES = (
    "AGENTS.md",
    "docs/protocol/codex/continuation.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
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
    r"\bsuperpowers:[a-z0-9][a-z0-9-]*\b", re.IGNORECASE
)
EXACT_NEXT_TRIGGER = "Exact Next Trigger"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _active_files(
    roots: Iterable[str], suffixes: set[str], root: Path = ROOT
) -> list[Path]:
    result = git_runner.run_git(
        root,
        ["ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", *roots],
        mode="dashboard",
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    return [
        root / relative
        for relative in result.stdout.decode("utf-8").split("\0")
        if relative
        and Path(relative).suffix in suffixes
        and (root / relative).is_file()
    ]


def test_codex_entry_surfaces_are_compact_executable_and_native() -> None:
    budgets = {
        "AGENTS.md": 140,
        "docs/protocol/codex/continuation.md": 90,
        ".agents/skills/four-seat-protocol/SKILL.md": 60,
        ".codex/agents/README.md": 25,
    }
    copied_host_mechanics = (
        "wait_threads",
        "read_thread(turnLimit",
        "supported scoped execution profile",
        "at most one discovery refresh",
        "Capacity Split Default:",
        "2-cycle escalation limit",
    )
    for path in CODEX_ENTRY_SURFACES:
        text = _read(path)
        compact = _compact(text.replace("`", ""))
        assert "scripts/codex_protocol_model.py" in compact
        assert "render_" not in compact
        assert "native" in text.casefold()
        assert "GIT_INDEX_FILE" not in text
        assert not any(item in compact for item in copied_host_mechanics)
    for path, maximum in budgets.items():
        assert len(_read(path).splitlines()) <= maximum, path


def test_codex_agent_catalog_contains_only_named_role_deltas() -> None:
    for number in range(1, 5):
        assert not (ROOT / f".codex/agents/agent{number:02}.toml").exists()
    configs = {
        path.stem: tomllib.loads(path.read_text(encoding="utf-8"))
        for path in (ROOT / ".codex/agents").glob("*.toml")
    }
    assert set(configs) == CORE_CODEX_AGENTS
    assert {config["name"] for config in configs.values()} == CORE_CODEX_AGENTS
    readme = _read(".codex/agents/README.md")
    assert "agentNN" not in readme
    for name in CORE_CODEX_AGENTS:
        assert f"`{name}`" in readme
    assert "only role-specific deltas" in readme


def test_transport_role_and_execution_boundaries_stay_explicit() -> None:
    continuation = _compact(_read("docs/protocol/codex/continuation.md"))
    for phrase in (
        "mailbox is the configured coordination transport",
        "governance.toml",
        "explicit reviewed transport change",
        "fails closed",
        "transport ambiguity fails visibly",
        "coordination/bin/send-event",
        "coordination/bin/consume-events",
        "never raw event or cursor edits",
        "coordinator has no cursor",
    ):
        assert phrase.casefold() in continuation.casefold(), phrase

    skill = _compact(_read(".agents/skills/four-seat-protocol/SKILL.md"))
    for phrase in (
        "Do not infer a live role",
        "never reviews authored work",
        "without becoming a production author or approval gate",
        "reports state without claiming work",
        "do not publish live-role events or verdicts",
        "External effects remain separately authorized",
    ):
        assert phrase.casefold() in skill.casefold(), phrase

    agents = _compact(_read("AGENTS.md"))
    for phrase in (
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
        assert phrase.casefold() in agents.casefold(), phrase
    assert "skill presence alone is not a trigger" in agents
    assert "task-count or line-count mandate" not in agents


def test_checkpoint_contract_is_shared_without_becoming_startup_ceremony() -> None:
    agents = _compact(_read("AGENTS.md"))
    for phrase in (
        "scripts/draft_checkpoint.py",
        "none-considered",
        "Durable shared state beats chat memory",
        "newest campaign checkpoint",
        "recalled state is advisory",
    ):
        assert phrase in agents
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
        assert "must query the index" not in adapter
        assert "mandatory checkpoint" not in adapter


def test_claude_learning_boundary_remains_small_and_explicit() -> None:
    text = _compact(_read("CLAUDE.md"))
    for phrase in (
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
        assert phrase.casefold() in text.casefold(), phrase
    for retired in (
        "then write the skill",
        "write the skill in the same session",
        "correct that file in the same session",
    ):
        assert retired.casefold() not in text.casefold(), retired


def test_provider_config_and_optional_consultation_do_not_grant_authority() -> None:
    config = tomllib.loads(_read(".codex/config.toml"))
    assert not {"approval_policy", "sandbox_mode", "features"} & set(config)

    agents = _read("AGENTS.md")
    for marker in (
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
    ):
        assert marker in agents
    assert "ChatGPT" not in agents

    pointer = (
        "Optional ChatGPT Pro consultation is parent-only and advisory: follow "
        ".agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol "
        "or side-effect authority."
    )
    assert (ROOT / ".agents/skills/chatgpt-pro-consultation/SKILL.md").is_file()
    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
    ):
        assert _read(path).count(pointer) == 1, path


def test_reviewer_templates_and_claude_skill_stubs_stay_bound() -> None:
    reviewer = _read("docs/templates/agents/reviewer.md")
    for field in (
        "schema_version",
        "reviewer-result/1",
        "reviewed_head != reviewed_commit",
        "working_tree_clean=false",
        "never invent trigger",
        "authority",
    ):
        assert field in reviewer

    stubs = 0
    for skill in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        if "canonical body of this skill is" not in text.casefold():
            continue
        stubs += 1
        target = ROOT / ".agents/skills" / skill.parent.name / "SKILL.md"
        assert target.is_file(), target
        assert f".agents/skills/{skill.parent.name}/SKILL.md" in text
    assert stubs >= 6

    canonical = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert canonical.read_bytes() == claude.read_bytes()
    template = canonical.read_text(encoding="utf-8")
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
        assert field in template


def test_active_surface_sweep_includes_untracked_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    untracked = tmp_path / ".claude/agents/new.md"
    untracked.parent.mkdir(parents=True)
    untracked.write_text("active\n", encoding="utf-8")
    assert _active_files((".claude/agents",), {".md"}, tmp_path) == [untracked]


def test_active_surface_sweep_uses_nonempty_repository_files_only() -> None:
    instructions = _active_files(ACTIVE_INSTRUCTION_ROOTS, {".md", ".toml"})
    protocol = _active_files(ACTIVE_PROTOCOL_ROOTS, {".md", ".toml", ".py"})
    assert ROOT / "AGENTS.md" in instructions
    assert ROOT / "scripts/claude_task_connector.py" in protocol

    superpowers = {
        path.relative_to(ROOT).as_posix(): sorted(
            set(MANDATORY_SUPERPOWERS_RE.findall(path.read_text(encoding="utf-8")))
        )
        for path in instructions
        if MANDATORY_SUPERPOWERS_RE.search(path.read_text(encoding="utf-8"))
    }
    exact_triggers = {
        path.relative_to(ROOT).as_posix()
        for path in protocol
        if EXACT_NEXT_TRIGGER in path.read_text(encoding="utf-8")
    }
    assert superpowers == {}
    assert exact_triggers == set()
