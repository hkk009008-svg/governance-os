# Coordinator → All: Evidence-Ledger Workbook Refresh Route

**When:** 2026-07-11T06:57:33Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-workbook-refresh-2026-07-11`
Supersedes active route: `coordination/mailbox/sent/2026-07-10T22-47-55Z-coordinator-to-all-coordination.md`
Pipeline authority: `62d6e5d`, `e2ff411`, `4b6ceed`
Target published base: `36f55063a2d87312810e82db624b837289a4a382`
Target branch: `codex/ledger-workbook-refresh-2026-07-11`
Target worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Cursor at send: 0

## Durable Disposition

- The user approved the source-scoped design and written specification, then
  selected routed subagent-driven execution (option 1). The incoming
  `/Users/hyungkoookkim/Downloads/260710.xlsx` is a cumulative refresh of the
  internal `excel_import` lane, not a second additive import.
- Commit `4b6ceed` closes two execution-contract gaps before product work: the
  live Director is the single target controller/committer with fresh bounded
  subagents and Operator is the independent verifier; the database contract
  separately binds a stable business-state fingerprint and the mutable
  evidence-chain head.
- The control-plane authority cycle is parked, not closed or excepted. Its
  coordinator join and Task2U Director packets are blocked on
  `coord-ledger-workbook-refresh-join`. Preserve the nine-file unstaged Task2U
  worktree at `6983673db60bff0d21548a90ab1db2fcbbfa377a` exactly as reported in
  `2026-07-11T00-06-19Z-director-to-coordinator-coordination.md`; do not clean,
  stage, commit, reset, rebase, or continue it without a fresh post-refresh
  coordinator route.
- The orthogonal `2026-07-11T00-11-01Z` Director2 → Operator2 cross-provider
  reverify request is also parked without a verdict. No receipt, consume, or
  invented verification outcome is authorized during this user-priority
  cycle.
- The target repo's one-controller rule remains intact. The user-principal's
  explicit option-1 choice is the narrow cycle-specific override permitting
  fresh Codex implementer/fix subagents where target R-OPUS-IMPL otherwise
  names opus; it does not amend the standing target doctrine and does not
  create a second committer.

## Capacity Split Default

The single-pair fast path owns implementation and independent cumulative
verification: Director is the sole evidence-ledger controller/committer and
Operator performs Lane V only after the cumulative verify-request. Pair B uses
the bounded planning or preflight branch: Director2 checks the approved
contract/write set and Operator2 checks base, isolation, tooling, and future
verification feasibility. The four deliverables are independently reviewable;
no two implementation lanes share files. Coordinator owns convergence.

## Seat Assignments

### Director — implementation controller

Own `director-ledger-workbook-refresh-implementation`. Start from Pipeline,
run the Director ledger guard/status, read this route and target instructions,
then use only the worktree token below. Run the service-free baseline before
edits. Execute plan Tasks 1–6 sequentially with a fresh implementer, fresh
specification reviewer, and fresh quality reviewer per task; maintain the
ignored SDD progress/review ledger; commit one bounded task at a time. Obtain
separate coordinator tokens before local service start, synthetic DB mutation,
real-data scratch work, or canonical activation. After reviewed Tasks 1–6,
execute Task 7 only under its future scratch token and send one cumulative
verify-request. No canonical DB/resource mutation is authorized now.

### Operator — blocked cumulative verifier

Own `operator-ledger-workbook-refresh-lanev`. Stay blocked until Director's
cumulative verify-request names the exact Tasks 1–7 range and evidence. Then
inspect the actual diff and rerun the named verification independently. Any
scratch DB/resource rehearsal requires a separate Operator token. Return one
GO/NITS/FAIL; never repair code or touch canonical data.

### Director2 — contract preflight

Own `director2-ledger-workbook-refresh-preflight`. Perform one bounded
read-only preflight over the approved Pipeline spec/plan, target instructions,
fresh worktree base, twenty-file write set, source-priority fences, evidence
contract, resource compensation, and direction/report separation. Report one
GO-for-route, contradiction, or missing-evidence artifact to coordinator
before product edits can outrun a route-changing issue.

### Operator2 — execution preflight

Own `operator2-ledger-workbook-refresh-preflight`. Perform one bounded
read-only preflight of published base, branch/worktree isolation, primary venv,
baseline commands, ignored real-data paths, service boundary, and likely
Operator selectors. Report one preflight verdict to coordinator. This is not
Lane V and does not dispose the parked cross-provider request.

### Coordinator — join only

Own `coord-ledger-workbook-refresh-join`. Reconcile durable seat artifacts,
issue narrowly target-bound executor tokens when their preconditions are
satisfied, and close only after canonical activation plus all-seat visibility.
Do not edit evidence-ledger product files or copy real business figures into
Pipeline artifacts.

## Scope And Stop Conditions

The Director and later Operator scopes are the exact twenty product/doc paths
named in their packets. Ignored `.superpowers/sdd/workbook-refresh-*` evidence
and one Pipeline mailbox baton are allowed; workbook bytes, `data/`, dumps,
credentials, generated readouts, and real figures are never committed.

Stop and report one bounded contradiction if the published base moves, the
branch/path exists, baseline fails for a product reason, a twenty-first product
path is required, an owner/checklist/source conflict appears, any blocker
disposition remains, a review fails, expected-old/evidence-head checks cannot
be made non-vacuous, canonical state changes during scratch work, or a newer
coordinator route supersedes this one.

## Capacity Packet Coverage

All 87 Wave-2 packet IDs are named for route-validator completeness. Only the
five `ledger-workbook-refresh-2026-07-11` packets are selected for this cycle;
the two formerly active control-plane packets are explicitly parked above and
all remaining historical packets retain their durable states.

- `coord-control-plane-authority-foundation-join`
- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
- `coord-ledger-phase2-detail-integration-join`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `coord-ledger-phase2-task22-join`
- `coord-ledger-phase2-task23-join`
- `coord-ledger-phase2-task24-join`
- `coord-ledger-phase2-task25-26-join`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `coord-ledger-workbook-refresh-join`
- `coord-unit-coherence-side-effect-token-join`
- `director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`
- `director-control-plane-authority-foundation-task2-race-fix`
- `director-control-plane-authority-foundation-task2-replacement`
- `director-control-plane-authority-foundation-task2-spec-review-fix`
- `director-control-plane-authority-foundation-task2u-fail-closed-closure`
- `director-control-plane-authority-foundation-tasks1-2`
- `director-execution-strength-broader-impl`
- `director-governance-hardening-bridge-impl`
- `director-ledger-phase2-detail-integration`
- `director-ledger-phase2-task21-write-path`
- `director-ledger-phase2-task22-validations`
- `director-ledger-phase2-task23-result-history`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director-ledger-phase2-task25a-result-entry`
- `director-ledger-publication-decision`
- `director-ledger-runway-stage0-owner-gates`
- `director-ledger-workbook-refresh-implementation`
- `director-unit-coherence-side-effect-token-impl`
- `director2-control-plane-authority-foundation-identity-interface-closure-preflight`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
- `director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight`
- `director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`
- `director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight`
- `director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight`
- `director2-control-plane-authority-foundation-task3h-causal-runtime-proof-closure-preflight`
- `director2-control-plane-authority-foundation-task3i-execution-contract-closure-preflight`
- `director2-execution-strength-broader-observer`
- `director2-governance-hardening-bridge-observer`
- `director2-ledger-next-brief`
- `director2-ledger-phase2-bounds-plan-sync`
- `director2-ledger-phase2-detail-integration-preflight`
- `director2-ledger-phase2-task22-observer`
- `director2-ledger-phase2-task23-observer`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `director2-ledger-phase2-task26a-history-component`
- `director2-ledger-runway-plan-reconcile`
- `director2-ledger-workbook-refresh-preflight`
- `director2-unit-coherence-observer-standby`
- `operator-control-plane-authority-foundation-lanev`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `operator-control-plane-authority-foundation-task2u-cumulative-lanev`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-phase2-task25a-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-ledger-workbook-refresh-lanev`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-control-plane-authority-foundation-activation-repreflight`
- `operator2-control-plane-authority-foundation-cutover-preflight`
- `operator2-execution-strength-broader-observer`
- `operator2-governance-hardening-bridge-observer`
- `operator2-ledger-main-verify`
- `operator2-ledger-phase2-base-preflight`
- `operator2-ledger-phase2-detail-integration-preflight`
- `operator2-ledger-phase2-task22-observer`
- `operator2-ledger-phase2-task23-observer`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
- `operator2-ledger-phase2-task26a-lanev`
- `operator2-ledger-runway-worktree-verify`
- `operator2-ledger-workbook-refresh-preflight`
- `operator2-unit-coherence-observer-standby`

