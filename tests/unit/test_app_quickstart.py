"""Contract pins for the desktop-first four-provider operating guide."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs/protocol/app-quickstart.md"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_every_provider_adapter_routes_to_one_app_quickstart() -> None:
    for provider in ("claude", "codex", "agy", "cursor"):
        adapter = _read(f"docs/protocol/{provider}/continuation.md")
        assert "docs/protocol/app-quickstart.md" in adapter, provider


def test_quickstart_names_unique_native_capacity_and_one_cross_app_path() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for heading in (
        "## Claude Desktop Code",
        "## Codex desktop",
        "## Antigravity / AGY",
        "## Cursor Desktop",
        "## Cross-app communication without another messaging layer",
    ):
        assert heading in text

    for capability in (
        "direct, attributed messaging",
        "task-tree coordination",
        "commentable plan, task, diff, walkthrough",
        "deepest IDE surface",
    ):
        assert capability in text

    assert "coordination/bin/send-event" in text
    assert "`send-event` stages but does not commit or land" in compact
    assert (
        "containing commit is landed and the receiving checkout is synchronized"
        in compact
    )
    assert "Do not add a generic relay daemon" in text
    assert "python3 scripts/status.py snapshot" in text
    assert "python scripts/status.py snapshot" not in text


def test_quickstart_carries_current_host_safety_limits() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    assert "2.1.224" in text
    assert "Antigravity Desktop 2.6.0" in text
    assert "preToolUse" in text
    assert "does not currently enforce" in compact
    assert "beforeMCPExecution" in _read("docs/protocol/cursor/continuation.md")
    assert "Do not create one inside a reserved seat worktree" in text
    assert ".agents/agents/" in _read("docs/protocol/agy/continuation.md")


def test_claude_peer_relay_defaults_are_low_friction_but_machine_bounded() -> None:
    settings = json.loads(_read(".claude/settings.json"))

    assert settings["isolatePeerMachines"] is True
    assert settings["workflowSizeGuideline"] == "small"
    assert "crossSessionInbound" not in settings

    adapter = _read("docs/protocol/claude/continuation.md")
    assert "native session listing and peer messaging" in adapter
    assert "coordination/bin/send-event" in adapter
