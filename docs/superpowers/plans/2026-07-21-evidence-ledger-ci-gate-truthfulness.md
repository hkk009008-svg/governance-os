# Evidence-Ledger CI and Gate Truthfulness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the omitted checklist-coverage suite in CI and make R4 require one real fixed regression-pin runner invocation instead of accepting a `--runxfail` comment or unrelated string.

**Architecture:** Add a tiny standard-library runner whose only job is to execute the fixed `tests/unit --runxfail` pytest command and return its exit code. CI invokes that runner through one exact single-line `run:` entry. `check_no_ceremony` validates the exact workflow line and the runner's exported fixed argv. Unit tests prove comments, names, and unrelated strings cannot satisfy R4 and that the runner actually passes its argv to `subprocess.run` without a shell.

**Tech Stack:** Python 3.11+, pytest, `subprocess`, `sys`, `pathlib`, GitHub Actions YAML as text, existing governance smoke.

## Global Constraints

- Bind this packet to the locally integrated, Operator2-accepted Packet 3 head. Before Task 1, set the task-specific shell variable `EVIDENCE_LEDGER_PACKET_PARENT_SHA` to the route's exact 40-hex parent, assert `git rev-parse HEAD` equals it, and keep that shell active for the packet.
- Use a dedicated evidence-ledger worktree; preserve `.vscode/` and unrelated WIP.
- Do not install PyYAML or another parser. The accepted CI contract is deliberately one exact line, so line-based structural validation is sufficient and auditable.
- Do not change R1, R2, R3, R5, R6, `wave_gate_check.py`, architecture-freshness behavior, reviewer authority, or test verdict semantics.
- Do not add a framework, start services, merge, or push.
- This packet may update stale gate prose but must not claim that a local result is a remote GitHub Actions run.

---

## Task 1: Pin the fixed regression-runner behavior

**Files:**

- Create: `tests/unit/test_regression_pin_runner.py`
- Create: `scripts/run_regression_pins.py`

- [ ] Write tests against this interface:

```python
PYTEST_ARGS = ("-m", "pytest", "tests/unit", "--runxfail", "-q")

def pytest_argv(python: str | None = None) -> tuple[str, ...]:
    return (python or sys.executable, *PYTEST_ARGS)

def main() -> int:
    completed = subprocess.run(pytest_argv(), cwd=ROOT, check=False)
    return completed.returncode
```

The tests must assert:

1. `pytest_argv("/synthetic/python")` equals `("/synthetic/python", "-m", "pytest", "tests/unit", "--runxfail", "-q")` exactly;
2. `main()` calls `subprocess.run` once with `pytest_argv()`, `cwd` equal to repository root, and no `shell=True`;
3. `main()` returns the subprocess return code unchanged for both 0 and a nonzero synthetic code.

- [ ] Run before implementation:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit/test_regression_pin_runner.py -q
```

Expected: collection FAIL because `run_regression_pins.py` does not exist.

- [ ] Implement the runner with only standard-library imports. Use `sys.executable`, never a bare `python` lookup inside the runner, and call:

```python
completed = subprocess.run(pytest_argv(), cwd=ROOT, check=False)
return completed.returncode
```

Use the ordinary `if __name__ == "__main__": raise SystemExit(main())` guard. Do not accept CLI targets or arbitrary extra arguments.

- [ ] Re-run the unit test. Expected: all three runner contracts pass.

## Task 2: Make R4 validate the exact runner contract

**Files:**

- Modify: `tests/unit/test_ceremony_gates.py`
- Modify: `scripts/check_no_ceremony.py`

- [ ] Refactor R4 around two pure helpers:

```python
RUNNER_WORKFLOW_LINE = "run: python scripts/run_regression_pins.py"
EXPECTED_RUNNER_ARGS = ("-m", "pytest", "tests/unit", "--runxfail", "-q")

def _workflow_invokes_regression_runner(text: str) -> bool:
    return any(
        line.strip() == RUNNER_WORKFLOW_LINE
        for line in text.splitlines()
        if not line.lstrip().startswith("#")
    )

def _runner_contract_is_executable(path: pathlib.Path) -> bool:
    try:
        spec = importlib.util.spec_from_file_location("_regression_pin_runner", path)
        if spec is None or spec.loader is None:
            return False
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return tuple(module.pytest_argv("/synthetic/python")) == (
            "/synthetic/python", *EXPECTED_RUNNER_ARGS
        )
    except (AttributeError, ImportError, OSError, SyntaxError, TypeError):
        return False
```

`_runner_contract_is_executable` loads the fixed local module without invoking `main`, calls `pytest_argv("/synthetic/python")`, and accepts only `("/synthetic/python", *EXPECTED_RUNNER_ARGS)`. Catch syntax/import/attribute/type errors and return `False`; R4 must fail cleanly rather than crash.

- [ ] Add positive tests for the exact single-line `run:` invocation and the actual runner file.

- [ ] Add separate negative tests proving each of these texts returns `False`:

```yaml
# run: python scripts/run_regression_pins.py
- name: python scripts/run_regression_pins.py
run: echo --runxfail
run: python scripts/other.py --runxfail
run: >-
  python scripts/run_regression_pins.py
```

The folded multiline case is intentionally rejected because the contract requires one exact, reviewable line.

- [ ] Add a test with a temporary fake runner whose `pytest_argv` omits `--runxfail`; `_runner_contract_is_executable` must return `False`.

- [ ] Run the new R4 tests before changing production code:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit/test_ceremony_gates.py -k 'runner or r4' -q
```

Expected: FAIL because the pure helpers do not exist and R4 currently accepts any `--runxfail` substring.

