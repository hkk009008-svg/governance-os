from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]
CHATGPT_PRO_POINTER = (
    "Optional ChatGPT Pro consultation is parent-only and advisory: follow "
    ".agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol "
    "or side-effect authority."
)
CHATGPT_PRO_POINTER_SURFACES = (
    "AGENTS.md",
    "docs/protocol/codex/continuation.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    ".agents/skills/seat-director/SKILL.md",
    ".agents/skills/seat-operator/SKILL.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
    ".claude/agents/readiness-bridge.md",
    "docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md",
    "docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md",
    "docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md",
)
RETIRED_PROVIDER_PATHS = (
    "scripts/opus_review_bridge.py",
    "scripts/opus_review_receipts.py",
    "tests/unit/test_opus_review_bridge.py",
    "tests/unit/test_opus_review_receipts.py",
    "docs/protocol/codex/chatgpt-pro-consultation-acceptance.md",
    "scripts/prompts/opus_lane_v_advisory.md",
    (
        "scripts/prompts/"
        "opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json"
    ),
)
HISTORICAL_DECOMMISSION_PACKET = (
    "coordination/capacity/packets/"
    "2026-07-16-provider-tools-decommission-director-implementation.json"
)
HISTORICAL_DECOMMISSION_ACCEPTANCE = frozenset(
    {
        (
            "No ChatGPT Pro, Claude, Opus, provider CLI, in-app browser, paid API, "
            "provider retry, or provider receipt action is authorized."
        ),
        (
            "Commit, push, merge, provider launch, runtime cleanup, and external "
            "publication are separate authorities; this packet authorizes no push, "
            "merge, provider call, or cleanup."
        ),
    }
)
COMPACT_PAIR_REFERENCE = (
    "Canonical Compact Pair Invariant: scripts/codex_protocol_model.py"
)
COMPACT_PAIR_SURFACES = (
    "AGENTS.md",
    "docs/protocol/codex/continuation.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    ".agents/skills/seat-director/SKILL.md",
    ".agents/skills/seat-operator/SKILL.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
    ".agents/skills/seat-operator/verification-report-format.md",
    ".claude/skills/seat-operator/verification-report-format.md",
    ".codex/agents/lane-v-verifier.toml",
    ".claude/agents/lane-v-verifier.md",
)
COMPACT_PAIR_CORE_SURFACES = COMPACT_PAIR_SURFACES[:10]
AUTONOMOUS_REFERENCE = (
    "Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py"
)
AUTONOMOUS_SURFACES = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/protocol/codex/continuation.md",
    "docs/protocol/claude/continuation.md",
    "docs/protocol/claude/independence-first.md",
    "docs/protocol/agents/orchestration.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    ".agents/skills/seat-director/SKILL.md",
    ".agents/skills/seat-operator/SKILL.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
    ".codex/agents/agent01.toml",
    ".codex/agents/lane-v-verifier.toml",
    ".claude/skills/four-seat-protocol/SKILL.md",
    ".claude/skills/seat-director/SKILL.md",
    ".claude/skills/seat-operator/SKILL.md",
    ".claude/skills/seat-coordinator/SKILL.md",
    ".claude/agents/readiness-bridge.md",
    ".claude/agents/lane-v-verifier.md",
)
GENERIC_AUTHORITY_STATEMENTS = (
    (
        "Mailbox decisions remain body-first: read relevant mailbox bodies before "
        "acting; live seat cursors are intentional per-seat state, and the "
        "coordinator has no cursor."
    ),
    (
        "The verifying operator must be a non-author and alone issues GO/NITS/FAIL "
        "from repository evidence."
    ),
    (
        "The coordinator may route and reconcile but not author behavior-changing "
        "production fixes."
    ),
    (
        "Push, merge, paid spend, and every other side effect are separately gated "
        "and require explicit authority."
    ),
)
DECISIONS_PRE_TASK5_PREFIX_BYTES = 57_646
DECISIONS_PRE_TASK5_PREFIX_SHA256 = (
    "3f09b44a053200daf337d6227c9578907137bf1d17e41f5e18e13bb7686f63de"
)
REQUIRED_REVIEWER_TEMPLATE_HEADINGS = (
    "# Reviewer prompt template - agent-neutral",
    "## Canonical verdict vocabulary",
    "## Independence + verify-before-asserting",
    "## Git hygiene",
    "## RESULT SCHEMA",
    "## Evidence preamble",
    "## Spec reviewer prompt template",
    "## Code quality reviewer prompt template",
)


def test_compact_chatgpt_tool_is_installed_and_each_surface_points_once():
    assert (ROOT / "scripts/chatgpt_pro_consult.py").is_file()
    assert (ROOT / ".agents/skills/chatgpt-pro-consultation/SKILL.md").is_file()
    for relative in CHATGPT_PRO_POINTER_SURFACES:
        assert _read(relative).count(CHATGPT_PRO_POINTER) == 1, relative


def test_retired_provider_paths_remain_absent():
    for relative in RETIRED_PROVIDER_PATHS:
        assert not (ROOT / relative).exists(), relative


def test_historical_decommission_packet_remains_present():
    packet = json.loads(_read(HISTORICAL_DECOMMISSION_PACKET))

    assert packet["cycle"] == "provider-tools-targeted-decommission-2026-07-16"
    assert packet["status"] == "done"
    assert HISTORICAL_DECOMMISSION_ACCEPTANCE.issubset(set(packet["acceptance"]))


def test_lifecycle_is_canonical_not_mirrored():
    for relative in CHATGPT_PRO_POINTER_SURFACES:
        text = _read(relative)
        assert "created:true" not in text, relative
        assert "reserved -> sent" not in text, relative
        assert "fresh empty chat" not in text, relative


