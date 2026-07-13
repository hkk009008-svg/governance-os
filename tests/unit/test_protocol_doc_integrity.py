from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def test_codex_subagents_never_inherit_seat_authority():
    continuation = _read("docs/protocol/codex/continuation.md")
    compact = _compact(continuation)

    assert "Subagents never inherit live-seat or coordinator authority." in compact
    assert "Subagents do not inherit live-seat or coordinator authority unless" not in compact
    assert "Subagents do not consume cursors, send mailbox events, issue GO" in compact


def test_independence_first_doc_tracks_mechanized_gate_and_remaining_followup():
    text = (ROOT / "docs/protocol/claude/independence-first.md").read_text(
        encoding="utf-8"
    )
    assert "Sync the operative stub into `AGENTS.md`" not in text
    assert "Mechanize the cross-model requirement" not in text
    assert "## Mechanized enforcement and remaining follow-up" in text
    assert "live receipt-backed advisory review/reconciliation" in text
    assert "dispatch templates" in text


def test_root_and_pr_docs_do_not_reference_stale_architecture_sections():
    for path in ("AGENTS.md", ".github/pull_request_template.md"):
        text = _read(path)
        assert "ARCHITECTURE.md §15" not in text
        assert "§15 smoke" not in text


def test_pr_template_matches_current_governance_repo_surfaces():
    text = _read(".github/pull_request_template.md")

    assert "234 passed" in text
    assert "478 pass" not in text
    assert "cd web" not in text
    assert "docs/STRATEGIC_REVIEW-2026-05-24.md" not in text


def test_pipeline_docs_do_not_launch_live_seats_from_content():
    text = _read("coordination/README.md")

    assert "cd /Users/hyungkoookkim/Content" not in text
    assert "absolute/path/to/Content" not in text
    assert "cd /Users/hyungkoookkim/Pipeline" in text


def test_incident_log_exists_for_emergency_protocol():
    text = _read("docs/INCIDENT-LOG.md")

    assert "# Incident Log" in text
    assert "Emergency protocol requires" in text


def test_threeway_docs_do_not_claim_local_cutover_when_refs_absent():
    docs = {
        path: _read(path)
        for path in (
            "docs/protocol/threeway/CODEX-ADOPTION.md",
            "docs/protocol/threeway/README.md",
            "docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md",
        )
    }

    for text in docs.values():
        compact = _compact(text)
        assert "git for-each-ref refs/threeway/" in compact
        assert "legacy mailbox remains authoritative for local work" in compact
        assert "CUT OVER (2026-06-22)" not in text
        assert "cutover WAS executed" not in text


def test_threeway_truth_links_resolve_to_existing_files():
    readme = _read("docs/protocol/threeway/README.md")
    doctrine = _read("docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md")

    assert "docs/superpowers/specs/2026-06-19-cross-provider-seat-topology-design.md" not in readme
    assert "docs/superpowers/plans/2026-06-20-cross-provider-seat-topology-slice2.5-legacy-bus-migration.md" not in readme
    assert "docs/protocol/threeway/CODEX-ADOPTION.md" in readme
    assert "docs/protocol/threeway/CODEX-ADOPTION.md" in doctrine


def test_task24_capacity_packets_reflect_operator_go_and_pair_b_preflight():
    operator_packet = json.loads(
        _read("coordination/capacity/packets/2026-07-08-ledger-phase2-task24-operator-lanev.json")
    )
    director2_packet = json.loads(
        _read(
            "coordination/capacity/packets/2026-07-08-ledger-phase2-task24-director2-planning-preflight.json"
        )
    )
    operator2_packet = json.loads(
        _read("coordination/capacity/packets/2026-07-08-ledger-phase2-task24-operator2-preflight.json")
    )
    coordinator_packet = json.loads(
        _read("coordination/capacity/packets/2026-07-08-ledger-phase2-task24-coordinator-join.json")
    )

    assert operator_packet["status"] == "done"
    assert operator_packet["target_commit"] == "9deb0f4"
    assert operator_packet["verify_request"] == (
        "coordination/mailbox/sent/2026-07-08T17-12-21Z-director-to-operator-verify-request.md"
    )
    assert operator_packet["handoff_artifact"] == (
        "coordination/mailbox/sent/2026-07-08T17-19-32Z-operator-to-all-verification-report.md"
    )
    assert any("VERDICT: GO" in item for item in operator_packet["done_evidence"])

    assert director2_packet["packet_type"] == "director-preflight"
    assert operator2_packet["packet_type"] == "operator-preflight"
    assert "director2-ledger-phase2-task24-planning-preflight" in coordinator_packet["dependencies"]
    assert "operator2-ledger-phase2-task24-preflight" in coordinator_packet["dependencies"]
    assert "director2-ledger-phase2-task24-observer" not in coordinator_packet["dependencies"]
    assert "operator2-ledger-phase2-task24-observer" not in coordinator_packet["dependencies"]


def test_operator_phase_taxonomy_uses_current_codex_triggers():
    for path in (
        ".agents/skills/seat-operator/SKILL.md",
        "docs/protocol/agents/director-operator.md",
        "docs/protocol/claude/director-operator.md",
    ):
        text = _read(path)
        compact = _compact(text)

        assert "operator waits for a fresh verify-request or shipping commit" in compact.lower()
        assert "in-chat \"Dispatching X\" narration" not in text
        assert "implicit git-log poll" not in text
