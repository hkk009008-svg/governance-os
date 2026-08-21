"""Tests for the regression-pin reconcile gate (pipeline/pin_reconciler.py).

Pins the two seams that feed pin-discipline decisions:

- ``_has_xfail_signal(result)`` regex-scans the runner result's stdout+stderr
  for pytest xfail/xpass vocabulary (XFAIL / XPASS / xfailed / xpassed).
- ``reconcile_report(inventory, wave=, runner=)`` audits *verified* inventory
  rows by re-running their pin selectors normally (no --runxfail) through an
  injectable ``runner`` callable: a still-xfailing selector means the pin was
  never reconciled after verification and is flagged as an issue; a clean
  normal pass is the healthy end-state.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import pin_reconciler


# ---------------------------------------------------------------- fixtures

_HEADER = (
    "| id | subsystem | file:line | severity | priority | fail-mode | repro |"
    " xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |"
)
_SEPARATOR = "|" + "----|" * 14


def _row(
    row_id: str,
    *,
    pin: str,
    wave: str = "2",
    status: str = "verified",
) -> str:
    cells = (row_id, "kernel", "pipeline/x.py:1", "MAJOR", "P1", "crash",
             "run it", pin, "lane-a", "none", wave, status, "operator", "-")
    return "| " + " | ".join(cells) + " |"


def _inventory(tmp_path: Path, *rows: str) -> Path:
    path = tmp_path / "inventory.md"
    path.write_text("\n".join(["# Inventory", "", _HEADER, _SEPARATOR, *rows]) + "\n")
    return path


def _stub_runner(exit_code: int = 0, stdout: str = "1 passed in 0.01s", stderr: str = ""):
    """Fake Runner: records selector lists, returns a canned pytest result dict."""
    calls: list[list[str]] = []

    def run(selectors: list[str]) -> dict:
        calls.append(list(selectors))
        return {
            "args": ["pytest", *selectors],
            "command": "pytest (stub)",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
        }

    return run, calls


# ---------------------------------------------------------- _has_xfail_signal

@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        ("XFAIL tests/unit/test_a.py::test_b - pinned defect", True),
        ("XPASS tests/unit/test_a.py::test_b", True),
        ("1 xfailed in 0.02s", True),
        ("1 xpassed, 3 passed in 0.02s", True),
        ("4 passed in 0.03s", False),
        ("", False),
        # Regex vocabulary is exact pytest output: bare lowercase "xfail"
        # (e.g. option text or prose) is NOT a signal.
        ("expected to xfail via --runxfail", False),
    ],
)
def test_has_xfail_signal_stdout_vocabulary(stdout: str, expected: bool):
    assert pin_reconciler._has_xfail_signal({"stdout": stdout, "stderr": ""}) is expected


def test_has_xfail_signal_reads_stderr_too():
    result = {"stdout": "4 passed", "stderr": "warning: 1 xfailed"}
    assert pin_reconciler._has_xfail_signal(result) is True


def test_has_xfail_signal_is_fail_open_on_empty_or_malformed_result():
    # Missing keys read as "" via .get -> no signal (False), not an error.
    # An empty runner result therefore looks like a clean (reconciled) pin.
    assert pin_reconciler._has_xfail_signal({}) is False
    # None values are rendered by the f-string ("None") -> still no signal.
    assert pin_reconciler._has_xfail_signal({"stdout": None, "stderr": None}) is False


# ------------------------------------------------------------ reconcile_report

def test_stale_pin_still_emitting_xfail_is_flagged(tmp_path: Path):
    inventory = _inventory(tmp_path, _row("W2-01", pin="tests/unit/test_alpha.py::test_pinned"))
    run, calls = _stub_runner(exit_code=0, stdout="1 xfailed in 0.01s")

    rep = pin_reconciler.reconcile_report(inventory, runner=run)

    assert calls == [["tests/unit/test_alpha.py::test_pinned"]]
    (entry,) = rep["results"]
    assert entry["has_xfail_signal"] is True
    assert entry["issue"] == "normal pytest still reports xfail/xpass state"
    assert rep["issues"] == [entry]
    assert rep["missing"] == []


def test_reconciled_pin_running_clean_reports_no_issue(tmp_path: Path):
    inventory = _inventory(
        tmp_path,
        _row("W2-01", pin="tests/unit/test_alpha.py::test_pinned"),
        _row("W2-02", pin="tests/unit/test_beta.py::test_other", status="open"),
    )
    run, calls = _stub_runner(exit_code=0, stdout="1 passed in 0.01s")

    rep = pin_reconciler.reconcile_report(inventory, runner=run)

    # Only the verified row is audited; the open row is out of scope.
    assert [r["id"] for r in rep["rows"]] == ["W2-01"]
    assert calls == [["tests/unit/test_alpha.py::test_pinned"]]
    (entry,) = rep["results"]
    assert entry["has_xfail_signal"] is False
    assert entry["issue"] is None
    assert rep["issues"] == []


def test_failing_selector_flagged_as_pytest_failure_even_with_xfail_signal(tmp_path: Path):
    inventory = _inventory(tmp_path, _row("W2-01", pin="tests/unit/test_alpha.py::test_pinned"))
    run, _calls = _stub_runner(exit_code=1, stdout="1 failed, 1 xfailed in 0.05s")

    rep = pin_reconciler.reconcile_report(inventory, runner=run)

    (entry,) = rep["results"]
    # Non-zero exit takes precedence over the xfail-signal classification.
    assert entry["issue"] == "normal pytest failed"
    assert entry["has_xfail_signal"] is True
    assert rep["issues"] == [entry]


def test_verified_row_without_selector_lands_in_missing(tmp_path: Path):
    inventory = _inventory(tmp_path, _row("W2-03", pin="planned; no pin yet"))
    run, calls = _stub_runner()

    rep = pin_reconciler.reconcile_report(inventory, runner=run)

    assert calls == []  # nothing executable, runner never invoked
    assert rep["results"] == []
    (missing,) = rep["missing"]
    assert missing["id"] == "W2-03"
    assert missing["issue"] == "verified row has no executable selector"
    assert rep["issues"] == [missing]


def test_wave_filter_scopes_rows_and_runs(tmp_path: Path):
    inventory = _inventory(
        tmp_path,
        _row("W2-01", pin="tests/unit/test_alpha.py::test_pinned", wave="2"),
        _row("W3-01", pin="tests/unit/test_gamma.py::test_late", wave="3"),
    )
    run, calls = _stub_runner()

    rep = pin_reconciler.reconcile_report(inventory, wave=3, runner=run)

    assert rep["wave"] == 3
    assert [r["id"] for r in rep["rows"]] == ["W3-01"]
    assert calls == [["tests/unit/test_gamma.py::test_late"]]


def test_duplicate_selector_mentions_run_once(tmp_path: Path):
    pin = "tests/unit/test_alpha.py::test_pinned; tests/unit/test_alpha.py::test_pinned"
    inventory = _inventory(tmp_path, _row("W2-01", pin=pin))
    run, calls = _stub_runner()

    pin_reconciler.reconcile_report(inventory, runner=run)

    assert calls == [["tests/unit/test_alpha.py::test_pinned"]]