def test_autonomous_contract_is_model_backed_and_adapters_are_thin() -> None:
    rendered = model.render_autonomous_seat_contract()
    for phrase in (
        "own the outcome",
        "choose the method",
        "ownership change",
        "without coordinator approval",
        "FINDING is not BLOCKED",
        "non-author Operator GO",
        "different reviewer model",
        "immutable parent and revision",
        "finding refs",
        "external effect",
    ):
        assert phrase.casefold() in rendered.casefold()

    forbidden_copies = (
        "Capacity Split Default:",
        "Subagent utilization decision",
        "2-cycle escalation limit",
        "coordinator owns convergence",
        "stop_if_newer_mail_or_live_target_satisfied",
    )
    for path in AUTONOMOUS_SURFACES:
        text = _read(path)
        assert _compact(text.replace("`", "")).count(AUTONOMOUS_REFERENCE) == 1
        for phrase in forbidden_copies:
            assert phrase not in text, (path, phrase)


def test_active_seat_adapter_line_budgets_prevent_protocol_regrowth() -> None:
    budgets = {
        "AGENTS.md": 210,
        "CLAUDE.md": 220,
        "docs/protocol/codex/continuation.md": 220,
        "docs/protocol/claude/continuation.md": 220,
        ".agents/skills/four-seat-protocol/SKILL.md": 100,
        ".agents/skills/seat-director/SKILL.md": 130,
        ".agents/skills/seat-operator/SKILL.md": 130,
        ".agents/skills/seat-coordinator/SKILL.md": 130,
        ".claude/skills/four-seat-protocol/SKILL.md": 100,
        ".claude/skills/seat-director/SKILL.md": 130,
        ".claude/skills/seat-operator/SKILL.md": 130,
        ".claude/skills/seat-coordinator/SKILL.md": 130,
    }
    for path, maximum in budgets.items():
        assert len(_read(path).splitlines()) <= maximum, path


def test_r_independence_truth_is_owner_assessment_plus_actual_diff_review() -> None:
    architecture = _compact(_read("ARCHITECTURE.md"))
    rendered = model.render_r_independence()

    for text in (architecture, rendered):
        assert "owner" in text.casefold()
        assert "plausible abuse classes" in text
        assert "material independent findings" in text
        assert "actual-diff" in text
        assert "distinct" in text
        assert "different" in text
        assert "Operator" in text

    assert "requires a durable independent design-time enumeration" not in architecture
    assert "early independent" in architecture.casefold()
    assert "advisory" in architecture.casefold()
    assert "not a universal requirement or CLEAR gate" in architecture


def test_capacity_board_is_optional_diagnostic_not_route_authority() -> None:
    architecture = _compact(_read("ARCHITECTURE.md"))
    source = _read("scripts/codex_protocol_model.py")
    coordinator = " ".join(model.COORDINATOR_INVARIANTS)
    live_loop = " ".join(model.LIVE_LOOP_STEPS)
    summary = model.render_surface_summary()

    required = "optional diagnostic evidence"
    assert required in architecture
    assert required in dict(model.ACTIVE_KERNEL_INVARIANTS)["capacity diagnostics"]
    assert "route and hard-boundary validation" in architecture

    forbidden = (
        "capacity-board route validation before any active coordinator task-board route",
        "Before any active coordinator task-board route",
        "fix named gate failures before committing the route",
        "route is valid only when",
    )
    for phrase in forbidden:
        assert phrase not in coordinator
        assert phrase not in live_loop
        assert phrase not in summary
        assert phrase not in architecture

    assert "protocol_capacity_board.py --wave <wave> --validate-route" not in source


def test_compact_production_line_budget():
    kernel_lines = _read("scripts/chatgpt_pro_consult.py").splitlines()
    skill_lines = _read(
        ".agents/skills/chatgpt-pro-consultation/SKILL.md"
    ).splitlines()
    assert len(kernel_lines) <= 250
    assert len(skill_lines) <= 100
    assert len(kernel_lines) + len(skill_lines) <= 350


def test_protocol_model_has_no_chatgpt_consultation_contract() -> None:
    source = (ROOT / "scripts/codex_protocol_model.py").read_text(encoding="utf-8")
    forbidden = (
        "render_" "chatgpt_pro_consultation",
        "chatgpt_pro_" "consultation_default",
        "validate_" "chatgpt_pro_activation_evidence",
        "chatgpt_pro_" "guard_manifest_hash",
    )
    assert all(token not in source for token in forbidden)


def test_threeway_dual_chief_contract_remains_provider_neutral_and_two_input() -> None:
    doctrine = _read("docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md")
    adoption = _read("docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md")
    diagram = _read("docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md")
    onboarding = _read("docs/protocol/threeway/ONBOARDING.md")

    assert (
        "| dual chief | two separately approved, human-relayed external "
        "advisory apps |"
    ) in doctrine
    assert "The dual chief comprises two separately approved" in adoption
    assert "Dual Chief<br/>Two Separately Approved External Advisory Apps" in diagram
    assert "Antigravity holds NO Layer-1 seat and is NOT the dual chief" in onboarding

    for text in (doctrine, adoption, diagram, onboarding):
        assert "Gemini Deep Think + ChatGPT Pro" not in text


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


FAST_RESUME_ADAPTER_SURFACES = (
    "AGENTS.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    "docs/protocol/codex/continuation.md",
    "docs/protocol/codex/ledger-cli-adoption.md",
)

AUTOMATIC_TASK_ROUTING_REFERENCE = (
    "Automatic Seat-Task Routing: scripts/codex_protocol_model.py"
)
AUTOMATIC_TASK_ROUTING_SURFACES = (
    "AGENTS.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    "docs/protocol/codex/continuation.md",
)


