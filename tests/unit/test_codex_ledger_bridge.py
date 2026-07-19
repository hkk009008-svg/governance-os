from __future__ import annotations

import contextlib
import io
import json
import shlex
import subprocess
from pathlib import Path

import pytest

import codex_protocol_model as model
import continuation_readiness
import protocol_doctor as doctor


ROOT = Path(__file__).resolve().parents[2]
STALE_SELECTORS = (
    "tests/unit/test_codex_protocol_model.py",
    "tests/unit/test_codex_protocol_artifacts.py",
    "tests/unit/test_protocol_capacity_board.py",
    "tests/unit/test_coordination_bin.py",
    "tests/unit/test_check_coordination.py",
)
CURRENT_PROTOCOL_TESTS = (
    "tests/unit/test_imports_smoke.py",
    "tests/unit/test_protocol_mailbox.py",
    "tests/unit/test_status.py",
    "tests/unit/test_coordination_tooling.py",
    "tests/unit/test_ceremony_gates.py",
    "tests/unit/test_protocol_capacity.py",
    "tests/unit/test_protocol_doc_integrity.py",
    "tests/unit/test_protocol_prompt_sync.py",
    "tests/unit/test_codex_ledger_bridge.py",
)
REQUIRED_LEDGER_DOC_PHRASES = (
    "Pipeline remains the Codex four-seat governance kernel.",
    "/Users/hyungkoookkim/evidence-ledger",
    "Do not start ledger work from `/Users/hyungkoookkim/Content`.",
    "scripts/ledger_start_guard.py --seat <seat> --wave 2",
    "env -u GIT_INDEX_FILE",
    "Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.",
    "Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.",
    "Cross-repo handoffs record both repo heads.",
)
DOC_SURFACES = (
    "docs/protocol/codex/ledger-cli-adoption.md",
    "docs/protocol/codex/continuation.md",
    "docs/protocol/protocol-assembly-map.md",
    "AGENTS.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
)
CORE_CODEX_ROLE_PROMPTS = (
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ledger_bridge_contract_declares_kernel_target_and_hygiene():
    bridge = model.LEDGER_CLI_BRIDGE
    assert bridge["doc_path"] == "docs/protocol/codex/ledger-cli-adoption.md"
    assert bridge["pipeline_kernel"] == "/Users/hyungkoookkim/Pipeline"
    assert bridge["target_repo"] == "/Users/hyungkoookkim/evidence-ledger"
    assert bridge["forbidden_kernel"] == "/Users/hyungkoookkim/Content"
    assert bridge["guard_script"] == "scripts/ledger_start_guard.py"
    assert "env -u GIT_INDEX_FILE" in "\n".join(bridge["cross_repo_git_rules"])

    rendered = model.render_ledger_cli_bridge()
    assert "/Users/hyungkoookkim/Pipeline" in rendered
    assert "/Users/hyungkoookkim/evidence-ledger" in rendered
    assert "/Users/hyungkoookkim/Content" in rendered
    assert "scripts/ledger_start_guard.py --seat <seat> --wave 2" in rendered
    assert "readiness bridge" in rendered
    assert "named seat" in rendered
    assert "env -u GIT_INDEX_FILE" in rendered
    for rule in bridge["kernel_rules"]:
        assert f"  - {rule}" in rendered
    for rule in bridge["cross_repo_git_rules"]:
        assert f"  - {rule}" in rendered


def test_codex_surfaces_include_ledger_bridge_doc():
    assert (
        "docs/protocol/codex/ledger-cli-adoption.md",
        "ledger CLI adoption bridge for evidence-ledger target work",
    ) in model.CODEX_SURFACES
    assert (
        "scripts/ledger_start_guard.py",
        "ledger seat start guard that enforces Pipeline kernel before target repo work",
    ) in model.CODEX_SURFACES


def test_ledger_start_guard_renderer_names_all_seat_first_commands():
    rendered = model.render_ledger_start_guard()

    assert "Ledger Start Guard:" in rendered
    assert "cd /Users/hyungkoookkim/Pipeline" in rendered
    assert "Do not start from `/Users/hyungkoookkim/Content`" in rendered
    for seat in ("coordinator", "director", "director2", "operator", "operator2"):
        assert (
            "env -u GIT_INDEX_FILE .venv/bin/python "
            f"scripts/ledger_start_guard.py --seat {seat} --wave 2"
        ) in rendered


def test_ledger_start_guard_renderer_has_one_optional_exact_resume_command():
    command = (
        "scripts/ledger_start_guard.py --seat <seat> --wave 2 "
        "--resume-from <route-path>@<full-commit>"
    )
    rendered = model.render_ledger_start_guard()

    assert model.LEDGER_CLI_BRIDGE["guard_resume_command"] == command
    assert model.LEDGER_CLI_BRIDGE["guard_start_command"] in rendered
    assert rendered.count(command) == 1
    for phrase in (
        "named seat or coordinator",
        "unchanged already-routed local implementation or review",
        "fresh, transplanted, ambiguous, or external-effect work",
        "FULL ORIENTATION REQUIRED",
        "advisory fallback",
        "not BLOCKED",
        "no external-effect authority",
    ):
        assert phrase.casefold() in rendered.casefold()


def test_read_only_benchmark_reports_actual_classification_and_all_git_launches(
    tmp_path, capsys, monkeypatch
):
    benchmark_path = ROOT / "scripts/measure_ledger_start_guard.py"
    assert benchmark_path.is_file(), "benchmark instrument is not implemented"

    import measure_ledger_start_guard as benchmark
    import ledger_start_guard

    root = tmp_path / "Pipeline"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Benchmark Test"], cwd=root, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "benchmark@example.test"],
        cwd=root,
        check=True,
    )
    (root / "tracked.txt").write_text("benchmark\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", "tracked.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "benchmark base"], cwd=root, check=True)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    route_ref = f"coordination/mailbox/sent/route.md@{head}"
    evaluator_calls = 0

    def fake_build_resume(**kwargs):
        nonlocal evaluator_calls
        evaluator_calls += 1
        assert kwargs["root"] == root
        subprocess.run(
            ["git", "status", "--short"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        process = subprocess.Popen(
            ["git", "status", "--short"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.communicate()
        assert process.returncode == 0
        return ledger_start_guard.ResumeResult(
            ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED,
            ("FULL ORIENTATION REQUIRED",),
            ("live evidence requires ordinary orientation",),
        )

    monkeypatch.setattr(benchmark.ledger_start_guard, "build_resume", fake_build_resume)
    monkeypatch.setattr(benchmark.ledger_start_guard, "PIPELINE_KERNEL", root)
    output = tmp_path / "benchmark.json"
    base_args = [
        "--seat",
        "director",
        "--wave",
        "2",
        "--resume-from",
        route_ref,
    ]

    with pytest.raises(SystemExit):
        benchmark.main([*base_args, "--root", str(root)])
    capsys.readouterr()
    unrelated_cwd = tmp_path / "unrelated"
    unrelated_cwd.mkdir()
    monkeypatch.chdir(unrelated_cwd)

    rc = benchmark.main(
        [
            *base_args,
            "--output",
            str(output),
        ]
    )

    printed = capsys.readouterr().out
    payload = json.loads(printed)
    assert rc == 0
    assert evaluator_calls == 1
    assert list(payload) == [
        "schema",
        "classification",
        "elapsed_seconds",
        "git_processes",
        "pipeline_head",
        "resume_from",
    ]
    assert payload["schema"] == "ledger-start-guard-benchmark-v1"
    assert payload["classification"] == "FULL ORIENTATION REQUIRED"
    assert isinstance(payload["elapsed_seconds"], float)
    assert payload["elapsed_seconds"] >= 0
    assert payload["git_processes"] == 3
    assert payload["pipeline_head"] == head
    assert payload["resume_from"] == route_ref
    assert output.read_text(encoding="utf-8").strip() == printed.strip()


def test_model_verification_commands_are_current():
    rendered = model.render_codex_verification_commands()
    for selector in CURRENT_PROTOCOL_TESTS:
        assert selector in rendered
        assert (ROOT / selector).exists(), selector
    for selector in STALE_SELECTORS:
        assert selector not in rendered


def test_protocol_doctor_derives_verification_commands_from_model():
    expected_pytest = shlex.split(model.CODEX_VERIFICATION_COMMANDS[0])[3:]
    expected_smoke = shlex.split(model.CODEX_VERIFICATION_COMMANDS[1])[3:]
    commands = doctor.verification_commands("/tmp/python")

    assert commands == [
        ["/tmp/python", *expected_pytest[1:]],
        ["/tmp/python", *expected_smoke[1:]],
    ]

    flattened = " ".join(part for command in commands for part in command)
    for selector in CURRENT_PROTOCOL_TESTS:
        assert selector in flattened
    for selector in STALE_SELECTORS:
        assert selector not in flattened


def test_protocol_doctor_final_claim_requires_packets_without_duplicate_route_gate(monkeypatch):
    commands: list[list[str]] = []

    def fake_run_command(cmd, cwd, timeout=120):
        commands.append(cmd)
        return doctor.CommandResult(cmd, 0, "", "")

    monkeypatch.setattr(doctor, "run_command", fake_run_command)

    assert doctor.main(["--wave", "2", "--final-claim"]) == 0
    final_claim_commands = [
        command
        for command in commands
        if "scripts/protocol_capacity_board.py" in command and "--require-packets" in command
    ]
    assert len(final_claim_commands) == 1
    assert "--validate-route" not in final_claim_commands[0]

    commands.clear()

    assert doctor.main(
        [
            "--wave",
            "2",
            "--route",
            "coordination/mailbox/sent/route.md",
            "--final-claim",
        ]
    ) == 0
    route_require_commands = [
        command
        for command in commands
        if "scripts/protocol_capacity_board.py" in command and "--require-packets" in command
    ]
    assert len(route_require_commands) == 1


def test_ledger_bridge_doc_exists_and_names_required_boundaries():
    text = _read("docs/protocol/codex/ledger-cli-adoption.md")
    for phrase in REQUIRED_LEDGER_DOC_PHRASES:
        assert phrase in text


def test_doc_surfaces_route_to_ledger_bridge_without_stale_selectors():
    for path in DOC_SURFACES:
        text = _read(path)
        assert "docs/protocol/codex/ledger-cli-adoption.md" in text
        for selector in STALE_SELECTORS:
            assert selector not in text


def test_protocol_assembly_renderer_includes_target_repo_bridge():
    rendered = model.render_protocol_assembly_map()
    assert "Target-repo CLI adoption bridge" in rendered
    assert "docs/protocol/codex/ledger-cli-adoption.md" in rendered


def test_core_codex_role_prompts_reference_ledger_bridge_and_hygiene():
    for path in CORE_CODEX_ROLE_PROMPTS:
        text = _read(path)
        assert "docs/protocol/codex/ledger-cli-adoption.md" in text
        assert "scripts/ledger_start_guard.py --seat" in text
        assert "cd /Users/hyungkoookkim/Pipeline" in text
        assert "Do not start ledger work from `/Users/hyungkoookkim/Content`." in text
        assert "/Users/hyungkoookkim/evidence-ledger" in text
        assert "env -u GIT_INDEX_FILE" in text
        assert "Pipeline remains the Codex four-seat governance kernel" in text
        assert "evidence-ledger owns product-local truth" in text


def test_readiness_and_coordinator_prompts_keep_mutation_boundaries():
    readiness = _read(".codex/agents/readiness-bridge.toml")
    coordinator = _read(".codex/agents/protocol-coordinator.toml")
    assert "A readiness bridge must not mutate evidence-ledger." in readiness
    assert "Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes." in coordinator


def test_readiness_render_codex_surfaces_ledger_bridge():
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        continuation_readiness.render_codex(ROOT)

    rendered = buffer.getvalue()
    assert "Ledger CLI Bridge:" in rendered
    assert "docs/protocol/codex/ledger-cli-adoption.md" in rendered
    assert "Ledger Start Guard:" in rendered
    assert "scripts/ledger_start_guard.py --seat <seat> --wave 2" in rendered
    assert "Capacity Split Default:" in rendered
    assert "divisible or preplanned larger work defaults to dual-pair routing" in rendered
    assert "R-INDEPENDENCE:" in rendered
    assert "independent design-time enumeration" in rendered


def test_ledger_start_guard_cli_rejects_content_kernel():
    import ledger_start_guard
    import target_binding

    forbidden = target_binding.forbidden_roots()[0]
    result = ledger_start_guard.build_guard(
        seat="operator2",
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
            "operator2",
            "--wave",
            "2",
        ]
    )

    out = capsys.readouterr().out
    target = target_binding.resolve_target()
    assert rc == 0
    assert "Ledger seat start guard: PASS" in out
    assert "Active route: coordination/mailbox/sent/2026-07-07T09-36-23Z-coordinator-to-all-coordination.md" in out
    assert "env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator2 --wave 2" in out
    assert f"env -u GIT_INDEX_FILE git -C {target.path.as_posix()} status --short --branch" in out


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
            "director",
            "--wave",
            "2",
        ]
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "route base: origin/main @ abc1234" in out
    assert "route worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-task23" in out
    assert (
        "env -u GIT_INDEX_FILE git -C "
        "/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-task23 "
        "status --short --branch"
    ) in out
    assert "normal target checkout may be stale; do not start product work there unless the route names it" in out
    assert "env -u GIT_INDEX_FILE git log --oneline -5" not in out
    assert "env -u GIT_INDEX_FILE git status --short\n" not in out
