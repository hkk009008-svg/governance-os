from __future__ import annotations

import shlex
from pathlib import Path

import pytest

import codex_protocol_model as model
import protocol_doctor as doctor


ROOT = Path(__file__).resolve().parents[2]
STALE_SELECTORS = (
    "tests/unit/test_codex_protocol_artifacts.py",
    "tests/unit/test_protocol_capacity_board.py",
    "tests/unit/test_coordination_bin.py",
    "tests/unit/test_check_coordination.py",
    "tests/unit/test_protocol_capacity.py",
    "tests/unit/test_claude_task_connector.py",
)
CURRENT_PROTOCOL_TESTS = (
    "tests/unit/test_imports_smoke.py",
    "tests/unit/test_protocol_mailbox.py",
    "tests/unit/test_status.py",
    "tests/unit/test_coordination_tooling.py",
    "tests/unit/test_ceremony_gates.py",
    "tests/unit/test_protocol_doc_integrity.py",
    "tests/unit/test_protocol_prompt_sync.py",
    "tests/unit/test_codex_protocol_model.py",
    "tests/unit/test_model_families_config.py",
    "tests/unit/test_compact_pair_loop.py",
    "tests/unit/test_provider_surface_map.py",
    "tests/unit/test_harness_preflight.py",
    "tests/unit/test_app_integration.py",
    "tests/unit/test_team_mcp.py",
    "tests/unit/test_team_messages.py",
    "tests/unit/test_team_security.py",
    "tests/unit/test_claude_hook_isolation.py",
    "tests/unit/test_codex_hook_lifecycle.py",
    "tests/unit/test_codex_ledger_bridge.py",
)
REQUIRED_LEDGER_DOC_PHRASES = (
    "Pipeline owns the shared engineering and review boundary",
    "registered `evidence-ledger` target",
    "Do not work",
    "user Content checkout",
    "bin/pipeline target --target evidence-ledger --print-path",
    "pipeline/ledger_start_guard.py --seat <author|reviewer> --wave 2",
    "native Git index",
    "temporary formal responsibility",
    "AGY may co-direct",
    "push, merge, release",
    "Record both repository heads only when ownership or context really transfers",
)
# AGENTS.md deliberately absent: the universal router names no product
# target; per-task routes resolve through pipeline/target_binding.py
# (context-pruning PR 2).
DOC_SURFACES = (
    "docs/protocol/codex/continuation.md",
    "docs/protocol/protocol-assembly-map.md",
)
CORE_CODEX_ROLE_PROMPTS = (
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ledger_start_guard_cli_rejects_obsolete_resume_flag(capsys):
    import ledger_start_guard

    with pytest.raises(SystemExit) as exc:
        ledger_start_guard.main(
            [
                "--seat",
                "author",
                "--resume-from",
                "coordination/mailbox/sent/route.md@" + "a" * 40,
            ]
        )

    assert exc.value.code == 2
    assert "unrecognized arguments: --resume-from" in capsys.readouterr().err


def test_ledger_route_guidance_accepts_only_structured_safe_scope(tmp_path):
    import ledger_start_guard

    worktree = tmp_path / "target"
    body = (
        f"Target worktree: {worktree}\n"
        f"Accepted target HEAD: {'a' * 40}\n"
        "Only edit ignored/prose.py\n"
        "\n## Target Allowed Paths\n"
        "- exact/path.py\n"
    )

    assert ledger_start_guard.parse_route_guidance_body(body) == (
        ledger_start_guard.RouteGuidance(
            worktree=worktree.as_posix(),
            accepted_target_head="a" * 40,
            allowed_paths=("exact/path.py",),
        )
    )
    for invalid in (
        body + f"Target worktree: {tmp_path / 'duplicate'}\n",
        body.replace("a" * 40, "A" * 40),
        body.replace("exact/path.py", "../escape.py"),
        body.replace("exact/path.py", "/absolute.py"),
        body.replace("exact/path.py", "wild/*.py"),
    ):
        with pytest.raises(ValueError):
            ledger_start_guard.parse_route_guidance_body(invalid)


def test_ledger_route_guidance_keeps_committed_legacy_aliases(tmp_path):
    import ledger_start_guard

    guidance = ledger_start_guard.parse_route_guidance_body(
        f"Route worktree: {tmp_path / 'target'}\n"
        f"Target reviewed head: {'b' * 40}\n"
        "\n## Allowed Paths\n"
        "- legacy/path.py\n"
    )

    assert guidance == ledger_start_guard.RouteGuidance(
        worktree=(tmp_path / "target").as_posix(),
        accepted_target_head="b" * 40,
        allowed_paths=("legacy/path.py",),
    )


def test_model_verification_commands_are_current():
    rendered = " ".join(model.CODEX_VERIFICATION_COMMANDS)
    for selector in CURRENT_PROTOCOL_TESTS:
        assert selector in rendered
        assert (ROOT / selector).exists(), selector
    for selector in STALE_SELECTORS:
        assert selector not in rendered


def test_protocol_doctor_derives_verification_commands_from_model():
    expected_pytest = shlex.split(model.CODEX_VERIFICATION_COMMANDS[0])[1:]
    expected_smoke = shlex.split(model.CODEX_VERIFICATION_COMMANDS[1])[1:]
    commands = doctor.verification_commands("/tmp/python")

    assert commands == [
        ["/tmp/python", *expected_pytest],
        ["/tmp/python", *expected_smoke],
    ]

    flattened = " ".join(part for command in commands for part in command)
    for selector in CURRENT_PROTOCOL_TESTS:
        assert selector in flattened
    for selector in STALE_SELECTORS:
        assert selector not in flattened


def test_protocol_doctor_defaults_current_and_makes_history_explicit(monkeypatch):
    """The ordinary doctor omits retired lineage checks."""

    commands: list[list[str]] = []

    def fake_run_command(cmd, cwd, timeout=120):
        commands.append(cmd)
        return doctor.CommandResult(cmd, 0, "", "")

    monkeypatch.setattr(doctor, "run_command", fake_run_command)

    assert doctor.main([]) == 0
    rendered = [" ".join(command) for command in commands]
    assert any("check_coordination.py" in line for line in rendered)
    assert any("target_binding.py --check" in line for line in rendered)
    assert not any("route_lineage.py --check" in line for line in rendered)
    assert not any("capacity" in line for line in rendered)
    assert not any("--require-packets" in line for line in rendered)

    commands.clear()
    assert doctor.main(["--history"]) == 0
    rendered = [" ".join(command) for command in commands]
    assert any("check_coordination.py --history" in line for line in rendered)
    assert any("route_lineage.py --check" in line for line in rendered)


def test_ledger_bridge_doc_exists_and_names_required_boundaries():
    text = " ".join(
        _read("docs/protocol/codex/ledger-cli-adoption.md").split()
    )
    for phrase in REQUIRED_LEDGER_DOC_PHRASES:
        assert phrase in text


def test_doc_surfaces_route_to_ledger_bridge_without_stale_selectors():
    for path in DOC_SURFACES:
        text = _read(path)
        assert "docs/protocol/codex/ledger-cli-adoption.md" in text
        for selector in STALE_SELECTORS:
            assert selector not in text
    assert "evidence-ledger" not in _read(
        ".agents/skills/four-seat-protocol/SKILL.md"
    )


def test_core_codex_role_prompts_are_thin_deltas_with_ledger_pointer():
    for path in CORE_CODEX_ROLE_PROMPTS:
        text = _read(path)
        assert "docs/protocol/codex/ledger-cli-adoption.md" in text
        assert "pipeline/codex_protocol_model.py" in text
        assert "pipeline/ledger_start_guard.py --seat" not in text
        assert "env -u GIT_INDEX_FILE" not in text
        assert len(text.splitlines()) <= 30, path


def test_readiness_prompt_keeps_mutation_boundary_and_coordinator_is_retired():
    readiness = " ".join(_read(".codex/agents/readiness-bridge.toml").split())
    assert "read-only" in readiness
    assert "Do not claim work" in readiness
    assert not (ROOT / ".codex/agents/protocol-coordinator.toml").exists()


def test_ledger_start_guard_cli_rejects_content_kernel():
    import ledger_start_guard
    import target_binding

    forbidden = target_binding.forbidden_roots()[0]
    result = ledger_start_guard.build_guard(
        seat="reviewer",
        root=forbidden,
        kernel=ledger_start_guard.PIPELINE_KERNEL,
    )

    assert not result.ok
    assert f"Refusing `{forbidden.as_posix()}` for ledger work." in "\n".join(result.errors)


def test_ledger_start_guard_cli_prints_route_and_first_commands(tmp_path, capsys, monkeypatch):
    import ledger_start_guard
    import target_binding

    ledger = tmp_path / "evidence-ledger"
    ledger.mkdir()
    monkeypatch.setenv("GOVERNANCE_TARGET_PATH", str(ledger))

    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    route = sent / "2026-07-07T09-36-23Z-coordinator-to-all-coordination.md"
    route.write_text(
        "# Coordinator -> All: ledger alignment task-board\n\n"
        "Task-board: ledger-t14-align-2026-07-07\n"
        f"Target repo: {ledger}\n",
        encoding="utf-8",
    )

    rc = ledger_start_guard.main(
        [
            "--root",
            str(tmp_path),
            "--kernel",
            str(tmp_path),
            "--seat",
            "reviewer",
            "--wave",
            "2",
        ]
    )

    out = capsys.readouterr().out
    target = target_binding.resolve_target()
    assert rc == 0
    assert "Ledger seat start guard: PASS" in out
    assert "Active route: coordination/mailbox/sent/2026-07-07T09-36-23Z-coordinator-to-all-coordination.md" in out
    assert "seat_status.py" not in out
    assert "env -u GIT_INDEX_FILE" not in out
    assert f"git -C {target.path.as_posix()} status --short --branch" in out


def test_ledger_start_guard_surfaces_route_base_and_worktree_before_normal_checkout(tmp_path, capsys):
    import ledger_start_guard

    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    route = sent / "2026-07-08T14-39-41Z-coordinator-to-all-coordination.md"
    route.write_text(
        "# Coordinator -> All: ledger implementation route\n\n"
        "Task-board: ledger-phase2-task23\n"
        "Target repo: /Users/hyungkoookkim/evidence-ledger\n"
        "Route base: `origin/main @ abc1234`\n"
        "Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-task23`\n",
        encoding="utf-8",
    )

    rc = ledger_start_guard.main(
        [
            "--root",
            str(tmp_path),
            "--kernel",
            str(tmp_path),
            "--seat",
            "author",
            "--wave",
            "2",
        ]
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "route base: origin/main @ abc1234" in out
    assert "route worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-task23" in out
    assert (
        "git -C "
        "/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-task23 "
        "status --short --branch"
    ) in out
    assert "normal target checkout may be stale; use the route worktree above" in out
    assert "git -C /Users/hyungkoookkim/evidence-ledger status" not in out
    assert "env -u GIT_INDEX_FILE" not in out