def test_automatic_task_routing_model_is_direct_deduplicated_and_effect_free() -> None:
    rendered = _compact(model.render_automatic_task_routing())

    required = (
        "committed immutable trigger",
        "dispatch identity",
        "already in progress",
        "monitor",
        "automatically create",
        "Never ask the user to relay",
        "concrete live-seat Codex task",
        "tooling blocker",
        "grants no external-effect authority",
    )
    for phrase in required:
        assert phrase.casefold() in rendered.casefold(), phrase

    assert "persistent task registry" not in rendered
    assert "parent-scoped subagent may issue GO" not in rendered


def test_automatic_task_routing_adapters_are_thin_and_synced() -> None:
    required = (
        "discover/deduplicate",
        "reuse one compatible task",
        "automatically create a fresh missing task",
        "send the exact trigger",
        "wait",
        "reconcile",
        "Never ask the user to relay a seat prompt",
        "grants no seat or external-effect authority",
    )
    for path in AUTOMATIC_TASK_ROUTING_SURFACES:
        text = _compact(_read(path).replace("`", ""))
        assert text.count(AUTOMATIC_TASK_ROUTING_REFERENCE) == 1, path
        for phrase in required:
            assert phrase.casefold() in text.casefold(), (path, phrase)


def test_fast_resume_adapter_rules_are_thin_truthful_and_authority_free() -> None:
    for path in FAST_RESUME_ADAPTER_SURFACES:
        text = _compact(_read(path).replace("`", ""))
        for phrase in (
            "fresh, transplanted, ambiguous, or external-effect work",
            "unchanged already-routed local implementation or review",
            "exact current route ref",
            "FAST RESUME: PASS",
            "FULL ORIENTATION REQUIRED",
            "START GUARD: FAIL",
            "advisory fallback",
            "not BLOCKED",
            "no external-effect authority",
        ):
            assert phrase.casefold() in text.casefold(), (path, phrase)

        for duplicated_checklist_detail in (
            "target-dirty-outside-allowed-paths",
            "expected-route-body-mismatch",
            "mailbox-unavailable",
            "route-candidate-issue",
        ):
            assert duplicated_checklist_detail not in text, (
                path,
                duplicated_checklist_detail,
            )


def test_ledger_adoption_names_canonical_resume_source_and_command_once() -> None:
    text = _read("docs/protocol/codex/ledger-cli-adoption.md")
    command = model.LEDGER_CLI_BRIDGE["guard_resume_command"]

    assert "scripts/codex_protocol_model.py" in text
    assert "LEDGER_CLI_BRIDGE" in text
    assert text.count(command) == 1


def _trigger_contract_text(path: str) -> str:
    return _compact(_read(path).replace("`", ""))


VERIFY_REQUEST_TRIGGER_FRAGMENTS = (
    "one committed verify-request",
    "full reviewed base/head",
    "author seat/model",
    "assigned Operator",
    "question",
    "allowed paths",
    "commands",
)
INVALID_TRIGGER_FRAGMENTS = (
    "Missing, duplicated, abbreviated, uppercase, uncommitted, or mismatched",
    "not authority",
    "stop with a blocker",
)
TASK8_TRIGGER_FRAGMENT_CATEGORIES = (
    ("lawful verify-request production", VERIFY_REQUEST_TRIGGER_FRAGMENTS),
    ("invalid-trigger fail-closed", INVALID_TRIGGER_FRAGMENTS),
)


def test_agent_neutral_reviewer_template_exists_with_schema():
    text = _read("docs/templates/agents/reviewer.md")

    assert "schema_version" in text
    assert "reviewer-result/1" in text
    assert '"verdict": "pass | issues | unable_to_verify"' in text
    assert "env -u GIT_INDEX_FILE" in text


def test_agent_neutral_reviewer_template_keeps_required_plan_headings():
    text = _read("docs/templates/agents/reviewer.md")
    normalized = text.replace("—", "-")

    for heading in REQUIRED_REVIEWER_TEMPLATE_HEADINGS:
        assert heading in normalized


def retired_codex_director_skill_uses_agent_neutral_templates():
    for path in (
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-director/r-brief-template.md",
        ".agents/skills/seat-operator/SKILL.md",
    ):
        text = _read(path)
        assert "docs/templates/agents/" in text
        assert "docs/protocol/agents/orchestration.md" in text
        assert "docs/templates/claude/implementer.md" not in text
        assert "docs/templates/claude/reviewer.md" not in text
        assert "docs/protocol/claude/orchestration.md" not in text


def retired_claude_function_harmonization_is_model_backed_and_documented():
    rendered = model.render_claude_function_harmonization()

    required_phrases = (
        "Claude Function Harmonization:",
        "adapt Claude functions to Codex-native primitives",
        "do not transplant Claude-only mechanics",
        "AskUserQuestion discipline",
        "background work discipline",
        "dispatch-template minimalism",
        "reviewer evidence rigor",
        "adversarial verification",
    )
    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
    ):
        text = _read(path)
        for phrase in required_phrases:
            assert phrase in text


def test_reviewer_template_adopts_claude_evidence_rigor_without_claude_mechanics():
    text = _read("docs/templates/agents/reviewer.md")

    for reason in ("U1", "U2", "U3", "U4", "U5"):
        assert reason in text
    assert "reviewed_head != reviewed_commit" in text
    assert "working_tree_clean=false" in text
    assert "--runxfail" in text
    assert "Execute touched scripts or hooks" in text
    assert "Do not cite Claude-only tool syntax" in text


def retired_codex_specialist_agents_require_adversarial_proof_loop():
    for path in (
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
    ):
        text = _read(path)
        assert "Adversarial proof loop" in text
        assert "try to make the gate or proof fail" in text
        assert "unable_to_verify" in text


