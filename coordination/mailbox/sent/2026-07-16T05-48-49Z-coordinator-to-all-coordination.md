# Coordinator → All: Release Sequential Shared Root to Director2 for ROOT-COMPACT

**When:** 2026-07-16T05:48:49Z · **From:** coordinator (online)

Event type: coordination
Disposition: ROOT_COMPACT_RELEASED_TO_DIRECTOR2_AFTER_HOLD_CLEAR
Task-board: pipeline-recovery-owner-wip-disposition-2026-07-16
Protocol wave: 2
Route base before commit: `96aa0b2e2885d85501fc4fd8e8ffd452710e3b4a`
Plan: `docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md`
User-principal authority: the explicit 2026-07-16 instruction to refresh `ed67467`, confirm the `ROOT-CHATGPT` paths are clear, and release the sequential shared root to Director2 for `ROOT-COMPACT`, followed by the explicit coordinator continuation command.
Continues: the owner assignments and bridge lifecycle in `coordination/mailbox/sent/2026-07-16T04-35-22Z-coordinator-to-all-coordination.md`.
Supersedes: only the shared-root hold in `coordination/mailbox/sent/2026-07-16T04-59-40Z-coordinator-to-all-coordination.md`; every frozen-ChatGPT firewall, Opus-bridge separation, owner assignment, and unrelated blocker remains binding.

## Findings First

- Current shared-root `main` is `96aa0b2e2885d85501fc4fd8e8ffd452710e3b4a`. The post-hold commit changes only `.claude/agents/readiness-bridge.md` and does not overlap either recovery unit.
- All sixteen paths bound by `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md` are clean in shared-root `main`, and `ed6746725501bb86dd44426e6bc1090f15eb5702..HEAD` changes none of them.
- The former seven-path peer write set is no longer present in shared-root `main`. Its exact bytes are durably preserved in clean owner-controlled worktree `.worktrees/chatgpt-pro-claude-surface-wip-2026-07-16` on branch `codex/chatgpt-pro-claude-surface-wip-2026-07-16` at `233ef8126bc75dc6a2a13adcb70810b619faa85c`, whose parent is current `main`. That commit changes exactly the seven held paths, and its `tests/unit/test_protocol_prompt_sync.py` blob is the held working blob `21e6777bf4df509f8b7be47e910ceb37a8978d34`.
- No mailbox event is newer than the hold, the shared index is empty, and no protocol lock exists. No unclassified peer WIP remains on the compact checkout.
- The remaining classified `ROOT-COMPACT` bytes are tracked `ARCHITECTURE.md` at working blob `f790828b5492f3284a9933a1c6c16e401eb6a433` plus the untracked entries under `logs/capability-first/`. Ambient `.agents/`, `.codex/runtime/`, `ORIGINAL_REQUEST.md`, and `PROJECT.md` artifacts remain excluded.
- `codex/recovery-compact-root-wip-2026-07-16` and `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md` are absent, so no live target is already satisfied.
- Task 3 is stale before execution. Four clean paths still equal checkpoint `1306c157ac434389444e77935d24db8b3189ee2c`: `governance.toml` at `da0d444ceef156c577636b2bc7d0fc168cff66bd`, `scripts/target_binding.py` at `bc8a1a210e1b56d197282c61b6bb5d679368c55b`, `tests/unit/test_target_binding.py` at `0fba3865772e8905eec9c795baee86aea6cb842a`, and `tests/fixtures/compact_kernel/v1_misuse_vectors.json` at `2ed1c69a4700edd9e87f18b436f36f0573917a56`.
- Three clean paths have advanced in contained `main` history and must not be re-preserved as dirty WIP: `scripts/compact_state_mapping.py` is `ff9118cbc509ae1a3e5a5f15816f907316f06218` through `484b16a27f45eb6f4b973894499ea1e5edf704c4`; `tests/fixtures/compact_state_mapping/v1.json` is `65e3bf1ec847c3b556f752198c00ba7647fd3a34` through `be1488a41b6174b4503fb23f8885794fa37528fc`; and `tests/unit/test_compact_state_mapping.py` is `f9905658de63cce75f51a57414f5c211abdac665` through `7151cee977693bcdf0dda262d68bd9e0253f7aa2`.

## Exclusive Release And Ordered Authority

Director2 exclusively owns the shared root for this release from the commit containing this event until the compact preservation branch and owner handoff are complete. Director, Operator, Operator2, coordinator helpers, and the active Opus bridge must not write, switch, stage, commit, clean, or otherwise mutate the shared-root checkout during that interval.

Director2 must execute these phases in order:

1. On `main`, edit only `docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md` and commit only that path with subject `docs(recovery): correct compact root checkpoint`. The correction must replace Task 3's seven checkpoint-equality claim with the four exact checkpoint matches and three exact contained-history advances above; classify all seven clean code, fixture, and test paths as comparison evidence rather than preservation-commit paths; define the preservation write set as only the live dirty `ARCHITECTURE.md` and `logs/capability-first/` bytes; and update its staging, expected diff, clean-root proof, and owner-handoff requirements consistently.
2. Before any branch switch, refresh HEAD, newest mailbox bodies, locks, shared index, all sixteen frozen ChatGPT paths, the former seven peer paths, the compact branch and handoff, `ARCHITECTURE.md` working blob, the `logs/capability-first/` untracked set, capacity, route validation, Protocol Doctor, Wave 2, and smoke. Stop if any binding input differs or if any unclassified peer WIP appears.
3. Only after the plan-only commit and successful refresh, create `codex/recovery-compact-root-wip-2026-07-16` from that post-plan `main` while preserving the live dirty bytes. Stage only `ARCHITECTURE.md` and the then-bound untracked `logs/capability-first/` entries; prove the staged set contains no clean compact code, fixture, or test path and no ambient artifact; run the focused compact tests and smoke; then commit subject `chore(recovery): preserve compact root WIP` and capture the exact diff and blob manifest.
4. Return the shared root to `main` without reset, restore, stash, clean, history rewrite, or silent absorption. Prove the compact targets are clean because their dirty bytes remain reachable from the preservation branch.
5. Create `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md` on `main` and commit only that path with subject `docs(recovery): hand off compact root WIP`. The handoff must bind the post-plan source base, preservation head, exact preserved paths and blobs, the four checkpoint matches, the three contained-history advances, the composite `ARCHITECTURE.md` disposition, evidence-only log disposition, and the plan's next lawful trigger.
No activation, merge, push, or cleanup authority is granted.
6. Return to coordinator after the handoff commit. This preservation-only release creates no Operator or Operator2 verification trigger and grants no integration authority.

