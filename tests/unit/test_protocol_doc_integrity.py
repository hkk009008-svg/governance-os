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
    compact = _compact(continuation).casefold()

    assert "subagent" in compact
    assert "never inherits live-role authority" in compact
    assert "never publish a formal verdict or live-role event" in compact
    assert "unless explicitly delegated" not in compact


def test_every_provider_entrypoint_points_to_the_canonical_policy_model():
    """One executable policy source, named by every side's adapter.

    Providers differ in runtime mechanics, not in policy. Each adapter must
    name `scripts/codex_protocol_model.py` as the canonical source rather than
    restating identity, ownership, risk, or external-effect rules in prose that
    can drift. The assertion is on the pointer target, not on one sentence, so
    an adapter may word its own hand-off naturally.
    """
    pointer = "scripts/codex_protocol_model.py"
    for path in (
        "AGENTS.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
    ):
        compact = _compact(_read(path).replace("`", ""))
        assert pointer in compact, path


def test_work_mode_docs_point_to_the_executable_profiles_and_keep_explore_light():
    work_modes = _compact(_read("docs/protocol/work-modes.md"))

    assert "scripts/codex_protocol_model.py" in work_modes
    assert "work_profile_for" in work_modes
    assert "work mode is separate from review risk" in work_modes.lower()
    assert "one campaign brief" in work_modes.lower()
    assert "no formal review inside explore" in work_modes.lower()
    assert "provider launch remains separately authorized" in work_modes.lower()

    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".claude/skills/four-seat-protocol/SKILL.md",
        "docs/protocol/claude/continuation.md",
    ):
        text = _compact(_read(path))
        assert "docs/protocol/work-modes.md" in text, path
        assert "explore" in text.lower(), path
        assert "validate" in text.lower(), path
        assert "promote" in text.lower(), path


def test_independence_first_doc_tracks_mechanized_gate_and_remaining_followup():
    text = (ROOT / "docs/protocol/claude/independence-first.md").read_text(
        encoding="utf-8"
    )
    assert "Sync the operative stub into `AGENTS.md`" not in text
    assert "Mechanize the cross-model requirement" not in text
    assert "Compact Pair Invariant" in text
    assert "fixed mailbox writer" in text
    compact = _compact(text)
    assert "owner explicitly assesses plausible abuse classes" in compact
    assert "Early independent review is encouraged" in compact
    assert "no universal preflight CLEAR" in compact
    assert "distinct seat and different system-visible model" in compact
    assert "actual commit or range" in compact
    assert "live receipt-backed advisory review/reconciliation" not in text
    assert "lane-v-report/v2" not in text
    assert "same-model reviewer does not discharge it" not in text
    assert "does not replace the preferred cross-model per-task verification" not in text
    assert "that it was cross-model" not in text
    assert "changing owners or reviewers cannot erase material evidence" in compact


def test_root_and_pr_docs_do_not_reference_stale_architecture_sections():
    for path in ("AGENTS.md", ".github/pull_request_template.md"):
        text = _read(path)
        assert "ARCHITECTURE.md §15" not in text
        assert "§15 smoke" not in text


def test_pr_template_matches_current_governance_repo_surfaces():
    text = _read(".github/pull_request_template.md")

    # Drift-proof: the checklist cites the command + asks for the literal summary
    # line, never a frozen pass count (which always re-stales — the 234/478 drift).
    assert "paste the literal summary line" in text
    assert "234 passed" not in text
    assert "478 pass" not in text
    assert "cd web" not in text
    assert "docs/STRATEGIC_REVIEW-2026-05-24.md" not in text


def test_pipeline_docs_do_not_launch_live_seats_from_content():
    text = _read("coordination/README.md")

    assert "/Users/" not in text
    assert "absolute/path/to/Content" not in text
    assert 'PIPELINE_ROOT="$(git rev-parse --show-toplevel)"' in text
    assert 'cd "$PIPELINE_ROOT"' in text


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
    ):
        text = _read(path)
        compact = _compact(text)

        assert "committed verify-request" in compact.lower()
        assert "in-chat \"Dispatching X\" narration" not in text
        assert "implicit git-log poll" not in text
