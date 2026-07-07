from __future__ import annotations

import contextlib
import io
import shlex
from pathlib import Path

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
    "tests/unit/test_ceremony_gates.py",
    "tests/unit/test_codex_ledger_bridge.py",
)
REQUIRED_LEDGER_DOC_PHRASES = (
    "Pipeline remains the Codex four-seat governance kernel.",
    "/Users/hyungkoookkim/evidence-ledger",
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
