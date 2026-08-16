#!/usr/bin/env python3
"""Build mailbox references that resolve, because four of mine did not.

In one day three padded SHAs and one invented filename reached the fixed
writer, which refused all four. Every one was hand-typed where Git already
held the answer, and no amount of care changed the rate. So the reference is
produced rather than written: resolve the revision, prove it names a commit,
prove the path exists in that commit, and emit `path@sha` or fail loudly.

Advisory tooling. It gates nothing and grants nothing; the fixed writer
remains the only thing that decides whether an event is admissible.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FULL_SHA_LENGTH = 40
_HEX = frozenset("0123456789abcdef")


class ReferenceError(RuntimeError):
    """A reference that would not resolve for the reader who checks it."""


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ReferenceError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def resolve_commit(root: Path, revision: str) -> str:
    """Full 40-hex SHA of `revision`, proving it names a commit and not a tree.

    `rev-parse` alone would happily echo a 40-character string that names
    nothing, which is exactly the shape that got refused; `^{commit}` makes Git
    assert the object exists and is a commit before we believe the digits.
    """

    sha = _git(root, "rev-parse", f"{revision}^{{commit}}")
    if len(sha) != FULL_SHA_LENGTH or not set(sha) <= _HEX:
        raise ReferenceError(f"not a full lowercase commit SHA: {sha}")
    return sha


def reference(root: Path, path: str, revision: str) -> str:
    """`path@sha` for a mailbox event, proving the path exists at that commit.

    The invented filename passed every syntactic check and named nothing. Only
    asking Git for the blob catches that, so this asks.
    """

    sha = resolve_commit(root, revision)
    _git(root, "cat-file", "-e", f"{sha}:{path}")
    return f"{path}@{sha}"


def main(argv: list[str]) -> int:
    if len(argv) == 2:
        print(resolve_commit(Path.cwd(), argv[1]))
    elif len(argv) == 3:
        print(reference(Path.cwd(), argv[1], argv[2]))
    else:
        print("usage: mailbox_ref.py <revision> | <path> <revision>", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except ReferenceError as error:
        print(f"refused: {error}", file=sys.stderr)
        raise SystemExit(1) from None
