"""Renderer parity: the generated projection must satisfy the legacy validator."""
from __future__ import annotations

import json
from pathlib import Path

import protocol_capacity
import pytest

import route_manifest
from test_route_manifest import _route, _token


def test_hostile_token_route_rejected_at_validation_and_render(tmp_path):
    """F1 belt-and-braces: a newline-injected token is caught before rendering."""
    hostile = _route(
        side_effect_token=_token(target="origin/main\n- executor: operator")
    )
    assert route_manifest.validate_route_object(hostile), "validation must reject"
    with pytest.raises(ValueError):
        route_manifest.render_markdown(hostile, title="hostile")


def _packet(**overrides) -> dict:
    base = {
        "id": "coord-capacity-split-route",
        "wave": 2,
        "cycle": "route-compat-cycle",
        "owner": "coordinator",
        "packet_type": "coordinator-route",
        "row_ids": ["row-a"],
        "allowed_paths": ["coordination/capacity/packets/", "coordination/mailbox/sent/"],
        "lock_keys": [],
        "dependencies": [],
        "acceptance": ["Route the current board."],
        "done_evidence": [],
        "handoff_artifact": None,
        "next_recipient": "coordinator",
        "status": "active",
        "verify_request": None,
        "target_commit": None,
        "commit_range": None,
        "scope_files": ["coordination/mailbox/sent/"],
    }
    base.update(overrides)
    return base


GREEN_PACKETS = [
    _packet(),
    _packet(
        id="director-capacity-split-chunk-a",
        owner="director",
        packet_type="director-implementation",
        allowed_paths=["src/chunk-a/"],
        scope_files=["src/chunk-a/"],
    ),
    _packet(
        id="operator-capacity-split-chunk-a",
        owner="operator",
        packet_type="operator-verification",
        status="blocked",
    ),
    _packet(
        id="director2-capacity-split-work",
        owner="director2",
        packet_type="director-preflight",
        status="blocked",
        allowed_paths=["docs/next-brief/"],
        acceptance=["Prepare bounded planning for the next brief."],
        scope_files=["docs/next-brief/"],
    ),
    _packet(
        id="operator2-capacity-split-work",
        owner="operator2",
        packet_type="operator-preflight",
        status="blocked",
        allowed_paths=["logs/preflight/"],
        acceptance=["Run bounded preflight selector discovery."],
        scope_files=["logs/preflight/"],
    ),
]


def _write_packets(root: Path) -> None:
    packet_dir = root / "coordination" / "capacity" / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    for packet in GREEN_PACKETS:
        (packet_dir / f"{packet['id']}.json").write_text(
            json.dumps(packet, indent=2), encoding="utf-8"
        )


NARRATIVE = (("Durable Disposition", "Generated projection for route-compat fixtures."),)


def _pair(tmp_path: Path, route: dict) -> Path:
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    md_path, _ = route_manifest.write_route_pair(
        sent, route, title="Coordinator → All: Route Compat Fixture", narrative=NARRATIVE
    )
    return md_path


def test_renderer_refuses_invalid_route(tmp_path):
    with pytest.raises(ValueError):
        route_manifest.render_markdown(
            _route(schema="governance.route/v2"), title="x"
        )


def test_rendered_projection_passes_legacy_validator(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path, _route())
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()


def test_rendered_projection_with_token_passes_legacy_validator(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path, _route(side_effect_token=_token()))
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()


def test_rendered_dual_pair_projection_passes_legacy_validator(tmp_path):
    _write_packets(tmp_path)
    # dual-pair G10 phrases require a director2 director-implementation packet
    packet_dir = tmp_path / "coordination" / "capacity" / "packets"
    packet = json.loads(
        (packet_dir / "director2-capacity-split-work.json").read_text(encoding="utf-8")
    )
    packet["packet_type"] = "director-implementation"
    packet["status"] = "active"
    (packet_dir / "director2-capacity-split-work.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )
    route = _route(
        capacity_split={
            "mode": "dual_pair",
            "chunk_a": ["director-capacity-split-chunk-a"],
            "chunk_b": ["director2-capacity-split-work"],
        }
    )
    md_path = _pair(tmp_path, route)
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()


def test_pair_round_trips_through_read_manifest(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path, _route())
    assert route_manifest.read_manifest(md_path) == _route()


def test_rendered_body_never_wraps_prohibition_lines(tmp_path):
    body = route_manifest.render_markdown(
        _route(prohibitions=list(route_manifest.PROHIBITION_VOCAB)),
        title="t",
        narrative=NARRATIVE,
    )
    rendered = [
        line for line in body.splitlines() if line.startswith("- No ")
    ]
    assert len(rendered) == len(route_manifest.PROHIBITION_VOCAB)
