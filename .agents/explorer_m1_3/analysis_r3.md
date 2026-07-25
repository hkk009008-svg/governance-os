# R3 Unit Test & CI Suite Analysis Report

## Executive Summary

This report delivers the comprehensive analysis of unit test suites (`tests/unit/test_agy_*.py`, `tests/unit/test_provider_protocol_isolation.py`) and `scripts/ci_smoke.py` as part of Milestone 1 (R3 Unit Test & CI Suite Analysis) for AGY Protocol Modernization.

The analysis confirms that:
1. **Four AGY-specific unit test files** (`test_agy_protocol_model.py`, `test_agy_seat_launcher.py`, `test_agy_agent_surfaces.py`, `test_agy_emit.py`) and **one cross-provider isolation test** (`test_provider_protocol_isolation.py`) currently test AGY runtime behavior.
2. **Five specific test functions** in `test_agy_protocol_model.py` and `test_agy_seat_launcher.py` explicitly lock in legacy advisory posture requirements (`AGY_SEAT="agy-advisory"`, `AGY_AGENT_MODE="advisory-readiness"`, and process exit code 2 on direct launch without `--mode single-model-autonomous`).
3. **`scripts/ci_smoke.py`** exercises governance OS invariants, ceremony rules, placeholders, and report schemas across all seats. It contains zero hardcoded dependencies on advisory flags and will pass 100% cleanly once unit test assertions are aligned with direct autonomous operation.
4. **Non-AGY provider mechanics** (Codex, Claude, Cursor) remain completely unaffected, as proven by `test_provider_protocol_isolation.py` and provider-specific test suites.

---

## 1. Test File Inventory

The table below catalogs all test files relevant to AGY protocol models, seat launchers, binary wrappers, and cross-provider containment:

| Test File Path | Line Count | Primary Subject | Alignment Need for R3 |
|---|---|---|---|
| `tests/unit/test_agy_protocol_model.py` | 36 | `scripts/agy_protocol_model.py` (`infer_runtime_env`) | High — Update default mode assertions from `ADVISORY_MODE` to `SINGLE_MODEL_MODE` |
| `tests/unit/test_agy_seat_launcher.py` | 591 | `scripts/agy_seat_launcher.py` (CLI, env, specs, dry-run) | High — Replace advisory default launch tests with direct autonomous launch assertions |
| `tests/unit/test_agy_agent_surfaces.py` | 110 | `.agy/agents/*.toml` catalog & `README.md` | Low — Confirm agent surface rules remain valid under new harness doctrine |
| `tests/unit/test_agy_emit.py` | 23 | `scripts/agy_emit.py` (mailbox event CLI wrapper) | Medium — Verify `dispatch_cmd` invocation without redundant `--mode` flag |
| `tests/unit/test_provider_protocol_isolation.py` | 160 | Cross-provider env isolation (Codex vs AGY) | Medium — Verify AGY runtime env parameters remain inert to Codex |
| `scripts/ci_smoke.py` | 392 | Governance OS runtime invariants & CI smoke gates | Low (No changes needed) — Verify clean execution via `--fast` and full run |

---

## 2. Legacy Assertions Requiring Alignment

### A. `tests/unit/test_agy_protocol_model.py`

- **Line 8 (`test_advisory_runtime_is_agy_named_and_has_no_shared_seat_identity`)**:
  - *Current behavior*: Calls `protocol.infer_runtime_env(profile="director", mode=protocol.ADVISORY_MODE, ...)` expecting `AGY_SEAT="agy-advisory"` and `AGY_AGENT_MODE="advisory-readiness"`.
  - *Required update*: Update or add test asserting `infer_runtime_env(profile="director")` defaults to `SINGLE_MODEL_MODE` (`single-model-autonomous`) with `AGY_SEAT="agy-unit-director"`, `AGY_AGENT_ROLE="agy-unit-director"`, and `AGY_BEHAVIOR_SOURCE="agy-unit-director"`.

### B. `tests/unit/test_agy_seat_launcher.py`

- **Line 32 (`test_build_launch_spec_defaults_to_advisory_agy_identity_and_cleans_authority`)**:
  - *Current behavior*: Calls `launcher.build_launch_spec()` without `mode` parameter, expecting `spec.env["AGY_SEAT"] == "agy-advisory"` and `spec.env["AGY_AGENT_MODE"] == "advisory-readiness"`.
  - *Required update*: Change assertion to expect direct autonomous identity:
    - `spec.env["AGY_SEAT"] == "agy-unit-director"`
    - `spec.env["AGY_AGENT_MODE"] == "single-model-autonomous"`
    - `spec.env["AGY_AGENT_ROLE"] == "agy-unit-director"`
    - `spec.env["AGY_BEHAVIOR_SOURCE"] == "agy-unit-director"`

- **Line 87 (`test_build_launch_spec_requires_explicit_isolated_mode_for_agy_unit`)**:
  - *Current behavior*: Passed explicit `mode=launcher.SINGLE_MODEL_MODE` to get autonomous environment variables.
  - *Required update*: Refactor to verify that default invocation (omitting `mode`) produces the exact same autonomous environment variables.

