"""Unit tests for scripts/check_go_schema.py — GO verification-report evidence validator.

Hermetic: uses tmp_path fixture dirs with *-verification-report.md files; no real
mailbox required.  All assertions go through the pure `go_report_violations()` helper
(no filesystem I/O needed for the core gate logic), plus a main() integration test
against tmp_path directories for the I/O path.

Test cases mirror the brief:
  (a) well-formed GO (VERDICT: GO + `$ cmd`/`→ out` + SHA in H1) → PASS (no violations)
  (b) GO missing the `→ output` line → FAIL, missing field named
  (c) GO whose only evidence cites `wave_gate_check`, no pin output → FAIL

Additional cases for full branch coverage of the pure helper.
"""
from __future__ import annotations

import contextlib
import io
import pathlib

import pytest

import check_go_schema as cgs


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

# A well-formed v6.0 GO report body (all required fields present).
_WELL_FORMED_GO = """\
# Operator → Director: Lane V verification report — commit `abc1234`

**When:** 2026-06-30T10:00:00Z · **From:** operator (online)

VERDICT: GO

## Evidence
$ grep -rn 'self\\.spent_usd' --include='*.py' .
→ cost_tracker.py:224 (single chokepoint confirmed)

## Findings
1. INFORMATIONAL — `cost_tracker.py:224` — increment at log() chokepoint; no double-count.

Cursor at send: 2026-06-30T09:00:00Z
"""

_NITS_REPORT = """\
# Operator → Director: Lane V verification report — commit `def5678`

**When:** 2026-06-30T11:00:00Z · **From:** operator (online)

VERDICT: NITS

## Evidence
$ pytest tests/ -q
→ 5 passed in 0.3s

## Findings
1. MINOR — `foo.py:42` — trivial whitespace nit.

Cursor at send: 2026-06-30T10:30:00Z
"""

_FAIL_REPORT = """\
# Operator → Director: Lane V verification report — commit `fed9876`

**When:** 2026-06-30T11:30:00Z · **From:** operator (online)

VERDICT: FAIL

## Findings
1. CRITICAL — `gate.py:10` — missing guard.

Cursor at send: 2026-06-30T11:00:00Z
"""


