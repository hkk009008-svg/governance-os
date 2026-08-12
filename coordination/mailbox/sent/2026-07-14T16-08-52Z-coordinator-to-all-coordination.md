# Coordinator -> All: route cumulative Opus receipt corrective cycle

**When:** 2026-07-14T16:08:52Z · **From:** coordinator (online)

Event type: coordination
Disposition: `PIPELINE_LEVEL5_OPUS_RECEIPT_CORRECTIVE_ROUTE_ACTIVE`
Task-board: `pipeline-level5-opus-receipt-corrective-2026-07-15`
Protocol wave: `2`
Route base before commit: `563cc85c6716b746c5baff788cae8408c38b31d0`
Coordinator mailbox at preflight: `0 unread / all-scope; no consume`
Binding report: `coordination/mailbox/sent/2026-07-14T15-53-30Z-operator2-to-all-verification-report.md`

## Findings First

Operator2 returned binding `FAIL` for the immutable range
`555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`.
The deterministic suite, smoke, schema gate, and protocol doctor passed, but five
adversarial probes exposed blocking guarantee failures:

1. `coordination/bin/send-event` can delete the witnessed publication candidate
   after real process death and can delete a substituted foreign pathname.
2. `scripts/check_go_schema.py` lets `PATH` select or suppress the Git executable
   used for historical-baseline authority.
3. The report-corpus scan follows a symlinked canonical sent directory and can
   accept outside bytes under a canonical-looking path.
4. `scripts/opus_review_bridge.py` can start a verifier child before publishing
   it to the active registry, so shutdown can miss and leak the process.
5. Reconciliation can initialize receipt state before rejecting a malformed
   receipt identifier.

The manually approved provider attempt reached provider entry but normalized to
`unavailable` at `provider_exit` with `process_failed`, no model identity, and no
findings. Manual approval was not the fix. Receipt
`opr1:b79ded16d73c5c001a811b1377ba8df85e4577c2cb8d0e87535e105548e35a49`
and all prior attempt identities are terminal evidence only. No retry, reset,
replay, fallback, or substitute review is authorized for that task/head/base.

## Coordinator Decision

Open one cumulative corrective implementation and verification loop:

- `director2-pipeline-level5-opus-receipt-corrective-implementation` is active.
  Director2 owns the five exact findings, their non-vacuous regressions, one
  descriptor at
  `coordination/verification/scopes/256b36e2-2fe4-43e8-b2e3-0a99a07e6229.json`,
  one cumulative shipping head, and one canonical verify-request.
- `operator2-pipeline-level5-opus-receipt-corrective-lanev` is blocked until
  that lawful trigger lands, then independently returns one GO/NITS/FAIL.
- `director-pipeline-level5-opus-receipt-corrective-standby` and
  `operator-pipeline-level5-opus-receipt-corrective-standby` are excepted.
- `coord-pipeline-level5-opus-receipt-corrective-join` remains blocked on the
  Operator2 verdict.

Director2 starts from exact Pipeline main commit
`563cc85c6716b746c5baff788cae8408c38b31d0` in a fresh isolated worktree and
branch. The prior `.worktrees/opus-lanev-receipt-hardening` worktree and every
receipt/runtime artifact remain immutable.

## Capacity Split Default

Use the **single-pair fast path**. A dual-pair routing split was rejected even
though the files are superficially separable: Chunk A would change the mailbox
publisher and corpus gate, while Chunk B would change the process and receipt
machinery used by Lane V itself. Each independent verdict would otherwise run
through tooling that still lacked the other chunk's correction.

The required **bounded planning or preflight** was completed by the coordinator
as a distinct self-hosting-boundary question, not as a third repeat of the same
defect review. Pair A stays observer-only. The five fixes converge as one
descriptor-bound head and one Operator2 verdict.

## Corrective Acceptance Boundary

- Treat the committed Operator2 report as the independent pre-implementation
  abuse-case enumeration. Add one deterministic regression per finding, capture
  pre-fix RED or strict-xfail evidence, and finish with passing tests rather than
  final xfails for fixed defects.
- Audit sibling cleanup/removal paths, historical-baseline Git invocations,
  report-corpus opens, verifier-child lifecycle paths, and untrusted receipt-ID
  entry points. The verify-request records mirror/defer/document/exempt
  disposition for every sibling.
- Do not regenerate the historical report baseline, weaken a gate, widen the
  descriptor silently, or change prior receipt evidence.
- At minimum run `bash -n coordination/bin/send-event`, the focused five-file
  regression suite, `scripts/check_go_schema.py`,
  `scripts/check_doc_claims.py --sha-refs`, `scripts/ci_smoke.py`,
  `scripts/protocol_doctor.py --wave 2`, and exact-range `git diff --check`.
- Any cross-model step for the new corrective head must derive from the new
  descriptor and standing policy only. This route grants no manual approval,
  credential entry, old-identity reuse, retry, alternate transport, or extra
  paid-call authority.

## Subagent Utilization

