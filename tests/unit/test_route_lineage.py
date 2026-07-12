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


# --- Cross-model part-#4: check_cas must enforce int-only generations ---------
#
# Rule #13 symmetric-endpoint gap: the sibling currency gate
# route_capability.capability_is_current enforces `type(...) is int` ("a boolean
# grant must never ride an int-1 route into current"), but check_cas — the
# CAS-acceptance gate — did not. Because `True == 1 == 0 + 1`, a bool generation
# rode the successor arithmetic. Defense-in-depth (check_cas has no prod caller
# today, and parse_lineage only ever emits real ints), but the two gates must
# agree so a future JSON/TOML source (where `true` parses to bool) cannot slip
# a bool generation through one gate but not the other.

def test_cas_rejects_bool_generation_int_only():
    # 0 -> True is the numeric successor (True == 1 == 0 + 1), so ONLY the type,
    # not the arithmetic, distinguishes accept from refuse.
    current = _lr("r0", generation=0, parent=None)
    proposed = _lr("r1", generation=True, parent="r0")  # bool where int required
    result = route_lineage.check_cas(current, proposed)
    assert not result.ok and "integer" in result.reason


def test_cas_rejects_bool_generation_on_current_side():
    current = _lr("r0", generation=True, parent=None)
    proposed = _lr("r1", generation=2, parent="r0")
    result = route_lineage.check_cas(current, proposed)
    assert not result.ok and "integer" in result.reason


def test_cas_still_accepts_plain_int_generations():
    # positive control: the ordinary int successor path is unaffected.
    assert route_lineage.check_cas(_lr("r1", 1, None), _lr("r2", 2, "r1")).ok


# --- Task 4: load_routes + --check CLI + lineage-first guard rewire ---
from pathlib import Path


def _write_route(root: Path, name: str, body: str) -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / name
    path.write_text(body, encoding="utf-8")
    return path


def test_find_latest_is_lineage_tip_when_generations_present(tmp_path):
    import ledger_start_guard

    # older filename carries the HIGHER generation -> lineage must beat filename sort
    _write_route(
        tmp_path,
        "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-a\nThis routes ledger work.\nRoute generation: 3\n"
        "Supersedes route: coordination/mailbox/sent/2026-07-12T09-00-00Z-coordinator-to-all-coordination.md\n",
    )
    _write_route(
        tmp_path,
        "2026-07-12T09-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-b\nThis routes ledger work.\nRoute generation: 2\n",
    )
    result = ledger_start_guard.find_latest_ledger_route(tmp_path)
    assert result is not None
    assert result.name == "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md"


def test_find_latest_falls_back_to_reverse_lex_without_generation(tmp_path):
    import ledger_start_guard

    _write_route(
        tmp_path,
        "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-a\nThis routes ledger work.\n",
    )
    newest = _write_route(
        tmp_path,
        "2026-07-12T09-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-b\nThis routes ledger work.\n",
    )
    result = ledger_start_guard.find_latest_ledger_route(tmp_path)
    assert result == newest  # identical to prior reverse-lex behavior


def test_check_cli_passes_on_legacy_route_set(tmp_path, capsys):
    _write_route(
        tmp_path,
        "2026-07-12T09-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: ledger-b\nThis routes ledger work.\n",
    )
    rc = route_lineage.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0 and "legacy" in out.lower()


def test_check_cli_fails_on_forked_lineage(tmp_path, capsys):
    _write_route(
        tmp_path,
        "2026-07-12T01-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: a\nRoute generation: 1\n",
    )
    _write_route(
        tmp_path,
        "2026-07-12T02-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: b\nRoute generation: 2\n"
        "Supersedes route: 2026-07-12T01-00-00Z-coordinator-to-all-coordination.md\n",
    )
    _write_route(
        tmp_path,
        "2026-07-12T03-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: c\nRoute generation: 2\n"
        "Supersedes route: 2026-07-12T01-00-00Z-coordinator-to-all-coordination.md\n",
    )
    rc = route_lineage.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1 and "forked lineage" in out


def test_protocol_doctor_base_commands_include_lineage_check():
    import protocol_doctor

    commands = protocol_doctor.base_commands(python_executable="PY", wave=2)
    assert ["PY", "scripts/route_lineage.py", "--check"] in commands


# --- Task 4 hardening: --check as a complete audit surface ---


def test_resolve_flags_abandoned_different_generation_branch():
    # r2a is an unsuperseded orphan tip at gen2 alongside r3b at gen3 -> a fork,
    # even though the two live tips are at DIFFERENT generations.
    routes = [
        _lr("r1", generation=1, parent=None),
        _lr("r2a", generation=2, parent="r1"),
        _lr("r2b", generation=2, parent="r1"),
        _lr("r3b", generation=3, parent="r2b"),
    ]
    res = route_lineage.resolve_authoritative(routes)
    assert res.mode == "lineage"
    assert res.winner == "r3b"  # highest-generation tip, deterministic
    assert any(
        "forked" in issue or "multiple" in issue for issue in res.issues
    ), res.issues
    assert any("r2a" in issue for issue in res.issues), res.issues


def test_resolve_flags_dangling_parent():
    routes = [_lr("r1", generation=5, parent="ghost")]
    res = route_lineage.resolve_authoritative(routes)
    assert res.winner == "r1"  # unchanged winner
    assert any(
        "dangling parent" in issue and "ghost" in issue for issue in res.issues
    ), res.issues


def test_check_cli_fails_on_dangling_parent(tmp_path, capsys):
    _write_route(
        tmp_path,
        "2026-07-12T05-00-00Z-coordinator-to-all-coordination.md",
        "Task-board: x\nRoute generation: 5\n"
        "Supersedes route: 2026-07-11T00-00-00Z-coordinator-to-all-coordination.md\n",
    )
    rc = route_lineage.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1 and "dangling parent" in out
