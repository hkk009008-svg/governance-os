#!/usr/bin/env python3
"""Prove a control can fail, because three of ours could not.

Run by hand about eight times in a single day, always the same seven steps:
copy the tree, delete the guard, run the test, require red, restore, prove the
restore was exact, require green again. Two controls survived that and were
found vacuous by the other reviewer; a third asserted an inode that never
changed. Doing it by hand is what made it optional.

`seam` is the field that matters. One of the vacuous controls exercised the
guard directly and passed, while the production call site had no guard at all,
so a bypass aimed anywhere but the seam proves nothing about what ships.

Advisory tooling: it gates nothing and grants nothing.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class VacuityError(RuntimeError):
    """The control did not behave as a control must."""


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=root, capture_output=True, text=True, check=False)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prove_control_can_fail(
    root: Path, seam: str, bypass: str, test: str, python: str = sys.executable
) -> dict[str, str]:
    """Remove `bypass` from `seam`, require `test` to fail, restore, require pass.

    The copy is disposable so a crashed run cannot leave the caller's tree
    mutated, which is the failure mode of doing this in place. The digest check
    is not ceremony: a restore that silently differs would leave every later
    measurement in that tree describing something other than the source.
    """

    sandbox = Path(tempfile.mkdtemp(prefix="vacuity-"))
    try:
        work = sandbox / "tree"
        shutil.copytree(root, work, symlinks=True, ignore=shutil.ignore_patterns(".git"))
        target = work / seam
        original = target.read_text()
        if bypass not in original:
            raise VacuityError(f"seam does not contain the declared bypass: {seam}")
        before = _digest(target)

        target.write_text(original.replace(bypass, "", 1))
        removed = _run(work, python, "-m", "pytest", "-q", "-p", "no:cacheprovider", test)
        if removed.returncode == 0:
            raise VacuityError(f"VACUOUS: {test} still passes without {seam}'s guard")

        target.write_text(original)
        if _digest(target) != before:
            raise VacuityError(f"restore did not reproduce {seam}")
        restored = _run(work, python, "-m", "pytest", "-q", "-p", "no:cacheprovider", test)
        if restored.returncode != 0:
            raise VacuityError(f"{test} fails on the unmutated tree: {restored.stdout[-300:]}")
        return {"control": test, "seam": seam, "verdict": "proved", "digest": before}
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: vacuity.py <seam-path> <bypass-text> <test-id>", file=sys.stderr)
        return 2
    print(prove_control_can_fail(Path.cwd(), argv[1], argv[2], argv[3]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except VacuityError as error:
        print(f"refused: {error}", file=sys.stderr)
        raise SystemExit(1) from None
