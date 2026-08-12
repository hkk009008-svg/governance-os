# Coordinator -> All: correct Stage A append-only review-fix history contract

**When:** 2026-07-15T15:33:10Z · **From:** coordinator (online)

Event type: coordination
Disposition: PIPELINE_OPUS_TRANSPORT_FIRST_STAGE_A_HISTORY_CONTRACT_CORRECTED
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Route base before commit: ab4cc556965682c7f4cbf01b8599d9d31c4ceeb6
Supersedes only the Stage A implementation-history clauses in: coordination/mailbox/sent/2026-07-15T12-19-46Z-coordinator-to-all-coordination.md and coordination/mailbox/sent/2026-07-15T13-03-19Z-coordinator-to-all-coordination.md
Plan: docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md
Coordinator mailbox at preflight: 0 unread / all-scope; no consume

## Findings First

Director2's blocker at
`coordination/mailbox/sent/2026-07-15T14-10-21Z-director2-to-coordinator-coordination.md`
is confirmed. Independent spec review found one Important backward-compatibility
defect in the immutable, untriggered initial Stage A commit
`56091d107382abfe9f06df1aa4cd003d71be7b5e`: resolver `ENOENT` must preserve
public `process_failed/provider_spawn`, add finite detail `binary_missing`, and
leave `provider_returncode` null. The current exact-one-shipping-commit clause
conflicts with the repository's no-amend review-fix rule.

The user selected the recommended append-only boundary. Preserve the first
candidate commit and authorize exactly one additive compatibility-fix commit.
This correction changes authority metadata only. It neither implements the
resolver fix nor claims that Opus transport is restored.

## Corrected History Contract

The only authorized Stage A topology is:

```text
R   40fd0a5e43c6b28330ced9ddffe01483cde42b65
└─ M0  56091d107382abfe9f06df1aa4cd003d71be7b5e
   └─ F   exactly one additive resolver compatibility-fix commit
      └─ D   descriptor-only commit
         └─ T   canonical verify-request-only commit
```

- `M0` is immutable. No amend, rebase, reset, rewrite, replacement, merge,
  cherry-pick, or rebuild is authorized.
- `parent(F)` must equal `M0`. The `M0..F` diff may touch only
  `scripts/opus_review_bridge.py` and
  `tests/unit/test_opus_review_bridge.py`.
- The reviewed descriptor range is `R..F`. Its aggregate changed-path set must
  remain exactly:
  - `scripts/opus_review_bridge.py`
  - `scripts/opus_review_receipts.py`
  - `tests/unit/test_opus_review_bridge.py`
  - `tests/unit/test_opus_review_receipts.py`
- Descriptor `b8c59c86-2426-46cf-8975-7b075d75fc09` keeps reviewed base `R`
  and binds reviewed head `F`. Its verification commands remain the two
  trusted-Python commands fixed by the prior coordinator correction.
- Current-main commits after `R`, including this correction, remain outside
  `R..F`. Do not fast-forward, merge, or cherry-pick them into the Stage A
  branch before Lane V. Operator2 reads this correction separately; it is not
  a descriptor requirement.
- This is a bounded one-off bootstrap correction. It does not attach or claim
  enforcement of the generalized `candidate_policy` design, whose validator
  is not implemented yet.

All other Stage A constraints remain binding: exact four-path aggregate scope,
zero provider attempts, immutable terminal receipt, no retry or fallback,
provider-free tests, independent spec and code-quality review after `F`, one
descriptor-only commit, and one canonical verify-request-only commit.

## Corrected Seat Routes

Director2:

- Packet `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics`
  remains active.
- Resume the clean isolated branch at immutable `M0`. Add the resolver-ENOENT
  regression first, then exactly one fix commit `F` restoring:

```text
unavailable_reason = process_failed
failure_stage       = provider_spawn
failure_detail      = binary_missing
provider_returncode = null
```

- Re-run the complete provider-free gate, independent spec review, and
  code-quality review against `R..F`. Only after both reviews pass, commit
  descriptor `D` and canonical request `T`.
- Provider process attempts authorized: 0. Stop after `T` with Operator2 as
  next owner.

Operator2:

- Packet `operator2-pipeline-opus-transport-first-recovery-stage-a-lanev`
  remains blocked until `T` resolves provider-free to descriptor
  `b8c59c86-2426-46cf-8975-7b075d75fc09`, base `R`, and head `F`.
