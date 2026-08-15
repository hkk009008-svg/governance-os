"""Unit tests for scripts/check_no_ceremony.py — the anti-ceremony detector.

Covers the pure, mailbox-free helpers (R6 `_pass_reports_missing_runxfail`,
R5 `_utv_status_violations`, the `_is_xfail_decorator` AST classifier) plus the
top-level `main()` GO/NO-GO on this repo (currently clean -> exit 0).

Hermetic: no network or repository writes. R3 uses a temporary test module and
two nested local pytest selectors; other helpers use in-memory inputs.
"""
from __future__ import annotations

import ast
import contextlib
import io
import sys

import check_no_ceremony as cnc
import wave_gate_check


# --------------------------------------------------------------------------
# main() — the whole detector on THIS repo (it currently passes -> exit 0)
# --------------------------------------------------------------------------

def test_main_returns_zero_when_configured_checks_pass():
    """Passing the bounded rules must not claim that all ceremony is absent."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cnc.main()
    assert rc == 0
    out = buf.getvalue()
    # sanity: it actually ran the rule pipeline, not a short-circuit
    assert "CEREMONY CHECK" in out
    assert "RESULT: configured anti-ceremony checks passed" in out
    assert "does not certify every protocol surface" in out
    assert "no ceremony detected" not in out


def test_r3_executes_a_real_selector_through_the_wave_gate():
    status, details = cnc.rule_gate_executes()

    assert status == "PASS", details
    assert "executed witnessed strict-xfail controls" in details[0]
    assert "unresolved UNMET, fixed MET" in details[0]


def test_r3_rejects_a_met_report_without_runner_evidence(monkeypatch):
    """A status-only MET cannot satisfy the behavioral execution control."""

    monkeypatch.setattr(
        wave_gate_check,
        "gate_report",
        lambda *_args, **_kwargs: {
            "verdict": "MET",
            "selectors": [],
            "pytest": None,
        },
    )

    status, details = cnc.rule_gate_executes()

    assert status == "FAIL"
    assert "did not produce" in details[0]


def test_r3_rejects_fabricated_pytest_results_without_execution_witness(
    monkeypatch,
):
    def fabricated_runner(selectors: list[str]) -> dict:
        unresolved = "unresolved_defect" in selectors[0]
        return {
            "args": ["pytest", *selectors, "--runxfail"],
            "command": "pytest " + " ".join(selectors) + " --runxfail",
            "exit_code": 1 if unresolved else 0,
            "stdout": "1 failed\n" if unresolved else "1 passed\n",
            "stderr": "",
        }

    monkeypatch.setattr(wave_gate_check, "_run_pytest_selectors", fabricated_runner)

    status, details = cnc.rule_gate_executes()

    assert status == "FAIL"
    assert "did not produce" in details[0]


def test_r6_fails_closed_when_its_consumer_is_unavailable(monkeypatch):
    monkeypatch.setitem(sys.modules, "consume_reviewer_result", None)

    status, details = cnc.rule_report_cites_executed_pin()

    assert status == "FAIL"
    assert "consumer unavailable" in details[0]


# --------------------------------------------------------------------------
# R6 — _pass_reports_missing_runxfail (pure over (label, result) pairs)
# --------------------------------------------------------------------------

def test_pass_with_no_runxfail_command_flags_violation():
    """A `pass` verdict whose commands[] cites no --runxfail pin is ceremony."""
    out = cnc._pass_reports_missing_runxfail([("r", {"verdict": "pass", "commands": []})])
    assert len(out) == 1
    assert out[0].startswith("r:")
    assert "--runxfail" in out[0]


def test_pass_citing_runxfail_command_is_clean():
    """A `pass` whose commands[] cites a --runxfail command yields no violation."""
    results = [
        ("r", {"verdict": "pass", "commands": [{"command": "pytest tests/pins --runxfail -q"}]})
    ]
    assert cnc._pass_reports_missing_runxfail(results) == []


def test_non_pass_verdicts_are_not_gated():
    """`issues` / `unable_to_verify` make no GO claim, so they owe no pin re-exec."""
    results = [
        ("a", {"verdict": "issues", "commands": []}),
        ("b", {"verdict": "unable_to_verify", "commands": []}),
    ]
    assert cnc._pass_reports_missing_runxfail(results) == []


def test_pass_with_non_list_commands_is_a_clean_fail_not_a_crash():
    """Wrong-type commands[] is treated as 'no pin cited' -> one violation, no exception."""
    out = cnc._pass_reports_missing_runxfail([("r", {"verdict": "pass", "commands": None})])
    assert len(out) == 1
    assert "--runxfail" in out[0]


# --------------------------------------------------------------------------
# R5 — _utv_status_violations over an inventory markdown string
# --------------------------------------------------------------------------

def test_utv_status_violation_flags_exact_cell_match():
    """A data row with a cell that is exactly `unable_to_verify` is flagged."""
    text = (
        "| id | subsystem | status |\n"
        "|----|-----------|--------|\n"
        "| r1 | foo | unable_to_verify |\n"
        "| r2 | bar | open |\n"
    )
    out = cnc._utv_status_violations(text)
    assert len(out) == 1
    assert out[0].startswith("row 'r1':")
    assert "unable_to_verify" in out[0]


def test_utv_status_clean_table_passes():
    """No data row carries the UTV verdict as a status -> no violations.

    The header row's `status` column header is prose, not the token, so it is
    not flagged; the separator and header rows are skipped entirely.
    """
    text = (
        "| id | subsystem | status |\n"
        "|----|-----------|--------|\n"
        "| r1 | foo | open |\n"
        "| r2 | bar | done |\n"
    )
    assert cnc._utv_status_violations(text) == []


def test_utv_status_is_case_insensitive():
    """The exact-cell match is case-insensitive (Unable_To_Verify is still UTV)."""
    text = (
        "| id | subsystem | status |\n"
        "|----|-----------|--------|\n"
        "| r9 | baz | Unable_To_Verify |\n"
    )
    out = cnc._utv_status_violations(text)
    assert len(out) == 1
    assert out[0].startswith("row 'r9':")


# --------------------------------------------------------------------------
# _is_xfail_decorator — AST classifier
# --------------------------------------------------------------------------

def _first_decorator(snippet: str) -> ast.expr:
    tree = ast.parse(snippet)
    fn = tree.body[-1]  # the decorated def is the last statement
    return fn.decorator_list[0]


def test_is_xfail_decorator_identifies_pytest_mark_xfail_call():
    """A `@pytest.mark.xfail(...)` Call node is recognized and returned as-is."""
    deco = _first_decorator(
        "import pytest\n"
        "@pytest.mark.xfail(strict=True, reason='known defect')\n"
        "def test_x():\n    pass\n"
    )
    assert isinstance(deco, ast.Call)
    assert cnc._is_xfail_decorator(deco) is deco


def test_is_xfail_decorator_identifies_bare_attribute():
    """A bare `@pytest.mark.xfail` Attribute node is also recognized."""
    deco = _first_decorator(
        "import pytest\n"
        "@pytest.mark.xfail\n"
        "def test_x():\n    pass\n"
    )
    assert isinstance(deco, ast.Attribute)
    assert cnc._is_xfail_decorator(deco) is deco


def test_is_xfail_decorator_rejects_non_xfail_marker():
    """A non-xfail marker (e.g. pytest.mark.skip) returns None."""
    deco = _first_decorator(
        "import pytest\n"
        "@pytest.mark.skip\n"
        "def test_x():\n    pass\n"
    )
    assert cnc._is_xfail_decorator(deco) is None


def test_python_growth_rejects_large_total_and_per_file_growth():
    violations, summary = cnc._python_growth_violations(
        "120\t5\tscripts/large.py\n10\t0\ttests/test_large.py\n"
    )

    assert "net 125" in summary
    assert any("scripts/large.py" in item for item in violations)
    assert any("total net Python growth" in item for item in violations)


def test_python_growth_accepts_deletion_first_refactor():
    violations, summary = cnc._python_growth_violations(
        "40\t100\tscripts/compact.py\n"
    )

    assert violations == []
    assert "net -60" in summary


def test_python_growth_cannot_be_hidden_by_deleting_another_file():
    violations, summary = cnc._python_growth_violations(
        "260\t250\tscripts/new_layer.py\n0\t100\tscripts/old_layer.py\n"
    )

    assert "net -90" in summary
    assert any("scripts/new_layer.py" in item for item in violations)


def test_main_wires_python_growth_as_a_hard_failure(monkeypatch):
    monkeypatch.setattr(cnc, "rule_python_growth", lambda: ("FAIL", ["oversized"]))
    with contextlib.redirect_stdout(io.StringIO()) as output:
        assert cnc.main() == 1
    assert "python-growth            FAIL  oversized" in output.getvalue()
