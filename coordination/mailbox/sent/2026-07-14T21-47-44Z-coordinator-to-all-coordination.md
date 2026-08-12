# Coordinator -> All: return unbound-candidate cleanup defect

**When:** 2026-07-14T21:47:44Z · **From:** coordinator (online)

Event type: coordination
Disposition: PIPELINE_LEVEL5_OPUS_UNBOUND_CANDIDATE_CORRECTION_ACTIVE
Task-board: pipeline-level5-opus-receipt-corrective-2026-07-15
Protocol wave: 2
Route base before commit: d42f7282ef975ead173c8d8ea97580afa67ce3a2
Supersedes: coordination/mailbox/sent/2026-07-14T16-08-52Z-coordinator-to-all-coordination.md
Binding report: coordination/mailbox/sent/2026-07-14T20-09-29Z-operator2-to-all-verification-report.md
Coordinator mailbox at preflight: 0 unread / all-scope; no consume

## Findings First

Operator2 returned binding FAIL for reviewed head
63062315a738be1a7f3ff62f0388dc957339ad0c. The focused suite, smoke,
schema gate, and protocol doctor passed, and the report independently confirmed
the five originally routed closures. One IMPORTANT resource-ownership defect
remains in scripts/verification_report_gate.py:

- When an older Codex receipt or non-Codex task is already publishing, a fresh
  publication attempt fails before owning its new candidate but still sets the
  preserve-unowned guard. The exact stored recovery witness survives, as it
  must, but the distinct fresh unowned candidate also survives. Repeated failed
  attempts can therefore accumulate untracked mailbox candidates.

The failed cross-model attempt is explicit degraded evidence only:
process_failed, no model identity, and zero findings. Receipt
opr1:8f300fc15c890616befae00a24b9424982aec45ba1b552514dc8d67eb3e64c29,
descriptor 256b36e2-2fe4-43e8-b2e3-0a99a07e6229, reviewed head 63062315,
verify-request 93c504bf, and every earlier attempt identity are terminal. Do
not retry, reset, replay, overwrite, or reuse them.

## Coordinator Decision

Keep the existing corrective cycle and packet identities:

- director2-pipeline-level5-opus-receipt-corrective-implementation stays
  active but is narrowed to scripts/verification_report_gate.py, its focused
  regression file, fresh descriptor
  coordination/verification/scopes/30f5c1d6-6da7-4d19-a70f-1ed1a2c103f9.json,
  and one later canonical verify-request.
- operator2-pipeline-level5-opus-receipt-corrective-lanev stays blocked until
  that lawful trigger, then independently returns one GO, NITS, or FAIL.
- coord-pipeline-level5-opus-receipt-corrective-join remains blocked on the
  Operator2 verdict.
- Pair A remains excepted and observer-only. No new cycle, duplicate packet
  pair, lock, provider attempt, or production integration is opened here.

Director2 creates a fresh isolated worktree and branch directly at immutable
failed reviewed head 63062315a738be1a7f3ff62f0388dc957339ad0c. The existing
corrective worktree at 93c504bf, the prior receipt-hardening worktree, all prior
branches, descriptors, reports, receipts, and runtime state remain unchanged.

## Verify-Request Authority Topology

Use a fresh verify-request-trigger descriptor, not the prior shipping trigger:

    63062315 failed reviewed head
      -> H narrow fix + regression + fresh descriptor
      -> T canonical verify-request, strictly after H

Descriptor 30f5c1d6-6da7-4d19-a70f-1ed1a2c103f9 binds exact base 63062315,
trigger_kind verify-request, the two mutable code/test paths plus itself, the
existing pre-publication cleanup design guarantee, and the content-addressed
provider-prompt authority already present at H.

H uses a fix subject but no Lane-V-Scope shipping trailer. T contains exactly
one Event type: verify-request, full Reviewed head H, full Reviewed base
63062315, and the matching Lane-V-Scope path and digest. Its acceptance text is
neutral and complete: determine whether each distinct fresh unowned candidate
is removed while the exact stored eight-field publishing witness survives for
both Codex and non-Codex paths, without deleting a substituted foreign object.
T must not expose Operator2's verdict or conclusions to the blind reviewer.
Missing or mismatched authority blocks; never fall back to a shipping trigger.

## Corrective Acceptance Boundary

- Add the strict non-vacuous regression before the fix. Capture RED or
  strict-xfail evidence against 63062315, then finish GREEN with no final xfail.
- Exercise both receipt-backed and task-backed existing-publishing branches.
  The stored recovery witness must survive; the distinct fresh candidate must
  be identity-checked and removed; a substituted foreign object must never be
  deleted.
- Audit every preserve_unowned_candidate or equivalent cleanup sibling in
  scripts/verification_report_gate.py and record mirror, defer, document, or
  exempt disposition in T.
