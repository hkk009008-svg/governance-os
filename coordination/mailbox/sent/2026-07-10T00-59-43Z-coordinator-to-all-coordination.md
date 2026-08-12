# Coordinator -> All: Control-Plane Authority Foundation Route

**When:** 2026-07-10T00:59:43Z - **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Prior closeout: `coordination/mailbox/sent/2026-07-09T05-40-25Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Route branch: `codex/control-plane-authority-foundation-2026-07-10`
Implementation plan: `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`

## Outcome

This cycle opens the first dependency-safe slice of the approved control-plane
hardening program. Pair A implements plan Tasks 1 and 2: an explicit channel
authority manifest and the separation of human-mailbox state from signed-fact
cursors. Pair B performs bounded preflight for the next identity and cutover
slice.

The user's signed-bus activation decision is recorded in the approved design
and plan. This first slice intentionally commits signed-facts authority as
`shadow`; the live transition remains the later, double-gated Task 6 after the
trust root, cutover tooling, and postchecks exist. Human Markdown mail remains
the live coordination channel throughout.

No remote publication, signing-key creation, signed-ref mutation, mailbox
cursor consumption, lock action, paid-service spend, pod action, or production
generation is granted by this route.

## Capacity Split Default

- Single-pair fast path remains the default for narrow or shared-file work.
- If the implementation cannot be split safely, one pair implements while
  Pair B performs bounded planning or preflight.
- Coordinator owns convergence: capacity packets, one consolidated route, the
  join condition, conflict handling, and closeout evidence.

Capacity split decision: Tasks 1 and 2 are sequential on the same authority
seam, so concurrent implementation would create shared-file and semantic
collisions. Director owns the two-commit implementation lane and Operator owns
Lane V. Director2 preflights Task 3 design/write-set sufficiency; Operator2
preflights Tasks 4 and 5 execution safety and test feasibility. This is the
bounded-preflight branch of the Capacity Split Default.

## Capacity Packet Coverage

Capacity packet coverage list:
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
- `coord-unit-coherence-side-effect-token-join`
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
- `director-unit-coherence-side-effect-token-impl`
- `director2-control-plane-authority-foundation-identity-preflight`
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
- `director2-unit-coherence-observer-standby`
- `operator-control-plane-authority-foundation-lanev`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-phase2-task25a-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
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
- `operator2-unit-coherence-observer-standby`

Active coordinator join packet:
`coord-control-plane-authority-foundation-join`.
Active Director implementation packet:
`director-control-plane-authority-foundation-tasks1-2`.
Blocked Operator verification packet:
`operator-control-plane-authority-foundation-lanev`.
Active Director2 preflight packet:
`director2-control-plane-authority-foundation-identity-preflight`.
Active Operator2 preflight packet:
`operator2-control-plane-authority-foundation-cutover-preflight`.

## Seat Assignments

Director owns `director-control-plane-authority-foundation-tasks1-2`. Start
from Pipeline, run the Wave-2 start guard and seat status, read the newest
same-seat handoff and this route, create the routed worktree only under the
executor token below, then execute plan Tasks 1 and 2 only. Keep them as two
separate TDD commits, capture the prescribed RED/GREEN/non-vacuity evidence,
dispatch a fresh implementer, fresh spec reviewer, and fresh quality reviewer
for each task, cite all six review artifacts and dispositions, and send one
verify-request with the full two-commit range. Task 1 appends ADR-012 before
the manifest cites it. Initial signed-facts authority stays `shadow`.

Operator owns `operator-control-plane-authority-foundation-lanev`. Remain
blocked until the fresh Director verify-request names the exact range. Then
inspect the range independently, rerun focused selectors and mutation flips,
adversarially verify channel separation and unpinned coordinator behavior, and
return exactly one GO, NITS, or FAIL report. Operator does not repair the diff.

Director2 owns
`director2-control-plane-authority-foundation-identity-preflight`. Perform
read-only Task-3 design/interface/write-set preflight, including the complete
runtime-identity caller matrix and every mismatch case that affects the next
route. Report clear or contradiction once to coordinator; do not edit code.

Operator2 owns
`operator2-control-plane-authority-foundation-cutover-preflight`. Perform
read-only Tasks-4/5 environment and verification-feasibility preflight:
current signed-ref state, selector availability, fixture feasibility, roster
completeness, dry-run non-mutation, duplicate-cutover refusal, key idempotence,
and private-key non-tracking. Report clear or blocked once to coordinator; do
not create keys or refs and do not execute cutover.

Coordinator owns `coord-control-plane-authority-foundation-join`. Reconcile
durable reports only; do not author production fixes. The coordinator route
artifact was authored directly because it is narrow and authority-sensitive.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-worktree-create-2026-07-10`
- executor: `director`
- target: local branch `codex/control-plane-authority-foundation-2026-07-10` and worktree `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10` in `/Users/hyungkoookkim/Pipeline`, based at `78b48ed493899dd126de2d1764cbdbf022111dfd`
- allowed_command_class: `env -u GIT_INDEX_FILE git worktree add -b codex/control-plane-authority-foundation-2026-07-10 /Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10 78b48ed493899dd126de2d1764cbdbf022111dfd`
- preflight: confirm refreshed mail names this route, Pipeline HEAD contains route commit, the target path is absent, the target branch is absent, the shared worktree has no unrelated changes, and the named base resolves exactly
- stop_if_newer_mail_or_live_target_satisfied: stop without mutation if newer coordinator mail supersedes this token, the path or branch already exists, the named base no longer matches the routed plan boundary, or unrelated worktree changes appear
- postcheck: `git worktree list --porcelain` names the exact path and branch, the new branch resolves to the named base before implementation, and `git -C /Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10 status --short --branch` is clean
- observer_seats: `operator`, `director2`, `operator2`, `coordinator`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: remote-ref update/push, force update, target-repo checkout refresh, signing-key or secret creation, signed-ref mutation, lock action, paid-service spend, pod action, production generation, cursor consume, route mutation, merge, rebase, or any additional branch/worktree

