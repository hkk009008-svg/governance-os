"""Drift gate for the Cursor adoption surfaces.

Keeps the Cursor-native surfaces (runtime adapter, launcher, hooks, mailbox
wrappers, continuation, role prompts, scoped rule, assembly-map pointers)
truthful and mutually consistent without duplicating canonical protocol prose.
This file is Cursor-scoped on purpose so it does not disturb the concurrently
edited shared prompt-sync gate.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = "scripts/codex_protocol_model.py"
LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
ROLE_FILES = ("director", "operator", "coordinator")


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_cursor_scripts_and_shims_are_present_and_delegating() -> None:
    for relative in (
        "scripts/cursor_protocol_model.py",
        "scripts/cursor_seat_launcher.py",
        "scripts/cursor_hook_policy.py",
        "scripts/cursor_mailbox.py",
        "coordination/bin/cursor-seat",
        "coordination/bin/cursor-publish",
        "coordination/bin/cursor-consume",
        ".cursor/hooks/seat-policy",
    ):
        assert (ROOT / relative).is_file(), relative

    # The interactive wrappers must delegate to the fixed writers, not reinvent.
    mailbox = _read("scripts/cursor_mailbox.py")
    assert "send-event" in mailbox
    assert "consume-events" in mailbox
    assert "mailbox_writer" not in mailbox  # never bypass the fixed writer


def test_cursor_naming_adapter_stays_thin_over_canonical() -> None:
    source = _read("scripts/cursor_protocol_model.py")
    assert "import codex_protocol_model" in source
    # The adapter renames onto the canonical contract; it must not re-derive it.
    assert "SEAT_BEHAVIOR_SOURCE" not in source
    assert "infer_runtime_env" in source


@pytest.mark.parametrize("role", ROLE_FILES)
def test_role_prompts_bind_seat_identity_and_cite_canonical(role: str) -> None:
    text = _read(f"docs/protocol/cursor/roles/{role}.md")
    assert CANONICAL in text
    assert "docs/protocol/cursor/continuation.md" in text
    assert role.capitalize() in text.splitlines()[0]


def test_launcher_reads_role_prompts_from_the_canonical_location() -> None:
    launcher = _read("scripts/cursor_seat_launcher.py")
    assert '"protocol"' in launcher and '"cursor"' in launcher and '"roles"' in launcher
    for role in ROLE_FILES:
        assert (ROOT / "docs/protocol/cursor/roles" / f"{role}.md").is_file()


def test_continuation_adapter_is_present_and_points_at_kernel() -> None:
    text = _read("docs/protocol/cursor/continuation.md")
    for marker in (
        CANONICAL,
        "scripts/cursor_protocol_model.py",
        "coordination/bin/cursor-seat",
        "coordination/bin/cursor-publish",
        ".cursor/hooks.json",
        "Canonical Compact Pair Invariant: scripts/codex_protocol_model.py",
        "readiness bridge",
    ):
        assert marker in text, marker
    # Same terminal-ceremony ban the shared active-surface gate enforces.
    assert "Exact Next Trigger" not in text


def test_scoped_rule_declares_readiness_default_and_advisor_subagents() -> None:
    text = _read(".cursor/rules/cursor-seats.mdc")
    assert "alwaysApply: true" in text
    assert "readiness bridge" in text
    assert "advisor" in text.casefold()
    assert "cannot spawn" in text
    assert "cursor-publish" in text


def test_assembly_map_points_at_every_cursor_surface() -> None:
    text = _read("docs/protocol/protocol-assembly-map.md")
    for marker in (
        "docs/protocol/cursor/continuation.md",
        "docs/protocol/cursor/roles/",
        "scripts/cursor_seat_launcher.py",
        ".cursor/hooks.json",
    ):
        assert marker in text, marker


def test_root_router_points_to_cursor_adoption() -> None:
    router = _read("AGENTS.md")

    assert "docs/protocol/cursor/continuation.md" in router


def test_hooks_wire_seat_policy_and_fail_closed_on_sensitive_events() -> None:
    config = json.loads(_read(".cursor/hooks.json"))
    hooks = config["hooks"]
    assert set(hooks) >= {
        "sessionStart",
        "preToolUse",
        "beforeShellExecution",
        "subagentStart",
    }
    for event in ("preToolUse", "beforeShellExecution", "subagentStart"):
        entries = hooks[event]
        assert entries, event
        for entry in entries:
            assert entry["command"] == ".cursor/hooks/seat-policy", event
            assert entry.get("failClosed") is True, event


def test_gitignore_excludes_cursor_seat_runtime_and_indexes() -> None:
    gitignore = _read(".gitignore")
    assert ".cursor/runtime/" in gitignore
    assert ".git/index-cursor-*" in gitignore
