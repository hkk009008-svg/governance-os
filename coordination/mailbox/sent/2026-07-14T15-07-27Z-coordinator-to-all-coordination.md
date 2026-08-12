# Coordinator -> All: route one manually approved end-to-end Opus attempt

**When:** 2026-07-14T15:07:27Z · **From:** coordinator (online)

Event type: coordination
Disposition: `PIPELINE_LEVEL5_OPUS_MANUAL_APPROVAL_E2E_ROUTE_ACTIVE`
Task-board: `pipeline-level5-opus-manual-approval-e2e-2026-07-14`
Protocol wave: `2`
Route base before commit: `b89a5a86a60e9954069caf35687f381d49b622fb`
Coordinator mailbox at preflight: `0 unread / all-scope; no consume`

## Findings First

The previous four Opus side-effect identities are terminal and remain untouched.
The most recent attempt was denied before process creation by the outer runtime.
The user then verified that this runtime can present and accept a manual approval
using a harmless read-only command, and directly instructed the active
coordinator: “try opus end to end.”

This route creates one distinct side-effect identity, `pipeline-level5-opus-manual-approval-e2e-attempt-2026-07-14`, with
authorization source `user-task:pipeline-level5-opus-manual-approval-e2e-2026-07-14`. It does not retry, replay,
resume, or reuse any prior identity. The provider command itself still requires
a fresh manual approval because it transmits private-repository review material
and may incur paid-service spend.

Fresh coordinator evidence at route base `b89a5a86a60e9954069caf35687f381d49b622fb`: unread is zero; Wave 2 is
MET; capacity and protocol doctor pass; locks contain only `.gitkeep`; the
immutable worktree is clean at `97c270f8f0e630fdaaded672e0da37ed32335de5`; base `555041477bcdb9a432a1b238d664be0958c5c9ef` is
an ancestor; bridge blob `5e37f668a9e0c401ea8583cd0e07cebfffa9ba67`,
receipt blob `a67da9672d5c94fc2916ad6c17d4d10841f7d122`, and descriptor
digest `sha256:e393655f4ba9ad0dcfa0467fcc54c809c79a1b28b76a2022a7d846acc8996e84` match the guarded prior route. The prior
`897 passed, 18 skipped` deterministic bundle is reusable because those
relevant blobs and the immutable worktree are unchanged; fresh smoke and doctor
passes are the current-state checks. No provider success is claimed.

## Coordinator Decision

Create one five-packet cycle:

- `coord-pipeline-level5-opus-manual-approval-e2e-executor-join` is active and holds the only provider/spend executor authority.
- `director-pipeline-level5-opus-manual-approval-e2e-standby`, `director2-pipeline-level5-opus-manual-approval-e2e-standby`, and `operator-pipeline-level5-opus-manual-approval-e2e-standby` are excepted.
- `operator2-pipeline-level5-opus-manual-approval-e2e-lanev` is blocked until one canonical receipt-backed coordinator verify-request lands.

Coordinator will invoke the merged bridge once against immutable range
`555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`, shipping commit `97c270f8f0e630fdaaded672e0da37ed32335de5`, descriptor
`2a876e95-3a87-4203-a613-1a29dd957b5b`, review profile `codex-lane-v`,
and transport profile `anthropic-claude-existing-session-v1`. Any denial,
ambiguity, timeout, unavailable or uncertain result, receipt conflict, or
normalized result ends the attempt with zero retry. A receipt proves transport,
not correctness.

## Capacity Split Default

Use the single-pair fast path because the external launch is one
authority-sensitive action. The bounded planning or preflight work is the
coordinator preflight. The other seats remain excepted; Operator2 activates only
from a lawful receipt-backed trigger.

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
- `operator2-pipeline-level5-opus-user-approved-lanev`
- `operator2-pipeline-level5-wave0-opus-final-lanev`
- `operator2-unit-coherence-observer-standby`

## Side-Effect Executor Token

- side_effect_id: `pipeline-level5-opus-manual-approval-e2e-attempt-2026-07-14`
- executor: `coordinator`
- target: `scripts/opus_review_bridge.py review` for `555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`, Anthropic/Claude existing-session paid-service spend, this coordinator route mutation, one content-free acceptance log, and any canonical receipt-backed verify-request
- allowed_command_class: exact-path coordinator route mutation and local commit; one manually approved `opus_review_bridge.py review` paid-service spend command; read-only preflight/postchecks; one content-free result reconciliation; if receipt exists, one canonical coordinator verify-request
- preflight: user directly instructed the active coordinator to try Opus end to end after verifying manual approval; HEAD `b89a5a86a60e9954069caf35687f381d49b622fb`; coordinator unread zero; Wave 2 MET; capacity, doctor, and smoke pass; locks empty; receipt root absent; immutable worktree clean at `97c270f8f0e630fdaaded672e0da37ed32335de5`; bridge, receipt, descriptor, prompt-authority, and reviewed-base evidence unchanged
- stop_if_newer_mail_or_live_target_satisfied: stop before commit or launch if HEAD moves, relevant mailbox state changes, a provider/bridge process or receipt appears, target paths gain peer WIP, the immutable worktree drifts, any environment/credential fence fails, or capacity, route, doctor, smoke, blob, ancestry, descriptor, or manual approval validation fails
- postcheck: record exactly one launch-request outcome; if a receipt exists, preserve it and route one Operator2 verify-request; otherwise park this cycle; confirm zero retry/fallback, immutable worktree unchanged, no unexpected process, capacity/route/doctor/smoke valid, and exact committed metadata scope
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no production edit, credential entry, API/Chrome/manual or alternate-transport fallback, retry, replay, workaround, prior-identity reuse, raw prompt/response persistence, cursor consume, lock/ref mutation, worktree change, merge, push, publication, cleanup, pod action, production generation, downstream PPL action, or claim that receipt presence is GO

## Validation Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2`: valid before this route.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2`: PASS.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`: `OK`.
- `env -u GIT_INDEX_FILE git -C .worktrees/opus-lanev-receipt-hardening status --short`: empty.
- `env -u GIT_INDEX_FILE git merge-base --is-ancestor 555041477bcdb9a432a1b238d664be0958c5c9ef 97c270f8f0e630fdaaded672e0da37ed32335de5`: exit 0.

Join condition: one bridge-issued receipt under `pipeline-level5-opus-manual-approval-e2e-attempt-2026-07-14`, one
Operator2 verification-report GO for the immutable range, and fresh
capacity/route/doctor/smoke/receipt evidence. A denial or receipt-less result
ends this cycle without joining.

Cursor at send: all-scope-unpinned

## Exact Next Trigger

Remain in coordinator. Commit this validated route, refresh every named
preflight, and submit the exact bridge command for manual approval once. If and
only if a real receipt exists, land one canonical receipt-backed verify-request
for Operator2. Any denial, ambiguity, timeout, unavailable or uncertain result,
drift, or missing precondition parks this cycle permanently with zero retry.
