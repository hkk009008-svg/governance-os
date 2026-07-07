from __future__ import annotations

import shlex
from pathlib import Path

import codex_protocol_model as model
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
    "tests/unit/test_ceremony_gates.py",
    "tests/unit/test_codex_ledger_bridge.py",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ledger_bridge_contract_declares_kernel_target_and_hygiene():
    bridge = model.LEDGER_CLI_BRIDGE
    assert bridge["doc_path"] == "docs/protocol/codex/ledger-cli-adoption.md"
    assert bridge["pipeline_kernel"] == "/Users/hyungkoookkim/Pipeline"
    assert bridge["target_repo"] == "/Users/hyungkoookkim/evidence-ledger"
    assert "env -u GIT_INDEX_FILE" in "\n".join(bridge["cross_repo_git_rules"])

    rendered = model.render_ledger_cli_bridge()
    assert "/Users/hyungkoookkim/Pipeline" in rendered
    assert "/Users/hyungkoookkim/evidence-ledger" in rendered
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
