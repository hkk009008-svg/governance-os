# Handoff Report — Challenger M2-1 (Milestone 2 R1 Empirical Verification)

## 1. Observation

Direct empirical execution was performed on `coordination/bin/agy-seat` and `scripts/agy_seat_launcher.py`:

1. **Task 1: Direct Launch Director (`coordination/bin/agy-seat --dry-run director`)**:
   - Exit code: `0`
   - Parsed JSON output:
     ```json
     {
       "argv": [
         "agy",
         "--model",
         "gemini-2.5-pro",
         "--config",
         "service_tier=\"default\"",
         "--cd",
         "/Users/hyungkoookkim/Pipeline"
       ],
       "env": {
         "AGY_AGENT_MODE": "single-model-autonomous",
         "AGY_AGENT_ROLE": "agy-unit-director",
         "AGY_BEHAVIOR_SOURCE": "agy-unit-director",
         "AGY_GIT_INDEX_FILE": "/Users/hyungkoookkim/Pipeline/.git/index-agy-director",
         "AGY_SEAT": "agy-unit-director",
         "GIT_INDEX_FILE": "/Users/hyungkoookkim/Pipeline/.git/index-agy-director"
       },
       "index_exists": true
     }
     ```
   - `"AGY_SEAT"` verified as `"agy-unit-director"`.
   - `"AGY_AGENT_MODE"` verified as `"single-model-autonomous"`.

2. **Task 2: Direct Launch Operator (`.venv/bin/python scripts/agy_seat_launcher.py --dry-run operator`)**:
   - Exit code: `0`
   - Parsed JSON output:
     ```json
     {
       "argv": [
         "agy",
         "--model",
         "gemini-2.5-pro",
         "--config",
         "service_tier=\"default\"",
         "--cd",
         "/Users/hyungkoookkim/Pipeline"
       ],
       "env": {
         "AGY_AGENT_MODE": "single-model-autonomous",
         "AGY_AGENT_ROLE": "agy-unit-operator",
         "AGY_BEHAVIOR_SOURCE": "agy-unit-operator",
         "AGY_GIT_INDEX_FILE": "/Users/hyungkoookkim/Pipeline/.git/index-agy-operator",
         "AGY_SEAT": "agy-unit-operator",
         "GIT_INDEX_FILE": "/Users/hyungkoookkim/Pipeline/.git/index-agy-operator"
       },
       "index_exists": true
     }
     ```
   - `"AGY_SEAT"` verified as `"agy-unit-operator"`.
   - `"AGY_AGENT_MODE"` verified as `"single-model-autonomous"`.

3. **Task 3: Direct Launch Coordinator (`coordination/bin/agy-seat --dry-run coordinator`)**:
   - Exit code: `0`
   - Parsed JSON output:
     ```json
     {
       "argv": [
         "agy",
         "--model",
         "gemini-2.5-flash",
         "--config",
         "service_tier=\"fast\"",
         "--cd",
         "/Users/hyungkoookkim/Pipeline"
       ],
       "env": {
         "AGY_AGENT_MODE": "single-model-autonomous",
         "AGY_AGENT_ROLE": "agy-unit-coordinator",
         "AGY_BEHAVIOR_SOURCE": "agy-unit-coordinator",
         "AGY_GIT_INDEX_FILE": "/Users/hyungkoookkim/Pipeline/.git/index-agy-coordinator",
         "AGY_SEAT": "agy-unit-coordinator",
         "GIT_INDEX_FILE": "/Users/hyungkoookkim/Pipeline/.git/index-agy-coordinator"
       },
       "index_exists": true
     }
     ```
   - Exit code 0 verified.

4. **Task 4: Edge Cases & Error Handling**:
   - Invalid profile (`coordination/bin/agy-seat --dry-run invalid_seat`): Exit code `2`, stderr output `agy_seat_launcher.py: error: argument seat: invalid choice: 'invalid_seat'`.
   - Invalid mode (`.venv/bin/python scripts/agy_seat_launcher.py --mode invalid-mode --dry-run director`): Exit code `2`, stderr output `agy_seat_launcher.py: error: argument --mode: invalid choice: 'invalid-mode'`.
   - Missing config file (`coordination/bin/agy-seat --config non_existent_file.toml --dry-run director`): Exit code `2`, stderr output `agy-seat: cannot load seat config non_existent_file.toml...`.
   - Invalid option flag (`coordination/bin/agy-seat --invalid-option director`): Exit code `2`, stderr output `agy_seat_launcher.py: error: unrecognized arguments: --invalid-option`.
   - Explicit advisory mode (`coordination/bin/agy-seat --mode advisory --dry-run director`): Exit code `0`, output `"AGY_SEAT": "agy-advisory"`.
   - Argument forwarding (`coordination/bin/agy-seat --dry-run director -- --foo bar`): Exit code `0`, `argv` contains `"--foo"` and `"bar"`.

5. **Unit Tests & Smoke Verification**:
   - `.venv/bin/pytest tests/unit/test_agy_*.py tests/unit/test_provider_protocol_isolation.py`: 125 passed in 0.88s.
   - `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`: Exit code `0`, all invariants passed.

## 2. Logic Chain

1. Executing dry-run invocations across `director`, `operator`, and `coordinator` profiles proved that default launch behavior resolves to `single-model-autonomous` mode and assigns per-profile seat identities (`agy-unit-{profile}`).
2. Negative testing with invalid profiles, invalid modes, missing configs, and bad flags confirmed that error boundaries handle invalid input safely, returning exit code 2 without unhandled exceptions.
3. Regression test suite execution (125 tests) and system smoke script (`ci_smoke.py`) confirmed that protocol invariants remain fully intact.

## 3. Caveats

- **Network / Live Execution**: Live invocation of the AGY binary (`agy`) against remote endpoints was not executed during dry-run empirical verification.
- **Provider Scope**: Verification was restricted to AGY protocol components.

## 4. Conclusion

Empirical verification for Milestone 2 (R1 Direct Launch Empirical Challenger) is **COMPLETE with FULL PASS**.
- `coordination/bin/agy-seat` and `scripts/agy_seat_launcher.py` operate accurately under default direct launch.
- All JSON environment outputs and seat identities match protocol specifications.
- Error handling behavior for edge cases is verified.

## 5. Verification Method

To re-verify independently:

```bash
# 1. Test director dry-run
coordination/bin/agy-seat --dry-run director

# 2. Test operator dry-run via Python launcher
.venv/bin/python scripts/agy_seat_launcher.py --dry-run operator

# 3. Test coordinator dry-run
coordination/bin/agy-seat --dry-run coordinator

# 4. Test error handling
coordination/bin/agy-seat --dry-run invalid_seat

# 5. Run test suite & smoke script
.venv/bin/pytest tests/unit/test_agy_*.py tests/unit/test_provider_protocol_isolation.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```
