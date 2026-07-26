"""Tests for the pre-dispatch harness readiness check.

Each case encodes a failure observed on 2026-07-26 that exited 0 and produced
silence. The point of the check is that these become loud before spend, so a
test that passed while the check was blind would defeat it entirely.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import agy_seat_launcher as launcher
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


def _binary_rows(results) -> list:
    return [result for result in results if result.detail.startswith("binary ")]


def _capability_rows(results) -> list:
    return [result for result in results if not result.detail.startswith("binary ")]


# Every grant row a fully granted `check_agy` must report, named rather than
# counted. A non-empty check passes on one row, so an early return after the
# first passing grant would leave the rest unreported and still look covered:
# with only `command(git diff)` granted, the missing pytest, send-event and
# commit grants were never named. The tuple is what notices that.
AGY_GRANT_DETAILS = ("read_file granted", "review commands granted")
AGY_PARITY_OK = "declared flags all defined by the installed CLI"


def _grant_everything(tmp_path: Path) -> Path:
    return _settings(
        tmp_path,
        ["read_file", *(f"command({command})" for command in preflight.REVIEW_COMMANDS)],
    )


def _install(monkeypatch: pytest.MonkeyPatch, name: str | None) -> None:
    """Put exactly *name* on PATH as far as `_binary` can tell, or nothing."""
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda probe: f"/probe/bin/{probe}" if probe == name else None,
    )


def _cli_defines(monkeypatch: pytest.MonkeyPatch, flags) -> None:
    monkeypatch.setattr(preflight, "_agy_defined_flags", lambda _exe: flags)


@pytest.mark.parametrize("installed", ("agy", "antigravity"))
def test_agy_with_every_review_grant_is_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, installed: str
) -> None:
    """Full readiness, with the binary's presence supplied rather than borrowed.

    This asserted that nothing fails, which is a claim about the grants — but
    `check_agy` also reports whether the CLI is on PATH, so the assertion only
    held on a host that happened to have AGY installed. Committed CI installs
    `requirements-dev.txt` and no AGY, so it failed there while passing for
    whoever wrote it.

    `shutil.which` is stubbed rather than `_binary`, so the real lookup runs.
    Both accepted names are driven, because a stub answering the first one never
    reaches the second: `_binary` falls back from `agy` to `antigravity`, and a
    regression dropping that fallback is invisible to a host where the first
    name resolves.
    """
    _install(monkeypatch, installed)
    _cli_defines(monkeypatch, launcher.AGY_CLI_FLAGS)

    results = preflight.check_agy(_grant_everything(tmp_path))

    assert _failures(results) == []
    assert [result.detail for result in _binary_rows(results)] == [
        f"binary /probe/bin/{installed}"
    ]
    # Readiness may not be reachable without the external gate having run, so
    # its passing row is required here rather than merely permitted.
    assert AGY_PARITY_OK in [result.detail for result in results]


def test_agy_capability_rows_run_when_the_binary_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing CLI fails on its own row and silences none of the others.

    The capability checks deliberately keep running when the binary is absent,
    so one report can say both things: the grants are right, and nothing can
    execute. That is only safe while the binary row still fails, because
    capability rows reading PASS is precisely what would be mistaken for
    readiness — the reason the early return was removed in the first place.

    Every expected capability row is named, not merely counted as non-empty. An
    early return after the first passing grant satisfied a non-empty check while
    leaving the remaining grants unreported, which is the same defect this test
    exists to catch arriving one row later.
    """
    _install(monkeypatch, None)

    results = preflight.check_agy(_grant_everything(tmp_path))

    assert [result.ok for result in _binary_rows(results)] == [False]
    capability = _capability_rows(results)
    # The grant rows, all of them, and no parity row: parity is a question about
    # a binary that is not there, and asking it would report a second failure
    # for one cause.
    assert tuple(result.detail for result in capability) == AGY_GRANT_DETAILS
    assert [result.ok for result in capability] == [True] * len(capability)
    # Exactly the binary row fails, so every capability check ran and passed.
    assert _failures(results) == ["binary NOT FOUND on PATH"]