Direct/no subagent for this coordinator reconciliation: the binding report
already supplies independent findings, and route mutation is tightly coupled to
coordinator authority. Director2 may make its own bounded implementation-helper
decision under its seat rules; helpers inherit no mailbox, verdict, provider,
spend, or remote-publication authority.

## Capacity Packet Coverage

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
- `coord-pipeline-level5-opus-coordinator-e2e-executor-join`
- `coord-pipeline-level5-opus-existing-session-join`
- `coord-pipeline-level5-opus-manual-approval-e2e-executor-join`
- `coord-pipeline-level5-opus-receipt-corrective-join`
- `coord-pipeline-level5-opus-user-approved-join`
- `coord-pipeline-level5-wave0-join`
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
- `director-pipeline-level5-opus-coordinator-e2e-standby`
- `director-pipeline-level5-opus-existing-session-standby`
- `director-pipeline-level5-opus-manual-approval-e2e-standby`
- `director-pipeline-level5-opus-receipt-corrective-standby`
- `director-pipeline-level5-opus-user-approved-standby`
- `director-pipeline-level5-wave0-p0-containment`
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
- `director2-pipeline-level5-opus-coordinator-e2e-standby`
- `director2-pipeline-level5-opus-existing-session-transport`
- `director2-pipeline-level5-opus-manual-approval-e2e-standby`
- `director2-pipeline-level5-opus-receipt-corrective-implementation`
- `director2-pipeline-level5-opus-user-approved-transport`
- `director2-pipeline-level5-wave0-opus-finalization`
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
- `operator-pipeline-level5-opus-coordinator-e2e-standby`
- `operator-pipeline-level5-opus-existing-session-standby`
- `operator-pipeline-level5-opus-manual-approval-e2e-standby`
- `operator-pipeline-level5-opus-receipt-corrective-standby`
- `operator-pipeline-level5-opus-user-approved-standby`
- `operator-pipeline-level5-wave0-p0-containment-lanev`
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
- `operator2-pipeline-level5-opus-coordinator-e2e-lanev`
- `operator2-pipeline-level5-opus-existing-session-lanev`
- `operator2-pipeline-level5-opus-manual-approval-e2e-lanev`
- `operator2-pipeline-level5-opus-receipt-corrective-lanev`
- `operator2-pipeline-level5-opus-user-approved-lanev`
- `operator2-pipeline-level5-wave0-opus-final-lanev`
- `operator2-unit-coherence-observer-standby`

## Side-Effect Executor Token

- side_effect_id: `pipeline-level5-opus-receipt-corrective-route-2026-07-15`
- executor: `coordinator`
- target: this route mutation: close the completed manual-approval Operator2 packet, add the five
  corrective capacity packets, update the prior coordinator join with truthful
  FAIL closeout evidence, publish this one consolidated route, and make one
  exact-path local coordinator commit
- allowed_command_class: `apply_patch`, read-only validation, exact-path local
  staging, route mutation, and one local coordinator route commit
- preflight: user explicitly continued the coordinator; HEAD
  `563cc85c6716b746c5baff788cae8408c38b31d0`; coordinator unread zero; binding
  Operator2 FAIL body read; Wave 2 MET; capacity valid before route mutation;
  locks empty; smoke OK; protocol doctor PASS; user-owned untracked files
  identified and excluded
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if HEAD moves,
  new relevant mail lands, any route/packet path gains peer WIP, a newer route
  already satisfies the FAIL, locks appear, or capacity/route/doctor/smoke fails
- postcheck: committed scope contains exactly the two old packet updates, five
  new corrective packets, and this route; capacity and route validation pass;
  protocol doctor and smoke pass; old receipt state and production files remain
  unchanged
- observer_seats: `director`, `operator`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no production fix, provider launch, receipt/runtime mutation,
  approval-mode change, credential entry, retry, fallback, alternate reviewer,
  mailbox cursor write, lock/ref mutation, worktree creation, merge, external
  publication, cleanup, pod action, or production generation

## Validation Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2`:
  valid after the proposed packet transition.
- Pre-route `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2`:
  427 tests passed and `PROTOCOL DOCTOR: PASS`.
- Pre-route `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`:
  project smoke OK, ceremony gates PASS, 38 reports schema-valid, and
  architecture freshness PASS.
- `find coordination/locks -maxdepth 2 -type f -not -name .gitkeep -print`:
  no lock files.

Join condition: Director2 lands one cumulative descriptor-bound corrective
head and canonical verify-request; Operator2 returns one valid GO for that exact
head/range after reproducing and closing all five abuse cases; fresh capacity,
route, doctor, smoke, schema, architecture, and branch evidence pass. NITS or
FAIL returns only the bounded corrective diff to Director2 and does not join.

Cursor at send: all-scope-unpinned

## Exact Next Trigger

Continue as `director2` from
`director2-pipeline-level5-opus-receipt-corrective-implementation`. Start a
fresh isolated worktree at `563cc85c6716b746c5baff788cae8408c38b31d0`, fix
the five binding findings with pre-fix regression evidence, land one cumulative
descriptor-bound shipping head, and commit one canonical verify-request to
Operator2. Do not invoke Opus, reuse any prior receipt identity, merge, or
publish remotely.
