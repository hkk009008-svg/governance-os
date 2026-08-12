# Coordinator execution release — normalization sidecar Task 4

**When:** 2026-07-11T19:30:17Z

Event type: coordination
Disposition: `IMPLEMENTATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `f9784ab`
Corrected spec/plan: `66905e2`

Task 3 is complete with fresh SPEC PASS and QUALITY APPROVED. Release Task 4
only in exactly:

- `import/plan_workbook_refresh.py`
- `import/apply_workbook_refresh.py`
- `import/tests/test_workbook_refresh_plan_cli.py`
- `import/tests/test_workbook_refresh_apply.py`

Use synthetic tests-only RED before production. Add the optional canonical
override input, validate every path before reads/connect, pass the independently
resolved clean current commit to the pure planner, bind normalization fields in
plan/report/evidence bytes, and load them canonically in the applier. The
applier must gain no sidecar/override CLI input and must never read editable
Excel. Preserve byte-compatible absent-override behavior.

Commit a clean four-path result, then obtain fresh specification and quality
reviews and update the ignored progress ledger. No real workbook, database/
resource/scratch/service, push, merge, publication, or cursor action.

## Exact Next Trigger

Director refreshes target/mail, writes CLI/load/evidence RED pins, observes the
missing support, then implements only the released Task 4 integration.
