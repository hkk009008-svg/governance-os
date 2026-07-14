from __future__ import annotations

import hashlib
import json
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


def _trigger_contract_text(path: str) -> str:
    return _compact(_read(path).replace("`", ""))


VERIFY_REQUEST_TRIGGER_FRAGMENTS = (
    "canonical committed sent-mailbox event",
    "strictly after the reviewed HEAD",
    "Event type: verify-request",
    "Reviewed head: <40-lowercase-hex>",
    "Reviewed base: <40-lowercase-hex>",
    (
        "Lane-V-Scope: coordination/verification/scopes/"
        "<uuid>.json@sha256:<64-lowercase-hex>"
    ),
)
SHIPPING_TRIGGER_FRAGMENTS = (
    "shipping trigger commit equals the reviewed HEAD",
    "subject begins feat, fix, or refactor",
    "exactly one identical descriptor reference in the terminal Git trailer block",
)
INVALID_TRIGGER_FRAGMENTS = (
    (
        "Missing, duplicated, abbreviated, uppercase, misplaced, uncommitted, "
        "stale, or mismatched authority is not a trigger"
    ),
    "stop with a blocker",
    "do not reconstruct missing fields",
    "do not fall back to the other trigger kind",
)
PIPELINE_ONLY_EXECUTION_BOUNDARY_FRAGMENTS = (
    "descriptor and trigger grammar is Pipeline-only",
    "return to the coordinator",
    "separate evidence-ledger-aware bridge route",
    "never fabricate Pipeline descriptor authority",
)
TASK8_TRIGGER_FRAGMENT_CATEGORIES = (
    ("lawful verify-request production", VERIFY_REQUEST_TRIGGER_FRAGMENTS),
    ("lawful shipping production", SHIPPING_TRIGGER_FRAGMENTS),
    ("invalid-trigger fail-closed", INVALID_TRIGGER_FRAGMENTS),
    (
        "Pipeline-only execution boundary",
        PIPELINE_ONLY_EXECUTION_BOUNDARY_FRAGMENTS,
    ),
)


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
        "Desktop r3 result": "pass",
        "Desktop r3 state file": ".codex/runtime/task5-iab-r3-acceptance.json",
        "Desktop r3 request hash": "9f551ed6…57b2b5",
        "Desktop r3 idempotency key": "faec7aba…2f98e25",
        "Desktop r3 binding hash": "f8f0eaef…ebe107f",
        "Desktop r3 correlation": "pass",
        "Desktop r3 transport sends": "1",
        "Desktop r3 transport resend": "no",
        "Desktop r3 interrupted local accept": "1",
        "Desktop r3 state after interrupted accept": "sent",
        "Desktop r3 response imports": "1",
        "Desktop r3 final state": "reconciled",
        "Desktop r3 tab finalized": "yes",
        "Desktop r4 result": "pass",
        "Desktop r4 state file": ".codex/runtime/task5-iab-r4-acceptance.json",
        "Desktop r4 request hash": "db21ab3d…ae2843e",
        "Desktop r4 idempotency key": "2f823517…023add1",
        "Desktop r4 binding hash": "37ce5271…fadbbf36",
        "Desktop r4 correlation": "pass",
        "Desktop r4 transport sends": "1",
        "Desktop r4 retry": "no",
        "Desktop r4 response imports": "1",
        "Desktop r4 final state": "reconciled",
        "Desktop r4 tab finalized": "yes",
        "Desktop r4 failure": "none",
        "Bare CLI manual r2 result": "pass",
        "Bare CLI manual r2 state file": (
            ".codex/runtime/task5-manual-r2-acceptance.json"
        ),
        "Bare CLI manual r2 request hash": "c2dee748…451918",
        "Bare CLI manual r2 idempotency key": "a3ed85e4…77fd5b",
        "Bare CLI manual r2 binding hash": "f8f0eaef…ebe107f",
        "Bare CLI manual r2 prompt parity": "pass",
        "Bare CLI manual r2 correlation": "pass",
        "Bare CLI manual r2 relays": "1",
        "Bare CLI manual r2 response imports": "1",
        "Bare CLI manual r2 final state": "reconciled",
        "Bare CLI manual r3 result": "pass",
        "Bare CLI manual r3 state file": (
            ".codex/runtime/task5-manual-r3-acceptance.json"
        ),
        "Bare CLI manual r3 request hash": "6704a57f…0c93feb",
        "Bare CLI manual r3 idempotency key": "22176eba…1a633ad",
        "Bare CLI manual r3 binding hash": "37ce5271…fadbbf36",
        "Bare CLI manual r3 prompt parity": "pass",
        "Bare CLI manual r3 correlation": "pass",
        "Bare CLI manual r3 relays": "1",
        "Bare CLI manual r3 response imports": "1",
        "Bare CLI manual r3 final state": "reconciled",
        "Bare CLI manual r3 failure": "none",
        "Failure-fixture result": "pass",
        "Failure-fixture cases": (
            "signed-out,wrong-account,challenge,refusal,html,truncated-json,"
            "partial-send"
        ),
        "Failure-fixture pre-send stops": "signed-out,wrong-account,challenge",
        "Failure-fixture partial-send start": "sending",
        "Failure-fixture retry or fallback": "none",
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


