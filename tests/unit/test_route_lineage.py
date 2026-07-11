"""Route lineage parsing, resolution, and compare-and-swap (ADR-015)."""
from __future__ import annotations

import route_lineage


def test_route_id_of_strips_path_and_md_suffix():
    assert route_lineage.route_id_of(
        "coordination/mailbox/sent/2026-07-11T09-42-22Z-coordinator-to-all-coordination.md"
    ) == "2026-07-11T09-42-22Z-coordinator-to-all-coordination"
    assert route_lineage.route_id_of("  `foo.md`  ".strip("` ")) == "foo"


def test_parse_generation_and_parent_backtick_and_plain():
    backtick = (
        "Task-board: x\n"
        "Supersedes active route: `coordination/mailbox/sent/2026-07-10T22-47-55Z-coordinator-to-all-coordination.md`\n"
        "Route generation: 7\n"
    )
    plain = (
        "Task-board: x\n"
        "Supersedes route: coordination/mailbox/sent/2026-07-11T07-38-30Z-coordinator-to-all-coordination.md\n"
        "Route generation: 12\n"
        "Expected control HEAD: 808bda9\n"
    )
    a = route_lineage.parse_lineage(backtick)
    assert a.generation == 7
    assert a.parent_route_id == "2026-07-10T22-47-55Z-coordinator-to-all-coordination"
    assert a.expected_control_head is None
    b = route_lineage.parse_lineage(plain)
    assert b.generation == 12
    assert b.parent_route_id == "2026-07-11T07-38-30Z-coordinator-to-all-coordination"
    assert b.expected_control_head == "808bda9"


def test_parse_legacy_route_without_generation():
    body = "Task-board: x\nSupersedes route: coordination/mailbox/sent/foo.md\n"
    parsed = route_lineage.parse_lineage(body)
    assert parsed.generation is None
    assert parsed.parent_route_id == "foo"


def test_parse_first_generation_no_parent():
    parsed = route_lineage.parse_lineage("Task-board: x\nRoute generation: 1\n")
    assert parsed.generation == 1
    assert parsed.parent_route_id is None


def test_control_head_lowercased():
    parsed = route_lineage.parse_lineage("Expected control HEAD: 808BDA9\n")
    assert parsed.expected_control_head == "808bda9"


def _lr(route_id, generation=None, parent=None):
    return route_lineage.LineageRoute(
        route_id, route_lineage.RouteLineage(generation, parent, None)
    )


def test_resolve_empty():
    assert route_lineage.resolve_authoritative([]).mode == "empty"


def test_resolve_legacy_when_no_generation():
    res = route_lineage.resolve_authoritative([_lr("a"), _lr("b")])
    assert res.mode == "legacy" and res.winner is None


def test_resolve_lineage_tip_is_unsuperseded_highest_generation():
    routes = [
        _lr("r1", generation=1, parent=None),
        _lr("r2", generation=2, parent="r1"),
        _lr("r3", generation=3, parent="r2"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.mode == "lineage" and res.winner == "r3" and res.issues == ()


def test_resolve_detects_forked_lineage_two_tips_same_generation():
    routes = [
        _lr("r1", generation=1, parent=None),
        _lr("r2a", generation=2, parent="r1"),
        _lr("r2b", generation=2, parent="r1"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.mode == "lineage"
    assert res.winner is not None  # still deterministic
    assert any("forked lineage" in issue for issue in res.issues)


def test_resolve_detects_cycle_no_tip():
    routes = [
        _lr("r1", generation=2, parent="r2"),
        _lr("r2", generation=1, parent="r1"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.winner is None
    assert any("no tip" in issue for issue in res.issues)


def test_resolve_is_deterministic_regardless_of_input_order():
    a = [_lr("r1", 1, None), _lr("r2", 2, "r1")]
    b = list(reversed(a))
    assert (
        route_lineage.resolve_authoritative(a).winner
        == route_lineage.resolve_authoritative(b).winner
        == "r2"
    )


def test_cas_accepts_parent_tip_and_next_generation():
    current = _lr("r2", generation=2, parent="r1")
    proposed = _lr("r3", generation=3, parent="r2")
    assert route_lineage.check_cas(current, proposed).ok


def test_cas_rejects_wrong_parent_with_stale_parent():
    current = _lr("r2", generation=2, parent="r1")
    proposed = _lr("r3", generation=3, parent="r1")  # stale: parent is not the tip
    result = route_lineage.check_cas(current, proposed)
    assert not result.ok and "stale_parent" in result.reason


def test_cas_rejects_non_incremented_generation():
    current = _lr("r2", generation=2, parent="r1")
    proposed = _lr("r9", generation=9, parent="r2")
    result = route_lineage.check_cas(current, proposed)
    assert not result.ok and "stale_parent" in result.reason
