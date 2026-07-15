# Coordinator → All: preserve control-plane WIP for compact convergence

**When:** 2026-07-15T22:02:30Z · **From:** coordinator (online)

Event type: coordination
Disposition: CONTROL_PLANE_WIP_PRESERVATION_ONLY
Task-board: pipeline-recovery-owner-wip-disposition-2026-07-16
Protocol wave: 2
Route base before commit: 6e336a09143f7939dc8c3b6f1c839586c7d16d88
Plan: docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md

Director retains ownership of the parked nine-path Task2U working snapshot at
base 6983673db60bff0d21548a90ab1db2fcbbfa377a. Switch only that worktree to
codex/recovery-control-plane-wip-2026-07-16, commit the nine exact paths as
preservation evidence, execute the four named focused test files, and publish
docs/HANDOFF-owner-2026-07-16-control-plane-wip.md. This does not authorize Task2U
acceptance, GO, integration, activation, merge, remote-ref update, cleanup, or
modification of another path. The original control-plane branch ref remains fixed at the
base above.

This route is additive and disjoint from the committed Stage-A route
coordination/mailbox/sent/2026-07-15T21-52-09Z-coordinator-to-all-coordination.md.
Operator2 remains the sole active Stage-A verifier for final T eb05da5004b5ab8a3ce12187ec2eec12bdf98f15; Director must not touch the Stage-A branch, request, descriptor, receipts, or provider boundary.

Join condition: the preservation branch and owner handoff exist at exact full
SHAs, the original branch still equals the base above, and no production
integration or side effect occurred. The separate Stage-A join remains blocked on its canonical Operator2 GO/NITS/FAIL.

## Capacity Split Default

For the control-plane preservation unit, use the single-pair fast path for this one-owner action; Pair B is limited to bounded planning or preflight. Reject dual-pair routing because Chunk A and Chunk B would share the same nine dirty blobs. The already-routed Stage-A Operator2 verification remains a separate disjoint Lane-V action rather than a second control-plane chunk.

## Capacity Packet Coverage

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
- `coord-ledger-phase2-task24-join`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `operator-ledger-phase2-task24-lanev`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
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
- `coord-ledger-phase2-detail-integration-join`
- `director-ledger-phase2-detail-integration`
- `director2-ledger-phase2-detail-integration-preflight`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator2-ledger-phase2-detail-integration-preflight`
- `coord-ledger-phase2-task25-26-join`
- `director-ledger-phase2-task25a-result-entry`
- `operator-ledger-phase2-task25a-lanev`
- `director2-ledger-phase2-task26a-history-component`
- `operator2-ledger-phase2-task26a-lanev`
- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`
- `director-control-plane-authority-foundation-task2-race-fix`
- `director-control-plane-authority-foundation-task2-replacement`
- `director-control-plane-authority-foundation-task2-spec-review-fix`
- `director-control-plane-authority-foundation-task2u-fail-closed-closure`
- `director-control-plane-authority-foundation-tasks1-2`
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
- `operator-control-plane-authority-foundation-lanev`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `operator-control-plane-authority-foundation-task2u-cumulative-lanev`
- `operator2-control-plane-authority-foundation-cutover-preflight`
- `operator2-control-plane-authority-foundation-activation-repreflight`
- `coord-ledger-workbook-refresh-join`
- `director-ledger-workbook-refresh-implementation`
- `director2-ledger-workbook-refresh-contract-correction-preflight`
- `director2-ledger-workbook-refresh-preflight`
- `operator-ledger-workbook-refresh-lanev`
- `operator2-ledger-workbook-refresh-preflight`
- `coord-ledger-ppl-recommendation-evaluation-join`
- `director-ledger-ppl-recommendation-evaluation-implementation`
- `director2-ledger-ppl-recommendation-evaluation-preflight`
- `operator-ledger-ppl-recommendation-evaluation-lanev`
- `operator2-ledger-ppl-recommendation-evaluation-preflight`
- `coord-pipeline-level5-opus-coordinator-e2e-executor-join`
- `director-pipeline-level5-opus-coordinator-e2e-standby`
- `director2-pipeline-level5-opus-coordinator-e2e-standby`
- `operator-pipeline-level5-opus-coordinator-e2e-standby`
- `operator2-pipeline-level5-opus-coordinator-e2e-lanev`
- `coord-pipeline-level5-opus-existing-session-join`
- `director-pipeline-level5-opus-existing-session-standby`
- `director2-pipeline-level5-opus-existing-session-transport`
- `operator-pipeline-level5-opus-existing-session-standby`
- `operator2-pipeline-level5-opus-existing-session-lanev`
- `coord-pipeline-level5-opus-manual-approval-e2e-executor-join`
- `director-pipeline-level5-opus-manual-approval-e2e-standby`
- `director2-pipeline-level5-opus-manual-approval-e2e-standby`
- `operator-pipeline-level5-opus-manual-approval-e2e-standby`
- `operator2-pipeline-level5-opus-manual-approval-e2e-lanev`
- `coord-pipeline-level5-opus-user-approved-join`
- `director-pipeline-level5-opus-user-approved-standby`
- `director2-pipeline-level5-opus-user-approved-transport`
- `operator-pipeline-level5-opus-user-approved-standby`
- `operator2-pipeline-level5-opus-user-approved-lanev`
- `coord-pipeline-level5-wave0-join`
- `director-pipeline-level5-wave0-p0-containment`
- `director2-pipeline-level5-wave0-opus-finalization`
- `operator-pipeline-level5-wave0-p0-containment-lanev`
- `operator2-pipeline-level5-wave0-opus-final-lanev`
- `coord-pipeline-level5-opus-receipt-corrective-join`
- `director-pipeline-level5-opus-receipt-corrective-standby`
- `director2-pipeline-level5-opus-receipt-corrective-implementation`
- `operator-pipeline-level5-opus-receipt-corrective-standby`
- `operator2-pipeline-level5-opus-receipt-corrective-lanev`
- `coord-pipeline-level5-opus-receipt-integration-join`
- `director-pipeline-level5-opus-receipt-integration-standby`
- `director2-pipeline-level5-opus-receipt-integration-implementation`
- `operator-pipeline-level5-opus-receipt-integration-standby`
- `operator2-pipeline-level5-opus-receipt-integration-lanev`
- `coord-pipeline-opus-transport-first-recovery-stage-a-join`
- `director-pipeline-opus-transport-first-recovery-stage-a-standby`
- `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics`
- `operator-pipeline-opus-transport-first-recovery-stage-a-standby`
- `operator2-pipeline-opus-transport-first-recovery-stage-a-lanev`

## Exact Next Trigger

Run `coordination/bin/codex-seat director -- "continue as director"` or continue in the explicitly user-authorized Director seat. Director preserves the exact nine-path snapshot and stops after the committed owner handoff. Coordinator then rechecks the original and preservation refs. Operator2 independently resumes only through its existing Stage-A trigger.

Cursor at send: 0
