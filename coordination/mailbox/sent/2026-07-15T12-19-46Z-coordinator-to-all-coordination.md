# Coordinator -> All: route Opus transport-first recovery Stage A

**When:** 2026-07-15T12:19:46Z · **From:** coordinator (online)

Event type: coordination
Disposition: PIPELINE_OPUS_TRANSPORT_FIRST_RECOVERY_STAGE_A_ACTIVE
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Route base before commit: f0fb231f64b6a22e19ef214e7994f0ab2f3e6183
Plan: docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md
Coordinator mailbox at preflight: 0 unread / all-scope; no consume

## Findings First

Opus is not fixed. The only real attempt remains terminal receipt
`opr1:de2f5b672b8e1ea03b7575d7a636e0d56bef9817f0d8b5b74fb0632678b68f85`:
`process_failed` at `provider_exit`, no effective model, and zero findings.
Current code proves the CLI binary resolves, host seatbelt and AF_UNIX probes
pass, retry counts are zero, and `system/init.model` is the authoritative
model field. It does not preserve the original child's return code, signal, or
sanitized stderr category, so the first failed transport boundary remains
unproven.

The current broad hypothesis that a real `HOME` plus outer-profile HOME write
denial may interfere with existing-session startup is unverified. Stage A tests
that boundary only with a fake client and pytest-owned temporary HOME; it does
not broaden access or treat the hypothesis as a fix.

## Authorized Stage A

Director2 may add only provider-free, secret-safe diagnostics and deterministic
fake-client tests under the committed plan. Public unavailable reasons and
failure stages, receipt one-shot behavior, environment allowlisting, sandbox
behavior, model validation, and transport profile
`anthropic-claude-existing-session-v1` remain fail-closed.

Provider process attempts authorized: 0. This route carries no provider-side
diagnostic identity, canary identity, paid-service executor, merge authority, or
remote-ref executor. Any such action requires a later fresh coordinator route,
state binding, descriptor/receipt identity, and Side-Effect Executor Token.

## Seat Routes

Director:

- Packet `director-pipeline-opus-transport-first-recovery-stage-a-standby` is
  excepted because a parallel bridge implementation would overlap the same
  causal boundary.
- Report only a contradiction, changed authority boundary, or explicit
  coordinator request.

Director2:

- Packet
  `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics` is
  active.
- Start from this committed route in an isolated worktree. Execute plan Tasks
  1-3 with tests first, preserve unrelated root WIP, and create no provider
  process or receipt.
- Land one shipping diagnostics commit, descriptor
  `b8c59c86-2426-46cf-8975-7b075d75fc09`, and one canonical committed
  verify-request. Stop with Operator2 as next owner.

Operator:

- Packet `operator-pipeline-opus-transport-first-recovery-stage-a-standby` is
  excepted because a second same-question verdict would be redundant.
- Do not duplicate Lane V or invoke a provider.

Operator2:

- Packet `operator2-pipeline-opus-transport-first-recovery-stage-a-lanev`
  remains blocked until the canonical request resolves provider-free to the
  fresh descriptor.
- Verify the exact diagnostic diff and all ten committed abuse cases without
  invoking Opus. Return exactly one canonical GO, NITS, or FAIL.
- A GO proves Stage A diagnostics only. It must name the first proven boundary
  or exact remaining ambiguity and does not mean transport is restored.

Coordinator:

- Packet `coord-pipeline-opus-transport-first-recovery-stage-a-join` remains
  blocked on Operator2.
- On GO, route only the smallest proven Stage B repair. On NITS or FAIL, route
  only the diagnostic correction. Do not author production behavior.

## Capacity Split Default

Reject dual-pair routing. Chunk A would own the bridge and receipt diagnostic
contract while Chunk B would require the same files and same failure boundary,
so the chunks are not independently reviewable. Use the single-pair fast path:
Director2 implements and Operator2 verifies. The bounded planning or preflight
signal is the reconciled manual ChatGPT Pro adversarial consultation plus the
coordinator's local code, receipt, capability, and failure-layer audit. Pair A
remains excepted.

## ChatGPT Pro Consultation Summary

- Consultation ID: `ca74dca9-948a-4b59-8b01-07840cb65715`
- Phase: design-time adversarial recovery planning
- Bound HEAD/route:
  `f0fb231f64b6a22e19ef214e7994f0ab2f3e6183` /
  `pipeline-level5-opus-receipt-integration-2026-07-15`
