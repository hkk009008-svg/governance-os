# R1 Codebase Analysis & Modernization Plan

## Overview
This report provides a comprehensive analysis of the AGY (Antigravity) launcher and runtime identity infrastructure (`scripts/agy_protocol_model.py`, `scripts/agy_seat_launcher.py`, and `coordination/bin/agy-seat`) as part of Milestone 1 (R1 Codebase Analysis) for AGY Protocol Modernization.

The objective of R1 refactoring is to transition AGY seat launchers from a legacy advisory posture (which blocked direct execution unless explicit `--mode single-model-autonomous` or `--dry-run` flags were provided) to a first-class autonomous operation posture by default.

---

## 1. Inventory & Codebase Examination

### A. `coordination/bin/agy-seat`
- **File Path**: `/Users/hyungkoookkim/Pipeline/coordination/bin/agy-seat`
- **Lines**: 6
- **Implementation**:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail

  ROOT=$(cd "$(dirname "$0")/../.." && pwd)
  exec /usr/bin/env python3 "$ROOT/scripts/agy_seat_launcher.py" "$@"
  ```
- **Behavior**: Forwarding script that delegates argument parsing and execution directly to `scripts/agy_seat_launcher.py`. Any restriction or default value in `agy_seat_launcher.py` directly impacts `agy-seat`.

### B. `scripts/agy_protocol_model.py`
- **File Path**: `/Users/hyungkoookkim/Pipeline/scripts/agy_protocol_model.py`
- **Lines**: 41
- **Key Definitions**:
  - `ADVISORY_MODE = "advisory"` (Line 7)
  - `SINGLE_MODEL_MODE = "single-model-autonomous"` (Line 8)
  - `MODES = (ADVISORY_MODE, SINGLE_MODEL_MODE)` (Line 9)
- **`infer_runtime_env` Function Signature**:
  ```python
  def infer_runtime_env(*, profile: str, mode: str, index_path: str) -> dict[str, str]:
  ```
  - **Issue**: `mode` parameter is required without default value. When `mode == ADVISORY_MODE`, it generates advisory readiness environment values (`AGY_SEAT: "agy-advisory"`, `AGY_AGENT_MODE: "advisory-readiness"`). When `mode == SINGLE_MODEL_MODE`, it generates autonomous seat identity (`AGY_SEAT: "agy-unit-{profile}"`, `AGY_AGENT_MODE: "single-model-autonomous"`).

### C. `scripts/agy_seat_launcher.py`
- **File Path**: `/Users/hyungkoookkim/Pipeline/scripts/agy_seat_launcher.py`
- **Lines**: 386
- **Key Sections**:
  1. **`build_launch_spec`** (Lines 112-160):
     - Line 121: `mode: str = ADVISORY_MODE` parameter default.
     - Calls `infer_runtime_env(profile=seat, mode=mode, index_path=str(index_path))`.
  2. **`_parse_args`** (Lines 295-325):
     - Lines 309-317:
       ```python
       parser.add_argument(
           "--mode",
           choices=MODES,
           default=ADVISORY_MODE,
           help=(
               "AGY posture: advisory is dry-run/readiness only; "
               "single-model-autonomous is an explicit independent-unit mode"
           ),
       )
       ```
     - **Issue**: Default value for `--mode` is `ADVISORY_MODE`.
  3. **Posture Restriction Error Block in `main()`** (Lines 334-338):
     ```python
     if not args.dry_run and args.mode != SINGLE_MODEL_MODE:
         raise LaunchError(
             "advisory mode does not launch AGY; use --dry-run or explicitly "
             "select --mode single-model-autonomous for an independent unit"
         )
     ```
     - **Issue**: When invoked directly as `coordination/bin/agy-seat director`, `args.dry_run` is `False` and `args.mode` defaults to `ADVISORY_MODE`. This check triggers, raising `LaunchError` and exiting with status `2`.

---

## 2. Root Cause Analysis: Why Direct Launch Fails by Default

1. **Default Mode Setting**: `_parse_args` in `agy_seat_launcher.py` defaults `--mode` to `ADVISORY_MODE` ("advisory").
2. **Mandatory Mode Restriction**: `main()` in `agy_seat_launcher.py` contains an explicit error guard (lines 334-338) refusing process launch when `args.mode != SINGLE_MODEL_MODE` unless `--dry-run` is specified.
3. **Execution Failure**: Calling `coordination/bin/agy-seat director` produces:
   `agy-seat: advisory mode does not launch AGY; use --dry-run or explicitly select --mode single-model-autonomous for an independent unit` (exit status code 2).

---

## 3. Step-by-Step Refactoring Plan (R1 Implementation)

### Step 3.1: Update `scripts/agy_protocol_model.py`
- Add default parameter `mode: str = SINGLE_MODEL_MODE` to `infer_runtime_env`.
- Ensure calling `infer_runtime_env(profile="director", index_path="...")` produces single-model autonomous identity by default.

### Step 3.2: Update `scripts/agy_seat_launcher.py`
- In `build_launch_spec`: change default parameter to `mode: str = SINGLE_MODEL_MODE`.
- In `_parse_args`: change argparse default to `default=SINGLE_MODEL_MODE`.
- In `main()`: **remove** the posture restriction error block (lines 334-338).
- Retain argument `--mode` for optional explicit overrides if needed, but ensure default behavior for all launches is `SINGLE_MODEL_MODE`.

### Step 3.3: Update `scripts/agy_emit.py`
- In line 132: update auto-routing dispatch command string from `.venv/bin/python scripts/agy_seat_launcher.py {args.to} --mode single-model-autonomous` to `coordination/bin/agy-seat {args.to}` or `.venv/bin/python scripts/agy_seat_launcher.py {args.to}` without redundant `--mode` flag.

### Step 3.4: Align Unit Tests (`tests/unit/test_agy_*.py`)
- **`tests/unit/test_agy_seat_launcher.py`**:
  - Update `test_build_launch_spec_defaults_to_advisory_agy_identity_and_cleans_authority`: rename to `test_build_launch_spec_defaults_to_single_model_autonomous_and_cleans_authority`, assert `spec.env["AGY_SEAT"] == "agy-unit-director"`, `spec.env["AGY_AGENT_MODE"] == launcher.SINGLE_MODEL_MODE`.
  - Update `test_dry_run_does_not_create_index_or_start_agy`: assert payload `AGY_SEAT == "agy-unit-director"`, `AGY_AGENT_MODE == "single-model-autonomous"`.
  - Replace `test_default_advisory_mode_refuses_provider_launch` with a test verifying that default launcher invocation (`main(["--config", ..., "director"])`) attempts `ensure_seat_index` and `os.execvpe` rather than failing with advisory posture error.
- **`tests/unit/test_agy_protocol_model.py`**:
  - Add test verifying default `infer_runtime_env` call (without `mode`) defaults to `SINGLE_MODEL_MODE`.

---

## 4. Expected Behavior Verification Matrix

| Launch Command | Default Mode | `AGY_SEAT` Identity | Action | Exit Code |
|----------------|--------------|----------------------|--------|-----------|
| `coordination/bin/agy-seat director` | `single-model-autonomous` | `agy-unit-director` | Seed index `.git/index-agy-director`, `os.execvpe` launcher binary | 0 (on exec) |
| `coordination/bin/agy-seat --dry-run director` | `single-model-autonomous` | `agy-unit-director` | Print JSON launch spec to stdout | 0 |
| `coordination/bin/agy-seat --mode advisory --dry-run director` | `advisory` | `agy-advisory` | Print advisory JSON launch spec to stdout | 0 |

---

## 5. Non-Regression Scope
- Non-AGY providers (Codex, Claude, Cursor) are isolated in separate launcher binaries (`codex-seat`, `claude-seat`, etc.) and adaptors.
- `tests/unit/test_provider_protocol_isolation.py` validates that `AGY_*` environment variables do not leak into Codex runtime identity.
