# Handoff Report — Milestone 1 (R1 Codebase Analysis)

## 1. Observation

Direct examination of the AGY protocol launcher files and unit tests yielded the following specific observations:

1. **`coordination/bin/agy-seat` (lines 1-6)**:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail

   ROOT=$(cd "$(dirname "$0")/../.." && pwd)
   exec /usr/bin/env python3 "$ROOT/scripts/agy_seat_launcher.py" "$@"
   ```
   Direct execution delegates directly to `scripts/agy_seat_launcher.py`.

2. **`scripts/agy_protocol_model.py` (lines 7-16, 23-40)**:
   - Line 7: `ADVISORY_MODE = "advisory"`
   - Line 8: `SINGLE_MODEL_MODE = "single-model-autonomous"`
   - Line 16: `def infer_runtime_env(*, profile: str, mode: str, index_path: str) -> dict[str, str]:`
   - `infer_runtime_env` requires `mode` without a default value. When `mode == ADVISORY_MODE`, returns `{"AGY_SEAT": "agy-advisory", "AGY_AGENT_MODE": "advisory-readiness", ...}`. When `mode == SINGLE_MODEL_MODE`, returns `{"AGY_SEAT": "agy-unit-" + profile, "AGY_AGENT_MODE": "single-model-autonomous", ...}`.

3. **`scripts/agy_seat_launcher.py` (lines 121, 309-317, 334-338)**:
   - Line 121: `build_launch_spec(..., *, mode: str = ADVISORY_MODE)` sets default `mode` to `ADVISORY_MODE`.
   - Lines 312: `_parse_args` sets `default=ADVISORY_MODE` for `--mode`.
   - Lines 334-338:
     ```python
     if not args.dry_run and args.mode != SINGLE_MODEL_MODE:
         raise LaunchError(
             "advisory mode does not launch AGY; use --dry-run or explicitly "
             "select --mode single-model-autonomous for an independent unit"
         )
     ```
   - Running `coordination/bin/agy-seat director` triggers this error block, writing `agy-seat: advisory mode does not launch AGY...` to stderr and returning exit code `2`.

4. **`tests/unit/test_agy_seat_launcher.py` (lines 32-86, 540-579)**:
   - `test_build_launch_spec_defaults_to_advisory_agy_identity_and_cleans_authority` (lines 32-86) asserts `spec.env["AGY_SEAT"] == "agy-advisory"`.
   - `test_dry_run_does_not_create_index_or_start_agy` (lines 540-552) asserts `payload["env"]["AGY_SEAT"] == "agy-advisory"`.
   - `test_default_advisory_mode_refuses_provider_launch` (lines 554-579) asserts exit code `2` when calling `main(["--config", ..., "director"])`.

---

## 2. Logic Chain

1. **Observation 1 & 3** show that invoking `coordination/bin/agy-seat director` runs `scripts/agy_seat_launcher.py` with default arguments (`args.dry_run = False`, `args.mode = "advisory"`).
2. **Observation 3** shows that lines 334-338 of `scripts/agy_seat_launcher.py` explicitly check `if not args.dry_run and args.mode != SINGLE_MODEL_MODE:` and raise a `LaunchError`.
3. **Observation 2 & 3** show that both `infer_runtime_env` and `build_launch_spec` default to or require `ADVISORY_MODE`, preventing autonomous seat initialization (`agy-unit-{profile}`).
4. **Observation 4** shows that unit tests in `tests/unit/test_agy_seat_launcher.py` explicitly check for and lock in this legacy advisory posture behavior.
5. Therefore, enabling direct first-class autonomous operation by default requires:
   - Setting default `mode` to `SINGLE_MODEL_MODE` in `scripts/agy_protocol_model.py` and `scripts/agy_seat_launcher.py`.
   - Removing the posture restriction block (lines 334-338) in `scripts/agy_seat_launcher.py`.
   - Updating unit tests in `tests/unit/test_agy_seat_launcher.py` to assert autonomous identity defaults.

---

## 3. Caveats

- **Scope Limit**: This report covers R1 Codebase Analysis (`scripts/agy_protocol_model.py`, `scripts/agy_seat_launcher.py`, `coordination/bin/agy-seat`). Document & harness skill refactoring (R2) and test suite alignment execution (R3) are handled in separate subtasks/milestones.
- **Provider Isolation**: All changes are strictly contained within `agy_*` scripts and `coordination/bin/agy-seat`. Non-AGY providers (Codex, Claude, Cursor) are unaffected.

---

## 4. Conclusion

R1 Codebase Analysis is complete. The root causes blocking direct execution of `coordination/bin/agy-seat director` have been identified in `scripts/agy_seat_launcher.py` (lines 121, 312, 334-338) and `scripts/agy_protocol_model.py` (line 16).

A 4-step refactoring plan has been established in `/Users/hyungkoookkim/Pipeline/.agents/explorer_m1_1/analysis_r1.md`.

---

## 5. Verification Method

To verify the analysis and refactoring plan independently:

1. **Inspect Analysis Report**:
   Read `/Users/hyungkoookkim/Pipeline/.agents/explorer_m1_1/analysis_r1.md`.

2. **Verify Current Failure Mode**:
   Run `.venv/bin/python scripts/agy_seat_launcher.py director` (or `.venv/bin/pytest tests/unit/test_agy_seat_launcher.py -k test_default_advisory_mode_refuses_provider_launch`). Confirm it currently exits with code 2 and outputs `advisory mode does not launch AGY`.

3. **Verify Target Behavior After Refactoring**:
   - `coordination/bin/agy-seat --dry-run director` should print JSON payload with `"AGY_SEAT": "agy-unit-director"` and `"AGY_AGENT_MODE": "single-model-autonomous"`.
   - `.venv/bin/pytest tests/unit/test_agy_*.py` should pass 100% cleanly.