def test_codex_facing_prompts_name_pipeline_not_content():
    paths = [
        ".agents/skills/four-seat-protocol/SKILL.md",
        *sorted(
            str(path.relative_to(ROOT))
            for path in (ROOT / ".codex" / "agents").glob("*.toml")
        ),
    ]

    for path in paths:
        text = _read(path)
        assert "Content four-seat process" not in text
        assert "Content repo's four-seat protocol" not in text
        assert "Content repo" not in text


def test_live_seat_behavior_sources_use_director_and_operator2_defaults():
    assert model.SEAT_BEHAVIOR_SOURCE == {
        "director": "director",
        "director2": "director",
        "operator": "operator2",
        "operator2": "operator2",
    }

    expected_map = (
        "Behavior source map: `director -> director`, `director2 -> director`, "
        "`operator -> operator2`, `operator2 -> operator2`."
    )
    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
    ):
        assert expected_map in _read(path)

    director_prompt = _read(".codex/agents/protocol-director.toml")
    operator_prompt = _read(".codex/agents/protocol-operator.toml")
    assert "Canonical behavior source: `director` for both `director` and `director2`" in director_prompt
    assert "Canonical behavior source: `operator2` for both `operator` and `operator2`" in operator_prompt

    threeway_adoption = _read("docs/protocol/threeway/CODEX-ADOPTION.md")
    assert "behavior source is `director`" in threeway_adoption
    assert "behavior source `operator2`" in threeway_adoption


def retired_subagent_utilization_decision_is_rendered_and_documented():
    rendered = model.render_seat_subagent_development()
    assert "Subagent utilization decision" in rendered
    assert "direct/no-op because" in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
    ):
        text = _read(path)
        assert "Subagent utilization decision" in text
        assert "direct/no-op because" in text


def retired_codex_execution_tiers_are_model_backed_and_surface_synced():
    expected = (
        (
            "tier-0-conversational",
            "self-contained answer",
            "no repo orientation, implementation skills, mailbox checks, "
            "smoke, worktree, or verification commands",
        ),
        (
            "tier-1-read-only",
            "repository inspection or evidence-backed report",
            "smallest scoped read commands; no implementation skills or "
            "live-seat checks without an explicit protocol trigger",
        ),
        (
            "tier-2-local-mutation",
            "ordinary code, test, config, or documentation edit",
            "impact analysis, task-relevant implementation discipline, focused "
            "tests, and one completion verification pass",
        ),
        (
            "tier-3-governed-side-effect",
            "live-seat decision, shared protocol state, or external side effect",
            "exact mailbox, capacity, independent-verification, and "
            "user-authorization gates",
        ),
    )

    assert model.CODEX_EXECUTION_TIERS == expected
    rendered = model.render_codex_execution_tiers()
    for tier in expected:
        assert all(value in rendered for value in tier)
    assert "unchanged HEAD and unchanged relevant paths" in rendered
    assert "same unchanged commit" in rendered
    assert "Deterministic artifact evidence may be reused" in rendered
    assert "Tier 3 requires fresh signed-bus, mailbox/cursor, lock, approval" in rendered
    assert "reuse never relaxes a triggered guard" in rendered

    for path in ("AGENTS.md", "docs/protocol/codex/continuation.md"):
        text = _compact(_read(path))
        for tier, _, _ in expected:
            assert tier in text
        assert "same unchanged commit" in text
        assert "Deterministic artifact evidence may be reused" in text
        assert "Tier 3 requires fresh signed-bus, mailbox/cursor, lock, approval" in text
        assert "reuse never relaxes a triggered guard" in text


def test_r_independence_is_model_backed_and_surface_synced():
    assert model.R_INDEPENDENCE_TRIGGER_SURFACES == (
        "input rendered or composed into a parseable or executable context",
        "authority or security-boundary enforcement",
        "side-effect gating",
        "schema validation whose acceptance grants trust",
    )

    rendered = model.render_r_independence()
    required = (
        "R-INDEPENDENCE",
        "standing default",
        "plausible abuse classes",
        "coverage targets",
        "proportional review depth",
        "advisory",
        "no universal pre-implementation CLEAR gate",
        "distinct non-author Operator seat",
        "different system-visible model",
        "actual diff or range",
        "fixed mailbox writer",
        "R-VERIFY-TIER",
        "docs/protocol/claude/independence-first.md",
    )
    for phrase in required:
        assert phrase in rendered

    shared_surface_phrases = ("plausible abuse classes", "proportional review depth")
    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/claude/independence-first.md",
    ):
        text = _compact(_read(path))
        for phrase in shared_surface_phrases:
            assert phrase in text, (path, phrase)

    assert "R-INDEPENDENCE" in model.render_start_session_inhabitance()


def test_agent_extension_routing_contract_is_model_backed():
    expected_contract = (
        (
            "agent01",
            "capacity manager companion",
            "explicit coordinator/cycle capacity-max planning",
        ),
        (
            "agent02",
            "explicit-mode bounded worker",
            "a parent names a concrete mode and allowed write set",
        ),
        (
            "agent03",
            "general senior repo worker",
            "ordinary repo coding or documentation work with protocol awareness",
        ),
        (
            "agent04",
            "read-only protocol auditor/router",
            "read-only protocol diagnosis and route recommendation",
        ),
    )

    assert model.AGENT_EXTENSION_ROUTING_CONTRACT == expected_contract

    rendered = model.render_agent_extension_routing_contract()
    assert "Agent Extension Routing Contract:" in rendered
    for agent, purpose, route_when in expected_contract:
        assert agent in rendered
        assert purpose in rendered
        assert route_when in rendered

    assert "extension output is evidence for the parent" in rendered
    assert "not a mailbox event, cursor advance, operator GO, coordinator route, lock action, push, or spend authorization" in rendered


