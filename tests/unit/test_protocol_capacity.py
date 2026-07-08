from __future__ import annotations

import json
from pathlib import Path

import pytest

import protocol_capacity


def _packet(
    *,
    packet_id: str = "coord-test-route",
    owner: str = "coordinator",
    packet_type: str = "coordinator-route",
    status: str = "active",
    cycle: str = "cycle-a",
) -> dict:
    return {
        "id": packet_id,
        "wave": 2,
        "cycle": cycle,
        "owner": owner,
        "packet_type": packet_type,
        "row_ids": ["row-a"],
        "allowed_paths": ["coordination/capacity/packets/", "coordination/mailbox/sent/"],
        "lock_keys": [],
        "dependencies": [],
        "acceptance": ["Route the current board."],
        "done_evidence": [],
        "handoff_artifact": None,
        "next_recipient": "coordinator",
        "status": status,
        "verify_request": None,
        "target_commit": None,
        "commit_range": None,
        "scope_files": ["coordination/mailbox/sent/"],
    }


def _write_packet(root: Path, packet: dict) -> None:
    packet_dir = root / "coordination" / "capacity" / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    (packet_dir / f"{packet['id']}.json").write_text(
        json.dumps(packet, indent=2),
        encoding="utf-8",
    )


def _write_route(root: Path, name: str, body: str) -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    path = sent / name
    path.write_text(body, encoding="utf-8")
    return path


def _write_capacity_split_cycle(
    root: Path,
    *,
    director2_type: str = "director-brief",
    operator2_type: str = "operator-verification",
    director2_status: str = "blocked",
    operator2_status: str = "blocked",
) -> None:
    packets = [
        _packet(
            packet_id="coord-capacity-split-route",
            owner="coordinator",
            packet_type="coordinator-route",
            status="active",
            cycle="capacity-split-cycle",
        ),
        _packet(
            packet_id="director-capacity-split-chunk-a",
            owner="director",
            packet_type="director-implementation",
            status="active",
            cycle="capacity-split-cycle",
        )
        | {
            "allowed_paths": ["src/chunk-a/"],
            "scope_files": ["src/chunk-a/"],
        },
        _packet(
            packet_id="operator-capacity-split-chunk-a",
            owner="operator",
            packet_type="operator-verification",
            status="blocked",
            cycle="capacity-split-cycle",
        ),
        _packet(
            packet_id="director2-capacity-split-work",
            owner="director2",
            packet_type=director2_type,
            status=director2_status,
            cycle="capacity-split-cycle",
        )
        | {
            "allowed_paths": ["docs/next-brief/"],
            "acceptance": ["Prepare bounded planning for the next brief."],
            "scope_files": ["docs/next-brief/"],
        },
        _packet(
            packet_id="operator2-capacity-split-work",
            owner="operator2",
            packet_type=operator2_type,
            status=operator2_status,
            cycle="capacity-split-cycle",
        )
        | {
            "allowed_paths": ["logs/preflight/"],
            "acceptance": ["Run bounded preflight selector discovery."],
            "scope_files": ["logs/preflight/"],
        },
    ]
    for packet in packets:
        _write_packet(root, packet)


def _capacity_split_route_body(extra: str = "") -> str:
    packet_ids = (
        "coord-capacity-split-route\n"
        "- director-capacity-split-chunk-a\n"
        "- operator-capacity-split-chunk-a\n"
        "- director2-capacity-split-work\n"
        "- operator2-capacity-split-work"
    )
    return (
        "Task-board: capacity-split-cycle\n\n"
        f"- {packet_ids}\n\n"
        f"{extra}\n\n"
        "Join condition: coordinator closes after both pair lanes are accounted for.\n\n"
        "## Exact Next Trigger\n\n"
        "Director continues Chunk A; Pair B follows the capacity split decision.\n"
    )


def test_require_packets_flags_empty_final_claim(tmp_path: Path):
    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    required = protocol_capacity.require_packets(report)

    assert [issue["gate"] for issue in required.blocking_issues] == ["G9"]


def test_active_cycle_rejects_pair_b_idle_observer_packets(tmp_path: Path):
    _write_capacity_split_cycle(
        tmp_path,
        director2_type="idle",
        operator2_type="idle",
    )

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    messages = "\n".join(issue["message"] for issue in report.blocking_issues)
    assert "Pair B must perform bounded planning or preflight" in messages
    packet_ids = {
        packet_id
        for issue in report.blocking_issues
        for packet_id in issue["packet_ids"]
    }
    assert "director2-capacity-split-work" in packet_ids
    assert "operator2-capacity-split-work" in packet_ids


