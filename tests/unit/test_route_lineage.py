"""Route lineage parsing, resolution, and compare-and-swap (ADR-015)."""
from __future__ import annotations

import subprocess

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
    assert res.winner is None
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
    assert res.winner is None
    assert any(
        "forked" in issue or "multiple" in issue for issue in res.issues
    ), res.issues
    assert any("r2a" in issue for issue in res.issues), res.issues


def test_resolve_flags_dangling_parent():
    routes = [_lr("r1", generation=5, parent="ghost")]
    res = route_lineage.resolve_authoritative(routes)
    assert res.winner is None
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


# --- Autonomous per-task routes ------------------------------------------------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def _init_event_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Route Test")
    _git(repo, "config", "user.email", "route@example.test")


def _commit_event(
    repo: Path,
    *,
    sender: str,
    recipient: str,
    kind: str,
    timestamp: str,
    body: str,
) -> tuple[Path, str]:
    sent = repo / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / f"{timestamp}-{sender}-to-{recipient}-{kind}.md"
    iso = timestamp[:11] + timestamp[11:19].replace("-", ":") + "Z"
    path.write_text(
        f"# {sender} -> {recipient}: route event\n\n"
        f"**When:** {iso} · **From:** {sender} (online)\n\n"
        f"{body.rstrip()}\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    rel = path.relative_to(repo).as_posix()
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-q", "-m", f"{kind} from {sender}")
    return path, f"{rel}@{_git(repo, 'rev-parse', 'HEAD')}"


def _autonomous_body(
    *,
    task: str,
    parent: str = "(none)",
    revision: int = 0,
    previous: str = "(none)",
    owners: str = "director",
    proposal: str = "self-candidate",
    acceptances: str = "self-candidate",
    findings: str = "(none)",
) -> str:
    return "\n".join(
        (
            f"Task ID: {task}",
            "Outcome contract: deliver tested route behavior",
            f"Parent contract: {parent}",
            f"Contract revision: {revision}",
            f"Previous owners: {previous}",
            f"Owners: {owners}",
            f"Proposal ref: {proposal}",
            f"Acceptance refs: {acceptances}",
            f"Finding refs: {findings}",
        )
    )


def _root_contract(repo: Path, *, task: str, timestamp: str = "2026-07-18T08-00-00Z"):
    return _commit_event(
        repo,
        sender="director",
        recipient="all",
        kind="coordination",
        timestamp=timestamp,
        body=_autonomous_body(task=task),
    )


def _transfer_route(
    repo: Path,
    *,
    task: str,
    parent: str,
    new_owner: str,
    minute: int,
) -> tuple[Path, str]:
    proposal_body = "\n".join(
        (
            f"Task ID: {task}",
            f"Parent contract: {parent}",
            "Contract revision: 1",
            "Previous owners: director",
            f"Proposed owners: {new_owner}",
            "Outcome: deliver tested route behavior",
            "Finding refs: (none)",
        )
    )
    _, proposal_ref = _commit_event(
        repo,
        sender="director",
        recipient="all",
        kind="proposal",
        timestamp=f"2026-07-18T08-{minute:02d}-00Z",
        body=proposal_body,
    )
    _, acceptance_ref = _commit_event(
        repo,
        sender=new_owner,
        recipient="director",
        kind="proposal-reply",
        timestamp=f"2026-07-18T08-{minute + 1:02d}-00Z",
        body=proposal_body + f"\nProposal ref: {proposal_ref}",
    )
    return _commit_event(
        repo,
        sender=new_owner,
        recipient="all",
        kind="coordination",
        timestamp=f"2026-07-18T08-{minute + 2:02d}-00Z",
        body=_autonomous_body(
            task=task,
            parent=parent,
            revision=1,
            previous="director",
            owners=new_owner,
            proposal=proposal_ref,
            acceptances=acceptance_ref,
        ),
    )


def test_staged_self_is_structural_only_and_not_yet_effective(tmp_path):
    path = _write_route(
        tmp_path,
        "2026-07-18T08-00-00Z-director-to-all-coordination.md",
        _autonomous_body(task="demo-task"),
    )

    candidate = route_lineage.validate_route_candidate_structure(
        path, path.read_text(encoding="utf-8")
    )

    assert candidate.task_id == "demo-task"
    assert not candidate.effective


def test_recipient_authored_route_accepts_exact_incumbent_proposal(tmp_path):
    _init_event_repo(tmp_path)
    _, parent_ref = _root_contract(tmp_path, task="demo-task")
    _transfer_route(
        tmp_path,
        task="demo-task",
        parent=parent_ref,
        new_owner="operator",
        minute=3,
    )

    routes = route_lineage.load_routes(tmp_path)
    resolution = route_lineage.resolve_task_routes(routes, "demo-task")

    assert resolution.authoritative is not None
    assert resolution.authoritative.owners == ("operator",)
    assert resolution.issues == ()


def test_incumbent_proposal_alone_does_not_transfer(tmp_path):
    _init_event_repo(tmp_path)
    _, parent_ref = _root_contract(tmp_path, task="demo-task")
    proposal_body = "\n".join(
        (
            "Task ID: demo-task",
            f"Parent contract: {parent_ref}",
            "Contract revision: 1",
            "Previous owners: director",
            "Proposed owners: operator",
            "Outcome: deliver tested route behavior",
            "Finding refs: (none)",
        )
    )
    _, proposal_ref = _commit_event(
        tmp_path,
        sender="director",
        recipient="all",
        kind="proposal",
        timestamp="2026-07-18T08-03-00Z",
        body=proposal_body,
    )
    _commit_event(
        tmp_path,
        sender="operator",
        recipient="all",
        kind="coordination",
        timestamp="2026-07-18T08-04-00Z",
        body=_autonomous_body(
            task="demo-task",
            parent=parent_ref,
            revision=1,
            previous="director",
            owners="operator",
            proposal=proposal_ref,
            acceptances="(none)",
        ),
    )

    resolution = route_lineage.resolve_task_routes(
        route_lineage.load_routes(tmp_path), "demo-task"
    )
    assert resolution.authoritative is None
    assert any("ineffective" in issue for issue in resolution.issues)


def test_same_task_fork_fails_closed_in_both_input_orders(tmp_path):
    _init_event_repo(tmp_path)
    _, parent_ref = _root_contract(tmp_path, task="demo-task")
    _transfer_route(
        tmp_path, task="demo-task", parent=parent_ref, new_owner="operator", minute=3
    )
    _transfer_route(
        tmp_path, task="demo-task", parent=parent_ref, new_owner="operator2", minute=10
    )
    routes = route_lineage.load_routes(tmp_path)

    for ordered in (routes, list(reversed(routes))):
        resolution = route_lineage.resolve_task_routes(ordered, "demo-task")
        assert resolution.authoritative is None
        assert resolution.winner is None
        assert any("fork" in issue or "tip" in issue for issue in resolution.issues)


def test_unrelated_task_continues_when_another_task_forks(tmp_path):
    _init_event_repo(tmp_path)
    _, parent_ref = _root_contract(tmp_path, task="forked-task")
    _transfer_route(
        tmp_path, task="forked-task", parent=parent_ref, new_owner="operator", minute=3
    )
    _transfer_route(
        tmp_path, task="forked-task", parent=parent_ref, new_owner="operator2", minute=10
    )
    _root_contract(tmp_path, task="healthy-task", timestamp="2026-07-18T09-00-00Z")

    routes = route_lineage.load_routes(tmp_path)
    assert route_lineage.resolve_task_routes(routes, "forked-task").authoritative is None
    healthy = route_lineage.resolve_task_routes(routes, "healthy-task")
    assert healthy.authoritative is not None
    assert healthy.authoritative.owners == ("director",)


def test_unmarked_seat_coordination_is_not_a_route(tmp_path):
    path = _write_route(
        tmp_path,
        "2026-07-18T08-00-00Z-director-to-all-coordination.md",
        "Task ID: demo-task\nThis is ordinary coordination.\n",
    )
    assert not route_lineage.is_route_event(path, path.read_text(encoding="utf-8"))


def test_legacy_task_board_coordination_status_and_decision_are_readable(repo_root):
    paths = (
        "2026-07-07T09-36-23Z-coordinator-to-all-coordination.md",
        "2026-07-07T16-52-18Z-coordinator-to-all-status.md",
        "2026-07-07T17-12-12Z-coordinator-to-all-decision.md",
    )
    discovered = {path.name for path in route_lineage.load_route_paths(repo_root)}
    assert set(paths) <= discovered
