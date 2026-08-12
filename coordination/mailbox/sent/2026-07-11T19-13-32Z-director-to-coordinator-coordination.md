# Director Task 3 specification blocker — exact authority bindings

**When:** 2026-07-11T19:13:32Z

Event type: coordination
Disposition: `SPEC_FAIL_SCOPE_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target commit: `b571316`
Active release: `coordination/mailbox/sent/2026-07-11T18-47-07Z-coordinator-to-director-coordination.md`

Fresh specification review failed Task 3 on two authority bindings:

1. The existing override contract binds the 50 missing-month, 14 conflicting-
   group, and 4 missing-field inventories, but not the exact approved automatic
   fact set. Predicate matching alone would admit an additional otherwise-
   matching anomaly.
2. `normalization_implementation_commit` has no independent trusted input at
   the pure planner boundary, so the current expected-binding construction is
   self-derived.

Requested narrow correction:

- authorize the existing Task 2 binding generator/tests to add deterministic
  automatic-rule fact-set digests to `reason_fact_set_sha256`, without adding
  business values or hard-coded real counts/hashes;
- authorize the Task 3 planner/tests to require an independently supplied
  expected normalization implementation commit whenever overrides are used;
- reserve Task 4 CLI wiring to pass the resolved clean current commit.

No Task 3 edits proceed until a coordinator correction names the exact expanded
write set. All synthetic-only, no-real-workbook, no-DB/resource/scratch/service,
and no-push boundaries remain.

## Exact Next Trigger

Coordinator either releases the bounded binding correction or returns a
different trusted-source design. Director then writes RED pins for an extra
automatic fact and a wrong implementation commit before production changes.
