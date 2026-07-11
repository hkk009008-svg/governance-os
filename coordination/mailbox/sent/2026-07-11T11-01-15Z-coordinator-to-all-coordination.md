# Coordinator → All: Task 3 Apply-Identity Contract Resolution

**When:** 2026-07-11T11:01:15Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-workbook-refresh-2026-07-11
Supersedes route: coordination/mailbox/sent/2026-07-11T09-42-22Z-coordinator-to-all-coordination.md
Contradiction artifact: cfaa5b7
Corrective authority: 95d621b
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
Target HEAD: 72ec2b44a578c8f171b8f9187a274fa76eca707e
Cursor at send: 0

## Durable Disposition

- The Task-3 apply-identity contradiction is closed by plan correction
  95d621b. A planned after projection is apply-time-principal agnostic.
- For every action, evidence compares all planned after keys except entered_by
  to the truthful reselected actual_after row. For each mutating action whose
  planned row carries entered_by, actual_after.entered_by must equal the apply
  command identity. The plan SHA retains the original planned projection and
  actual_after proves the transaction result.
- No Task-1 planner edit is required. Task 3 retains its exact seven-path
  implementation scope. The implementer may now write RED tests; Director alone
  executes DB-backed RED/GREEN selectors under the reaffirmed synthetic token.
- Tasks 0–2 are accepted through target 72ec2b4 with final spec/quality passes,
  187 import tests, target smoke, unchanged scratch catalog, and a clean target.
- Operator remains blocked until the cumulative verify-request. Director2 and
  Operator2 take no new action. Real-data and canonical actions remain later
  separate coordinator gates.

## Capacity Split Default

The single-pair fast path remains Director implementation plus later Operator
Lane V. Pair B's bounded planning or preflight contribution is complete; its
packets remain evidence-complete blocked holds. Coordinator owns convergence.

## Capacity Packet Coverage

All 88 Wave-2 packet IDs are named. In this cycle,
coord-ledger-workbook-refresh-join and
director-ledger-workbook-refresh-implementation are ready; the corrective
Director2 packet is the evidence-complete blocked current hold; Operator is
blocked pending the Director verify-request.