## Frozen ChatGPT Approval Firewall

`3dcff96948003d510451266b017895b42bd73c2e` remains preservation-only. It must not enter design review, implementation review, independent review, Lane V, integration, merge, publication, or push until the user-principal separately and explicitly approves both a dedicated design and a `superpowers:writing-plans`-compliant implementation plan. Neither this release nor the compact plan correction satisfies that gate.

## Authority And Prohibitions

No provider or browser send, retry, credential entry, receipt/runtime mutation, cursor consume, lock action, paid spend, pod action, production generation, merge, integration, push, remote-ref update, publication, deployment, cleanup, or change to the Opus bridge lifecycle is authorized. No subagent may write the shared root, send mailbox events, issue a verdict, consume a cursor, claim a lock, push, or invoke a provider. The active Opus bridge remains advisory and separate from all five live seats.

## Capacity Split Default

The single-pair fast path applies because the compact unit is one sequential shared-root write set. Pair A may perform bounded planning or preflight only and may not touch the shared root. Coordinator owns convergence, conflict handling, and final closeout.

## Subagent Utilization

Two bounded read-only helpers independently checked hold clearance and compact-plan readiness. Their evidence informed this coordinator synthesis.
No helper made an edit, mailbox write, cursor change, verdict, lock action, provider call, ref mutation, branch switch, commit, push, or other side effect, and no helper received route or seat authority.

## Capacity Packet Coverage

All 133 current Wave-2 packet IDs are named:

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
- coord-unit-coherence-side-effect-token-join
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
- director-unit-coherence-side-effect-token-impl
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
- director2-unit-coherence-observer-standby
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
- operator-unit-coherence-side-effect-token-verification
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
- operator2-unit-coherence-observer-standby

## Side-Effect Executor Token

- side_effect_id: recovery-root-compact-release-2026-07-16
- executor: director2
- target: shared-root `main`, `docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md`, local branch `codex/recovery-compact-root-wip-2026-07-16`, `ARCHITECTURE.md`, `logs/capability-first/`, and `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md`
- allowed_command_class: fresh read-only HEAD/mailbox/capacity/protocol/lock/index/path checks; `apply_patch` for the exact plan correction and exact handoff; exact-path local staging and commits; one local branch creation and the necessary local branch switches; focused compact tests and smoke; exact postchecks
- preflight: HEAD is the commit containing this one coordinator event with parent `96aa0b2e2885d85501fc4fd8e8ffd452710e3b4a`; the event is the newest mailbox body; shared-root branch is `main`; the shared index and locks are empty; all sixteen frozen ChatGPT paths and the former seven peer paths are clear; `233ef8126bc75dc6a2a13adcb70810b619faa85c` cleanly preserves the held seven-path bytes; compact branch and handoff are absent; only the classified compact and excluded ambient WIP remains; capacity, this route, Protocol Doctor, Wave 2, and smoke pass
- stop_if_newer_mail_or_live_target_satisfied: stop before each stage or branch switch if HEAD, newest mailbox body, event parent or exact diff, any frozen or peer path, owner worktree cleanliness, lock, shared index, current branch, plan content, compact working bytes, log set, compact branch or handoff presence, capacity state, route validity, Protocol Doctor, Wave 2, or smoke changes; stop if another actor has already satisfied the target
- postcheck: prove the plan-only commit changes only the plan; prove the preservation commit changes only live `ARCHITECTURE.md` and `logs/capability-first/` bytes; prove the shared root returns to `main` clean on all compact targets; prove the handoff-only commit changes only the handoff; bind full commit and blob IDs; rerun capacity, route validation, Protocol Doctor, Wave 2, smoke, mailbox, lock, index, and excluded-WIP checks
- observer_seats: director, operator, operator2, coordinator2
- final_closeout_owner: coordinator
- non_goals: no frozen ChatGPT review or integration, no clean compact code/fixture/test re-preservation, no Opus-bridge integration or lifecycle change, no destructive working-tree command, no provider action, no verdict, no lock or cursor action, no merge, no push or remote-ref update, no publication, no cleanup

Join condition: Director2 has committed the corrected Task 3 plan on `main`, preserved exactly the live compact dirty bytes on `codex/recovery-compact-root-wip-2026-07-16`, returned shared-root `main` clean on the compact targets, committed the exact owner handoff on `main`, and coordinator has refreshed the resulting evidence without any forbidden side effect or frozen-ChatGPT authority expansion.

## Exact Next Trigger

Run `coordination/bin/codex-seat director2 -- "continue as director2"`. Director2 must refresh this committed route and execute the plan-only correction first; it may create or switch to the compact preservation branch only after the required post-plan hot-tree checks pass.

Cursor at send: 0
