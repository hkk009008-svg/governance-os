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
    director2_type: str = "director-preflight",
    operator2_type: str = "operator-preflight",
    operator_status: str = "blocked",
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
            status=operator_status,
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
    assert "invalid packet_type" not in messages


def test_capacity_board_renders_next_lawful_action_per_actor(tmp_path: Path):
    _write_capacity_split_cycle(tmp_path)

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)
    rendered = protocol_capacity.render_capacity_board(report)

    assert "NEXT LAWFUL ACTIONS" in rendered
    assert "director2" in rendered
    assert "startup: env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director2 --wave 2" in rendered
    assert "packet: director2-capacity-split-work (director-preflight, blocked)" in rendered
    assert "deps: -" in rendered
    assert "stop: report bounded planning/preflight evidence to coordinator; no production fix or GO" in rendered


def test_capacity_board_renders_structural_lane_v_trigger_authority_for_active_pair(
    tmp_path: Path,
) -> None:
    _write_capacity_split_cycle(tmp_path, operator_status="active")
    report = protocol_capacity.collect_capacity_report(tmp_path, 2)
    rendered = protocol_capacity.render_capacity_board(report)

    director_block = "\n".join(
        (
            "director",
            "  startup: env -u GIT_INDEX_FILE .venv/bin/python "
            "scripts/ledger_start_guard.py --seat director --wave 2",
            "  packet: director-capacity-split-chunk-a "
            "(director-implementation, active)",
            "  deps: -",
            "  next: implement the named scope inside allowed paths",
            "  stop: send one committed verify-request naming full reviewed "
            "base/head, author seat/model, assigned Operator, question, allowed "
            "paths, and commands",
        )
    )
    operator_block = "\n".join(
        (
            "operator",
            "  startup: env -u GIT_INDEX_FILE .venv/bin/python "
            "scripts/ledger_start_guard.py --seat operator --wave 2",
            "  packet: operator-capacity-split-chunk-a "
            "(operator-verification, active)",
            "  deps: -",
            "  next: verify only the assigned committed verify-request as a "
            "non-author; bind the exact request, range, and allowed paths",
            "  stop: send one directly publishable verification-report "
            "GO/NITS/FAIL through the fixed mailbox writer; no descriptor, "
            "shipping trigger, task publication state, or recovery path",
        )
    )

    assert director_block in rendered
    assert operator_block in rendered
    assert "commit/range, tests, and exclusions" not in rendered
    assert "Lane-V-Scope" not in rendered
    assert "shipping commit" not in rendered


def test_capacity_board_keeps_authorized_pair_chain_internal_until_real_boundary(
    tmp_path: Path,
) -> None:
    _write_capacity_split_cycle(tmp_path)
    report = protocol_capacity.collect_capacity_report(tmp_path, 2)
    rendered = protocol_capacity.render_capacity_board(report)

    assert (
        "internally continue an already-authorized Director→Operator chain" in rendered
    )
    assert (
        "return to the user only at completion, a genuine blocker, scope expansion, "
        "or a separately gated side effect" in rendered
    )


def test_capacity_board_renders_blocked_operator_trigger_stop(tmp_path: Path) -> None:
    _write_capacity_split_cycle(tmp_path)
    report = protocol_capacity.collect_capacity_report(tmp_path, 2)
    rendered = protocol_capacity.render_capacity_board(report)

    blocked_operator_block = "\n".join(
        (
            "operator",
            "  startup: env -u GIT_INDEX_FILE .venv/bin/python "
            "scripts/ledger_start_guard.py --seat operator --wave 2",
            "  packet: operator-capacity-split-chunk-a "
            "(operator-verification, blocked)",
            "  deps: -",
            "  next: wait on named dependency or report the concrete blocker",
            "  stop: wait for the assigned committed verify-request/dependency "
            "or report FAIL/NITS with evidence; never reconstruct missing fields",
        )
    )

    assert blocked_operator_block in rendered


