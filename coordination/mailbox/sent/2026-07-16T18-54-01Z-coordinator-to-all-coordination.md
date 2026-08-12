# Coordinator → All: Replace invalid compact Phase 3 alignment route

**When:** 2026-07-16T18:54:01Z · **From:** coordinator (online)

Event type: coordination
Disposition: `COMPACT_PHASE3_ALIGNMENT_ROUTE_REPLACED`
Task-board: `compact-phase3-corpus-live-alignment-2026-07-17`
Protocol wave: 2
Route parent: `3f3342f9864bf6eea318dd43d93c70a753059dfe`
Supersedes: `coordination/mailbox/sent/2026-07-16T18-44-15Z-coordinator-to-director-coordination.md` at `3f3342f9864bf6eea318dd43d93c70a753059dfe`
Plan: `docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md`
Constraint source: `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

## Decision

The superseded coordinator-to-director baton failed the Wave-2 route validator and grants no execution authority. This coordinator-to-all task-board route is the sole active Phase 3 alignment authority.

Director is the only implementation writer. The defect is only the committed corpus/live-proof mismatch: `ambiguous_effect_outcome_retry` is still listed in `deferred_phase3_misuse_ids` although the live marker-effect path already reserves before one attempt, reconciles an observed marker, and refuses an uncertain retry. The compact reducer must not be presented as an external-effect executor.

Checked RED at the route parent:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -c 'import json,subprocess,sys; report=json.loads(subprocess.check_output([sys.executable,"scripts/capability_v1_adapter.py","--check-corpus","tests/fixtures/compact_kernel/v1_to_v2_replay.json"], text=True)); deferred=report["deferred_phase3_misuse_ids"]; print("PHASE3 GATE — FAIL: deferred misuse cases remain: " + ", ".join(deferred) if deferred else "PHASE3 GATE — PASS: no deferred misuse cases"); raise SystemExit(1 if deferred else 0)'
```

Observed: `PHASE3 GATE — FAIL: deferred misuse cases remain: ambiguous_effect_outcome_retry` with exit `1`.

## Capacity Split Default

This is the single-pair fast path: Director alone owns every implementation write. Pair B performs bounded planning or preflight only:

- Director2 traces whether the five-path boundary can honestly bind the corpus case to existing live enforcement.
- Operator2 checks that the RED gate and named no-retry tests are non-vacuous and identifies any dishonest green mutation.
- Operator remains blocked. It activates only for a behavior-changing committed diff with lawful trigger authority.
- Coordinator owns only packet reconciliation and the final join.

Subagent utilization: direct. This one route and its packet topology are tightly coupled coordinator authority work.

## Active packet assignments

- `director-compact-phase3-alignment-implementation`: ready; sole writer.
- `director2-compact-phase3-alignment-live-boundary-preflight`: ready; read-only live-boundary question.
- `operator2-compact-phase3-alignment-red-gate-preflight`: ready; read-only RED/non-vacuity question.
- `operator-compact-phase3-alignment-lanev`: blocked on the three preceding packets and activated only when behavior changes.
- `coord-compact-phase3-alignment-join`: blocked until every required disposition is durable.

## Narrow writer boundary

Director may modify only:

- `tests/fixtures/compact_kernel/v1_to_v2_replay.json`
- `scripts/capability_v1_adapter.py`
- `tests/unit/test_capability_v1_adapter.py`
- `tests/unit/test_capability_baseline_runtime.py`
- `logs/capability-first/phase2b-shadow-parity.json` only when canonical regeneration requires it

Do not modify `scripts/capability_baseline_runtime.py`, `scripts/capability_reducer.py`, the misuse-vector invariant text, provider surfaces, evidence-ledger, task-board files, locks, cursors, or peer worktrees. If honest alignment needs another source path or a new effect state/API/store/framework, stop with one blocker.

## Acceptance

1. Preserve a checked-in focused RED before the smallest GREEN change.
2. Bind the misuse ID to existing live no-retry enforcement without copying that enforcement or claiming reducer coverage.
3. The exact gate above prints PASS and exits `0`.
4. Run:
   ```bash
   env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_baseline_runtime.py -k 'marker_effect or run_one_seals_timeout_as_uncertain' -q
   env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_reducer.py tests/unit/test_capability_v1_adapter.py tests/unit/test_target_binding.py -q
   env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
   env -u GIT_INDEX_FILE git diff --check
   ```
5. Keep epoch `0` and writer `v1` unchanged.
6. Director commits one smallest local change or one blocker. A behavior-changing diff gets exactly one cold non-author-model Operator verdict; a corpus/test/proof-only diff records a verification-not-needed reason and does not create a Lane V cycle.

## Capacity packet coverage

