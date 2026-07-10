# Coordinator → All: Corrective Task 2 And Runtime-Authority Bounded Reroute

**When:** 2026-07-10T08:58:02Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Failed Task-2 candidate retained as provenance: `205f077a23291496ea4b84c8de1f8acdfa2bd040`

## Durable Dispositions

- Operator returned binding `FAIL` for `78b48ed..205f077` in
  `coordination/mailbox/sent/2026-07-10T07-23-26Z-operator-to-all-verification-report.md`.
- Director confirmed every finding and the expanded minimum scope in
  `coordination/mailbox/sent/2026-07-10T08-30-14Z-director-to-coordinator-coordination.md`.
- Director2 returned route-changing `CONTRADICTION` for Tasks 3A-3D in
  `coordination/mailbox/sent/2026-07-10T04-29-26Z-director2-to-coordinator-coordination.md`.
- Operator2 returned `CLEAR` for Tasks 4-6C in
  `coordination/mailbox/sent/2026-07-10T04-24-26Z-operator2-to-coordinator-coordination.md`.

The user-principal's live coordinator `proceed` authorizes this reversible
local route mutation. It does not authorize production edits or another shared
side effect.

The bounded Task-2 choice is exact canonical signed refs, not configurable
refs. `refs/threeway/events` and `refs/threeway/cursors/` are fixed at manifest
load; `consume_bus.py` must load that manifest. Legacy numeric mailbox
envelopes remain readable only when the unique `typed-v1` marker-introduction
commit is not an ancestor of their unique event-introduction commit and current
bytes equal the introducing blob. Zero/multiple introductions and post-marker,
uncommitted, backdated, renamed, or modified numeric envelopes fail closed.
ADR-013 is append-only and narrows
the live transition to Task 6C.

The failed candidate remains immutable. Director adds exactly one corrective
child of `205f077`; no amend, reset, rebase, squash, branch rewrite, or checkout
refresh is authorized. Operator later verifies the cumulative three-commit
range from `78b48ed` through the corrective child.

## Capacity Split Default

Single-pair fast path remains the default for shared-file implementation.
Director owns the one tightly coupled Task-2 correction and Operator owns its
Lane V. Because implementation is not safely divisible, Pair B performs
bounded planning or preflight: Director2 owns one read-only Task-3
re-repreflight, while Operator2 holds its already-durable CLEAR without a third
Tasks-4/6C pass. Coordinator owns convergence and this one consolidated route.

## Capacity Packet Coverage

Current packet IDs:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-replacement`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
- `operator2-control-plane-authority-foundation-activation-repreflight`

Closed attempt and preflight packet IDs:

- `director-control-plane-authority-foundation-tasks1-2`
- `operator-control-plane-authority-foundation-lanev`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `operator2-control-plane-authority-foundation-cutover-preflight`

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

## Director — Additive Task 2 Correction

Director owns `director-control-plane-authority-foundation-task2-replacement`.
The original packet is done with its verify-request, failed candidate, Operator
FAIL, and Director blocker. Start from the clean routed worktree at `205f077`
and create one additive child only.

Retain every original Task-2 path and add the exact corrective scope:

- `DECISIONS.md`;
- `coordination/authority.toml`;
- `scripts/protocol_authority.py`;
- `scripts/protocol_effectiveness_report.py`;
- `.codex/hooks/update-state.sh`;
- `.claude/hooks/update-state.sh`;
- `tests/unit/test_protocol_authority.py`;
- `tests/unit/test_protocol_effectiveness_report.py`;
- `ARCHITECTURE.md` only if changed implementation makes a current claim or
  anchor stale.

One fresh implementer closes all nine findings using the plan's exact nine-row
pytest selector and RED/GREEN/non-vacuity contract. The implementation uses one canonical event
parser, synchronized atomic cursor publication, canonical unread across hooks
and observational tools, exact canonical signed refs, full-file and
missing-mailbox visibility, and both coordinator observational aliases.
Canonical-`coordinator` route discovery in `ledger_start_guard.py` and
`protocol_capacity.py` is documented/exempt and is not widened.

After fresh Task-2 specification and quality review, Director sends one
verify-request for `78b48ed..<corrective-child>` with all provenance, selectors,
paths, and exclusions.

## Operator — Replacement Lane V

The original `operator-control-plane-authority-foundation-lanev` packet is done
with binding FAIL. Operator now owns
`operator-control-plane-authority-foundation-replacement-lanev` and remains
blocked until the fresh verify-request. Operator independently reads all three
commits, every cumulative changed file, reproduces the nine prior failures,
reruns all corrective selectors and one-fact flips, and returns exactly one GO,
NITS, or FAIL. Operator does not repair the diff.

## Director2 — Task 3 Re-Repreflight

The prior identity repreflight packet is done with CONTRADICTION. Director2 now
owns `director2-control-plane-authority-foundation-identity-rerepreflight`.
The new read-only question is whether revised Tasks 3A-3D completely close the
four plan-sufficiency findings:

1. one cumulative runtime-and-token authorizer with frozen local/remote
   signed-fact and cursor command bundles;
2. identity, token, binding, runtime-guard, and service-principal suite
   registration in the canonical doctor selector;
3. exact narrow-only defaults and grammar for every supported spawned role;
4. exact mechanical-principal signer/token/credential maps plus a truly
   non-mutating merge-gate evaluator.

Return one CLEAR or CONTRADICTION report to coordinator. Do not implement.

## Operator2 — CLEAR Hold

`operator2-control-plane-authority-foundation-activation-repreflight` is
blocked as a hold packet with its `2026-07-10T04-24-26Z` CLEAR attached. Tasks
4-6C and their activation-safety contract are semantically unchanged, so
R-VERIFY-TIER forbids another same-question pass. Reopen only if a later diff
changes those task bodies or that contract.

## R-VERIFY-TIER Disposition

Operator and Director already confirmed the nine Task-2 defects. The three
coordinator helpers answered genuinely different predeclared questions:
minimal corrective scope, Task-3 plan repair, and packet/route mechanics. No
third defect-convergence pass was launched. The prior Director report labels
the old packet's test edit test-infeasible because required test paths were
outside its authority; this route immediately grants those test paths to the
replacement Director rather than deferring the defects.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-corrective-reroute-2026-07-10`
- executor: `coordinator`
- target: local route mutation limited to `coordination/mailbox/sent/2026-07-10T08-58-02Z-coordinator-to-all-coordination.md`, `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`, `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`, and the eight exact packet paths named in the coordinator join `scope_files`
- allowed_command_class: route mutation through `apply_patch`, ordinary strict-pathspec `env -u GIT_INDEX_FILE git add` for the ten visible paths, `env -u GIT_INDEX_FILE git add -f` for the one ignored route, cached-name verification of exactly eleven paths, and one local coordinator commit; no other mutation class
- preflight: user-principal said `proceed` in the live coordinator session; Pipeline HEAD is exactly `c6f0603a220f62e127578db4c5d9c04b74f307e5`; main and routed worktree are clean; routed HEAD is `205f077a23291496ea4b84c8de1f8acdfa2bd040`; accepted Task 1 is unchanged; this route is absent; and the Operator FAIL, Director blocker, Director2 CONTRADICTION, and Operator2 CLEAR are the newest binding reports
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if Pipeline HEAD or routed HEAD/worktree changes, newer coordinator mail or another route supersedes this appointment, a newer seat report changes a disposition, the edit exceeds the named target, Tasks 4-6C change semantically, or another committed route already satisfies this correction
- postcheck: the coordinator commit is the direct child of `c6f0603a220f62e127578db4c5d9c04b74f307e5`; cached and committed scope contains exactly the named route/design/plan/eight packet paths; capacity board and this route validate; protocol doctor and smoke pass; doc claims resolve; and the routed worktree remains clean at `205f077a23291496ea4b84c8de1f8acdfa2bd040`
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: production or routed-worktree edit, amend/reset/rebase/squash, key or signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-repo checkout refresh, paid-service spend, pod action, production generation, merge, protected-main update, or external deployment