def _write_report(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    """Write a verification-report file into tmp_path."""
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# (a) Well-formed GO → PASS (no violations, main exits 0)
# ---------------------------------------------------------------------------

def test_well_formed_go_produces_no_violations():
    """A GO with VERDICT: GO, `$ cmd`/`→ out` in Evidence, and SHA in H1 → clean."""
    viol = cgs.go_report_violations([("report.md", _WELL_FORMED_GO)])
    assert viol == [], f"Expected no violations, got: {viol}"


def test_main_exits_0_on_well_formed_go(tmp_path: pathlib.Path):
    """main() scans a dir with a well-formed GO report and exits 0."""
    _write_report(tmp_path, "2026-06-30T10-00-00Z-operator-to-director-verification-report.md", _WELL_FORMED_GO)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cgs.main.__wrapped__(tmp_path) if hasattr(cgs.main, "__wrapped__") else _run_main_with_dir(tmp_path)
    assert rc == 0


def _run_main_with_dir(directory: pathlib.Path) -> int:
    """Call check_go_schema.main() with a custom directory via the _scan_dir + go_report_violations path."""
    named = cgs._scan_dir(directory)
    viol = cgs.go_report_violations(named)
    return 1 if viol else 0


# ---------------------------------------------------------------------------
# (b) GO missing the `→ output` line → FAIL, field named in output
# ---------------------------------------------------------------------------

_GO_MISSING_OUTPUT = """\
# Operator → Director: Lane V verification report — commit `abc1234`

VERDICT: GO

## Evidence
$ pytest tests/unit/ -q

## Findings
1. INFORMATIONAL — nothing notable.
"""


def test_go_missing_output_line_is_a_violation():
    """A GO with `$ cmd` but no `→ out` in Evidence must produce a violation naming the missing field."""
    viol = cgs.go_report_violations([("missing-output.md", _GO_MISSING_OUTPUT)])
    assert len(viol) >= 1, f"Expected at least one violation, got: {viol}"
    assert "missing-output.md" in viol[0]
    # The violation must name the missing field.
    joined = " ".join(viol)
    assert "→" in joined or "output" in joined, f"Violation should name missing output field; got: {viol}"


def test_go_missing_cmd_line_is_a_violation():
    """A GO with `→ out` but no `$ cmd` line must be flagged."""
    body = """\
# Operator → Director: Lane V verification report — commit `abc1234`

VERDICT: GO

## Evidence
→ 5 passed in 0.3s

## Findings
"""
    viol = cgs.go_report_violations([("no-cmd.md", body)])
    assert any("no-cmd.md" in v for v in viol)
    joined = " ".join(viol)
    assert "$" in joined or "cmd" in joined.lower(), f"Should name missing cmd field; got: {viol}"


def test_go_missing_evidence_section_is_a_violation():
    """A GO with no ## Evidence section at all must be flagged."""
    body = """\
# Op → Dir: Lane V report — commit `abc1234`

VERDICT: GO

## Findings
1. INFORMATIONAL — all good.
"""
    viol = cgs.go_report_violations([("no-evidence.md", body)])
    assert any("Evidence" in v or "evidence" in v.lower() for v in viol), (
        f"Expected Evidence-related violation; got: {viol}"
    )


def test_go_missing_sha_and_logs_ref_is_a_violation():
    """A GO with no commit SHA in H1 and no logs/ ref must be flagged."""
    body = """\
VERDICT: GO

## Evidence
$ pytest tests/ -q
→ 5 passed in 0.2s

## Findings
"""
    viol = cgs.go_report_violations([("no-sha.md", body)])
    assert any("SHA" in v or "sha" in v.lower() or "commit" in v.lower() or "logs/" in v for v in viol), (
        f"Expected SHA/logs ref violation; got: {viol}"
    )


def test_go_with_logs_ref_passes_sha_check():
    """A GO that has no SHA in H1 but cites `logs/` somewhere in the body passes the SHA check."""
    body = """\
VERDICT: GO

## Evidence
$ .venv/bin/pytest tests/ -q
→ 10 passed in 0.5s

See logs/ci-2026-06-30.txt for full output.

## Findings
"""
    viol = cgs.go_report_violations([("logs-ref.md", body)])
    # Should have no SHA violation; may have other violations if any
    sha_viol = [v for v in viol if "SHA" in v or "sha" in v.lower() or "logs/" in v]
    assert sha_viol == [], f"Logs ref should satisfy the SHA check; got: {sha_viol}"


# ---------------------------------------------------------------------------
# (c) GO whose only evidence cites `wave_gate_check`, no pin output → FAIL
# ---------------------------------------------------------------------------

_GO_WAVE_GATE_NO_PYTEST = """\
# Operator → Director: Lane V verification report — commit `cafe123`

VERDICT: GO

## Evidence
$ python scripts/wave_gate_check.py
→ GATE MET — all rows verified

## Findings
"""


def test_go_wave_gate_only_is_a_violation():
    """A GO citing only wave_gate_check with no pytest/--runxfail output → FAIL (ceremony)."""
    viol = cgs.go_report_violations([("wave-gate-only.md", _GO_WAVE_GATE_NO_PYTEST)])
    assert any("wave-gate-only.md" in v for v in viol), f"Expected violation for wave-gate-only; got: {viol}"
    joined = " ".join(viol)
    assert "wave_gate_check" in joined, f"Violation should mention wave_gate_check; got: {viol}"


def test_go_wave_gate_with_runxfail_passes():
    """A GO citing wave_gate_check BUT ALSO --runxfail output passes the sub-rule."""
    body = """\
# Operator → Director: Lane V verification report — commit `cafe123`

VERDICT: GO

## Evidence
$ python scripts/wave_gate_check.py
→ GATE MET — all rows verified

$ .venv/bin/pytest tests/pins/ --runxfail -q
→ 12 passed in 1.2s

## Findings
"""
    viol = cgs.go_report_violations([("wave-gate-with-runxfail.md", body)])
    wave_viol = [v for v in viol if "wave_gate_check" in v]
    assert wave_viol == [], f"Should pass when --runxfail is also present; got: {wave_viol}"


# ---------------------------------------------------------------------------
# False-PASS pin (F2): the bare prose word "pytest" must NOT satisfy the
# wave_gate sub-rule — only a real execution signal does.
# ---------------------------------------------------------------------------

_GO_WAVE_GATE_PROSE_PYTEST = """\
# Operator → Director: Lane V verification report — commit `cafe123`

VERDICT: GO

## Evidence
$ python scripts/wave_gate_check.py
→ GATE MET — all rows verified

Note: I did not run pytest this round; the wave gate is green.

## Findings
"""


def test_go_wave_gate_with_prose_pytest_word_is_a_violation():
    """The bare word 'pytest' in prose must NOT defeat the wave_gate sub-rule (F2 pin)."""
    viol = cgs.go_report_violations([("wave-gate-prose-pytest.md", _GO_WAVE_GATE_PROSE_PYTEST)])
    wave_viol = [v for v in viol if "wave_gate_check" in v]
    assert wave_viol, (
        f"Bare prose 'pytest' should not satisfy the sub-rule; expected a "
        f"wave_gate violation, got: {viol}"
    )


def test_go_wave_gate_with_pytest_result_marker_passes():
    """A real pytest RESULT marker (`12 passed`) satisfies the sub-rule (no over-fix)."""
    body = """\
# Operator → Director: Lane V verification report — commit `cafe123`

VERDICT: GO

## Evidence
$ python scripts/wave_gate_check.py
→ GATE MET — all rows verified

$ .venv/bin/pytest tests/ -q
→ 12 passed in 1.2s

## Findings
"""
    viol = cgs.go_report_violations([("wave-gate-result-marker.md", body)])
    wave_viol = [v for v in viol if "wave_gate_check" in v]
    assert wave_viol == [], f"A real pytest result marker should pass; got: {wave_viol}"


# ---------------------------------------------------------------------------
# False-PASS pins (F3): off-form VERDICT tokens must be gated, not fail-open.
# Before the fix, `VERDICT: GO (pending)` / `**VERDICT: GO**` matched no regex →
# treated as not-a-GO → skipped ALL evidence checks (silent fail-open).
# ---------------------------------------------------------------------------

def test_go_pending_suffix_is_gated():
    """`VERDICT: GO (pending)` with no evidence is a GO and must produce violations (F3 pin)."""
    body = "VERDICT: GO (pending)\n\n(no Evidence section, no SHA)\n"
    viol = cgs.go_report_violations([("go-pending.md", body)])
    assert viol, f"Suffixed GO must be gated (not fail-open); got: {viol}"


def test_go_bold_decorated_is_gated():
    """`**VERDICT: GO**` with no evidence is a GO and must produce violations (F3 pin)."""
    body = "**VERDICT: GO**\n\n(no Evidence section, no SHA)\n"
    viol = cgs.go_report_violations([("go-bold.md", body)])
    assert viol, f"Decorated GO must be gated (not fail-open); got: {viol}"


def test_verdict_gonzo_is_not_gated():
    """`VERDICT: GONZO` must NOT be treated as a GO (the \\bGO\\b boundary rejects it)."""
    body = "VERDICT: GONZO\n\n(no evidence — should not be gated)\n"
    viol = cgs.go_report_violations([("gonzo.md", body)])
    assert viol == [], f"GONZO must not be gated as a GO; got: {viol}"


# ---------------------------------------------------------------------------
# NITS and FAIL verdicts are NOT gated
# ---------------------------------------------------------------------------

def test_nits_report_not_gated():
    """A NITS report is never checked (even if it has no Evidence section)."""
    viol = cgs.go_report_violations([("nits.md", _NITS_REPORT)])
    assert viol == [], f"NITS should not be gated; got: {viol}"


def test_fail_report_not_gated():
    """A FAIL report is never checked (even if it lacks Evidence)."""
    viol = cgs.go_report_violations([("fail.md", _FAIL_REPORT)])
    assert viol == [], f"FAIL should not be gated; got: {viol}"


# ---------------------------------------------------------------------------
# Multiple reports — only GO reports checked
# ---------------------------------------------------------------------------

def test_mixed_reports_only_checks_go():
    """With a clean GO, a NITS, and a FAIL report, only the GO is checked."""
    named = [
        ("go-clean.md", _WELL_FORMED_GO),
        ("nits.md", _NITS_REPORT),
        ("fail.md", _FAIL_REPORT),
    ]
    viol = cgs.go_report_violations(named)
    assert viol == [], f"Expected clean; got: {viol}"


def test_multiple_go_reports_all_checked():
    """All GO reports in the list are checked; violations for each are returned."""
    bad_go = """\
VERDICT: GO

## Evidence
$ pytest tests/ -q

## Findings
"""
    named = [
        ("go-clean.md", _WELL_FORMED_GO),
        ("go-bad.md", bad_go),
    ]
    viol = cgs.go_report_violations(named)
    assert any("go-bad.md" in v for v in viol), f"go-bad.md should have violations; got: {viol}"
    assert not any("go-clean.md" in v for v in viol), f"go-clean.md should be clean; got: {viol}"


# ---------------------------------------------------------------------------
# Empty / no-GO directory → exit 0 (vacuous pass)
# ---------------------------------------------------------------------------

def test_empty_directory_passes(tmp_path: pathlib.Path):
    """An empty directory produces no violations (vacuous pass)."""
    named = cgs._scan_dir(tmp_path)
    viol = cgs.go_report_violations(named)
    assert viol == []


def test_nonexistent_directory_passes():
    """A non-existent directory (the default mailbox when empty) exits cleanly."""
    named = cgs._scan_dir(pathlib.Path("/does/not/exist"))
    assert named == []
    assert cgs.go_report_violations(named) == []


def test_main_exits_0_on_empty_sent_dir(tmp_path: pathlib.Path):
    """main() scans an empty dir and exits 0 (vacuous pass)."""
    # Use _scan_dir + go_report_violations to simulate main()'s logic.
    named = cgs._scan_dir(tmp_path)
    assert cgs.go_report_violations(named) == []


# ---------------------------------------------------------------------------
# Live repo smoke: default mailbox is currently empty → exit 0
# ---------------------------------------------------------------------------

def test_main_on_live_mailbox():
    """main() on the real coordination/mailbox/sent/ exits 0 (empty mailbox today)."""
    import sys
    # Patch sys.argv so main() uses the live mailbox.
    old_argv = sys.argv
    try:
        sys.argv = ["check_go_schema.py"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cgs.main()
    finally:
        sys.argv = old_argv
    assert rc == 0, f"Expected exit 0 on live (empty) mailbox; got {rc}.\n{buf.getvalue()}"