- Question: how to restore existing-session Opus end to end after a terminal
  `provider_exit/process_failed` receipt without retry, fallback, or
  authority drift
- Advice summary: isolate executable, process, I/O, sandbox, session,
  authentication, parser, model, and receipt layers with zero-provider
  evidence; add minimum sanitized observability; repair only the first proven
  boundary; then use one fresh canary and independent GO
- Codex dispositions: adopted transport-first isolation, fake-client coverage,
  fresh identity per attempt, one-shot canary, and GO-before-merge; modified
  the advice to extend existing bridge/receipt machinery; rejected
  replacement-first, broad HOME access, browser/API fallback, automatic retry,
  and premature canary; unresolved the original return code, signal,
  diagnostic category, and session entitlement pending Stage A
- Resulting change: this active route authorizes Stage A only; root repair,
  canary, merge, and publication remain later separately gated stages

The consultation does not authorize a route, trigger, provider, receipt, verdict, merge, push, or other side effect; it is advisory only.

## Subagent Utilization

Direct/no-op. Route construction is authority-sensitive, the relevant local
facts are already bounded, and the guarded manual ChatGPT Pro consultation
supplies the independent design-time challenge. No new helper would add a
distinct question without duplicating current evidence. No subagent consumes,
writes mail, issues GO, invokes a provider, mutates refs, or authorizes a side
effect.

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

## Side-Effect Executor Token

- side_effect_id: pipeline-opus-transport-first-recovery-stage-a-route-2026-07-15
- executor: coordinator
- target: this plan, the five new Stage A capacity packets, this one coordinator-to-all route, and one exact-path local coordinator commit
- allowed_command_class: apply_patch, read-only local validation, scoped temporary-index staging, route mutation, and one local coordinator metadata commit
- preflight: user explicitly instructed the coordinator to proceed with the Opus transport-first recovery route; HEAD is f0fb231f64b6a22e19ef214e7994f0ab2f3e6183; coordinator unread is zero; Wave 2 is MET; capacity was valid; locks and the shared index were empty; smoke passed; the newest handoff and relevant mailbox bodies were read; the manual consultation is reconciled; target paths had no peer WIP
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if HEAD moves, newer relevant mail lands, any target path gains peer WIP, a lock/shared-index/Git-operation entry appears, the terminal receipt changes, or JSON parsing, capacity, route validation, Protocol Doctor, smoke, exact-scope, secrecy, or diff checks fail
- postcheck: the committed scope is exactly the plan, five packet files, and this route; capacity and route validation, Protocol Doctor, smoke, JSON parsing, exact-scope, and diff checks pass; production, receipts, runtime state, refs, worktrees, shared root WIP, and remote state remain unchanged
- observer_seats: director, director2, operator, operator2, coordinator2
- final_closeout_owner: coordinator
- non_goals: no production fix, real Claude or Opus invocation, provider-side diagnostic, canary, receipt/runtime mutation, credential or browser action, API/fallback/retry, cursor consume, lock action, merge, cherry-pick, push, remote publication, branch/worktree cleanup, unrelated cleanup, pod action, or production generation

## Validation Evidence

- `scripts/protocol_capacity_board.py --wave 2` reports valid true with the new
  Stage A cycle active and no blocking issues.
- Capacity route validation reports route valid true with no blocking issues.
- Protocol Doctor passes its coordination, binding, lineage, capacity, route,
  protocol-test, and smoke bundle.
- `scripts/ci_smoke.py` passes project, ceremony, placeholder, GO-schema, and
  architecture-freshness checks.
- Every new packet parses as JSON; focused capacity tests pass; the exact
  seven-path `git diff --check` is clean.

Join condition: Stage A joins only after Director2 lands the provider-free diagnostic head and canonical descriptor/request, Operator2 returns one binding GO/NITS/FAIL, and the coordinator reconciles the exact first-failed-layer evidence. GO routes a fresh Stage B root repair; it does not close Opus as fixed or authorize a provider call.

## Exact Next Trigger

Continue as Director2 from the committed Stage A route. Create an isolated
worktree, execute Tasks 1-3 of the committed plan with zero provider attempts,
land the shipping diagnostics commit plus descriptor
`b8c59c86-2426-46cf-8975-7b075d75fc09` and one canonical verify-request, then
stop with Operator2 as next owner. Do not launch Opus.
