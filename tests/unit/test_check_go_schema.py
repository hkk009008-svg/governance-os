"""Unit tests for exact Lane V report accounting and GO evidence validation.

Hermetic: uses tmp_path fixture dirs with *-verification-report.md files; no real
mailbox required.  All assertions go through the pure `go_report_violations()` helper
(no filesystem I/O needed for the core gate logic), plus a main() integration test
against tmp_path directories for the I/O path.

Test cases mirror the brief:
  (a) well-formed GO (VERDICT: GO + `$ cmd`/`→ out` + SHA in H1) → PASS (no violations)
  (b) GO missing the `→ output` line → FAIL, missing field named
  (c) GO whose only evidence cites `wave_gate_check`, no pin output → FAIL

Additional cases cover the unchanged pure GO helper plus pre-v3 repository
validation, raw filesystem scanning, and durable baseline generation.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import pathlib
import stat
import subprocess
import sys
import time

import pytest

import check_go_schema as cgs
import verification_report_gate as report_gate


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
# Live repo smoke: exact historical baseline plus current filesystem corpus
# ---------------------------------------------------------------------------

def test_main_on_live_mailbox():
    """The live corpus contains the routed base and every reviewed baseline path."""
    reports = cgs.scan_repository_reports(cgs.ROOT)
    manifest = cgs.load_baseline_manifest(cgs.DEFAULT_MANIFEST)
    report_paths = {report.relative_path for report in reports}
    manifest_paths = {entry["path"] for entry in manifest["reports"]}
    assert len(reports) >= 38
    assert manifest_paths
    assert manifest_paths <= report_paths
    assert cgs.repository_report_violations(cgs.ROOT, reports, manifest) == []
    import sys

    old_argv = sys.argv
    try:
        sys.argv = ["check_go_schema.py"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cgs.main()
    finally:
        sys.argv = old_argv
    assert rc == 0, f"Expected exit 0 on baseline-backed mailbox; got {rc}.\n{buf.getvalue()}"


# ---------------------------------------------------------------------------
# Repository-wide pre-v3/v3 report accounting
# ---------------------------------------------------------------------------

_BASELINE_SCHEMA = "lane-v-report-pre-v3-baseline/v1"
_REPOSITORY_REPORT = (
    "coordination/mailbox/sent/"
    "2026-07-13T06-00-00Z-operator-to-all-verification-report.md"
)


def _manifest(*entries: tuple[str, str]) -> dict[str, object]:
    return {
        "schema_version": _BASELINE_SCHEMA,
        "reports": [
            {"path": path, "sha256": digest}
            for path, digest in sorted(entries)
        ],
    }


def _git(root: pathlib.Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _shipping_v3_fixture(
    root: pathlib.Path,
) -> tuple[str, bytes, dict[str, object]]:
    root.mkdir()
    (root / "requirements").mkdir()
    (root / "requirements" / "task.md").write_text(
        "Review the report gate.\n", encoding="utf-8"
    )
    (root / "scripts").mkdir()
    for relative in report_gate.PIPELINE_MARKER_PATHS:
        marker = root / relative
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(f"synthetic Pipeline marker: {relative}\n", encoding="utf-8")
    feature = root / "scripts" / "feature.py"
    feature.write_text("VALUE = 'base'\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Repository Report Fixture")
    _git(root, "config", "user.email", "repository-report@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")

    task_id = "11111111-2222-4333-8444-555555555555"
    descriptor_path = f"coordination/verification/scopes/{task_id}.json"
    descriptor = {
        "schema_version": "lane-v-scope/v1",
        "task_id": task_id,
        "question_id": "repository-report-fixture",
        "trigger_kind": "shipping-commit",
        "verification_mode": "independent-lane-v",
        "verification_harness": "lane-v:independent-verifier",
        "review_profile": "independent-lane-v",
        "reviewed_base": {"policy": "exact", "commit": base},
        "requirement_paths": ["requirements/task.md"],
        "allowed_path_roots": ["coordination/verification/scopes", "scripts"],
        "verification_commands": [
            "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"
        ],
    }
    descriptor_file = root / descriptor_path
    descriptor_file.parent.mkdir(parents=True)
    descriptor_raw = (json.dumps(descriptor, indent=2) + "\n").encode()
    descriptor_file.write_bytes(descriptor_raw)
    descriptor_digest = "sha256:" + hashlib.sha256(descriptor_raw).hexdigest()
    scope = f"{descriptor_path}@{descriptor_digest}"
    _git(root, "add", descriptor_path)
    _git(root, "commit", "-q", "-m", "docs: bind report authority")

    feature.write_text("VALUE = 'reviewed'\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    _git(
        root,
        "commit",
        "-q",
        "-m",
        "feat: reviewed report gate",
        "-m",
        f"Lane-V-Scope: {scope}",
    )
    head = _git(root, "rev-parse", "HEAD")
    fields = [
        ("Verification schema", "lane-v-report/v3"),
        ("Verification mode", "independent-lane-v"),
        ("Verification harness", "lane-v:independent-verifier"),
        ("Verification task ID", task_id),
        ("Scope authority", scope),
        ("Trigger identity", f"shipping-commit:{head}"),
        ("Reviewed head", head),
        ("Reviewed base", base),
        ("Review profile", "independent-lane-v"),
        ("Reviewer identity", "operator"),
    ]
    raw = (
        f"# Operator → All: Lane V verification report — commit `{head}`\n\n"
        "**When:** 2026-07-13T06:00:00Z · **From:** operator (online)\n\n"
        "VERDICT: GO\n\n"
        "## Evidence\n"
        "$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py\n"
        "→ OK\n\n"
        "## Verification Attestation\n\n"
        + "\n".join(f"{label}: {value}" for label, value in fields)
        + "\n"
    ).encode()
    return _REPOSITORY_REPORT, raw, _manifest((_REPOSITORY_REPORT, "0" * 64))


def test_repository_reports_accept_exact_legacy_path_and_raw_digest(
    tmp_path: pathlib.Path,
) -> None:
    raw = b"# historical report\n\nVERDICT: FAIL\n"
    manifest = _manifest((_REPOSITORY_REPORT, hashlib.sha256(raw).hexdigest()))

    violations = cgs.repository_report_violations(
        tmp_path,
        [cgs.RawReport(_REPOSITORY_REPORT, raw)],
        manifest,
    )

    assert violations == []


def test_pre_v3_report_requires_exact_manifest_path_and_digest(
    tmp_path: pathlib.Path,
) -> None:
    raw = b"# historical\n\nVERDICT: FAIL\n"
    path = _REPOSITORY_REPORT
    manifest = _manifest((path, hashlib.sha256(raw).hexdigest()))

    assert cgs.repository_report_violations(
        tmp_path, [cgs.RawReport(path, raw)], manifest
    ) == []
    assert cgs.repository_report_violations(
        tmp_path, [cgs.RawReport(path, raw + b"changed\n")], manifest
    )
    copied = path.replace("06-00-00", "06-00-01")
    assert cgs.repository_report_violations(
        tmp_path, [cgs.RawReport(copied, raw)], manifest
    )


def test_unlisted_pre_v3_report_fails_while_unlisted_v3_is_live_validated(
    tmp_path: pathlib.Path,
) -> None:
    legacy = b"# historical\n\nVERDICT: FAIL\n"
    legacy_path = _REPOSITORY_REPORT.replace("06-00-00", "06-00-01")
    assert cgs.repository_report_violations(
        tmp_path,
        [cgs.RawReport(legacy_path, legacy)],
        _manifest(),
    )

    path, raw, _ = _shipping_v3_fixture(tmp_path / "repo")
    assert b"Verification schema: lane-v-report/v3" in raw
    assert cgs.repository_report_violations(
        tmp_path / "repo",
        [cgs.RawReport(path, raw)],
        _manifest(),
    ) == []


def test_repository_reports_detect_changed_deleted_and_new_non_v3_history(
    tmp_path: pathlib.Path,
) -> None:
    legacy = b"# historical report\n\nVERDICT: FAIL\n"
    manifest = _manifest(
        (_REPOSITORY_REPORT, hashlib.sha256(legacy).hexdigest())
    )
    changed = cgs.repository_report_violations(
        tmp_path,
        [cgs.RawReport(_REPOSITORY_REPORT, legacy + b"changed\n")],
        manifest,
    )
    deleted = cgs.repository_report_violations(tmp_path, [], manifest)
    new_path = _REPOSITORY_REPORT.replace("06-00-00", "06-00-01")
    new = cgs.repository_report_violations(
        tmp_path,
        [cgs.RawReport(new_path, legacy)],
        _manifest(),
    )

    assert any("baseline drift" in item for item in changed)
    assert deleted == [f"{_REPOSITORY_REPORT}: missing historical baseline report"]
    assert any("lane-v-report/v3" in item for item in new)


def test_repository_reports_strictly_reject_invalid_utf8(tmp_path: pathlib.Path) -> None:
    path = _REPOSITORY_REPORT.replace("06-00-00", "06-00-02")

    violations = cgs.repository_report_violations(
        tmp_path,
        [cgs.RawReport(path, b"VERDICT: FAIL\n\xff")],
        _manifest(),
    )

    assert violations == [f"{path}: report must be strict UTF-8"]


def test_manifest_listed_report_rejects_valid_v3_replacement_as_baseline_drift(
    tmp_path: pathlib.Path,
) -> None:
    path, raw, manifest = _shipping_v3_fixture(tmp_path / "repo")

    violations = cgs.repository_report_violations(
        tmp_path / "repo",
        [cgs.RawReport(path, raw)],
        manifest,
    )

    assert violations == [f"{path}: baseline drift; raw digest does not match manifest"]


def test_repository_scan_never_reads_private_receipts(
    tmp_path: pathlib.Path,
) -> None:
    path, raw, _ = _shipping_v3_fixture(tmp_path / "repo")
    private_runtime = tmp_path / "repo" / ".codex" / "runtime"
    private_runtime.mkdir(parents=True)
    private_runtime.chmod(0)
    try:
        violations = cgs.repository_report_violations(
            tmp_path / "repo",
            [cgs.RawReport(path, raw)],
            _manifest(),
        )
    finally:
        private_runtime.chmod(0o700)

    assert violations == []


def _baseline_repo(root: pathlib.Path) -> tuple[str, str]:
    root.mkdir()
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    first = (
        "coordination/mailbox/sent/"
        "2026-07-13T06-10-00Z-operator-to-all-verification-report.md"
    )
    second = (
        "coordination/mailbox/sent/"
        "2026-07-13T06-11-00Z-operator2-to-all-verification-report.md"
    )
    (root / first).write_bytes(b"# first historical report\n\nVERDICT: FAIL\n")
    (root / second).write_bytes(b"# second historical report\n\nVERDICT: NITS\n")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Baseline Fixture")
    _git(root, "config", "user.email", "baseline@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: historical reports")
    return first, second


def _git_blob(root: pathlib.Path, path: str) -> bytes:
    return subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", "show", f"HEAD:{path}"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout


def _wait_for_file(path: pathlib.Path, *, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.01)
    pytest.fail(f"timed out waiting for {path}")


def _baseline_worker_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    scripts = str(cgs.ROOT / "scripts")
    inherited = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        scripts if not inherited else scripts + os.pathsep + inherited
    )
    return environment




@pytest.mark.parametrize(
    "unsafe_kind", ["symlink", "directory", "mode", "hardlink"]
)
def test_baseline_generation_rejects_unsafe_stable_lock_metadata(
    tmp_path: pathlib.Path, unsafe_kind: str
) -> None:
    root = tmp_path / "repo"
    _baseline_repo(root)
    common_text = _git(root, "rev-parse", "--git-common-dir")
    common = pathlib.Path(common_text)
    if not common.is_absolute():
        common = root / common
    lock = common.resolve() / "lane-v-reports-pre-v3-baseline.lock"
    if unsafe_kind == "symlink":
        target_file = common.resolve() / "attacker-lock-target"
        target_file.write_bytes(b"")
        target_file.chmod(0o600)
        lock.symlink_to(target_file)
    elif unsafe_kind == "directory":
        lock.mkdir()
    else:
        lock.write_bytes(b"")
        lock.chmod(0o600 if unsafe_kind == "hardlink" else 0o644)
        if unsafe_kind == "hardlink":
            os.link(lock, common.resolve() / "attacker-lock-alias")
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    with pytest.raises(cgs.BaselineGenerationError, match="unsafe baseline generation lock"):
        cgs.generate_baseline(root, target)


def test_filesystem_scan_reads_tracked_and_untracked_reports_once(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, second = _baseline_repo(root)
    untracked = (
        "coordination/mailbox/sent/"
        "2026-07-13T06-12-00Z-operator-to-all-verification-report.md"
    )
    (root / untracked).write_bytes(b"# untracked report\n\nVERDICT: FAIL\n")
    original_read = cgs.os.read
    reads: list[int] = []

    def counted(descriptor: int, count: int) -> bytes:
        if stat.S_ISREG(os.fstat(descriptor).st_mode):
            reads.append(descriptor)
        return original_read(descriptor, count)

    monkeypatch.setattr(cgs.os, "read", counted)

    reports = cgs.scan_repository_reports(root)

    assert [item.relative_path for item in reports] == sorted(
        [first, second, untracked]
    )
    assert len(reads) == 3


def test_filesystem_scan_surfaces_read_errors(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, _ = _baseline_repo(root)
    original_open = cgs.os.open
    denied_name = pathlib.PurePosixPath(first).name

    def denied(
        path: os.PathLike[str] | str,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if dir_fd is not None and os.fspath(path) == denied_name:
            raise PermissionError("report read denied")
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(cgs.os, "open", denied)

    with pytest.raises(PermissionError, match="report read denied"):
        cgs.scan_repository_reports(root)


def test_filesystem_scan_rejects_symlink_swap_at_open(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, _ = _baseline_repo(root)
    victim = root / first
    attacker = root / "attacker-report.md"
    attacker.write_bytes(b"# attacker\n\nVERDICT: FAIL\n")
    victim_name = victim.name
    original_open = cgs.os.open
    swapped = False

    def swap_before_open(
        path: os.PathLike[str] | str,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal swapped
        if not swapped and dir_fd is not None and os.fspath(path) == victim_name:
            swapped = True
            victim.unlink()
            victim.symlink_to(attacker)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(cgs.os, "open", swap_before_open)

    with pytest.raises(OSError):
        cgs.scan_repository_reports(root)

    assert swapped


@pytest.mark.parametrize(
    ("component", "outside_tail"),
    [
        ("coordination", ("mailbox", "sent")),
        ("mailbox", ("sent",)),
        ("sent", ()),
    ],
)
def test_filesystem_scan_rejects_symlink_in_canonical_directory_component(
    tmp_path: pathlib.Path,
    component: str,
    outside_tail: tuple[str, ...],
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    canonical_components = ("coordination", "mailbox", "sent")
    component_index = canonical_components.index(component)
    canonical_parent = root.joinpath(*canonical_components[:component_index])
    canonical_parent.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / f"outside-{component}"
    outside.mkdir()
    outside_sent = outside.joinpath(*outside_tail)
    outside_sent.mkdir(parents=True, exist_ok=True)
    canonical_parent.joinpath(component).symlink_to(
        outside,
        target_is_directory=True,
    )
    outside_raw = b"# outside report\n\nVERDICT: FAIL\n"
    outside_sent.joinpath(
        "2026-07-15T00-00-00Z-attacker-to-all-verification-report.md"
    ).write_bytes(outside_raw)
    explicit_directory = root / "coordination" / "mailbox" / "sent"

    for directory in (None, explicit_directory):
        try:
            reports = cgs.scan_repository_reports(root, directory)
        except OSError:
            continue
        assert outside_raw not in {report.raw for report in reports}, (
            f"outside bytes accepted through symlinked {component} component"
        )
        pytest.fail(f"symlinked {component} component was not rejected")


@pytest.mark.parametrize("unsafe_kind", ["symlink", "fifo"])
def test_filesystem_scan_rejects_symlink_and_special_file(
    tmp_path: pathlib.Path, unsafe_kind: str
) -> None:
    root = tmp_path / "repo"
    first, _ = _baseline_repo(root)
    victim = root / first
    victim.unlink()
    if unsafe_kind == "symlink":
        attacker = root / "attacker-report.md"
        attacker.write_bytes(b"# attacker\n\nVERDICT: FAIL\n")
        victim.symlink_to(attacker)
    else:
        os.mkfifo(victim)

    with pytest.raises(OSError):
        cgs.scan_repository_reports(root)


def test_initial_baseline_uses_only_sorted_tracked_head_raw_blobs(
    tmp_path: pathlib.Path,
) -> None:
    root = tmp_path / "repo"
    first, second = _baseline_repo(root)
    untracked = (
        "coordination/mailbox/sent/"
        "2026-07-13T06-12-00Z-operator-to-all-verification-report.md"
    )
    (root / untracked).write_bytes(b"# untracked report\n\nVERDICT: FAIL\n")
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    manifest = cgs.generate_baseline(root, target)

    assert [entry["path"] for entry in manifest["reports"]] == [first, second]
    assert [entry["sha256"] for entry in manifest["reports"]] == [
        hashlib.sha256(_git_blob(root, first)).hexdigest(),
        hashlib.sha256(_git_blob(root, second)).hexdigest(),
    ]
    assert json.loads(target.read_text(encoding="utf-8")) == manifest


def test_baseline_pins_one_head_when_symbolic_head_moves_after_enumeration(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, _ = _baseline_repo(root)
    original_head = _git(root, "rev-parse", "HEAD")
    original_raw = (root / first).read_bytes()
    original_baseline_git = cgs._baseline_git
    moved = False

    def move_head_after_ls_tree(
        git_root: pathlib.Path, *args: str
    ) -> bytes:
        nonlocal moved
        result = original_baseline_git(git_root, *args)
        if not moved and "ls-tree" in args:
            moved = True
            (root / first).write_bytes(
                b"# moved HEAD report\n\nVERDICT: FAIL\n"
            )
            _git(root, "add", first)
            _git(root, "commit", "-q", "-m", "test: move symbolic HEAD")
        return result

    monkeypatch.setattr(cgs, "_baseline_git", move_head_after_ls_tree)
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    manifest = cgs.generate_baseline(root, target)

    assert moved
    assert _git(root, "rev-parse", "HEAD") != original_head
    digest_by_path = {
        entry["path"]: entry["sha256"] for entry in manifest["reports"]
    }
    assert digest_by_path[first] == hashlib.sha256(original_raw).hexdigest()


def test_baseline_git_ignores_inherited_git_selectors(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, second = _baseline_repo(root)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "attacker.git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path / "attacker-worktree"))
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(tmp_path / "attacker-objects"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "attacker-index"))
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    manifest = cgs.generate_baseline(root, target)

    assert [entry["path"] for entry in manifest["reports"]] == [first, second]


def test_baseline_git_uses_literal_system_binary_under_hostile_path(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, second = _baseline_repo(root)
    shim_directory = tmp_path / "hostile-bin"
    shim_directory.mkdir()
    marker = tmp_path / "hostile-git-invoked"
    shim = shim_directory / "git"
    shim.write_text(
        "#!/bin/sh\n"
        "printf 'invoked\\n' >> \"$BASELINE_GIT_SHIM_MARKER\"\n"
        "exec /usr/bin/git \"$@\"\n",
        encoding="utf-8",
    )
    shim.chmod(0o755)
    monkeypatch.setenv("BASELINE_GIT_SHIM_MARKER", str(marker))
    monkeypatch.setenv("PATH", str(shim_directory))
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    manifest = cgs.generate_baseline(root, target)

    assert [entry["path"] for entry in manifest["reports"]] == [first, second]
    assert json.loads(target.read_text(encoding="utf-8")) == manifest
    assert not marker.exists(), "PATH-selected git shim handled baseline reads"


def test_baseline_git_uses_literal_system_binary_when_path_has_no_git(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    first, second = _baseline_repo(root)
    no_git_directory = tmp_path / "no-git-bin"
    no_git_directory.mkdir()
    monkeypatch.setenv("PATH", str(no_git_directory))
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    manifest = cgs.generate_baseline(root, target)

    assert [entry["path"] for entry in manifest["reports"]] == [first, second]
    assert json.loads(target.read_text(encoding="utf-8")) == manifest


def test_baseline_git_ignores_replace_refs(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "repo"
    first, _ = _baseline_repo(root)
    original_head = _git(root, "rev-parse", "HEAD")
    original_raw = (root / first).read_bytes()
    (root / first).write_bytes(b"# replacement object\n\nVERDICT: FAIL\n")
    _git(root, "add", first)
    attacker_tree = _git(root, "write-tree")
    attacker = subprocess.run(
        ["git", "commit-tree", attacker_tree],
        cwd=root,
        input="chore: attacker replacement\n",
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _git(root, "reset", "-q", "--hard", original_head)
    _git(root, "replace", original_head, attacker)
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"

    manifest = cgs.generate_baseline(root, target)

    digest_by_path = {
        entry["path"]: entry["sha256"] for entry in manifest["reports"]
    }
    assert digest_by_path[first] == hashlib.sha256(original_raw).hexdigest()


def test_initial_baseline_publication_is_atomic_no_clobber(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    _baseline_repo(root)
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"
    original_link = os.link

    def competing_link(source: object, destination: object) -> None:
        pathlib.Path(destination).write_bytes(b"concurrent winner\n")
        original_link(source, destination)

    monkeypatch.setattr(os, "link", competing_link)

    with pytest.raises(cgs.BaselineGenerationError, match="already exists"):
        cgs.generate_baseline(root, target)

    assert target.read_bytes() == b"concurrent winner\n"


def test_existing_baseline_is_unchanged_on_initial_generation_failure(
    tmp_path: pathlib.Path,
) -> None:
    root = tmp_path / "repo"
    _baseline_repo(root)
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"
    cgs.generate_baseline(root, target)
    before = target.read_bytes()

    with pytest.raises(cgs.BaselineGenerationError, match="already exists"):
        cgs.generate_baseline(root, target)

    assert target.read_bytes() == before


def test_pre_v3_cutover_manifest_is_one_shot_for_api_and_cli(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    first, _ = _baseline_repo(root)
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"
    cgs.generate_baseline(root, target)
    frozen = target.read_bytes()

    (root / first).write_bytes(b"# changed historical report\n\nVERDICT: FAIL\n")
    _git(root, "add", first)
    _git(root, "commit", "-q", "-m", "docs: mutate frozen history")

    with pytest.raises(cgs.BaselineGenerationError, match="frozen|one-shot"):
        cgs.generate_baseline(root, target, replace=True)
    assert target.read_bytes() == frozen

    monkeypatch.setattr(cgs, "ROOT", root)
    assert cgs.main(
        [
            "--generate-baseline",
            "scripts/baselines/lane_v_reports_pre_v3.json",
            "--replace-baseline",
        ]
    ) == 1
    assert target.read_bytes() == frozen

    manifest = cgs.load_baseline_manifest(target)
    violations = cgs.repository_report_violations(
        root, cgs.scan_repository_reports(root), manifest
    )
    assert any(first in item and "baseline drift" in item for item in violations)




def test_untracked_report_is_not_grandfathered_by_generation(
    tmp_path: pathlib.Path,
) -> None:
    root = tmp_path / "repo"
    _baseline_repo(root)
    target = root / "scripts" / "baselines" / "lane_v_reports_pre_v3.json"
    manifest = cgs.generate_baseline(root, target)
    untracked = (
        "coordination/mailbox/sent/"
        "2026-07-13T06-14-00Z-operator-to-all-verification-report.md"
    )
    (root / untracked).write_bytes(b"# untracked report\n\nVERDICT: FAIL\n")

    violations = cgs.repository_report_violations(
        root,
        cgs.scan_repository_reports(root),
        manifest,
    )

    assert any(untracked in violation and "lane-v-report/v3" in violation for violation in violations)


def test_cli_and_smoke_call_the_same_public_repository_validator() -> None:
    smoke_source = (cgs.ROOT / "scripts" / "ci_smoke.py").read_text(encoding="utf-8")
    checker_source = (cgs.ROOT / "scripts" / "check_go_schema.py").read_text(
        encoding="utf-8"
    )

    assert "_cgs.repository_report_violations(" in smoke_source
    assert "violations = repository_report_violations(" in checker_source
    assert "_cgs._scan_dir" not in smoke_source
    assert "_cgs.go_report_violations" not in smoke_source
