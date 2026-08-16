"""Fixtures built to the shape of the two claims that FAILed today.

Both were topology assertions written without running a command: a successor
that was a sibling, and a pull request asserted to land cleanly while GitHub
had it CONFLICTING. The tree below reproduces both shapes, so the tool is shown
a true descendant, a sibling pair, and a real conflict before it is trusted.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import composes  # noqa: E402


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _tree(tmp_path: Path) -> Path:
    """base -> descendant on main; base -> sibling on a branch, both editing
    the same line so the sibling pair genuinely conflicts."""
    root = tmp_path / "repo"
    root.mkdir()
    for args in (
        ("init", "-q", "-b", "main"),
        ("config", "user.email", "t@t"),
        ("config", "user.name", "t"),
    ):
        _git(root, *args)
    (root / "f.txt").write_text("base\n")
    _git(root, "add", "f.txt")
    _git(root, "commit", "-qm", "base")
    (root / "f.txt").write_text("main side\n")
    _git(root, "commit", "-qam", "descendant")
    _git(root, "checkout", "-q", "-b", "sibling", "HEAD~1")
    (root / "f.txt").write_text("sibling side\n")
    _git(root, "commit", "-qam", "sibling")
    return root


def test_a_true_descendant_stacks_and_merges(tmp_path: Path) -> None:
    """Known-good: a real successor. Both answers should be the easy ones."""
    root = _tree(tmp_path)

    record = composes.describes(root, "main", "main~1")

    assert record["stacks_on_target"] is True
    assert record["merges_cleanly"] is True
    assert record["conflict_paths"] == []


def test_siblings_do_not_stack_in_either_direction(tmp_path: Path) -> None:
    """The exact shape of the claim that shipped to main and was false.

    "Stacked on this" was written about two commits whose merge-base is their
    common parent. The tool must answer NO both ways rather than let the phrase
    stand.
    """
    root = _tree(tmp_path)

    record = composes.describes(root, "sibling", "main")

    assert record["stacks_on_target"] is False
    assert record["target_stacks_on_candidate"] is False
    assert record["merge_base"] == _git(root, "rev-parse", "main~1")


def test_it_reports_the_conflicting_paths(tmp_path: Path) -> None:
    """"Lands directly on this" was asserted while the PR was CONFLICTING.

    A tool that only answered the ancestry question would have agreed with the
    other half of that mistake, so this pins the conflict and its path.
    """
    root = _tree(tmp_path)

    record = composes.describes(root, "sibling", "main")

    assert record["merges_cleanly"] is False
    assert record["conflict_paths"] == ["f.txt"]


def test_it_refuses_a_revision_that_is_not_a_commit(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    try:
        composes.describes(root, "main", "does-not-exist")
    except composes.CompositionError:
        return
    raise AssertionError("a missing revision must refuse, not answer")