def test_chatgpt_pro_consultation_model_contract_is_auto_or_block():
    assert model.CHATGPT_PRO_CONSULTATION_MODES == ("auto", "manual", "off")
    assert model.CHATGPT_PRO_CONSULTATION_DEFAULT == "auto"
    assert model.CHATGPT_PRO_CONSULTATION_TRANSPORT_ORDER == ("iab", "block")

    rendered = model.render_chatgpt_pro_consultation()
    for phrase in (
        "ChatGPT Pro Advisory Consultation:",
        "always invocable",
        "one guarded send per idempotency key",
        "current runtime in-app Browser transport (iab)",
        "transport order: iab -> block",
        "not the dual-chief order path",
        "advisory only",
        "no automatic Chrome, manual relay, API, retry, or workaround fallback",
        "prompts and responses stay out of Git",
        "coordinator refreshes live state before send and before use",
        "operator Lane V is never replaced",
    ):
        assert phrase in rendered

    assert (
        model.infer_runtime_env({})["CODEX_CHATGPT_PRO_CONSULTATION"]
        == "auto"
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


def test_chatgpt_pro_transport_order_is_iab_then_block_in_model_and_skill():
    assert model.CHATGPT_PRO_CONSULTATION_TRANSPORT_ORDER == ("iab", "block")
    rendered = model.render_chatgpt_pro_consultation()
    assert rendered.index("transport order: iab -> block") < rendered.index(
        "no automatic Chrome"
    )

    skill = _compact(_read(".agents/skills/chatgpt-pro-consultation/SKILL.md"))
    assert "transport order is `iab -> block`" in skill
    assert "Use only the current runtime in-app Browser transport (`iab`)" in skill
    assert "do not launch or substitute Chrome" in skill


def test_chatgpt_pro_auto_policy_is_iab_then_block_without_fallback_instructions():
    assert model.CHATGPT_PRO_CONSULTATION_DEFAULT == "auto"
    assert model.infer_runtime_env({})["CODEX_CHATGPT_PRO_CONSULTATION"] == "auto"
    assert model.CHATGPT_PRO_CONSULTATION_TRANSPORT_ORDER == ("iab", "block")

    rendered = _compact(model.render_chatgpt_pro_consultation())
    assert "transport order: iab -> block" in rendered
    assert "approved Chrome bridge" not in rendered
    assert "then manual relay" not in rendered

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
    for path in surfaces:
        text = _compact(_read(path))
        assert "default is `auto`" in text, path
        assert "transport order is `iab -> block`" in text, path
        assert "approved Chrome bridge" not in text, path
        assert "resume-manual" not in text, path


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
        "automatic path is `iab -> block`",
        "block with zero send",
        "does not claim live readiness",
        "historical acceptance log remains historical",
        "signed-out",
        "wrong-account",
        "challenge",
        "partial-send",
        "current_repo_head",
        "direct `.codex/runtime/<file>`",
        "Guard commit",
        "Guard relevant paths hash",
        "complete failure-fixture matrix",
        "normalized `options`",
        "browser cookie/login stores",
        "`.crt` or `.cer`",
        "known backup or database sidecar suffix",
    ):
        assert phrase in procedure
    lower_procedure = procedure.lower()
    assert "never enter credentials" in lower_procedure
    assert "never inspect cookies" in lower_procedure
    assert "no automatic retry" in lower_procedure
    assert "chrome" not in lower_procedure
    assert "manual relay" not in lower_procedure
    assert "configured cli browser" not in lower_procedure
    assert "resume-manual" not in lower_procedure

    acceptance_log = _read(
        "logs/chatgpt-pro-consultation-acceptance-2026-07-13.md"
    )
    _validate_acceptance_log_structure(acceptance_log)


