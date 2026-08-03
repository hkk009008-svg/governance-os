from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

import pytest

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
    baselines = tmp_path / "scripts/baselines"
    baselines.mkdir(parents=True)
    (baselines / "lane_v_reports_pre_v3.json").write_text(
        json.dumps(
            {"schema_version": "lane-v-report-pre-v3-baseline/v1", "reports": []}
        ),
        encoding="utf-8",
    )
    (baselines / "immutable_review_history_exceptions.json").write_text(
        json.dumps(
            {"schema_version": "immutable-review-history-exceptions/v1", "entries": []}
        ),
        encoding="utf-8",
    )
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
    finding_refs: bool = True,
) -> tuple[str, str]:
    path = (
        "coordination/mailbox/sent/"
        f"{timestamp}-director-to-operator-verify-request.md"
    )
    when = timestamp[:11] + timestamp[11:].replace("-", ":")
    finding_lines = () if not finding_refs else (
        "",
        "## Finding Refs",
        "",
        "- sha256:" + "1" * 64,
    )
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
                *finding_lines,
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
    legacy: bool = False,
) -> tuple[str, str]:
    path = (
        "coordination/mailbox/sent/"
        f"{timestamp}-operator-to-director-verification-report.md"
    )
    when = timestamp[:11] + timestamp[11:].replace("-", ":")
    supersedes_line = () if supersedes is None else (f"Supersedes: {supersedes}",)
    risk_lines = ("Risk class: material-behavior",)
    finding_lines = () if legacy else (
        "",
        "## Finding Refs",
        "",
        "- sha256:" + "1" * 64,
        "",
        "## Finding Dispositions",
        "",
        f"- sha256:{'1' * 64}: "
        + ("addressed" if verdict != "FAIL" else "counter-evidence"),
    )
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
                *risk_lines,
                *finding_lines,
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
    _git(tmp_path, "init", "-q")
    _write_event(
        coord,
        "2026-07-25T07-00-00Z-director-to-operator-verify-request.md",
        "unreadable committed projection\n",
    )
    monkeypatch.setattr(
        cc,
        "_committed_mailbox_projection",
        lambda _root: (None, "projection unavailable"),
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
    (coord / "mailbox/kinds.txt").write_text(
        "verify-request\n", encoding="utf-8"
    )
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


def test_same_request_go_without_supersedes_leaves_fail_active(
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
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (fail_path, fail_commit)
    ]


def test_unrelated_request_go_cannot_supersede_current_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    older_path, older_commit = _commit_request(
        root, base, head, timestamp="2026-07-25T06-00-00Z"
    )
    current_path, current_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root, base, head, current_path, current_commit, verdict="FAIL"
    )
    _commit_report(
        root,
        base,
        head,
        older_path,
        older_commit,
        verdict="GO",
        timestamp="2026-07-25T07-20-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (fail_path, fail_commit)
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


def test_modified_terminal_event_fails_immutable_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    _commit_report(
        root, base, head, request_path, request_commit, verdict="GO"
    )

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.problem is not None
    assert "immutable" in state.problem
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


@pytest.mark.parametrize("target", ("request", "report"))
def test_deleted_canonical_review_event_fails_projection(
    tmp_path: Path, target: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, _report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    deleted = request_path if target == "request" else report_path
    _git(root, "rm", "-q", deleted)
    _git(root, "commit", "-q", "-m", f"delete {target}")

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert deleted in state.problem
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


def test_renamed_terminal_report_fails_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, _report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    renamed = report_path.replace("-verification-report.md", "-status.md")
    _git(root, "mv", report_path, renamed)
    _git(root, "commit", "-q", "-m", "rename terminal report")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert report_path in state.problem


@pytest.mark.parametrize("mutation", ("removed", "empty", "duplicate"))
def test_mutated_report_request_binding_fails_projection_before_filtering(
    tmp_path: Path, mutation: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, _report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    text = report.read_text(encoding="utf-8")
    binding = f"Verification request: {request_path}@{request_commit}"
    if mutation == "removed":
        text = text.replace(binding + "\n", "")
    elif mutation == "empty":
        text = text.replace(binding, "Verification request: ")
    else:
        text = text.replace(binding, binding + "\n" + binding)
    report.write_text(text, encoding="utf-8")
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", f"mutate binding {mutation}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert "immutable" in state.problem


def test_dirty_worktree_deletion_does_not_hide_committed_fail(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    (root / request_path).unlink()
    (root / report_path).unlink()

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is None
    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


def test_nonexistent_reviewed_range_does_not_clear_pending(tmp_path: Path) -> None:
    root, coord, _base, _head = _review_repo(tmp_path)
    base, head = "0" * 40, "f" * 40
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="GO"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.failed == ()
    assert len(state.pending) == 1
    assert state.pending[0].path == request_path
    assert state.pending[0].valid is False
    assert state.pending[0].problem


@pytest.mark.parametrize("verdict", ("GO", "NITS"))
def test_valid_same_request_superseding_report_clears_fail(
    tmp_path: Path, verdict: str,
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
        verdict=verdict,
        timestamp="2026-07-25T07-20-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()


def test_review_projection_uses_bounded_git_processes(
    tmp_path: Path, monkeypatch,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    current_path, current_commit = _commit_request(root, base, head)
    template = (root / current_path).read_text(encoding="utf-8")
    unrelated: list[str] = []
    for minute in range(40):
        stamp = f"2026-07-24T06-{minute:02d}-00Z"
        when = f"2026-07-24T06:{minute:02d}:00Z"
        path = (
            "coordination/mailbox/sent/"
            f"{stamp}-director-to-operator-verify-request.md"
        )
        (root / path).write_text(
            template.replace(
                "**When:** 2026-07-25T07:00:00Z",
                f"**When:** {when}",
            ),
            encoding="utf-8",
        )
        unrelated.append(path)
    _git(root, "add", *unrelated)
    _git(root, "commit", "-q", "-m", "unrelated old requests")

    real_run = subprocess.run
    calls = 0

    def counted_run(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_run(*args, **kwargs)

    monkeypatch.setattr(cc.subprocess, "run", counted_run)
    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (current_path, current_commit)
    ]
    assert calls <= 12


def test_replace_ref_cannot_rewrite_committed_fail_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    original_head = _git(root, "rev-parse", "HEAD")
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8")
        .replace("# Operator → Director: FAIL", "# Operator → Director: GO")
        .replace("VERDICT: FAIL", "VERDICT: GO"),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    replacement_tree = _git(root, "write-tree")
    _git(root, "restore", "--staged", "--worktree", "--", report_path)
    replacement_commit = _git(
        root,
        "commit-tree",
        replacement_tree,
        "-p",
        _git(root, "rev-parse", f"{original_head}^"),
        "-m",
        "replacement GO tree",
    )
    _git(root, "replace", original_head, replacement_commit)
    assert "VERDICT: GO" in _git(root, "show", f"HEAD:{report_path}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is None
    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


def test_projection_git_scrubs_ambient_repository_and_config_overrides(
    tmp_path: Path, monkeypatch,
) -> None:
    root, _coord, _base, _head = _review_repo(tmp_path)
    expected = _git(root, "rev-parse", "HEAD")
    poisoned = {
        "GIT_INDEX_FILE": "/missing/index",
        "GIT_DIR": "/missing/git-dir",
        "GIT_WORK_TREE": "/missing/work-tree",
        "GIT_OBJECT_DIRECTORY": "/missing/objects",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/missing/alternate",
        "GIT_REPLACE_REF_BASE": "refs/hostile/replace/",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.repositoryformatversion",
        "GIT_CONFIG_VALUE_0": "999",
        "GIT_CONFIG_GLOBAL": "/missing/global-config",
        "GIT_CONFIG_SYSTEM": "/missing/system-config",
        "GIT_CONFIG_NOSYSTEM": "0",
    }
    for name, value in poisoned.items():
        monkeypatch.setenv(name, value)

    result = cc._projection_git(root, "rev-parse", "HEAD")

    assert result.returncode == 0
    assert result.stdout.decode().strip() == expected


def test_legacy_reports_do_not_add_per_artifact_git_processes(
    tmp_path: Path, monkeypatch,
) -> None:
    fixtures: list[tuple[Path, Path, str, str | None]] = []
    for report_count in (0, 5, 20):
        root, coord, base, head = _review_repo(tmp_path / f"reports-{report_count}")
        request_path, request_commit = _commit_request(
            root, base, head, finding_refs=False
        )
        fail_path = None
        for index in range(report_count):
            path, _commit = _commit_report(
                root,
                base,
                head,
                request_path,
                request_commit,
                verdict="FAIL" if index == 0 else "GO",
                timestamp=f"2026-07-25T07-{index + 10:02d}-00Z",
                legacy=True,
            )
            fail_path = fail_path or path
        _git(root, "commit", "--allow-empty", "-q", "-m", "legacy cutoff")
        fixtures.append((root, coord, _git(root, "rev-parse", "HEAD"), fail_path))

    process_counts: list[int] = []
    for root, coord, cutoff, fail_path in fixtures:
        calls: list[tuple[str, ...]] = []
        real_run = subprocess.run

        def counted_run(*args, **kwargs):
            calls.append(tuple(args[0]))
            return real_run(*args, **kwargs)

        with monkeypatch.context() as scoped:
            scoped.setattr(cc.compact_pair_loop, "LEGACY_VERBOSE_CUTOFF", cutoff)
            scoped.setattr(cc.subprocess, "run", counted_run)
            state = cc.inspect_verify_review_state(root, coord)
        process_counts.append(len(calls))
        assert not [command for command in calls if "show" in command]
        if fail_path is None:
            assert len(state.pending) == 1
            assert state.failed == ()
        else:
            assert state.pending == ()
            assert [item.report_path for item in state.failed] == [fail_path]

    assert process_counts[0] == process_counts[1] == process_counts[2]
    assert process_counts[0] <= 12


def _history_exception_entry(
    path: str,
    introduction_commit: str,
    introduction_blob: str,
    accepted_current_blob: str,
    accepted_current_sha256: str,
) -> dict[str, str]:
    is_report = path.endswith("-verification-report.md")
    return {
        "path": path,
        "artifact_class": (
            "pre-v3-report-schema-repair"
            if is_report
            else "pre-enforcement-request-schema-format"
        ),
        "introduction_commit": introduction_commit,
        "introduction_blob": introduction_blob,
        "accepted_current_blob": accepted_current_blob,
        "accepted_current_sha256": accepted_current_sha256,
        "digest_authority": (
            "scripts/baselines/lane_v_reports_pre_v3.json"
            if is_report
            else "scripts/baselines/immutable_review_history_exceptions.json"
        ),
        "reason": "measured pre-enforcement fixture repair",
    }


def _commit_history_exception(
    root: Path,
    path: str,
    introduction_commit: str,
) -> dict[str, str]:
    raw = (root / path).read_bytes()
    entry = _history_exception_entry(
        path,
        introduction_commit,
        _git(root, "rev-parse", f"{introduction_commit}:{path}"),
        _git(root, "rev-parse", f"HEAD:{path}"),
        hashlib.sha256(raw).hexdigest(),
    )
    baselines = root / "scripts/baselines"
    if path.endswith("-verification-report.md"):
        (baselines / "lane_v_reports_pre_v3.json").write_text(
            json.dumps(
                {
                    "schema_version": "lane-v-report-pre-v3-baseline/v1",
                    "reports": [
                        {"path": path, "sha256": entry["accepted_current_sha256"]}
                    ],
                }
            ),
            encoding="utf-8",
        )
    (baselines / "immutable_review_history_exceptions.json").write_text(
        json.dumps(
            {"schema_version": "immutable-review-history-exceptions/v1", "entries": [entry]}
        ),
        encoding="utf-8",
    )
    _git(root, "add", "scripts/baselines")
    _git(root, "commit", "-q", "-m", "bind exact history exception")
    return entry


def test_exact_history_exception_surfaces_advisory_and_preserves_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "# Operator → Director: FAIL", "# Operator → Director: amended FAIL"
        ),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    _commit_history_exception(root, report_path, report_commit)

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.problem is None
    assert [item.report_path for item in state.failed] == [report_path]
    assert state.grandfathered_history == (report_path,)
    assert [
        (issue.kind, issue.severity)
        for issue in issues
        if issue.kind == "grandfathered_review_history"
    ] == [("grandfathered_review_history", "ADVISORY")]


@pytest.mark.parametrize("corruption", ("path", "digest", "introduction"))
def test_history_exception_refuses_binding_corruption(
    tmp_path: Path, corruption: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace("Remediation required.", "Repair recorded."),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    entry = _commit_history_exception(root, report_path, report_commit)
    if corruption == "path":
        entry["path"] = report_path.replace("07-10-00Z", "07-11-00Z")
    elif corruption == "digest":
        entry["accepted_current_sha256"] = "0" * 64
    else:
        entry["introduction_blob"] = "0" * 40
    manifest = root / "scripts/baselines/immutable_review_history_exceptions.json"
    manifest.write_text(
        json.dumps(
            {"schema_version": "immutable-review-history-exceptions/v1", "entries": [entry]}
        ),
        encoding="utf-8",
    )
    _git(root, "add", str(manifest.relative_to(root)))
    _git(root, "commit", "-q", "-m", f"corrupt exception {corruption}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert state.pending == ()
    assert state.failed == ()


@pytest.mark.parametrize("evasion", ("delete", "change"))
def test_history_exception_refuses_later_artifact_evasion(
    tmp_path: Path, evasion: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace("Remediation required.", "Repair recorded."),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    _commit_history_exception(root, report_path, report_commit)
    if evasion == "delete":
        _git(root, "rm", "-q", report_path)
    else:
        report.write_text(
            report.read_text(encoding="utf-8") + "later drift\n", encoding="utf-8"
        )
        _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", f"later artifact {evasion}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert state.pending == ()
    assert state.failed == ()


@pytest.mark.parametrize(
    "mutation",
    (
        {"schema_version": "wrong", "entries": []},
        {
            "schema_version": "immutable-review-history-exceptions/v1",
            "entries": [
                _history_exception_entry(
                    "../bad-verification-report.md", "1" * 40, "2" * 40, "3" * 40, "4" * 64
                )
            ],
        },
    ),
)
def test_history_exception_loader_rejects_schema_and_noncanonical_paths(
    mutation: dict[str, object],
) -> None:
    exceptions, problem = cc._parse_history_exceptions(json.dumps(mutation).encode())

    assert exceptions is None
    assert problem is not None


def test_history_exception_loader_rejects_duplicate_paths() -> None:
    entry = _history_exception_entry(
        "coordination/mailbox/sent/"
        "2026-07-01T00-00-00Z-operator-to-director-verification-report.md",
        "1" * 40,
        "2" * 40,
        "3" * 40,
        "4" * 64,
    )
    raw = json.dumps(
        {
            "schema_version": "immutable-review-history-exceptions/v1",
            "entries": [entry, entry],
        }
    ).encode()

    exceptions, problem = cc._parse_history_exceptions(raw)

    assert exceptions is None
    assert problem is not None
    assert "duplicate" in problem


def _tar_bytes(*members: tuple[tarfile.TarInfo, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:") as archive:
        for member, raw in members:
            member.size = len(raw)
            archive.addfile(member, io.BytesIO(raw))
    return output.getvalue()


@pytest.mark.parametrize(
    ("name", "kind"),
    (
        ("/coordination/mailbox/kinds.txt", "file"),
        ("coordination/mailbox/sent/../escape.md", "file"),
        ("coordination/mailbox/sent/link.md", "symlink"),
    ),
)
def test_mailbox_archive_rejects_unsafe_members(name: str, kind: str) -> None:
    member = tarfile.TarInfo(name)
    if kind == "symlink":
        member.type = tarfile.SYMTYPE
        member.linkname = "coordination/mailbox/kinds.txt"

    files, problem = cc._parse_mailbox_archive(_tar_bytes((member, b"body\n")))

    assert files is None
    assert problem is not None


def test_mailbox_archive_rejects_duplicate_paths() -> None:
    name = "coordination/mailbox/kinds.txt"

    files, problem = cc._parse_mailbox_archive(
        _tar_bytes((tarfile.TarInfo(name), b"one\n"), (tarfile.TarInfo(name), b"two\n"))
    )

    assert files is None
    assert problem is not None
    assert "duplicate" in problem


def test_mailbox_archive_rejects_non_utf8_event_bytes() -> None:
    name = (
        "coordination/mailbox/sent/"
        "2026-07-25T07-10-00Z-operator-to-director-verification-report.md"
    )

    files, problem = cc._parse_mailbox_archive(
        _tar_bytes((tarfile.TarInfo(name), b"\xff\xfe"))
    )

    assert files is None
    assert problem is not None
    assert "UTF-8" in problem


def test_projection_wires_strict_archive_parser(
    tmp_path: Path, monkeypatch,
) -> None:
    root, coord, _base, _head = _review_repo(tmp_path)
    member = tarfile.TarInfo("coordination/mailbox/sent/hostile.md")
    member.type = tarfile.SYMTYPE
    member.linkname = "coordination/mailbox/kinds.txt"
    hostile_archive = _tar_bytes((member, b""))
    real_projection_git = cc._projection_git

    def hostile_projection_git(repo_root: Path, *arguments: str):
        if arguments and arguments[0] == "archive":
            return subprocess.CompletedProcess(
                args=arguments,
                returncode=0,
                stdout=hostile_archive,
                stderr=b"",
            )
        return real_projection_git(repo_root, *arguments)

    monkeypatch.setattr(cc, "_projection_git", hostile_projection_git)

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert "unexpected member type" in state.problem


def test_live_snapshot_surfaces_failed_review_and_exact_history_exceptions(
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

    assert state.problem is None
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
    assert len(state.grandfathered_history) == 6
    assert snapshot["current_request"] is None
    assert snapshot["failed_review"] == {
        "request_path": request_path,
        "request_commit": request_commit,
        "report_path": report_path,
        "report_commit": report_commit,
        "assigned_operator": "operator2",
    }
    assert snapshot["gate"] == {"status": "WARN", "fatal": 0, "advisory": 7}
    assert "remediate failed review" in snapshot["next_action"]