- Verify the strict linear topology, both exact path sets, the complete plan
  abuse matrix, provider-free evidence, receipt immutability, and the corrected
  public compatibility mapping. Return exactly one GO, NITS, or FAIL for
  Stage A diagnostics only.

Director and Operator remain excepted. The coordinator join remains blocked on
Operator2. A Stage A GO proves diagnostics only and authorizes neither a live
provider attempt nor Stage B by itself.

Join condition: Operator2 returns one canonical Stage A GO, NITS, or FAIL for
the corrected descriptor/request; until then the coordinator join remains
blocked.

## Capacity Split Default

Reject dual-pair routing. Chunk A would own the compatibility fix while Chunk B
would require the same bridge boundary and descriptor range, so they are not
independently reviewable. Keep the single-pair fast path: Director2 implements
and Operator2 verifies; Pair A remains excepted.

## Subagent Utilization

Two bounded read-only helpers were already available from the interrupted
coordinator turn. The Stage A helper independently confirmed the append-only
topology and exact five-path coordinator correction. The integration helper
confirmed the older receipt-integration cycle is already closed, preventing
an accidental reopen. Neither helper edited files, consumed mail, issued a
verdict, invoked a provider, mutated receipts, merged, or pushed. The
coordinator retains the routing decision.

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

- side_effect_id: pipeline-opus-transport-first-stage-a-history-contract-correction-2026-07-15
- executor: coordinator
- target: the Stage A plan, the Director2 packet, the Operator2 packet, the coordinator-join packet, and this one coordinator-to-all correction route in one exact-path local metadata commit
- allowed_command_class: apply_patch, read-only local validation, scoped temporary-index staging, route mutation, and one local coordinator metadata commit
- preflight: the user selected option 1; HEAD is ab4cc556965682c7f4cbf01b8599d9d31c4ceeb6; coordinator unread is zero; Wave 2 is MET; capacity is valid; smoke passes; locks and shared index are empty; target paths have no peer WIP; the isolated Stage A branch is clean at immutable M0 with parent R and the exact four-path aggregate diff; the terminal receipt hash is a4ea49a79fd6a5e95fe89626d3a3305fcdb31b4a6a9709514ce8a7c8b2263a25
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if HEAD moves, newer relevant mail lands, a target path gains peer WIP, a lock/shared-index/Git-operation entry appears, packet state changes, the isolated branch moves, the terminal receipt changes, or plan consistency, JSON parsing, capacity, route validation, Protocol Doctor, smoke, exact-scope, secrecy, or diff checks fail
- postcheck: the committed scope is exactly the plan, three packet files, and this route; capacity and corrected-route validation, Protocol Doctor, smoke, JSON parsing, exact-scope, and diff checks pass; production code, receipts, runtime state, refs, worktrees, shared root WIP, and remote state remain unchanged
- observer_seats: director, director2, operator, operator2, coordinator2
- final_closeout_owner: coordinator
- non_goals: no production/test/descriptor change, generalized candidate-policy implementation, provider call, retry, fallback, canary, receipt/runtime mutation, credential or browser action, cursor consume, lock action, merge, cherry-pick, push, remote publication, branch/worktree cleanup, unrelated cleanup, pod action, or production generation

## Validation Evidence

- The isolated branch is clean at `M0`; `parent(M0) = R`; `R..M0` changes
  exactly the four authorized implementation/test paths.
- The terminal receipt remains byte-identical at SHA-256
  `a4ea49a79fd6a5e95fe89626d3a3305fcdb31b4a6a9709514ce8a7c8b2263a25`.
- Capacity remains valid; corrected-route validation reports `route valid: true`
  with no blocking issues; Protocol Doctor passes 436 protocol tests plus
  smoke; all three packet files parse as JSON; the focused capacity suite is
  28/28; exact five-path staged scope and diff checks remain mandatory before
  commit.

## Exact Next Trigger

Run `coordination/bin/codex-seat director2 -- "continue as director2"`.
Director2 appends exactly one resolver compatibility-fix commit to immutable
`56091d107382abfe9f06df1aa4cd003d71be7b5e`, re-runs independent spec and
quality review, then publishes descriptor/request authority for Operator2.

No Claude or Opus process, receipt mutation, merge, or push is authorized.
