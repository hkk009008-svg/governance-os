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
