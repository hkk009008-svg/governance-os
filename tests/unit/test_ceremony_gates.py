"""Unit tests for scripts/check_no_ceremony.py — the anti-ceremony detector.

Covers the pure, mailbox-free helpers (R6 `_pass_reports_missing_runxfail`,
R5 `_utv_status_violations`, the `_is_xfail_decorator` AST classifier) plus the
top-level `main()` GO/NO-GO on this repo (currently clean -> exit 0).

Hermetic: no network, no git, no filesystem writes — all inputs are in-memory
strings / AST nodes, and `main()` only reads committed source.
"""
from __future__ import annotations

import ast
import contextlib
import io

import check_no_ceremony as cnc


# --------------------------------------------------------------------------
# main() — the whole detector on THIS repo (it currently passes -> exit 0)
# --------------------------------------------------------------------------

def test_main_returns_zero_on_clean_repo():
    """The repo is ceremony-clean today, so main() must return 0 (no HARD violation)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cnc.main()
    assert rc == 0
    out = buf.getvalue()
    # sanity: it actually ran the rule pipeline, not a short-circuit
    assert "CEREMONY CHECK" in out
    assert "RESULT: no ceremony detected" in out


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
    """A `pass` whose commands[] cites an executed --runxfail run yields no violation."""
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