def test_active_cycle_allows_pair_b_planning_and_preflight_packets(tmp_path: Path):
    _write_capacity_split_cycle(tmp_path)

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    messages = "\n".join(issue["message"] for issue in report.blocking_issues)
    assert "Pair B must perform bounded planning or preflight" not in messages


def test_route_validation_requires_capacity_split_decision(tmp_path: Path):
    _write_capacity_split_cycle(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-09T00-00-00Z-coordinator-to-all-coordination.md",
        _capacity_split_route_body(),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "missing Capacity Split Default decision" in messages


def test_route_validation_allows_single_pair_with_pair_b_preflight_decision(
    tmp_path: Path,
):
    _write_capacity_split_cycle(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-09T00-05-00Z-coordinator-to-all-coordination.md",
        _capacity_split_route_body(
            "## Capacity Split Default\n\n"
            "- single-pair fast path remains the default for narrow or shared-file work.\n"
            "- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.\n"
            "- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid


def test_route_validation_requires_chunk_labels_for_dual_pair_route(
    tmp_path: Path,
):
    _write_capacity_split_cycle(
        tmp_path,
        director2_type="director-implementation",
        director2_status="active",
    )
    route = _write_route(
        tmp_path,
        "2026-07-09T00-10-00Z-coordinator-to-all-coordination.md",
        _capacity_split_route_body(
            "## Capacity Split Default\n\n"
            "- divisible or preplanned larger work defaults to dual-pair routing.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "dual-pair route missing" in messages
    assert "chunk b" in messages


def test_route_validation_allows_dual_pair_route_with_chunk_labels(
    tmp_path: Path,
):
    _write_capacity_split_cycle(
        tmp_path,
        director2_type="director-implementation",
        director2_status="active",
    )
    route = _write_route(
        tmp_path,
        "2026-07-09T00-15-00Z-coordinator-to-all-coordination.md",
        _capacity_split_route_body(
            "## Capacity Split Default\n\n"
            "- divisible or preplanned larger work defaults to dual-pair routing.\n"
            "- Chunk A: director owns src/chunk-a/ and operator verifies Chunk A.\n"
            "- Chunk B: director2 owns docs/next-brief/ and operator2 verifies Chunk B.\n"
            "- The two active chunks must name disjoint write sets, explicit interfaces, focused tests, forbidden side effects, and separate verify-request/verification-report loops.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid


def test_route_validation_rejects_route_outside_mailbox_sent(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = tmp_path / "scratch-coordinator-to-all-coordination.md"
    route.write_text(
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "Join condition: coordinator closes.\n\n"
        "## Exact Next Trigger\n\n"
        "Coordinator sends the next route.\n",
        encoding="utf-8",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(issue["gate"] == "G7" and "coordination/mailbox/sent" in issue["message"] for issue in result.blocking_issues)


def test_route_validation_rejects_subagent_authority_leakage(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-07T18-10-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "This route authorizes a subagent to issue operator GO and consume-events for operator.\n\n"
        "Join condition: coordinator closes.\n\n"
        "## Exact Next Trigger\n\n"
        "Operator sends a verification-report.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    messages = "\n".join(issue["message"] for issue in result.blocking_issues)
    assert "subagent" in messages
    assert "operator GO" in messages or "consume" in messages


@pytest.mark.parametrize(
    ("directive", "expected_labels"),
    (
        (
            "Subagent will issue operator GO and consume-events for operator.",
            ("subagent operator GO", "subagent cursor consume"),
        ),
        (
            "Subagents may send mailbox events and create coordinator routes.",
            ("subagent mailbox event", "subagent coordinator route"),
        ),
        (
            "Dispatch a subagent to claim locks and push after tests pass.",
            ("subagent lock claim", "subagent push"),
        ),
    ),
)
def test_route_validation_rejects_delegated_subagent_side_effect_directives(
    tmp_path: Path,
    directive: str,
    expected_labels: tuple[str, ...],
):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-07T18-20-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        f"{directive}\n\n"
        "Join condition: coordinator closes.\n\n"
        "## Exact Next Trigger\n\n"
        "Operator sends a verification-report.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "forbidden side effect authorization" in messages
    for label in expected_labels:
        assert label in messages


def test_route_validation_allows_explicit_subagent_negative_boundaries(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-07T18-25-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "No subagents may issue operator GO.\n"
        "Subagents do not consume cursors.\n\n"
        "Join condition: coordinator closes.\n\n"
        "## Exact Next Trigger\n\n"
        "Operator sends a verification-report.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not any(
        "forbidden side effect authorization" in issue["message"]
        for issue in result.route_issues
    )


def test_route_validation_rejects_shared_side_effect_without_executor_token(
    tmp_path: Path,
):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-08T02-10-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "This route authorizes director to push origin/main after green tests.\n\n"
        "Join condition: coordinator closes after postcheck.\n\n"
        "## Exact Next Trigger\n\n"
        "Director executes the routed side effect.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "missing side-effect executor token" in messages
    assert "push" in messages


def test_route_validation_allows_complete_side_effect_executor_token(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-08T02-15-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "## Side-Effect Executor Token\n\n"
        "- side_effect_id: publish-main-2026-07-08\n"
        "- executor: director\n"
        "- target: origin/main\n"
        "- allowed_command_class: git push\n"
        "- preflight: git status plus divergence check\n"
        "- stop_if_newer_mail_or_live_target_satisfied: re-read mailbox and ls-remote\n"
        "- postcheck: git ls-remote origin refs/heads/main\n"
        "- observer_seats: director2, operator, operator2\n"
        "- final_closeout_owner: coordinator\n"
        "- non_goals: no force-push and no lock claim\n\n"
        "Join condition: coordinator closes after postcheck evidence.\n\n"
        "## Exact Next Trigger\n\n"
        "Director executes the token or stops on failed preflight.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.route_issues == ()


def test_route_validation_rejects_duplicate_side_effect_success_claims_without_common_token(
    tmp_path: Path,
):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-08T02-20-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "Side-effect success claim: remote-ref update target=origin/main actor=director\n"
        "Side-effect success claim: remote-ref update target=origin/main actor=operator\n\n"
        "Join condition: coordinator closes after reconciling claims.\n\n"
        "## Exact Next Trigger\n\n"
        "Coordinator reconciles the duplicated success claims.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "multiple side-effect success claims" in messages
    assert "origin/main" in messages


@pytest.mark.parametrize(
    "directive",
    (
        "Director may push origin/main after green tests.",
        "Director pushes origin/main after green tests.",
        "Director claims lock coordination/locks/foo.lock before work.",
    ),
)
def test_route_validation_requires_token_for_modal_side_effect_language(
    tmp_path: Path,
    directive: str,
):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-08T02-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        f"{directive}\n\n"
        "Join condition: coordinator closes after postcheck.\n\n"
        "## Exact Next Trigger\n\n"
        "Director executes the routed side effect.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "missing side-effect executor token" in messages


def test_route_validation_rejects_multi_executor_token(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-08T02-35-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "## Side-Effect Executor Token\n\n"
        "- side_effect_id: publish-main-2026-07-08\n"
        "- executor: director, operator\n"
        "- target: origin/main\n"
        "- allowed_command_class: git push\n"
        "- preflight: git status plus divergence check\n"
        "- stop_if_newer_mail_or_live_target_satisfied: re-read mailbox and ls-remote\n"
        "- postcheck: git ls-remote origin refs/heads/main\n"
        "- observer_seats: director2, operator2\n"
        "- final_closeout_owner: coordinator\n"
        "- non_goals: no force-push\n\n"
        "This route authorizes director to push origin/main after green tests.\n\n"
        "Join condition: coordinator closes after postcheck evidence.\n\n"
        "## Exact Next Trigger\n\n"
        "Director executes the token or stops on failed preflight.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "side-effect executor token" in messages
    assert "executor" in messages


def test_route_validation_rejects_token_for_different_side_effect_target(
    tmp_path: Path,
):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-08T02-40-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "## Side-Effect Executor Token\n\n"
        "- side_effect_id: lock-only-2026-07-08\n"
        "- executor: director\n"
        "- target: coordination/locks/foo.lock\n"
        "- allowed_command_class: lock claim\n"
        "- preflight: check mailbox\n"
        "- stop_if_newer_mail_or_live_target_satisfied: re-read mailbox\n"
        "- postcheck: lock exists\n"
        "- observer_seats: operator\n"
        "- final_closeout_owner: coordinator\n"
        "- non_goals: no push\n\n"
        "This route authorizes director to push origin/main after green tests.\n\n"
        "Join condition: coordinator closes after postcheck evidence.\n\n"
        "## Exact Next Trigger\n\n"
        "Director executes the token or stops on failed preflight.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    messages = "\n".join(issue["message"] for issue in result.route_issues)
    assert "side-effect executor token" in messages
    assert "target" in messages
