#!/usr/bin/env python3
"""check_no_ceremony.py — forbid ceremony from the verification core.

CEREMONY = anything that produces the APPEARANCE of verification/enforcement
WITHOUT the substance: a green/PASS/verified signal that is NOT backed by
actually executing the check it claims to perform. The archetype (DECISIONS.md
ADR-027): a gate that READ an inventory `status` string and ran zero tests, so
"GATE MET" proved only that a ceremony was logged. FIX-1 has since landed — R3
now verifies wave_gate_check.py executes the pins.

This detector is the enforcement arm of ADR-028. It hard-fails (exit 1) on the
ceremony patterns it can detect with high precision, so new ceremony cannot be
introduced. FIX-1 (gate executes pins) has landed — see R3. FIX-2, a suite-wide
`--runxfail` CI step, was withdrawn as logically backwards: the normal strict
run already fails an unexpected XPASS, whereas a suite-wide --runxfail instead
fails deliberately-deferred pins by design. Targeted pin execution lives in
wave_gate_check.py. R4, which enforced the withdrawn step, was removed with it —
the rule roster is R1-R3, R5-R6 (numbering preserved for provenance).

Rules:
  R1  xfail-strictness     every pytest.mark.xfail must be strict=True + reason=  (AST; prevention)
  R2  invisible-green      importorskip/skipif in a campaign *xfail*.py pin file that would
                           SKIP (dep genuinely absent) -> hard; dep present -> WARN (latent)
  R3  gate-executes-pins   scripts/wave_gate_check.py must EXECUTE the pins, not read status  [FIX-1]
  R5  utv-not-a-row-status  `unable_to_verify` is a reviewer/operator VERDICT, never an inventory
                           row `status` — else it bypasses wave_gate_check blocking (ADR-027)  [ADR-032]
  R6  report-cites-pin-command  a verification-report whose verdict is `pass` must cite a
                           `--runxfail` pin command in commands[]; the consumer, not this rule,
                           re-runs it to detect fabrication                                    [ADR-032]

This script never modifies anything and never relaxes a gate; it only ADDS signal.
It is NOT itself a status-reader — it parses/executes against live source.

Usage:  .venv/bin/python scripts/check_no_ceremony.py   # exit 0 clean, 1 on any HARD violation
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"


def _is_xfail_decorator(node: ast.expr) -> ast.Call | ast.Attribute | None:
    """Return the decorator node if it is a pytest.mark.xfail (Call or bare Attribute)."""
    target = node.func if isinstance(node, ast.Call) else node
    # walk attribute chain, collect the trailing names
    names = []
    cur = target
    while isinstance(cur, ast.Attribute):
        names.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        names.append(cur.id)
    names = list(reversed(names))
    # match ...mark.xfail
    if len(names) >= 2 and names[-1] == "xfail" and names[-2] == "mark":
        return node
    return None


def rule_xfail_strictness() -> tuple[str, list[str]]:
    """R1 — every pytest.mark.xfail must carry strict=True and a non-empty reason."""
    violations: list[str] = []
    total = 0
    for py in sorted(TESTS.rglob("*.py")):
        try:
            tree = ast.parse(py.read_text(), filename=str(py))
        except SyntaxError as exc:  # pragma: no cover - defensive
            violations.append(f"{py.relative_to(ROOT)}: unparseable ({exc})")
            continue
        for n in ast.walk(tree):
            decos = getattr(n, "decorator_list", None)
            if not decos:
                continue
            for d in decos:
                xf = _is_xfail_decorator(d)
                if xf is None:
                    continue
                total += 1
                rel = f"{py.relative_to(ROOT)}:{d.lineno}"
                if isinstance(xf, ast.Attribute):
                    violations.append(f"{rel}: bare @pytest.mark.xfail (no strict=, no reason=)")
                    continue
                kw = {k.arg: k.value for k in xf.keywords if k.arg}
                strict = kw.get("strict")
                if not (isinstance(strict, ast.Constant) and strict.value is True):
                    violations.append(f"{rel}: xfail without strict=True (soft xfail hides a real failure)")
                reason = kw.get("reason")
                ok_reason = reason is not None and not (
                    isinstance(reason, ast.Constant) and not str(reason.value).strip()
                )
                if not ok_reason:
                    violations.append(f"{rel}: xfail without a non-empty reason=")
    status = "PASS" if not violations else "FAIL"
    summary = f"{total} xfail markers; all strict=True+reason" if not violations else f"{len(violations)} violation(s) of {total} markers"
    return status, [summary] + violations


def rule_invisible_green() -> tuple[str, list[str], list[str]]:
    """R2 — importorskip/skipif inside campaign *xfail*.py pin files.

    HARD only when the dependency is genuinely absent (the test would silently SKIP =
    invisible green). If the dep is importable, downgrade to WARN (latent risk).
    """
    hard: list[str] = []
    warn: list[str] = []
    for py in sorted(TESTS.glob("**/*xfail*.py")):
        try:
            tree = ast.parse(py.read_text(), filename=str(py))
        except SyntaxError:  # pragma: no cover
            continue
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            name = None
            if isinstance(f, ast.Attribute):
                name = f.attr
            if name not in ("importorskip", "skip", "skipif"):
                continue
            rel = f"{py.relative_to(ROOT)}:{n.lineno}"
            if name == "importorskip" and n.args and isinstance(n.args[0], ast.Constant):
                mod = str(n.args[0].value)
                present = importlib.util.find_spec(mod) is not None
                (warn if present else hard).append(
                    f"{rel}: importorskip({mod!r}) — dep {'present (latent invisible-green risk)' if present else 'ABSENT -> test SKIPS silently = ceremony'}"
                )
            else:
                warn.append(f"{rel}: {name}() in a pin file — confirm it cannot hide the pinned defect")
    status = "FAIL" if hard else ("WARN" if warn else "PASS")
    return status, hard, warn


def rule_gate_executes() -> tuple[str, list[str]]:
    """R3 — prove that a selected strict-xfail pin is load-bearing.

    This follows the production ``gate_report`` and pytest runner with two
    temporary strict-xfail controls: an unresolved defect must make the gate
    UNMET under ``--runxfail``, while the same pin shape with fixed behavior
    must flip to MET. Looking for runner strings is not execution evidence.
    """
    gate = ROOT / "scripts" / "wave_gate_check.py"
    if not gate.exists():
        return "FAIL", ["scripts/wave_gate_check.py is absent; the execution control cannot run"]

    try:
        import wave_gate_check as wave_gate
    except Exception as exc:  # pragma: no cover - defensive import boundary
        return "FAIL", [f"cannot import scripts/wave_gate_check.py: {exc}"]

    unresolved_selector = "tests/test_r3_control.py::test_unresolved_defect"
    fixed_selector = "tests/test_r3_control.py::test_fixed_behavior"
    header = (
        "| id | subsystem | file:line | severity | priority | fail-mode | repro | "
        "xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    def inventory_row(selector: str) -> str:
        return (
            "| R3-control | verification | scripts/wave_gate_check.py | CRITICAL | P0 | "
            f"false green | live control | {selector} | local | none | 1 | done | local | "
            "behavioral execution control |\n"
        )

    original_root = wave_gate._REPO_ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="pipeline-r3-") as tmp:
            control_root = pathlib.Path(tmp)
            tests_dir = control_root / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_r3_control.py").write_text(
                "from pathlib import Path\n\n"
                "import pytest\n\n"
                "@pytest.mark.xfail(strict=True, reason='R3 unresolved control')\n"
                "def test_unresolved_defect():\n"
                "    Path(__file__).with_name('unresolved.executed').write_text('R3 unresolved executed\\n')\n"
                "    assert False\n\n"
                "@pytest.mark.xfail(strict=True, reason='R3 fixed control')\n"
                "def test_fixed_behavior():\n"
                "    Path(__file__).with_name('fixed.executed').write_text('R3 fixed executed\\n')\n"
                "    assert True\n",
                encoding="utf-8",
            )
            unresolved_inventory = control_root / "unresolved.md"
            fixed_inventory = control_root / "fixed.md"
            unresolved_inventory.write_text(
                header + inventory_row(unresolved_selector), encoding="utf-8"
            )
            fixed_inventory.write_text(
                header + inventory_row(fixed_selector), encoding="utf-8"
            )
            wave_gate._REPO_ROOT = control_root
            unresolved_report = wave_gate.gate_report(
                unresolved_inventory,
                1,
                product_oracle_paths=[],
            )
            fixed_report = wave_gate.gate_report(
                fixed_inventory,
                1,
                product_oracle_paths=[],
            )
            unresolved_witness_path = tests_dir / "unresolved.executed"
            fixed_witness_path = tests_dir / "fixed.executed"
            unresolved_witness = (
                unresolved_witness_path.read_text(encoding="utf-8")
                if unresolved_witness_path.is_file()
                else None
            )
            fixed_witness = (
                fixed_witness_path.read_text(encoding="utf-8")
                if fixed_witness_path.is_file()
                else None
            )
    except Exception as exc:
        return "FAIL", [f"wave-gate execution control raised: {exc}"]
    finally:
        wave_gate._REPO_ROOT = original_root

    unresolved_run = unresolved_report.get("pytest")
    fixed_run = fixed_report.get("pytest")
    unresolved_args = (
        unresolved_run.get("args", []) if isinstance(unresolved_run, dict) else []
    )
    fixed_args = fixed_run.get("args", []) if isinstance(fixed_run, dict) else []
    if (
        unresolved_report.get("verdict") == "UNMET"
        and unresolved_report.get("selectors") == [unresolved_selector]
        and unresolved_report.get("pytest_blocking") is True
        and isinstance(unresolved_run, dict)
        and unresolved_run.get("exit_code") != 0
        and unresolved_selector in unresolved_args
        and "--runxfail" in unresolved_args
        and fixed_report.get("verdict") == "MET"
        and fixed_report.get("selectors") == [fixed_selector]
        and fixed_report.get("pytest_blocking") is False
        and isinstance(fixed_run, dict)
        and fixed_run.get("exit_code") == 0
        and fixed_selector in fixed_args
        and "--runxfail" in fixed_args
        and "passed" in fixed_run.get("stdout", "")
        and unresolved_witness == "R3 unresolved executed\n"
        and fixed_witness == "R3 fixed executed\n"
    ):
        return "PASS", [
            "wave_gate_check.py executed witnessed strict-xfail controls: unresolved UNMET, fixed MET"
        ]
    return "FAIL", [
        "wave_gate_check.py did not produce both selector-bound strict-xfail controls "
        f"(unresolved={unresolved_report!r}, fixed={fixed_report!r})"
    ]


def _inventory_data_rows(text: str) -> list[list[str]]:
    """Stripped pipe-delimited cells of each DATA row in the inventory table.

    Skips the `| id | subsystem | ... |` header, the `|---|` separator, and any
    non-table line. Robust to the surrounding markdown.
    """
    rows: list[list[str]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if set("".join(cells)) <= set("-: "):  # |---|:--| separator row
            continue
        lowered = [c.lower() for c in cells]
        if lowered[0] == "id" and "subsystem" in lowered:  # header
            continue
        rows.append(cells)
    return rows


def _utv_status_violations(text: str) -> list[str]:
    """Rows where any cell is EXACTLY `unable_to_verify` (case-insensitive).

    UTV is a verdict token; legitimately it can only ever be a standalone status
    cell, never embedded in prose — so an exact full-cell match is high-precision
    and immune to column miscounting from stray pipes in free-text cells.
    """
    bad: list[str] = []
    for cells in _inventory_data_rows(text):
        rid = cells[0] if cells else "<?>"
        for i, c in enumerate(cells):
            if c.lower() == "unable_to_verify":
                bad.append(
                    f"row {rid!r}: cell #{i} == 'unable_to_verify' — UTV is a reviewer/operator "
                    "verdict, never a row status (it would bypass wave_gate_check blocking)"
                )
    return bad


def rule_utv_not_a_row_status() -> tuple[str, list[str]]:
    """R5 — `unable_to_verify` must never be an inventory row status (ADR-027 / ADR-032).

    wave_gate_check.py tallies any status string but blocks only on severity/provisional,
    so a UTV row status would be silently NON-blocking — green-washing an unverified row.
    UTV is the reviewer/operator could-not-conclude VERDICT; the row stays in its prior
    state (typically `open`) and the receiving seat RE-DISPATCHES in a fixed env.
    """
    inv = ROOT / "docs" / "REMEDIATION-INVENTORY.md"
    if not inv.exists():
        return "PASS", ["docs/REMEDIATION-INVENTORY.md absent"]
    violations = _utv_status_violations(inv.read_text())
    if violations:
        return "FAIL", violations
    return "PASS", ["no inventory row uses unable_to_verify as a status (it is a verdict only)"]


def _pass_reports_missing_runxfail(named_results: list[tuple[str, dict]]) -> list[str]:
    """Violations for ``pass`` results that cite no ``--runxfail`` command.

    Pure over (label, result) pairs so the gate logic is unit-testable without a mailbox.
    Only the `pass` verdict is gated: `issues`/`unable_to_verify` make no GO claim, so they
    do not owe a pin re-execution.
    """
    bad: list[str] = []
    for label, result in named_results:
        if result.get("verdict") != "pass":
            continue
        commands = result.get("commands")
        if not isinstance(commands, list):
            commands = []  # wrong-type commands -> treated as "no pin cited" (clean FAIL, not crash)
        if not any(
            isinstance(c, dict) and "--runxfail" in (c.get("command") or "")
            for c in commands
        ):
            bad.append(
                f"{label}: verdict 'pass' but no command in commands[] cites a "
                "--runxfail pin run for the consumer to execute (ADR-032 R6)"
            )
    return bad


def rule_report_cites_executed_pin(repo_root: pathlib.Path = ROOT) -> tuple[str, list[str]]:
    """R6 — a ``pass`` report must cite a ``--runxfail`` command.

    This rule validates the report field only. ``consume_reviewer_result`` owns
    execution and result checking, so this function must not call the cited string
    "executed". Parsing is delegated to that consumer so there is one parser.
    """
    try:
        import consume_reviewer_result as _crr
    except Exception as exc:  # pragma: no cover - defensive (consumer should always import)
        return "FAIL", [f"reviewer-result consumer unavailable: {exc}"]
    try:
        results = _crr.iter_reviewer_results(repo_root)
    except _crr.ResultParseError as exc:
        return "FAIL", [f"malformed reviewer-result block — {exc}"]
    named = [(path.name, result) for path, result in results]
    violations = _pass_reports_missing_runxfail(named)
    if violations:
        return "FAIL", violations
    if named:
        return "PASS", [
            f"{len(named)} reviewer-result block(s); every pass cites a --runxfail command"
        ]
    return "PASS", ["no reviewer-result blocks in the mailbox yet (R6 inert until reviewers emit the schema)"]


def main() -> int:
    print("CEREMONY CHECK — forbid appearance-of-verification-without-substance (ADR-027 / ADR-028)\n")
    hard_fail = False

    r1_status, r1 = rule_xfail_strictness()
    print(f"R1 xfail-strictness ....... {r1_status}  {r1[0]}")
    for v in r1[1:]:
        print(f"     - {v}")
    hard_fail |= r1_status == "FAIL"

    r2_status, r2_hard, r2_warn = rule_invisible_green()
    print(f"R2 invisible-green ........ {r2_status}")
    for v in r2_hard:
        print(f"     ! {v}")
    for v in r2_warn:
        print(f"     ~ {v}")
    hard_fail |= r2_status == "FAIL"

    r3_status, r3 = rule_gate_executes()
    print(f"R3 gate-executes-pins ..... {r3_status}  {r3[0]}")
    hard_fail |= r3_status == "FAIL"

    r5_status, r5 = rule_utv_not_a_row_status()
    print(f"R5 utv-not-a-row-status ... {r5_status}  {r5[0]}")
    for v in r5[1:]:
        print(f"     ! {v}")
    hard_fail |= r5_status == "FAIL"

    r6_status, r6 = rule_report_cites_executed_pin()
    print(f"R6 report-cites-pin-command {r6_status}  {r6[0]}")
    for v in r6[1:]:
        print(f"     ! {v}")
    hard_fail |= r6_status == "FAIL"

    print()
    if hard_fail:
        print("RESULT: HARD ceremony violation(s) present — the verification core is not fully self-executing.")
        return 1
    print(
        "RESULT: configured anti-ceremony checks passed — this bounded rule set "
        "does not certify every protocol surface."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
