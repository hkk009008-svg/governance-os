from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

import pytest

import protocol_capacity
import route_lineage


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
    sent.mkdir(parents=True, exist_ok=True)
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


def _autonomous_route_body(
    extra: str = "",
    *,
    task_id: str = "autonomous-capacity-test",
    parent: str = "none",
    revision: int = 0,
    previous_owners: str = "none",
) -> str:
    return (
        f"Task ID: {task_id}\n"
        "Outcome contract: seats can deliver the routed outcome\n"
        f"Parent contract: {parent}\n"
        f"Contract revision: {revision}\n"
        f"Previous owners: {previous_owners}\n"
        "Owners: director\n"
        "Proposal ref: self-candidate\n"
        "Acceptance refs: self-candidate\n"
        "Finding refs: none\n"
        f"{extra}"
    )


def _git(repo: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    ).stdout.strip()


def _commit_legacy_parent(
    root: Path,
    *,
    task_id: str = "autonomous-capacity-test",
    generation: int = 3,
) -> str:
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Capacity Test")
    _git(root, "config", "user.email", "capacity@example.test")
    path = _write_route(
        root,
        "2026-07-18T09-00-00Z-coordinator-to-all-coordination.md",
        "# coordinator -> all: route event\n\n"
        "**When:** 2026-07-18T09:00:00Z · **From:** coordinator (online)\n\n"
        f"Task-board: {task_id}\nRoute generation: {generation}\n\n"
        "Cursor at send: 0\n",
    )
    relative = path.relative_to(root).as_posix()
    _git(root, "add", "--", relative)
    _git(root, "commit", "-q", "-m", "add parent route")
    return f"{relative}@{_git(root, 'rev-parse', 'HEAD')}"


def _commit_legacy_successor(
    root: Path,
    *,
    task_id: str,
    generation: int,
    parent_ref: str,
) -> str:
    path = _write_route(
        root,
        "2026-07-18T09-05-00Z-coordinator-to-all-coordination.md",
        "# coordinator -> all: route event\n\n"
        "**When:** 2026-07-18T09:05:00Z · **From:** coordinator (online)\n\n"
        f"Task-board: {task_id}\n"
        f"Route generation: {generation}\n"
        f"Supersedes route: {parent_ref.split('@', 1)[0]}\n\n"
        "Cursor at send: 0\n",
    )
    relative = path.relative_to(root).as_posix()
    _git(root, "add", "--", relative)
    _git(root, "commit", "-q", "-m", "add cross-task successor route")
    return f"{relative}@{_git(root, 'rev-parse', 'HEAD')}"


def _legacy_route_body(
    *,
    task_id: str,
    generation: int,
    parents: tuple[str, ...] = (),
) -> str:
    lines = [f"Task-board: {task_id}", f"Route generation: {generation}"]
    lines.extend(
        f"Supersedes route: {parent.split('@', 1)[0]}" for parent in parents
    )
    return "\n".join(lines) + "\n"


def _commit_legacy_branch(
    root: Path,
    *,
    task_id: str,
    generation: int,
    parents: tuple[str, ...],
    minute: int,
) -> str:
    path = _write_route(
        root,
        f"2026-07-18T09-{minute:02d}-00Z-coordinator-to-all-coordination.md",
        "# coordinator -> all: route event\n\n"
        f"**When:** 2026-07-18T09:{minute:02d}:00Z · "
        "**From:** coordinator (online)\n\n"
        + _legacy_route_body(
            task_id=task_id,
            generation=generation,
            parents=parents,
        )
        + "\nCursor at send: 0\n",
    )
    relative = path.relative_to(root).as_posix()
    _git(root, "add", "--", relative)
    _git(root, "commit", "-q", "-m", f"add legacy route generation {generation}")
    return f"{relative}@{_git(root, 'rev-parse', 'HEAD')}"


def _commit_two_tip_legacy_fork(root: Path) -> tuple[str, str, str]:
    root_ref = _commit_legacy_parent(
        root,
        task_id="legacy-root",
        generation=0,
    )
    left = _commit_legacy_branch(
        root,
        task_id="left-branch",
        generation=40,
        parents=(root_ref,),
        minute=10,
    )
    right = _commit_legacy_branch(
        root,
        task_id="right-branch",
        generation=1,
        parents=(root_ref,),
        minute=20,
    )
    return root_ref, left, right


