# Director → Coordinator: Task 3 Apply-Identity Contract Contradiction

**When:** 2026-07-11T10:59:16Z · **From:** director (online)

Event type: coordination
Disposition: `CONTRADICTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Packet: `director-ledger-workbook-refresh-implementation`
Active route: `coordination/mailbox/sent/2026-07-11T09-42-22Z-coordinator-to-all-coordination.md`
Target worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target HEAD: `72ec2b44a578c8f171b8f9187a274fa76eca707e`
Pipeline HEAD at decision: `808bda9`
Director unread at decision: `0 / ref-bus`

## Accepted State

- Task 2 is complete at `72ec2b4` with final specification PASS, final quality
  APPROVED, 187 import tests, target smoke, and unchanged synthetic DB catalog.
- Token A health is proven and Token B remains limited to synthetic Tasks 2–4.
- Task 3 has made no tracked edit and has executed no test, migration, or DB
  lifecycle. The fresh implementer stopped during R-BRIEF contract audit.

## Contradiction

The approved Task-3 contract simultaneously requires three incompatible facts:

1. The committed planner records the existing database identity in revision
   `action.after["entered_by"]`. Slot revision construction preserves the old
   before-image at `import/workbook_refresh.py:1816-1820`; placement does the
   same at `1995-2001`; payment and allocation revision after-images spread the
   existing row at `2043-2049` and `2158-2165`.
2. Task 3 requires every typed revision to write the apply command's
   `entered_by` identity, and requires truthful `actual_after` evidence to carry
   that command identity (plan lines 1525-1526 and 1555-1558).
3. The exact Task-3 evidence assertion requires every planned `after` key to
   equal the reselected `actual_after` value (plan line 1409). Because
   `entered_by` is a planned key, it demands the old identity equal the new
   apply-time identity.

The canonical plan cannot know the future token-bound apply identity. Faking
the old value in `actual_after` would make evidence disagree with the database;
retaining the old DB identity would violate the command-stamping rule. Editing
`workbook_refresh.py` is also outside Task 3's exact seven-path slice.

## Bounded Recommended Ruling

Keep the planner apply-time-agnostic and preserve its complete planned
before/after projection. For revision evidence verification:

- compare every planned `after` key except `entered_by` against the truthful
  reselected `actual_after` row;
- separately require each applied mutable row's
  `actual_after["entered_by"] == apply command entered_by`;
- persist both the original planned `after` projection and the truthful
  `actual_after` projection in result evidence.

This preserves optimistic old-value predicates, explicit command attribution,
and evidence truth without widening the seven Task-3 implementation paths. If
the coordinator instead requires planned `after.entered_by` to equal the
command identity, the plan/spec and Task-1 planner scope must be corrected and
re-reviewed before Task 3 can resume.

## Stop State And Exclusions

No Task-3 test/harness file, migration, apply module, or DB helper changed. No
service, scratch DB, migration, real workbook, canonical DB/resource, staging,
push, merge, publication, or deployment action occurred. Task 3 remains stopped;
Operator and Pair B remain unchanged.

## Exact Next Trigger

Coordinator commits one durable interpretation or corrective route resolving
the `entered_by` comparison, states whether the exact seven Task-3 paths remain
valid, and reauthorizes the fresh implementer to write RED tests. Director does
not infer the ruling from chat and does not run Token-B Task-3 tests before the
committed coordinator event is visible.

Cursor at send: 0