def test_refreshed_acceptance_requires_exact_seven_case_fixture_evidence():
    acceptance_log = _read(
        "logs/chatgpt-pro-consultation-acceptance-2026-07-13.md"
    )

    assert (
        "| T5-FAILURE-FIXTURES-r1 | fixture/disposable profile | pass | "
        "not applicable | seven-case fixture matrix failed closed; fixtures "
        "finalized | pass; no retry or fallback | pass; content-free snapshots "
        "match | none |"
    ) in acceptance_log
    assert "- Failure-fixture cases: `signed-out,wrong-account,challenge,refusal,html,truncated-json,partial-send`" in acceptance_log
    assert "- Failure-fixture pre-send stops: `signed-out,wrong-account,challenge`" in acceptance_log
    assert "- Failure-fixture partial-send start: `sending`" in acceptance_log


def test_final_guard_acceptance_binding_preserves_blocked_manual_default():
    acceptance_log = _read(
        "logs/chatgpt-pro-consultation-acceptance-2026-07-13.md"
    )

    assert (
        "- Bound HEAD: `b7efee47314785397ec2e173778881a1c9eb9899`"
    ) in acceptance_log
    assert (
        "- Guard commit: `b7efee47314785397ec2e173778881a1c9eb9899`"
    ) in acceptance_log
    assert (
        "- Guard relevant paths hash: "
        "`1dca17fe72a60f06d6c870dfba7dd312673f82abcb4329f55e79af2b83c57e19`"
    ) in acceptance_log
    assert (
        "| T5-IAB-r4 (`be64019b…d2a8`) | Desktop in-app | pass | pass | "
        "`prepared -> sending -> sent -> received -> reconciled`; tab finalized "
        "| pass; one send | pass; content-free snapshots match | none |"
    ) in acceptance_log
    assert (
        "| T5-CLI-MANUAL-r3 (`dd2106d4…7b34`) | bare CLI manual relay | pass "
        "| pass | `prepared -> sending -> sent -> received -> reconciled`; manual "
        "relay finalized | pass; one relay | pass; content-free snapshots match | "
        "none |"
    ) in acceptance_log
    assert "- Configured CLI browser gate: `fail`" in acceptance_log
    assert "- Activation gate: `blocked`" in acceptance_log
    assert "- Shipped default: `manual`" in acceptance_log
    assert "- Bounded blocker: `backend_unavailable`" in acceptance_log


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
        "current runtime in-app Browser transport",
        "prompts and responses stay out of Git",
        "advisory only",
        "not the dual-chief order path",
        "subagents may prepare a bounded question but only the parent context may send",
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


