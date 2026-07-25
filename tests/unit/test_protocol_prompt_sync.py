from __future__ import annotations

import re
import tomllib
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
MANDATORY_SUPERPOWERS_RE = re.compile(
    r"\bsuperpowers:[a-z0-9][a-z0-9-]*\b",
    re.IGNORECASE,
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


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
    paths: list[Path] = []
    for relative in ACTIVE_INSTRUCTION_ROOTS:
        root = ROOT / relative
        if root.is_file():
            paths.append(root)
        else:
            paths.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix in {".md", ".toml"}
            )

    violations = {
        path.relative_to(ROOT).as_posix(): sorted(
            set(MANDATORY_SUPERPOWERS_RE.findall(path.read_text(encoding="utf-8")))
        )
        for path in paths
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
    roots = (
        ROOT / ".agents",
        ROOT / ".claude",
        ROOT / ".codex",
        ROOT / "docs/protocol",
        ROOT / "scripts",
    )
    paths = [ROOT / "docs/PROGRAM-MANUAL.md"]
    for root in roots:
        paths.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix in {".md", ".toml", ".py"}
        )

    violations = {
        path.relative_to(ROOT).as_posix()
        for path in paths
        if "Exact Next Trigger" in path.read_text(encoding="utf-8")
    }
    assert violations == set()
