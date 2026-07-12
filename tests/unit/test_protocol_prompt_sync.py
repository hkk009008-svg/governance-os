from __future__ import annotations

import re
from pathlib import Path

import pytest

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


def _acceptance_backed_default(text: str | None = None) -> str:
    if text is None:
        text = _read("logs/chatgpt-pro-consultation-acceptance-2026-07-13.md")

    if "- Shipped default: `auto`" not in text:
        return model.chatgpt_pro_consultation_default(
            repo_root=ROOT,
            evidence_text=text,
        )
    try:
        return model.validate_chatgpt_pro_activation_evidence(text, repo_root=ROOT)
    except model.ChatGPTProActivationEvidenceError as exc:
        raise AssertionError(str(exc)) from exc


def _validate_acceptance_log_structure(text: str) -> None:
    forbidden = (
        "RAW_PROMPT_CANARY",
        "<consultation_request>",
        "</consultation_request>",
        '"prompt"',
        '"response"',
        '"schema_version"',
        '"recommendation"',
        '"reasoning"',
        '"assumptions"',
        '"risks"',
        '"questions"',
    )
    for marker in forbidden:
        assert marker not in text

    lines = text.splitlines()
    assert lines[0] == "# ChatGPT Pro consultation acceptance - 2026-07-13"
    expected_headings = (
        "## Scope",
        "## Results",
        "## Commands",
        "## Diagnostics",
        "## Activation decision",
    )
    sections: dict[str, list[str]] = {heading: [] for heading in expected_headings}
    seen_headings: list[str] = []
    current: str | None = None
    for line in lines[1:]:
        if not line:
            continue
        if line.startswith("## "):
            assert line in sections
            seen_headings.append(line)
            current = line
            continue
        assert current is not None
        sections[current].append(line)
    assert tuple(seen_headings) == expected_headings

    def bullets(heading: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in sections[heading]:
            match = re.fullmatch(r"- ([A-Za-z0-9 /-]+): `([^`\n]+)`", line)
            assert match is not None
            label, value = match.groups()
            assert label not in values
            values[label] = value
        return values

    scope = bullets("## Scope")
    base_scope = {
        "Bound HEAD",
        "Procedure",
        "Default before gate",
        "Raw consultation content persisted",
    }
    guard_scope = {"Guard commit", "Guard relevant paths hash"}
    assert frozenset(scope) in {
        frozenset(base_scope),
        frozenset(base_scope | guard_scope),
    }
    assert re.fullmatch(r"[0-9a-f]{40}", scope["Bound HEAD"])
    if guard_scope <= set(scope):
        assert re.fullmatch(r"[0-9a-f]{40}", scope["Guard commit"])
        assert re.fullmatch(r"[0-9a-f]{64}", scope["Guard relevant paths hash"])
    assert scope["Procedure"] == (
        "docs/protocol/codex/chatgpt-pro-consultation-acceptance.md"
    )
    assert scope["Default before gate"] in {"auto", "manual"}
    assert scope["Raw consultation content persisted"] == "no"

    result_lines = sections["## Results"]
    assert result_lines[:2] == [
        "| Test ID | Transport class | Result | Safe correlation | Lifecycle | "
        "Duplicate send | Protocol/ref/remote mutation | Failure class |",
        "|---|---|---|---|---|---|---|---|",
    ]
    allowed_transports = {
        "Desktop in-app",
        "configured CLI browser",
        "configured CLI non-sending diagnostic",
        "bare CLI manual relay",
        "fixture/disposable profile",
    }
    allowed_correlation = {
        "pass",
        "not applicable",
        "not applicable; no response/import",
        "pending",
    }
    allowed_lifecycle = {
        "`prepared -> sending -> sent -> failed`",
        "`prepared -> sending -> sent -> received -> reconciled`; tab finalized",
        "`prepared -> sending -> sent -> received -> reconciled`; manual relay finalized",
        "seven-case fixture matrix failed closed; fixtures finalized",
        "`prepared -> sending -> failed`; ephemeral process terminated after 5.5 "
        "minutes; tab finalization unverified",
        "core model healthy; Browser skill loaded; no navigation, tab, or message",
        "pending",
    }
    allowed_duplicate = {
        "pass; one send",
        "pass; one relay",
        "pass; no retry or fallback",
        "delivery uncertain; no retry",
        "no send",
        "pending",
    }
    allowed_mutation = {
        "pass; content-free snapshots match",
        "pass; content-free snapshots match; no Codex session persisted",
        "pass; no protected mutation",
        "pending",
    }
    allowed_failure = {
        "none",
        "pending",
        "`malformed`",
        "`partial_send`",
        "`backend_unavailable`",
    }
    for line in result_lines[2:]:
        assert line.startswith("| T5-") and line.endswith("|")
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 8
        assert re.fullmatch(
            r"T5-[A-Za-z0-9-]+(?: \(`[0-9a-f]{8}…[0-9a-f]{4}`\))?",
            cells[0],
        )
        assert cells[1] in allowed_transports
        assert cells[2] in {"pass", "fail", "pending"}
        assert cells[3] in allowed_correlation
        assert cells[4] in allowed_lifecycle
        assert cells[5] in allowed_duplicate
        assert cells[6] in allowed_mutation
        assert cells[7] in allowed_failure

    commands = bullets("## Commands")
    assert set(commands) == {
        "Focused tests",
        "Full protocol tests",
        "Project smoke",
        "Persistence/security scans",
        "Runtime state/lock pairs checked",
        "Protected hashes",
        "CLI-window rollout files created",
        "CLI-window rollout files modified",
    }
    assert re.fullmatch(r"[1-9][0-9]* passed", commands["Focused tests"])
    assert re.fullmatch(r"[1-9][0-9]* passed", commands["Full protocol tests"])
    assert commands["Project smoke"] == "OK"
    assert commands["Persistence/security scans"] == "pass"
    assert re.fullmatch(
        r"[1-9][0-9]*",
        commands["Runtime state/lock pairs checked"],
    )
    assert commands["Protected hashes"] == "match"
    assert commands["CLI-window rollout files created"] == "0"
    assert commands["CLI-window rollout files modified"] == "0"

    diagnostics = bullets("## Diagnostics")
    expected_diagnostics = {
        "Desktop r1 failure": "malformed",
        "Desktop r1 retry": "no",
        "Desktop r1 tab finalized": "yes",
        "Desktop r2 result": "pass",
        "Desktop r2 duplicate send": "no",
        "Desktop r2 tab finalized": "yes",
        "Configured CLI r1 failure": "partial_send",
        "Configured CLI r1 response imported": "no",
        "Configured CLI r1 retry": "no",
        "Configured CLI r1 duration seconds": "330",
        "Configured CLI r1 tab finalized": "unverified",
        "Configured CLI preflight duration seconds": "27.7",
        "Configured CLI core model": "pass",
        "Configured CLI Browser skill load": "pass",
        "Configured CLI backend": "iab",
        "Configured CLI browser connected": "false",
        "Configured CLI documentation loaded": "false",
        "Configured CLI preflight navigation": "none",
        "Configured CLI preflight messaging": "none",
        "Configured CLI preflight failure": "backend_unavailable",
    }
    assert diagnostics == expected_diagnostics

    activation = bullets("## Activation decision")
    base_activation = {
        "Desktop in-app gate",
        "Configured CLI browser gate",
        "Activation gate",
        "Shipped default",
        "Bounded blocker",
    }
    required_activation = {"Bare CLI manual gate", "Failure-fixture gate"}
    assert frozenset(activation) in {
        frozenset(base_activation),
        frozenset(base_activation | required_activation),
    }
    assert activation["Desktop in-app gate"] in {"pass", "fail"}
    assert activation["Configured CLI browser gate"] in {"pass", "fail"}
    assert activation["Activation gate"] in {"pass", "blocked"}
    assert activation["Shipped default"] in {"auto", "manual"}
    assert activation["Bounded blocker"] in {"none", "backend_unavailable"}
    if activation["Shipped default"] == "auto":
        assert guard_scope <= set(scope)
        assert required_activation <= set(activation)
        assert _acceptance_backed_default(text) == "auto"
    else:
        assert activation["Activation gate"] == "blocked"
        assert activation["Bounded blocker"] == "backend_unavailable"
        assert _acceptance_backed_default(text) == "manual"


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


def test_chatgpt_pro_consultation_model_contract_tracks_gate_and_fails_closed():
    expected_default = _acceptance_backed_default()
    assert model.CHATGPT_PRO_CONSULTATION_MODES == ("auto", "manual", "off")
    assert model.CHATGPT_PRO_CONSULTATION_DEFAULT == expected_default
    assert model.CHATGPT_PRO_CONSULTATION_TRANSPORT_ORDER == (
        "in-app browser",
        "approved Chrome bridge",
        "manual relay",
    )

    rendered = model.render_chatgpt_pro_consultation()
    for phrase in (
        "ChatGPT Pro Advisory Consultation:",
        "always invocable",
        "one guarded browser send per idempotency key",
        "manual relay",
        "not the dual-chief order path",
        "advisory only",
        "no API fallback",
        "raw prompts and responses stay out of Git",
        "coordinator refreshes live state before send and before use",
        "operator Lane V is never replaced",
    ):
        assert phrase in rendered

    assert (
        model.infer_runtime_env({})["CODEX_CHATGPT_PRO_CONSULTATION"]
        == expected_default
    )
    assert (
        model.infer_runtime_env({"CODEX_CHATGPT_PRO_CONSULTATION": "auto"})[
            "CODEX_CHATGPT_PRO_CONSULTATION"
        ]
        == "auto"
    )
    assert (
        model.infer_runtime_env({"CODEX_CHATGPT_PRO_CONSULTATION": "invalid"})[
            "CODEX_CHATGPT_PRO_CONSULTATION"
        ]
        == "off"
    )


def test_chatgpt_pro_transport_order_is_browser_first_in_model_and_skill():
    assert model.CHATGPT_PRO_CONSULTATION_TRANSPORT_ORDER == (
        "in-app browser",
        "approved Chrome bridge",
        "manual relay",
    )
    rendered = model.render_chatgpt_pro_consultation()
    assert rendered.index("in-app browser") < rendered.index("approved Chrome bridge")
    assert rendered.index("approved Chrome bridge") < rendered.index("manual relay")

    skill = _compact(_read(".agents/skills/chatgpt-pro-consultation/SKILL.md"))
    assert skill.index("Prefer the in-app browser") < skill.index(
        "approved Chrome bridge"
    )
    assert skill.index("approved Chrome bridge") < skill.index("Manual relay")


def test_chatgpt_pro_acceptance_procedure_is_fail_closed_and_content_free():
    procedure = _compact(
        _read("docs/protocol/codex/chatgpt-pro-consultation-acceptance.md")
    )
    for phrase in (
        "signed-in user-controlled session",
        "stdin",
        "never shell arguments",
        "CODEX_CHATGPT_PRO_CONSULTATION=auto",
        "in-app Browser",
        "CLI-driven browser",
        "signed-out",
        "wrong-account",
        "challenge",
        "partial-send",
        "do not set the default to auto",
        "current_repo_head",
        "direct `.codex/runtime/<file>`",
        "Guard commit",
        "Guard relevant paths hash",
        "bare-CLI manual relay",
        "complete failure-fixture matrix",
        "normalized `options`",
        "browser cookie/login stores",
    ):
        assert phrase in procedure
    lower_procedure = procedure.lower()
    assert "never enter credentials" in lower_procedure
    assert "never inspect cookies" in lower_procedure
    assert "no automatic retry" in lower_procedure

    acceptance_log = _read(
        "logs/chatgpt-pro-consultation-acceptance-2026-07-13.md"
    )
    _validate_acceptance_log_structure(acceptance_log)


@pytest.mark.parametrize(
    "injection",
    [
        "RAW_PROMPT_CANARY arbitrary raw payload",
        "<consultation_request>{}</consultation_request>",
        '{"schema_version":"v1","recommendation":"raw response"}',
        "## Unknown free-form section\n- arbitrary: content",
    ],
    ids=("canary", "prompt-marker", "raw-schema-fields", "unknown-section"),
)
def test_acceptance_log_structure_rejects_unsanitized_or_unknown_content(injection):
    acceptance_log = _read(
        "logs/chatgpt-pro-consultation-acceptance-2026-07-13.md"
    )

    with pytest.raises(AssertionError):
        _validate_acceptance_log_structure(f"{acceptance_log}\n{injection}\n")


def test_acceptance_log_structure_rejects_blocked_summary_without_blocker():
    acceptance_log = _read(
        "logs/chatgpt-pro-consultation-acceptance-2026-07-13.md"
    ).replace(
        "- Bounded blocker: `backend_unavailable`",
        "- Bounded blocker: `none`",
    )

    with pytest.raises(AssertionError):
        _validate_acceptance_log_structure(acceptance_log)


def test_chatgpt_pro_consultation_is_model_backed_and_surface_synced():
    rendered = model.render_chatgpt_pro_consultation()
    shared = (
        "ChatGPT Pro Advisory Consultation",
        "always invocable",
        "one guarded browser send per idempotency key",
        "manual relay",
        "no API fallback",
        "raw prompts and responses stay out of Git",
        "advisory only",
        "not the dual-chief order path",
        "subagents may prepare a bounded question but only the parent context may send",
        "automatic retries are zero in V1",
    )
    for phrase in shared:
        assert phrase in rendered

    for path in (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/chatgpt-pro-consultation/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/readiness-bridge.toml",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/protocol-operator.toml",
    ):
        text = _compact(_read(path))
        for phrase in shared:
            assert phrase in text, (path, phrase)


def test_chatgpt_pro_consultation_role_boundaries_are_explicit():
    coordinator_surfaces = (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/chatgpt-pro-consultation/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".codex/agents/protocol-coordinator.toml",
    )
    for path in coordinator_surfaces:
        text = _compact(_read(path))
        assert "mailbox-first before consultation" in text
        assert (
            "refresh HEAD, mailbox bodies, route, wave, capacity, and locks before prepare"
            in text
        )
        assert (
            "refresh HEAD, mailbox bodies, route, wave, capacity, and locks again "
            "before send and before use"
            in text
        )
        assert "pre-send drift discards the prepared packet and requires re-prepare" in text
        assert "drift marks the response stale" in text

    operator_surfaces = (
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/protocol-operator.toml",
    )
    for path in operator_surfaces:
        text = _compact(_read(path))
        assert "never replaces Lane V" in text
        assert "cannot contribute authority to GO, NITS, or FAIL" in text
        assert "distinct, pre-stated strategic question" in text


def test_chatgpt_pro_consultation_skill_preserves_all_normative_triggers():
    skill = _read(".agents/skills/chatgpt-pro-consultation/SKILL.md")
    _, frontmatter, body = skill.split("---", 2)
    description = next(
        line for line in frontmatter.splitlines() if line.startswith("description:")
    )
    assert description.startswith("description: Use when")
    assert "Provides guarded" not in description

    discovery_triggers = (
        "user explicitly asks to consult ChatGPT Pro",
        "idea or plan has unresolved material tradeoffs",
        "authority, security, external-input, parseable-context, schema-trust, or side-effect boundary",
        "post-plan needs a distinct adversarial challenge",
        "mailbox-oriented coordinator needs strategic advice",
    )
    for phrase in discovery_triggers:
        assert phrase in description

    compact_body = _compact(body)
    for trigger in model.CHATGPT_PRO_CONSULTATION_TRIGGERS:
        assert trigger in compact_body


def test_chatgpt_pro_consultation_manual_fallback_is_surface_synced():
    surfaces = (
        "AGENTS.md",
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/chatgpt-pro-consultation/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/readiness-bridge.toml",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/protocol-operator.toml",
    )
    fallback = (
        "definite safe auto failure is transitioned to failed",
        "resume-manual --state-file PATH --consultation-id UUID",
        "return the same record to prepared/manual",
        "uncertain or partial delivery stops for explicit user decision",
        "never retry or resume automatically",
    )
    for path in surfaces:
        text = _compact(_read(path)).replace("`", "")
        for phrase in fallback:
            assert phrase in text, (path, phrase)

    skill = _compact(_read(".agents/skills/chatgpt-pro-consultation/SKILL.md")).replace(
        "`", ""
    )
    assert (
        ".venv/bin/python scripts/chatgpt_pro_consult.py resume-manual "
        "--state-file PATH --consultation-id UUID"
        in skill
    )
    assert "command arguments are content-free identifiers" in skill
    assert "request and response payload content remains stdin-only" in skill


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
        "review profile codex-lane-v",
        "standing-policy:codex-lane-v-opus-v1",
        "only when the authorization source is absent",
        "malformed explicit authorization never falls back",
        "one provider process attempt and no automatic retry",
        "one invocation per unchanged Lane V verification",
        "does not authorize design-time Opus or any other paid call",
        "opus-review/v2",
        "V1 applies only to Pipeline-repository verification",
        "Cross-repo and evidence-ledger verification use explicit Codex-only fallback outside V1",
        "operator retains GO/NITS/FAIL authority",
        "unavailable is explicit degraded Codex-only fallback",
        "every Opus finding requires a disposition",
        "unresolved Opus finding blocks GO",
        "reconciliation requires explicit expected HEAD/base and preserves reviewed scope",
        "reconciliation requires an explicit Pipeline repo root and local proof that expected HEAD/base commits exist before GO",
        "no third same-question generic reviewer",
        "Do not launch generic same-question spec or code-quality reviewers",
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
        "Review profile:",
        "Authorization identity:",
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
    assert (
        "## ADR-023: Make Codex R-INDEPENDENCE operative and authorize one standing Lane-V Opus attempt"
        in decisions
    )
    assert "standing-policy:codex-lane-v-opus-v1" in architecture
    assert "opus-review/v2" in architecture
    assert "R-INDEPENDENCE" in architecture
    assert "one provider process" in architecture


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
