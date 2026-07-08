from __future__ import annotations

import os
from pathlib import Path

import pytest

import latest_handoff


def _write_handoff(path: Path, *, mtime: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {path.name}\n", encoding="utf-8")
    os.utime(path, (mtime, mtime))
    return path


def test_canonical_pattern_uses_concrete_seat_identity_and_coordinator_alias():
    assert latest_handoff.canonical_pattern("director") == "HANDOFF-director-*.md"
    assert latest_handoff.canonical_pattern("operator2") == "HANDOFF-operator2-*.md"
    assert latest_handoff.canonical_pattern("coordinator") == "HANDOFF-coordinator-*.md"
    assert latest_handoff.canonical_pattern("coordinator2") == "HANDOFF-coordinator-*.md"


def test_find_latest_handoff_selects_newest_canonical_and_warns_on_near_matches(tmp_path: Path):
    docs = tmp_path / "docs"
    older = _write_handoff(docs / "HANDOFF-director-2026-07-08-older.md", mtime=100)
    newer = _write_handoff(docs / "HANDOFF-director-2026-07-09-good.md", mtime=200)
    _write_handoff(docs / "HANDOFF-director2-2026-07-10-other-seat.md", mtime=300)
    _write_handoff(docs / "HANDOFF-2026-07-09-director-session.md", mtime=400)

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == newer
    assert selection.path != older
    assert selection.pattern == "HANDOFF-director-*.md"
    assert "HANDOFF-2026-07-09-director-session.md" in selection.warnings[0]


def test_find_latest_handoff_uses_basename_as_tiebreaker_for_equal_mtime(tmp_path: Path):
    docs = tmp_path / "docs"
    low = _write_handoff(docs / "HANDOFF-operator2-2026-07-09-alpha.md", mtime=200)
    high = _write_handoff(docs / "HANDOFF-operator2-2026-07-09-zulu.md", mtime=200)

    selection = latest_handoff.find_latest_handoff(tmp_path, "operator2")

    assert selection.path == high
    assert selection.path != low


def test_main_prints_selected_path_and_warnings(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    docs = tmp_path / "docs"
    selected = _write_handoff(docs / "HANDOFF-coordinator-2026-07-09-good.md", mtime=200)
    _write_handoff(docs / "HANDOFF-2026-07-09-coordinator-session.md", mtime=300)

    rc = latest_handoff.main(["coordinator2", "--root", str(tmp_path)])
    out = capsys.readouterr()

    assert rc == 0
    assert out.out.strip() == str(selected)
    assert "HANDOFF-2026-07-09-coordinator-session.md" in out.err