Every Wave-2 packet ID present at route validation is named:
- coord-chatgpt-local-reprepare-task1-join
- coord-compact-phase3-alignment-join
- coord-control-plane-authority-foundation-join
- coord-execution-strength-broader-join
- coord-governance-hardening-bridge-join
- coord-ledger-phase2-detail-integration-join
- coord-ledger-phase2-task21-join
- coord-ledger-phase2-task21-route
- coord-ledger-phase2-task22-join
- coord-ledger-phase2-task23-join
- coord-ledger-phase2-task24-join
- coord-ledger-phase2-task25-26-join
- coord-ledger-ppl-recommendation-evaluation-join
- coord-ledger-runway-stage0-join
- coord-ledger-runway-stage0-route
- coord-ledger-t14-align-join
- coord-ledger-t14-align-route
- coord-ledger-workbook-refresh-join
- coord-pipeline-level5-opus-coordinator-e2e-executor-join
- coord-pipeline-level5-opus-existing-session-join
- coord-pipeline-level5-opus-manual-approval-e2e-executor-join
- coord-pipeline-level5-opus-receipt-corrective-join
- coord-pipeline-level5-opus-receipt-integration-join
- coord-pipeline-level5-opus-user-approved-join
- coord-pipeline-level5-wave0-join
- coord-pipeline-opus-transport-first-recovery-stage-a-join
- coord-provider-tools-decommission-join
- coord-unit-coherence-side-effect-token-join
- director-chatgpt-local-reprepare-task1-candidate
- director-compact-phase3-alignment-implementation
- director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix
- director-control-plane-authority-foundation-task2-race-fix
- director-control-plane-authority-foundation-task2-replacement
- director-control-plane-authority-foundation-task2-spec-review-fix
- director-control-plane-authority-foundation-task2u-fail-closed-closure
- director-control-plane-authority-foundation-tasks1-2
- director-execution-strength-broader-impl
- director-governance-hardening-bridge-impl
- director-ledger-phase2-detail-integration
- director-ledger-phase2-task21-write-path
- director-ledger-phase2-task22-validations
- director-ledger-phase2-task23-result-history
- director-ledger-phase2-task24-ios-slot-entry
- director-ledger-phase2-task25a-result-entry
- director-ledger-ppl-recommendation-evaluation-implementation
- director-ledger-publication-decision
- director-ledger-runway-stage0-owner-gates
- director-ledger-workbook-refresh-implementation
- director-pipeline-level5-opus-coordinator-e2e-standby
- director-pipeline-level5-opus-existing-session-standby
- director-pipeline-level5-opus-manual-approval-e2e-standby
- director-pipeline-level5-opus-receipt-corrective-standby
- director-pipeline-level5-opus-receipt-integration-standby
- director-pipeline-level5-opus-user-approved-standby
- director-pipeline-level5-wave0-p0-containment
- director-pipeline-opus-transport-first-recovery-stage-a-standby
- director-provider-tools-decommission-implementation
- director-unit-coherence-side-effect-token-impl
- director2-chatgpt-local-reprepare-task1-preflight
- director2-compact-phase3-alignment-live-boundary-preflight
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
- director2-execution-strength-broader-observer
- director2-governance-hardening-bridge-observer
- director2-ledger-next-brief
- director2-ledger-phase2-bounds-plan-sync
- director2-ledger-phase2-detail-integration-preflight
- director2-ledger-phase2-task22-observer
- director2-ledger-phase2-task23-observer
- director2-ledger-phase2-task24-observer
- director2-ledger-phase2-task24-planning-preflight
- director2-ledger-phase2-task26a-history-component
- director2-ledger-ppl-recommendation-evaluation-preflight
- director2-ledger-runway-plan-reconcile
- director2-ledger-workbook-refresh-contract-correction-preflight
- director2-ledger-workbook-refresh-preflight
- director2-pipeline-level5-opus-coordinator-e2e-standby
- director2-pipeline-level5-opus-existing-session-transport
- director2-pipeline-level5-opus-manual-approval-e2e-standby
- director2-pipeline-level5-opus-receipt-corrective-implementation
- director2-pipeline-level5-opus-receipt-integration-implementation
- director2-pipeline-level5-opus-user-approved-transport
- director2-pipeline-level5-wave0-opus-finalization
- director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics
- director2-provider-tools-decommission-implementation
- director2-unit-coherence-observer-standby
- operator-chatgpt-local-reprepare-task1-lanev
- operator-compact-phase3-alignment-lanev
- operator-control-plane-authority-foundation-lanev
- operator-control-plane-authority-foundation-replacement-lanev
- operator-control-plane-authority-foundation-task2u-cumulative-lanev
- operator-execution-strength-broader-verification
- operator-governance-hardening-bridge-lanev
- operator-ledger-phase2-detail-integration-lanev
- operator-ledger-phase2-task21-lanev
- operator-ledger-phase2-task22-lanev
- operator-ledger-phase2-task23-lanev
- operator-ledger-phase2-task24-lanev
- operator-ledger-phase2-task25a-lanev
- operator-ledger-ppl-recommendation-evaluation-lanev
- operator-ledger-runway-stage0-verify
- operator-ledger-workbook-refresh-lanev
- operator-pipeline-level5-opus-coordinator-e2e-standby
- operator-pipeline-level5-opus-existing-session-standby
- operator-pipeline-level5-opus-manual-approval-e2e-standby
- operator-pipeline-level5-opus-receipt-corrective-standby
- operator-pipeline-level5-opus-receipt-integration-standby
- operator-pipeline-level5-opus-user-approved-standby
- operator-pipeline-level5-wave0-p0-containment-lanev
- operator-pipeline-opus-transport-first-recovery-stage-a-standby
- operator-pipeline-tooling-verify
- operator-provider-tools-decommission-lanev
- operator-unit-coherence-side-effect-token-verification
- operator2-chatgpt-local-reprepare-task1-preflight
- operator2-compact-phase3-alignment-red-gate-preflight
- operator2-control-plane-authority-foundation-activation-repreflight
- operator2-control-plane-authority-foundation-cutover-preflight
- operator2-execution-strength-broader-observer
- operator2-governance-hardening-bridge-observer
- operator2-ledger-main-verify
- operator2-ledger-phase2-base-preflight
- operator2-ledger-phase2-detail-integration-preflight
- operator2-ledger-phase2-task22-observer
- operator2-ledger-phase2-task23-observer
- operator2-ledger-phase2-task24-observer
- operator2-ledger-phase2-task24-preflight
- operator2-ledger-phase2-task26a-lanev
- operator2-ledger-ppl-recommendation-evaluation-preflight
- operator2-ledger-runway-worktree-verify
- operator2-ledger-workbook-refresh-preflight
- operator2-pipeline-level5-opus-coordinator-e2e-lanev
- operator2-pipeline-level5-opus-existing-session-lanev
- operator2-pipeline-level5-opus-manual-approval-e2e-lanev
- operator2-pipeline-level5-opus-receipt-corrective-lanev
- operator2-pipeline-level5-opus-receipt-integration-lanev
- operator2-pipeline-level5-opus-user-approved-lanev
- operator2-pipeline-level5-wave0-opus-final-lanev
- operator2-pipeline-opus-transport-first-recovery-stage-a-lanev
- operator2-provider-tools-decommission-quality-preflight
- operator2-unit-coherence-observer-standby

