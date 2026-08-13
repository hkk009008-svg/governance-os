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
    assert "Do not add a relay daemon" in text
    assert "python3 scripts/status.py snapshot" in text
    assert "python scripts/status.py snapshot" not in text


def test_claude_peer_relay_defaults_are_low_friction_but_machine_bounded() -> None:
    settings = json.loads(_read(".claude/settings.json"))

    assert settings["isolatePeerMachines"] is True
    assert settings["workflowSizeGuideline"] == "small"
    assert "crossSessionInbound" not in settings

    adapter = _read("docs/protocol/claude/continuation.md")
    assert "native session listing and peer messaging" in adapter
    assert "coordination/bin/send-event" in adapter