def retired_agentnn_extensions_have_distinct_routing_prompts():
    expected = {
        "agent01": (
            "capacity manager companion",
            "explicit coordinator/cycle capacity-max planning",
            "build all-seat awareness",
        ),
        "agent02": (
            "explicit-mode bounded worker",
            "a parent names a concrete mode and allowed write set",
            "bounded protocol edits, handoffs, mailbox/cursor maintenance, or Codex agent/config edits",
        ),
        "agent03": (
            "general senior repo worker",
            "ordinary repo coding or documentation work with protocol awareness",
            "defaults to readiness-bridge posture when no live role is named",
        ),
        "agent04": (
            "read-only protocol auditor/router",
            "read-only protocol diagnosis and route recommendation",
            "diagnose stale indexes, mailbox drift, routing gaps, gate/readiness evidence, and authority mismatches",
        ),
    }

    assert dict(
        (agent, (purpose, route_when))
        for agent, purpose, route_when in model.AGENT_EXTENSION_ROUTING_CONTRACT
    ) == {
        agent: values[:2]
        for agent, values in expected.items()
    }

    for agent, phrases in expected.items():
        text = _compact(_read(f".codex/agents/{agent}.toml"))
        for phrase in phrases:
            assert phrase in text


def retired_agentnn_extensions_keep_no_seat_authority_boundary():
    required_phrases = (
        "extension, not a protocol seat",
        "cannot consume cursors, send mailbox events, issue GO, create coordinator routes, claim locks, push, start pods, or spend paid API budget",
        "authority work routes to `protocol-director`, `protocol-operator`, or `protocol-coordinator`",
        "extension output is evidence for the parent",
    )

    for agent in ("agent01", "agent02", "agent03", "agent04"):
        text = _compact(_read(f".codex/agents/{agent}.toml"))
        for phrase in required_phrases:
            assert phrase in text


def test_agent04_uses_artifact_neutral_capacity_language():
    text = _read(".codex/agents/agent04.toml")

    assert "target proof artifacts" in text
    assert "co-sign or target-proof review" in text
    assert "product-oracle status" not in text
    assert "co-sign/product-oracle review" not in text


def retired_capacity_split_default_is_model_backed_and_surface_synced():
    rendered = model.render_capacity_split_default()

    required_phrases = (
        "Capacity Split Default:",
        "single-pair fast path remains the default for narrow or shared-file work",
        "divisible or preplanned larger work defaults to dual-pair routing",
        "two independently reviewable deliverables",
        "director owns Chunk A and operator verifies Chunk A",
        "director2 owns Chunk B and operator2 verifies Chunk B",
        "Pair B performs bounded planning or preflight instead of idle standby",
        "Pair B preflight packets use `director-preflight` and `operator-preflight` packet types",
        "coordinator owns convergence",
    )

    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/agent01.toml",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def retired_side_effect_executor_token_contract_is_model_backed_and_documented():
    rendered = model.render_side_effect_executor_contract()

    required_phrases = (
        "Side-Effect Executor Token:",
        "side_effect_id",
        "allowed_command_class",
        "stop_if_newer_mail_or_live_target_satisfied",
        "observer seats default to observer mode",
        "generic user approval is unit consent, not executor election",
        "live evidence may close an already-satisfied side effect",
    )
    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _read(path)
        for phrase in required_phrases:
            assert phrase in text


def retired_side_effect_executor_token_detailed_contract_is_surface_synced():
    rendered = model.render_side_effect_executor_contract()
    detailed_phrases = (
        "shared user-gated side effects need exactly one named executor",
        "side effects covered: remote-ref update",
        "multiple same-target side-effect success claims need a common side_effect_id",
        "report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request",
    )
    for phrase in detailed_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _read(path)
        for phrase in detailed_phrases:
            assert phrase in text


def test_optional_codex_agent_selection_matrix_exists():
    text = _read(".codex/agents/README.md")

    for phrase in (
        "Optional Agent Selection Matrix",
        "agent01",
        "agent02",
        "agent03",
        "agent04",
        "These agents do not replace protocol-director, protocol-operator, or protocol-coordinator.",
    ):
        assert phrase in text


