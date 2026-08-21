#!/usr/bin/env python3
"""Executable wave-gate checker for the hardening campaign.

Reads docs/REMEDIATION-INVENTORY.md and reports, for a wave, whether the gate is
MET. ADR-027 makes the inventory status column display-only for this verdict:
the gate executes the wave's CRITICAL/MAJOR pins with pytest --runxfail and
fails closed on missing/non-executable oracles.

Read-only - never mutates the inventory.
"""
from __future__ import annotations
import argparse
import ast
import fnmatch
import json
import math
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Callable

_MODULE_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _MODULE_ROOT
_RUNTIME_OPTION = "--pipeline-wave-gate-runtime"
_runtime_enabled = False
_runtime_skips: list[str] = []

_COLS = ("id", "subsystem", "file:line", "severity", "priority", "fail-mode",
         "repro", "xfail-pin", "lane-owner", "shared-lock", "wave", "status",
         "verifier", "notes")
_BLOCK_SEV = {"CRITICAL", "MAJOR"}
_SELECTOR_RE = re.compile(
    r"(?P<selector>(?:\.?/)?tests/[A-Za-z0-9_./-]+\.py(?:::[^\s;,()]+)*)"
)
_XFAIL_SIGNAL_RE = re.compile(r"\b(?:XFAIL|XPASS|xfailed|xpassed)\b")
_PRODUCT_ORACLE_MIN_WAVE = 2
_PRODUCT_ORACLE_PATTERN = "logs/product-oracle-*.json"

PytestRunner = Callable[[list[str]], dict]


def pytest_addoption(parser) -> None:
    """Trusted child-pytest option used to prove selected pins are real and execute."""

    parser.getgroup("pipeline-wave-gate").addoption(
        _RUNTIME_OPTION,
        action="store_true",
        default=False,
        help="require every selected item to carry an active strict xfail marker",
    )


def pytest_configure(config) -> None:
    global _runtime_enabled, _runtime_skips
    _runtime_enabled = bool(config.getoption(_RUNTIME_OPTION))
    _runtime_skips = []


def pytest_collection_modifyitems(config, items) -> None:
    if not config.getoption(_RUNTIME_OPTION):
        return
    import pytest

    violations: list[str] = []
    for item in items:
        marker = item.get_closest_marker("xfail")
        if marker is None:
            violations.append(f"{item.nodeid}: no runtime xfail marker")
            continue
        if marker.args or "condition" in marker.kwargs:
            violations.append(f"{item.nodeid}: conditional runtime xfail marker")
        if marker.kwargs.get("strict") is not True:
            violations.append(f"{item.nodeid}: runtime xfail marker is not strict=True")
        if marker.kwargs.get("run", True) is not True:
            violations.append(f"{item.nodeid}: runtime xfail marker is not executable")
        if list(item.iter_markers(name="skip")) or list(item.iter_markers(name="skipif")):
            violations.append(f"{item.nodeid}: selected pin is also skipped")
    if violations:
        raise pytest.UsageError("wave-gate runtime marker check failed: " + "; ".join(violations))


def pytest_runtest_logreport(report) -> None:
    if _runtime_enabled and report.skipped:
        _runtime_skips.append(report.nodeid)


def pytest_sessionfinish(session, exitstatus) -> None:
    if _runtime_enabled and _runtime_skips and int(session.exitstatus) == 0:
        import pytest

        session.exitstatus = pytest.ExitCode.TESTS_FAILED

def _parse_rows(inventory_path: Path) -> list[dict]:
    rows: list[dict] = []
    malformed: list[str] = []
    for line in inventory_path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(_COLS):
            # Header/separator rows are exempt; a DATA row with a drifted column
            # count must fail closed — silently dropping it would let a schema
            # drift erase rows from the gate.
            if cells and (cells[0] == "id" or set("".join(cells)) <= set("-: ")):
                continue
            malformed.append(line[:80])
            continue
        row = dict(zip(_COLS, cells))
        if row["id"] in ("id", "----", "") or set(row["id"]) <= {"-"}:
            continue
        rows.append(row)
    if malformed:
        raise ValueError(
            f"{inventory_path.name}: {len(malformed)} data row(s) with a drifted "
            f"column count (expected {len(_COLS)}): " + " ; ".join(malformed[:3])
        )
    return rows