Subagent utilization decision: three bounded read-only helpers independently
audited Task-2 corrective scope, Task-3 plan sufficiency, and route/capacity
mechanics. They made no edits, mailbox events, cursor changes, verdicts, or
side-effect decisions. Coordinator owns this synthesis.

Join condition: coordinator may close only after the additive Task-2 child and
fresh verify-request exist; Operator returns GO for the exact cumulative
three-commit range; Director2 returns CLEAR for revised Tasks 3A-3D; Operator2
CLEAR remains applicable; routed provenance is clean; and capacity board,
route validation, protocol doctor, smoke, and doc claims pass. NITS, FAIL,
CONTRADICTION, changed Tasks 4-6C, changed scope, or newer route causes bounded
rerouting instead of closeout.

## Evidence

- `seat_status.py coordinator --wave 2` → HEAD `c6f0603`; coordinator
  all-scope unread surface `0 / ref-bus`; Wave-2 string gate MET.
- `git status --short --branch` → clean `main...origin/main [ahead 58]` before
  coordinator edits.
- routed `git status --short --branch` → clean
  `codex/control-plane-authority-foundation-2026-07-10` at `205f077`.
- `protocol_capacity_board.py --wave 2` → valid true on this draft; replacement
  Director and Director2 active, replacement Operator and Operator2 CLEAR hold
  blocked, no blocking issue.
- validation of
  `coordination/mailbox/sent/2026-07-10T08-58-02Z-coordinator-to-all-coordination.md`
  → route valid true; all Wave-2 packet IDs present; no blocking issue.
- `protocol_doctor.py --wave 2 --route coordination/mailbox/sent/2026-07-10T08-58-02Z-coordinator-to-all-coordination.md`
  → 114 passed, smoke OK, `PROTOCOL DOCTOR: PASS`.
- `check_doc_claims.py <design> <plan>` → all anchors checked; no drift.
- `scripts/ci_smoke.py` → project smoke, anti-ceremony, placeholders,
  GO-schema, and architecture freshness all pass.
- `wave_gate_check.py 2` → process gate MET with zero rows; this is not
  correctness evidence and does not override Operator FAIL.

## Exact Next Trigger

`continue as director` executes the additive Task-2 correction now.
`continue as director2` runs the focused Task-3 re-repreflight now. `operator`
waits for the new Director verify-request. `operator2` holds its CLEAR and
reopens only if Tasks 4-6C change. Coordinator waits for those durable outputs;
no push or activation action is authorized.

Cursor at send: all-scope-unpinned
