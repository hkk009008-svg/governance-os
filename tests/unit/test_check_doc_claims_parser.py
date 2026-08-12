"""A parser corpus for scripts/check_doc_claims.py (2k lines, no dedicated test).

Exercises the line-anchor engine end to end on a tiny synthetic repo: a
correct citation, a line-drifted symbol, a missing target file, fenced-code
immunity, the fail-loud missing-doc guard, and the atomic --fix rewriter.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import check_doc_claims as cdc


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    # A three-line source file; ``target`` is defined on line 3.
    (tmp_path / "src" / "mod.py").write_text(
        "# header\n\n" "def target():\n    return 1\n", encoding="utf-8"
    )
    return tmp_path


def _kinds(drifts, target_line: int) -> set[str]:
    return {d.kind for d in drifts if d.target_line == target_line}


def test_correct_line_anchor_has_no_drift(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "doc.md").write_text(
        "The `target` function lives at [target](src/mod.py:3).\n",
        encoding="utf-8",
    )
    drifts = cdc.check_line_anchors(["doc.md"], root)
    assert drifts == []


def test_line_drift_is_detected(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    # ``target`` is on line 3, but the doc cites line 1.
    (root / "doc.md").write_text(
        "The `target` function lives at [target](src/mod.py:1).\n",
        encoding="utf-8",
    )
    drifts = cdc.check_line_anchors(["doc.md"], root)
    assert drifts, "expected a drift for the stale line number"
    drift = drifts[0]
    assert drift.target_file == "src/mod.py"
    assert drift.suggested_line == 3


def test_missing_target_file_is_reported(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "doc.md").write_text(
        "See [ghost](src/does_not_exist.py:1).\n", encoding="utf-8"
    )
    drifts = cdc.check_line_anchors(["doc.md"], root)
    assert any(d.kind == "missing_file" for d in drifts)


def test_anchors_inside_code_fences_are_ignored(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "doc.md").write_text(
        "```\n[target](src/does_not_exist.py:99)\n```\n", encoding="utf-8"
    )
    assert cdc.check_line_anchors(["doc.md"], root) == []


def test_missing_doc_fails_loud_not_silent_green(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    with pytest.raises(FileNotFoundError):
        cdc.check_line_anchors(["absent.md"], root)


def test_fix_rewrites_the_stale_line_number_atomically(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    doc = root / "doc.md"
    doc.write_text(
        "The `target` function lives at [target](src/mod.py:1).\n",
        encoding="utf-8",
    )
    unfixed = cdc.run(["doc.md"], root, fix=True)
    assert unfixed == []
    assert "src/mod.py:3" in doc.read_text(encoding="utf-8")
    # No stray temp files left beside the doc.
    assert [p.name for p in root.iterdir() if p.name.startswith(".doc.md")] == []