def _commit_autonomous_route(
    root: Path,
    *,
    task_id: str,
    parent: str,
    revision: int,
    minute: int,
) -> str:
    name = (
        f"2026-07-18T09-{minute:02d}-00Z-director-to-all-coordination.md"
    )
    path = _write_route(
        root,
        name,
        "# director -> all: route event\n\n"
        f"**When:** 2026-07-18T09:{minute:02d}:00Z · "
        "**From:** director (online)\n\n"
        + _autonomous_route_body(
            task_id=task_id,
            parent=parent,
            revision=revision,
            previous_owners="director",
        )
        + "\nCursor at send: 0\n",
    )
    relative = path.relative_to(root).as_posix()
    _git(root, "add", "--", relative)
    _git(root, "commit", "-q", "-m", f"add route revision {revision}")
    return f"{relative}@{_git(root, 'rev-parse', 'HEAD')}"


def _compact_token_body(
    *,
    executor: str = "director",
    target: str = "origin/main",
    scope: str = "commit:abc123, ref:refs/heads/main",
) -> str:
    return (
        "\n## Side-Effect Executor Token\n\n"
        "- effect: git push\n"
        f"- executor: {executor}\n"
        f"- target: {target}\n"
        f"- scope: {scope}\n"
    )


def _legacy_token_body(*, target: str = "origin/main") -> str:
    return (
        "\n## Side-Effect Executor Token\n\n"
        "- side_effect_id: publish-main-2026-07-18\n"
        "- executor: director\n"
        f"- target: {target}\n"
        "- allowed_command_class: git push\n"
        "- preflight: git status plus divergence check\n"
        "- stop_if_newer_mail_or_live_target_satisfied: re-read mailbox and ls-remote\n"
        "- postcheck: git ls-remote origin refs/heads/main\n"
        "- observer_seats: operator, director2, operator2\n"
        "- final_closeout_owner: coordinator\n"
        "- non_goals: no force-push\n"
    )