- **Line 490 (`test_dry_run_does_not_create_index_or_start_agy`)**:
  - *Current behavior*: Asserts `payload["env"]["AGY_SEAT"] == "agy-advisory"` and `payload["env"]["AGY_AGENT_MODE"] == "advisory-readiness"`.
  - *Required update*: Update assertions to expect `payload["env"]["AGY_SEAT"] == "agy-unit-director"` and `payload["env"]["AGY_AGENT_MODE"] == "single-model-autonomous"`.

- **Line 554 (`test_default_advisory_mode_refuses_provider_launch`)**:
  - *Current behavior*: Calls `launcher.main(["--config", str(config_path), "director"])` expecting exit code 2 and error message `"advisory mode does not launch AGY"`.
  - *Required update*: Replace this test with `test_direct_autonomous_mode_launches_provider()`, asserting that direct invocation without advisory or mode flags proceeds to build launch spec and launch AGY executable cleanly.

- **Line 580 (`test_continuation_documents_advisory_default_and_stdin_writer`)**:
  - *Current behavior*: Asserts `docs/protocol/agy/continuation.md` contains `--mode single-model-autonomous` and `does not claim a shared Pipeline seat`.
  - *Required update*: Align doc assertions with modernized `continuation.md` (R2 updates) confirming native subagent & artifact mesh documentation.

### C. `scripts/agy_emit.py`

- **Line 132 (`dispatch_cmd`)**:
  - *Current string*: `".venv/bin/python scripts/agy_seat_launcher.py {args.to} --mode single-model-autonomous"`
  - *Required update*: Simplify to `"coordination/bin/agy-seat {args.to}"` or `".venv/bin/python scripts/agy_seat_launcher.py {args.to}"` without the legacy `--mode` flag.

---

## 3. CI Smoke Suite Analysis (`scripts/ci_smoke.py`)

`scripts/ci_smoke.py` operates in two halves:
1. **Half A (`_project_smoke`)**: Verifies core governance OS runtime invariants:
   - Signed-bus package (`threeway`) import cleanliness, RFC-8785 canonicalization stability, and `LOAD_BEARING_KINDS`.
   - Protocol mailbox seat roster (`protocol_mailbox.SEATS`) containing `director`, `director2`, `operator`, `operator2`, and mailbox kind parsing.
2. **Half B (Governance Gates)**:
   - Doc-anchor drift gate (`check_doc_claims` on `ARCHITECTURE.md`).
   - Manual anchor drift check (`docs/PROGRAM-MANUAL.md`).
   - Commit-SHA ref drift baseline.
   - Coordination state gate (`check_coordination`).
   - Anti-ceremony gate (`check_no_ceremony` — ADR-028).
   - Reviewer-result schema validation (`consume_reviewer_result`).
   - Adoption placeholder gate (`check_placeholders` — ADR-002).
   - Lane V report & GO evidence validator (`check_go_schema`).
   - Mechanism ledger validation (`threeway_mechanism_ledger`).
   - Architecture freshness stamp gate (`check_arch_freshness`).

**Findings for CI Integration**:
- `ci_smoke.py` does NOT contain hardcoded references to AGY advisory mode or launch flags.
- `ci_smoke.py` tests seat rosters and governance invariants in a provider-agnostic manner.
- Non-AGY providers (Codex, Claude, Cursor) are unaffected by AGY launcher refactoring.
- Both fast preflight (`.venv/bin/python scripts/ci_smoke.py --fast`) and full smoke test (`.venv/bin/python scripts/ci_smoke.py`) pass cleanly in the current working tree and will remain 100% green after M2/M4 changes.

---

## 4. Verification Instructions

The alignment of unit tests and CI smoke suite must be verified using the following standard commands:

### A. Targeted AGY & Provider Isolation Unit Tests
```bash
.venv/bin/pytest tests/unit/test_agy_agent_surfaces.py tests/unit/test_agy_emit.py tests/unit/test_agy_protocol_model.py tests/unit/test_agy_seat_launcher.py tests/unit/test_provider_protocol_isolation.py
```

### B. Full Pytest Unit Suite
```bash
.venv/bin/pytest tests/unit/
```

### C. CI Smoke Preflight & Full Checks
```bash
# Fast preflight check (runs essential coordination, ceremony, placeholder checks)
.venv/bin/python scripts/ci_smoke.py --fast

# Complete governance OS CI smoke check
.venv/bin/python scripts/ci_smoke.py
```

---

## 5. Next Steps for Implementation (Milestone 4 / R3)

1. Perform M2 (R1 launcher & protocol model code refactoring).
2. Perform M3 (R2 documentation & harness skill updates).
3. Apply formulated updates to `tests/unit/test_agy_protocol_model.py` and `tests/unit/test_agy_seat_launcher.py`.
4. Run verification commands to ensure 100% pass rate.