- The reviewed diff 63062315..H contains only
  scripts/verification_report_gate.py,
  tests/unit/test_verification_report_gate.py, and descriptor
  30f5c1d6-6da7-4d19-a70f-1ed1a2c103f9.
- Run the focused RED/GREEN selectors, the full five-file regression suite,
  scripts/check_go_schema.py, scripts/check_doc_claims.py --sha-refs,
  scripts/ci_smoke.py, scripts/protocol_doctor.py --wave 2, provider-free
  structural resolution of T, and exact-range git diff --check.
- Director2 invokes no provider. Operator2 may use only one newly
  guard-authorized standing-policy attempt derived from the fresh
  descriptor/head/trigger identity, with zero retry or fallback. Provider
  unavailability never supplies the Codex verdict.

## Capacity Split Default

Reject dual-pair routing for this residual. Chunk A is the single cleanup guard
and its paired regression. A separate Chunk B would inspect or edit the same
publication state machine and would duplicate the same Lane V boundary. The
distinct bounded planning or preflight requirement is satisfied by the
coordinator's local authority-topology analysis plus one read-only
reconciliation helper. Pair A remains excepted; Director2 implements and
Operator2 verifies.

## Subagent Utilization

One bounded read-only helper inspected packet law, commit topology, descriptor
resolution, and trigger semantics. It recommended the in-place packet
transition and fresh verify-request authority because the resolver separately
content-binds the later trigger blob without merging the main-side FAIL report
into the reviewed branch. The coordinator independently verified those resolver
and test paths and retains the routing decision. No helper edit or mailbox
write occurred. No helper verdict, cursor, lock, provider call, or worktree
mutation occurred.
No helper merge, push, or spend action occurred.

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

- side_effect_id: pipeline-level5-opus-unbound-candidate-reroute-2026-07-15
- executor: coordinator
- target: narrow the three existing corrective capacity packets, publish this
  one consolidated route, and make one exact-path local coordinator commit
- allowed_command_class: apply_patch, read-only validation, exact-path local
  staging, route mutation, and one local coordinator route commit
- preflight: user explicitly continued the coordinator; HEAD
  d42f7282ef975ead173c8d8ea97580afa67ce3a2; coordinator unread zero; binding
  Operator2 FAIL body read; Wave 2 MET; capacity valid before and after packet
  narrowing; locks empty; smoke OK; unrelated user WIP identified and excluded
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if HEAD moves,
  new relevant mail lands, any of the four route/packet paths gains peer WIP, a
  newer route already satisfies the FAIL, locks appear, or
  capacity/route/doctor/smoke fails
- postcheck: committed scope contains exactly the three packet updates and this
  route; capacity and route validation, protocol doctor, smoke, and diff check
  pass; production, prior branches/worktrees, descriptors, receipts, reports,
  runtime state, and unrelated WIP remain unchanged
- observer_seats: director, operator, coordinator2
- final_closeout_owner: coordinator
- non_goals: no production fix, provider launch, receipt/runtime mutation,
  no approval-mode change, credential entry, retry, fallback, or alternate
  reviewer; no mailbox cursor write, lock/ref mutation, worktree creation,
  no merge, cherry-pick, push, external publication, cleanup, or pod action;
  no production generation

## Validation Evidence

- Pre-route scripts/protocol_capacity_board.py --wave 2: valid after the
  three-packet narrowing.
- Pre-route scripts/ci_smoke.py: project smoke OK; ceremony checks, GO schema,
  and architecture freshness passed.
- find coordination/locks -maxdepth 2 -type f -not -name .gitkeep -print:
  no lock files.
- scripts/protocol_capacity_board.py --wave 2 --validate-route <this route>:
  route valid; no blocking issues.
- scripts/protocol_doctor.py --wave 2 --route <this route>: 432 tests passed;
  PROTOCOL DOCTOR: PASS.
- Final scripts/ci_smoke.py: project smoke OK; 39 verification reports passed
  schema validation; architecture freshness passed.
- git diff --check over the exact three packet paths plus this route produced
  no output.

Join condition: Director2 lands H and T under the fresh descriptor; Operator2
returns one valid GO for 63062315..H after reproducing and closing the single
cleanup abuse case; fresh capacity, route, doctor, smoke, schema, architecture,
branch, and exact-scope evidence pass. NITS or FAIL returns only the same
bounded correction to Director2 and does not join.

Cursor at send: all-scope-unpinned

## Exact Next Trigger

Continue as director2 from
director2-pipeline-level5-opus-receipt-corrective-implementation. Create a fresh
isolated worktree and branch at
63062315a738be1a7f3ff62f0388dc957339ad0c, add the strict regression first,
fix only the unbound fresh-candidate cleanup for both publishing paths, create
fresh verify-request descriptor
30f5c1d6-6da7-4d19-a70f-1ed1a2c103f9, land H, then commit canonical trigger T
to Operator2. Do not invoke a provider, merge, cherry-pick, reuse old
identities, or publish remotely.
