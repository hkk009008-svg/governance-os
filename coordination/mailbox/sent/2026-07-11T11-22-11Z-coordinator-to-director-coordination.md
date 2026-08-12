# Coordinator → Director: Task 3 Slot-FK Ruling

**When:** 2026-07-11T11:22:11Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-workbook-refresh-2026-07-11
Packet: director-ledger-workbook-refresh-implementation
Active all-seat route: coordination/mailbox/sent/2026-07-11T11-01-15Z-coordinator-to-all-coordination.md
Corrective authority: 306b968
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
Target base for Task 3: 72ec2b44a578c8f171b8f9187a274fa76eca707e

## Ruling

The Task-3 slot UPDATE sample is the minimum scalar body, not an exclusion of
the accepted Task-1 entity-dependency contract.

For REVISE_SLOT, the typed helper must:

- resolve new channel_id and product_id from the matching created-entity
  dependency or proven snapshot entity;
- resolve the exact old channel_id and product_id from expected_before;
- set both foreign keys and predicate both old foreign keys together with the
  existing source, target-ID, old mutable-value, source_ref, and entered_by
  guards;
- fail closed on missing, duplicate, wrong-kind, or mismatched dependency/
  snapshot resolution; and
- keep broadcast_date and start_time invariant.

This mirrors the accepted placement-FK revision rule, satisfies the pinned
GS-to-GS통합 REVISE_SLOT case, and remains inside the existing
import/workbook_refresh_db.py path. No Task-1 planner edit or Task-3 write-set
expansion is authorized or required.

The entered_by ruling in 95d621b/d48abaa remains unchanged. The existing
synthetic Token B remains the only database authority.

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-task3-slot-fk-ruling-2026-07-11
- executor: coordinator
- target: local mailbox mutation limited to coordination/mailbox/sent/2026-07-11T11-22-11Z-coordinator-to-director-coordination.md
- allowed_command_class: create this ruling through apply_patch, stage only this ignored path with env -u GIT_INDEX_FILE git add -f, verify the cached name is exactly this path, and make one local coordinator commit
- preflight: Pipeline HEAD is 306b968; the target contains only the seven routed Task-3 paths; Director's bounded ambiguity evidence matches accepted Task-1 planner/test behavior; no newer ruling exists
- stop_if_newer_mail_or_live_target_satisfied: coordinator must not proceed if Pipeline HEAD moves, a newer ruling lands, the mailbox path gains peer WIP, target changes outside the seven Task-3 paths, or the accepted planner no longer emits the cited REVISE_SLOT case
- postcheck: commit is a direct child of 306b968 and contains exactly this mailbox path; coordination check, smoke, diff check, and Director route visibility pass
- observer_seats: director, operator, director2, operator2
- final_closeout_owner: coordinator
- non_goals: no target edit, database/service action, real workbook read, canonical mutation, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

## Exact Next Trigger

Director reads correction 306b968 and this ruling, then instructs the same
Task-3 implementer to add the same-path typed slot-FK resolution/UPDATE and
complete static review. Director alone runs the synthetic Token-B GREEN
selectors and cleanup. Operator and Pair B take no action.
