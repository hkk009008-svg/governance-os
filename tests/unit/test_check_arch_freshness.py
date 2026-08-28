"""Unit tests for pipeline/check_arch_freshness.py — Last-verified stamp gate.

Tests the pure `arch_freshness_violation(old_text, new_text) -> bool` helper.
No git fixture needed — the function is hermetic over string inputs.

Cases from brief:
  (a) body changed, stamp line(s) unchanged → violation True (would fail CI)
  (b) body changed AND a *Last verified:* line bumped → False (passes)
  (c) only the stamp changed, body identical → False (no false positive)
  (d) nothing changed → False
"""
from __future__ import annotations

import check_arch_freshness as caf


# ---------------------------------------------------------------------------
# Shared fixture text
# ---------------------------------------------------------------------------

_BASE = """\
# ARCHITECTURE.md — Governance OS

*Last verified: <date> @ <sha>*

---

## §1 Purpose

A multi-agent governance operating system.

---

## §2 Topology

Six subsystems interconnect here.

*Last verified: <YYYY-MM-DD> @ <git-sha>*
"""

_BODY_CHANGED = """\
# ARCHITECTURE.md — Governance OS

*Last verified: <date> @ <sha>*

---

## §1 Purpose

A multi-agent governance operating system — updated description.

---

## §2 Topology

Six subsystems interconnect here.

*Last verified: <YYYY-MM-DD> @ <git-sha>*
"""

_BODY_CHANGED_STAMP_BUMPED = """\
# ARCHITECTURE.md — Governance OS

*Last verified: 2026-06-30 @ abc1234*

---

## §1 Purpose

A multi-agent governance operating system — updated description.

---

## §2 Topology

Six subsystems interconnect here.

*Last verified: 2026-06-30 @ abc1234*
"""

_ONLY_STAMP_CHANGED = """\
# ARCHITECTURE.md — Governance OS

*Last verified: 2026-06-30 @ abc1234*

---

## §1 Purpose

A multi-agent governance operating system.

---

## §2 Topology

Six subsystems interconnect here.

*Last verified: 2026-06-30 @ abc1234*
"""


# ---------------------------------------------------------------------------
# (a) body changed, stamp unchanged → violation
# ---------------------------------------------------------------------------

def test_body_changed_stamp_unchanged_is_violation():
    """Body changed but both stamp lines identical → violation (True)."""
    result = caf.arch_freshness_violation(_BASE, _BODY_CHANGED)
    assert result is True, (
        "Expected violation when body changed but stamp unchanged"
    )


# ---------------------------------------------------------------------------
# (b) body changed AND stamp bumped → no violation
# ---------------------------------------------------------------------------

def test_body_changed_stamp_bumped_is_clean():
    """Body changed AND stamp bumped → passes (False)."""
    result = caf.arch_freshness_violation(_BASE, _BODY_CHANGED_STAMP_BUMPED)
    assert result is False, (
        "Expected no violation when body changed and stamp was also bumped"
    )


# ---------------------------------------------------------------------------
# (c) only stamp changed, body identical → no violation (no false positive)
# ---------------------------------------------------------------------------

def test_only_stamp_changed_no_false_positive():
    """Only the stamp line(s) changed, body identical → no violation (False)."""
    result = caf.arch_freshness_violation(_BASE, _ONLY_STAMP_CHANGED)
    assert result is False, (
        "Expected no false positive when only the stamp changed"
    )


# ---------------------------------------------------------------------------
# (d) nothing changed → no violation
# ---------------------------------------------------------------------------

def test_nothing_changed_is_clean():
    """Identical old and new text → no violation (False)."""
    result = caf.arch_freshness_violation(_BASE, _BASE)
    assert result is False, (
        "Expected no violation when nothing changed"
    )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_single_stamp_line_bumped():
    """Works correctly when only one stamp line is present."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nSome body text.\n"
    new_bumped = "# Arch\n\n*Last verified: 2026-06-30 @ abc1234*\n\nSome body text.\n"
    assert caf.arch_freshness_violation(old, new_bumped) is False


def test_single_stamp_not_bumped_body_changed():
    """Single stamp line not bumped, body changed → violation."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nOriginal body.\n"
    new_not_bumped = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nChanged body.\n"
    assert caf.arch_freshness_violation(old, new_not_bumped) is True


def test_empty_texts_no_violation():
    """Two empty texts → no violation."""
    assert caf.arch_freshness_violation("", "") is False


def test_no_stamp_lines_body_changed_is_violation():
    """If neither old nor new have stamp lines but body changed → violation.

    Both stamp sequences are empty (equal), body differs → True.
    This is the correct behaviour: absence of a stamp is not a bump.
    """
    old = "# Arch\n\nOriginal text.\n"
    new = "# Arch\n\nChanged text.\n"
    assert caf.arch_freshness_violation(old, new) is True