def test_autonomous_route_needs_no_packets_join_or_capacity_split(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-00-00Z-director-to-all-coordination.md",
        _autonomous_route_body(),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.route_issues == ()
    assert result.advisories == []


def test_route_validation_rejects_prose_inside_target_allowed_paths(
    tmp_path: Path,
):
    route = _write_route(
        tmp_path,
        "2026-07-22T01-43-27Z-director-to-all-coordination.md",
        _autonomous_route_body(
            "\n## Target Allowed Paths\n\n"
            "- scripts/protocol_capacity.py\n"
            "Explanatory prose is not an allowed-path bullet.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        route.name in issue["message"]
        and "allowed-path section accepts bullet paths only" in issue["message"]
        for issue in result.route_issues
    )


def test_route_validation_accepts_semantics_after_allowed_path_heading(
    tmp_path: Path,
):
    route = _write_route(
        tmp_path,
        "2026-07-22T02-01-34Z-director-to-all-coordination.md",
        _autonomous_route_body(
            "\n## Target Allowed Paths\n\n"
            "- scripts/protocol_capacity.py\n\n"
            "## Allowed Path Semantics\n\n"
            "The bullet is implementation scope; this prose is explanation.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.route_issues == ()


def test_autonomous_route_candidate_accepts_exact_effective_parent_continuity(
    tmp_path: Path,
):
    parent_ref = _commit_legacy_parent(tmp_path, generation=3)
    route = _write_route(
        tmp_path,
        "2026-07-18T10-00-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=parent_ref,
            revision=4,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.route_issues == ()


def test_autonomous_candidate_accepts_cross_task_generation_32_33_tip(
    tmp_path: Path,
):
    generation_32 = _commit_legacy_parent(
        tmp_path,
        task_id="task6-local-acceptance",
        generation=32,
    )
    generation_33 = _commit_legacy_successor(
        tmp_path,
        task_id="route-preflight-friction",
        generation=33,
        parent_ref=generation_32,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-10-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            task_id="route-preflight-friction",
            parent=generation_33,
            revision=34,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.route_issues == ()


def test_committed_autonomous_candidate_accepts_repository_relative_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    generation_32 = _commit_legacy_parent(
        tmp_path,
        task_id="task6-local-acceptance",
        generation=32,
    )
    generation_33 = _commit_legacy_successor(
        tmp_path,
        task_id="route-preflight-friction",
        generation=33,
        parent_ref=generation_32,
    )
    candidate_ref = _commit_autonomous_route(
        tmp_path,
        task_id="route-preflight-friction",
        parent=generation_33,
        revision=34,
        minute=10,
    )
    candidate_path = Path(candidate_ref.split("@", 1)[0])
    monkeypatch.chdir(tmp_path)

    result = protocol_capacity.validate_route(tmp_path, 2, candidate_path)

    assert result.valid
    assert result.route_issues == ()


def test_autonomous_route_candidate_rejects_nonzero_root_revision(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-00-01Z-director-to-all-coordination.md",
        _autonomous_route_body(revision=1),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "parent none requires contract revision 0" in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_route_candidate_rejects_unknown_exact_parent(tmp_path: Path):
    parent_ref = _commit_legacy_parent(tmp_path)
    missing_ref = parent_ref.replace(
        "2026-07-18T09-00-00Z-coordinator-to-all-coordination.md",
        "2026-07-18T08-59-59Z-coordinator-to-all-coordination.md",
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-00-02Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=missing_ref,
            revision=4,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "parent contract is not an effective committed route" in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_route_candidate_rejects_cross_task_parent(tmp_path: Path):
    parent_ref = _commit_legacy_parent(tmp_path, task_id="different-task")
    route = _write_route(
        tmp_path,
        "2026-07-18T10-00-03Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=parent_ref,
            revision=4,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "parent Task ID does not match candidate Task ID" in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_route_candidate_rejects_nonconsecutive_revision(tmp_path: Path):
    parent_ref = _commit_legacy_parent(tmp_path, generation=3)
    route = _write_route(
        tmp_path,
        "2026-07-18T10-00-04Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=parent_ref,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "contract revision must equal parent revision plus one" in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_candidate_accepts_current_authoritative_tip(tmp_path: Path):
    parent = _commit_legacy_parent(tmp_path, generation=3)
    tip = _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=parent,
        revision=4,
        minute=10,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=tip,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid


def test_autonomous_candidate_rejects_effective_superseded_parent(tmp_path: Path):
    legacy = _commit_legacy_parent(tmp_path, generation=3)
    superseded = _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=10,
    )
    _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=superseded,
        revision=5,
        minute=20,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=superseded,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "parent contract must equal current authoritative task tip"
        in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_root_rejects_existing_same_task_route(tmp_path: Path):
    _commit_legacy_parent(tmp_path, generation=3)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "revision-zero root requires an empty committed task"
        in issue["message"]
        for issue in result.route_issues
    )


def test_autonomous_candidate_rejects_unresolved_same_task_fork(tmp_path: Path):
    legacy = _commit_legacy_parent(tmp_path, generation=3)
    left = _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=10,
    )
    _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=11,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            parent=left,
            revision=5,
            previous_owners="director",
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "current task lineage is unresolved" in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_task_with_autonomous_lineage(tmp_path: Path):
    legacy = _commit_legacy_parent(tmp_path, generation=3)
    _commit_autonomous_route(
        tmp_path,
        task_id="autonomous-capacity-test",
        parent=legacy,
        revision=4,
        minute=10,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: autonomous-capacity-test\n"
        "Route generation: 4\n"
        f"Supersedes route: {legacy.split('@', 1)[0]}\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "legacy route cannot extend a task with autonomous lineage"
        in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_new_global_root_beside_existing_tip(
    tmp_path: Path,
):
    _commit_legacy_parent(tmp_path, task_id="prior-global-task", generation=3)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: next-global-task\nRoute generation: 0\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "generated legacy route must extend current global tip"
        in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_accepts_next_global_generation_and_tip(
    tmp_path: Path,
):
    legacy = _commit_legacy_parent(
        tmp_path,
        task_id="prior-global-task",
        generation=3,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        "Task-board: next-global-task\n"
        "Route generation: 4\n"
        f"Supersedes route: {legacy.split('@', 1)[0]}\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid


def test_legacy_candidate_accepts_exact_two_tip_merge_and_restores_lineage_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    _, left, right = _commit_two_tip_legacy_fork(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=41,
            parents=(left, right),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    relative = route.relative_to(tmp_path).as_posix()
    _git(tmp_path, "add", "--", relative)
    _git(tmp_path, "commit", "-q", "-m", "reconcile legacy tips")
    assert route_lineage.main(["--root", str(tmp_path), "--check"]) == 0
    assert capsys.readouterr().out.startswith("ROUTE LINEAGE — legacy route set")


def test_legacy_candidate_rejects_partial_merge_of_current_two_tip_fork(tmp_path: Path):
    _, left, _ = _commit_two_tip_legacy_fork(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=41,
            parents=(left,),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "complete current unsuperseded tip set" in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_extra_or_non_tip_merge_parent(tmp_path: Path):
    root_ref, left, right = _commit_two_tip_legacy_fork(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=41,
            parents=(left, right, root_ref),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "complete current unsuperseded tip set" in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_unknown_merge_parent(tmp_path: Path):
    _, left, right = _commit_two_tip_legacy_fork(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=41,
            parents=(left, right, "unknown-route.md"),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "unknown parent" in issue["message"] for issue in result.route_issues
    )


def test_legacy_candidate_rejects_merge_with_wrong_successor_generation(
    tmp_path: Path,
):
    _, left, right = _commit_two_tip_legacy_fork(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=40,
            parents=(left, right),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "max current tip generation plus one" in issue["message"]
        for issue in result.route_issues
    )


def test_legacy_candidate_rejects_reconciliation_over_cyclic_current_lineage(
    tmp_path: Path,
):
    root_ref = _commit_legacy_parent(
        tmp_path,
        task_id="legacy-root",
        generation=0,
    )
    future_parent = (
        "coordination/mailbox/sent/"
        "2026-07-18T09-20-00Z-coordinator-to-all-coordination.md"
    )
    left = _commit_legacy_branch(
        tmp_path,
        task_id="cycle-left",
        generation=2,
        parents=(future_parent,),
        minute=10,
    )
    _commit_legacy_branch(
        tmp_path,
        task_id="cycle-right",
        generation=3,
        parents=(left,),
        minute=20,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=1,
            parents=(root_ref,),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "cyclic lineage" in issue["message"] for issue in result.route_issues
    )


def test_legacy_candidate_rejects_reconciliation_over_dangling_current_lineage(
    tmp_path: Path,
):
    root_ref = _commit_legacy_parent(
        tmp_path,
        task_id="legacy-root",
        generation=0,
    )
    _commit_legacy_branch(
        tmp_path,
        task_id="dangling-branch",
        generation=2,
        parents=("unknown-route.md",),
        minute=10,
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T09-30-00Z-coordinator-to-all-coordination.md",
        _legacy_route_body(
            task_id="legacy-reconciliation",
            generation=1,
            parents=(root_ref,),
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "dangling parent" in issue["message"] for issue in result.route_issues
    )


def test_capacity_findings_are_advisory_to_autonomous_route_validity(tmp_path: Path):
    packet_dir = tmp_path / "coordination" / "capacity" / "packets"
    packet_dir.mkdir(parents=True)
    (packet_dir / "malformed.json").write_text("{", encoding="utf-8")
    route = _write_route(
        tmp_path,
        "2026-07-18T10-01-00Z-director-to-all-coordination.md",
        _autonomous_route_body(),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.blocking_issues == []
    assert result.advisories
    assert result.to_dict()["advisories"] == result.advisories


def test_internal_ownership_event_is_not_an_external_effect(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-02-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            "Director may send-event an ownership proposal to exchange the route.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert not any(
        "side-effect executor token" in issue["message"]
        for issue in result.route_issues
    )


def test_complete_compact_token_is_only_structural_without_user_grant(
    tmp_path: Path,
):
    body = _autonomous_route_body(_compact_token_body())
    route = _write_route(
        tmp_path,
        "2026-07-18T10-03-00Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)
    tokens = protocol_capacity.structural_external_effect_tokens(body)

    assert result.valid
    assert len(tokens) == 1
    assert tokens[0].effect == "git push"
    assert tokens[0].executor == "director"
    assert tokens[0].target == "origin/main"
    assert tokens[0].scope == ("commit:abc123", "ref:refs/heads/main")
    assert len(result.token_results) == 1
    assert result.token_results[0].complete
    assert result.token_results[0].explicit_external_user_authorization_required
    assert result.token_results[0].execution_authorized is False


def test_legacy_token_is_readable_but_still_needs_separate_user_grant(
    tmp_path: Path,
):
    body = _autonomous_route_body(_legacy_token_body())
    route = _write_route(
        tmp_path,
        "2026-07-18T10-04-00Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)
    tokens = protocol_capacity.structural_external_effect_tokens(body)

    assert result.valid
    assert len(tokens) == 1
    assert tokens[0].effect == "git push"
    assert tokens[0].executor == "director"
    assert tokens[0].target == "origin/main"
    assert tokens[0].scope
    assert result.token_results[0].complete
    assert result.token_results[0].explicit_external_user_authorization_required
    assert result.token_results[0].execution_authorized is False


def test_incomplete_legacy_token_result_stays_structurally_incomplete(
    tmp_path: Path,
):
    body = _autonomous_route_body(
        _legacy_token_body().replace("- observer_seats: operator, director2, operator2\n", "")
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-04-30Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.token_results[0].complete
    assert "observer_seats" in result.token_results[0].issues
    assert result.token_results[0].execution_authorized is False


def test_structurally_complete_token_reports_explicit_user_authority_required(
    tmp_path: Path,
):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-05-00Z-director-to-all-coordination.md",
        _autonomous_route_body(_compact_token_body()),
    )

    rendered = protocol_capacity.validate_route(tmp_path, 2, route).to_dict()

    assert rendered["explicit_external_user_authorization_required"] is True
    assert rendered["execution_authorized"] is False
    assert rendered["structural_token_results"] == [
        {
            "complete": True,
            "issues": [],
            "explicit_external_user_authorization_required": True,
            "execution_authorized": False,
        }
    ]


def test_route_validator_never_returns_execution_authorized(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-00Z-director-to-all-coordination.md",
        _autonomous_route_body(_compact_token_body()),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.execution_authorized is False
    assert result.to_dict()["execution_authorized"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("effect", "git push"),
        ("executor", "director"),
        ("target", "origin/main"),
        ("scope", "commit:abc123, ref:refs/heads/main"),
    ),
)
def test_repeated_canonical_token_field_is_rejected(
    tmp_path: Path,
    field: str,
    value: str,
):
    token = _compact_token_body().replace(
        f"- {field}: {value}\n",
        f"- {field}: {value}\n- {field}: {value}\n",
    )
    route = _write_route(
        tmp_path,
        f"2026-07-18T10-06-1{len(field)}Z-director-to-all-coordination.md",
        _autonomous_route_body(
            token
            + "\nDirector may push origin/main after green tests "
            "scope=commit:abc123,ref:refs/heads/main\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert not result.token_results[0].complete
    assert any(
        f"duplicate side-effect executor token field: {field}" in issue["message"]
        for issue in result.route_issues
    )


@pytest.mark.parametrize(
    ("field", "alias", "value"),
    (
        ("effect", "effect kind", "git push"),
        ("executor", "executor seat", "director"),
        ("target", "target resource", "origin/main"),
        ("scope", "bounded scope", "commit:abc123, ref:refs/heads/main"),
    ),
)
def test_canonical_and_alias_duplicate_token_field_is_rejected(
    tmp_path: Path,
    field: str,
    alias: str,
    value: str,
):
    token = _compact_token_body().replace(
        f"- {field}: {value}\n",
        f"- {field}: {value}\n- {alias}: {value}\n",
    )
    route = _write_route(
        tmp_path,
        f"2026-07-18T10-06-2{len(field)}Z-director-to-all-coordination.md",
        _autonomous_route_body(token),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert not result.token_results[0].complete
    assert any(
        f"duplicate side-effect executor token field: {field}" in issue["message"]
        for issue in result.route_issues
    )


def test_two_matching_tokens_with_different_executors_are_rejected(tmp_path: Path):
    body = _autonomous_route_body(
        _compact_token_body(executor="director")
        + _compact_token_body(executor="operator")
        + "\nDirector may push origin/main after green tests "
        "scope=commit:abc123,ref:refs/heads/main\n"
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-30Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "multiple side-effect executor tokens cover" in issue["message"]
        and "different executors" in issue["message"]
        for issue in result.route_issues
    )


def test_duplicate_matching_tokens_are_rejected(tmp_path: Path):
    token = _compact_token_body()
    body = _autonomous_route_body(
        token
        + token
        + "\nDirector may push origin/main after green tests "
        "scope=commit:abc123,ref:refs/heads/main\n"
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-40Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "duplicate side-effect executor tokens cover" in issue["message"]
        for issue in result.route_issues
    )


def test_exactly_one_covering_token_is_valid(tmp_path: Path):
    body = _autonomous_route_body(
        _compact_token_body()
        + "\nDirector may push origin/main after green tests "
        "scope=commit:abc123,ref:refs/heads/main\n"
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-50Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert len(result.token_results) == 1
    assert result.token_results[0].complete
    assert result.execution_authorized is False


def test_nonmatching_scope_token_does_not_create_executor_ambiguity(tmp_path: Path):
    body = _autonomous_route_body(
        _compact_token_body(executor="director")
        + _compact_token_body(executor="operator", scope="commit:def456")
        + "\nDirector may push origin/main after green tests "
        "scope=commit:abc123,ref:refs/heads/main\n"
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-60Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid


def test_token_only_group_with_different_executors_is_rejected(tmp_path: Path):
    body = _autonomous_route_body(
        _compact_token_body(executor="director")
        + _compact_token_body(executor="operator")
    )
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-70Z-director-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "multiple side-effect executor tokens define" in issue["message"]
        and "different executors" in issue["message"]
        for issue in result.route_issues
    )


def test_token_only_exact_duplicate_group_is_rejected(tmp_path: Path):
    token = _compact_token_body()
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-71Z-director-to-all-coordination.md",
        _autonomous_route_body(token + token),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "duplicate side-effect executor tokens define" in issue["message"]
        for issue in result.route_issues
    )


def test_token_only_nonoverlapping_exact_scopes_are_valid(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-72Z-director-to-all-coordination.md",
        _autonomous_route_body(
            _compact_token_body(executor="director", scope="commit:abc123")
            + _compact_token_body(executor="operator", scope="commit:def456")
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert all(token.complete for token in result.token_results)
    assert result.execution_authorized is False


def test_token_only_single_complete_token_is_valid(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-06-73Z-director-to-all-coordination.md",
        _autonomous_route_body(_compact_token_body()),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert len(result.token_results) == 1
    assert result.token_results[0].complete
    assert result.execution_authorized is False


def test_side_effect_target_match_is_exact_not_substring(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T10-07-00Z-director-to-all-coordination.md",
        _autonomous_route_body(
            _legacy_token_body(target="evil-origin/main-backup")
            + "\nDirector may push origin/main after green tests.\n"
        ),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(
        "target/command mismatch" in issue["message"]
        for issue in result.route_issues
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
    assert "orientation: python scripts/status.py snapshot director2" in rendered
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
            "  orientation: python scripts/status.py snapshot director",
            "  packet: director-capacity-split-chunk-a "
            "(director-implementation, active)",
            "  deps: -",
            "  next: implement the named scope inside allowed paths",
            "  stop: send one committed verify-request naming full reviewed "
            "base/head or range, outcome, author seat/model, assigned Operator, "
            "and immutable finding refs",
        )
    )
    operator_block = "\n".join(
        (
            "operator",
            "  orientation: python scripts/status.py snapshot operator",
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
            "  orientation: python scripts/status.py snapshot operator",
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


def test_capacity_split_decision_is_not_a_route_validity_gate(tmp_path: Path):
    _write_capacity_split_cycle(tmp_path)
    route = _write_route(
        tmp_path,
        "2026-07-09T00-00-00Z-coordinator-to-all-coordination.md",
        _capacity_split_route_body(),
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert result.route_issues == ()


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


def test_route_validation_accepts_internal_continuation_without_terminal_heading(
    tmp_path: Path,
):
    _write_capacity_split_cycle(tmp_path)
    body = _capacity_split_route_body(
        "## Capacity Split Default\n\n"
        "- single-pair fast path remains the default for narrow or shared-file work.\n"
        "- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.\n"
        "- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.\n"
    ).replace(
        "\n\n## Exact Next Trigger\n\n"
        "Director continues Chunk A; Pair B follows the capacity split decision.\n",
        "\n",
    )
    route = _write_route(
        tmp_path,
        "2026-07-09T00-07-00Z-coordinator-to-all-coordination.md",
        body,
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert result.valid
    assert not any("Exact Next Trigger" in issue["message"] for issue in result.route_issues)


def test_dual_pair_chunk_labels_are_not_a_route_validity_gate(
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

    assert result.valid
    assert result.route_issues == ()


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
