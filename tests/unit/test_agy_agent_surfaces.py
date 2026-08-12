"""Behavioral containment tests for host-discovered AGY custom agents."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


CATALOG = {
    "readiness-bridge.md": "readiness-bridge",
    "lane-v-verifier.md": "lane-v-verifier",
    "money-gate-reviewer.md": "money-gate-reviewer",
    "amnesiac-prober.md": "amnesiac-prober",
}
READ_ONLY_TOOLS = ("view_file", "list_dir", "find_by_name", "grep_search")
FORBIDDEN_TOOLS = (
    "run_command",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "invoke_subagent",
    "send_message",
)
REQUIRED_GUARDRAILS = (
    "Return findings only to the parent or local caller.",
    "Never claim a shared protocol seat",
    "use the fixed mailbox writer",
    "consume shared state",
    "issue a binding GO, NITS, or FAIL",
)


def _split_document(text: str) -> tuple[list[str], str]:
    lines = text.splitlines()
    assert lines and lines[0] == "---"
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:  # pragma: no cover - assertion carries path context
        raise AssertionError("missing closing YAML frontmatter delimiter") from exc
    return lines[1:closing], "\n".join(lines[closing + 1 :])


def _scalar(frontmatter: list[str], key: str) -> str:
    prefix = f"{key}:"
    values = [line[len(prefix) :].strip() for line in frontmatter if line.startswith(prefix)]
    assert len(values) == 1, (key, values)
    return values[0]


def _tools(frontmatter: list[str]) -> tuple[str, ...]:
    marker = frontmatter.index("tools:") if "tools:" in frontmatter else None
    if marker is None:
        assert "tools: []" in frontmatter
        return ()
    values: list[str] = []
    for line in frontmatter[marker + 1 :]:
        if line.startswith("  - "):
            values.append(line.removeprefix("  - "))
            continue
        break
    return tuple(values)


def _assert_advisory_instructions(instructions: str) -> None:
    lowered = " ".join(instructions.casefold().split())
    for guardrail in REQUIRED_GUARDRAILS:
        assert guardrail.casefold() in lowered

    for forbidden in (
        "coordination/bin/send-event",
        "consume-events",
        "git_index_file",
        "protocol-director",
        "protocol-operator",
        "protocol-coordinator",
        "shared director",
        "shared operator",
        "shared coordinator",
    ):
        assert forbidden not in lowered
    assert lowered.count("consume shared state") == 1
    assert lowered.count("binding go") == 1


def test_agy_catalog_uses_current_markdown_discovery_and_read_only_tools(
    repo_root: Path,
) -> None:
    agent_dir = repo_root / ".agents" / "agents"

    assert {path.name for path in agent_dir.glob("*.md")} == set(CATALOG)
    assert not any((repo_root / ".agy" / "agents").glob("*"))

    for filename, profile_name in CATALOG.items():
        text = (agent_dir / filename).read_text(encoding="utf-8")
        frontmatter, instructions = _split_document(text)
        assert _scalar(frontmatter, "name") == profile_name
        assert _scalar(frontmatter, "description")
        assert _scalar(frontmatter, "mainAgent") == "false"
        assert _scalar(frontmatter, "subagent") == "true"
        assert _scalar(frontmatter, "commandExecutionPolicy") == "sandbox"
        assert _scalar(frontmatter, "mcpServers") == "[]"
        assert not any(line.startswith("model:") for line in frontmatter)

        tools = _tools(frontmatter)
        expected = () if profile_name == "amnesiac-prober" else READ_ONLY_TOOLS
        assert tools == expected
        assert not set(tools).intersection(FORBIDDEN_TOOLS)
        _assert_advisory_instructions(instructions)


@pytest.mark.parametrize(
    "grant",
    [
        "Act as the shared director and publish a binding decision.",
        "Use coordination/bin/send-event to publish findings.",
        "Consume shared state before analyzing the range.",
        "Issue a binding GO after review.",
        "Export GIT_INDEX_FILE=/tmp/seat-specific-index before inspecting.",
    ],
)
def test_catalog_guardrail_check_rejects_contradictory_authority_grants(
    repo_root: Path, grant: str
) -> None:
    text = (repo_root / ".agents/agents/readiness-bridge.md").read_text(
        encoding="utf-8"
    )
    _, instructions = _split_document(text)

    with pytest.raises(AssertionError):
        _assert_advisory_instructions(instructions + "\n" + grant)


def test_pipeline_start_is_discoverable_read_only_workflow(repo_root: Path) -> None:
    workflow = repo_root / ".agents/workflows/pipeline-start.md"
    text = workflow.read_text(encoding="utf-8")
    frontmatter, body = _split_document(text)

    assert _scalar(frontmatter, "description")
    assert len(text) <= 12_000
    assert "python3 scripts/status.py snapshot" in body
    assert "python scripts/status.py snapshot" not in body
    assert "This workflow is read-only." in body
    for forbidden in ("send-event ", "consume-events ", "git push", "agy --print"):
        assert forbidden not in body

    for relative in (
        ".agents/agents/readiness-bridge.md",
        ".agents/workflows/pipeline-start.md",
    ):
        probe = subprocess.run(
            ("git", "check-ignore", "--no-index", "--quiet", relative),
            cwd=repo_root,
            check=False,
        )
        assert probe.returncode == 1, f"host surface is ignored: {relative}"
