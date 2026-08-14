"""Contract pins for the supported desktop-app guide."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs/protocol/app-quickstart.md"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_supported_provider_adapters_route_to_one_app_quickstart() -> None:
    for provider in ("claude", "codex"):
        adapter = _read(f"docs/protocol/{provider}/continuation.md")
        assert "docs/protocol/app-quickstart.md" in adapter, provider


def test_quickstart_names_supported_native_capacity_and_shared_path() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for heading in (
        "## Claude Desktop Code",
        "## Codex desktop",
        "## Cross-app communication",
    ):
        assert heading in text

    assert "direct, attributed messaging" in text
    assert "task-tree coordination" in text
    assert "coordination/bin/send-event" in text
    assert "stages but does not commit or land" in compact
    assert "one named, persistent Claude Agent SDK peer" in text
    assert "private RPC/socket" in text
    assert "Native `SendMessage` has no end-to-end delivery" in text
    assert (
        "coordination/bin/pipeline-python scripts/status.py snapshot" in text
    )
    assert "python3 scripts/status.py snapshot" not in text
    assert "`python scripts/status.py snapshot" not in text


def test_codex_desktop_lifecycle_is_native_reversible_and_non_authoritative() -> None:
    guide = GUIDE.read_text(encoding="utf-8")
    adapter = _read("docs/protocol/codex/continuation.md")
    guide_compact = " ".join(guide.split())
    adapter_compact = " ".join(adapter.split())

    for phrase in (
        "Rename and pin active tasks",
        "read older turns with paginated history",
        "Archive completed tasks reversibly",
        "Fork only completed history",
        "branch, staged, unstaged, or last-turn review",
        "Never automate hard deletion",
        "only when the user explicitly asks for one",
    ):
        assert phrase in guide_compact

    assert "does not replace committed checkpoints" in guide_compact
    assert (
        "task metadata grants no role, review, or effect authority"
        in adapter_compact
    )
    assert "archive or unarchive" in adapter_compact


def test_claude_peer_relay_defaults_are_low_friction_but_machine_bounded() -> None:
    settings = json.loads(_read(".claude/settings.json"))

    assert settings["isolatePeerMachines"] is True
    assert settings["workflowSizeGuideline"] == "small"
    assert "crossSessionInbound" not in settings

    adapter = _read("docs/protocol/claude/continuation.md")
    assert "native session listing and peer messaging" in adapter
    assert "pipeline-codex-bridge" in adapter
    assert "coordination/bin/send-event" in adapter


def test_both_adapters_default_to_the_supported_transient_task_connector() -> None:
    contract = _read("docs/protocol/claude/task-connector.md")
    compact = " ".join(contract.split())
    assert "ListAgents" in contract
    assert "SendMessage" in contract
    assert "local_*" in contract
    assert "claude_bridge_send" in contract
    assert "claude_bridge_wait" in contract
    assert "five-tool contract" in contract.lower()
    assert "cannot" in contract and "grant authority" in compact

    for provider in ("claude", "codex"):
        adapter = _read(f"docs/protocol/{provider}/continuation.md")
        assert "docs/protocol/claude/task-connector.md" in adapter
        assert "pipeline-codex-bridge" in adapter


def test_active_guides_use_available_python_bootstrap_commands() -> None:
    for relative in (
        "docs/protocol/app-quickstart.md",
        "docs/protocol/codex/continuation.md",
        "docs/protocol/codex/ledger-cli-adoption.md",
        "docs/protocol/claude/task-connector.md",
    ):
        text = _read(relative)
        assert "`python scripts/" not in text, relative
        assert "`python3 scripts/" not in text, relative
        assert "`python -m " not in text, relative


def test_connector_wrapper_does_not_accept_an_ambient_python_override() -> None:
    wrapper = _read("coordination/bin/claude-task-connector")
    assert "PIPELINE_CLAUDE_CONNECTOR_PYTHON" not in wrapper


def test_repository_python_wrapper_is_present_and_executable() -> None:
    wrapper = ROOT / "coordination/bin/pipeline-python"
    assert wrapper.is_file()
    assert wrapper.stat().st_mode & 0o111
