# Coordinator capacity correction — sequential cold Lane V reviewers

**When:** 2026-07-11T21:08:53Z

Event type: coordination
Disposition: `CAPACITY_CORRECTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Active verification token: `coordination/mailbox/sent/2026-07-11T21-02-07Z-coordinator-to-operator-verify-request.md`

The first cold specification reviewer is active, but the simultaneous cold
quality-review dispatch failed with the concrete four-thread capacity limit.
The remaining listed reviewer is not eligible for reuse because it previously
reviewed `cb9c278`, which is inside the cumulative range.

Preserve coldness by completing the current specification review, then
dispatching one genuinely fresh quality reviewer into the released slot.
Sequential dispatch is authorized only for this capacity condition. Operator
may continue its own read-only diff inspection and synthetic gates in parallel,
but must not execute the token-bound real negative validation until both cold
reviewer verdicts are complete. Record the capacity deviation in the final
verification report. All token boundaries and stop conditions otherwise remain
unchanged.

## Exact Next Trigger

Operator completes the current cold specification review, launches a fresh
quality review, reconciles both, and only then proceeds to the real read-only
validation if neither review blocks.
