# Coordinator -> All: correct Stage A descriptor command contract

**When:** 2026-07-15T13:03:19Z · **From:** coordinator (online)

Event type: coordination
Disposition: PIPELINE_OPUS_TRANSPORT_FIRST_STAGE_A_DESCRIPTOR_CONTRACT_CORRECTED
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Route base before commit: 39d2cf3429e533419c3dc70c5245bb42b6d601aa
Supersedes only the descriptor-command clause in: coordination/mailbox/sent/2026-07-15T12-19-46Z-coordinator-to-all-coordination.md
Plan: docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md
Coordinator mailbox at preflight: 0 unread / all-scope; no consume

## Findings First

Director2's blocker at
`coordination/mailbox/sent/2026-07-15T12-55-36Z-director2-to-coordinator-coordination.md`
is confirmed. The bridge accepts descriptor verification commands only when
they start with `env -u GIT_INDEX_FILE` and invoke `.venv/bin/python` or the
trusted absolute Python interpreter. The routed `git diff --check` command is
therefore mandatory evidence but structurally invalid as a descriptor command.

Choose the smallest correction. Do not widen the trusted command allowlist.
The descriptor `verification_commands` must contain exactly:

```text
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_verification_report_gate.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

`env -u GIT_INDEX_FILE git diff --check` remains mandatory before each Stage A
shipping, descriptor, and verify-request commit and during Operator2 Lane V,
but it must not be serialized into the descriptor. This corrects instruction
consistency only; it does not change bridge code, the security allowlist, the
descriptor schema, or any transport behavior.

## Corrected Seat Routes

Director2:

- Packet `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics`
  remains active with descriptor
  `b8c59c86-2426-46cf-8975-7b075d75fc09`.
- Resume only from the commit containing this correction. The existing clean
  isolated worktree may be fast-forwarded to that commit or replaced by a new
  isolated worktree; do not implement from stale base `bcae6d2`.
- Execute plan Tasks 1-3. The corrected coordinator commit is the descriptor's
  exact reviewed base, and the later shipping diagnostics commit is its
  reviewed head. Require both coordinator routes plus the corrected plan.
- Provider process attempts authorized: 0. Stop after one shipping commit, one
  descriptor-only commit, and one canonical verify-request-only commit.

Operator2:

- Packet `operator2-pipeline-opus-transport-first-recovery-stage-a-lanev`
  remains blocked until the corrected canonical descriptor and verify-request
  resolve provider-free.
- Run both descriptor commands plus supplemental `git diff --check` and the
  packet's existing no-provider checks. Return exactly one GO, NITS, or FAIL
  for Stage A diagnostics only.

Director and Operator remain excepted. The coordinator join remains blocked on
Operator2. All original Stage A constraints not explicitly corrected here
remain binding, including the terminal prior receipt and zero provider calls.

Join condition: Operator2 returns one canonical Stage A GO, NITS, or FAIL for the corrected descriptor/request; until then the coordinator join remains blocked.

## Capacity Split Default

Reject dual-pair routing. Chunk A would change the same bridge/receipt paths and
Chunk B would depend on the identical descriptor boundary, so they are not
independently reviewable. Keep the single-pair fast path: Director2 implements
and Operator2 verifies. The bounded planning or preflight signal remains the
reconciled manual ChatGPT Pro challenge plus Director2's executable contract
blocker; Pair A remains excepted.

## Subagent Utilization

Direct/no-op for this correction. The issue is a small, tightly coupled,
authority-sensitive route contradiction already proven by Director2 and
confirmed against the bridge validator. No helper consumes mail, writes a
route, issues a verdict, invokes a provider, or authorizes a side effect.

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

- side_effect_id: pipeline-opus-transport-first-stage-a-descriptor-contract-correction-2026-07-15
- executor: coordinator
- target: the Stage A plan and this one coordinator-to-all correction route in one exact-path local metadata commit
- allowed_command_class: apply_patch, read-only local validation, scoped temporary-index staging, route mutation, and one local coordinator metadata commit
- preflight: user instructed continue as coordinator; HEAD is 39d2cf3429e533419c3dc70c5245bb42b6d601aa; coordinator unread is zero; Wave 2 is MET; capacity is valid; smoke passes; locks and shared index are empty; target paths have no peer WIP; Director2's blocker and validator code were read; the rejected Git command is covered by the existing invalid-command test
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if HEAD moves, newer relevant mail lands, a target path gains peer WIP, a lock/shared-index/Git-operation entry appears, packet state changes, the terminal receipt changes, or plan consistency, capacity, route validation, Protocol Doctor, smoke, exact-scope, secrecy, or diff checks fail
- postcheck: the committed scope is exactly this plan and this route; capacity and corrected-route validation, Protocol Doctor, smoke, exact-scope, and diff checks pass; production code, packet state, receipts, runtime state, refs, worktrees, shared root WIP, and remote state remain unchanged
- observer_seats: director, director2, operator, operator2, coordinator2
- final_closeout_owner: coordinator
- non_goals: no production/test/packet change, command-allowlist expansion, descriptor construction, provider call, retry, fallback, canary, receipt/runtime mutation, credential or browser action, cursor consume, lock action, merge, cherry-pick, push, remote publication, branch/worktree cleanup, unrelated cleanup, pod action, or production generation

## Validation Evidence

- `scripts/opus_review_bridge.py::_validated_verification_rule` requires the
  trusted Python interpreter and accepts `scripts/ci_smoke.py` without
  arguments.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_opus_review_bridge.py::test_review_rejects_mutating_network_provider_or_arbitrary_commands -q`
  passes all 11 cases, including rejection of a Git verifier command.
- Capacity, corrected-route, Protocol Doctor, smoke, exact-scope, and diff
  checks are mandatory before this event is committed.

## Exact Next Trigger

Run `coordination/bin/codex-seat director2 -- "continue as director2"`. Director2 resumes from the commit containing this correction and executes provider-free Stage A Tasks 1-3.

No Claude or Opus process, receipt, merge, or push is authorized.
