"""The pack corpus must exist for anyone who clones this commit.

Reversion control for a defect that made a green suite unreproducible: an
untracked pack, and later an ignored duplicate skill name, both turned an
exact-commit failure into a pass while `git status` stayed empty.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from test_skill_packs import _PACKS, _REPO_ROOT


def test_the_pack_corpus_comes_from_committed_bytes() -> None:
    """The corpus this suite validates must exist for anyone who clones it.

    Reversion control for the defect that made a green suite unreproducible:
    an untracked pack in the working tree must not enter _PACKS.
    """

    assert _PACKS, "no tracked packs found; the suite would prove nothing"
    tracked = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "ls-files", "--error-unmatch", "--",
         *[str(pack.relative_to(_REPO_ROOT)) for pack in _PACKS]],
        capture_output=True,
        check=False,
    )
    assert tracked.returncode == 0, tracked.stderr.decode()
