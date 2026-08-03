from __future__ import annotations

from pathlib import Path
import subprocess

import check_coordination as cc
import status


def _seed_coordination(tmp_path: Path) -> Path:
    coord = tmp_path / "coordination"
    sent = coord / "mailbox" / "sent"
    seen = coord / "mailbox" / "seen"
    sent.mkdir(parents=True)
    seen.mkdir(parents=True)
    for seat in cc.ROLES:
        (seen / f"{seat}.txt").write_text("0", encoding="utf-8")
    return coord


def _write_event(coord: Path, name: str, body: str) -> None:
    (coord / "mailbox" / "sent" / name).write_text(body, encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def _review_repo(tmp_path: Path) -> tuple[Path, Path, str, str]:
    coord = _seed_coordination(tmp_path)
    (coord / "mailbox/kinds.txt").write_text(
        "verification-report\nverify-request\n", encoding="utf-8"
    )
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Coord Test")
    _git(tmp_path, "config", "user.email", "coord@example.invalid")
    (tmp_path / "payload.txt").write_text("base\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "payload.txt").write_text("head\n", encoding="utf-8")
    _git(tmp_path, "add", "payload.txt")
    _git(tmp_path, "commit", "-q", "-m", "head")
    return tmp_path, coord, base, _git(tmp_path, "rev-parse", "HEAD")


def _commit_request(
    root: Path,
    base: str,
    head: str,
    *,
    timestamp: str = "2026-07-25T07-00-00Z",
) -> tuple[str, str]:
    path = (
        "coordination/mailbox/sent/"
        f"{timestamp}-director-to-operator-verify-request.md"
    )
    when = timestamp[:11] + timestamp[11:].replace("-", ":")
    (root / path).write_text(
        "\n".join(
            (
                "# Director → Operator: test request",
                "",
                f"**When:** {when} · **From:** director (online)",
                "",
                "Event type: verify-request",
                f"Reviewed repository: {root}",
                f"Reviewed base: {base}",
                f"Reviewed head: {head}",
                "Author seat: director",
                "Author model: composer-2.5",
                "Assigned operator: operator",
                "Risk class: material-behavior",
                "",
                "## Outcome",
                "",
                "Review the exact range.",
                "",
                "## Finding Refs",
                "",
                "- sha256:" + "1" * 64,
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", "verify request")
    return path, _git(root, "rev-parse", "HEAD")


def _commit_report(
    root: Path,
    base: str,
    head: str,
    request_path: str,
    request_commit: str,
    *,
    verdict: str,
    timestamp: str = "2026-07-25T07-10-00Z",
    supersedes: str | None = None,
) -> tuple[str, str]:
    path = (
        "coordination/mailbox/sent/"
        f"{timestamp}-operator-to-director-verification-report.md"
    )
    when = timestamp[:11] + timestamp[11:].replace("-", ":")
    supersedes_line = () if supersedes is None else (f"Supersedes: {supersedes}",)
    (root / path).write_text(
        "\n".join(
            (
                f"# Operator → Director: {verdict}",
                "",
                f"**When:** {when} · **From:** operator (online)",
                "",
                "Event type: verification-report",
                f"VERDICT: {verdict}",
                f"Verification request: {request_path}@{request_commit}",
                *supersedes_line,
                f"Reviewed repository: {root}",
                f"Reviewed head: {head}",
                f"Reviewed base: {base}",
                "Reviewer seat: operator",
                "Reviewer model: claude-sonnet-5",
                "Risk class: material-behavior",
                "",
                "## Finding Refs",
                "",
                "- sha256:" + "1" * 64,
                "",
                "## Finding Dispositions",
                "",
                f"- sha256:{'1' * 64}: "
                + ("addressed" if verdict != "FAIL" else "counter-evidence"),
                "",
                "## Evidence",
                "",
                "$ independent actual-diff inspection",
                "→ exact range inspected",
                "",
                "## Findings",
                "",
                "None." if verdict != "FAIL" else "Remediation required.",
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", f"{verdict.lower()} report")
    return path, _git(root, "rev-parse", "HEAD")


def test_live_seat_event_without_terminal_trigger_heading_is_accepted(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-director-to-all-status.md",
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T18:01:00Z · **From:** director\n\n"
        "The seat chain continues internally.\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    assert not [issue for issue in issues if issue.severity == "FATAL"]
    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]


def test_heading_free_event_still_enforces_filename_envelope_and_cursor_guards(
    tmp_path: Path,
):
    coord = _seed_coordination(tmp_path)
    (coord / "mailbox/seen/director.txt").write_text(
        "not-a-cursor", encoding="utf-8"
    )
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-director-to-director-status.md",
        "# Director -> Director: status\n\n"
        "**When:** 2026-07-07T18:00:00Z · **From:** director\n\n"
        "A malformed event remains malformed without a terminal heading.\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    kinds = {issue.kind for issue in issues}
    assert {"cursor_unparseable", "self_addressed", "when_mismatch"} <= kinds
    assert "missing_end_trigger" not in kinds


def test_scalar_cursor_without_bus_reports_mailbox_fallback_unread(
    tmp_path: Path,
) -> None:
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-17T01-02-03Z-director-to-operator-status.md",
        "# Director → Operator: status\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** director (online)\n\n"
        "body\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(coord, now="2026-07-17T02:00:00Z", docs_root=tmp_path / "docs")

    unread = [
        issue.message
        for issue in issues
        if issue.kind == "unread" and "operator:" in issue.message
    ]
    assert unread == ["operator: 1 unread event(s) via mailbox-fallback"]
    assert not [issue for issue in issues if issue.kind == "transport_incoherent"]


def test_partial_bus_refs_are_fatal_transport_incoherence(tmp_path: Path) -> None:
    coord = _seed_coordination(tmp_path)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Coord Test")
    _git(tmp_path, "config", "user.email", "coord@example.invalid")
    (tmp_path / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(tmp_path, "add", "seed.txt")
    _git(tmp_path, "commit", "-q", "-m", "seed")
    _git(
        tmp_path,
        "update-ref",
        "refs/threeway/cursors/operator",
        _git(tmp_path, "rev-parse", "HEAD"),
    )

    issues = cc.run(coord, now="2026-07-17T02:00:00Z", docs_root=tmp_path / "docs")

    fatals = [
        issue for issue in issues
        if issue.kind == "transport_incoherent" and "operator" in issue.message
    ]
    assert fatals
    assert all(issue.severity == "FATAL" for issue in fatals)


def test_review_projection_failure_is_not_an_empty_pending_queue(
    tmp_path: Path, monkeypatch
) -> None:
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-25T07-00-00Z-director-to-operator-verify-request.md",
        "unreadable committed projection\n",
    )
    monkeypatch.setattr(
        cc,
        "_committed_mailbox_projection",
        lambda _root: ({}, "projection unavailable"),
    )

    state = cc.inspect_verify_review_state(tmp_path, coord)
    issues = cc._check_current_verify_requests(tmp_path, coord, state)

    assert state.pending == ()
    assert state.problem == "projection unavailable"
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


def test_coordinator_cursor_files_are_not_required_or_actionable(
    tmp_path: Path,
) -> None:
    coord = _seed_coordination(tmp_path)

    issues = cc.run(coord, now="2026-07-17T02:00:00Z", docs_root=tmp_path / "docs")

    assert not [
        issue
        for issue in issues
        if issue.kind.startswith("cursor_") and "coordinator" in issue.path
    ]
    assert not [
        issue
        for issue in issues
        if issue.kind == "unread" and "coordinator:" in issue.message
    ]


def test_new_invalid_current_verify_request_is_fatal(tmp_path: Path) -> None:
    coord = _seed_coordination(tmp_path)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Coord Test")
    _git(tmp_path, "config", "user.email", "coord@example.invalid")
    request = (
        coord
        / "mailbox/sent/"
        "2026-07-25T06-00-00Z-coordinator-to-operator-verify-request.md"
    )
    request.write_text(
        "# Coordinator → Operator: invalid request\n\n"
        "**When:** 2026-07-25T06:00:00Z · **From:** coordinator (online)\n\n"
        "Event type: verify-request\n"
        f"Reviewed head: {'a' * 40}\n"
        f"Reviewed base: {'b' * 40}\n"
        "Author seat: coordinator\n"
        "Author model: fixture\n"
        "Assigned operator: operator\n\n"
        "## Outcome\n\n"
        "Review it.\n\n"
        "Cursor at send: 0\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "invalid request")

    issues = cc.run(coord, now="2026-07-25T06:01:00Z", docs_root=tmp_path / "docs")

    invalid = [issue for issue in issues if issue.kind == "invalid_current_verify_request"]
    assert len(invalid) == 1
    assert invalid[0].severity == "FATAL"


def test_live_repo_has_no_fatal_invalid_current_verify_request(
    repo_root: Path,
) -> None:
    """No seat may be left holding an unparseable current request.

    An invalid request cannot be answered: a verdict bound to it has no
    machine-valid binding, so the work reads as accepted while nothing
    validates. The 2026-07-25 duplicate-cursor-footer request was exactly that
    case, and it was cleared by a superseding re-issue rather than by lowering
    the gate.

    A pre-cutover immutable request may still surface as ADVISORY — it is
    evidence that grants no authority, and a FATAL on an immutable artifact
    could never be cleared by anyone. Post-cutover invalid requests stay FATAL;
    that path is covered against a synthetic repository above.
    """
    issues = cc.run(
        repo_root / "coordination",
        now="2026-07-25T06:01:00Z",
        docs_root=repo_root / "docs",
    )

    invalid = [
        issue
        for issue in issues
        if issue.kind == "invalid_current_verify_request"
    ]

    assert [issue for issue in invalid if issue.severity == "FATAL"] == []
    for issue in invalid:
        assert issue.severity == "ADVISORY"
        assert "pre-cutover immutable request remains invalid" in issue.message


def test_valid_terminal_report_removes_request_from_pending(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="GO"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()


def test_valid_fail_is_terminal_but_surfaces_remediation_blocker(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.request_path, item.request_commit) for item in state.failed] == [
        (request_path, request_commit)
    ]
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


def test_malformed_or_mismatched_report_does_not_clear_pending(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root,
        base,
        head,
        request_path,
        "0" * 40,
        verdict="FAIL",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert state.failed == ()
    snapshot = status.collect_orientation_snapshot(root, "operator")
    assert snapshot["current_request"]["path"] == request_path
    assert snapshot["current_request"]["commit"] == request_commit
    assert snapshot["next_action"] == "operator reviews the exact committed request"


def test_malformed_report_does_not_clear_pending(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    path = (
        "coordination/mailbox/sent/"
        "2026-07-25T07-10-00Z-operator-to-director-verification-report.md"
    )
    (root / path).write_text(
        "\n".join(
            (
                "# Operator → Director: malformed FAIL",
                "",
                "**When:** 2026-07-25T07:10:00Z · **From:** operator (online)",
                "",
                "Event type: verification-report",
                "VERDICT: FAIL",
                f"Verification request: {request_path}@{request_commit}",
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", "malformed report")

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert state.failed == ()


def test_superseded_terminal_request_stays_complete_and_go_clears_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    _commit_report(
        root,
        base,
        head,
        request_path,
        request_commit,
        verdict="GO",
        timestamp="2026-07-25T07-20-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()


def test_live_snapshot_surfaces_real_failed_review_not_false_pending(
    repo_root: Path,
) -> None:
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T02-57-16Z-director2-to-operator2-verify-request.md"
    )
    request_commit = "eb05a76f79599b93cbc8dafa0ce1e4a42d6d5e7f"
    report_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T03-26-01Z-operator2-to-director2-verification-report.md"
    )
    report_commit = "e0fbefdb56af03b8c04b6df58245f7533a3d83c0"

    state = cc.inspect_verify_review_state(repo_root)
    snapshot = status.collect_orientation_snapshot(repo_root, "operator2")

    assert (request_path, request_commit) not in {
        (item.path, item.commit) for item in state.pending
    }
    assert (request_path, request_commit, report_path, report_commit) in {
        (
            item.request_path,
            item.request_commit,
            item.report_path,
            item.report_commit,
        )
        for item in state.failed
    }
    assert snapshot["current_request"] is None
    assert snapshot["failed_review"] == {
        "request_path": request_path,
        "request_commit": request_commit,
        "report_path": report_path,
        "report_commit": report_commit,
        "assigned_operator": "operator2",
    }
    assert "remediate failed review" in snapshot["next_action"]
