# Coordinator → All: Task 3E Proof-Capability Reroute

**When:** 2026-07-10T13:51:18Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T12-11-02Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Failed Task-2 candidate retained as provenance: `205f077a23291496ea4b84c8de1f8acdfa2bd040`
Reviewed-but-spec-failed Task-2 child retained as provenance: `92d1fbcd1bb76ccb377d6bca1631374569696626`
Task2R candidate: `ef76fd11ea61e27778d0cedf65c1a608cf826354`

## Durable Disposition

- Director2's `2026-07-10T13-22-51Z` report is binding
  `CONTRADICTION`: `init=False` did not make the proposed frozen/slot
  `EventSnapshot` acquisition-only, and proof-object traversal inherited Git
  replacement and repository-redirection state.
- Director2 confirmed the local prepared two-ref transaction, remote atomic
  two-ref publication, exact leases, unique endpoint binding, race denials, and
  no-retry boundary sufficient. Task 3E does not repeat those questions.
- The prior remote-lock, signed-fact, cursor, and publication-grammar Task-3
  findings remain closed. Task 4 through EOF remains byte-identical at SHA-256
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- Director has landed the sole additive Task2R child `ef76fd1` directly on
  `92d1fbc`; the routed worktree is clean. The Director packet remains active
  and unchanged because no fresh specification/quality review evidence or
  cumulative verify-request has landed in Pipeline. Operator remains blocked
  until that request exists.
- Operator2's `2026-07-10T04-24-26Z` Tasks-4/6C CLEAR remains applicable and
  is not repeated.

The user-principal's `continue as coordinator` selects the coordinator for this
bounded local route mutation. It grants no production edit, cursor movement,
remote publication, lock action, or other user-gated side effect.

## Task 3E Design Correction

Public evaluation no longer accepts or returns an `EventSnapshot`, proof path/
ref, event bytes, tip/tree/digest, or caller-provided acquisition capability.
`evaluate_gate_read_only()` accepts the trusted `RefEventStore`; the real
`poll_once()` captures once; private candidate discovery, independent proof
revalidation, reduction, and every evaluation finish inside one lexical
acquisition lifetime. Private state retains only immutable ordered JSON bytes;
candidate discovery discards its temporary parsed events, and every reduction
reparses fresh, so mutable `Event.payload` values cannot cross phases. The proof
path/ref never crosses the public interface.

Every proof-object command uses the dedicated identity-checked
`--no-replace-objects --no-lazy-fetch --literal-pathspecs --git-dir` runner with
no inherited `GIT_*` values and the plan's fixed safe settings. The protected
runner supplies an absolute Git executable before store/key/candidate access;
its no-follow path/device/inode is rechecked for every invocation, which executes
that exact binary instead of ambient `PATH`. It also binds Git's discovered
exec-path and ordered absolute, non-group/world-writable helper directories by
path/device/inode/owner/mode; child `PATH` and `--exec-path` contain only those
bound directories. Real remote acquisition therefore cannot launch an ambient
fake `ssh`, `git-upload-pack`, or `git-remote-*` helper. A same-tip
replacement ref, alternate, graft/shallow marker, missing or wrong-type object,
ambient repository/object/config/pathspec redirect, nonzero command status, or
same-path proof-directory inode rebound fails closed before reduction.

The thirteen exact selectors retain the six already-sufficient apply controls/
denials and add seven causal acquisition/provenance checks: no caller snapshot
input, independent proof-ref reread against a valid-digest subset, honest
store-owned acceptance, fresh reparse after temporary event mutation, a one-
fact same-tip replacement-ref denial, proof Git executable/helper/argv/
environment hardening, and same-path proof-repository inode-substitution denial.

## Capacity Split Default

The single-pair fast path remains correct for the tightly coupled Task2R
implementation and one final cumulative Operator Lane V. The production change
is not safely divisible, so Pair B continues bounded planning or preflight:
Director2 owns only the read-only Task 3E proof-capability closure check while
Operator2 holds its existing CLEAR. Coordinator owns convergence.

## Capacity Packet Coverage

Current packets:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-spec-review-fix`
- `director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `operator2-control-plane-authority-foundation-activation-repreflight`

Closed control-plane attempts retained as provenance:

- `director-control-plane-authority-foundation-tasks1-2`
- `director-control-plane-authority-foundation-task2-replacement`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
- `director2-control-plane-authority-foundation-identity-interface-closure-preflight`
- `director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight`
- `operator-control-plane-authority-foundation-lanev`
- `operator2-control-plane-authority-foundation-cutover-preflight`

Historical Wave-2 coverage retained for validator completeness:

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

## Director — Task2R Candidate Landed; Reviews Pending

Director continues
`director-control-plane-authority-foundation-task2-spec-review-fix` exactly as
routed at `12-11-02Z`: preserve topology
`78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> ef76fd1` and create no second
child. Complete fresh specification review of `92d1fbc..ef76fd1`; only after it
passes complete fresh quality review, then send one cumulative Operator
verify-request for
`78b48ed493899dd126de2d1764cbdbf022111dfd..ef76fd11ea61e27778d0cedf65c1a608cf826354`.

## Operator — One Final Cumulative Lane V

Operator remains blocked on the Director packet and fresh verify-request. It
then independently verifies the four-commit cumulative range and returns one
GO, NITS, or FAIL. Operator does not repair the Director diff.

## Director2 — Task 3E Proof-Capability Closure

Director2 owns
`director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`.
Read the `13-22-51Z` report and inspect only the corrected public acquisition
boundary, dedicated proof Git boundary, and seven named provenance selectors.
Return CLEAR only if acquisition is public-input-free, proof state remains
private and identity-bound for its lexical lifetime, mutable parsed events are
not reused, the protected-runner Git binary plus exec/helper search paths are
identity-bound, all proof/remote-acquisition reads disable replacement/redirect
state, and every denial has its honest one-fact control.