Join condition: coordinator may close this cycle only after Director's two
implementation commits and verify-request exist, that request cites the fresh
implementer/spec-review/quality-review artifact and disposition for each task,
Operator reports GO for that exact range, Director2 reports no Task-3 route-changing contradiction,
Operator2 reports no Tasks-4/5 safety blocker, the worktree/branch token has
one executor and a clean postcheck, capacity board and route validation are
valid, protocol doctor passes, smoke is OK, and closeout cites every artifact.
NITS, FAIL, a preflight blocker, a changed write set, or a newer route causes
bounded rerouting instead of closeout.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2`
  -> PASS; the prior active route was the 2026-07-09 detail-integration closeout.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2`
  -> HEAD `3fbd984`, 44 commits ahead of the local `origin/main` snapshot, Wave
  2 MET; the known false-clean mailbox surface still renders `0 / ref-bus`.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2`
  -> `valid: true`, packet state `active`, all five routed actors represented,
  no blocking issues.
- `test ! -e /Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
  -> worktree path absent at route preflight.
- `env -u GIT_INDEX_FILE git branch --list codex/control-plane-authority-foundation-2026-07-10`
  -> no output at route preflight.
- `env -u GIT_INDEX_FILE git rev-parse 78b48ed`
  -> `78b48ed493899dd126de2d1764cbdbf022111dfd`, matching the approved plan
  and every executor-token boundary.
- `env -u GIT_INDEX_FILE git for-each-ref --format='%(refname)' refs/threeway/`
  -> no signed-bus refs at route preflight; this route does not create them.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
  -> project smoke OK; ceremony, placeholder, GO-schema, and architecture
  freshness checks PASS.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route coordination/mailbox/sent/2026-07-10T00-59-43Z-coordinator-to-all-coordination.md`
  -> `route valid: true`; no blocking issues.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2 --route coordination/mailbox/sent/2026-07-10T00-59-43Z-coordinator-to-all-coordination.md`
  -> `PROTOCOL DOCTOR: PASS`; 114 focused tests passed, capacity board and
  route validation passed, and smoke returned OK.
- Independent semantic route review found and this route corrected the plan
  base mismatch, missing ADR anchor sequencing, weakened mandatory review
  evidence, and incorrect Pair-B preflight paths before commit.

## Exact Next Trigger

`continue as director` to execute
`director-control-plane-authority-foundation-tasks1-2`; `continue as
director2` and `continue as operator2` may execute their bounded preflight
packets now. `operator` waits for the Director verify-request.

Cursor at send: 0
