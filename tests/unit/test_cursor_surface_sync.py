"""Drift gate for Cursor Desktop app-seat surfaces."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = "scripts/codex_protocol_model.py"
ROLE_FILES = ("director", "operator", "coordinator")


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_cursor_app_scripts_and_shims_are_present() -> None:
    for relative in (
        "scripts/cursor_app_binding.py",
        "scripts/cursor_protocol_model.py",
        "scripts/cursor_seat_launcher.py",
        "scripts/cursor_hook_policy.py",
        "scripts/cursor_mailbox.py",
        "scripts/cursor_review_snapshot.py",
        "scripts/cursor_land_gate.py",
        ".cursor/hooks/seat-policy",
        ".cursor/skills/review-next/SKILL.md",
        "coordination/bin/cursor-seat",
        "coordination/bin/cursor-publish",
        "coordination/bin/cursor-consume",
    ):
        assert (ROOT / relative).is_file(), relative


def test_retired_scaffolding_is_absent() -> None:
    for relative in (
        "scripts/cursor_apply_bundle.py",
        "scripts/launch_all_cursor_seats.sh",
        "coordination/bin/cursor-apply-bundle",
        "tests/unit/test_cursor_apply_bundle.py",
        "tests/unit/test_cursor_hook_env_fallback.py",
    ):
        assert not (ROOT / relative).exists(), relative


def test_mailbox_front_door_delegates_to_fixed_writers() -> None:
    source = _read("scripts/cursor_mailbox.py")
    assert "send-event" in source
    assert "consume-events" in source
    assert "subprocess.run" in source
    assert "resolve_registered_session" in source
    assert "mailbox_writer" not in source
    assert "subprocess.call" not in source


def test_hook_policy_is_write_governed_with_one_identity() -> None:
    source = _read("scripts/cursor_hook_policy.py")
    assert "resolve_registered_session" in source
    assert "_SAFE_GIT_READS" not in source
    assert "_SAFE_READ_COMMANDS" not in source
    assert "_ORIENTATION_SCRIPTS" not in source
    assert "_binding_command_environment" not in source
    assert "validate_payload_session" not in source
    assert "_EPHEMERAL_WRITE_TARGETS" in source


def test_cursor_naming_adapter_stays_thin_over_canonical() -> None:
    source = _read("scripts/cursor_protocol_model.py")
    assert "import codex_protocol_model" in source
    assert "SEAT_BEHAVIOR_SOURCE" not in source
    assert "infer_runtime_env" in source


@pytest.mark.parametrize("role", ROLE_FILES)
def test_role_docs_bind_app_identity_and_cite_canonical(role: str) -> None:
    text = _read(f"docs/protocol/cursor/roles/{role}.md")
    assert CANONICAL in text
    assert "docs/protocol/cursor/continuation.md" in text
    assert role.capitalize() in text.splitlines()[0]
    assert "top-level chat" in text


def test_launcher_is_read_only_app_diagnostic() -> None:
    launcher = _read("scripts/cursor_seat_launcher.py")
    lowered = launcher.casefold()
    assert "read-only" in lowered
    assert "agents window" in lowered
    assert "execvpe" not in lowered
    assert "cursor-agent" not in lowered
    assert "cursor_sdk" not in lowered


def test_cursor_land_gate_uses_native_worktree_index() -> None:
    source = _read("scripts/cursor_land_gate.py")
    assert "reject GIT_INDEX_FILE" in source
    assert '"-u"' not in source
    assert "test_cursor_apply_bundle" not in source
    assert "test_cursor_hook_env_fallback" not in source


def test_continuation_documents_app_runtime_and_minimal_handoff() -> None:
    text = _read("docs/protocol/cursor/continuation.md")
    for marker in (
        CANONICAL,
        "scripts/cursor_protocol_model.py",
        "scripts/cursor_app_binding.py",
        "scripts/cursor_review_snapshot.py",
        "coordination/bin/cursor-publish",
        ".cursor/hooks.json",
        "Cursor Desktop/Agents Window",
        "cursor-seat/director",
        "conversation_id",
        "/review-next",
        "one baseline manual app handoff",
        "Reads are free",
        "in-app approval",
    ):
        assert marker in text, marker
    assert "cursor-seat build" not in text
    assert "do not require `cursor-agent`" in text


def test_scoped_rule_declares_binding_and_advisor_subagents() -> None:
    text = _read(".cursor/rules/cursor-seats.mdc")
    assert "alwaysApply: true" in text
    assert "readiness bridge" in text
    assert "conversation_id" in text
    assert "selected model ID" in text
    assert "native Git index" in text
    assert "optional advisors" in text
    assert "cursor-publish" in text


def test_assembly_map_points_at_app_surfaces() -> None:
    text = _read("docs/protocol/protocol-assembly-map.md")
    for marker in (
        "docs/protocol/cursor/continuation.md",
        "docs/protocol/cursor/roles/",
        "scripts/cursor_app_binding.py",
        ".cursor/skills/review-next/SKILL.md",
        ".cursor/hooks.json",
    ):
        assert marker in text, marker


def test_hooks_wire_policy_once_and_fail_closed_on_sensitive_events() -> None:
    config = json.loads(_read(".cursor/hooks.json"))
    hooks = config["hooks"]
    assert set(hooks) >= {
        "sessionStart",
        "preToolUse",
        "beforeShellExecution",
        "subagentStart",
    }
    for event in ("preToolUse", "beforeShellExecution", "subagentStart"):
        for entry in hooks[event]:
            assert entry["command"] == ".cursor/hooks/seat-policy"
            assert entry.get("failClosed") is True
    # Shell commands are evaluated exactly once, by beforeShellExecution.
    assert "Shell" not in hooks["preToolUse"][0]["matcher"]


def test_root_router_points_to_cursor_adoption() -> None:
    assert "docs/protocol/cursor/continuation.md" in _read("AGENTS.md")


def test_cursor_surfaces_have_no_retired_product_destination() -> None:
    retired = "foul" + "play"
    for relative in (
        "AGENTS.md",
        "ARCHITECTURE.md",
        "README.md",
        "OPERATIONS.md",
        "governance.toml",
        ".cursor/rules/cursor-seats.mdc",
        ".cursor/rules/pipeline-os-cursor.mdc",
        "docs/protocol/cursor/continuation.md",
        "docs/protocol/protocol-assembly-map.md",
    ):
        lowered = _read(relative).casefold()
        assert retired not in lowered
        assert retired.replace("play", " play") not in lowered
    for relative in (
        f".cursor/rules/{retired}-target.mdc",
        f"docs/protocol/cursor/{retired}-adoption.md",
        "tools/test.sh",
    ):
        assert not (ROOT / relative).exists()


@pytest.mark.parametrize(
    "relative",
    (
        "coordination/bin/cursor-publish",
        "coordination/bin/cursor-consume",
    ),
)
def test_cursor_bin_shims_import_without_ambient_pythonpath(relative: str) -> None:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("GIT_INDEX_FILE", None)
    result = subprocess.run(
        ["/bin/bash", str(ROOT / relative), "--help"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "ModuleNotFoundError" not in result.stderr
