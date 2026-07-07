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
    ):
        text = _read(path)
        assert "docs/templates/agents/implementer.md" in text
        assert "docs/protocol/agents/orchestration.md" in text
        assert "docs/templates/claude/implementer.md" not in text
        assert "docs/protocol/claude/orchestration.md" not in text


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
