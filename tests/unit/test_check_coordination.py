from __future__ import annotations

from pathlib import Path

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


def test_future_live_seat_event_without_terminal_trigger_is_fatal(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-director-to-all-status.md",
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T18:01:00Z · **From:** director\n\n"
        "Body without the required terminal trigger.\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    fatal = [issue for issue in issues if issue.kind == "missing_end_trigger"]
    assert fatal
    assert fatal[0].severity == "FATAL"
    assert "must end with Exact Next Trigger" in fatal[0].message


def test_future_live_seat_event_with_terminal_trigger_passes(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-operator-to-all-verification-report.md",
        "# Operator -> All: verification\n\n"
        "**When:** 2026-07-07T18:01:00Z · **From:** operator\n\n"
        "VERDICT: GO\n\n"
        "## Exact Next Trigger\n\n"
        "Coordinator closes the route or sends a new verify-request.\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]


def test_historical_live_seat_event_before_trigger_adoption_is_exempt(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T17-53-30Z-director-to-coordinator-status.md",
        "# Director -> Coordinator: old status\n\n"
        "**When:** 2026-07-07T17:53:30Z · **From:** director\n\n"
        "Historical body without the new trigger section.\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]


def test_same_hour_event_after_colon_form_trigger_adoption_is_fatal(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    name = "2026-07-07T17-59-00Z-director-to-all-status.md"
    _write_event(
        coord,
        name,
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T17:59:00Z · **From:** director\n\n"
        "Body without the required terminal trigger.\n",
    )

    issues = cc._check_end_triggers(
        coord,
        [name],
        trigger_since="2026-07-07T17:58:38Z",
    )

    fatal = [issue for issue in issues if issue.kind == "missing_end_trigger"]
    assert fatal
    assert fatal[0].severity == "FATAL"


def test_event_just_before_colon_form_trigger_adoption_is_exempt(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    name = "2026-07-07T17-58-37Z-director-to-all-status.md"
    _write_event(
        coord,
        name,
        "# Director -> All: old status\n\n"
        "**When:** 2026-07-07T17:58:37Z · **From:** director\n\n"
        "Historical body without the new trigger section.\n",
    )

    issues = cc._check_end_triggers(
        coord,
        [name],
        trigger_since="2026-07-07T17:58:38Z",
    )

    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]


def test_future_event_with_placeholder_trigger_is_fatal(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-05-00Z-director-to-all-status.md",
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T18:05:00Z · **From:** director\n\n"
        "## Exact Next Trigger\n\n"
        "none\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:06:00Z",
        docs_root=tmp_path / "docs",
    )

    assert [issue for issue in issues if issue.kind == "missing_end_trigger"]
