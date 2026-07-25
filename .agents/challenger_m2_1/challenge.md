# Adversarial Challenge Report — Challenger M2-1

## Challenge Summary

**Overall risk assessment**: LOW

Empirical testing confirmed that `coordination/bin/agy-seat` and `scripts/agy_seat_launcher.py` operate robustly in default `single-model-autonomous` mode. Output identity maps to `agy-unit-{profile}`, environment isolation is preserved, error handling is clean (exit code 2 on validation failure), and backward compatibility for explicit `--mode advisory` is fully functional.

---

## Challenges

### [Low] Challenge 1: Posture & Identity Default Change

- **Assumption challenged**: Shifting the default `mode` to `single-model-autonomous` in `infer_runtime_env` and `agy_seat_launcher.py` could break advisory readiness checks or create identity collision across seats.
- **Attack scenario**: Executing direct launcher calls for different profiles (`director`, `operator`, `coordinator`) with default parameters to inspect identity output and testing explicit `--mode advisory`.
- **Blast radius**: Low. Identity is cleanly namespaced to `agy-unit-{profile}` per profile. Explicit `--mode advisory` remains supported.
- **Mitigation**: Verified JSON dry-run output across all profiles and verified `--mode advisory` behavior.

### [Low] Challenge 2: Invalid Input & Error Boundary Handling

- **Assumption challenged**: Malformed options, unsupported profiles, or missing configuration files might cause unhandled exceptions or invalid state transitions.
- **Attack scenario**: Executing launcher with unsupported seat profile (`invalid_seat`), unsupported mode (`invalid-mode`), missing TOML config file (`non_existent_file.toml`), and invalid CLI options (`--invalid-option`).
- **Blast radius**: Low. All validation errors are caught and printed to stderr with process exit code 2.
- **Mitigation**: Empirically confirmed all error cases exit cleanly with code 2 and helpful usage/error messages.

### [Low] Challenge 3: Argument Forwarding & Passthrough

- **Assumption challenged**: Extra CLI options passed after `--` boundary might be misparsed or swallowed by the launcher parser.
- **Attack scenario**: Invoking `coordination/bin/agy-seat --dry-run director -- --foo bar`.
- **Blast radius**: Low. Parser splits args at `--` correctly.
- **Mitigation**: Empirically verified forwarded flags appear in `spec.argv`.

---

## Stress Test Results

| Scenario | Command | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|
| Direct Launch Director | `coordination/bin/agy-seat --dry-run director` | Exit 0, `"AGY_SEAT": "agy-unit-director"`, `"AGY_AGENT_MODE": "single-model-autonomous"` | Exit 0, JSON matched expected keys exactly | PASS |
| Direct Launch Operator | `.venv/bin/python scripts/agy_seat_launcher.py --dry-run operator` | Exit 0, `"AGY_SEAT": "agy-unit-operator"`, `"AGY_AGENT_MODE": "single-model-autonomous"` | Exit 0, JSON matched expected keys exactly | PASS |
| Direct Launch Coordinator | `coordination/bin/agy-seat --dry-run coordinator` | Exit 0, `"AGY_SEAT": "agy-unit-coordinator"`, `"AGY_AGENT_MODE": "single-model-autonomous"` | Exit 0, JSON matched expected keys exactly | PASS |
| Invalid Seat Profile | `coordination/bin/agy-seat --dry-run invalid_seat` | Exit 2, error: invalid choice | Exit 2, error message printed cleanly | PASS |
| Invalid Mode Choice | `.venv/bin/python scripts/agy_seat_launcher.py --mode invalid-mode --dry-run director` | Exit 2, error: invalid choice | Exit 2, error message printed cleanly | PASS |
| Missing Config File | `coordination/bin/agy-seat --config non_existent_file.toml --dry-run director` | Exit 2, error: cannot load seat config | Exit 2, `agy-seat: cannot load seat config...` | PASS |
| Invalid Option Flag | `coordination/bin/agy-seat --invalid-option director` | Exit 2, error: unrecognized arguments | Exit 2, error message printed cleanly | PASS |
| Explicit Advisory Mode | `coordination/bin/agy-seat --mode advisory --dry-run director` | Exit 0, `"AGY_SEAT": "agy-advisory"`, `"AGY_AGENT_MODE": "advisory-readiness"` | Exit 0, JSON matched advisory identity | PASS |
| Argument Forwarding | `coordination/bin/agy-seat --dry-run director -- --foo bar` | Exit 0, `argv` contains `--foo bar` | Exit 0, `argv` includes appended args | PASS |
| Suite Unit Tests | `.venv/bin/pytest tests/unit/test_agy_*.py tests/unit/test_provider_protocol_isolation.py` | 125 passed | 125 passed in 0.88s | PASS |
| Runtime Invariants | `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` | Exit 0, all invariants OK | Exit 0, all invariants OK | PASS |

---

## Unchallenged Areas

- **Live Remote Process Execution**: Live invocation of `agy` backend binary over network was not executed because testing was conducted in dry-run mode under CODE_ONLY network constraints.
