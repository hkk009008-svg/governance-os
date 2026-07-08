# Coordinator -> All: Ledger Phase 2 Task 2.4 Route

**When:** 2026-07-08T15:29:17Z - **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-task24-2026-07-08`
Route base: `bdc7f6b8aef74eddeb35993f18d7bef48fd2a58f`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`

## Outcome

The next ledger implementation slice is active: Phase 2 Task 2.4, iOS slot
entry form (`계획`).

This route does not authorize publication, force-push, lock action, paid API
spend, pod spend, production generation, normal evidence-ledger checkout
refresh, evidence-ledger main refresh, real-data/config edits, cursor
consumption, or coordinator-mail consumption.

The normal target checkout at `/Users/hyungkoookkim/evidence-ledger` is stale
for this route. Director must start from Pipeline, read this route, then use the
route worktree/base above.

## Capacity Packet Coverage

Capacity packet coverage list:
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `director-ledger-publication-decision`
- `director2-ledger-next-brief`
- `operator-pipeline-tooling-verify`
- `operator2-ledger-main-verify`
- `coord-execution-strength-broader-join`
- `director-execution-strength-broader-impl`
- `director2-execution-strength-broader-observer`
- `operator-execution-strength-broader-verification`
- `operator2-execution-strength-broader-observer`
- `coord-governance-hardening-bridge-join`
- `director-governance-hardening-bridge-impl`
- `director2-governance-hardening-bridge-observer`
- `operator-governance-hardening-bridge-lanev`
- `operator2-governance-hardening-bridge-observer`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `director-ledger-phase2-task21-write-path`
- `director2-ledger-phase2-bounds-plan-sync`
- `operator-ledger-phase2-task21-lanev`
- `operator2-ledger-phase2-base-preflight`
- `coord-ledger-phase2-task22-join`
- `director-ledger-phase2-task22-validations`
- `director2-ledger-phase2-task22-observer`
- `operator-ledger-phase2-task22-lanev`
- `operator2-ledger-phase2-task22-observer`
- `coord-ledger-phase2-task23-join`
- `director-ledger-phase2-task23-result-history`
- `director2-ledger-phase2-task23-observer`
- `operator-ledger-phase2-task23-lanev`
- `operator2-ledger-phase2-task23-observer`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `director-ledger-runway-stage0-owner-gates`
- `director2-ledger-runway-plan-reconcile`
- `operator-ledger-runway-stage0-verify`
- `operator2-ledger-runway-worktree-verify`
- `coord-unit-coherence-side-effect-token-join`
- `director-unit-coherence-side-effect-token-impl`
- `director2-unit-coherence-observer-standby`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-unit-coherence-observer-standby`
- `coord-ledger-phase2-task24-join`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director2-ledger-phase2-task24-observer`
- `operator-ledger-phase2-task24-lanev`
- `operator2-ledger-phase2-task24-observer`

Coordinator join packet: `coord-ledger-phase2-task24-join`.
Director implementation packet: `director-ledger-phase2-task24-ios-slot-entry`.
Operator verification packet: `operator-ledger-phase2-task24-lanev`.
Director2 observer packet: `director2-ledger-phase2-task24-observer`.
Operator2 observer packet: `operator2-ledger-phase2-task24-observer`.

## Director Scope

Director owns a narrow evidence-ledger implementation for Phase 2 Task 2.4:

- add failing iOS unit tests for `RecordOutcome` decoding and mirrored client
  validation;
- add `EntryAPI.recordSlot(_:)` using the existing Supabase client and
  `JSONDecoder.postgrest`;
- add pure `EntryValidation` functions for the client mirror;
- add `SlotEntryView` reachable from `BroadcastListView` toolbar `+`, with
  Korean form sections, busy/error states, warning rendering, and read-only
  post-save `biz.slot_pnl` preview;
- keep Task 2.3 publication as a separate user-gated boundary.

Director should run evidence-ledger R-START, focused iOS tests,
`SIM_DEVICE="iPhone 17 Pro" scripts/ci_local.sh`, `git diff --check`, and any
touched-doc verification. If local simulator/tooling is unavailable, director
must report the exact command output and preserve the unverifiable boundary.

## Observer And Verification Boundary

Operator remains blocked until director sends a Task 2.4 verify-request.
Operator verifies only the named diff and returns GO/NITS/FAIL.

Director2 and operator2 are observer-standby. They should report only
contradiction, missing required evidence, changed safety boundary, or explicit
coordinator request; they should not duplicate success mail.

Subagent utilization decision: direct/no-op for coordinator. This route is a
single authority-sensitive coordinator artifact; director/operator may use
bounded helpers within their own seat rules.

Join condition: coordinator closes this cycle only after director lands the
Task 2.4 diff, operator sends GO/NITS/FAIL, director2/operator2 observer state
is accounted for, capacity board is valid, route validation passes for this
route, smoke is OK, and the closeout cites the implementation commit/range and
operator verdict.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2` -> PASS; previous active route `coordination/mailbox/sent/2026-07-08T15-20-01Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/mailbox_monitor.py --once` -> latest coordinator broadcast `2026-07-08T15-20-01Z-coordinator-to-all-coordination.md`; unread 0 for all seats; receipt unknown alert preserved.
- `env -u GIT_INDEX_FILE git log --oneline -5` -> top commit `aa5f9b2 coord(coordinator): close governance bridge cycle`.
- `env -u GIT_INDEX_FILE git status --short --branch` -> `## main...origin/main`.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --require-packets` before this route was written -> valid: true; no current actor packets; `BLOCKING ISSUES - none`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short --branch` -> `## main...origin/main [behind 3]`, so normal checkout is stale for product edits.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger ls-remote origin refs/heads/main` -> `36f55063a2d87312810e82db624b837289a4a382 refs/heads/main`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 status --short --branch` -> `## codex/ledger-phase2-task23-pipeline-2026-07-08`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 log --oneline -3` -> top commit `bdc7f6b feat(db): add result_history audit view`.
- Read `docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md` Task 2.4 and inspected real iOS paths under the route worktree.

## Exact Next Trigger

`continue as director` to implement `director-ledger-phase2-task24-ios-slot-entry`, then send one verify-request to operator for `operator-ledger-phase2-task24-lanev`.

Cursor at send: 0
