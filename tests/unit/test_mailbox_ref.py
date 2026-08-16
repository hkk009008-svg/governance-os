"""Fixtures for the reference builder, good and bad, because an instrument
that has never been shown a wrong answer cannot be trusted with a right one.

The bad cases are not hypothetical. Each is a shape that reached the fixed
writer during one day of review and was refused there: a short SHA padded out
to forty characters, a filename that was plausible and named nothing, and a
revision that resolves to something other than a commit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import mailbox_ref  # noqa: E402


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for args in (
        ("init", "-q", "-b", "main"),
        ("config", "user.email", "t@t"),
        ("config", "user.name", "t"),
    ):
        subprocess.run(["git", "-C", str(root), *args], check=True)
    (root / "event.md").write_text("body\n")
    subprocess.run(["git", "-C", str(root), "add", "event.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "one"], check=True)
    return root


def test_it_resolves_an_abbreviation_the_way_git_does(tmp_path: Path) -> None:
    """The good case: a short revision becomes the full SHA of a real commit."""
    root = _repo(tmp_path)
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    assert mailbox_ref.resolve_commit(root, head[:8]) == head
    assert mailbox_ref.reference(root, "event.md", "HEAD") == f"event.md@{head}"


def test_it_refuses_a_padded_sha(tmp_path: Path) -> None:
    """Three of today's four refusals were this: a short SHA typed out to 40.

    It is well formed, it is lowercase hex, it is exactly the right length, and
    it names nothing. Only asking Git separates it from a real one.
    """
    root = _repo(tmp_path)
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    padded = head[:8] + "0" * 32

    with pytest.raises(mailbox_ref.ReferenceError):
        mailbox_ref.resolve_commit(root, padded)


def test_it_refuses_a_filename_that_names_nothing(tmp_path: Path) -> None:
    """The fourth refusal: the SHA was right and the path was invented."""
    root = _repo(tmp_path)

    with pytest.raises(mailbox_ref.ReferenceError):
        mailbox_ref.reference(root, "coordination/mailbox/sent/invented.md", "HEAD")


def test_it_refuses_a_revision_that_is_not_a_commit(tmp_path: Path) -> None:
    """rev-parse alone would echo a tree's SHA and let it pass as provenance."""
    root = _repo(tmp_path)

    with pytest.raises(mailbox_ref.ReferenceError):
        mailbox_ref.resolve_commit(root, "HEAD^{tree}")