def test_chatgpt_pro_consultation_auto_failure_block_is_surface_synced():
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
    block = (
        "If iab is unavailable, signed out, challenged, or ambiguous before send",
        "transition the record to failed when safe to do so and block with zero send",
        "Uncertain or partial delivery also blocks without retry or fallback",
    )
    for path in surfaces:
        text = _compact(_read(path)).replace("`", "")
        for phrase in block:
            assert phrase in text, (path, phrase)
        assert "resume-manual" not in text, path
        assert "approved Chrome bridge" not in text, path


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
        "lane-v-scope/v1",
        "opus-review/v3",
        "opus-reconciliation/v2",
        "--shipping-commit",
        "--verify-request-commit",
        "--verify-request-path",
        "--receipt-id",
        "--opus-review-json is removed",
        "attempt_state_uncertain",
        "one provider process attempt and no automatic retry",
        "lane-v-report/v2",
        "## Verification Attestation",
        "Opus receipt ID:",
        "Opus scope digest:",
        "exact stored Codex verdict",
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
        for phrase in required:
            assert phrase.lower() in text, (path, phrase)
        for stale in (
            "--requirement ",
            "--allow-path",
            "--verification-command",
            "reconcile --opus-review-json",
            "normalized opus-review/v2",
        ):
            assert stale not in text, (path, stale)

    report_fields = (
        "Review profile:",
        "Authorization identity:",
        "Opus receipt ID:",
        "Opus scope digest:",
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
        "exact stored Codex verdict",
        "Opus receipt ID: exact stored reconcile field",
        "Opus scope digest: exact stored reconcile field",
        "send-event publication gate is authority, not a Codex hook",
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
    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".codex/agents/lane-v-verifier.toml",
        ".codex/agents/protocol-operator.toml",
    ):
        assert "send-event publication gate" in _read(path), path
    hooks = _read(".codex/hooks.json")
    assert "opus_review_bridge" not in hooks
    assert "verification_report_gate" not in hooks


def test_lane_v_trigger_producer_contract_is_surface_synced() -> None:
    producer_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "coordination/README.md",
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
        for fragment in (
            *VERIFY_REQUEST_TRIGGER_FRAGMENTS,
            *SHIPPING_TRIGGER_FRAGMENTS,
            *INVALID_TRIGGER_FRAGMENTS,
        ):
            assert fragment in text, (path, fragment)


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
        for fragment in (
            *VERIFY_REQUEST_TRIGGER_FRAGMENTS,
            *SHIPPING_TRIGGER_FRAGMENTS,
            *INVALID_TRIGGER_FRAGMENTS,
        ):
            assert fragment in text, (path, fragment)


def test_lane_v_trigger_renderers_include_every_task8_contract_category() -> None:
    rendered_outputs = (
        ("render_pair_operating_contract", model.render_pair_operating_contract()),
        (
            "render_cross_model_verification",
            model.render_cross_model_verification(),
        ),
    )

    for renderer_name, rendered in rendered_outputs:
        text = _compact(rendered.replace("`", ""))
        for category, fragments in TASK8_TRIGGER_FRAGMENT_CATEGORIES:
            for fragment in fragments:
                assert fragment in text, (renderer_name, category, fragment)


