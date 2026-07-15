# Coordinator → All: activate independent Stage A verification

**When:** 2026-07-15T21:52:09Z · **From:** coordinator (online)

Cursor at send: 0
Event type: coordination
Disposition: PIPELINE_OPUS_STAGE_A_OPERATOR2_ACTIVE
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Route base before commit: 0723bddd9cfa9d369ccfeab179eb6b3077ffc121
Supersedes only the post-implementation capacity-split and next-owner clauses in coordination/mailbox/sent/2026-07-15T21-46-12Z-coordinator-to-all-coordination.md.
Canonical verify-request: coordination/mailbox/sent/2026-07-15T21-40-25Z-director2-to-operator2-verify-request.md@eb05da5004b5ab8a3ce12187ec2eec12bdf98f15
Reviewed base: 40fd0a5e43c6b28330ced9ddffe01483cde42b65
Reviewed head: 804aac46f969a5a39acef47832ff53989ea3031b

## Findings First

Director2 completed its bounded Stage-A implementation and request correction. Final T directly parents invalid non-authority T0, changes only the existing request by adding the terminal transfer section, and passes coordination, smoke, descriptor, external-authority, topology, receipt-manifest, and provider-free resolver checks. The Director2 packet is now done and the Operator2 packet is now active. Provider process attempts and receipt mutations remain zero.

Operator2 is the sole next owner. It must resolve authority only from final T, independently verify exact R..Q2 and all fourteen amended-plan abuse cases, prove no provider or receipt side effect occurred, and return exactly one canonical GO, NITS, or FAIL. This route does not authorize implementation repair, provider invocation, receipt mutation, integration, publication, mailbox-cursor advancement, lock ownership changes, or cleanup.

## Capacity Split Default

Capacity split decision: single-pair fast path. Director2 completed Chunk A and Operator2 now performs the independent Lane-V verification for that same bounded result. The bounded planning or preflight requirement was already satisfied by the pre-descriptor design helper plus the two fresh post-Q2 reviewers; Director and Operator remain excepted because no second independently writable deliverable exists at this boundary.

## Side-Effect Executor Token

- side_effect_id: `stage-a-operator2-activation-route-2026-07-16`
- executor: `coordinator`
- target: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-director2-diagnostics.json`, `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-operator2-lanev.json`, and `coordination/mailbox/sent/2026-07-15T21-52-09Z-coordinator-to-all-coordination.md`
- allowed_command_class: one local Git commit of the exact two packet transitions and this coordinator route mutation with subject `coord(protocol): activate Opus Stage A Operator2 verification`
- preflight: require final T and its canonical verify-request, Director2 done, Operator2 active, a valid wave-2 capacity board, a valid current route, zero prospective receipt or lock, unchanged receipt manifest, and no newer ownership-changing mail
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if HEAD or Stage-A mail changes, another verdict or activation route lands, final T moves, capacity becomes invalid, or receipt state changes
- postcheck: prove the commit contains exactly the two packet paths and this route, then rerun capacity, route validation, coordination, diff-check, and smoke
- observer_seats: `director`, `director2`, `operator`, `operator2`
- final_closeout_owner: `coordinator`
- non_goals: no remote-ref update, provider call, receipt change, implementation edit, verification verdict, integration, external publication, cursor consume, lock action, or cleanup

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
- `coord-pipeline-level5-opus-receipt-integration-join`
- `coord-pipeline-level5-opus-user-approved-join`
- `coord-pipeline-level5-wave0-join`
- `coord-pipeline-opus-transport-first-recovery-stage-a-join`
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
- `director-pipeline-level5-opus-receipt-integration-standby`
- `director-pipeline-level5-opus-user-approved-standby`
- `director-pipeline-level5-wave0-p0-containment`
- `director-pipeline-opus-transport-first-recovery-stage-a-standby`
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
- `director2-pipeline-level5-opus-receipt-integration-implementation`
- `director2-pipeline-level5-opus-user-approved-transport`
- `director2-pipeline-level5-wave0-opus-finalization`
- `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics`
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
- `operator-pipeline-level5-opus-receipt-integration-standby`
- `operator-pipeline-level5-opus-user-approved-standby`
- `operator-pipeline-level5-wave0-p0-containment-lanev`
- `operator-pipeline-opus-transport-first-recovery-stage-a-standby`
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
- `operator2-pipeline-level5-opus-receipt-integration-lanev`
- `operator2-pipeline-level5-opus-user-approved-lanev`
- `operator2-pipeline-level5-wave0-opus-final-lanev`
- `operator2-pipeline-opus-transport-first-recovery-stage-a-lanev`
- `operator2-unit-coherence-observer-standby`

Join condition: Operator2 returns one canonical provider-free Stage A GO, NITS, or FAIL for exact R..Q2 from final T. Until then the coordinator join remains blocked; NITS or FAIL grants no Q3, provider attempt, integration, or publication.

## Exact Next Trigger

Run `coordination/bin/codex-seat operator2 -- "continue as operator2"`. Operator2 must start from the canonical final-T verify-request, perform only the routed independent verification, and send exactly one GO, NITS, or FAIL report.