## Side-Effect Executor Token

- side_effect_id: `compact-phase3-route-replacement-2026-07-17`
- executor: `coordinator`
- target: five `2026-07-17-compact-phase3-alignment-*.json` capacity packet files and this coordinator-to-all route mutation
- allowed_command_class: fresh read-only git, mailbox, capacity, plan, and validator checks; apply_patch for the five packet files; one coordination/bin/send-event route mutation; exact-path staging and one local metadata commit; capacity, route, doctor, coordination, smoke, and diff postchecks
- preflight: HEAD equals `3f3342f9864bf6eea318dd43d93c70a753059dfe`; tracked tree is unchanged; no newer Phase 3 replacement route exists; the RED command exits `1`; the five new packet identities are absent before this mutation
- stop_if_newer_mail_or_live_target_satisfied: stop before mutation on HEAD, mailbox, packet, scope, or RED drift, a newer replacement route, an already-green target, overlapping tracked WIP, or need for a production change outside the five-path writer boundary
- postcheck: one six-path metadata commit contains exactly five valid packet files and one validator-clean coordinator-to-all route; the old route remains historical and superseded; capacity, doctor, coordination, smoke, and diff checks pass
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no production edit by coordinator, second implementation writer, provider or evidence-ledger work, packet cleanup, cursor change, lock action, remote update, merge, deployment, publication, or ambient-WIP mutation

Join condition: Director2 and Operator2 return their two distinct bounded preflights; Director alone lands the smallest scoped commit or blocker; for a behavior-changing diff Director creates one lawful trigger and Operator alone returns GO/NITS/FAIL, otherwise Coordinator records verification-not-needed and excepts the unopened Operator packet; Coordinator then closes the five-packet cycle from fresh validator and smoke evidence.

## Exact Next Trigger

Director, Director2, and Operator2 each start only their named ready packet from the commit containing this route. Operator remains blocked until all three dependencies are terminal and lawful trigger authority exists. Coordinator waits for those durable results and performs no implementation work.

No remote action is authorized.

Cursor at send: 0
