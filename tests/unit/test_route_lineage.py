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