def test_agy_flag_parity_fails_when_the_cli_drops_a_declared_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The external gate, and the reason it lives here rather than in a test.

    `AGY_CLI_FLAGS` is a committed copy of another program's interface. Every
    check of it against the real CLI was written as a test and therefore skipped
    wherever AGY is absent, which is every CI run, because AGY ships as a
    platform executable with no package or pinned download in this repository.
    So the comparison moved to the place where the binary is guaranteed: the
    pre-dispatch check, which the binary row already fails when it is missing.

    Dropping `--model` is the control because it is the flag every seat emits, so
    a CLI without it starts no seat at all.
    """
    _install(monkeypatch, "agy")
    _cli_defines(monkeypatch, launcher.AGY_CLI_FLAGS - {"--model"})

    results = preflight.check_agy(_grant_everything(tmp_path))

    assert _failures(results) == [
        "declared flags the installed CLI does not define: --model"
    ]
    assert not all(result.ok for result in results)


def test_agy_flag_parity_is_unchecked_rather_than_clean_when_help_is_unreadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unanswerable CLI is not a CLI that agrees with us.

    `_agy_defined_flags` returns None for that, kept apart from the empty set,
    because an empty parse would make every declared flag look undefined and
    turn one broken invocation into a flood of false parity failures. Neither may
    read as parity holding, so both fail — this one for being unanswered.
    """
    _install(monkeypatch, "agy")
    _cli_defines(monkeypatch, None)

    results = preflight.check_agy(_grant_everything(tmp_path))

    assert _failures(results) == [
        "cannot read `agy --help`, so flag parity is unchecked"
    ]


def test_agy_defined_flags_reads_the_installed_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """The parse itself, driven against a captured help shape rather than a host.

    `subprocess.run` is stubbed so this runs in CI, where no AGY exists. The
    shape is AGY's real `--help` layout: a leading-whitespace flag column with
    long names, short aliases and a repeatable default suffix.
    """
    help_text = (
        "Usage of agy:\n"
        "  --add-dir                Add a directory (repeatable) (default [])\n"
        "  --model                  Model for the current CLI session\n"
        "  -c                       Short alias for --continue\n"
        "  not-a-flag               ignored\n"
    )

    def fake_run(_argv, **_kwargs):
        return subprocess.CompletedProcess(_argv, 0, stdout=help_text, stderr="")

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    assert preflight._agy_defined_flags("/probe/bin/agy") == frozenset(
        {"--add-dir", "--model", "-c"}
    )

    monkeypatch.setattr(
        preflight.subprocess, "run",
        lambda _argv, **_k: subprocess.CompletedProcess(_argv, 0, stdout="", stderr=""),
    )
    # Empty is unanswered, never "defines nothing".
    assert preflight._agy_defined_flags("/probe/bin/agy") is None


def test_main_is_not_ready_when_only_the_binary_row_fails(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """Readiness is `main`'s to decide, so `main` is what gets asked.

    Recomputing `all(result.ok ...)` inside a test asserts nothing about the
    program: it restates rows the test already inspected. Measured against a
    `main` that treated a failed AGY binary row as non-fatal, that restatement
    stayed green while `main` printed READY and exited 0 — the exact shape this
    is meant to stop, since a capability-rich report beside a missing binary is
    what reads as readiness.

    `check_agy` is replaced rather than driven, because `main` calls it with no
    argument and so with the real user settings path, which would put this test
    back on the host. What is under test here is the aggregation, not the rows.
    """
    rows = [
        preflight.Result("agy", False, "binary NOT FOUND on PATH", "install the AGY CLI"),
        *(preflight.Result("agy", True, detail) for detail in AGY_GRANT_DETAILS),
    ]
    monkeypatch.setattr(preflight, "check_agy", lambda *_a, **_k: rows)

    code = preflight.main(["agy"])

    printed = capsys.readouterr().out
    assert code == 1
    assert "NOT READY" in printed
    assert "READY\n" not in printed
    # The capability rows still have to be shown; a not-ready verdict that hid
    # what was satisfied would send the operator hunting for the wrong thing.
    for detail in AGY_GRANT_DETAILS:
        assert f"PASS  agy     {detail}" in printed
    assert "FAIL  agy     binary NOT FOUND on PATH" in printed


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