- [ ] Replace `rule_ci_runs_runxfail`'s substring search. It passes only when at least one workflow has the exact invocation and the canonical `scripts/run_regression_pins.py` contract is executable. Its failure evidence must distinguish `workflow invocation missing` from `runner contract invalid`.

- [ ] Update the module's R4 description to name the fixed runner rather than a raw marker string. Leave R3 unchanged even though its separate detector has known limitations; that belongs to a different remediation route.

- [ ] Re-run all ceremony and runner tests:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest \
  tests/unit/test_ceremony_gates.py \
  tests/unit/test_regression_pin_runner.py -q
```

Expected: all selected tests pass, including every negative spoof case.

## Task 3: Wire the runner and omitted checklist suite into CI

**Files:**

- Modify: `.github/workflows/ci.yml`

- [ ] Replace the existing raw pytest `--runxfail` step with exactly:

```yaml
- name: Execute strict-xfail regression pins
  run: python scripts/run_regression_pins.py
```

The `run:` line must remain a single line and byte-exact after indentation is stripped. Remove comments that themselves advertise `--runxfail`; the runner owns that detail.

- [ ] Add this exact path to the `import-hermetic` folded pytest command:

```text
import/tests/test_checklist_coverage_unit.py
```

Keep every Packet 3 hermetic suite already present. Update the lane comment to enumerate the full file list instead of saying `five`.

- [ ] Run the fixed runner directly:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/run_regression_pins.py
```

Expected: exit 0; pytest's final summary shows the `tests/unit` suite executed under `--runxfail`.

- [ ] Run the checklist suite directly:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_checklist_coverage_unit.py -q
```

Expected: 13 passed.

- [ ] Run the exact final hermetic import command copied from the edited workflow. Expected: exit 0 and no DB connection. Do not substitute `pytest import/tests` because that includes live-DSN files.

## Task 4: Update truthful gate and lane documentation

**Files:**

- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`

- [ ] Collect the final unit and hermetic lane inventories with the exact workflow targets:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest --collect-only -q tests/unit
```

Then run the exact folded import-hermetic target list from `.github/workflows/ci.yml` with `--collect-only -q`.

Expected: each exits 0 with one final `N tests collected` line where `N` is an integer. Use those emitted integers in docs; do not reuse a pre-packet count.

- [ ] In `ARCHITECTURE.md`, update both `*Last verified:*` lines to `2026-07-21 @ ` followed by the exact value of `EVIDENCE_LEDGER_PACKET_PARENT_SHA`. Update the CI and governance sections to state:

  - `pytest-unit` invokes `scripts/run_regression_pins.py`;
  - the runner executes the fixed `tests/unit --runxfail` command;
  - R4 requires the exact workflow invocation plus the runner argv contract;
  - comments, step names, folded commands, and unrelated strings do not satisfy R4;
  - import-hermetic includes checklist coverage; and
  - architecture freshness itself was not changed.

- [ ] In `OPERATIONS.md`, replace raw `pytest tests/unit --runxfail` instructions that claim to satisfy R4 with `python scripts/run_regression_pins.py`. Update the hermetic file list/count and the gate table. Keep direct pytest commands only when described as diagnostic, not as the structural R4 witness.

- [ ] Repair and verify anchors and freshness:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py --fix
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py OPERATIONS.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_arch_freshness.py --base "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"
```

Expected: all three commands exit 0; no architecture mechanism file changes.

## Task 5: Run the complete gate profile and commit

**Files:**

- Verify all changed files, then commit them explicitly.

- [ ] Run focused and complete governance checks:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest \
  tests/unit/test_ceremony_gates.py \
  tests/unit/test_regression_pin_runner.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/run_regression_pins.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/check_no_ceremony.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_checklist_coverage_unit.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/ci_smoke.py
```

Expected: both pytest invocations pass; the runner returns 0; R4 prints PASS for the fixed runner; checklist coverage reports 13 passed; smoke ends in `OK`.

- [ ] Inspect scope and formatting:

```bash
env -u GIT_INDEX_FILE git diff --check "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD
env -u GIT_INDEX_FILE git diff --name-only "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD
env -u GIT_INDEX_FILE git status --short --branch
```

Expected before commit: only the seven paths named in this plan are modified/created, plus no `.vscode/` change.

- [ ] Commit with explicit pathspecs:

```bash
env -u GIT_INDEX_FILE git add \
  scripts/run_regression_pins.py scripts/check_no_ceremony.py \
  tests/unit/test_regression_pin_runner.py tests/unit/test_ceremony_gates.py \
  .github/workflows/ci.yml ARCHITECTURE.md OPERATIONS.md
env -u GIT_INDEX_FILE git commit -m "fix(ci): require executable regression evidence"
```

Expected: one commit containing exactly seven paths.

- [ ] Re-run smoke and `git diff --check "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD` after commit. Expected: `OK`, silent diff check, clean worktree.

## Task 6: Request review and stop at the side-effect boundary

**Files:**

- No new files.

- [ ] Publish an immutable verify-request assigning non-author Operator2. Name separate finding references for checklist CI execution, exact workflow invocation, runner argv, runner subprocess behavior, comment spoof, step-name spoof, unrelated-string spoof, folded-command rejection, and unchanged architecture-freshness behavior.

- [ ] Require Operator2 to run the exact committed runner and the negative R4 unit tests against the actual range. A generic smoke-only review is insufficient for this packet.

- [ ] Stop after GO/NITS/FAIL reconciliation. Do not integrate, merge, push, or claim remote CI execution without separate authority and evidence.
