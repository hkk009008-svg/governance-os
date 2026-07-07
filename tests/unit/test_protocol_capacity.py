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