Inherit the already-confirmed local/remote two-ref transaction closure and prior
Task-3 closures without another pass. Confirm only that those plan sections and
Task 4 onward remain unchanged. Return one CLEAR or CONTRADICTION; do not
implement, issue Operator GO, consume mail, or take a user-gated side effect.

## Operator2 — CLEAR Hold

`operator2-control-plane-authority-foundation-activation-repreflight` remains
blocked/observer-only. Reuse its attached CLEAR while Task 4 through EOF and the
activation contract remain unchanged. Send no receipt or duplicate report.

## R-VERIFY-TIER Disposition

Task 3E asks only the new acquisition-capability and proof-process questions
raised by the binding Task-3D contradiction. It does not launch a third pass on
the confirmed CAS, remote-lock, signed-fact, cursor, publication-grammar, or
activation questions. Task2R and its per-commit reviews remain separate.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-task3e-reroute-2026-07-10`
- executor: `coordinator`
- target: local route mutation limited to `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3d-snapshot-cas-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3e-proof-capability-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator2-repreflight.json`, `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`, `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`, and `coordination/mailbox/sent/2026-07-10T13-51-18Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, strict-pathspec `env -u GIT_INDEX_FILE git add` for six visible paths, `env -u GIT_INDEX_FILE git add -f` for the ignored route, cached-name verification of exactly seven paths, and one local coordinator commit; no other mutation class
- preflight: user-principal said `continue as coordinator`; expected Pipeline HEAD is `9ec9c0267a270e1b62b752713ba997189f5ba687`; Pipeline main was clean before coordinator edits; `13-22-51Z` is the newest binding report; routed HEAD is the clean sole Task2R child `ef76fd11ea61e27778d0cedf65c1a608cf826354` whose parent is `92d1fbcd1bb76ccb377d6bca1631374569696626`; no fresh Task2R verify-request exists; Task 4 onward is unchanged; and this route is absent from HEAD
- stop_if_newer_mail_or_live_target_satisfied: refresh before commit if Pipeline HEAD changes, newer coordinator mail or route appears, a fresh Task2R verify-request or Task3E disposition lands, the edit exceeds the seven named paths, routed HEAD moves from `ef76fd11ea61e27778d0cedf65c1a608cf826354`, new Director WIP touches a coordinator-owned path, Task 4 onward changes, or another committed route already closes the report
- postcheck: the coordinator commit is a direct child of refreshed expected Pipeline HEAD; cached and committed scope contains exactly the seven named paths; capacity board and this route validate; protocol doctor, smoke, doc claims, diff checks, packet JSON, and Task-4 suffix hash pass; coordinator made no routed-worktree edit
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no Task2R or Task-3 production edit, amend/reset/rebase/squash, key or signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-checkout refresh, paid-service spend, pod action, production generation, merge, protected-main update, or external deployment

Join condition: coordinator closes only after Director completes Task2R with one
additive child, fresh specification and quality reviews, and one cumulative
verify-request; Operator returns GO for the exact cumulative range; Director2
returns CLEAR for Task 3E; Operator2's prior CLEAR remains applicable; routed
provenance is clean; capacity board, route validation, protocol doctor, smoke,
doc claims, and immutable-suffix checks pass; and no forbidden side effect
occurred. Any NITS, FAIL, CONTRADICTION, changed suffix, changed scope, or newer
route causes bounded reconciliation instead of closeout.

## Evidence

- The binding `13-22-51Z` mailbox body was read in full; no coordinator cursor
  was consumed.
- The proposed frozen/slot shape was constructed with `S()` and populated via
  `object.__setattr__`, proving `init=False` did not enforce acquisition.
- Git 2.50.1 reports the repository-local environment controls through
  `git rev-parse --local-env-vars`; Git's primary `git-replace` documentation
  states replacement refs affect object commands by default and identifies
  `--no-replace-objects` / `GIT_NO_REPLACE_OBJECTS` as the suppression boundary.
- Capacity reconciliation is valid and active with Director and Director2
  active, Operator and Operator2 blocked on their named dependencies, and no
  blocking issue.
- `protocol_doctor.py --wave 2 --route <this-route>` reports route valid,
  capacity valid, `114 passed`, smoke OK, and `PROTOCOL DOCTOR: PASS`; direct
  doc-claim checking reports all anchors checked with no drift.
- Packet JSON, placeholder self-review, selector count, and `git diff --check`
  pass. The plan names thirteen exact selectors and contains no mutable parsed
  event in `_AcquiredEventState`.
- Pipeline main started clean at `9ec9c02`; routed HEAD is clean at sole direct
  child `ef76fd1` with parent `92d1fbc` and nine paths inside the Director
  packet. No cumulative verify-request existed at refresh. Task 4 through EOF remains
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- Three bounded read-only reviews independently confirmed the contradiction,
  the private lexical-acquisition correction, the hardened proof-process
  boundary, and the exact seven-path route transition. They made no edits and
  inherited no seat or side-effect authority.

## Exact Next Trigger

`continue as director2` performs only the Task-3E proof-capability closure
preflight and returns one CLEAR or CONTRADICTION. `continue as director`
completes fresh specification and quality review of `92d1fbc..ef76fd1` and
sends the cumulative verify-request without creating another implementation
child. Operator waits for that request; Operator2 holds its existing CLEAR.
Coordinator waits for those durable outputs. No remote publication or
activation action is permitted.

Cursor at send: all-scope-unpinned