def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            out.append(value)
            seen.add(value)
    return out

def _selectors_from_pin(pin_cell: str) -> list[str]:
    """Extract executable pytest selectors from an inventory xfail-pin cell."""
    selectors: list[str] = []
    last_path: str | None = None
    pieces = re.split(r"\s+/\s+|[;,]\s*", pin_cell.strip())
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        if piece.startswith("::") and last_path:
            node = piece.split()[0].rstrip(").,;")
            selectors.append(f"{last_path}{node}")
            continue
        for match in _SELECTOR_RE.finditer(piece):
            selector = match.group("selector").rstrip(").,;")
            selectors.append(selector)
            last_path = selector.split("::", 1)[0]
    return _dedupe(selectors)

def _gate_row(row: dict) -> bool:
    return row["severity"].upper() in _BLOCK_SEV or row["status"] == "provisional"


def _strict_xfail_issue(selector: str) -> str | None:
    """Return why a selector is not a literal strict-xfail regression pin."""

    pieces = selector.removeprefix("./").split("::")
    if len(pieces) < 2 or not pieces[1]:
        return "selector must name one strict-xfail test node"
    source = (_REPO_ROOT / pieces[0]).resolve()
    tests_root = (_REPO_ROOT / "tests").resolve()
    try:
        source.relative_to(tests_root)
    except ValueError:
        return "selector resolves outside the tests tree"
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return f"selector source is unreadable: {exc}"

    body: list[ast.stmt] = tree.body
    target: ast.FunctionDef | ast.AsyncFunctionDef | None = None
    for index, raw_name in enumerate(pieces[1:]):
        name = raw_name.split("[", 1)[0]
        node = next(
            (
                candidate
                for candidate in body
                if isinstance(
                    candidate, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                )
                and candidate.name == name
            ),
            None,
        )
        if node is None:
            return f"selector node {raw_name!r} does not exist"
        if index < len(pieces[1:]) - 1:
            if not isinstance(node, ast.ClassDef):
                return f"selector component {raw_name!r} is not a test class"
            body = node.body
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            target = node

    if target is None:
        return "selector must resolve to one test function"
    for decorator in target.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        func = decorator.func
        dotted = []
        while isinstance(func, ast.Attribute):
            dotted.append(func.attr)
            func = func.value
        if isinstance(func, ast.Name):
            dotted.append(func.id)
        if list(reversed(dotted)) != ["pytest", "mark", "xfail"]:
            continue
        if decorator.args:
            return "pytest.mark.xfail condition must be absent, not positional"
        if any(keyword.arg is None for keyword in decorator.keywords):
            return "pytest.mark.xfail metadata must be literal, not **kwargs"
        if any(keyword.arg == "condition" for keyword in decorator.keywords):
            return "pytest.mark.xfail condition must be absent"
        run_value = next(
            (kw.value for kw in decorator.keywords if kw.arg == "run"), None
        )
        if run_value is not None and not (
            isinstance(run_value, ast.Constant) and run_value.value is True
        ):
            return "pytest.mark.xfail run must be absent or literal True"
        strict = next((kw.value for kw in decorator.keywords if kw.arg == "strict"), None)
        if isinstance(strict, ast.Constant) and strict.value is True:
            return None
        return "pytest.mark.xfail must declare literal strict=True"
    return "test is not decorated with literal pytest.mark.xfail(strict=True)"

def _blocker(row: dict, reason: str) -> dict:
    blocked = dict(row)
    blocked["block_reason"] = reason
    return blocked

