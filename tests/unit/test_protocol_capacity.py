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
    packet_dir.mkdir(parents=True)
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


def test_require_packets_flags_empty_final_claim(tmp_path: Path):
    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    required = protocol_capacity.require_packets(report)

    assert [issue["gate"] for issue in required.blocking_issues] == ["G9"]


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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "protocol-unit-coherence-side-effect-token: modal side-effect wording "
        "must require an executor token"
    ),
)
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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "protocol-unit-coherence-side-effect-token: executor token must name "
        "exactly one executor"
    ),
)
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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "protocol-unit-coherence-side-effect-token: executor token must match "
        "the routed side-effect target"
    ),
)
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
