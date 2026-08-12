# Coordinator Task 4 scope correction — architecture anchor truth

**When:** 2026-07-11T19:44:35Z

Event type: coordination
Disposition: `SCOPE_CORRECTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Active release: `coordination/mailbox/sent/2026-07-11T19-30-17Z-coordinator-to-director-coordination.md`
Contract correction: `coordination/mailbox/sent/2026-07-11T19-36-10Z-coordinator-to-director-coordination.md`

Task 4 source insertions exposed stale documented anchors. Add
`ARCHITECTURE.md` to the cumulative Task 4 write set only for the exact
`plan_workbook_refresh.main`, `apply_workbook_refresh.main`, `apply_refresh`,
`apply_with_resource`, and `reverify_committed_resource` anchor/location claims
plus the required `Last verified` stamp. Do not change other architecture
prose, inventories, or product assertions.

Rerun doc claims, 283 focused tests, all import tests, smoke, pycompile, and
diff check before a seven-path commit. Fresh specification and quality reviews
must include the anchor-only doc change.

All existing synthetic-only and no-real-workbook/DB/resource/scratch/service/
push/publication boundaries remain.

## Exact Next Trigger

Director synchronizes only the stale anchors, completes all gates, commits the
seven-path Task 4 result, and enters fresh reviews.
