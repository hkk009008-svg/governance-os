# Director Task 4 blocker — final plan commit semantics

**When:** 2026-07-11T19:34:49Z

Event type: coordination
Disposition: `CONTRACT_CONTRADICTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `f9784ab`
Active release: `coordination/mailbox/sent/2026-07-11T19-30-17Z-coordinator-to-director-coordination.md`

Task 4 tests-only RED is established:

- planner CLI rejects the absent `--normalization-overrides` option;
- applier rejects canonical normalization-aware plan bytes as
  `plan-not-canonical` because it does not reconstruct audit fields.

Read-only integration found a cross-task commit contradiction. Task 3 uses
`parser_commit` to validate the blocked source-plan commit `A`, then preserves
`A` in the normalized `RefreshPlan`. The independently trusted normalization
implementation commit may be `B`. The applier requires current clean
`HEAD == plan.parser_commit`, so a valid `A != B` normalized plan cannot pass
the existing apply boundary at `B`.

Requested narrow ruling:

- authorize `import/workbook_refresh.py` plus its planner test solely so the
  normalized final plan retains the override-bound source `A` through the
  override hash/audits but sets final `RefreshPlan.parser_commit` to the
  independently supplied clean implementation commit `B`; or
- name a different canonical final-plan commit field/check that Task 4 may use.

No production Task 4 edit proceeds until this final-plan authority is explicit.
All synthetic-only, no-real-workbook, no-DB/resource/scratch/service, and
no-push boundaries remain.

## Exact Next Trigger

Coordinator publishes the selected final-plan commit contract and exact
expanded write set. Director adds a RED pin for `source=A, implementation=B,
final-plan=B`, then implements the bounded correction and resumes Task 4.