def retired_rule_12_pattern_reference_transplant_is_surface_synced():
    required_phrases = (
        "brief-pattern references are runtime claims when they cite canonical sites",
        "verify the named symbol exists at the cited SHA",
        "verify the cited SHA exhibits the named sub-pattern",
    )

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        ".agents/skills/seat-director/SKILL.md",
        "docs/templates/agents/implementer.md",
        "docs/templates/claude/implementer.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def retired_rule_13_disposition_transplant_is_surface_synced():
    required_phrases = (
        "audit-completeness is not audit-disposition",
        "mirror / defer / document / exempt",
        "state the disposition for each sibling",
    )

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-director/r-brief-template.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_pattern_doc_uniformity_transplant_is_surface_synced():
    required_phrases = (
        "pattern-doc uniformity pass",
        "cumulative production sites cross 20",
        "per-site detail drift",
    )

    for path in (
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/templates/agents/implementer.md",
        "docs/templates/claude/implementer.md",
        "docs/PROTOCOL-RULES-LOG.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def retired_emergency_and_disagreement_contracts_are_model_backed_and_synced():
    emergency_rendered = model.render_emergency_handling_contract()
    disagreement_rendered = model.render_disagreement_handling_contract()

    emergency_phrases = (
        "Production-affecting OR user-data-integrity issue",
        "Security-critical",
        "Active bleed-rate",
        "External time-pressure",
        "first-noticer claims initial response",
        "stop-the-bleed first",
        "acting under v5 §E temporary authority",
        "coordinator no-production-code boundary remains in force",
        "post-incident note",
    )
    disagreement_phrases = (
        "States the disagreement explicitly",
        "project-data-grounded evidence",
        "counter-refinement",
        "defer to v(N+1)",
        "acceptance criterion",
        "silent-accept is the receiver's own acceptance",
        "2-cycle escalation limit",
    )

    for phrase in emergency_phrases:
        assert phrase in emergency_rendered
    for phrase in disagreement_phrases:
        assert phrase in disagreement_rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _compact(_read(path))
        for phrase in (*emergency_phrases, *disagreement_phrases):
            assert phrase in text


def retired_blocked_wave_and_acting_coordinator_contract_is_model_backed_and_synced():
    rendered = model.render_blocked_wave_acting_coordinator_contract()
    required_phrases = (
        "wave-gate evidence before asserting blocked",
        "immediate pod-off when a director gate-request is unserviced",
        "one consolidated mailbox event naming blocker, owner, and SLA",
        "escalate to user with the acting-coordinator path",
        "pre-brief skeleton only",
        "no gate-relaxing or suppressive pins",
        "verified only from operator GO",
    )

    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-coordinator.toml",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def retired_reviewer_result_handling_contract_is_model_backed_and_synced():
    rendered = model.render_reviewer_result_handling_contract()
    required_phrases = (
        "findings-first ordering by severity",
        "preserve verdict, findings, and next steps",
        "separate uncertainty, inference, and follow-up",
        "do not auto-fix after a review",
        "failed, incomplete, or unable_to_verify runs are not permission to invent substitute output",
    )

    for phrase in required_phrases:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
        "docs/templates/agents/reviewer.md",
        "docs/templates/agents/implementer.md",
    ):
        text = _compact(_read(path))
        for phrase in required_phrases:
            assert phrase in text


def test_compact_pair_is_model_backed_and_surface_synced():
    rendered = model.render_lane_v_v3()
    required = (
        "Compact Pair Invariant",
        "one committed verify-request",
        "reviewed base/head",
        "outcome",
        "author seat and system-visible author model",
        "assigned non-author Operator",
        "allowed paths",
        "immutable finding refs",
        "different reviewer model",
        "explicitly dispositions every finding ref",
        "mailbox bodies before acting",
        "live seat cursors are intentional per-seat state",
        "coordinator has no cursor",
        "non-author",
        "GO/NITS/FAIL",
        "fixed mailbox writer",
        "coordinator may route and reconcile but not author behavior-changing production fixes",
        "push, merge, paid spend, and every other side effect are separately gated",
    )
    for phrase in required:
        assert phrase in rendered

    for path in (
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
    ):
        assert COMPACT_PAIR_REFERENCE in _compact(_read(path).replace("`", "")), path

    invariants = dict(model.ACTIVE_KERNEL_INVARIANTS)
    assert "merge" in invariants["user-gated side effects"]
    assert "separately gated" in invariants["separate side-effect gates"]

    source = _read("scripts/codex_protocol_model.py")
    assert "CROSS_MODEL_VERIFICATION_RULES" not in source
    assert "render_cross_model_verification" not in source

    hooks = _read(".codex/hooks.json")
    assert "verification_report_gate" not in hooks


@pytest.mark.parametrize(
    ("renderer_name", "rendered"),
    (
        ("render_runtime_env_contract", model.render_runtime_env_contract({})),
        ("render_seat_contract", model.render_seat_contract({})),
    ),
)
def test_executable_contract_renderers_separately_gate_merge(
    renderer_name: str,
    rendered: str,
) -> None:
    normalized = rendered.lower()
    assert "merge" in normalized, renderer_name
    assert "separately gated" in normalized, renderer_name
    assert "user consent" in normalized, renderer_name


def test_lane_v_trigger_producer_contract_is_surface_synced() -> None:
    producer_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "docs/PROGRAM-MANUAL.md",
        "scripts/codex_protocol_model.py",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/protocol/claude/continuation.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".codex/agents/protocol-director.toml",
    )

    for path in producer_paths:
        text = _trigger_contract_text(path)
        assert COMPACT_PAIR_REFERENCE in text, path


def test_lane_v_trigger_consumer_contract_is_surface_synced() -> None:
    consumer_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "docs/PROGRAM-MANUAL.md",
        "scripts/codex_protocol_model.py",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/protocol/claude/continuation.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
    )

    for path in consumer_paths:
        text = _trigger_contract_text(path)
        assert COMPACT_PAIR_REFERENCE in text, path


def retired_lane_v_trigger_renderers_include_every_task8_contract_category() -> None:
    rendered_outputs = (
        ("render_pair_operating_contract", model.render_pair_operating_contract()),
        (
            "render_lane_v_v3",
            model.render_lane_v_v3(),
        ),
    )

    for renderer_name, rendered in rendered_outputs:
        text = _compact(rendered.replace("`", ""))
        for category, fragments in TASK8_TRIGGER_FRAGMENT_CATEGORIES:
            for fragment in fragments:
                assert fragment in text, (renderer_name, category, fragment)


def retired_lane_v_active_surfaces_remove_commit_only_and_prose_only_substitutes() -> None:
    rendered_pair = model.render_pair_operating_contract()
    rendered_lane_v = model.render_lane_v_v3()
    stale_model_phrases = (
        "operator verifies only that artifact or landed commit",
        "include commit/range, brief path",
        "Operator waits for a fresh verify-request or shipping commit",
        "Lane-V-Scope",
        "TaskPublicationStore",
    )
    for phrase in stale_model_phrases:
        assert phrase not in rendered_pair
        assert phrase not in rendered_lane_v

    active_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "docs/PROGRAM-MANUAL.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
        "docs/protocol/claude/continuation.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
    )
    stale_surface_phrases = (
        "send one verify-request to operator with commit/range, tests, and exclusions",
        "verify only the named verify-request or shipping commit/range",
        "Fresh verify-request naming a commit/range, scope",
        "Lane-V-Scope",
        "TaskPublicationStore",
    )
    for path in active_paths:
        text = _trigger_contract_text(path)
        for phrase in stale_surface_phrases:
            assert phrase not in text, (path, phrase)

    for path in (
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/reviewer.md",
    ):
        assert "the only sanctioned trailer" not in _read(path), path


