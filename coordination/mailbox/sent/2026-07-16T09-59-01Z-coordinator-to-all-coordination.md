# Coordinator → All: retire provider routes and route targeted decommission

**When:** 2026-07-16T09:59:01Z · **From:** coordinator (online)

Event type: coordination
Disposition: PROVIDER_TOOLS_TARGETED_DECOMMISSION_ACTIVE
Task-board: provider-tools-targeted-decommission-2026-07-16
Protocol wave: 2
Approved design: 66c73f07c2cedb998a6709db9b5a2ff4ce47812e

## Decision and Preservation Boundary

User-principal decision: permanently retire the executable ChatGPT Pro consultation and Opus review subsystems while preserving generic Lane V and historical audit evidence.

Packet transitions:
- operator-chatgpt-local-reprepare-task1-lanev: blocked -> excepted
- coord-chatgpt-local-reprepare-task1-join: blocked -> excepted
- operator2-pipeline-opus-transport-first-recovery-stage-a-lanev: blocked -> excepted
- coord-pipeline-opus-transport-first-recovery-stage-a-join: blocked -> excepted

Preservation boundary: keep Git history, historical mailbox events, plans, specifications, logs, scope descriptors, completed packets, historical handoffs, and ignored local runtime evidence unchanged.

Execution boundary: no future task may invoke ChatGPT Pro, Claude, Opus, a provider CLI, an in-app browser, a paid API, a provider retry, or an Opus receipt lifecycle. Do not clean provider/runtime state, push, or merge.

## Sequential Ownership

- Director owns Tasks 2-3.
- Director2 starts only after Director finishes and owns Tasks 4-5.
- Operator2 asks the bounded Task 6 quality-preflight question without repair.
- Operator performs the final provider-neutral Lane V pass without repair.
- Coordinator closes only after one schema-valid GO.

## Capacity Split Default

Dual-pair routing is sequential because the shared compact, report, and doctrine surfaces prohibit overlap.
Chunk A: Director owns Tasks 2-3 and their exact packet scope.
Chunk B: Director2 owns Tasks 4-5 only after Chunk A is terminal and then works only inside its exact packet scope.
Operator2 performs the bounded quality preflight after Chunk B; Operator performs the final provider-neutral Lane V pass.

## Capacity Packet Coverage

