# Coordinator → All: Workbook Refresh Synthetic Test Authorities

**When:** 2026-07-11T09:42:22Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-workbook-refresh-2026-07-11
Supersedes route: coordination/mailbox/sent/2026-07-11T07-38-30Z-coordinator-to-all-coordination.md
Token request: fbd0478
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
Target HEAD: 059bea28b9e0de9a53c05fffb3e9e9217dfd7d40
Cursor at send: 0

## Durable Disposition

- Task 0 is accepted at 25e5110 and Task 1 is accepted through 059bea2 after
  specification PASS, cumulative quality APPROVED, 58 combined tests, target
  smoke, diff checks, and a clean routed worktree.
- Director remains the sole target controller and committer. It may execute
  Tasks 2–4 sequentially through the routed implementer/spec-review/
  quality-review loops under the two separately bounded authorities below.
- Token A is conditional local-service-start authority. Director first runs
  its read-only health checks and starts only the unhealthy local component.
- Token B is synthetic scratch-database lifecycle authority. It becomes usable
  only after Token A health is proven or the stack is already healthy.
- Operator remains blocked until the cumulative verify-request. Director2 and
  Operator2 take no new action. Coordinator retains convergence and all later
  real-data/canonical token authority.

## Capacity Split Default

The single-pair fast path remains Director implementation plus later Operator
Lane V. Pair B has completed its bounded planning or preflight contribution
and remains on evidence-complete blocked holds. Coordinator owns convergence.

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

- side_effect_id: ledger-workbook-refresh-local-service-start-2026-07-11
- executor: director
- target: local Docker Desktop daemon and the Supabase project rooted only at /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11, exposing PostgreSQL only at 127.0.0.1:54322
- allowed_command_class: bind DOCKER=/Users/hyungkoookkim/.local/bin/docker, SUPABASE=/opt/homebrew/bin/supabase, PG_BIN=/opt/homebrew/opt/libpq/bin, and WORKTREE to the routed worktree; run read-only docker info, supabase status --workdir "$WORKTREE", and "$PG_BIN/pg_isready" against 127.0.0.1:54322/postgres; only when unhealthy, execute /usr/bin/open -a Docker and/or "$SUPABASE" start --workdir "$WORKTREE" --exclude analytics,edge-runtime,functions,imgproxy,inbucket,kong,meta,realtime,rest,storage,studio,vector; poll health at bounded intervals; finish with read-only pg_isready and psql select current_database(), current_user
- preflight: Pipeline HEAD is fbd0478; target HEAD is exact clean 059bea28b9e0de9a53c05fffb3e9e9217dfd7d40; Director request fbd0478 names the same binaries, worktree, endpoint, and exclusions; coordinator unread is zero; capacity is valid; no newer route or token exists
- stop_if_newer_mail_or_live_target_satisfied: Director must not proceed if Pipeline or target HEAD moves, target becomes dirty, a newer route/token lands, the local endpoint/project differs, Docker or Supabase reports a collision, health is not reached within 120 seconds after each authorized start, or any command requires stop/delete/cleanup, container or volume deletion, non-local access, credentials beyond the local defaults, or paid service
- postcheck: docker info succeeds; supabase status identifies the routed project; pg_isready succeeds only at 127.0.0.1:54322/postgres; read-only psql returns postgres and the expected local admin user; Director records whether each component was already healthy or started; target git status and HEAD remain unchanged
- observer_seats: coordinator, operator, director2, operator2
- final_closeout_owner: coordinator
- non_goals: no service stop, container/image/network/volume deletion, target edit, database create/drop, real workbook read, canonical database/resource mutation, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-synthetic-db-tasks2-4-2026-07-11
- executor: director
- target: synthetic-only PostgreSQL databases at 127.0.0.1:54322 whose names match exactly refresh_<12-lowercase-hex>, test_<12-lowercase-hex>, import_<12-lowercase-hex>, load_<12-lowercase-hex>, or agency_<12-lowercase-hex>; no postgres, canonical, remote, or pre-existing database is a mutation target
- allowed_command_class: after Token A health proof, bind PG_BIN=/opt/homebrew/opt/libpq/bin and use only its executable createdb, dropdb, psql, pg_isready, pg_dump, and pg_restore clients; for each fresh UUID-derived allowed name, prove absence with a read-only pg_database query, create only that name, install only synthetic auth helpers, apply sorted migrations only from the routed worktree with ON_ERROR_STOP, seed only committed synthetic fixtures, run Tasks 2–4 snapshot/plan/rollback/dry-run/apply/resource-compensation tests in that database and pytest temporary paths, then force-drop exactly the successfully created name; the versioned fixture may perform the equivalent psycopg CREATE DATABASE allowed-name and DROP DATABASE same-name WITH FORCE inside its finally cleanup
- preflight: Token A postchecks pass or prove the stack already healthy; all six bound PG_BIN executables exist and are executable; admin DSN is exactly postgresql://postgres:postgres@127.0.0.1:54322/postgres; target HEAD is exact clean 059bea28b9e0de9a53c05fffb3e9e9217dfd7d40 before Task 2 edits; each generated name is absent and matches the allowlist; test inputs contain synthetic values only
- stop_if_newer_mail_or_live_target_satisfied: Director must not proceed before each lifecycle mutation if Pipeline route changes, target HEAD/worktree differs from the Director-controlled current Task commit state, the name exists or falls outside the allowlist, endpoint/DSN/migration root differs, a non-synthetic value or real workbook path enters the run, cleanup fails, or any command targets postgres, a canonical/remote database, canonical workbook/resource, push, publication, or deployment
- postcheck: every successfully created name is recorded before migration and absent from pg_database after its finally/dropdb cleanup; no migration is applied to postgres; no retry occurs over a partial database; target git status contains only the current routed task paths before Director commit and is clean after each accepted task; no generated workbook, dump, credential, report, business value, data directory, or .superpowers evidence is tracked
- observer_seats: coordinator, operator, director2, operator2
- final_closeout_owner: coordinator
- non_goals: no real-data scratch clone/apply, user workbook read/copy, canonical database/resource activation, normal-checkout mutation, service stop, container/volume deletion, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

