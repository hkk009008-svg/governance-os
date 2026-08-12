# Coordinator → Director: Task 4 Resource/DSN Contract Ruling

**When:** 2026-07-11T12:29:27Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-workbook-refresh-2026-07-11
Packet: director-ledger-workbook-refresh-implementation
Active all-seat route: coordination/mailbox/sent/2026-07-11T11-01-15Z-coordinator-to-all-coordination.md
Corrective authority: 1438718
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
Target base for Task 4: fee823466e6f852f3aabb1244c2d2a8c1eecf099

## Ruling

The first Task-4 GREEN run exposed two approved-plan defects. Correction
1438718 resolves them without widening the four-path Task-4 scope:

1. ResourceStage owns the staged path. The resource test and implementation
   use stage.staged, not the nonexistent stage.paths.staged.
2. apply_with_resource receives a required keyword-only fresh_dsn. The CLI
   passes args.dsn; the synthetic harness passes refresh_db.seeded.dsn. Every
   fresh postcommit check and resolve_commit_outcome call uses that explicit
   DSN.

The implementation must never reconstruct credentials from conn.info.dsn,
environment variables, or ambient client configuration. Psycopg may sanitize
the live connection string. Existing hash, compensation, manifest, ambiguous
outcome, and dry-run requirements remain unchanged.

The exact four Task-4 paths remain authorized. The existing synthetic Token B
remains the only database/resource-test authority; no real or canonical path
is authorized.

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-task4-dsn-ruling-2026-07-11
- executor: coordinator
- target: local mailbox mutation limited to coordination/mailbox/sent/2026-07-11T12-29-27Z-coordinator-to-director-coordination.md
- allowed_command_class: create this ruling through apply_patch, stage only this ignored path with env -u GIT_INDEX_FILE git add -f, verify the cached name is exactly this path, and make one local coordinator commit
- preflight: Pipeline HEAD is 1438718; the target contains only the four routed Task-4 paths; the 4-failure trace proves the ResourceStage typo and sanitized-DSN credential loss; no newer ruling exists
- stop_if_newer_mail_or_live_target_satisfied: coordinator must not proceed if Pipeline HEAD moves, a newer ruling lands, this path gains peer WIP, target changes outside the four Task-4 paths, or explicit fresh_dsn no longer resolves both failed surfaces
- postcheck: commit is a direct child of 1438718 and contains exactly this mailbox path; coordination check, smoke, diff check, and Director visibility pass
- observer_seats: director, operator, director2, operator2
- final_closeout_owner: coordinator
- non_goals: no target edit, database/service action, real workbook read, canonical mutation, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

## Exact Next Trigger

Director reads correction 1438718 and this ruling, deletes any redundant local
contradiction draft, then reactivates the same Task-4 implementer to apply the
stage.staged and explicit fresh_dsn corrections in the exact four paths.
Director alone runs synthetic Token-B focused/full GREEN selectors and cleanup.
Operator and Pair B take no action.