def test_implementer_and_reviewer_templates_never_invent_trigger_authority() -> None:
    implementer_paths = (
        "docs/templates/agents/implementer.md",
        "docs/templates/claude/implementer.md",
    )
    reviewer_paths = (
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/reviewer.md",
    )
    for path in implementer_paths:
        text = _trigger_contract_text(path)
        assert "never invent trigger authority" in text, path

    for path in reviewer_paths:
        text = _trigger_contract_text(path)
        assert "a named commit or prose-only event is not trigger authority" in text, path
        assert "never invent trigger authority" in text, path


def test_lane_v_trigger_guidance_pins_compact_report_and_pipeline_boundary() -> None:
    report_paths = (
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
    )
    for path in report_paths:
        text = _read(path)
        assert "Event type: verification-report" in text, path
        assert "Verification request:" in text, path
        assert "Reviewer seat:" in text, path
        assert "Reviewer model:" in text, path
        assert "Verification harness:" in text, path
        assert "Verification context:" in text, path
        assert "## Allowed Paths" in text, path
        assert "--receipt-id" not in text, path
        assert "provider process" not in text, path

    verifier = _trigger_contract_text(".codex/agents/lane-v-verifier.toml")
    assert COMPACT_PAIR_REFERENCE in verifier
    assert "--receipt-id" not in verifier

    agent_report = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude_report = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert agent_report.read_bytes() == claude_report.read_bytes()


def retired_active_codex_operator_prompts_drop_descriptor_v3_contract() -> None:
    operator = _trigger_contract_text(".codex/agents/protocol-operator.toml")
    verifier_raw = _read(".codex/agents/lane-v-verifier.toml")
    verifier = _trigger_contract_text(".codex/agents/lane-v-verifier.toml")

    assert "resolve one trigger-bound committed lane-v-scope/v1 descriptor" not in operator
    assert "require the exact ordered lane-v-report/v3 block" not in operator
    assert "against the descriptor" not in verifier_raw
    assert verifier.count(COMPACT_PAIR_REFERENCE) == 1

    required = (
        "one assigned committed verify-request",
        "Verification request: canonical committed request path@full request commit",
        "Reviewed head and Reviewed base: exact full lowercase SHAs from the request",
        "assigned non-author Operator seat",
        "Reviewer model: actual model identity, different from the author model",
        "Verification harness and Verification context",
        "Allowed Paths exactly matching the request",
        "GO / NITS / FAIL",
        "coordination/bin/send-event",
    )
    for phrase in required:
        assert phrase in operator, phrase
        assert phrase in verifier, phrase


def retired_active_surfaces_continue_internally_without_terminal_heading_ceremony() -> None:
    active_paths = (
        "scripts/codex_protocol_model.py",
        "docs/PROGRAM-MANUAL.md",
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-coordinator/SKILL.md",
    )
    required = (
        "Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.",
        "At a real stop, state the blocking boundary or plain next authority without a prescribed heading or returning seat commands to the user.",
    )
    retired = (
        "Every live-seat/coordinator turn ends with",
        "Before ending any live-seat/coordinator turn",
        "every coordinator turn ends with",
        "must end with Exact Next Trigger",
    )
    for path in active_paths:
        text = _compact(_read(path))
        for phrase in required:
            assert phrase in text, (path, phrase)
        for phrase in retired:
            assert phrase not in text, (path, phrase)


def test_active_protocol_surfaces_have_no_exact_next_trigger_prescription() -> None:
    roots = (
        ROOT / ".agents",
        ROOT / ".claude",
        ROOT / ".codex",
        ROOT / "docs/protocol",
        ROOT / "scripts",
    )
    active_paths = [ROOT / "docs/PROGRAM-MANUAL.md"]
    for root in roots:
        active_paths.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix in {".md", ".toml", ".py"}
        )

    matches = {
        path.relative_to(ROOT).as_posix(): [
            line_number
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            )
            if "Exact Next Trigger" in line
        ]
        for path in active_paths
    }
    assert not {path: lines for path, lines in matches.items() if lines}


