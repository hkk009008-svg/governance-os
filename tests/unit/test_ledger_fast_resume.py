from __future__ import annotations

import dataclasses
import os
import subprocess
from pathlib import Path

import pytest

import ledger_start_guard
import protocol_mailbox
import route_lineage
import startup_snapshot


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
    ).stdout.strip()


def _init_repo(repo: Path, *, tracked: bool = True) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Fast Resume Test")
    _git(repo, "config", "user.email", "fast-resume@example.test")
    if tracked:
        (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        _git(repo, "add", "--", "tracked.txt")
        _git(repo, "commit", "-qm", "initial target")


def _route_body(
    target: Path,
    target_head: str,
    *,
    allowed_paths: tuple[str, ...] = (),
    allowed_section_suffix: str = "",
    sender: str = "director",
    parent: str = "(none)",
    revision: int = 0,
    previous: str = "(none)",
    owners: str = "director",
    proposal: str = "self-candidate",
    acceptances: str = "self-candidate",
) -> str:
    allowed = ""
    if allowed_paths:
        allowed = (
            "\n## Allowed Paths\n"
            + "".join(f"- {path}\n" for path in allowed_paths)
            + allowed_section_suffix
            + "\n## Route Metadata\n"
        )
    return (
        f"# {sender} -> all: autonomous demo route\n\n"
        f"**When:** 2026-07-19T00:00:00Z · **From:** {sender} (online)\n\n"
        "Task ID: demo-fast-resume\n"
        "Outcome contract: deliver the exact demo outcome\n"
        f"Parent contract: {parent}\n"
        f"Contract revision: {revision}\n"
        f"Previous owners: {previous}\n"
        f"Owners: {owners}\n"
        f"Proposal ref: {proposal}\n"
        f"Acceptance refs: {acceptances}\n"
        "Finding refs: (none)\n"
        f"Target worktree: {target.as_posix()}\n"
        f"Accepted target HEAD: {target_head}\n"
        f"{allowed}\n"
        "Cursor at send: 0\n"
    )


def _make_lane(
    tmp_path: Path,
    *,
    allowed_paths: tuple[str, ...] = (),
    allowed_section_suffix: str = "",
) -> tuple[Path, Path, str, Path]:
    root = tmp_path / "Pipeline"
    target = tmp_path / "demo-app"
    _init_repo(target)
    target_head = _git(target, "rev-parse", "HEAD")
    _init_repo(root, tracked=False)
    (root / "governance.toml").write_text(
        "[kernel]\nrepository = \"example/pipeline\"\n\n"
        "[binding]\ndefault_target = \"demo-app\"\n\n"
        "[targets.demo-app]\nrepository = \"example/demo-app\"\n"
        f"path = \"{target.as_posix()}\"\n"
        "route_keywords = [\"demo\"]\n\n"
        "[paths]\nforbidden_roots = []\n",
        encoding="utf-8",
    )
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    route = sent / "2026-07-19T00-00-00Z-director-to-all-coordination.md"
    route.write_text(
        _route_body(
            target,
            target_head,
            allowed_paths=allowed_paths,
            allowed_section_suffix=allowed_section_suffix,
        ),
        encoding="utf-8",
    )
    seen = root / "coordination/mailbox/seen"
    seen.mkdir(parents=True)
    (seen / "director.txt").write_text("2099-01-01T00:00:00Z\n", encoding="utf-8")
    _git(root, "add", "--", "governance.toml", "coordination")
    _git(root, "commit", "-qm", "routed lane")
    route_ref = f"{route.relative_to(root).as_posix()}@{_git(root, 'rev-parse', 'HEAD')}"
    return root, target, route_ref, route


def _commit_event(
    root: Path,
    *,
    sender: str,
    recipient: str,
    kind: str,
    minute: int,
    body: str,
) -> str:
    timestamp = f"2026-07-19T00-{minute:02d}-00Z"
    path = (
        root
        / "coordination/mailbox/sent"
        / f"{timestamp}-{sender}-to-{recipient}-{kind}.md"
    )
    iso = timestamp[:11] + timestamp[11:19].replace("-", ":") + "Z"
    path.write_text(
        f"# {sender} -> {recipient}: route evidence\n\n"
        f"**When:** {iso} · **From:** {sender} (online)\n\n"
        f"{body.rstrip()}\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    relative = path.relative_to(root).as_posix()
    _git(root, "add", "--", relative)
    _git(root, "commit", "-qm", f"{kind} from {sender}")
    return f"{relative}@{_git(root, 'rev-parse', 'HEAD')}"


def _accepted_successor(
    root: Path,
    target: Path,
    parent_ref: str,
    *,
    new_owners: tuple[str, ...],
    minute: int,
) -> str:
    owners = ", ".join(new_owners)
    proposal_body = "\n".join(
        (
            "Task ID: demo-fast-resume",
            f"Parent contract: {parent_ref}",
            "Contract revision: 1",
            "Previous owners: director",
            f"Proposed owners: {owners}",
            "Outcome: deliver the exact demo outcome",
            "Finding refs: (none)",
        )
    )
    proposal_ref = _commit_event(
        root,
        sender="director",
        recipient="all",
        kind="proposal",
        minute=minute,
        body=proposal_body,
    )
    acceptance_refs = tuple(
        _commit_event(
            root,
            sender=owner,
            recipient="director",
            kind="proposal-reply",
            minute=minute + offset,
            body=proposal_body + f"\nProposal ref: {proposal_ref}",
        )
        for offset, owner in enumerate(new_owners, start=1)
    )
    successor_minute = minute + len(new_owners) + 1
    sender = new_owners[-1]
    full_body = _route_body(
        target,
        _git(target, "rev-parse", "HEAD"),
        sender=sender,
        parent=parent_ref,
        revision=1,
        previous="director",
        owners=owners,
        proposal=proposal_ref,
        acceptances=", ".join(acceptance_refs),
    )
    payload = full_body.split("\n\n", 2)[2].rsplit("\nCursor at send: 0\n", 1)[0]
    return _commit_event(
        root,
        sender=sender,
        recipient="all",
        kind="coordination",
        minute=successor_minute,
        body=payload,
    )


def _resume(root: Path, route_ref: str) -> ledger_start_guard.ResumeResult:
    return ledger_start_guard.build_resume(
        seat="director",
        root=root,
        kernel=root,
        binding_root=root,
        resume_from=route_ref,
    )


def _reference_classification(
    root: Path,
    route_ref: str,
    *,
    candidate_refs: tuple[str, ...] | None = None,
) -> ledger_start_guard.ResumeClassification:
    """Classify from exact per-object proofs, without the production batch path."""
    fallback = ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    try:
        expected_event = protocol_mailbox.load_committed_event_ref(root, route_ref)
    except (OSError, ValueError):
        return fallback
    if expected_event.sender not in protocol_mailbox.SEATS:
        return fallback

    try:
        routes = [
            route_lineage.validate_committed_route_effectiveness(root, ref)
            for ref in (candidate_refs or (route_ref,))
        ]
    except (OSError, ValueError):
        return fallback
    expected = next((route for route in routes if route.route_ref == route_ref), None)
    if expected is None or expected.task_id is None:
        return fallback
    resolution = route_lineage.resolve_task_routes(routes, expected.task_id)
    current = resolution.authoritative
    if resolution.issues or current is None or current.route_ref != route_ref:
        return fallback

    try:
        guidance = ledger_start_guard.parse_route_guidance_body(current.body or "")
    except ValueError:
        return fallback
    if guidance.worktree is None or guidance.accepted_target_head is None:
        return fallback

    pipeline = startup_snapshot.collect_git_snapshot(root)
    target = startup_snapshot.collect_git_snapshot(Path(guidance.worktree))
    mailbox = startup_snapshot.collect_mailbox_snapshot(root, "director")
    dirty_paths = tuple(
        path
        for state in target.dirty_paths
        for path in (state.path, state.original_path)
        if path is not None
    )
    eligible = (
        current.effective
        and not current.legacy
        and current.revision is not None
        and bool(current.owners)
        and not pipeline.errors
        and not pipeline.dirty_paths
        and not target.errors
        and target.head == guidance.accepted_target_head
        and all(path in guidance.allowed_paths for path in dirty_paths)
        and mailbox.unavailable_reason is None
        and not mailbox.unread_refs
    )
    return (
        ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
        if eligible
        else fallback
    )


def _snapshot_bytes(repo: Path) -> tuple[bytes, bytes, str, dict[str, bytes]]:
    cursor = repo / "coordination/mailbox/seen/director.txt"
    index = Path(_git(repo, "rev-parse", "--git-path", "index"))
    if not index.is_absolute():
        index = repo / index
    worktree = {
        path.relative_to(repo).as_posix(): path.read_bytes()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(repo).parts
    }
    return (
        cursor.read_bytes(),
        index.read_bytes(),
        _git(repo, "for-each-ref", "--format=%(refname) %(objectname)"),
        worktree,
    )


def test_unchanged_exact_route_clean_target_and_zero_unread_passes(tmp_path):
    root, _target, route_ref, _route = _make_lane(tmp_path)

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
    assert result.reasons == ()


def test_ordinary_cli_without_resume_from_preserves_guard_semantics_and_uses_one_status_snapshot(
    tmp_path, capsys
):
    root, _target, _route_ref, _route = _make_lane(tmp_path)

    rc = ledger_start_guard.main(
        ["--root", str(root), "--kernel", str(root), "--binding-root", str(root), "--seat", "director"]
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "Ledger seat start guard: PASS" in out
    assert out.count("seat_status.py director --wave 2") == 1
    assert "env -u GIT_INDEX_FILE git log --oneline -5" not in out
    assert "env -u GIT_INDEX_FILE git status --short\n" not in out


@pytest.mark.parametrize(
    "expected",
    ["", "not-a-ref", "coordination/mailbox/sent/missing.md@" + "0" * 40],
)
def test_malformed_missing_or_historical_expected_ref_requires_full_orientation(
    tmp_path, expected
):
    root, _target, _route_ref, _route = _make_lane(tmp_path)

    result = _resume(root, expected)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(reason.startswith("expected-route-") for reason in result.reasons)


def test_replaced_forked_or_ineffective_route_requires_full_orientation(tmp_path):
    root, _target, route_ref, route = _make_lane(tmp_path)
    route.write_text(route.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any("route" in reason for reason in result.reasons)


def test_live_malformed_candidate_issue_forces_full_orientation(tmp_path):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    malformed = (
        root
        / "coordination/mailbox/sent/2026-07-19T00-01-00Z-coordinator-to-all-coordination.md"
    )
    malformed.write_text(
        "Task-board: demo-malformed\nTask-board: demo-duplicate\n",
        encoding="utf-8",
    )
    _git(root, "add", "--", malformed.relative_to(root).as_posix())
    _git(root, "commit", "-qm", "malformed route-shaped candidate")

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(
        reason.startswith("route-candidate-issue: malformed route-shaped event:")
        for reason in result.reasons
    )


@pytest.mark.parametrize("change", ["worktree", "binding", "head"])
def test_changed_route_worktree_binding_or_target_head_requires_full_orientation(
    tmp_path, change
):
    root, target, route_ref, route = _make_lane(tmp_path)
    if change == "head":
        (target / "next.txt").write_text("next\n", encoding="utf-8")
        _git(target, "add", "--", "next.txt")
        _git(target, "commit", "-qm", "target advanced")
    elif change == "worktree":
        route.write_text(
            route.read_text(encoding="utf-8").replace(
                f"Target worktree: {target.as_posix()}",
                f"Target worktree: {(target.parent / 'other-worktree').as_posix()}",
            ),
            encoding="utf-8",
        )
    else:
        replacement = target.parent / "replacement"
        _init_repo(replacement)
        config = root / "governance.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(target.as_posix(), replacement.as_posix()),
            encoding="utf-8",
        )
        _git(root, "add", "--", "governance.toml")
        _git(root, "commit", "-qm", "binding changed")

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED


def test_changed_or_ambiguous_ownership_requires_full_orientation(tmp_path, monkeypatch):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    original = ledger_start_guard.resolve_latest_ledger_route

    def ambiguous(*args, **kwargs):
        route = original(*args, **kwargs)
        assert route is not None
        return dataclasses.replace(route, owners=())

    monkeypatch.setattr(ledger_start_guard, "resolve_latest_ledger_route", ambiguous)

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(reason.startswith("ownership-") for reason in result.reasons)


@pytest.mark.parametrize("mailbox", ["unread", "unavailable"])
def test_any_unread_or_unavailable_mailbox_state_requires_full_orientation(
    tmp_path, monkeypatch, mailbox
):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    if mailbox == "unread":
        value = startup_snapshot.MailboxSnapshot("director", "1", ("ref:2",), None)
    else:
        value = startup_snapshot.MailboxSnapshot("director", "1", (), "ref-bus")
    monkeypatch.setattr(startup_snapshot, "collect_mailbox_snapshot", lambda *_: value)

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(reason.startswith("mailbox-") for reason in result.reasons)


def test_exact_committed_allowed_paths_surface_attributable_wip(tmp_path):
    root, target, route_ref, _route = _make_lane(tmp_path, allowed_paths=("tracked.txt",))
    (target / "tracked.txt").write_text("routed edit\n", encoding="utf-8")

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
    assert any("tracked.txt" in line for line in result.lines)


@pytest.mark.parametrize("allowed", [(), ("other.txt",)])
def test_missing_ambiguous_or_out_of_lane_dirty_paths_require_full_orientation(
    tmp_path, allowed
):
    root, target, route_ref, _route = _make_lane(tmp_path, allowed_paths=allowed)
    (target / "tracked.txt").write_text("unattributed edit\n", encoding="utf-8")

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(reason.startswith("target-dirty-") for reason in result.reasons)


def test_pipeline_dirty_state_requires_full_orientation(tmp_path):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    (root / "ambient.txt").write_text("dirty\n", encoding="utf-8")

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(reason.startswith("pipeline-dirty") for reason in result.reasons)


def test_resume_preserves_valid_seats_and_rejects_coordinator2(tmp_path, capsys):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    for seat in ledger_start_guard.VALID_SEATS:
        result = ledger_start_guard.build_resume(
            seat=seat,
            root=root,
            kernel=root,
            binding_root=root,
            resume_from=route_ref,
        )
        assert result.classification is not ledger_start_guard.ResumeClassification.START_GUARD_FAIL

    with pytest.raises(SystemExit) as excinfo:
        ledger_start_guard.main(["--seat", "coordinator2", "--resume-from", route_ref])
    assert excinfo.value.code == 2
    assert "coordinator2" in capsys.readouterr().err


def test_batch_unavailable_falls_back_to_ordinary_orientation(tmp_path, monkeypatch):
    root, _target, route_ref, _route = _make_lane(tmp_path)

    def unavailable(_self):
        raise ValueError("batch unavailable")

    monkeypatch.setattr(route_lineage.RouteBatchReader, "__enter__", unavailable)

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    assert any(reason.startswith("batch-unavailable") for reason in result.reasons)
    assert any("scripts/ledger_start_guard.py --seat director --wave 2" in line for line in result.lines)


def test_existing_kernel_route_or_binding_failure_remains_start_guard_fail(tmp_path):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    wrong_root = root.parent / "wrong"
    wrong_root.mkdir()

    result = ledger_start_guard.build_resume(
        seat="director",
        root=wrong_root,
        kernel=root,
        binding_root=root,
        resume_from=route_ref,
    )

    assert result.classification is ledger_start_guard.ResumeClassification.START_GUARD_FAIL
    assert result.reasons


def test_resume_resolves_route_once_and_guard_git_processes_are_bounded(
    tmp_path, monkeypatch
):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    original_resolve = ledger_start_guard.resolve_latest_ledger_route
    original_popen = subprocess.Popen
    calls = {"resolve": 0, "git": 0}

    def counted_resolve(*args, **kwargs):
        calls["resolve"] += 1
        return original_resolve(*args, **kwargs)

    def counted_popen(*args, **kwargs):
        command = args[0] if args else kwargs.get("args", ())
        if command and Path(command[0]).name == "git":
            calls["git"] += 1
        return original_popen(*args, **kwargs)

    monkeypatch.setattr(ledger_start_guard, "resolve_latest_ledger_route", counted_resolve)
    monkeypatch.setattr(subprocess, "Popen", counted_popen)

    result = _resume(root, route_ref)

    assert result.classification is ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
    assert calls["resolve"] == 1
    assert calls["git"] <= 20


def test_full_orientation_is_exit_zero_and_never_prints_blocked(tmp_path, capsys):
    root, _target, _route_ref, _route = _make_lane(tmp_path)

    rc = ledger_start_guard.main(
        [
            "--root", str(root), "--kernel", str(root), "--binding-root", str(root),
            "--seat", "director", "--resume-from", "not-a-ref",
        ]
    )

    out = capsys.readouterr().out
    assert rc == 0
    assert "FULL ORIENTATION REQUIRED" in out
    assert "BLOCKED" not in out


def test_fast_capsule_contains_exact_body_state_ownership_and_no_effect_authority(tmp_path):
    root, target, route_ref, route = _make_lane(tmp_path)

    result = _resume(root, route_ref)
    capsule = "\n".join(result.lines)

    assert "FAST RESUME: PASS" in capsule
    assert "Seat: director" in capsule
    assert _git(root, "rev-parse", "HEAD") in capsule
    assert route_ref in capsule
    assert route.read_text(encoding="utf-8") in capsule
    assert "Task ID: demo-fast-resume" in capsule
    assert "Revision: 0" in capsule
    assert "Current owners: director" in capsule
    assert target.as_posix() in capsule
    assert _git(target, "rev-parse", "HEAD") in capsule
    assert "Unread: 0" in capsule
    assert "Routed outcome: deliver the exact demo outcome" in capsule
    assert "External effects authorized: none by fast resume" in capsule


def test_resume_collection_mutates_no_cursor_index_ref_lock_or_worktree_byte(tmp_path):
    root, _target, route_ref, _route = _make_lane(tmp_path)
    before = _snapshot_bytes(root)

    result = _resume(root, route_ref)

    after = _snapshot_bytes(root)
    assert result.classification is ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
    assert after == before


@pytest.mark.parametrize(
    "case",
    [
        "autonomous-clean",
        "autonomous-dirty",
        "accepted-transfer",
        "accepted-exchange",
        "legacy",
        "same-task-fork",
        "route-replacement",
        "changed-head",
        "unread",
        "unavailable-mailbox",
        "malformed-git",
    ],
)
def test_batch_and_reference_collectors_make_equal_decisions_over_shared_corpus(
    tmp_path, monkeypatch, case
):
    allowed = ("tracked.txt",) if case == "autonomous-dirty" else ()
    root, target, route_ref, _route = _make_lane(tmp_path, allowed_paths=allowed)
    candidate_refs = [route_ref]
    expected_ref = route_ref
    if case == "autonomous-dirty":
        (target / "tracked.txt").write_text("in lane\n", encoding="utf-8")
    elif case in {"accepted-transfer", "accepted-exchange"}:
        owners = (
            ("operator",)
            if case == "accepted-transfer"
            else ("director2", "operator")
        )
        successor_ref = _accepted_successor(
            root, target, route_ref, new_owners=owners, minute=1
        )
        candidate_refs.append(successor_ref)
        expected_ref = successor_ref
    elif case == "legacy":
        legacy_ref = _commit_event(
            root,
            sender="coordinator",
            recipient="all",
            kind="coordination",
            minute=1,
            body=(
                "Task-board: demo-fast-resume\n"
                f"Target worktree: {target.as_posix()}\n"
                f"Accepted target HEAD: {_git(target, 'rev-parse', 'HEAD')}"
            ),
        )
        candidate_refs.append(legacy_ref)
        expected_ref = legacy_ref
    elif case == "same-task-fork":
        first = _accepted_successor(
            root, target, route_ref, new_owners=("operator",), minute=1
        )
        second = _accepted_successor(
            root, target, route_ref, new_owners=("operator2",), minute=10
        )
        candidate_refs.extend((first, second))
        expected_ref = second
    elif case == "route-replacement":
        candidate_refs.append(
            _accepted_successor(
                root, target, route_ref, new_owners=("operator",), minute=1
            )
        )
    elif case == "changed-head":
        (target / "next.txt").write_text("next\n", encoding="utf-8")
        _git(target, "add", "--", "next.txt")
        _git(target, "commit", "-qm", "changed head")
    elif case == "unread":
        monkeypatch.setattr(
            startup_snapshot,
            "collect_mailbox_snapshot",
            lambda *_: startup_snapshot.MailboxSnapshot("director", "1", ("ref:2",), None),
        )
    elif case == "unavailable-mailbox":
        monkeypatch.setattr(
            startup_snapshot,
            "collect_mailbox_snapshot",
            lambda *_: startup_snapshot.MailboxSnapshot("director", "1", (), "ref-bus"),
        )
    elif case == "malformed-git":
        original = startup_snapshot.collect_git_snapshot
        monkeypatch.setattr(
            startup_snapshot,
            "collect_git_snapshot",
            lambda path, **kwargs: dataclasses.replace(
                original(path, **kwargs), errors=("dirty paths parse error: malformed porcelain record",)
            ),
        )

    production = _resume(root, expected_ref).classification
    reference = _reference_classification(
        root, expected_ref, candidate_refs=tuple(candidate_refs)
    )
    expected = (
        ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
        if case
        in {
            "autonomous-clean",
            "autonomous-dirty",
            "accepted-transfer",
            "accepted-exchange",
        }
        else ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    )

    assert reference is expected
    assert production is reference


def test_reference_classifier_never_calls_batch_or_production_resume(
    tmp_path, monkeypatch
):
    root, _target, route_ref, _route = _make_lane(tmp_path)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("reference path called production batch resume")

    monkeypatch.setattr(ledger_start_guard, "build_resume", forbidden)
    monkeypatch.setattr(route_lineage.RouteBatchReader, "__enter__", forbidden)

    assert (
        _reference_classification(root, route_ref)
        is ledger_start_guard.ResumeClassification.FAST_RESUME_PASS
    )


def test_allowed_path_section_rejects_prose_after_a_valid_bullet(tmp_path):
    root, _target, route_ref, _route = _make_lane(
        tmp_path,
        allowed_paths=("tracked.txt",),
        allowed_section_suffix="This prose is still inside the allowed-path section.\n",
    )

    result = _resume(root, route_ref)

    assert (
        result.classification
        is ledger_start_guard.ResumeClassification.FULL_ORIENTATION_REQUIRED
    )
    assert any(reason.startswith("route-guidance-invalid:") for reason in result.reasons)


def test_route_guidance_is_strict_and_never_infers_path_scope_from_prose(tmp_path):
    target = tmp_path / "target"
    head = "a" * 40
    body = (
        f"Target worktree: {target}\n"
        f"Accepted target HEAD: {head}\n"
        "Only edit inferred/from/prose.py\n"
        "\n## Allowed Paths\n- exact/path.py\n"
    )
    assert ledger_start_guard.parse_route_guidance_body(body) == ledger_start_guard.RouteGuidance(
        worktree=target.as_posix(),
        accepted_target_head=head,
        allowed_paths=("exact/path.py",),
    )
    for invalid in (
        body + "Target worktree: /duplicate\n",
        body + "\n## Target Allowed Paths\n- second.py\n",
        body.replace("a" * 40, "A" * 40),
        body.replace("exact/path.py", "../escape.py"),
        body.replace("exact/path.py", "/absolute.py"),
        body.replace("exact/path.py", "wild/*.py"),
        body.replace("- exact/path.py\n", "- exact/path.py\n- exact/path.py\n"),
        body.replace(target.as_posix(), (target / ".." / "escape").as_posix()),
    ):
        with pytest.raises(ValueError):
            ledger_start_guard.parse_route_guidance_body(invalid)
