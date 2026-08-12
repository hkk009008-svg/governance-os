# Coordinator Task 3 correction — independent automatic authority bindings

**When:** 2026-07-11T19:14:43Z

Event type: coordination
Disposition: `SPEC_FAIL_CORRECTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `b571316`
Corrected spec/plan: `66905e2`

The Task 3 SPEC FAIL is accepted. Authorize a strict RED-first correction in
the cumulative Task 3 write set:

- `ARCHITECTURE.md`
- `import/workbook_refresh.py`
- `import/tests/make_refresh_fixture.py`
- `import/tests/refresh_test_support.py`
- `import/tests/test_workbook_refresh_plan.py`
- `import/workbook_refresh_corrections.py`
- `import/tests/test_workbook_refresh_corrections.py`

Add exact fact-set digests for the three automatic rule families to the
existing `reason_fact_set_sha256` binding; do not add real hashes/counts or a
new authority field. Require the pure planner caller to supply
`expected_normalization_implementation_commit` independently whenever an
override is present. Task 4 will pass the clean resolved current commit.

First prove RED for an additional otherwise-matching automatic fact and for a
wrong/missing independently expected commit. Then fix, rerun Task 1–3 focused
suites, all import tests, doc claims, target smoke, and diff checks. Commit a
bounded correction and obtain fresh cumulative specification and quality
reviews.

All work remains synthetic; no real workbook, DB/resource/scratch/service,
push, merge, publication, or cursor action is authorized.

## Exact Next Trigger

Director refreshes corrected spec/plan `66905e2`, writes the two load-bearing
RED pins, implements only the bound correction, and re-enters both Task 3
review gates.
