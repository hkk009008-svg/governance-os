# Handoff Report — Explorer 3 (Milestone 1 / R3 Unit Test & CI Suite Analysis)

## 1. Observation

- **Observation 1 (Unit Test Files)**: Located 4 AGY-specific unit test files (`tests/unit/test_agy_agent_surfaces.py`, `tests/unit/test_agy_emit.py`, `tests/unit/test_agy_protocol_model.py`, `tests/unit/test_agy_seat_launcher.py`) and 1 cross-provider isolation test (`tests/unit/test_provider_protocol_isolation.py`).
- **Observation 2 (`test_agy_protocol_model.py` Line 8-21)**:
  ```python
  def test_advisory_runtime_is_agy_named_and_has_no_shared_seat_identity() -> None:
      values = protocol.infer_runtime_env(
          profile="director",
          mode=protocol.ADVISORY_MODE,
          index_path="/repo/.git/index-agy-director",
      )
      assert values == {
          "AGY_SEAT": "agy-advisory",
          "AGY_AGENT_MODE": "advisory-readiness",
          "AGY_AGENT_ROLE": "readiness-bridge",
          "AGY_BEHAVIOR_SOURCE": "advisory-read-only",
          "AGY_GIT_INDEX_FILE": "/repo/.git/index-agy-director",
      }
  ```
- **Observation 3 (`test_agy_seat_launcher.py` Line 32-75)**:
  `test_build_launch_spec_defaults_to_advisory_agy_identity_and_cleans_authority()` asserts that calling `launcher.build_launch_spec()` without explicit `mode` sets:
  ```python
  assert spec.env["AGY_SEAT"] == "agy-advisory"
  assert spec.env["AGY_AGENT_MODE"] == "advisory-readiness"
  assert spec.env["AGY_AGENT_ROLE"] == "readiness-bridge"
  assert spec.env["AGY_BEHAVIOR_SOURCE"] == "advisory-read-only"
  ```
- **Observation 4 (`test_agy_seat_launcher.py` Line 554-578)**:
  `test_default_advisory_mode_refuses_provider_launch()` asserts that direct execution without `--mode single-model-autonomous` or `--dry-run` exits with code 2:
  ```python
  assert launcher.main(["--config", str(config_path), "director"]) == 2
  assert "advisory mode does not launch AGY" in capsys.readouterr().err
  ```
- **Observation 5 (`test_agy_seat_launcher.py` Line 490-552)**:
  `test_dry_run_does_not_create_index_or_start_agy()` asserts `payload["env"]["AGY_SEAT"] == "agy-advisory"` and `payload["env"]["AGY_AGENT_MODE"] == "advisory-readiness"`.
- **Observation 6 (`scripts/ci_smoke.py`)**:
  Executed `.venv/bin/python scripts/ci_smoke.py --fast` and `.venv/bin/python scripts/ci_smoke.py`. Both executed successfully with returncode 0 (`PROJECT SMOKE — governance-OS runtime invariants ... OK`, `FAST PREFLIGHT — PASS`, `GO-SCHEMA CHECK — PASS`, `MECHANISM-LEDGER CHECK — PASS`, `OK`).

---

## 2. Logic Chain

1. **Step 1 (From Observations 1 & 2)**: `test_agy_protocol_model.py` explicitly tests `infer_runtime_env` under `ADVISORY_MODE`. When default mode is changed to `SINGLE_MODEL_MODE` (`single-model-autonomous`), `infer_runtime_env` will return autonomous identity (`AGY_SEAT="agy-unit-director"`), causing this test to fail unless updated.
2. **Step 2 (From Observation 3)**: `test_build_launch_spec_defaults_to_advisory_agy_identity_and_cleans_authority` in `test_agy_seat_launcher.py` asserts that `build_launch_spec` defaults to `AGY_SEAT="agy-advisory"`. When R1 sets default mode to `SINGLE_MODEL_MODE`, `build_launch_spec` will default to `AGY_SEAT="agy-unit-director"`, breaking this assertion.
3. **Step 3 (From Observation 4)**: `test_default_advisory_mode_refuses_provider_launch` asserts that running `launcher.main` without flags returns exit code 2. When R1 removes the posture restriction block from `agy_seat_launcher.py`, direct launches will succeed, so this test will fail unless replaced with `test_direct_autonomous_mode_launches_provider`.
4. **Step 4 (From Observation 5)**: `test_dry_run_does_not_create_index_or_start_agy` asserts that `--dry-run` outputs `AGY_SEAT="agy-advisory"`. After R1, `--dry-run` will output `AGY_SEAT="agy-unit-director"`, requiring assertion updates.
5. **Step 5 (From Observation 6)**: `scripts/ci_smoke.py` relies on general governance OS runtime invariants, ceremony rules, placeholder allowlists, and report schemas. It has no hardcoded dependency on AGY advisory posture flags. Therefore, updating AGY launcher and protocol models to default autonomous operation will maintain 100% pass rates across `ci_smoke.py` and non-AGY provider test suites (`test_provider_protocol_isolation.py`, `test_codex_seat_launcher.py`, etc.).

---

## 3. Caveats

- **Scope Limit**: Read-only exploration. No source code or test file modifications were performed in this phase.
- **Dependency Order**: Updating test assertions in `tests/unit/test_agy_*.py` must occur in Milestone 4 (R3) in conjunction with or after Milestone 2 (R1 protocol model & launcher changes) and Milestone 3 (R2 documentation changes).

---

## 4. Conclusion

The unit test suite and CI smoke runner have been thoroughly analyzed:
- 5 specific test functions in `test_agy_protocol_model.py` and `test_agy_seat_launcher.py` explicitly lock in legacy advisory posture behavior and must be updated to validate direct autonomous operation.
- `scripts/ci_smoke.py` is fully provider-agnostic and will pass cleanly without modification once unit tests are aligned.
- All required test updates and verification commands have been fully formulated and documented in `/Users/hyungkoookkim/Pipeline/.agents/explorer_m1_3/analysis_r3.md`.

---

## 5. Verification Method

To verify the test alignment plan and current baseline:

1. **Current Pytest Unit Baseline**:
   ```bash
   .venv/bin/pytest tests/unit/test_agy_agent_surfaces.py tests/unit/test_agy_emit.py tests/unit/test_agy_protocol_model.py tests/unit/test_agy_seat_launcher.py tests/unit/test_provider_protocol_isolation.py
   ```
   *Expected result*: 35 passed in `test_agy_*.py` under current legacy behavior.

2. **CI Smoke Baseline**:
   ```bash
   .venv/bin/python scripts/ci_smoke.py --fast
   .venv/bin/python scripts/ci_smoke.py
   ```
   *Expected result*: Exit code 0 with `FAST PREFLIGHT — PASS` and `OK`.

3. **Analysis Document Inspection**:
   Inspect `/Users/hyungkoookkim/Pipeline/.agents/explorer_m1_3/analysis_r3.md` to review the precise line-by-line test modification mapping.
