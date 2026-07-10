# Coordinator → All: Task 3 Interface-Closure Reroute

**When:** 2026-07-10T10:26:39Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T08-58-02Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Failed Task-2 candidate retained as provenance: `205f077a23291496ea4b84c8de1f8acdfa2bd040`

## Durable Dispositions

- Operator returned binding `FAIL` for `78b48ed..205f077` in
  `coordination/mailbox/sent/2026-07-10T07-23-26Z-operator-to-all-verification-report.md`.
- Director confirmed every finding and the expanded minimum scope in
  `coordination/mailbox/sent/2026-07-10T08-30-14Z-director-to-coordinator-coordination.md`.
- Director2's first repreflight returned route-changing `CONTRADICTION` in
  `coordination/mailbox/sent/2026-07-10T04-29-26Z-director2-to-coordinator-coordination.md`.
- Director2's focused re-repreflight returned a second binding `CONTRADICTION`
  with five exact interface gaps in
  `coordination/mailbox/sent/2026-07-10T09-45-35Z-director2-to-coordinator-coordination.md`.
- Operator2 returned `CLEAR` for Tasks 4-6C in
  `coordination/mailbox/sent/2026-07-10T04-24-26Z-operator2-to-coordinator-coordination.md`.

The user-principal's `continue as coordinator` names the coordinator as the
executor for this bounded, reversible local route mutation. It does not
authorize production edits, remote publication, or another shared side effect.

The bounded Task-2 choice is exact canonical signed refs, not configurable
refs. `refs/threeway/events` and `refs/threeway/cursors/` are fixed at manifest
load; `consume_bus.py` must load that manifest. Legacy numeric mailbox
envelopes remain readable only when the unique `typed-v1` marker-introduction
commit is not an ancestor of their unique event-introduction commit and current
bytes equal the introducing blob. Zero/multiple introductions and post-marker,
uncommitted, backdated, renamed, or modified numeric envelopes fail closed.
ADR-013 is append-only and narrows
the live transition to Task 6C.

The failed candidate remains immutable. Director has landed provisional direct
child `92d1fbcd1bb76ccb377d6bca1631374569696626` of `205f077`; no amend, reset,
rebase, squash, or branch rewrite is authorized. Operator
later verifies the cumulative three-commit range from `78b48ed` through that
corrective child after Director sends the still-missing fresh verify-request.

## Capacity Split Default

Single-pair fast path remains the default for shared-file implementation.
Director owns the one tightly coupled Task-2 correction and Operator owns its
Lane V. Because implementation is not safely divisible, Pair B performs
bounded planning or preflight: Director2 owns one read-only Task-3 interface-
closure preflight, while Operator2 holds its already-durable CLEAR without
repeating Tasks 4-6C. Coordinator owns convergence and this one consolidated route.

## Capacity Packet Coverage

