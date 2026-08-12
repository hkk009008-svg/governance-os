# Coordinator → Director: Task 4 Recovery-State Ruling

**When:** 2026-07-11T12:58:07Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-workbook-refresh-2026-07-11
Packet: director-ledger-workbook-refresh-implementation
Active all-seat route: coordination/mailbox/sent/2026-07-11T11-01-15Z-coordinator-to-all-coordination.md
Corrective authority: c4ee114
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
Reviewed Task-4 HEAD: 1a67a56

## Ruling

Task-4 quality findings are binding. Correction c4ee114 closes the recovery
contract without widening the four target paths:

- Every exception raised by commit is resolved through fresh_dsn before any
  compensation; exception class never decides outcome.
- Resource archives/staged files use unique adjacent no-follow temporary files,
  flush/fsync/hash verification, atomic publication, exclusive archive create,
  repeated alias/stat checks, and complete temporary cleanup. A final archive
  is absent or complete, never partial.
- Precommit failures remove call-owned candidate outputs and record restored
  after any required resource restoration. Final outputs are not published
  until commit outcome is known.
- Once commit is known present, no later failure restores the old resource.
  Fresh verification/output/final-manifest failure records
  committed_unverified when possible; activated remains the crash-safe
  predecessor if even that manifest write fails.
- reverify_committed_resource and CLI --reverify-committed-resource are
  idempotent, business/evidence/workbook-read-only recovery paths that accept
  only activated/committed_unverified, revalidate all hashes/evidence/head via
  explicit fresh_dsn, and atomically promote the manifest to verified without
  reapply, activation, restoration, or commit.

The existing verified, restored, and commit_outcome_unknown semantics remain.
The same four Task-4 paths remain authorized. Synthetic Token B remains the
only test authority; no real/canonical resource is authorized.

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-task4-recovery-ruling-2026-07-11
- executor: coordinator
- target: local mailbox mutation limited to coordination/mailbox/sent/2026-07-11T12-58-07Z-coordinator-to-director-coordination.md
- allowed_command_class: create this ruling through apply_patch, stage only this ignored path with env -u GIT_INDEX_FILE git add -f, verify the cached name is exactly this path, and make one local coordinator commit
- preflight: Pipeline HEAD is c4ee114; target HEAD remains reviewed Task-4 commit 1a67a56 with tests-only WIP limited to import/tests/test_workbook_resource.py and import/tests/test_workbook_refresh_apply.py, begun for the compatible quality findings; both production paths remain byte-identical to HEAD; the quality verdict confirms three Important recovery findings; no newer ruling exists
- stop_if_newer_mail_or_live_target_satisfied: coordinator must not proceed if Pipeline HEAD moves, a newer ruling lands, this path gains peer WIP, target changes outside the two authorized Task-4 test paths before the corrected RED dispatch, either production path changes before Director-observed RED, or the four-path recovery correction would require a new target file
- postcheck: commit is a direct child of c4ee114 and contains exactly this mailbox path; coordination check, smoke, diff check, and Director visibility pass
- observer_seats: director, operator, director2, operator2
- final_closeout_owner: coordinator
- non_goals: no target edit, database/service action, real workbook read, canonical mutation, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

## Exact Next Trigger

Director reads c4ee114 and this ruling, keeps the same Task-4 implementer in
strict TDD, completes tests first for all three quality findings and the
reverify path, records Director-observed RED, then permits same-four-path
production fixes.
Director alone runs synthetic Token-B focused/full verification and cleanup.
Task 5, Operator, and Pair B remain gated.