def test_task8_scope_covers_the_exact_trigger_authority_generation() -> None:
    descriptor_path = (
        "coordination/verification/scopes/"
        "2a876e95-3a87-4203-a613-1a29dd957b5b.json"
    )
    descriptor_raw = (ROOT / descriptor_path).read_bytes()
    descriptor = json.loads(descriptor_raw)
    old_digest = "74d50ded74c017c614fb6a746231e0f910ac28d247c9ad728c099f71d2aa8ffe"
    task7_digest = "c16aa28ce9211e7214ba8fb5586059515a8a59de3b37a0f853c6e13da73d5a93"
    current_digest = "e393655f4ba9ad0dcfa0467fcc54c809c79a1b28b76a2022a7d846acc8996e84"

    expected_roots = (
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator",
        ".claude/agents/lane-v-verifier.md",
        ".claude/skills/seat-director/SKILL.md",
        ".claude/skills/seat-operator",
        ".codex/agents",
        ".github/workflows/ci.yml",
        ".gitignore",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "DECISIONS.md",
        "RUNBOOK-DAILY.md",
        "coordination/README.md",
        "coordination/bin/send-event",
        "coordination/verification/scopes",
        "docs/PROGRAM-MANUAL.md",
        "docs/PROTOCOL-RULES-LOG.md",
        "docs/protocol",
        "docs/superpowers/plans",
        "docs/superpowers/specs",
        "docs/templates/agents/implementer.md",
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/implementer.md",
        "docs/templates/claude/reviewer.md",
        "scripts",
        "tests/unit",
    )
    expected_focused_command = (
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
        "tests/unit/test_opus_review_receipts.py "
        "tests/unit/test_opus_review_bridge.py "
        "tests/unit/test_check_go_schema.py "
        "tests/unit/test_verification_report_gate.py "
        "tests/unit/test_coordination_tooling.py "
        "tests/unit/test_protocol_prompt_sync.py "
        "tests/unit/test_protocol_capacity.py "
        "tests/unit/test_protocol_doc_integrity.py -q"
    )

    assert descriptor["allowed_path_roots"] == list(expected_roots)
    assert descriptor["allowed_path_roots"] == sorted(descriptor["allowed_path_roots"])
    assert descriptor["verification_commands"][0] == expected_focused_command
    for broad_substitute in (".agents/skills", ".claude/agents", ".claude/skills", "docs"):
        assert broad_substitute not in descriptor["allowed_path_roots"]
    assert hashlib.sha256(descriptor_raw).hexdigest() == current_digest

    plan = _read(
        "docs/superpowers/plans/2026-07-13-opus-lanev-receipt-hardening.md"
    )
    design = _read(
        "docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md"
    )
    compact_plan = _compact(plan)
    compact_design = _compact(design)
    assert (
        f"Prep Task 5B and committed Task 6 remain historically bound to "
        f"`sha256:{old_digest}`" in compact_plan
    )
    assert (
        "Task 7 and the post-Task-7 test-only integration correction remain "
        f"historically bound to the amended `sha256:{task7_digest}` generation"
        in compact_plan
    )
    assert (
        f"Prep 5B and committed Task 6 remain historically bound to `{old_digest}`"
        in compact_design
    )
    assert (
        "Task 7 and its post-task test-only correction use the amended digest "
        f"`{task7_digest}`" in compact_design
    )

    task7 = plan.split("### Task 7:", 1)[1].split(
        "## Final Integration And Verification", 1
    )[0]
    correct_prior_design = (
        "docs/superpowers/specs/"
        "2026-07-12-codex-opus-cross-model-verification-design.md"
    )
    mistyped_prior_design = correct_prior_design.replace("/specs/", "/plans/")
    assert f"- Modify: `{descriptor_path}`" in task7
    assert descriptor_path in task7
    assert f"@sha256:{task7_digest}" in task7
    assert correct_prior_design in task7
    assert mistyped_prior_design not in task7

    task8 = plan.split("### Task 8:", 1)[1].split(
        "## Final Integration And Verification", 1
    )[0]
    expected_additions = (
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".claude/agents/lane-v-verifier.md",
        ".claude/skills/seat-director/SKILL.md",
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "coordination/README.md",
        "docs/PROGRAM-MANUAL.md",
        "docs/templates/agents/implementer.md",
        "docs/templates/agents/reviewer.md",
        "docs/templates/claude/implementer.md",
        "docs/templates/claude/reviewer.md",
    )
    for path in expected_additions:
        assert path in task8
    assert f"@sha256:{current_digest}" in task8

    final = plan.split("## Final Integration And Verification", 1)[1]
    assert f"Expected descriptor digest: `{current_digest}`" in final
    assert f"with amended digest `{current_digest}`" in _compact(final)


def test_verification_report_format_mirrors_pin_the_compact_binding_order():
    agent_path = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude_path = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert agent_path.read_bytes() == claude_path.read_bytes()

    text = agent_path.read_text(encoding="utf-8")
    start = text.index("Event type:", text.index("## Body skeleton"))
    end = text.index("\n\n## Findings", start)
    field_lines = [
        line.split(":", 1)[0] + ":"
        for line in text[start:end].splitlines()
        if line and ":" in line and not line.startswith("## ")
    ]
    assert field_lines == [
        "Event type:",
        "VERDICT:",
        "Verification request:",
        "Reviewed head:",
        "Reviewed base:",
        "Reviewer seat:",
        "Reviewer model:",
        "Verification harness:",
        "Verification context:",
    ]


def test_provider_tool_decommission_is_current_architecture_and_append_only_decision():
    architecture = _read("ARCHITECTURE.md")
    decisions = (ROOT / "DECISIONS.md").read_bytes()

    prefix = decisions[:DECISIONS_PRE_TASK5_PREFIX_BYTES]
    assert hashlib.sha256(prefix).hexdigest() == DECISIONS_PRE_TASK5_PREFIX_SHA256
    appended = decisions[DECISIONS_PRE_TASK5_PREFIX_BYTES:].decode("utf-8")
    assert "## Targeted decommission of Opus and ChatGPT Pro tools" in appended
    assert "lane-v-report/v3" in appended
    assert "TaskPublicationStore" in appended
    assert "frozen historical" in appended
    assert ".codex/runtime" in appended
    assert "separate approval" in appended

    assert COMPACT_PAIR_REFERENCE in _compact(architecture.replace("`", ""))
    assert "TaskPublicationStore" not in architecture
    assert "R-INDEPENDENCE" in architecture
    assert "lane-v-report/v2" not in architecture


def test_cross_model_design_and_plan_match_safe_mode_system_prompt_boundary():
    for path in (
        "docs/superpowers/specs/2026-07-12-codex-opus-cross-model-verification-design.md",
        "docs/superpowers/plans/2026-07-12-codex-opus-cross-model-verification.md",
    ):
        text = _read(path)
        assert "--safe-mode" in text, path
        assert "--disable-slash-commands" in text, path
        assert "--append-system-prompt" in text, path
        assert "dynamically injects" not in text, path
