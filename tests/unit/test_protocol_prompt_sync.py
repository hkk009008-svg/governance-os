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
