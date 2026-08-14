#!/usr/bin/env python3
"""check_placeholders.py — fail-closed adoption-placeholder scan (ADR-002).

Fails (exit 1) when an adoption-placeholder token appears in any file that is
NOT listed in `scripts/placeholder_allowlist.txt` and NOT under `.git/`.

Adoption note: filling a skeleton doc means REMOVING its path from
`scripts/placeholder_allowlist.txt`. When the allowlist is empty and this scan
is clean, the repo is fully bound (no skeleton placeholders remain).

Usage:  .venv/bin/python scripts/check_placeholders.py   # exit 0 clean, 1 on any violation
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import git_runner

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Allowlist file: one repo-relative path per line; # comments allowed.
ALLOWLIST_FILE = ROOT / "scripts" / "placeholder_allowlist.txt"

# Canonical placeholder tokens (from TRANSFER-MANIFEST.md "## Placeholder convention").
# Built via concatenation so this file itself does not self-trip the scan.
# Note: TODO(_P+"PROJECT"+_S) intentionally overlaps _P+"PROJECT"+_S — a line
# containing the former yields two violation entries (one for each token).
# This is benign and documented in the test suite (test_all_tokens_detected).
_P = "<"
_S = ">"
TOKENS: list[str] = [
    _P + "PROJECT" + _S,
    _P + "PROJECT_NAME" + _S,
    _P + "entrypoint" + _S,
    _P + "domain-skill" + _S,
    _P + "domain-lane-A" + _S,
    _P + "domain-lane-B" + _S,
    _P + "fill-in" + _S,
    "TODO(" + _P + "PROJECT" + _S + ")",
    _P + "ref" + _S,
]

# Fallback-only: directories to skip when git ls-files is unavailable.
# .superpowers is included so gitignored scratch does not cause false positives.
SKIP_DIRS: frozenset[str] = frozenset(
    {".git", ".venv", "__pycache__", ".pytest_cache", ".superpowers"}
)


def _load_allowlist(allowlist_file: pathlib.Path) -> frozenset[str]:
    """Return the set of repo-relative paths that are allowed to hold placeholders."""
    if not allowlist_file.exists():
        return frozenset()
    paths: set[str] = set()
    for raw_line in allowlist_file.read_text().splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line:
            paths.add(line)
    return frozenset(paths)


def _enumerate_files(root: pathlib.Path) -> list[pathlib.Path]:
    """Return the list of files to scan.

    Preferred strategy: ``git ls-files --cached --others --exclude-standard``
    run from *root*.  This enumerates tracked files plus untracked-but-NOT-ignored
    files, honouring ``.gitignore`` / ``.git/info/exclude`` automatically.
    Ignored scratch directories (``.superpowers/``, etc.) are therefore excluded
    without a hardcoded denylist.

    Fallback (when *root* is not a git checkout): filesystem walk skipping
    SKIP_DIRS.  The fallback also skips ``.superpowers/`` explicitly.
    """
    try:
        # Ceiling-pinned so a non-repository root falls back to the walk
        # instead of enumerating an enclosing checkout's files.
        result = git_runner.run_git(
            root,
            ("ls-files", "--cached", "--others", "--exclude-standard", "-z"),
            mode="dashboard",
            check=True,
        )
        raw = result.stdout
        paths = []
        for rel in raw.split(b"\x00"):
            if not rel:
                continue
            p = root / rel.decode("utf-8", errors="replace")
            if p.is_file():
                paths.append(p)
        return sorted(paths)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: filesystem walk (not a git repo, or git not available).
        files = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            parts = path.relative_to(root).parts
            if any(p in SKIP_DIRS for p in parts):
                continue
            files.append(path)
        return files


def run(root: pathlib.Path = ROOT,
        allowlist_file: pathlib.Path | None = None) -> list[str]:
    """Scan *root* for placeholder tokens; return a list of violation strings.

    Each violation string is:  ``<repo-relative-path>:<line>: <token>``
    An empty list means the tree is clean.
    """
    if allowlist_file is None:
        allowlist_file = ALLOWLIST_FILE
    allowed = _load_allowlist(allowlist_file)

    violations: list[str] = []
    for path in _enumerate_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in allowed:
            continue
        # Read bytes once; skip binary files; decode for line scanning.
        try:
            raw_bytes = path.read_bytes()
        except PermissionError:
            continue
        try:
            text = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            # Not valid UTF-8 text — treat as binary and skip.
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for token in TOKENS:
                if token in line:
                    violations.append(f"{rel}:{lineno}: {token}")
    return violations


def main() -> int:
    print("PLACEHOLDER CHECK — fail-closed adoption-placeholder scan (ADR-002)\n")
    violations = run()
    if violations:
        print(f"FAIL — {len(violations)} violation(s): placeholder token(s) found outside allowlist\n")
        for v in violations:
            print(f"  ! {v}")
        print(
            "\nTo fix: either fill in the placeholder or add the file path to "
            "scripts/placeholder_allowlist.txt."
        )
        return 1
    print("PASS — no unallowlisted placeholder tokens found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
