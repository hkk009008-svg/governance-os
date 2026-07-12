from __future__ import annotations

from pathlib import Path

import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]
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


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


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


def test_codex_director_skill_uses_agent_neutral_templates():
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


def test_claude_function_harmonization_is_model_backed_and_documented():
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


def test_codex_specialist_agents_require_adversarial_proof_loop():
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


def test_subagent_utilization_decision_is_rendered_and_documented():
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


def test_codex_execution_tiers_are_model_backed_and_surface_synced():
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
        "before implementation",
        "independent design-time enumeration",
        "abuse cases, edge cases, and coverage targets",
        "different model or harness is preferred",
        "same-model independent reviewer is weaker",
        "committed plan or equivalent durable artifact",
        "independent reviewer verifies the actual diff",
        "Lane V plus verdict-blind Opus",
        "R-VERIFY-TIER",
        "docs/protocol/claude/independence-first.md",
    )
    for phrase in required:
        assert phrase in rendered

    shared_surface_phrases = (
        "R-INDEPENDENCE",
        "adversarial-surface",
        "before implementation",
        "independent design-time enumeration",
        "enforced-and-tested",
        "verify the actual diff",
        "R-VERIFY-TIER",
    )
    for path in (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".codex/agents/readiness-bridge.toml",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/protocol-operator.toml",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/money-gate-reviewer.toml",
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


def test_agentnn_extensions_have_distinct_routing_prompts():
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


def test_agentnn_extensions_keep_no_seat_authority_boundary():
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


def test_capacity_split_default_is_model_backed_and_surface_synced():
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


def test_side_effect_executor_token_contract_is_model_backed_and_documented():
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


def test_side_effect_executor_token_detailed_contract_is_surface_synced():
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


def test_rule_12_pattern_reference_transplant_is_surface_synced():
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


def test_rule_13_disposition_transplant_is_surface_synced():
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


def test_emergency_and_disagreement_contracts_are_model_backed_and_synced():
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


def test_blocked_wave_and_acting_coordinator_contract_is_model_backed_and_synced():
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


def test_reviewer_result_handling_contract_is_model_backed_and_synced():
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


def test_cross_model_opus_verification_is_model_backed_and_surface_synced():
    rendered = model.render_cross_model_verification()
    required = (
        "Cross-Model Opus Verification:",
        "after every Codex Lane V verification",
        "exactly one verdict-blind Opus review",
        "parent prompt supplies recorded task-level authorization",
        "V1 applies only to Pipeline-repository verification",
        "Cross-repo and evidence-ledger verification use explicit Codex-only fallback outside V1",
        "operator retains GO/NITS/FAIL authority",
        "unavailable is explicit degraded Codex-only fallback",
        "every Opus finding requires a disposition",
        "unresolved Opus finding blocks GO",
        "reconciliation requires explicit expected HEAD/base and preserves reviewed scope",
        "reconciliation requires an explicit Pipeline repo root and local proof that expected HEAD/base commits exist before GO",
        "no automatic retry",
        "no third same-question generic reviewer",
        "Do not launch generic same-question spec or code-quality reviewers",
        "permits exactly the one bounded Opus call and does not grant inherited paid-spend authority",
        "only a different pre-stated specialist question is eligible",
    )
    for phrase in required:
        assert phrase in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/protocol-operator.toml",
    ):
        text = _read(path).replace("`", "").lower()
        for phrase in required[1:]:
            assert phrase.lower() in text, (path, phrase)

    report_fields = (
        "Cross-model review:",
        "Effective Opus model:",
        "Opus finding dispositions:",
        "Reconciliation guard:",
        "Degraded reason:",
    )
    for path in (
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/protocol-operator.toml",
    ):
        prompt = _read(path)
        for field in report_fields:
            assert field in prompt, (path, field)

    lane_v = _read(".codex/agents/lane-v-verifier.toml")
    assert "scripts/opus_review_bridge.py review" in lane_v
    assert "scripts/opus_review_bridge.py reconcile" in lane_v

    protocol_operator = _read(".codex/agents/protocol-operator.toml")
    for phrase in (
        "If any required cross-model field is missing, block GO",
        "go_allowed=false blocks GO",
        "Confirmed minor Opus findings require NITS",
        "confirmed important or critical Opus findings require FAIL",
    ):
        assert phrase in protocol_operator

    operator_skill = _read(".agents/skills/seat-operator/SKILL.md")
    assert "For non-Codex Lane V" in operator_skill
    assert "primary Codex analysis plus the blind Opus pass" in operator_skill
    assert "Spawn read-only `lane-v-verifier` for ordinary landed diffs" not in operator_skill
    assert (
        "For non-Codex Lane V, spawn read-only `lane-v-verifier` for ordinary landed diffs"
        in operator_skill
    )
    assert "Dispatch **cold-context** spec + code-quality reviewer subagents on every" not in operator_skill

    continuation = _read("docs/protocol/codex/continuation.md")
    assert (
        "The generic implementer -> spec review -> quality review loop applies to "
        "implementation delivery, not Codex Lane V same-question review."
    ) in continuation


def test_cross_model_opus_bridge_is_mapped_in_architecture_and_decisions():
    architecture = _read("ARCHITECTURE.md")
    decisions = _read("DECISIONS.md")

    assert "scripts/opus_review_bridge.py" in architecture
    assert "verdict-blind Opus review" in architecture
    assert "## ADR-020: Mandatory blind Opus review after Codex Lane V" in decisions
    assert "degraded Codex-only fallback" in decisions
    assert "operator retains GO/NITS/FAIL authority" in decisions
    assert "--safe-mode" in architecture
    assert "OS-enforced sandbox" in architecture
    assert "precedes the reviewed HEAD" in architecture
    assert "dynamically injects" not in decisions


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
