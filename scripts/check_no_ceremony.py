#!/usr/bin/env python3
"""Reject false verification signals and disproportionate Python growth."""

from __future__ import annotations

import ast
import importlib.util
import os
from pathlib import Path
import tempfile

import git_runner


ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
MAX_PYTHON_NET_GROWTH = 100
MAX_PYTHON_TEST_NET_GROWTH = 100
MAX_PYTHON_FILE_NET_GROWTH = 80
MAX_PYTHON_FILE_ADDITIONS = 250
PYTHON_PATHSPEC = ":(glob)**/*.py"


def _is_xfail_decorator(node: ast.expr) -> ast.Call | ast.Attribute | None:
    target = node.func if isinstance(node, ast.Call) else node
    if (
        isinstance(target, ast.Attribute)
        and target.attr == "xfail"
        and isinstance(target.value, ast.Attribute)
        and target.value.attr == "mark"
    ):
        return node
    return None


def rule_xfail_strictness() -> tuple[str, list[str]]:
    violations: list[str] = []
    total = 0
    for path in sorted(TESTS.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            violations.append(f"{path.relative_to(ROOT)}: unparseable ({exc})")
            continue
        for node in ast.walk(tree):
            for decorator in getattr(node, "decorator_list", ()):
                marker = _is_xfail_decorator(decorator)
                if marker is None:
                    continue
                total += 1
                label = f"{path.relative_to(ROOT)}:{decorator.lineno}"
                if isinstance(marker, ast.Attribute):
                    violations.append(f"{label}: bare xfail lacks strict=True and reason=")
                    continue
                keywords = {item.arg: item.value for item in marker.keywords if item.arg}
                strict = keywords.get("strict")
                reason = keywords.get("reason")
                if not (isinstance(strict, ast.Constant) and strict.value is True):
                    violations.append(f"{label}: xfail lacks strict=True")
                if reason is None or (
                    isinstance(reason, ast.Constant) and not str(reason.value).strip()
                ):
                    violations.append(f"{label}: xfail lacks a non-empty reason=")
    status = "PASS" if not violations else "FAIL"
    return status, [f"{total} xfail markers; {len(violations)} violation(s)", *violations]


def rule_invisible_green() -> tuple[str, list[str], list[str]]:
    hard: list[str] = []
    warnings: list[str] = []
    for path in sorted(TESTS.rglob("*xfail*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            name = node.func.attr
            if name not in {"importorskip", "skip", "skipif"}:
                continue
            label = f"{path.relative_to(ROOT)}:{node.lineno}"
            if name == "importorskip" and node.args and isinstance(node.args[0], ast.Constant):
                module = str(node.args[0].value)
                try:
                    present = importlib.util.find_spec(module) is not None
                except (ImportError, ModuleNotFoundError):
                    present = False
                (warnings if present else hard).append(
                    f"{label}: importorskip({module!r})"
                )
            else:
                warnings.append(f"{label}: {name}() can hide a pinned defect")
    return ("FAIL" if hard else "WARN" if warnings else "PASS"), hard, warnings


def rule_gate_executes() -> tuple[str, list[str]]:
    try:
        import wave_gate_check as wave_gate
    except Exception as exc:
        return "FAIL", [f"wave gate unavailable: {exc}"]

    selectors = {
        "unresolved": "tests/test_r3_control.py::test_unresolved_defect",
        "fixed": "tests/test_r3_control.py::test_fixed_behavior",
    }
    header = (
        "| id | subsystem | file:line | severity | priority | fail-mode | repro | "
        "xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    original_root = wave_gate._REPO_ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="pipeline-r3-") as tmp:
            root = Path(tmp)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_r3_control.py").write_text(
                "from pathlib import Path\nimport pytest\n\n"
                "@pytest.mark.xfail(strict=True, reason='unresolved control')\n"
                "def test_unresolved_defect():\n"
                "    Path(__file__).with_name('unresolved.executed').write_text('yes')\n"
                "    assert False\n\n"
                "@pytest.mark.xfail(strict=True, reason='fixed control')\n"
                "def test_fixed_behavior():\n"
                "    Path(__file__).with_name('fixed.executed').write_text('yes')\n"
                "    assert True\n",
                encoding="utf-8",
            )
            wave_gate._REPO_ROOT = root
            reports = {}
            for name, selector in selectors.items():
                inventory = root / f"{name}.md"
                inventory.write_text(
                    header
                    + "| R3 | verification | scripts/wave_gate_check.py | CRITICAL | P0 | "
                    f"false green | live | {selector} | local | none | 1 | done | local | control |\n",
                    encoding="utf-8",
                )
                reports[name] = wave_gate.gate_report(
                    inventory, 1, product_oracle_paths=[]
                )
            unresolved = reports["unresolved"]
            fixed = reports["fixed"]
            unresolved_run = unresolved.get("pytest") or {}
            fixed_run = fixed.get("pytest") or {}
            passed = all(
                (
                    unresolved.get("verdict") == "UNMET",
                    unresolved.get("selectors") == [selectors["unresolved"]],
                    unresolved.get("pytest_blocking") is True,
                    unresolved_run.get("exit_code") not in {None, 0},
                    "--runxfail" in unresolved_run.get("args", []),
                    fixed.get("verdict") == "MET",
                    fixed.get("selectors") == [selectors["fixed"]],
                    fixed.get("pytest_blocking") is False,
                    fixed_run.get("exit_code") == 0,
                    "--runxfail" in fixed_run.get("args", []),
                    (tests / "unresolved.executed").is_file(),
                    (tests / "fixed.executed").is_file(),
                )
            )
    except Exception as exc:
        return "FAIL", [f"wave-gate execution control raised: {exc}"]
    finally:
        wave_gate._REPO_ROOT = original_root
    if passed:
        return "PASS", ["executed witnessed strict-xfail controls: unresolved UNMET, fixed MET"]
    return "FAIL", ["wave gate did not produce both executed strict-xfail controls"]


def _inventory_data_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set("".join(cells)) <= set("-: "):
            continue
        if cells[0].lower() == "id" and any(cell.lower() == "subsystem" for cell in cells):
            continue
        rows.append(cells)
    return rows


def _utv_status_violations(text: str) -> list[str]:
    return [
        f"row {cells[0]!r}: cell #{index} is unable_to_verify, which is a verdict, not row status"
        for cells in _inventory_data_rows(text)
        for index, cell in enumerate(cells)
        if cell.lower() == "unable_to_verify"
    ]


def rule_utv_not_a_row_status() -> tuple[str, list[str]]:
    inventory = ROOT / "docs" / "REMEDIATION-INVENTORY.md"
    violations = _utv_status_violations(
        inventory.read_text(encoding="utf-8") if inventory.is_file() else ""
    )
    return ("FAIL" if violations else "PASS"), (
        violations or ["no inventory row uses unable_to_verify as a status"]
    )


def _pass_reports_missing_runxfail(named_results: list[tuple[str, dict]]) -> list[str]:
    violations: list[str] = []
    for label, result in named_results:
        if result.get("verdict") != "pass":
            continue
        commands = result.get("commands")
        if not isinstance(commands, list) or not any(
            isinstance(command, dict) and "--runxfail" in str(command.get("command", ""))
            for command in commands
        ):
            violations.append(f"{label}: pass verdict has no --runxfail command")
    return violations


def rule_report_cites_executed_pin(repo_root: Path = ROOT) -> tuple[str, list[str]]:
    try:
        import consume_reviewer_result

        named = [
            (path.name, result)
            for path, result in consume_reviewer_result.iter_reviewer_results(repo_root)
        ]
    except Exception as exc:
        return "FAIL", [f"reviewer-result consumer unavailable: {exc}"]
    violations = _pass_reports_missing_runxfail(named)
    return ("FAIL" if violations else "PASS"), (
        violations or [f"{len(named)} reviewer-result block(s) checked"]
    )


def _python_growth_violations(
    numstat: str, introduced: frozenset[str] = frozenset()
) -> tuple[list[str], str]:
    """Count growth by what it is, not only by how many lines it is.

    Two rules, each from a range this gate refused while doing no good. A file
    that did not exist at the base is an INTRODUCTION, so the per-file cap --
    which exists to stop one file bloating -- does not apply to it; three
    harness tools were refused for the crime of arriving with their fixtures.
    And tests carry their own ledger, because a reviewer-required control
    should never compete with feature logic for one number; a control this
    reviewer demanded once pushed a branch to 102 and FAILed it.

    Unexplained growth in existing production files is still refused exactly as
    before, which is the thing the gate is actually for.
    """

    rows = [line.split("\t", 2) for line in numstat.splitlines()]
    invalid = next((row for row in rows if len(row) != 3 or not row[0].isdigit() or not row[1].isdigit()), None)
    if invalid:
        return [f"unparseable Python numstat row: {invalid!r}"], "unparseable"
    files = [(int(a), int(d), path) for a, d, path in rows]
    added, deleted = (sum(item[index] for item in files) for index in (0, 1))
    tests = [item for item in files if item[2].startswith("tests/")]
    product = [item for item in files if not item[2].startswith("tests/")]
    violations: list[str] = []
    for additions, deletions, path in files:
        if additions > MAX_PYTHON_FILE_ADDITIONS:
            violations.append(f"{path}: {additions} added lines exceeds {MAX_PYTHON_FILE_ADDITIONS}")
        if path in introduced:
            continue
        if additions - deletions > MAX_PYTHON_FILE_NET_GROWTH:
            violations.append(f"{path}: net growth {additions - deletions} exceeds {MAX_PYTHON_FILE_NET_GROWTH}")
    for label, group, ceiling in (
        ("production", product, MAX_PYTHON_NET_GROWTH),
        ("test", tests, MAX_PYTHON_TEST_NET_GROWTH),
    ):
        net = sum(item[0] for item in group) - sum(item[1] for item in group)
        if net > ceiling:
            violations.append(f"net {label} Python growth {net} exceeds {ceiling}")
    return violations, f"{added} added, {deleted} deleted, net {added - deleted}"


def _introduced_python(base: str | None) -> frozenset[str]:
    """Paths that did not exist at `base`, asked of Git rather than inferred.

    A numstat row with no deletions looks identical whether the file is new or
    merely never shrank, so the distinction has to come from --diff-filter=A.
    """

    if base is None:
        return frozenset()
    result = git_runner.run_git(
        ROOT, ["diff", "--name-only", "--diff-filter=A", base, "--", PYTHON_PATHSPEC], text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"cannot list Python files introduced since {base}")
    return frozenset(line for line in result.stdout.splitlines() if line)


def _untracked_python_paths() -> frozenset[str]:
    """Untracked files are introductions by definition."""

    return frozenset(
        row.split("\t", 2)[2] for row in _untracked_python_numstat().splitlines() if row
    )


def _growth_base() -> str | None:
    explicit = os.environ.get("NO_CEREMONY_BASE", "").strip()
    if explicit and set(explicit) != {"0"}:
        return explicit
    dirty = git_runner.run_git(ROOT, ["diff", "--quiet", "HEAD", "--", PYTHON_PATHSPEC]).returncode
    if dirty == 1:
        return "HEAD"
    if dirty > 1:
        raise RuntimeError("git diff could not inspect Python changes")
    parent = git_runner.run_git(ROOT, ["rev-parse", "--verify", "HEAD^"])
    return "HEAD^" if parent.returncode == 0 else None


def _untracked_python_numstat() -> str:
    result = git_runner.run_git(
        ROOT,
        ["ls-files", "--others", "--exclude-standard", "-z", "--", PYTHON_PATHSPEC],
    )
    if result.returncode != 0:
        raise RuntimeError("git ls-files could not inspect untracked Python files")
    rows = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", "surrogateescape")
        if "\t" in path or "\n" in path:
            raise RuntimeError("untracked Python path contains a tab or newline")
        rows.append(f"{len((ROOT / path).read_bytes().splitlines())}\t0\t{path}")
    return "\n".join(rows)


def rule_python_growth() -> tuple[str, list[str]]:
    try:
        base = _growth_base()
        untracked = _untracked_python_numstat()
        if base is None and not untracked:
            return "PASS", ["no parent range to inspect"]
        tracked = ""
        if base is not None:
            diff = git_runner.run_git(ROOT, ["diff", "--numstat", base, "--", PYTHON_PATHSPEC], text=True)
            if diff.returncode != 0:
                return "FAIL", [f"cannot inspect Python growth from {base}"]
            tracked = diff.stdout
        numstat = "\n".join(
            part.rstrip("\n") for part in (tracked, untracked) if part
        )
        violations, summary = _python_growth_violations(
            numstat, _introduced_python(base) | _untracked_python_paths()
        )
    except Exception as exc:
        return "FAIL", [f"Python growth check failed: {exc}"]
    return ("FAIL" if violations else "PASS"), [
        f"{summary} from {base or 'untracked files'}",
        *violations,
    ]


def main() -> int:
    print("CEREMONY CHECK — executable evidence and bounded Python growth\n")
    status, details = rule_xfail_strictness()
    results = [("xfail-strictness", status, details)]
    status, hard, warnings = rule_invisible_green()
    results.append(("invisible-green", status, [*hard, *warnings] or ["clean"]))
    for name, rule in (
        ("gate-executes-pins", rule_gate_executes),
        ("utv-not-row-status", rule_utv_not_a_row_status),
        ("report-cites-pin", rule_report_cites_executed_pin),
        ("python-growth", rule_python_growth),
    ):
        status, details = rule()
        results.append((name, status, details))
    for name, status, details in results:
        print(f"{name:<24} {status}  {details[0]}")
        for detail in details[1:]:
            print(f"  - {detail}")
    if any(status == "FAIL" for _, status, _ in results):
        print("\nRESULT: hard violation present")
        return 1
    print(
        "\nRESULT: configured anti-ceremony checks passed; this bounded set "
        "does not certify every protocol surface"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
