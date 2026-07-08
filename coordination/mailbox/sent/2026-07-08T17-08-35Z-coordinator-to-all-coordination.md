# Coordinator -> All: Ledger Phase 2 Task 2.4 Capacity Split Addendum

**When:** 2026-07-08T17:08:35Z - **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-task24-2026-07-08`
Route base: `bdc7f6b8aef74eddeb35993f18d7bef48fd2a58f`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`

Worktree-name note: the route reuses the isolated Task 2.3 worktree name; the
task-board, route base, and target commit/range define the active Task 2.4
scope.

## Outcome

This addendum supersedes the Pair B observer-standby portion of
`coordination/mailbox/sent/2026-07-08T15-29-17Z-coordinator-to-all-coordination.md`
without changing the director/operator Task 2.4 implementation and Lane V
boundary.

The current Task 2.4 implementation remains single-pair because the iOS slot
entry form touches one coherent UI/API/validation surface in the routed
worktree. Pair B is no longer idle observer-standby: director2 owns bounded
planning/preflight for the next ledger Phase 2 slice, and operator2 owns
read-only route/preflight verification. Neither Pair B seat may duplicate
director Task 2.4 implementation work or operator Task 2.4 Lane V.

This route does not grant publication, force-push, lock action, paid API spend,
pod spend, production generation, normal evidence-ledger checkout refresh,
evidence-ledger main refresh, real-data/config edits, cursor consumption, or
coordinator-mail consumption.

## Capacity Split Default

- single-pair fast path remains the default for narrow or shared-file work.
- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.
- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.

Capacity split decision: Task 2.4 stays on the single-pair fast path for the
implementation/verification lane, while Pair B performs bounded planning or
preflight. The next coordinator route must re-ask whether the next slice can
produce two independently reviewable deliverables and, if yes, use dual-pair
routing with explicit Chunk A and Chunk B write sets.

## Capacity Packet Coverage

Capacity packet coverage list:
- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `coord-ledger-phase2-task22-join`
- `coord-ledger-phase2-task23-join`
- `coord-ledger-phase2-task24-join`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `coord-unit-coherence-side-effect-token-join`
- `director-execution-strength-broader-impl`
- `director-governance-hardening-bridge-impl`
- `director-ledger-phase2-task21-write-path`
- `director-ledger-phase2-task22-validations`
- `director-ledger-phase2-task23-result-history`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director-ledger-publication-decision`
- `director-ledger-runway-stage0-owner-gates`
- `director-unit-coherence-side-effect-token-impl`
- `director2-execution-strength-broader-observer`
- `director2-governance-hardening-bridge-observer`
- `director2-ledger-next-brief`
- `director2-ledger-phase2-bounds-plan-sync`
- `director2-ledger-phase2-task22-observer`
- `director2-ledger-phase2-task23-observer`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `director2-ledger-runway-plan-reconcile`
- `director2-unit-coherence-observer-standby`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-execution-strength-broader-observer`
- `operator2-governance-hardening-bridge-observer`
- `operator2-ledger-main-verify`
- `operator2-ledger-phase2-base-preflight`
- `operator2-ledger-phase2-task22-observer`
- `operator2-ledger-phase2-task23-observer`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
- `operator2-ledger-runway-worktree-verify`
- `operator2-unit-coherence-observer-standby`

Coordinator join packet: `coord-ledger-phase2-task24-join`.
Director implementation packet: `director-ledger-phase2-task24-ios-slot-entry`.
Operator verification packet: `operator-ledger-phase2-task24-lanev`.
Director2 planning/preflight packet: `director2-ledger-phase2-task24-planning-preflight`.
Operator2 preflight packet: `operator2-ledger-phase2-task24-preflight`.
Superseded director2 observer packet: `director2-ledger-phase2-task24-observer`.
Superseded operator2 observer packet: `operator2-ledger-phase2-task24-observer`.

## Seat Assignments

Director keeps the existing Task 2.4 implementation assignment from the prior
route. Director must start from Pipeline, run `ledger_start_guard.py --seat
director --wave 2`, read this active addendum, use the route worktree/base, and
send exactly one verify-request to operator after the implementation diff lands.

Operator remains blocked until director sends a Task 2.4 verify-request.
Operator verifies only the named Task 2.4 diff and returns GO/NITS/FAIL.

Director2 owns `director2-ledger-phase2-task24-planning-preflight`: inspect only
the routed worktree docs/progress state, decide whether the next Phase 2 slice
can split into two independently reviewable deliverables, and report the
smallest next brief or owner-question packet to coordinator. Director2 must not
edit evidence-ledger product code or duplicate director Task 2.4 work.

Operator2 owns `operator2-ledger-phase2-task24-preflight`: run read-only
route/base/worktree, presence/lock, selector, and stale-checkout preflight for
Task 2.4 and the next Phase 2 route. Operator2 must not verify the director
implementation until operator receives the Task 2.4 verify-request, and must not
create duplicate success mail.

Subagent utilization decision: direct/no-op for this coordinator addendum. The
change is a narrow capacity-packet and route-state correction; live seats may
use bounded helpers inside their own authority after orientation.

Join condition: coordinator closes this cycle only after director lands the
Task 2.4 diff, operator sends GO/NITS/FAIL, director2 reports the next-slice
planning/preflight result, operator2 reports route/preflight readiness or a
contradiction, capacity board is valid, route validation passes for this route,
smoke is OK, and the closeout cites the implementation commit/range and
operator verdict.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2` after the capacity-split validator was added initially failed with G10 on the old Pair B observer packets.
- Old Pair B observer packets were closed as superseded, and new ready packets were added for director2 planning/preflight and operator2 route/preflight.
- This addendum preserves the Task 2.4 director/operator implementation and Lane V boundary from `coordination/mailbox/sent/2026-07-08T15-29-17Z-coordinator-to-all-coordination.md`.

## Exact Next Trigger

`continue as director2` to execute `director2-ledger-phase2-task24-planning-preflight`, or `continue as operator2` to execute `operator2-ledger-phase2-task24-preflight`, while `continue as director` remains valid for the Task 2.4 implementation lane.

Cursor at send: 0