- coord-control-plane-authority-foundation-join
- coord-execution-strength-broader-join
- coord-governance-hardening-bridge-join
- coord-ledger-phase2-detail-integration-join
- coord-ledger-phase2-task21-join
- coord-ledger-phase2-task21-route
- coord-ledger-phase2-task22-join
- coord-ledger-phase2-task23-join
- coord-ledger-phase2-task24-join
- coord-ledger-phase2-task25-26-join
- coord-ledger-runway-stage0-join
- coord-ledger-runway-stage0-route
- coord-ledger-t14-align-join
- coord-ledger-t14-align-route
- coord-ledger-workbook-refresh-join
- coord-unit-coherence-side-effect-token-join
- director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix
- director-control-plane-authority-foundation-task2-race-fix
- director-control-plane-authority-foundation-task2-replacement
- director-control-plane-authority-foundation-task2-spec-review-fix
- director-control-plane-authority-foundation-task2u-fail-closed-closure
- director-control-plane-authority-foundation-tasks1-2
- director-execution-strength-broader-impl
- director-governance-hardening-bridge-impl
- director-ledger-phase2-detail-integration
- director-ledger-phase2-task21-write-path
- director-ledger-phase2-task22-validations
- director-ledger-phase2-task23-result-history
- director-ledger-phase2-task24-ios-slot-entry
- director-ledger-phase2-task25a-result-entry
- director-ledger-publication-decision
- director-ledger-runway-stage0-owner-gates
- director-ledger-workbook-refresh-implementation
- director-unit-coherence-side-effect-token-impl
- director2-control-plane-authority-foundation-identity-interface-closure-preflight
- director2-control-plane-authority-foundation-identity-preflight
- director2-control-plane-authority-foundation-identity-repreflight
- director2-control-plane-authority-foundation-identity-rerepreflight
- director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight
- director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight
- director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight
- director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight
- director2-control-plane-authority-foundation-task3h-causal-runtime-proof-closure-preflight
- director2-control-plane-authority-foundation-task3i-execution-contract-closure-preflight
- director2-execution-strength-broader-observer
- director2-governance-hardening-bridge-observer
- director2-ledger-next-brief
- director2-ledger-phase2-bounds-plan-sync
- director2-ledger-phase2-detail-integration-preflight
- director2-ledger-phase2-task22-observer
- director2-ledger-phase2-task23-observer
- director2-ledger-phase2-task24-observer
- director2-ledger-phase2-task24-planning-preflight
- director2-ledger-phase2-task26a-history-component
- director2-ledger-runway-plan-reconcile
- director2-ledger-workbook-refresh-contract-correction-preflight
- director2-ledger-workbook-refresh-preflight
- director2-unit-coherence-observer-standby
- operator-control-plane-authority-foundation-lanev
- operator-control-plane-authority-foundation-replacement-lanev
- operator-control-plane-authority-foundation-task2u-cumulative-lanev
- operator-execution-strength-broader-verification
- operator-governance-hardening-bridge-lanev
- operator-ledger-phase2-detail-integration-lanev
- operator-ledger-phase2-task21-lanev
- operator-ledger-phase2-task22-lanev
- operator-ledger-phase2-task23-lanev
- operator-ledger-phase2-task24-lanev
- operator-ledger-phase2-task25a-lanev
- operator-ledger-runway-stage0-verify
- operator-ledger-workbook-refresh-lanev
- operator-pipeline-tooling-verify
- operator-unit-coherence-side-effect-token-verification
- operator2-control-plane-authority-foundation-activation-repreflight
- operator2-control-plane-authority-foundation-cutover-preflight
- operator2-execution-strength-broader-observer
- operator2-governance-hardening-bridge-observer
- operator2-ledger-main-verify
- operator2-ledger-phase2-base-preflight
- operator2-ledger-phase2-detail-integration-preflight
- operator2-ledger-phase2-task22-observer
- operator2-ledger-phase2-task23-observer
- operator2-ledger-phase2-task24-observer
- operator2-ledger-phase2-task24-preflight
- operator2-ledger-phase2-task26a-lanev
- operator2-ledger-runway-worktree-verify
- operator2-ledger-workbook-refresh-preflight
- operator2-unit-coherence-observer-standby

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-synthetic-db-tasks2-4-2026-07-11
- executor: director
- target: synthetic-only PostgreSQL databases at 127.0.0.1:54322 whose names match exactly refresh_<12-lowercase-hex>, test_<12-lowercase-hex>, import_<12-lowercase-hex>, load_<12-lowercase-hex>, or agency_<12-lowercase-hex>; no postgres, canonical, remote, or pre-existing database is a mutation target
- allowed_command_class: with proven healthy local stack, bind PG_BIN=/opt/homebrew/opt/libpq/bin and use only its executable createdb, dropdb, psql, pg_isready, pg_dump, and pg_restore clients; for each fresh UUID-derived allowed name, prove absence with a read-only pg_database query, create only that name, install only synthetic auth helpers, apply sorted migrations only from the routed worktree with ON_ERROR_STOP, seed only committed synthetic fixtures, run Tasks 3–4 migration/rollback/dry-run/apply/resource-compensation tests in that database and pytest temporary paths, then force-drop exactly the successfully created name; the versioned fixture may perform equivalent psycopg CREATE DATABASE allowed-name and DROP DATABASE same-name WITH FORCE inside finally cleanup
- preflight: local Docker/Supabase health from the prior token remains proven at 127.0.0.1:54322; all six bound PG_BIN executables are present; target HEAD is exact clean 72ec2b44a578c8f171b8f9187a274fa76eca707e before Task-3 edits; plan correction 95d621b and this route are visible; every generated name is absent and matches the allowlist; inputs are synthetic only
- stop_if_newer_mail_or_live_target_satisfied: Director must not proceed before each lifecycle mutation if Pipeline route changes, target HEAD/worktree differs from the Director-controlled current Task commit state, the generated name exists or falls outside the allowlist, endpoint/DSN/migration root differs, a non-synthetic value or real workbook path enters the run, cleanup fails, or any command targets postgres, a canonical/remote database, canonical workbook/resource, push, publication, or deployment
- postcheck: every successfully created name is recorded before migration and absent from pg_database after its finally/dropdb cleanup; no migration is applied to postgres; no retry occurs over a partial database; the scratch catalog hash/count returns to its pre-run value; target status contains only current routed task paths before Director commit and is clean after each accepted task; no generated workbook, dump, credential, report, business value, data directory, or .superpowers evidence is tracked
- observer_seats: coordinator, operator, director2, operator2
- final_closeout_owner: coordinator
- non_goals: no real-data scratch clone/apply, user workbook read/copy, canonical database/resource activation, normal-checkout mutation, service stop, container/volume deletion, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-task3-resolution-route-2026-07-11
- executor: coordinator
- target: local route mutation limited to coordination/mailbox/sent/2026-07-11T11-01-15Z-coordinator-to-all-coordination.md
- allowed_command_class: create this route through apply_patch, stage only this ignored path with env -u GIT_INDEX_FILE git add -f, verify the cached name is exactly this path, and make one local coordinator commit; no other mutation class
- preflight: Pipeline HEAD is 95d621b; target worktree is clean at 72ec2b44a578c8f171b8f9187a274fa76eca707e; capacity is valid; coordinator unread is zero; contradiction cfaa5b7 is resolved by plan correction 95d621b; unrelated Pipeline WIP does not overlap this route
- stop_if_newer_mail_or_live_target_satisfied: coordinator must not proceed before staging if HEAD moves from 95d621b, newer coordinator mail or another correction route lands, this path gains peer WIP, target state changes, capacity becomes invalid, or another committed route already binds correction 95d621b
- postcheck: coordinator commit is a direct child of 95d621b; cached and committed scope contains exactly this route; board and route validate; doctor, smoke, diff checks, all-seat route visibility, and target cleanliness pass
- observer_seats: director, operator, director2, operator2, coordinator2
- final_closeout_owner: coordinator
- non_goals: no target product edit, Task-1 planner edit, service action, database action by coordinator, real workbook read, scratch/canonical mutation, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

Join condition: Task 3 remains open until Director completes its seven-path
strict-TDD implementation, synthetic Token-B migration/apply/rollback tests,
fresh spec review, and fresh quality review. Task 4 then reuses only the same
synthetic token. Real-data scratch and canonical activation require later
separate coordinator tokens.

## Exact Next Trigger

Director refreshes to this route and correction 95d621b, confirms clean target
72ec2b4, reactivates the same Task-3 implementer to write the corrected RED
tests in the exact seven paths, and executes DB-backed RED/GREEN selectors only
under the reaffirmed synthetic token. Operator, Director2, and Operator2 take
no action.
