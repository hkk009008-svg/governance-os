# Coordinator → All: authorize Stage A Q2 legacy output-limit compatibility correction

**When:** 2026-07-15T21:16:33Z · **From:** coordinator (online)

Cursor at send: 0
Event type: coordination
Disposition: PIPELINE_OPUS_TRANSPORT_FIRST_STAGE_A_Q2_COMPATIBILITY_AUTHORIZED
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Route base before commit: 9a50117320555de3146bd631d252be585e15e675
Plan: docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md@9a50117320555de3146bd631d252be585e15e675 blob=75b280769476bbe924ccc72477ce2544dfcbdf5a sha256=b7eb3f99fd46af1981b35192e71b536b8897dc9646b43990ea3704ab5f3cc9b1
Umbrella design: docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md@50cec4fba74fac3a7230ca3769d842e43d99045b blob=57e22851fb743d0328d8a7d3bedcb609ccbaa7e0
Supersedes only the post-Q1 topology and acceptance clauses in coordination/mailbox/sent/2026-07-15T20-20-07Z-coordinator-to-all-coordination.md@da23714ed7daf77dcf7c018bf8c547c549cea177 blob=598ff59872065090066811cd56c772fa2f7b472e.
Consumes blocker: coordination/mailbox/sent/2026-07-15T21-07-14Z-director2-to-coordinator-coordination.md@4025b4aaab3fa6aca2fb0dcda614cb422be54e1f blob=4fdcca877bf26b581822738e7ac2b345b8fc8254 sha256=a00e1e2c14cc62cdce4ead0b0bc63865b111f91cd27fff8a48dfe46d5c9fa6a3.
Coordinator mailbox at preflight: 0 unread / ref-bus; no consume.

## Findings First

Immutable Q1 is clean and structurally exact:

```text
R   40fd0a5e43c6b28330ced9ddffe01483cde42b65
└─ M0  56091d107382abfe9f06df1aa4cd003d71be7b5e
   └─ F   16c4f83aef4130d977a91d623a9254c4fd46980a
      └─ Q1  6d596b5f238fdc72f6d7384fddfd112072c52352
         └─ Q2  exactly one compatibility commit
            └─ D   descriptor-only commit
               └─ T   canonical verify-request-only commit
```

Q1 has subject `fix(opus): validate diagnostics and cleanup lifecycle`, directly parents F, and aggregate R..Q1 changes exactly the four routed implementation/test paths. Its fresh provider-free gate returned 860 passed; smoke, compile, anchors, and diff checks passed. Provider attempts and receipt mutations remained zero.

Both required post-Q1 reviews returned FAIL on the same Important legacy compatibility defect:

- Spec reviewer identity: `codex-subagent:/root/stagea_spec_review`
- Spec harness: `codex-collaboration/read-only-review/v1 (same-model, fresh-context)`
- Spec question SHA-256: `8878d209d32692e01315222a7ac73c6c66439146f14d17b22518a37055adcb3a`
- Spec result: `FAIL`
- Code-quality reviewer identity: `codex-subagent:/root/stagea_quality_review`
- Code-quality harness: `codex-collaboration/read-only-review/v1 (same-model, fresh-context)`
- Code-quality question SHA-256: `1de51976bae234ff20f5fc5d40c46c420521b571a89a8950e6736d141374d5d0`
- Code-quality result: `FAIL`

At immutable R, the legacy output-limit producer emitted null-detail/null-return-code `output_limit/provider_exit` records with the actual non-empty truncation flags. Q1 rejects all three emitted shapes and accepts the impossible false/false shape. The current route forbids a second post-Q1 implementation commit, so no descriptor, request, external authority object, or Operator2 trigger exists.

The amended plan is content-addressed above and is the only lawful correction. Receipt-store manifest before Stage A: sha256:b8facd94e2bed25f14cda80c98765e058a0248a6f69e55bf7da465687158fe2a

## Q2 Finite Correction Contract

- Preserve R, M0, F, and Q1 byte-for-byte.
- `parent(Q2) == Q1`; Q2 has fixed subject `fix(opus): restore legacy output-limit compatibility`.
- Q1..Q2 changes exactly `scripts/opus_review_bridge.py` and `tests/unit/test_opus_review_bridge.py`.
- Aggregate R..Q2 remains exactly `scripts/opus_review_bridge.py`, `scripts/opus_review_receipts.py`, `tests/unit/test_opus_review_bridge.py`, and `tests/unit/test_opus_review_receipts.py`.
- Legacy null-detail/null-return-code `output_limit/provider_exit` accepts exactly true/false, false/true, and true/true truncation. False/false rejects as `invalid_schema`.
- Every other lawful legacy null-diagnostic pair still requires false/false. All finite-detail, reason/stage, return-code, parser, receipt, and broker-lifecycle behavior from Q1 remains unchanged.
- Tests are non-vacuous in both directions and run before implementation. No Q3 is authorized.
- Two new distinct independent spec and code-quality reviews must both PASS exact R..Q2 with empty blocking findings before the coordinator-owned external authority object.
- Provider process attempts authorized: **0**.
- Receipt mutations authorized: **0**.