def _run_pytest_selectors(selectors: list[str]) -> dict:
    args = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "pipeline.wave_gate_check",
        _RUNTIME_OPTION,
        *selectors,
        "--runxfail",
        "-q",
        "--tb=short",
    ]
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(_MODULE_ROOT) + (
        os.pathsep + pythonpath if pythonpath else ""
    )
    proc = subprocess.run(
        args,
        cwd=_REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "args": args,
        "command": shlex.join(args),
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

def _committed_product_oracle_paths() -> tuple[list[Path], str | None]:
    """Return product-oracle artifacts committed in HEAD, ignoring seat-local indexes."""
    args = [
        "git",
        "ls-tree",
        "-r",
        "--name-only",
        "HEAD",
        "--",
        "logs",
    ]
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    try:
        proc = subprocess.run(
            args,
            cwd=_REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return [], str(exc)
    if proc.returncode != 0:
        return [], (proc.stderr or proc.stdout or "git ls-tree failed").strip()
    paths = []
    for line in proc.stdout.splitlines():
        rel = line.strip()
        if rel and fnmatch.fnmatch(rel, _PRODUCT_ORACLE_PATTERN):
            paths.append(_REPO_ROOT / rel)
    return paths, None

def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )

def _product_oracle_issue(path: Path, wave: int) -> str | None:
    try:
        data = json.loads(_product_oracle_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        return f"{path}: unreadable JSON ({exc})"
    if not isinstance(data, dict):
        return f"{path}: top-level JSON value is not an object"
    if data.get("artifact_kind") != "product-oracle":
        return f"{path}: artifact_kind is not product-oracle"
    if data.get("wave") != wave:
        return f"{path}: wave is not {wave}"
    # TODO(<PROJECT>): replace the two metric blocks below with project-specific
    # product-oracle fields (finite numeric quality metrics for your domain).
    primary_metric = data.get("primary_metric")
    if not isinstance(primary_metric, dict) or not _finite_number(primary_metric.get("score")):
        return f"{path}: missing finite primary_metric.score"
    secondary_metric = data.get("secondary_metric")
    if not isinstance(secondary_metric, dict) or not _finite_number(secondary_metric.get("value")):
        return f"{path}: missing finite secondary_metric.value"
    return None

def _product_oracle_text(path: Path) -> str:
    """Read artifact content from HEAD when the path belongs to the repo."""
    try:
        rel = path.resolve().relative_to(_REPO_ROOT.resolve())
    except (OSError, ValueError):
        return path.read_text()

    args = ["git", "show", f"HEAD:{rel.as_posix()}"]
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    proc = subprocess.run(
        args,
        cwd=_REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "git show failed").strip()
        raise OSError(msg)
    return proc.stdout

def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(_REPO_ROOT))
    except ValueError:
        return str(path)

def _product_oracle_report(paths: list[Path], wave: int) -> dict:
    valid: list[str] = []
    invalid: list[str] = []
    for path in paths:
        issue = _product_oracle_issue(path, wave)
        if issue:
            invalid.append(issue)
        else:
            valid.append(_display_path(path))
    return {"valid": valid, "invalid": invalid}

def _has_xfail_signal(pytest_result: dict | None) -> bool:
    if not pytest_result:
        return False
    return bool(_XFAIL_SIGNAL_RE.search(
        f"{pytest_result.get('stdout', '')}\n{pytest_result.get('stderr', '')}"
    ))

def gate_report(
    inventory_path: Path,
    wave: int,
    *,
    runner: PytestRunner | None = None,
    product_oracle_paths: list[Path] | None = None,
) -> dict:
    rows = [r for r in _parse_rows(inventory_path) if r["wave"] == str(wave)]
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    gate_rows = [r for r in rows if _gate_row(r)]
    selectors_by_row: dict[str, list[str]] = {}
    no_oracle_blockers: list[dict] = []
    provisional_blockers: list[dict] = []
    selectors: list[str] = []
    for row in gate_rows:
        row_selectors = _selectors_from_pin(row["xfail-pin"])
        if row_selectors:
            valid_selectors = []
            for selector in row_selectors:
                issue = _strict_xfail_issue(selector)
                if issue is None:
                    valid_selectors.append(selector)
                else:
                    no_oracle_blockers.append(
                        _blocker(row, f"invalid xfail-pin {selector}: {issue}")
                    )
            if valid_selectors:
                selectors_by_row[row["id"]] = valid_selectors
                selectors.extend(valid_selectors)
        else:
            no_oracle_blockers.append(_blocker(row, "no executable xfail-pin selector"))
        if row["status"] == "provisional":
            provisional_blockers.append(_blocker(row, "provisional row is not gate-clearable"))

    selectors = _dedupe(selectors)
    pytest_result = (runner or _run_pytest_selectors)(selectors) if selectors else None
    pytest_blocking = bool(
        pytest_result
        and (pytest_result["exit_code"] != 0 or _has_xfail_signal(pytest_result))
    )
    product_oracle_blockers: list[str] = []
    product_oracles = {"valid": [], "invalid": []}
    if rows and wave >= _PRODUCT_ORACLE_MIN_WAVE:
        if product_oracle_paths is None:
            product_oracle_paths, product_oracle_error = _committed_product_oracle_paths()
        else:
            product_oracle_error = None
        product_oracles = _product_oracle_report(product_oracle_paths, wave)
        if product_oracle_error:
            product_oracle_blockers.append(
                f"could not list committed {_PRODUCT_ORACLE_PATTERN} artifacts: "
                f"{product_oracle_error}"
            )
        if not product_oracles["valid"]:
            required = (
                f"Wave {wave} requires a committed {_PRODUCT_ORACLE_PATTERN} artifact "
                f"with artifact_kind=product-oracle, wave={wave}, finite "
                "primary_metric.score, and finite secondary_metric.value"
                # TODO(<PROJECT>): update field names to match your product-oracle schema
            )
            if product_oracles["invalid"]:
                required += f"; invalid artifacts: {'; '.join(product_oracles['invalid'][:3])}"
            product_oracle_blockers.append(required)
    empty_wave_blockers = []
    if not rows:
        empty_wave_blockers.append(
            {
                "id": f"wave-{wave}",
                "severity": "GATE",
                "status": "missing",
                "file:line": str(inventory_path),
                "block_reason": "wave has no inventory rows",
            }
        )
    blockers = empty_wave_blockers + no_oracle_blockers + provisional_blockers
    return {
        "wave": wave,
        "verdict": (
            "MET"
            if not blockers and not pytest_blocking and not product_oracle_blockers
            else "UNMET"
        ),
        "counts": counts,
        "blockers": blockers,
        "product_oracle_blockers": product_oracle_blockers,
        "product_oracles": product_oracles,
        "gate_rows": gate_rows,
        "selectors": selectors,
        "selectors_by_row": selectors_by_row,
        "pytest": pytest_result,
        "pytest_blocking": pytest_blocking,
    }

def _tail(text: str, max_lines: int = 40) -> list[str]:
    lines = text.rstrip().splitlines()
    if len(lines) <= max_lines:
        return lines
    return ["..."] + lines[-max_lines:]

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("wave", type=int)
    ap.add_argument("--inventory", default=_REPO_ROOT / "docs/REMEDIATION-INVENTORY.md", type=Path)
    args = ap.parse_args(argv)
    if not args.inventory.exists():
        print(f"inventory not found: {args.inventory}", file=sys.stderr)
        return 2
    try:
        rep = gate_report(args.inventory, args.wave)
    except ValueError as exc:
        print(f"inventory schema drift — gate fails closed: {exc}", file=sys.stderr)
        return 2
    print(f"Wave {rep['wave']} gate: {rep['verdict']}  counts={rep['counts']}")
    print(f"  gate rows: {len(rep['gate_rows'])}; executable selectors: {len(rep['selectors'])}")
    for b in rep["blockers"]:
        print(
            f"  BLOCKER [{b['severity']}/{b['status']}] {b['id']} "
            f"({b['file:line']}): {b['block_reason']}"
        )
    for blocker in rep["product_oracle_blockers"]:
        print(f"  PRODUCT ORACLE BLOCKER: {blocker}")
    for artifact in rep["product_oracles"]["valid"]:
        print(f"  PRODUCT ORACLE: {artifact}")
    if rep["pytest"]:
        print(f"  PYTEST: exit={rep['pytest']['exit_code']} command={rep['pytest']['command']}")
        output = "\n".join(
            _tail(rep["pytest"].get("stdout", ""))
            + _tail(rep["pytest"].get("stderr", ""))
        )
        if output:
            print("  PYTEST output tail:")
            for line in output.splitlines():
                print(f"    {line}")
    return 0 if rep["verdict"] == "MET" else 1

if __name__ == "__main__":
    sys.exit(main())
