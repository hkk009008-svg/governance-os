# Coordinator execution release — normalization sidecar Task 3

**When:** 2026-07-11T18:47:07Z

Event type: coordination
Disposition: `IMPLEMENTATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target base: `27272932e6fae47c387f9da1ad96a76d4057f366`
Approved plan: `docs/superpowers/plans/2026-07-12-ledger-workbook-normalization-sidecar.md` at `e109814`

Tasks 1 and 2 are complete with fresh SPEC PASS and QUALITY APPROVED. Release
Task 3 pure planner normalization only in exactly:

- `import/workbook_refresh.py`
- `import/tests/test_workbook_refresh_plan.py`
- `import/tests/make_refresh_fixture.py`
- `import/tests/refresh_test_support.py`

Use strict tests-only RED before production. Implement the exact 12 rule
audits, 50 missing-month decisions, 14 nested conflicting-group decisions, 4
missing-field decisions, summary-last evaluation, component bijection, and
unchanged default behavior without override input. Use synthetic fixtures only.
Commit, then obtain fresh specification and quality reviews before updating the
ignored ledger or requesting Task 4.

No real workbook read, CLI/apply path edit, database/resource/scratch/service
mutation, push, merge, publication, or cursor consume.

## Exact Next Trigger

Director refreshes target/mail, dispatches the Task 3 tests-only slice,
observes the missing override/audit interface RED, and then authorizes only the
released planner production path.