No real provider invocation, receipt/runtime mutation, retry, fallback, local integration, external publication, cursor consume, lock action, branch cleanup, or unrelated root-WIP edit is authorized by this route.

## Corrected Seat Routes

- Director2 owns packet `director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics`: start from clean exact Q1, add the four-way RED matrix, make the smallest validator correction, append exactly one Q2, run the complete provider-free gate, and obtain two new independent PASS reviews. Any Critical or Important finding stops with one bounded coordinator blocker; no Q3 is authorized.
- Coordinator owns only the content-addressed external authority object after both post-Q2 reviews pass. It does not author production or test changes.
- Director2 then commits descriptor-only D and request-only T. T binds reviewed head Q2 and references the external authority object exactly once; the out-of-range amended plan, umbrella, route, owner freeze, blocker, reviews, and authority object do not enter descriptor requirement_paths.
- Operator2 remains blocked on packet `operator2-pipeline-opus-transport-first-recovery-stage-a-lanev` until canonical T. It resolves the complete authority chain provider-free, verifies Q1..Q2 exactly two paths and R..Q2 exactly four paths, exercises the legacy truth table, and returns exactly one GO, NITS, or FAIL.
- Director and Operator remain excepted under `director-pipeline-opus-transport-first-recovery-stage-a-standby` and `operator-pipeline-opus-transport-first-recovery-stage-a-standby`.
- Coordinator join `coord-pipeline-opus-transport-first-recovery-stage-a-join` remains blocked on Operator2.

## Capacity Split Default

Capacity split decision: reject dual-pair routing. Chunk A is the two-path Q2 implementation owned by Director2. Chunk B would need the same validator, test matrix, immutable topology, descriptor identity, and authority chain, so it is not independently reviewable; Operator2 remains an independent verifier and Pair A remains excepted.

## Subagent Utilization

A bounded read-only fresh-context helper audited the Q2 plan, packet, route, external-authority, descriptor, request, resolver, completion, and stop-condition bindings. It found the unset reviewed-head risk, the two-path/four-path distinction, and the need to bind both the amended plan and blocker as route ancestors. The coordinator incorporated those findings but retained every route, write, and commit decision. The helper did not edit, consume mail, send events, invoke providers, issue GO, mutate receipts, integrate, or publish externally.

## Side-Effect Executor Token

- side_effect_id: `stage-a-q2-compatibility-route-2026-07-16`
- executor: `coordinator`
- target: the three exact Stage-A packet JSON files plus `coordination/mailbox/sent/2026-07-15T21-16-33Z-coordinator-to-all-coordination.md`
- allowed_command_class: one local Git commit of coordinator-owned capacity and route metadata with subject `docs(protocol): authorize Opus Stage A Q2 compatibility correction`
- preflight: re-read coordinator mailbox and blocker bodies; require main at exact route base, amended-plan commit/blob/digest match, blocker commit/blob/digest match, Stage-A worktree clean at exact Q1, capacity valid, shared index scoped, and receipt-store manifest equal to the recorded baseline
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if newer Stage-A mail changes ownership or verdict, Q1 moves, the receipt manifest changes, the shared index gains unrelated paths, or another matching Q2 route commit already exists
- postcheck: prove the commit contains exactly the three packet paths and one generated route event, then rerun capacity, route validation, coordination check, diff check, and smoke
- observer_seats: `director`, `director2`, `operator`, `operator2`
- final_closeout_owner: `coordinator`
- non_goals: no production/test edit, provider invocation, receipt mutation, descriptor, GO, local integration, external publication, cursor consume, lock action, cleanup, or target-repository mutation

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

Join condition: Operator2 returns one canonical provider-free Stage A GO, NITS, or FAIL for exact R..Q2 through lawful D and T after validating the amended plan, blocker, post-Q1 route, external authority object, two new PASS reviews, and unchanged receipt-store manifest. Until then the coordinator join remains blocked; NITS or FAIL grants no Q3.

## Exact Next Trigger

Run `coordination/bin/codex-seat director2 -- "continue as director2"`. Director2 must re-read this committed route, prove the Stage-A worktree is still clean at exact Q1=6d596b5f238fdc72f6d7384fddfd112072c52352, then implement Task 5A from `docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md` with tests first, zero provider attempts, and zero receipt mutations.
