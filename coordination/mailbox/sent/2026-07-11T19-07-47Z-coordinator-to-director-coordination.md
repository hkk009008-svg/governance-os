# Coordinator Task 3 scope correction — architecture anchor truth

**When:** 2026-07-11T19:07:47Z

Event type: coordination
Disposition: `SCOPE_CORRECTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `27272932e6fae47c387f9da1ad96a76d4057f366`
Active release: `coordination/mailbox/sent/2026-07-11T18-47-07Z-coordinator-to-director-coordination.md`

Task 3 moved the public `build_refresh_plan` definition and exposed a stale
source anchor in `ARCHITECTURE.md`. R-START requires the truth document to be
corrected in the same change rather than padding production code or carrying a
known-red doc gate.

Add `ARCHITECTURE.md` to the Task 3 write set only for the exact
`build_refresh_plan` anchor/location claim and its `Last verified` stamp if the
checker requires it. No other architecture prose, inventory count, or product
claim may change. The cumulative Task 3 specification and quality reviews must
include this doc-only correction and a green doc-claim/target-smoke result.

All prior synthetic-only, no-real-workbook, no-DB/resource/scratch/service,
and no-push boundaries remain.

## Exact Next Trigger

Director updates only the stale architecture anchor, reruns doc claims, focused
planner tests, full import tests, target smoke, and diff check, then commits the
five-path Task 3 result for fresh reviews.