def test_lane_v_active_surfaces_remove_commit_only_and_prose_only_substitutes() -> None:
    rendered_pair = model.render_pair_operating_contract()
    rendered_cross_model = model.render_cross_model_verification()
    stale_model_phrases = (
        "operator verifies only that artifact or landed commit",
        "include commit/range, brief path",
        "Operator waits for a fresh verify-request or shipping commit",
    )
    for phrase in stale_model_phrases:
        assert phrase not in rendered_pair
        assert phrase not in rendered_cross_model

    active_paths = (
        "AGENTS.md",
        "RUNBOOK-DAILY.md",
        "coordination/README.md",
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
    conditional_rule = (
        "emit a shipping Lane-V-Scope trailer only when the parent explicitly "
        "authorizes that commit and supplies the exact descriptor reference"
    )
    for path in implementer_paths:
        text = _trigger_contract_text(path)
        assert conditional_rule in text, path
        assert "never invent trigger authority" in text, path

    for path in reviewer_paths:
        text = _trigger_contract_text(path)
        assert "a named commit or prose-only event is not trigger authority" in text, path
        assert "never invent trigger authority" in text, path


def test_lane_v_trigger_guidance_pins_bridge_forms_and_pipeline_boundary() -> None:
    bridge_paths = (
        ".codex/agents/lane-v-verifier.toml",
        ".claude/agents/lane-v-verifier.md",
        ".agents/skills/seat-operator/verification-report-format.md",
        ".claude/skills/seat-operator/verification-report-format.md",
    )
    for path in bridge_paths:
        text = _read(path)
        assert '--shipping-commit "$HEAD"' in text, path
        assert '--verify-request-commit "$TRIGGER_COMMIT"' in text, path
        assert '--verify-request-path "$TRIGGER_PATH"' in text, path
        assert text.count(
            "--transport-profile anthropic-claude-existing-session-v1"
        ) == 2, path

    pipeline_boundary_paths = (
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
    )
    for path in pipeline_boundary_paths:
        text = _trigger_contract_text(path)
        for fragment in PIPELINE_ONLY_EXECUTION_BOUNDARY_FRAGMENTS:
            assert fragment in text, (path, fragment)

    agent_report = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude_report = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert agent_report.read_bytes() == claude_report.read_bytes()


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


def test_verification_report_format_mirrors_pin_the_v2_attestation_order():
    agent_path = ROOT / ".agents/skills/seat-operator/verification-report-format.md"
    claude_path = ROOT / ".claude/skills/seat-operator/verification-report-format.md"
    assert agent_path.read_bytes() == claude_path.read_bytes()

    text = agent_path.read_text(encoding="utf-8")
    start = text.index("## Verification Attestation\n", text.index("## Body skeleton"))
    end = text.index("\n\n## Findings", start)
    field_lines = [
        line.split(":", 1)[0] + ":"
        for line in text[start:end].splitlines()
        if line and not line.startswith("## ")
    ]
    assert field_lines == [
        "Verification schema:",
        "Verification mode:",
        "Verification harness:",
        "Verification task ID:",
        "Scope authority:",
        "Trigger identity:",
        "Reviewed head:",
        "Reviewed base:",
        "Review profile:",
        "Authorization identity:",
        "Opus receipt ID:",
        "Opus scope digest:",
        "Cross-model review:",
        "Effective Opus model:",
        "Opus finding dispositions:",
        "Reconciliation guard:",
        "Degraded reason:",
    ]


def test_cross_model_opus_bridge_is_mapped_in_architecture_and_decisions():
    architecture = _read("ARCHITECTURE.md")
    compact_architecture = _compact(architecture)
    decisions = _read("DECISIONS.md")

    assert "scripts/opus_review_bridge.py" in architecture
    assert "verdict-blind Opus review" in architecture
    assert "## ADR-020: Mandatory blind Opus review after Codex Lane V" in decisions
    assert "degraded Codex-only fallback" in decisions
    assert "operator retains GO/NITS/FAIL authority" in decisions
    assert "--safe-mode" in architecture
    assert "OS-enforced sandbox" in architecture
    assert "literal reviewed commit" in architecture
    assert "content-addressed prompt-authority requirement" in architecture
    assert "dynamically injects" not in decisions
    assert (
        "## ADR-023: Make Codex R-INDEPENDENCE operative and authorize one standing Lane-V Opus attempt"
        in decisions
    )
    assert "standing-policy:codex-lane-v-opus-v1" in architecture
    assert "opus-review/v3" in architecture
    assert "opus-reconciliation/v2" in architecture
    assert (
        "reserved -> reviewed -> reconciled -> publishing -> published"
        in compact_architecture
    )
    assert "prompt source itself is intentionally committed" in compact_architecture
    assert "raw prompt text is never persisted." not in architecture
    assert "R-INDEPENDENCE" in architecture
    assert "one provider process" in architecture

    hardened_design = _read(
        "docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md"
    )
    compact_design = _compact(hardened_design)
    assert "exact eight-field" in compact_design
    assert "Candidate-only recovery" in compact_design
    assert "Final-only recovery" in compact_design
    assert "Final-plus-candidate" in compact_design
    assert "only when both the stored final and candidate names are" in compact_design
    assert "exact five-part" not in hardened_design


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