All post-edit Wave-2 packet IDs are named.
- coord-ledger-t14-align-join
- coord-ledger-t14-align-route
- director-ledger-publication-decision
- director2-ledger-next-brief
- operator-pipeline-tooling-verify
- operator2-ledger-main-verify
- coord-execution-strength-broader-join
- director-execution-strength-broader-impl
- director2-execution-strength-broader-observer
- operator-execution-strength-broader-verification
- operator2-execution-strength-broader-observer
- coord-governance-hardening-bridge-join
- director-governance-hardening-bridge-impl
- director2-governance-hardening-bridge-observer
- operator-governance-hardening-bridge-lanev
- operator2-governance-hardening-bridge-observer
- coord-ledger-phase2-task21-join
- coord-ledger-phase2-task21-route
- director-ledger-phase2-task21-write-path
- director2-ledger-phase2-bounds-plan-sync
- operator-ledger-phase2-task21-lanev
- operator2-ledger-phase2-base-preflight
- coord-ledger-phase2-task22-join
- director-ledger-phase2-task22-validations
- director2-ledger-phase2-task22-observer
- operator-ledger-phase2-task22-lanev
- operator2-ledger-phase2-task22-observer
- coord-ledger-phase2-task23-join
- director-ledger-phase2-task23-result-history
- director2-ledger-phase2-task23-observer
- operator-ledger-phase2-task23-lanev
- operator2-ledger-phase2-task23-observer
- coord-ledger-phase2-task24-join
- director-ledger-phase2-task24-ios-slot-entry
- director2-ledger-phase2-task24-observer
- director2-ledger-phase2-task24-planning-preflight
- operator-ledger-phase2-task24-lanev
- operator2-ledger-phase2-task24-observer
- operator2-ledger-phase2-task24-preflight
- coord-ledger-runway-stage0-join
- coord-ledger-runway-stage0-route
- director-ledger-runway-stage0-owner-gates
- director2-ledger-runway-plan-reconcile
- operator-ledger-runway-stage0-verify
- operator2-ledger-runway-worktree-verify
- coord-unit-coherence-side-effect-token-join
- director-unit-coherence-side-effect-token-impl
- director2-unit-coherence-observer-standby
- operator-unit-coherence-side-effect-token-verification
- operator2-unit-coherence-observer-standby
- coord-ledger-phase2-detail-integration-join
- director-ledger-phase2-detail-integration
- director2-ledger-phase2-detail-integration-preflight
- operator-ledger-phase2-detail-integration-lanev
- operator2-ledger-phase2-detail-integration-preflight
- coord-ledger-phase2-task25-26-join
- director-ledger-phase2-task25a-result-entry
- operator-ledger-phase2-task25a-lanev
- director2-ledger-phase2-task26a-history-component
- operator2-ledger-phase2-task26a-lanev
- coord-control-plane-authority-foundation-join
- director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix
- director-control-plane-authority-foundation-task2-race-fix
- director-control-plane-authority-foundation-task2-replacement
- director-control-plane-authority-foundation-task2-spec-review-fix
- director-control-plane-authority-foundation-task2u-fail-closed-closure
- director-control-plane-authority-foundation-tasks1-2
- director2-control-plane-authority-foundation-identity-interface-closure-preflight
- director2-control-plane-authority-foundation-identity-preflight
- director2-control-plane-authority-foundation-identity-repreflight
- director2-control-plane-authority-foundation-identity-rerepreflight
- director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight
- director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight
- director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight
- director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight
- director2-control-plane-authority-foundation-task3h-causal-runtime-proof-closure-preflight
- director2-control-plane-authority-foundation-task3i-execution-contract-closure-preflight
- operator-control-plane-authority-foundation-lanev
- operator-control-plane-authority-foundation-replacement-lanev
- operator-control-plane-authority-foundation-task2u-cumulative-lanev
- operator2-control-plane-authority-foundation-cutover-preflight
- operator2-control-plane-authority-foundation-activation-repreflight
- coord-ledger-workbook-refresh-join
- director-ledger-workbook-refresh-implementation
- director2-ledger-workbook-refresh-contract-correction-preflight
- director2-ledger-workbook-refresh-preflight
- operator-ledger-workbook-refresh-lanev
- operator2-ledger-workbook-refresh-preflight
- coord-ledger-ppl-recommendation-evaluation-join
- director-ledger-ppl-recommendation-evaluation-implementation
- director2-ledger-ppl-recommendation-evaluation-preflight
- operator-ledger-ppl-recommendation-evaluation-lanev
- operator2-ledger-ppl-recommendation-evaluation-preflight
- coord-pipeline-level5-opus-coordinator-e2e-executor-join
- director-pipeline-level5-opus-coordinator-e2e-standby
- director2-pipeline-level5-opus-coordinator-e2e-standby
- operator-pipeline-level5-opus-coordinator-e2e-standby
- operator2-pipeline-level5-opus-coordinator-e2e-lanev
- coord-pipeline-level5-opus-existing-session-join
- director-pipeline-level5-opus-existing-session-standby
- director2-pipeline-level5-opus-existing-session-transport
- operator-pipeline-level5-opus-existing-session-standby
- operator2-pipeline-level5-opus-existing-session-lanev
- coord-pipeline-level5-opus-manual-approval-e2e-executor-join
- director-pipeline-level5-opus-manual-approval-e2e-standby
- director2-pipeline-level5-opus-manual-approval-e2e-standby
- operator-pipeline-level5-opus-manual-approval-e2e-standby
- operator2-pipeline-level5-opus-manual-approval-e2e-lanev
- coord-pipeline-level5-opus-user-approved-join
- director-pipeline-level5-opus-user-approved-standby
- director2-pipeline-level5-opus-user-approved-transport
- operator-pipeline-level5-opus-user-approved-standby
- operator2-pipeline-level5-opus-user-approved-lanev
- coord-pipeline-level5-wave0-join
- director-pipeline-level5-wave0-p0-containment
- director2-pipeline-level5-wave0-opus-finalization
- operator-pipeline-level5-wave0-p0-containment-lanev
- operator2-pipeline-level5-wave0-opus-final-lanev
- coord-pipeline-level5-opus-receipt-corrective-join
- director-pipeline-level5-opus-receipt-corrective-standby
- director2-pipeline-level5-opus-receipt-corrective-implementation
- operator-pipeline-level5-opus-receipt-corrective-standby
- operator2-pipeline-level5-opus-receipt-corrective-lanev
- coord-pipeline-level5-opus-receipt-integration-join
- director-pipeline-level5-opus-receipt-integration-standby
- director2-pipeline-level5-opus-receipt-integration-implementation
- operator-pipeline-level5-opus-receipt-integration-standby
- operator2-pipeline-level5-opus-receipt-integration-lanev
- coord-pipeline-opus-transport-first-recovery-stage-a-join
- director-pipeline-opus-transport-first-recovery-stage-a-standby
- director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics
- operator-pipeline-opus-transport-first-recovery-stage-a-standby
- operator2-pipeline-opus-transport-first-recovery-stage-a-lanev
- coord-chatgpt-local-reprepare-task1-join
- director-chatgpt-local-reprepare-task1-candidate
- director2-chatgpt-local-reprepare-task1-preflight
- operator-chatgpt-local-reprepare-task1-lanev
- operator2-chatgpt-local-reprepare-task1-preflight
- coord-provider-tools-decommission-join
- director-provider-tools-decommission-implementation
- director2-provider-tools-decommission-implementation
- operator-provider-tools-decommission-lanev
- operator2-provider-tools-decommission-quality-preflight

