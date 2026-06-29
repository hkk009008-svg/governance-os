#!/usr/bin/env python3
"""check_arch_freshness.py — block ARCHITECTURE.md edits that forget the Last-verified bump.

R-GATE-ARCH-FRESHNESS (ADR-003): any commit that changes the substantive body of
ARCHITECTURE.md MUST also change at least one `*Last verified:` stamp line.
Editing facts without bumping the stamp leaves stale provenance on the truth layer.

The gate is INERT unless ARCHITECTURE.md is actually in the changeset — the
unbound bundle's placeholder stamp never triggers a spurious failure.

Usage:  .venv/bin/python scripts/check_arch_freshness.py [--base REF]

        --base REF     Git ref to diff against (default: merge-base of HEAD and
                       origin/main or main; falls back gracefully if git is
                       unavailable or the file is absent at BASE).

Exit codes:
    0 — ARCHITECTURE.md is not in the changeset, or the body + stamp both
        changed (or only the stamp changed, or nothing changed) — clean.
    1 — ARCHITECTURE.md body changed but the Last-verified stamp was NOT bumped.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCH_FILE = ROOT / "ARCHITECTURE.md"

_STAMP_RE = re.compile(r"^\*Last verified:[^\n]*$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Pure function — testable without git
# ---------------------------------------------------------------------------

def arch_freshness_violation(old_text: str, new_text: str) -> bool:
    """Return True iff the body changed but the Last-verified stamp(s) did not.

    "body changed" = the two texts differ after stripping all `*Last verified:`
    lines.  "stamp bumped" = the set/sequence of `*Last verified:` lines differs.

    Cases:
        body changed AND stamp unchanged → True (violation)
        body changed AND stamp changed   → False (correct bump)
        only stamp changed, body same    → False (no false positive)
        nothing changed                  → False
    """
    old_stamps = _STAMP_RE.findall(old_text)
    new_stamps = _STAMP_RE.findall(new_text)

    old_body = _STAMP_RE.sub("", old_text)
    new_body = _STAMP_RE.sub("", new_text)

    body_changed = old_body != new_body
    stamp_changed = old_stamps != new_stamps

    return body_changed and not stamp_changed


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _resolve_base() -> str | None:
    """Return the merge-base ref string, or None if git is unavailable."""
    for default_branch in ("origin/main", "main"):
        try:
            result = subprocess.run(
                ["git", "merge-base", "HEAD", default_branch],
                cwd=str(ROOT),
                capture_output=True,
                check=True,
            )
            return result.stdout.strip().decode("utf-8", errors="replace")
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


def _arch_in_changeset(base: str) -> bool:
    """Return True if ARCHITECTURE.md appears in `git diff --name-only <base>`."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base, "--", "ARCHITECTURE.md"],
            cwd=str(ROOT),
            capture_output=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _show_at_base(base: str) -> str | None:
    """Return ARCHITECTURE.md content at `base`, or None if absent/unavailable."""
    try:
        result = subprocess.run(
            ["git", "show", f"{base}:ARCHITECTURE.md"],
            cwd=str(ROOT),
            capture_output=True,
            check=True,
        )
        return result.stdout.decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# ---------------------------------------------------------------------------
# I/O driver
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gate: block ARCHITECTURE.md edits without a Last-verified bump."
    )
    parser.add_argument("--base", default=None, metavar="REF", help="Git ref to diff against.")
    args = parser.parse_args()

    # Resolve base ref.
    base = args.base or _resolve_base()
    if base is None:
        print(
            "ARCH-FRESHNESS CHECK — git unavailable or no base ref found; "
            "skipping (exit 0)."
        )
        return 0

    # Gate is INERT if ARCHITECTURE.md not in changeset.
    if not _arch_in_changeset(base):
        print(
            "ARCH-FRESHNESS CHECK — ARCHITECTURE.md not in changeset; "
            "gate inert (exit 0)."
        )
        return 0

    # Fetch old text at base.
    old_text = _show_at_base(base)
    if old_text is None:
        # New file — no prior stamp to bump; allow.
        print(
            "ARCH-FRESHNESS CHECK — ARCHITECTURE.md is a new file at this base; "
            "gate inert (exit 0)."
        )
        return 0

    # Read working-tree version.
    if not ARCH_FILE.exists():
        print(
            "ARCH-FRESHNESS CHECK — ARCHITECTURE.md absent in working tree; "
            "gate inert (exit 0)."
        )
        return 0
    new_text = ARCH_FILE.read_text(encoding="utf-8", errors="replace")

    if arch_freshness_violation(old_text, new_text):
        print(
            "ARCH-FRESHNESS CHECK — FAIL\n"
            "\n"
            "  ARCHITECTURE.md body changed but no *Last verified:* stamp was bumped.\n"
            "\n"
            "  Remedy: update the *Last verified: <YYYY-MM-DD> @ <git-sha>* line(s)\n"
            "  (header ~line 9 and footer ~last line) to today's date and your\n"
            "  commit SHA before pushing.\n"
        )
        return 1

    print("ARCH-FRESHNESS CHECK — PASS (stamp bump detected or body unchanged).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
