"""route/v1 object validation, hashing, and sidecar manifest tests."""
from __future__ import annotations

import copy
import json

import pytest

import route_manifest


def _route(**overrides) -> dict:
    base = {
        "schema": "governance.route/v1",
        "route_id": "2026-07-11T20-00-00Z-coordinator-to-all-coordination",
        "task_board": "route-compat-cycle",
        "wave": 2,
        "generation": 1,
        "parent_route_id": None,
        "expected_control_head": None,
        "created_at": "2026-07-11T20:00:00Z",
        "created_by": "coordinator",
        "target": None,
        "packet_refs": [
            "coord-capacity-split-route",
            "director-capacity-split-chunk-a",
            "operator-capacity-split-chunk-a",
            "director2-capacity-split-work",
            "operator2-capacity-split-work",
        ],
        "packet_delta": None,
        "capability_refs": [],
        "capacity_split": {"mode": "single_pair"},
        "prohibitions": ["remote_ref_update"],
        "side_effect_token": None,
        "join_condition": "coordinator closes after both pair lanes are accounted for.",
        "next_trigger": "Director continues Chunk A; Pair B follows the capacity split decision.",
    }
    base.update(overrides)
    return base


def _token(**overrides) -> dict:
    token = {
        "side_effect_id": "publish-main-2026-07-11",
        "executor": "director",
        "target": "origin/main",
        "allowed_command_class": "git push",
        "preflight": "git status plus divergence check",
        "stop_if_newer_mail_or_live_target_satisfied": "re-read mailbox and ls-remote",
        "postcheck": "git ls-remote origin refs/heads/main",
        "observer_seats": "director2, operator, operator2",
        "final_closeout_owner": "coordinator",
        "non_goals": "no force-push and no lock claim",
    }
    token.update(overrides)
    return token


def test_valid_route_has_no_issues():
    assert route_manifest.validate_route_object(_route()) == []


def test_valid_route_with_token_has_no_issues():
    assert route_manifest.validate_route_object(_route(side_effect_token=_token())) == []


def test_non_dict_rejected():
    assert route_manifest.validate_route_object(["not", "a", "route"])


def test_unsupported_schema_version_rejected():
    issues = route_manifest.validate_route_object(_route(schema="governance.route/v2"))
    assert issues and "unsupported schema" in issues[0]


def test_unknown_field_rejected():
    issues = route_manifest.validate_route_object(_route(surprise="x"))
    assert any("unknown" in issue for issue in issues)


def test_extensions_object_permitted():
    assert route_manifest.validate_route_object(_route(extensions={"x-lab": 1})) == []


def test_missing_field_rejected():
    obj = _route()
    del obj["join_condition"]
    issues = route_manifest.validate_route_object(obj)
    assert any("missing required fields" in issue for issue in issues)


def test_generation_above_one_requires_parent():
    issues = route_manifest.validate_route_object(_route(generation=2, parent_route_id=None))
    assert any("parent_route_id" in issue for issue in issues)


def test_generation_one_forbids_parent():
    issues = route_manifest.validate_route_object(
        _route(parent_route_id="2026-07-11T10-00-00Z-coordinator-to-all-coordination")
    )
    assert any("parent_route_id" in issue for issue in issues)


def test_packet_delta_must_be_null_in_v1():
    issues = route_manifest.validate_route_object(_route(packet_delta={"changed": []}))
    assert any("packet_delta" in issue for issue in issues)


def test_capability_refs_must_be_empty_in_v1():
    issues = route_manifest.validate_route_object(_route(capability_refs=["cap-1"]))
    assert any("capability_refs" in issue for issue in issues)


def test_multi_executor_token_rejected():
    issues = route_manifest.validate_route_object(
        _route(side_effect_token=_token(executor="director and operator"))
    )
    assert any("executor" in issue for issue in issues)


def test_unknown_prohibition_rejected():
    issues = route_manifest.validate_route_object(_route(prohibitions=["push_hard"]))
    assert any("prohibition" in issue for issue in issues)


def test_weak_next_trigger_rejected():
    issues = route_manifest.validate_route_object(_route(next_trigger="none"))
    assert any("next_trigger" in issue for issue in issues)


def test_dual_pair_requires_disjoint_chunks_from_packet_refs():
    route = _route(
        capacity_split={
            "mode": "dual_pair",
            "chunk_a": ["director-capacity-split-chunk-a"],
            "chunk_b": ["director-capacity-split-chunk-a"],
        }
    )
    issues = route_manifest.validate_route_object(route)
    assert any("chunk" in issue for issue in issues)


def test_bad_created_at_rejected():
    issues = route_manifest.validate_route_object(_route(created_at="July 11, 2026"))
    assert any("created_at" in issue for issue in issues)


def test_route_id_must_be_coordinator_to_all_stem():
    issues = route_manifest.validate_route_object(_route(route_id="2026-07-11-director-note"))
    assert any("route_id" in issue for issue in issues)


def test_target_shape_checked():
    issues = route_manifest.validate_route_object(_route(target={"repository": "x"}))
    assert any("target" in issue for issue in issues)


def test_validation_does_not_mutate_input():
    obj = _route()
    snapshot = copy.deepcopy(obj)
    route_manifest.validate_route_object(obj)
    assert obj == snapshot


def test_route_hash_is_deterministic_and_key_order_free():
    obj_a = _route()
    obj_b = dict(reversed(list(_route().items())))
    assert route_manifest.route_hash(obj_a) == route_manifest.route_hash(obj_b)
    assert len(route_manifest.route_hash(obj_a)) == 64


def test_route_hash_changes_when_authority_changes():
    assert route_manifest.route_hash(_route()) != route_manifest.route_hash(
        _route(prohibitions=[])
    )


def test_route_hash_refuses_invalid_object():
    with pytest.raises(ValueError):
        route_manifest.route_hash(_route(schema="governance.route/v2"))


def _write_pair_by_hand(tmp_path, route, *, hash_line=None, sidecar_bytes=None):
    md_path = tmp_path / f"{route['route_id']}.md"
    sidecar = tmp_path / f"{route['route_id']}.route.json"
    digest = hash_line or f"route_hash: {route_manifest.route_hash(route)}"
    md_path.write_text(
        f"# Fixture route\n\nTask-board: {route['task_board']}\n\n{digest}\n",
        encoding="utf-8",
    )
    sidecar.write_bytes(
        sidecar_bytes
        if sidecar_bytes is not None
        else route_manifest.canonical_route_bytes(route)
    )
    return md_path


def test_read_manifest_round_trips(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route())
    assert route_manifest.read_manifest(md_path) == _route()


def test_read_manifest_rejects_missing_sidecar(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route())
    md_path.with_suffix(".route.json").unlink()
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


def test_read_manifest_rejects_hash_mismatch(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route(), hash_line="route_hash: " + "0" * 64)
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


def test_read_manifest_rejects_missing_hash_line(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route(), hash_line="(no pin)")
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


def test_read_manifest_rejects_noncanonical_sidecar_bytes(tmp_path):
    pretty = json.dumps(_route(), indent=2).encode("utf-8")
    md_path = _write_pair_by_hand(tmp_path, _route(), sidecar_bytes=pretty)
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)