Current packet IDs:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-replacement`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `director2-control-plane-authority-foundation-identity-interface-closure-preflight`
- `operator2-control-plane-authority-foundation-activation-repreflight`

Closed attempt and preflight packet IDs:

- `director-control-plane-authority-foundation-tasks1-2`
- `operator-control-plane-authority-foundation-lanev`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
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
FAIL, and Director blocker. Director's clean routed worktree now has provisional
additive child `92d1fbc` directly above `205f077`, but no newer verify-request
mailbox body exists. Director remains active to finish the routed specification/
quality reviews and send the exact cumulative verify-request; the coordinator
does not edit, stage, or commit that worktree.

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

## Director2 — Task 3 Interface-Closure Preflight

The completed `identity-rerepreflight` packet is closed by the
`2026-07-10T09-45-35Z` CONTRADICTION. Director2 now owns
`director2-control-plane-authority-foundation-identity-interface-closure-preflight`.
The predeclared read-only question is only whether revised Tasks 3A-3D close
these five findings:

1. `LOCK_CLAIM_REMOTE` and `LOCK_RELEASE_REMOTE` have distinct exact bundles
   containing both `LOCK_MUTATE` and `REMOTE_PUBLISH`, with every named
   mutation probe untouched on denial;
2. signed cursor writes remain local-only, while operator remote publication is
   limited to its own statically allowed fact, exact candidate, and committed
   opposite-operator GO binding;
3. merge evaluation and both mutation authorizations share one immutable
   repository/candidate/target/event-store/tip/materialization binding, apply
   revalidates tokens, and quarantine comparison plus prepared expected-old ref
   state precede import of only the exact verified object closure, with no free
   candidate/target arguments;
4. remote event acquisition produces immutable exact-OID bytes in a scratch
   repository/ref namespace and pure evaluation never syncs the live store or
   writes the input object database;
5. `CODEX_PUBLICATION_POLICY` has exact lowercase Boolean grammar, complete
   actor defaults, deterministic rejection order, and effective-false denial.

Return one CLEAR or CONTRADICTION report to coordinator. Do not implement,
issue Operator GO, consume mail, route, or take a user-gated side effect.

## Operator2 — CLEAR Hold

`operator2-control-plane-authority-foundation-activation-repreflight` is
blocked as a hold packet with its `2026-07-10T04-24-26Z` CLEAR attached. Tasks
4-6C and their activation-safety contract are semantically unchanged, so
R-VERIFY-TIER forbids another same-question pass. Reopen only if a later diff
changes those task bodies or that contract.

## R-VERIFY-TIER Disposition

Director2's second CONTRADICTION asks a new interface-sufficiency question and
changes which Task-3 sites/tests must be specified, so one focused follow-up is
lawful. Three coordinator helpers independently checked remote lock/fact
authority, merge-gate candidate/snapshot isolation, and publication grammar plus
route mechanics. They did not re-verify the Task-2 defects, repeat Operator2's
Tasks-4/6C question, or inherit seat authority.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-interface-closure-reroute-2026-07-10`
- executor: `coordinator`
- target: local route mutation limited to `coordination/mailbox/sent/2026-07-10T10-26-39Z-coordinator-to-all-coordination.md`, `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`, `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-rerepreflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-interface-closure-preflight.json`, and `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator2-repreflight.json`
- allowed_command_class: route mutation through `apply_patch`, ordinary strict-pathspec `env -u GIT_INDEX_FILE git add` for the six visible paths, `env -u GIT_INDEX_FILE git add -f` for the ignored route, cached-name verification of exactly seven paths, and one local coordinator commit; no other mutation class
- preflight: user-principal said `continue as coordinator`; Pipeline HEAD is `5b2a50ce5823d08d69dc1101082a504adac9b27d`; main was clean before coordinator edits; accepted Task 1 and failed Task-2 provenance are unchanged; the routed worktree is clean at provisional direct child `92d1fbcd1bb76ccb377d6bca1631374569696626`, with no newer Director verify-request; the 09:45 Director2 CONTRADICTION and Operator2 CLEAR are the newest binding reports; this route is absent from HEAD
- stop_if_newer_mail_or_live_target_satisfied: refresh before commit if Pipeline HEAD changes, newer coordinator mail or another route appears, Director sends a Task-2 verify-request, a newer seat report changes a disposition, the edit exceeds the seven named paths, Tasks 4-6C change semantically, or another committed route already satisfies these five gaps; Director-owned routed-worktree progress alone is not a stop condition
- postcheck: the coordinator commit is a direct child of the refreshed expected Pipeline HEAD; cached and committed scope contains exactly the seven named paths; capacity board and this route validate; protocol doctor, smoke, and doc claims pass; Tasks 4-6C are unchanged; and coordinator made no routed-worktree edit
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: Task-2 production/routed-worktree edit, Tasks 4-6C edit, amend/reset/rebase/squash, key or signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-repo checkout refresh, paid-service spend, pod action, production generation, merge, protected-main update, or external deployment

Subagent utilization decision: three bounded read-only helpers independently
audited remote lock/fact authority, merge-gate binding/snapshot isolation, and
publication grammar plus route/capacity mechanics. They made no edits, mailbox events, cursor changes, verdicts, or
side-effect decisions. Coordinator owns this synthesis.

Join condition: coordinator may close only after the additive Task-2 child and
fresh verify-request exist; Operator returns GO for the exact cumulative
three-commit range; Director2 returns CLEAR from the Task-3 interface-closure preflight; Operator2
CLEAR remains applicable; routed provenance is clean; and capacity board,
route validation, protocol doctor, smoke, and doc claims pass. NITS, FAIL,
CONTRADICTION, changed Tasks 4-6C, changed scope, or newer route causes bounded
rerouting instead of closeout.

## Evidence

- `seat_status.py coordinator --wave 2` → HEAD `5b2a50c`; coordinator
  all-scope unread surface `0 / ref-bus`; Wave-2 process gate MET.
- `git status --short --branch` → clean `main...origin/main [ahead 60]`
  before coordinator edits.
- routed status → clean HEAD `92d1fbc`, whose parent is exactly failed candidate
  `205f077`; no post-failure verify-request exists, and the coordinator did not
  edit that worktree.
- `protocol_capacity_board.py --wave 2` and validation of this `10-26-39`
  route → valid true with Director and Director2 active, both operators
  blocked on their exact dependencies, and no blocking issue.
- `protocol_doctor.py --wave 2 --route <this-route>` → 114 passed,
  smoke OK, `PROTOCOL DOCTOR: PASS`.
- `ci_smoke.py` → project smoke, anti-ceremony, placeholders, GO schema, and
  architecture freshness pass.
- `check_doc_claims.py <design> <plan>` → all anchors checked, no drift;
  `git diff --check` → no output.
- SHA-256 from `### Task 4` through EOF is byte-identical at HEAD and in the
  routed plan: `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- Director2's committed `09-45-35` body and direct source inspection confirm
  all five interface gaps; three bounded read-only helper audits supplied
  independent contract and route-mechanics checks. Focused actual-diff
  rechecks for remote lock/publication typing, merge snapshot/binding plus
  quarantine materialization, and route mechanics each returned `pass`.
- The Wave-2 string gate is process evidence only and does not override the
  binding CONTRADICTION.

## Exact Next Trigger

`continue as director2` runs only the Task-3 interface-closure preflight.
`continue as director` completes the routed reviews and sends the fresh
`78b48ed..92d1fbc` Task-2 verify-request.
`operator` waits for Director's fresh verify-request. `operator2` holds its
existing CLEAR and reopens only if Tasks 4-6C change. Coordinator waits for
those durable outputs.
No remote publication or activation action is authorized.

Cursor at send: all-scope-unpinned