## Side-Effect Executor Token

- side_effect_id: ledger-workbook-refresh-synthetic-token-route-2026-07-11
- executor: coordinator
- target: local route mutation limited to coordination/mailbox/sent/2026-07-11T09-42-22Z-coordinator-to-all-coordination.md
- allowed_command_class: create this route through apply_patch, stage only this ignored path with env -u GIT_INDEX_FILE git add -f, verify the cached name is exactly this path, and make one local coordinator commit; no other mutation class
- preflight: Pipeline HEAD is fbd0478; target worktree is clean at 059bea28b9e0de9a53c05fffb3e9e9217dfd7d40; capacity is valid; coordinator unread is zero; request fbd0478 is the newest Director token request; unrelated Pipeline WIP does not overlap this route
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if HEAD moves from fbd0478, newer coordinator mail or another token route lands, this path gains peer WIP, target state changes, capacity becomes invalid, or another committed route already grants these exact side-effect IDs
- postcheck: coordinator commit is a direct child of fbd0478; cached and committed scope contains exactly this route; board and route validate; doctor, smoke, diff checks, all-seat route visibility, and target cleanliness pass
- observer_seats: director, operator, director2, operator2, coordinator2
- final_closeout_owner: coordinator
- non_goals: no product/spec/plan/packet edit, service or database action by coordinator, real workbook read, scratch/canonical mutation, checkout refresh, cursor consume, remote update, push, force update, lock action, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or deployment

Join condition: Tasks 2–4 remain open until Director uses Token A only as
needed, uses Token B only for synthetic scratch databases, cleans every created
name, completes fresh implementation/spec/quality loops, and reports each
accepted commit plus service/database postchecks. Real-data scratch and
canonical activation still require later separate coordinator tokens.

## Exact Next Trigger

Director refreshes to this route, rechecks exact target state, executes Token A
read-only health preflight and conditional start, records its postchecks, then
uses Token B while implementing Tasks 2–4 sequentially. Director stops and
reports any token stop condition; Operator, Director2, and Operator2 take no
action.
