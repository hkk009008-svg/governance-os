# Coordinator execution release — normalization sidecar Task 2

**When:** 2026-07-11T18:05:32Z

Event type: coordination
Disposition: `IMPLEMENTATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target base: `752e69ae907cde9003c5778cfe7803d81bf0ab85`
Approved plan: `docs/superpowers/plans/2026-07-12-ledger-workbook-normalization-sidecar.md` at `e109814`

Task 1 is complete with fresh SPEC PASS and QUALITY APPROVED. Release Task 2
only in exactly:

- `import/workbook_refresh_corrections.py`
- `import/tests/test_workbook_refresh_corrections.py`
- `import/tests/refresh_test_support.py`

Use synthetic fixtures only. Write and observe the focused RED before adding
production. Implement the exact Excel generation/validation contract, strict
path/read ordering, formula rejection, canonical protected-cell model, and
atomic alias-safe publication. Commit a clean three-path result, then obtain
fresh specification and quality reviews. Update the ignored progress ledger
only after both approve.

No real workbook read, canonical/source workbook edit, database/resource/
scratch/service mutation, push, merge, publication, or cursor consume. Do not
begin Task 3 without a new coordinator release.

## Exact Next Trigger

Director refreshes target/mail, dispatches a fresh Task 2 tests-only
implementer, observes the expected missing-CLI RED, and authorizes production
only afterward.
