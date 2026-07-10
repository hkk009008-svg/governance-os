# Coordinator → All: Control-Plane Authority Foundation Bounded Reroute

**When:** 2026-07-10T02:42:37Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T00-59-43Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task-1 commit: `e43acc245e2492883ca04b0d835268708ad0995d`
Revised design: `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`
Revised implementation plan: `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`

## Outcome

This one bounded reroute reconciles all three durable route-changing reports:

- Director's Task-2 write-set blocker at
  `coordination/mailbox/sent/2026-07-10T02-01-34Z-director-to-coordinator-coordination.md`;
- Director2's Task-3 identity contradiction at
  `coordination/mailbox/sent/2026-07-10T01-26-00Z-director2-to-coordinator-coordination.md`;
- Operator2's Tasks-4/5 activation blocker at
  `coordination/mailbox/sent/2026-07-10T01-23-27Z-operator2-to-coordinator-coordination.md`.

The user-principal selected `verified-exact resume`. A repeated local cutover
may proceed only while signed-fact authority remains `shadow` and the complete
managed-ref set exactly matches the committed activation manifest. Resume
performs no ref rewrite and may finish only the durable `live` marker. Partial,
extra, mismatched, changed-HEAD/digest, or already-`live` state fails closed.

This route resumes only Task 2 implementation. Revised Tasks 3A-3D and 4-6C
return to focused read-only preflight. No key, ref, authority, cursor, lock,
remote, spend, pod, production-generation, or target-checkout side effect is
granted.

## Capacity Split Default

- Single-pair fast path remains the default for narrow or shared-file work.
- Divisible or preplanned larger work defaults to dual-pair routing.
- When implementation is not safely divisible, one pair implements while Pair
  B performs bounded planning or preflight.
- Coordinator owns convergence, one consolidated route, join conditions,
  conflict handling, and final closeout evidence.

Capacity decision: Director resumes the one remaining Task-2 commit in the
existing isolated worktree. Operator remains blocked for Lane V. Director2 and
Operator2 independently repreflight disjoint plan domains without edits.

## Capacity Packet Coverage

