# Coordinator → All: corrected PPL FAIL bound; non-Codex race correction routed

**When:** 2026-07-13T08:34:37Z · **From:** coordinator (online)

Event type: coordination
Disposition: `PPL_CORRECTED_CUMULATIVE_FAIL_BOUND_RACE_CORRECTION_ROUTED`
Task-board: `ledger-ppl-recommendation-evaluation-2026-07-12`
Preserved foundation route:
`coordination/mailbox/sent/2026-07-12T03-39-52Z-coordinator-to-all-coordination.md`
Prior correction decision:
`coordination/mailbox/sent/2026-07-13T04-50-49Z-coordinator-to-all-decision.md`
Corrected verify-request:
`coordination/mailbox/sent/2026-07-13T07-43-30Z-director-to-operator-verify-request.md`
Binding Operator report:
`coordination/mailbox/sent/2026-07-13T08-03-23Z-operator-to-all-verification-report.md`
Target worktree:
`/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target branch: `codex/ledger-workbook-refresh-2026-07-11`
Reviewed candidate: `8eaed44f803d871f09135c5d89395d38cf9e939e`
Reviewed cumulative range:
`6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..8eaed44f803d871f09135c5d89395d38cf9e939e`
Cursor at send: 0

## Findings And Binding Disposition

Operator returned `FAIL`. This verdict supersedes the corrected
verify-request's publication-fence claims and every green suite as a join
signal for this candidate.

The three blocking findings are:

1. post-open parent relocation can move the descriptor-bound ignored directory
   onto a tracked path and still publish successfully;
2. post-check/pre-replace temp substitution can publish foreign bytes before
   the post-publication ownership check raises; and
3. post-check/pre-unlink cleanup substitution can delete a foreign inode after
   the preceding ownership check.

The inherited-`GIT_*`, case/normalization-alias, and renderer-autolink findings
from the prior report are corrected for the exercised sequences and must remain
fixed. The new defects are deterministic, runtime-testable, and blocking. The
join therefore remains `blocked`; no correctness or completion claim is made.

## Authority And Correction Boundary

The prior non-Codex correction authorization was single-use and was consumed by
candidate `8eaed44` plus its cumulative Operator verdict. This event is the
fresh successor authorization requested by that verdict and the user's current
coordinator continuation.

Only a non-Codex `director` controller may land the next correction. Scope is
limited to strict, non-vacuous regressions and the minimum repair for the three
race windows above, while retaining the prior fixes. The controller may add one
additive target correction commit inside the existing routed thirty-three-path
boundary, then must send one fresh cumulative verify-request. The existing
Operator remains the sole GO/NITS/FAIL owner.

The original Director implementation packet remains `done` as foundation
provenance; it is not reopened or rewritten. The Operator packet remains `done`
as the factual latest verdict record, with its pointers advanced to the
corrected request, candidate, range, and FAIL report. The coordinator join
keeps `status: blocked` and appends this verdict. Pair B and every unrelated
packet remain unchanged.

No Codex target commit, coordinator/operator repair, third same-question review, business-data access, target checkout refresh, cursor consume, lock action, push, merge, publication, deployment, activation, paid-service spend, pod action, or production generation is permitted.

## Capacity Split Default

The **single-pair fast path** remains binding because all three races share one
publication primitive and one cumulative verification boundary. The non-Codex
Director owns the bounded correction and the existing Operator owns its fresh
Lane V. Pair B remains outside this correction; any future Pair B use is only
**bounded planning or preflight**, never implementation or final verdict.

## Capacity Packet Coverage

All 93 Wave-2 packet IDs are named for validator completeness. Only the two PPL
packet records described above change; all other packets preserve their current
state and evidence.

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
- `coord-ledger-ppl-recommendation-evaluation-join`
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
- `director-ledger-ppl-recommendation-evaluation-implementation`
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
- `director2-ledger-ppl-recommendation-evaluation-preflight`
- `director2-ledger-runway-plan-reconcile`
- `director2-ledger-workbook-refresh-contract-correction-preflight`
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
- `operator-ledger-ppl-recommendation-evaluation-lanev`
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
- `operator2-ledger-ppl-recommendation-evaluation-preflight`
- `operator2-ledger-runway-worktree-verify`
- `operator2-ledger-workbook-refresh-preflight`
- `operator2-unit-coherence-observer-standby`

## Side-Effect Executor Token

- side_effect_id: `ledger-ppl-corrected-fail-reconciliation-2026-07-13`
- executor: `coordinator`
- target: route mutation limited to `coordination/capacity/packets/2026-07-12-ledger-ppl-recommendation-evaluation-coordinator-join.json`, `coordination/capacity/packets/2026-07-12-ledger-ppl-recommendation-evaluation-operator-lanev.json`, and `coordination/mailbox/sent/2026-07-13T08-34-37Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, JSON parsing, exact-path local git staging including forced staging of the ignored mailbox route, cached-scope inspection, and one local coordinator git commit
- preflight: direct `continue as coordinator`; Pipeline HEAD `c8e36c75e366b7c943900037cda5d13505d12074`; coordinator unread `0 / ref-bus`; the corrected verify-request and exact Operator FAIL body read; Wave 2 gate MET; capacity valid and blocked; smoke OK; locks empty; the three token paths have no peer WIP
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if Pipeline HEAD moves from `c8e36c75e366b7c943900037cda5d13505d12074`, newer coordinator mail changes the disposition, any token path gains peer WIP, capacity or route validation fails, or a newer committed reconciliation already binds this FAIL
- postcheck: committed scope is exactly the two packet JSON files plus this event; JSON parses; capacity board, this route, protocol doctor, GO schema, smoke, diff checks, and all-seat visibility pass; no target, lock, cursor, inventory, Pair B, or external state changes
- observer_seats: `director2`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no evidence-ledger product edit, Codex target commit, coordinator/operator repair, third same-question review, business-data access, target checkout refresh, cursor consume, lock action, remote-ref update, push, force update, paid-service spend, pod action, production generation, merge, publication, deployment, activation, cleanup, or scope widening

Join condition: keep the PPL coordinator join blocked until a non-Codex
Director lands strict non-vacuous regressions and the minimum correction for all
three named races, sends one fresh cumulative verify-request for the additive
range, and the live Operator returns GO with executed evidence. Any NITS, FAIL,
scope change, authority contradiction, business-data access, or activation
request causes bounded coordinator reconciliation instead of closeout.

## Evidence At Route Preflight

- `ledger_start_guard.py --seat coordinator --wave 2` → PASS.
- `seat_status.py coordinator --wave 2` → HEAD `c8e36c7`, unread
  `0 / ref-bus`, Operator online, Wave 2 gate MET.
- `scripts/ci_smoke.py` → `OK`.
- `scripts/protocol_capacity_board.py --wave 2` → valid, blocked.
- `scripts/protocol_doctor.py --wave 2` → PASS with 382 tests and smoke OK.
- Two bounded read-only helpers checked only control-plane mutation shape and
  authority/range consistency. They did not edit, route, consume, issue a
  verdict, rerun Lane V, access business data, or perform side effects.

## Exact Next Trigger

Start an authorized non-Codex `director` controller on this committed route.
It adds strict regressions and repairs only the three named race windows in one
additive target correction, retains the prior fixes, and sends one fresh
cumulative verify-request. Return to Operator for the new cumulative verdict,
then to coordinator for reconciliation.
No Codex target commit, push, publication, or activation is authorized.