## Side-Effect Executor Token

- side_effect_id: `provider-tools-targeted-decommission-route-2026-07-16`
- executor: `coordinator`
- target: the four exact legacy packet transitions, five new decommission packet files, `docs/HANDOFF-owner-2026-07-16-provider-tool-decommission.md`, and this canonical coordinator-to-all route event
- allowed_command_class: fresh read-only git, mailbox, capacity, and status checks; metadata-only apply_patch; exact-path staging and one local coordinator commit; capacity, route, coordination, smoke, and diff postchecks
- preflight: HEAD, approved design and plan, four blocked packets, mailbox, locks, index, and ambient exclusions match Task 1 and no newer retirement event exists
- stop_if_newer_mail_or_live_target_satisfied: stop before mutation if HEAD, mailbox, packet state, locks, index, route identity, owner handoff, or overlapping WIP differs, or another actor already completed the target
- postcheck: exact eleven-path metadata set; four legacy packets excepted; five new packets in required sequential states; capacity and route valid; coordination and smoke pass; must not invoke a provider, mutate runtime state, push, merge, or clean up
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no production edit, provider/browser/API call, provider retry, receipt/runtime mutation, push, merge, publication, cleanup, cursor consume, lock action, or ambient-WIP mutation

Join condition: Director completes reviewed Tasks 2-3; Director2 then completes reviewed Tasks 4-5 and the spec event; Operator2 returns the bounded quality PASS; Operator returns one schema-valid provider-neutral Lane V GO; Coordinator alone then closes the cycle.

## Exact Next Trigger

Director starts Task 2 only after this metadata-only route commit passes the Wave-2 capacity and route validators; every later seat waits for its committed dependency and explicit activation.

Cursor at send: 0