Current packet IDs:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-tasks1-2`
- `operator-control-plane-authority-foundation-lanev`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `operator2-control-plane-authority-foundation-activation-repreflight`

Historical Wave-2 packet coverage retained for validator completeness:

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

Closed preflight evidence packets:

- `director2-control-plane-authority-foundation-identity-preflight`
- `operator2-control-plane-authority-foundation-cutover-preflight`

## Director — Revised Task 2

Director owns `director-control-plane-authority-foundation-tasks1-2`.

Task 1 is frozen at `e43acc245e2492883ca04b0d835268708ad0995d`.
Do not amend, rebase, repeat, or cherry-pick this coordinator reroute into the
routed worktree. Read the revised Task-2 plan from Pipeline main, then resume
the existing pre-edit Task-2 implementer and land exactly one direct child
commit.

The Task-2 write set adds:

- `.claude/skills/four-seat-protocol/scripts/seat_status.py`;
- `scripts/draft_handoff.py`;
- `scripts/protocol_capacity.py`;
- `tests/unit/test_draft_handoff.py`;
- `tests/unit/test_protocol_capacity.py`;
- the four explicit pair files under `coordination/mailbox/seen/`.

Retain both coordinator cursor deletions and every original Task-2 path. The
new regressions prove `.agents`/`.claude` seat-status parity,
coordinator all-scope draft-handoff behavior, pair addressed/watermarked
behavior, terminal footer exclusion for ISO/`UNINITIALIZED`/
`all-scope-unpinned`, honest four-pair cursor migration, and the plan's
named one-fact flips.

After implementation, obtain fresh Task-2 spec and quality review. Send one
verify-request naming the exact range from
`78b48ed493899dd126de2d1764cbdbf022111dfd` through the new Task-2 commit,
the accepted Task-1 review artifacts, fresh Task-2 artifacts, selectors,
non-vacuity evidence, changed files, and exclusions.

## Operator — Lane V

Operator owns `operator-control-plane-authority-foundation-lanev` and remains
blocked until the fresh Director verify-request names the exact range. Operator
then independently inspects both commits, confirms Task 1 is unchanged and
Task 2 is its direct child, reruns the revised focused selectors and mutation
flips, verifies every changed file, and returns exactly one GO, NITS, or FAIL
report. Operator does not repair the diff.

## Director2 — Task 3 Repreflight

Director2 owns
`director2-control-plane-authority-foundation-identity-repreflight`.

Perform one focused read-only sufficiency pass over revised Tasks 3A-3D. The
new question is whether the revised task boundaries completely implement the
already-approved global before-mutation/verdict guarantee. Confirm role-family
matching, the frozen typed interface, deterministic errors, set-based
narrowing, non-rebindable session binding, primary-worktree interpreter,
PreToolUse and hook-self zero-mutation coverage, every interactive mutator and
verdict entry point, exact mechanical/service-principal mapping, canonical
doctor-gate inclusion, disjoint reviewable commits, and non-vacuity selectors.
Return one CLEAR or CONTRADICTION report to coordinator; do not implement.

## Operator2 — Tasks 4-6C Repreflight

Operator2 owns
`operator2-control-plane-authority-foundation-activation-repreflight`.

Perform one focused read-only safety pass over revised Tasks 4-6C. Confirm the
verified-exact resume matrix, committed secret-free activation manifest,
token-bound exact HEAD/manifest digest, complete managed-ref match with zero
resume rewrites, exact pre-run rollback before `live` only, identical
signed-cursor rosters, exact 11-principal key state machine, explicit off-repo
keystore containment, and the three separate later gates:

1. Task 6A trust-root generation/public-key commit;
2. Task 6B measured activation-manifest commit;
3. Task 6C separately authorized ref/authority flip.

Return one CLEAR or BLOCKED report to coordinator; do not generate keys,
create refs, execute cutover, or implement.

## Route-Mutation Side-Effect Executor Token

- side_effect_id: `control-plane-authority-plan-reroute-2026-07-10`
- executor: `coordinator`
- target: local Pipeline-main route mutation limited to this route file, the revised design/plan, five existing control-plane capacity packets, and two new repreflight capacity packets
- allowed_command_class: coordinator-owned route mutation through `apply_patch` plus `env -u GIT_INDEX_FILE git add` and one strict-pathspec local `git commit`
- preflight: user explicitly continued as coordinator and selected verified-exact resume; HEAD is `99a8b5b813e526e8ff04a3836af8073e5c9c9081`; Pipeline main and the routed worktree are clean; routed worktree HEAD is `e43acc245e2492883ca04b0d835268708ad0995d`; the three cited blocker reports are newest; this route path is absent
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if newer coordinator mail supersedes this revision, Pipeline HEAD changes, unrelated worktree changes appear, the routed worktree leaves `e43acc245e2492883ca04b0d835268708ad0995d`, another route already satisfies all three blockers, or any edited path falls outside the named target
- postcheck: capacity board valid; this route valid; protocol doctor passes against this route; smoke OK; git diff/cached scope contains only the named design, plan, capacity packets, and route; committed HEAD contains this exact route
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: production-code edit, routed-worktree edit, implementation, Operator GO, key/secret generation, signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-checkout refresh, paid-service spend, pod action, production generation, remote signer/runner deployment, merge, rebase, or protected-main update

Subagent utilization decision: three bounded read-only helpers synthesized the
independent Task-2, Task-3, and Tasks-4/5 plan-readiness questions. Their output
was advisory; the coordinator retained every plan, packet, route, and
side-effect decision.

Join condition: coordinator may close this cycle only after Director's revised
Task-2 commit and fresh verify-request exist, Operator returns GO for the exact
`78b48ed493899dd126de2d1764cbdbf022111dfd`-through-Task-2 range,
Director2 returns CLEAR for Tasks 3A-3D, Operator2 returns CLEAR for Tasks
4-6C, the routed worktree remains provenance-clean, capacity board and this
route validate, protocol doctor passes, smoke is OK, and closeout cites every
artifact. NITS, FAIL, CONTRADICTION, BLOCKED, changed scope, or newer route
causes bounded rerouting instead of closeout.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2`
  → PASS; prior active route was `2026-07-10T00-59-43Z`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2`
  → HEAD `99a8b5b`; Wave 2 MET; known false-clean mailbox surface remains `0 / ref-bus`.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/mailbox_monitor.py --once`
  → latest broadcast receipt `unknown=6`; unknown means unproved, not delivered.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10 rev-parse HEAD`
  → `e43acc245e2492883ca04b0d835268708ad0995d`.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
  → project smoke, ceremony, placeholder, GO-schema, and architecture freshness checks OK on the staged revision.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2`
  → `valid: true`; coordinator/director/director2/operator2 active, Operator blocked, no blocking issue.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
  → `route valid: true`; no blocking issue.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2 --route coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
  → `PROTOCOL DOCTOR: PASS`; 114 model-derived tests passed, capacity/route checks passed, and smoke returned OK.

## Exact Next Trigger

`continue as director` resumes revised Task 2 now. `continue as director2`
and `continue as operator2` run the two focused repreflights now. `operator`
waits for the fresh Director verify-request.

Cursor at send: 0
