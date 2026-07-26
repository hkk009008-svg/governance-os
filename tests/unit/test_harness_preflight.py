"""Tests for the pre-dispatch harness readiness check.

Each case encodes a failure observed on 2026-07-26 that exited 0 and produced
silence. The point of the check is that these become loud before spend, so a
test that passed while the check was blind would defeat it entirely.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import harness_preflight as preflight


def _settings(tmp_path: Path, allow: list[str]) -> Path:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"permissions": {"allow": allow}}), encoding="utf-8")
    return path


def _failures(results) -> list[str]:
    return [result.detail for result in results if not result.ok]


def test_agy_missing_command_grants_is_not_ready(tmp_path: Path) -> None:
    """AGY auto-denies a tool it cannot prompt for and still exits 0.

    Granting read_file alone got the observed run past its first denial and
    straight into a second one, so a check that stopped at file reads would
    have called a harness ready that cannot run a single evidence command.
    """
    settings = _settings(tmp_path, ["read_file"])

    results = preflight.check_agy(settings)

    failures = _failures(results)
    assert any("missing grants" in detail for detail in failures)
    assert any(command in detail for detail in failures for command in ("git diff", "pytest"))


def test_agy_with_every_review_grant_is_ready(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path,
        ["read_file", *(f"command({command})" for command in preflight.REVIEW_COMMANDS)],
    )

    results = preflight.check_agy(settings)

    assert _failures(results) == []


def test_agy_missing_read_file_is_reported_separately(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path, [f"command({command})" for command in preflight.REVIEW_COMMANDS]
    )

    results = preflight.check_agy(settings)

    assert any("read_file NOT granted" in detail for detail in _failures(results))


def test_agy_absent_settings_is_not_ready(tmp_path: Path) -> None:
    results = preflight.check_agy(tmp_path / "nope.json")

    assert any("settings absent" in detail for detail in _failures(results))


def test_codex_ambient_runtime_authority_is_not_ready(tmp_path: Path) -> None:
    """A project config granting approvals-off is a launch hazard, not readiness.

    The reverted config carried approval_policy and sandbox_mode, and any Codex
    launch without explicit flags would have inherited approvals off with full
    disk access. A preflight blind to that would call the dangerous launch fine.
    """
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        'personality = "friendly"\napproval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )

    results = preflight.check_codex(tmp_path)

    ambient = [r for r in results if "project config" in r.detail]
    assert ambient, "the ambient-authority check did not run"
    assert not ambient[0].ok
    assert "approval_policy" in ambient[0].detail
    assert "sandbox_mode" in ambient[0].detail


def test_codex_clean_project_config_is_ready(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        'personality = "friendly"\n', encoding="utf-8"
    )

    results = preflight.check_codex(tmp_path)

    ambient = [r for r in results if "project config" in r.detail]
    assert ambient, "the ambient-authority check did not run"
    assert ambient[0].ok


def test_cursor_unregistered_seat_is_not_ready(tmp_path: Path) -> None:
    """Pointed at an unbound seat, Cursor reports itself unbound and does nothing.

    The observed run degraded to a readiness posture because --workspace was the
    main checkout rather than the seat worktree, and still exited 0.
    """
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"bindings": {}}), encoding="utf-8")

    results = preflight.check_cursor("operator", registry)

    assert any("not registered" in detail for detail in _failures(results))


def test_cursor_missing_worktree_is_not_ready(tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {"bindings": {"operator": {
                "root": str(tmp_path / "absent-worktree"),
                "branch": "cursor-seat/operator",
                "model_id": "composer-2.5",
            }}}
        ),
        encoding="utf-8",
    )

    results = preflight.check_cursor("operator", registry)

    assert any("MISSING" in detail for detail in _failures(results))


def test_main_fails_closed_when_any_check_fails(tmp_path: Path, capsys) -> None:
    """Readiness must be a nonzero exit, because every real failure returned 0."""
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        'approval_policy = "never"\n', encoding="utf-8"
    )

    code = preflight.main(["codex", "--repo-root", str(tmp_path)])

    assert code == 1
    assert "NOT READY" in capsys.readouterr().out


def test_review_commands_cover_evidence_and_publication() -> None:
    """A harness that reads but cannot publish is not a usable Operator.

    Evidence-only readiness is exactly Cursor's real posture, so the grant list
    has to span both halves or the check would pass a harness that can never
    issue a verdict.
    """
    joined = " ".join(preflight.REVIEW_COMMANDS)

    assert "git diff" in joined
    assert "pytest" in joined
    assert "send-event" in joined
    assert "git commit" in joined
