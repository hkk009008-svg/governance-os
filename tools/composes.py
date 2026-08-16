#!/usr/bin/env python3
"""Answer "stacks on" and "merges cleanly" with Git, not with confidence.

Two FAILs in one day came from claims of this exact shape, written without
running the command that settles them. "The successor lands directly on this"
was false: the branches were siblings, and the pull request was CONFLICTING at
the moment I wrote it. "Stacked on this" shipped to main and was false the same
way -- merge-base answers NO in both directions.

Both took one command. Neither got it, because prose about topology reads as
though it were knowledge. So this returns a record instead of a sentence.

Advisory tooling: it gates nothing and grants nothing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class CompositionError(RuntimeError):
    """A topology question that could not be answered."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def _commit(root: Path, revision: str) -> str:
    resolved = _git(root, "rev-parse", f"{revision}^{{commit}}")
    if resolved.returncode != 0:
        raise CompositionError(f"not a commit: {revision}")
    return resolved.stdout.strip()


def describes(root: Path, candidate: str, target: str) -> dict[str, object]:
    """Whether `candidate` stacks on `target`, and whether they merge cleanly.

    Both questions, because they are independent and I have been wrong about
    each separately. A branch can be a true descendant and still conflict, and
    two siblings can merge cleanly while neither stacks on the other -- which is
    exactly the pair of mistakes that produced today's two FAILs.
    """

    candidate_sha, target_sha = _commit(root, candidate), _commit(root, target)
    stacks = _git(root, "merge-base", "--is-ancestor", target_sha, candidate_sha)
    reverse = _git(root, "merge-base", "--is-ancestor", candidate_sha, target_sha)
    base = _git(root, "merge-base", candidate_sha, target_sha)
    merged = _git(root, "merge-tree", "--write-tree", candidate_sha, target_sha)
    conflicts = sorted(
        {
            line.split("\t")[-1]
            for line in merged.stdout.splitlines()
            if line.startswith(("100644", "100755", "120000"))
        }
    )
    return {
        "candidate": candidate_sha,
        "target": target_sha,
        "merge_base": base.stdout.strip(),
        "stacks_on_target": stacks.returncode == 0,
        "target_stacks_on_candidate": reverse.returncode == 0,
        "merges_cleanly": merged.returncode == 0,
        "conflict_paths": conflicts if merged.returncode != 0 else [],
        "git": _git(root, "--version").stdout.strip(),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: composes.py <candidate> <target>", file=sys.stderr)
        return 2
    record = describes(Path.cwd(), argv[1], argv[2])
    for key, value in record.items():
        print(f"{key}: {value}")
    return 0 if record["merges_cleanly"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except CompositionError as error:
        print(f"refused: {error}", file=sys.stderr)
        raise SystemExit(2) from None