def test_partial_stamp_bump_counts():
    """Bumping even one stamp line to a VALID date@sha counts → no violation."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nBody.\n\n*Last verified: <YYYY-MM-DD> @ <git-sha>*\n"
    new = "# Arch\n\n*Last verified: 2026-06-30 @ abc1234*\n\nBody changed.\n\n*Last verified: <YYYY-MM-DD> @ <git-sha>*\n"
    # One stamp bumped to a valid date@sha, other unchanged → no violation
    assert caf.arch_freshness_violation(old, new) is False


# ---------------------------------------------------------------------------
# False-PASS pins (F1): a junk/blank/TODO stamp "bump" must NOT satisfy the gate.
# Before the fix, any *change* to the stamp line passed; now the new stamp must
# match a real `YYYY-MM-DD @ <7-40 hex sha>` shape.
# ---------------------------------------------------------------------------

def test_body_changed_stamp_bumped_to_TODO_is_violation():
    """Bumping the stamp to `TODO` while changing the body → violation (False-PASS pin)."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nOriginal body.\n"
    new = "# Arch\n\n*Last verified: TODO*\n\nChanged body.\n"
    assert caf.arch_freshness_violation(old, new) is True


def test_body_changed_stamp_blanked_is_violation():
    """Blanking the stamp payload (`@ `) while changing the body → violation (pin)."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nOriginal body.\n"
    new = "# Arch\n\n*Last verified: @ *\n\nChanged body.\n"
    assert caf.arch_freshness_violation(old, new) is True


def test_body_changed_stamp_junk_is_violation():
    """Bumping the stamp to arbitrary junk while changing the body → violation (pin)."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nOriginal body.\n"
    new = "# Arch\n\n*Last verified: junk*\n\nChanged body.\n"
    assert caf.arch_freshness_violation(old, new) is True


def test_body_changed_real_date_at_sha_is_clean():
    """A real `YYYY-MM-DD @ <sha>` bump with a body change → no violation (must pass)."""
    old = "# Arch\n\n*Last verified: <date> @ <sha>*\n\nOriginal body.\n"
    new = "# Arch\n\n*Last verified: 2026-06-30 @ 7bfde17*\n\nChanged body.\n"
    assert caf.arch_freshness_violation(old, new) is False


def test_skeleton_placeholder_is_not_a_valid_stamp():
    """The skeleton `<date> @ <sha>` / `<YYYY-MM-DD> @ <git-sha>` placeholders do NOT
    count as a valid stamp — a body change with only a placeholder is still a violation."""
    old = "# Arch\n\n*Last verified: 2026-01-01 @ deadbee*\n\nOriginal body.\n"
    new = "# Arch\n\n*Last verified: <YYYY-MM-DD> @ <git-sha>*\n\nChanged body.\n"
    assert caf.arch_freshness_violation(old, new) is True


# ---------------------------------------------------------------------------
# Explicit-semantics label and provenance validation
# ---------------------------------------------------------------------------

def test_against_base_label_is_a_stamp_line():
    """The explicit `against base` form counts as a stamp bump."""
    new = _BODY_CHANGED.replace(
        "*Last verified: <date> @ <sha>*",
        "*Last verified against base: 2026-08-07 @ abc1234*",
    )
    assert caf.arch_freshness_violation(_BASE, new) is False


def test_new_valid_stamps_returns_only_new_valid_lines():
    stamps = caf.new_valid_stamps(_BASE, _BODY_CHANGED_STAMP_BUMPED)
    # The fixture bumps the header and footer stamps to the same value; both
    # lines are new and valid, and both get provenance-validated.
    assert stamps == ["*Last verified: 2026-06-30 @ abc1234*"] * 2
    assert caf.new_valid_stamps(_BASE, _BODY_CHANGED) == []


def test_stamp_provenance_rejects_unresolvable_sha():
    violations = caf.stamp_provenance_violations(
        ["*Last verified against base: 2026-08-07 @ abc1234*"],
        lambda sha: (False, False),
    )
    assert violations == [
        "stamp names abc1234, which does not resolve to a commit"
    ]


def test_stamp_provenance_rejects_non_ancestor_sha():
    violations = caf.stamp_provenance_violations(
        ["*Last verified against base: 2026-08-07 @ abc1234*"],
        lambda sha: (True, False),
    )
    assert len(violations) == 1
    assert "not an ancestor of HEAD" in violations[0]


def test_stamp_provenance_accepts_ancestor_commit():
    violations = caf.stamp_provenance_violations(
        ["*Last verified against base: 2026-08-07 @ abc1234*"],
        lambda sha: (True, True),
    )
    assert violations == []


def test_git_resolver_answers_for_real_repository_shas():
    """HEAD's parent is a commit and an ancestor; a fabricated SHA is neither."""
    import subprocess

    head_parent = subprocess.run(
        ["git", "rev-parse", "HEAD^"],
        cwd=str(caf.ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert caf._git_resolve_stamp(head_parent) == (True, True)
    assert caf._git_resolve_stamp("deadbeef" * 5) == (False, False)