def test_active_implementation_path_isolation_rejects_parent_child_overlap(
    tmp_path: Path,
):
    _write_capacity_split_cycle(
        tmp_path,
        director2_type="director-implementation",
        director2_status="active",
    )
    _write_packet(
        tmp_path,
        _packet(
            packet_id="director-capacity-split-chunk-a",
            owner="director",
            packet_type="director-implementation",
            status="active",
            cycle="capacity-split-cycle",
        )
        | {
            "allowed_paths": ["src/"],
            "scope_files": ["src/"],
        },
    )
    _write_packet(
        tmp_path,
        _packet(
            packet_id="director2-capacity-split-work",
            owner="director2",
            packet_type="director-implementation",
            status="active",
            cycle="capacity-split-cycle",
        )
        | {
            "allowed_paths": ["src/chunk-b/"],
            "scope_files": ["src/chunk-b/"],
        },
    )

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    messages = "\n".join(issue["message"] for issue in report.blocking_issues)
    assert "director-capacity-split-chunk-a and director2-capacity-split-work overlap" in messages
    assert "src/ <-> src/chunk-b/" in messages


def test_active_cycle_coverage_counts_completed_actor_packets(tmp_path: Path):
    _write_capacity_split_cycle(tmp_path)
    _write_packet(
        tmp_path,
        _packet(
            packet_id="operator-capacity-split-chunk-a",
            owner="operator",
            packet_type="operator-verification",
            status="done",
            cycle="capacity-split-cycle",
        )
        | {
            "done_evidence": ["Operator verification-report GO."],
            "handoff_artifact": "coordination/mailbox/sent/operator-go.md",
            "verify_request": "coordination/mailbox/sent/operator-verify-request.md",
            "target_commit": "abc1234",
            "commit_range": "base..abc1234",
        },
    )

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    messages = "\n".join(issue["message"] for issue in report.blocking_issues)
    assert "operator has 0 current packets" not in messages
    operator_row = next(row for row in report.actor_rows if row["owner"] == "operator")
    assert operator_row["packet_ids"] == ["operator-capacity-split-chunk-a"]
    assert operator_row["statuses"] == ["done"]


def test_closed_capacity_cycle_reports_closed_packet_state(tmp_path: Path):
    _write_capacity_split_cycle(
        tmp_path,
        director2_status="done",
        operator2_status="done",
    )
    for packet_id in (
        "coord-capacity-split-route",
        "director-capacity-split-chunk-a",
        "operator-capacity-split-chunk-a",
    ):
        packet = _packet(
            packet_id=packet_id,
            status="done",
            cycle="capacity-split-cycle",
        )
        if packet_id.startswith("director-"):
            packet["owner"] = "director"
            packet["packet_type"] = "director-implementation"
            packet["done_evidence"] = ["Director sent verify-request."]
        elif packet_id.startswith("operator-"):
            packet["owner"] = "operator"
            packet["packet_type"] = "operator-verification"
            packet["done_evidence"] = ["Operator verification-report GO."]
            packet["verify_request"] = "coordination/mailbox/sent/verify-request.md"
            packet["target_commit"] = "abc1234"
        _write_packet(tmp_path, packet)

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    assert report.packet_state == "closed"
    assert "packet state: closed" in protocol_capacity.render_capacity_board(report)


def test_active_cycle_coverage_prefers_done_replacement_over_idle_observer(
    tmp_path: Path,
):
    for packet in [
        _packet(
            packet_id="coord-join",
            owner="coordinator",
            packet_type="coordinator-join",
            status="active",
            cycle="cycle-replaced-observers",
        ),
        _packet(
            packet_id="director-done",
            owner="director",
            packet_type="director-brief",
            status="done",
            cycle="cycle-replaced-observers",
        ),
        _packet(
            packet_id="operator-done",
            owner="operator",
            packet_type="operator-doc-sync",
            status="done",
            cycle="cycle-replaced-observers",
        ),
        _packet(
            packet_id="director2-observer",
            owner="director2",
            packet_type="idle",
            status="done",
            cycle="cycle-replaced-observers",
        ),
        _packet(
            packet_id="director2-planning",
            owner="director2",
            packet_type="director-brief",
            status="done",
            cycle="cycle-replaced-observers",
        ),
        _packet(
            packet_id="operator2-observer",
            owner="operator2",
            packet_type="idle",
            status="done",
            cycle="cycle-replaced-observers",
        ),
        _packet(
            packet_id="operator2-preflight",
            owner="operator2",
            packet_type="operator-doc-sync",
            status="done",
            cycle="cycle-replaced-observers",
        ),
    ]:
        _write_packet(tmp_path, packet)

    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    messages = "\n".join(issue["message"] for issue in report.blocking_issues)
    assert "current/done packets" not in messages
    rows = {row["owner"]: row for row in report.actor_rows}
    assert rows["director2"]["packet_ids"] == ["director2-planning"]
    assert rows["operator2"]["packet_ids"] == ["operator2-preflight"]


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
