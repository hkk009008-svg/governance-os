from __future__ import annotations

from pathlib import Path
import subprocess

import check_coordination as cc


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