## Side-Effect Executor Token

- side_effect_id: `ledger-workbook-refresh-route-mutation-2026-07-11`
- executor: `coordinator`
- target: local route mutation limited to `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director-task2u-fail-closed-closure.json`, `coordination/capacity/packets/2026-07-11-ledger-workbook-refresh-coordinator-join.json`, `coordination/capacity/packets/2026-07-11-ledger-workbook-refresh-director-implementation.json`, `coordination/capacity/packets/2026-07-11-ledger-workbook-refresh-operator-lanev.json`, `coordination/capacity/packets/2026-07-11-ledger-workbook-refresh-director2-preflight.json`, `coordination/capacity/packets/2026-07-11-ledger-workbook-refresh-operator2-preflight.json`, and `coordination/mailbox/sent/2026-07-11T06-57-33Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, strict-pathspec `env -u GIT_INDEX_FILE git add` for seven visible packet paths, `env -u GIT_INDEX_FILE git add -f` for the ignored route, cached-name verification of exactly eight paths, and one local coordinator commit; no other mutation class
- preflight: user approved the written specification and selected option 1; expected Pipeline HEAD is `4b6ceed`; coordinator unread is zero; the prior active route is `2026-07-10T22-47-55Z`; the capacity board with this draft shape is valid at 87 packets with no blocking issues; the parked worktree remains at `6983673` with exactly nine unstaged routed files; evidence-ledger origin/main is `36f55063a2d87312810e82db624b837289a4a382`; the target branch/path are absent; unrelated Pipeline WIP is preserved and does not overlap these eight paths
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if Pipeline HEAD moves from `4b6ceed`, newer coordinator mail or a conflicting route lands, any of the eight paths has peer WIP, capacity becomes invalid, the parked worktree or its nine-file status changes, the target branch/path appears, origin/main moves, or another committed route already satisfies this request
- postcheck: the coordinator commit is a direct child of `4b6ceed`; cached and committed scope contains exactly the eight named paths; all seven JSON files parse; the capacity board and this route validate; protocol doctor, smoke, diff checks, and all-seat visibility pass; coordinator made no evidence-ledger or parked-worktree edit
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no evidence-ledger product edit, canonical database/resource mutation, local service start, database create/drop, real-data scratch apply, normal target-checkout refresh, additional worktree, amend/reset/rebase/squash, lock action, cursor consume, remote-ref update/push, force update, paid-service spend, pod action, production generation, merge, publication, or external deployment

## Side-Effect Executor Token

- side_effect_id: `ledger-workbook-refresh-worktree-create-2026-07-11`
- executor: `director`
- target: local evidence-ledger branch `codex/ledger-workbook-refresh-2026-07-11` and worktree `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11` in `/Users/hyungkoookkim/evidence-ledger`, based exactly at `36f55063a2d87312810e82db624b837289a4a382`
- allowed_command_class: `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger worktree add -b codex/ledger-workbook-refresh-2026-07-11 /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11 36f55063a2d87312810e82db624b837289a4a382`; no fetch, pull, checkout refresh, or second worktree
- preflight: confirm refreshed Director mail names this committed route; `git ls-remote origin refs/heads/main` still returns exactly `36f55063a2d87312810e82db624b837289a4a382`; local `origin/main` and the base object resolve to that OID; the branch is absent locally and remotely; the worktree path is absent and unregistered; the normal evidence-ledger checkout remains clean and untouched; Pipeline ignores `.worktrees/`
- stop_if_newer_mail_or_live_target_satisfied: stop without mutation if newer coordinator mail supersedes this token, origin/main moves, the branch or path exists, the base object differs, the normal target checkout gains WIP, or another committed worktree already satisfies the route
- postcheck: `git worktree list --porcelain` names the exact path and branch; the new branch and worktree HEAD equal `36f55063a2d87312810e82db624b837289a4a382`; `git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11 status --short --branch` is clean; the normal checkout HEAD/status are unchanged; Director then runs the documented service-free baseline before edits
- observer_seats: `operator`, `director2`, `operator2`, `coordinator`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no fetch/pull, normal target-checkout refresh, additional branch/worktree, product edit within this token, local service start, database create/drop, real-data scratch or canonical mutation, lock action, cursor consume, remote-ref update/push, force update, paid-service spend, pod action, production generation, merge, rebase, reset, amend, publication, or external deployment

Join condition: coordinator closes this cycle only after Director completes the
reviewed implementation and scratch rehearsal, Operator returns GO for the
exact cumulative range under an independent scratch token, Pair B preflights
are durably reconciled, a fresh zero-blocker real-data plan still matches the
reviewed code and target state, the coordinator issues one exact canonical
activation token, the sole Director activation succeeds, postchecks prove the
business fingerprint and final evidence-chain head plus resource/report hashes,
the local unified directional readout is generated without tracked figures,
all seats can see the closeout, and capacity/route/doctor/smoke pass. No remote
publication or other forbidden side effect may occur. NITS, FAIL,
contradiction, blocker,
changed scope/base/plan, or activation uncertainty causes bounded rerouting
instead of closeout.

## Evidence At Route Preflight

- `ledger_start_guard.py --seat coordinator --wave 2` → PASS against the prior
  control-plane route; the coordinator did not enter evidence-ledger.
- `seat_status.py coordinator --wave 2` → Pipeline HEAD `4b6ceed` after the
  approved contract correction, unread `0 / ref-bus`, Wave 2 MET.
- `protocol_capacity_board.py --wave 2 --json` on the draft packet shape →
  valid, 87 packets, no blocking issues; four new packets ready and the new
  Operator packet blocked on Director.
- `git ls-remote origin refs/heads/main` in evidence-ledger → exact published
  base `36f55063a2d87312810e82db624b837289a4a382`; local `origin/main` matched;
  no fetch occurred.
- target branch/path checks → both absent; the normal evidence-ledger checkout
  was clean and behind published main, so it is not the implementation base.
- parked control-plane worktree check → HEAD `6983673`, nine unstaged routed
  files, no staged files; this route does not touch it.
- `scripts/ci_smoke.py` → project smoke, ceremony, placeholder, GO-schema, and
  architecture-freshness checks PASS before route staging.

## Exact Next Trigger

After this eight-path coordinator route commit validates and all-seat
visibility is confirmed, Director uses only
`ledger-workbook-refresh-worktree-create-2026-07-11`; Director2 and Operator2
run their bounded read-only preflights in parallel; Operator remains blocked
until Director's cumulative Tasks 1–7 verify-request.
