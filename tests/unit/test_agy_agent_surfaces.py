"""Behavioral containment tests for the committed AGY advisory catalog."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest


CATALOG = {
    "readiness-bridge.toml": "readiness-bridge",
    "lane-v-verifier.toml": "lane-v-verifier",
    "money-gate-reviewer.toml": "money-gate-reviewer",
    "amnesiac-prober.toml": "amnesiac-prober",
}
REMOVED_LIVE_SEATS = {
    "protocol-director.toml",
    "protocol-operator.toml",
    "protocol-coordinator.toml",
}
REQUIRED_GUARDRAILS = (
    "Return findings only to the parent or local caller.",
    "Never claim a shared protocol seat.",
    "Never use the fixed mailbox writer.",
    "Never consume shared state.",
    "Never issue a binding GO, NITS, or FAIL.",
)


def _assert_advisory_instructions(instructions: str) -> None:
    for guardrail in REQUIRED_GUARDRAILS:
        assert guardrail in instructions

    lowered = instructions.lower()
    assert "coordination/bin/send-event" not in lowered
    assert "consume-events" not in lowered
    assert "index-agy-" not in lowered
    # The retired per-seat index is reachable by wording that never names the
    # index: an instruction to point GIT_INDEX_FILE anywhere reintroduces the
    # session-wide rebinding hazard, so reject the variable itself, not just
    # its old provider-prefixed filename.
    assert "git_index_file" not in lowered
    assert "protocol-director" not in lowered
    assert "protocol-operator" not in lowered
    assert "protocol-coordinator" not in lowered
    assert "shared director" not in lowered
    assert "shared operator" not in lowered
    assert "shared coordinator" not in lowered
    assert "publish" not in lowered
    assert "cursor" not in lowered
    assert lowered.count("fixed mailbox writer") == 1
    assert lowered.count("shared state") == 1
    assert lowered.count("binding") == 1


def test_agy_catalog_contains_only_read_only_advisory_profiles(repo_root: Path) -> None:
    agent_dir = repo_root / ".agy" / "agents"

    assert {path.name for path in agent_dir.glob("*.toml")} == set(CATALOG)
    assert not any((agent_dir / name).exists() for name in REMOVED_LIVE_SEATS)

    for filename, profile_name in CATALOG.items():
        document = tomllib.loads((agent_dir / filename).read_text(encoding="utf-8"))
        assert set(document) == {
            "name",
            "description",
            "sandbox_mode",
            "model_reasoning_effort",
            "developer_instructions",
        }
        assert document["name"] == profile_name
        assert document["sandbox_mode"] == "read-only"
        instructions = document["developer_instructions"]
        assert isinstance(instructions, str)
        _assert_advisory_instructions(instructions)


@pytest.mark.parametrize(
    "grant",
    [
        "Act as the shared director and publish a binding decision.",
        "Use coordination/bin/send-event to publish findings.",
        "Consume shared state before analyzing the range.",
        "Issue a binding GO after review.",
        # operator2's probe against 31e5cbf..b1c6c80: the retired binding
        # reintroduced by wording that never names index-agy-.
        "Export GIT_INDEX_FILE=/tmp/seat-specific-index before inspecting.",
    ],
)
def test_catalog_guardrail_check_rejects_contradictory_authority_grants(
    repo_root: Path, grant: str
) -> None:
    document = tomllib.loads(
        (repo_root / ".agy" / "agents" / "readiness-bridge.toml").read_text(
            encoding="utf-8"
        )
    )
    instructions = document["developer_instructions"]
    assert isinstance(instructions, str)

    with pytest.raises(AssertionError):
        _assert_advisory_instructions(instructions + "\n" + grant)


def test_agy_catalog_readme_describes_advisory_profiles_without_launch_instructions(
    repo_root: Path,
) -> None:
    text = (repo_root / ".agy" / "agents" / "README.md").read_text(encoding="utf-8")

    assert "read-only advisory profiles" in text
    assert "parent or local caller" in text
    assert "No direct launch instructions are provided." in text
    assert "protocol-director.toml" not in text
    assert "protocol-operator.toml" not in text
    assert "protocol-coordinator.toml" not in text
    assert "coordination/bin/agy-seat" not in text
    assert "~/.agy" not in text
