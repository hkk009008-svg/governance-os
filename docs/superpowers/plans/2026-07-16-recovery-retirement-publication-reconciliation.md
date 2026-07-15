# Recovery Retirement And Publication Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the recovery program with evidence-bound final dispositions, truthful architecture and plan status, retained compatibility history, and separately authorized publication and cleanup actions.

**Architecture:** This plan starts only after every implementation/correction/convergence phase has its required independent verdict and compact Phase 4 has validated duration, restart, delayed/retry-horizon, reader-consistency, ten-unit, three-profile, and five-by-five observation gates. A compact coordinator route authorizes a routed Director to reconcile descriptive documentation and historical plan status; an independent Operator publishes specialized compact verification evidence plus a compact verification transition. Legacy v1 mailbox files and join packets remain immutable historical projections. The coordinator commits one final candidate handoff, then appends one compact closeout transition that content-addresses it; that event OID is terminal `done_evidence`. Remote publication and local cleanup remain later distinct user-authorized side effects.

**Tech Stack:** Git and remote-ref inspection, Markdown/JSON evidence, Python 3.14, pytest, compact current-state/capacity/doctor tooling, activation archives and observation evidence, specialized compact verification evidence, and compact event transitions.

## Global Constraints

- The source design is `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` at `426744766711d4d6057a4698f5bb19d454ad621d`.
- This is Phase 6. It must not start from plan checkboxes, branch names, smoke alone, or capacity-board status. Each substantive disposition requires current ancestry, executed component evidence, and the required canonical Operator verdict.
- Required predecessor plans are:
  - `docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md`;
  - `docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md`;
  - `docs/superpowers/plans/2026-07-16-target-aware-evidence-ledger-opus-bridge.md`;
  - `docs/superpowers/plans/2026-07-16-ppl-publication-race-correction.md`;
  - `docs/superpowers/plans/2026-07-15-pre-trigger-append-only-candidate-range.md`;
  - `docs/superpowers/plans/2026-07-15-targeted-web-research-default.md`;
  - `docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md`;
  - `docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md`;
  - `docs/superpowers/plans/2026-07-16-compact-kernel-phase4-activation.md`.
- The coordinator reconciles historical packets, handoffs, compact routes, and final state only. It does not author a production fix, mutate legacy v1 packets/mailbox files, delete a production module, reinterpret an Operator verdict, or repair a failed observation.
- Descriptive-document edits belong to a compact-routed Director and receive independent compact `operator-doc-sync` evidence/transition before coordinator closeout. If any active instruction or executable behavior must change, stop and route a separate implementation range; do not hide it in the closeout docs commit.
- Keep `route/v1` decoding and committed golden histories indefinitely in Git with no automatic expiry. A later deletion requires a new user-approved retention decision; worktree cleanup never deletes Git history.
- `capability/v1` receipt/CAS laws, packet-state mapping fixtures, and route-lineage replay histories remain committed even when their standalone live executors or selectors are retired. Compatibility artifacts never regain live authority.
- Compact retirement requires validated `logs/capability-first/phase4-compact-activation-2026-07-16/observation.json` with exactly these fields and no substitutes: `schema`, `status`, `activation_id`, `activated_head`, `activation_epoch`, `activation_ref`, `activation_object_oid`, `writer_mode`, `observed_unit_ids`, `observed_unit_profiles`, `profile_counts`, `authority_divergence_count`, `effect_eligibility_divergence_count`, `duplicate_dispatch_count`, `unresolved_effect_count`, `rollback_rehearsal_epoch`, `observation_policy_decision_path`, `observation_policy_decision_digest`, `observation_started_at`, `observation_ended_at`, `observation_duration_seconds`, `minimum_observation_duration_seconds`, `required_restart_count`, `observed_restart_count`, `restart_evidence_digest`, `restart_evidence_path`, `max_delayed_retry_horizon_seconds`, `post_restart_observation_seconds`, `delayed_retry_inventory_digest`, `delayed_retry_inventory_path`, `precutover_measurement_path`, `precutover_measurement_digest`, `postactivation_measurement_path`, `postactivation_measurement_digest`, `measurement_host_binding_digest`, `measurement_baseline_digest`, `measurement_input_digest`, `measurement_instrumentation_digest`, `reporter_commit`, and `report_digest`. Its schema is `protocol-kernel-observation/v1`; `status` is immutable `pending_operator_go` with GO supplied by the bound compact Operator evidence; writer mode is `compact`; activation epoch is `1`; chosen duration/restart policy and measured horizon are satisfied; every serving reader is consistent; at least ten observed unit IDs are unique consecutive boundary-bearing units on one event chain; `observed_unit_profiles` maps those IDs exactly once to the five canonical profiles and recomputes exactly to `profile_counts`; at least three profile counts are positive; all four counters are zero; rollback rehearsal epoch is `2`; both fixed restart and delayed/retry evidence paths resolve at their bound digests; both five-by-five measurement artifacts resolve with identical host/baseline/input/instrumentation bindings; activated-head gates are green; and the live activation/ref/archive objects agree through stable view.
- A green `ci_smoke.py`, capacity board, or doctor is structural evidence only. It cannot replace component tests, the activated-head observation artifact, or an Operator GO.
- Refresh HEAD, compact event/evidence bodies, compact capacity/current-state, historical packet projections, locks, worktrees, local branches, remote-ref state, activation/archive state, and reader consistency immediately before each closeout, publication, or cleanup decision.
- Every ordinary Git and pytest command starts with `env -u GIT_INDEX_FILE`. Use exact pathspecs and inspect staged scope before each commit.
- Commit, local integration, remote publication, provider use, activation, and cleanup remain distinct authorities. This plan invokes no provider and authorizes no retry or fallback.
- A push of only `refs/heads/main` publishes a code/docs/history mirror, not a runnable activated replica. The compact activation, event, cursor, recovery, and archive refs plus every object reachable only from them remain local protocol state. This plan never pushes those refs. Any serving clone or disaster-recovery replica requires a separate authenticated protocol-state replication/import design, exact ref/object inventory, protection policy, user authorization, and post-import stable-view validation. Until then, a fresh clone with an epoch-1 mirror but no authority refs must fail closed.
- No force push, tag rewrite, branch force-delete, activation-ref deletion/lowering, history rewrite, `git reset --hard`, or `git clean` is permitted.
- Post-activation rollback is a newer epoch only. Retirement never deletes or lowers `refs/protocol/kernel-activation`.

---

## File Structure

### Final descriptive truth range

- Modify: `ARCHITECTURE.md` — current activated writer/readers, activation authority, and retained compatibility topology.
- Modify: `OPERATIONS.md` — current validation, observation, rollback, and retained-history operations.
- Modify: `docs/PROGRAM-MANUAL.md` — current capability-maximization path without historical execution claims.
- Append: `DECISIONS.md` — one final activation/retention ADR; never edit prior ADR text.
- Modify: `docs/protocol/route-v1.md` — retained decoder/replay status and no live route authority.
- Modify: `docs/protocol/capabilities.md` — compact effect-boundary status and retained v1 law/history disposition.
- Modify: `docs/protocol/packet-state.md` — compact mapping status and standalone-module disposition.
- Modify: `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md` — evidence-backed Phase 1-4 completion and observation references.
- Modify: `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` — terminal status plus final handoff path, authored by the routed Director and covered by the independent doc-sync verdict.

### Historical plan status surfaces

- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-08-coordination-hardening-subagent-capacity.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-09-codex-agent-toml-consolidation.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-11-typed-route-authority-slice1.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-12-route-lineage-cas-slice2.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-12-consumable-capabilities-slice3.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-12-packet-state-derivation-slice4.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-13-chatgpt-pro-browser-consultation.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-14-existing-session-bridge-repair.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-14-pipeline-level5-execution.md`
- Modify when ancestry/evidence proves a terminal state: `docs/superpowers/plans/2026-07-15-capability-baseline-runtime-collector.md`
- Modify when present on `main` after the Phase-1/2 integration: `docs/superpowers/plans/2026-07-15-capability-phase1-surface-inventory-closure.md`
- Modify when present on `main` after the Phase-1/2 integration: `docs/superpowers/plans/2026-07-15-capability-compact-reducer-phase2.md`
- Modify when present on `main` after the Phase-1/2 integration: `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md`
- Modify when its Operator evidence is terminal: `docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md`
- Modify when its Operator evidence is terminal: `docs/superpowers/plans/2026-07-15-pre-trigger-append-only-candidate-range.md`
- Modify when its Operator evidence is terminal: `docs/superpowers/plans/2026-07-15-targeted-web-research-default.md`

### Coordinator closeout state

- Read only as historical v1 projections: `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-12-ledger-ppl-recommendation-evaluation-coordinator-join.json`, `coordination/capacity/packets/2026-07-14-pipeline-level5-wave0-coordinator-join.json`, and `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-coordinator-join.json`.
- Create: `docs/HANDOFF-coordinator-2026-07-16-pipeline-recovery-final-closeout.md` as a candidate that binds compact doc-sync GO evidence.
- Append through the compact writer: one final closeout transition whose content-addressed handoff/report/predecessor set is terminal `done_evidence`. No Markdown mailbox event or legacy packet mutation is created.

### Fixed predecessor evidence

- `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md`
- `docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md`
- `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md`
- `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md`
- `docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md`
- `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md`
- `docs/HANDOFF-director-2026-07-16-targeted-web-integrated.md`
- `docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md`
- `docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md`
- `docs/HANDOFF-director-2026-07-16-compact-phase3-convergence.md`
- `docs/HANDOFF-coordinator-2026-07-16-compact-phase3-integrated.md`
- `docs/HANDOFF-director-2026-07-16-compact-kernel-phase4-ready.md`
- `docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-implementation-integrated.md`
- `docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-observed.md`
- `logs/capability-first/phase1-2-integration.json`
- `logs/capability-first/phase2b-shadow-parity.json`
- `tests/fixtures/compact_kernel/control_plane_convergence.json`
- `logs/capability-first/phase3-control-plane-convergence.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/preflight.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/activation.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/finalization-result.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/delayed-retry-inventory.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/restart-evidence.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/precutover-compact-five-profile.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/postactivation-live-five-profile.json`
- `logs/capability-first/phase4-compact-activation-2026-07-16/observation.json`
- The attempt-specific observation-policy and activation-archive paths/ref plus compact verification/closeout event OIDs bound by preflight and the Phase-4 observed handoff.

### Required final disposition register

The final handoff must contain these rows with the stated terminal meaning:

| Item | Required terminal disposition |
|---|---|
| Opus Stage A | Corrected provider-free range with canonical Operator GO; no provider claim widened from diagnostics |
| Opus Stages B-D | First proven boundary corrected, at most one separately authorized canary recorded, Operator GO, and accepted integration ancestry |
| Target-aware evidence-ledger bridge | Pipeline range integrated with independent GO and immutable target-binding handoff |
| Candidate policy | One-to-five-commit validator integrated with Operator GO and v1 compatibility retained |
| Targeted web default | Instruction/test range integrated with Operator GO and no provider/side-effect authority |
| ChatGPT local-reprepare WIP | Either independently approved, verified, and integrated, or explicitly withdrawn by its owner; preservation alone is not terminal shipping status |
| Capability Phase 1 | Closure range independently accepted and integrated before Phase-2 claims |
| Capability Phase 2 | Parity/closeout independently accepted and integrated as epoch-0 non-authoritative shadow history |
| Compact Phases 3-4 | Phase-3 convergence accepted, Phase-4 reader/writer migration activated once, and ten-unit observation validated |
| PPL recommendation path | Exact evidence-ledger correction range has target-aware cumulative Operator GO; target publication remains separately dispositioned |
| Control-plane authority branch | Unsuperseded guarantees mapped into compact evidence; old join excepted as superseded and preservation branch retained |
| `route/v1` | Retained read-only decoder/replay input with no independent live authority |
| `capability/v1` | Receipt/CAS laws and histories retained; no independent live token authority |
| `packet_state.py` | Mapping laws/fixtures carried into compact coverage; standalone module absent or retained only with a named real historical-adapter caller |
| Route-lineage CAS | Historical lineage retained for v1 replay; compact activation ref is the sole writer-mode CAS |
| Level-5 unexecuted work | Unmet useful criteria mapped to accepted Opus/compact successors; duplicate waves remain excepted, not falsely completed |
| Existing-session bridge worktrees | Preserved through replacement Opus GO, then classified for separately authorized cleanup |
| ChatGPT consultation | Existing live implementation and regression coverage retained without reimplementation |
| Codex role TOMLs | Existing live role wiring and prompt-sync coverage retained without reimplementation |
| Subagent-capacity policy | Existing live behavior and regression coverage retained without reimplementation |

---

### Task 1: Prove every predecessor is eligible for final reconciliation

**Files:**

- Read: all predecessor plans and fixed evidence paths above
- Read: canonical Operator verification reports and coordinator closeout events produced by the Opus, candidate-policy, targeted-web, compact, bridge, and PPL routes
- No file mutation in this task

**Interfaces:**

- Consumes: exact merged/activated heads, Operator reports, fixed evidence files, current compact event/current-state/capacity/lock state, historical v1 projections, and target-repository PPL handoff.
- Produces: one in-memory eligibility table with no `pending`, `inferred`, or evidence-free completion row. Failure of any hard prerequisite blocks this plan before documentation or compact closeout routing; legacy packet files are never changed.

- [ ] **Step 1: Refresh current coordinator and activation state**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -12
env -u GIT_INDEX_FILE .venv/bin/python scripts/wave_gate_check.py 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
find coordination/locks -type f ! -name .gitkeep -print
env -u GIT_INDEX_FILE git worktree list --porcelain
```

Expected: compact current-state/capacity and doctor pass, locks print nothing, and worktrees are fully enumerated. Read every newer relevant compact event and specialized evidence body before accepting these results; legacy mailbox files are historical only.

- [ ] **Step 2: Prove the fixed evidence set is committed on `main`**

Run:

```bash
for item_path in \
  docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md \
  docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md \
  docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md \
  docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md \
  docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md \
  docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md \
  docs/HANDOFF-director-2026-07-16-targeted-web-integrated.md \
  docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md \
  docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md \
  docs/HANDOFF-director-2026-07-16-compact-phase3-convergence.md \
  docs/HANDOFF-coordinator-2026-07-16-compact-phase3-integrated.md \
  docs/HANDOFF-director-2026-07-16-compact-kernel-phase4-ready.md \
  docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-implementation-integrated.md \
  docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-observed.md \
  logs/capability-first/phase1-2-integration.json \
  logs/capability-first/phase2b-shadow-parity.json \
  tests/fixtures/compact_kernel/control_plane_convergence.json \
  logs/capability-first/phase3-control-plane-convergence.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/preflight.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/activation.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/finalization-result.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/delayed-retry-inventory.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/restart-evidence.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/precutover-compact-five-profile.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/postactivation-live-five-profile.json \
  logs/capability-first/phase4-compact-activation-2026-07-16/observation.json; do
  test -f "$item_path" || exit 1
  env -u GIT_INDEX_FILE git cat-file -e "HEAD:$item_path" || exit 1
  env -u GIT_INDEX_FILE git log -1 --format='%H %s' -- "$item_path"
done
```

Expected: one committed-path evidence line per literal entry and exit `0`. Then resolve the attempt-specific observation-policy path, activation archive path/ref, compact Operator evidence, and terminal Phase-4 event OID only from the committed preflight/observed handoff and validate their path/commit/blob/digest or ref/object identities. A worktree-only, legacy-packet-only, or untracked artifact is not accepted.

- [ ] **Step 3: Validate the activated observation with the committed validator**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py \
  validate-observation \
  --path logs/capability-first/phase4-compact-activation-2026-07-16/observation.json \
  --root .
```

Expected: PASS only for the exact Global-Constraints schema: immutable `status=pending_operator_go` plus the separately bound compact GO evidence; epoch `1`/writer `compact`; exact observation-policy and horizon digests; duration at least the user minimum; required restart count met; post-restart observation at least the measured maximum horizon; all readers consistent; at least ten unique consecutive units on one contiguous event chain; three positive profiles; all four counters `0`; rollback rehearsal epoch `2`; both committed same-host five-by-five artifacts with matching baseline/input/instrumentation; full reporter/activated SHAs; green activated-head gates; and live activation/ref/archive agreement. Any failure keeps retirement and publication blocked.

- [ ] **Step 4: Confirm the activation reference and activated head are current**

Run:

```bash
env -u GIT_INDEX_FILE git show-ref --verify refs/protocol/kernel-activation
env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2 --current
```

Expected: the activation ref exists, the observation validator already bound it to the current activated full head/object, and doctor reports exactly one compact writer with no mixed-writer violation. Never repair a mismatch by moving or lowering the ref here.

- [ ] **Step 5: Bind each non-fixed predecessor to one uniquely derived committed authority chain**

Use the fixed handoffs in the evidence list as roots; never choose a report by timestamp or scan all mailbox files. Resolve each handoff's exact commit/blob/digest, then follow only its explicitly content-addressed route, descriptor, report, integration authorization, merged head, and terminal event OID. Historical pre-activation v1 report paths remain valid evidence only when named by those roots. Current Phase-4/retirement authority must be a compact event/evidence OID.

For Opus, target bridge, candidate, PPL, web, Phase-1/2, and Phase-3 require the fixed integrated handoff and every bound GO/merged SHA. For Phase 4 require the implementation-integrated and observed handoffs, selected preparation attempt/archive, specialized preparation/execution GO evidence, activation intent, finalization-result receipt with actual finalizer attestation/metadata SHA, observation compact GO, and terminal event. Every reviewed/integrated head must be an ancestor of the activated/current head, with no unreviewed later relevant edit. Zero/multiple matches, branch-only state, a report selected from ambient `HEAD`, or a legacy packet that disagrees with its fixed successor is a hard stop.

- [ ] **Step 6: Validate the already-terminal ChatGPT disposition**

Read `docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md` at its exact commit/blob/digest and require terminal status `withdrawn-preserved` or `integrated-reviewed`. For withdrawal, validate the owner withdrawal handoff and prove no preserved production blob entered main. For integration, validate the dedicated plan, Operator GO, user-named integrator, exact integrated main SHA, and merged-tree tests. Retirement makes no new decision and performs no post-activation integration. A missing, preservation-only, or contradictory disposition blocks before Task 2 because changing these overlapping surfaces would invalidate activated-head observation.

- [ ] **Step 7: Verify the evidence-ledger target handoff without fabricating Pipeline Lane-V authority**

Read `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md`, extract its target root, cumulative base/head, exact path set, target Operator report, and tests. Run `scripts/ledger_start_guard.py --seat coordinator --wave 2` from Pipeline and then only the read-only target Git commands named by that handoff. Expected: target head and report match the handoff, the corrected range is accepted by the target-aware bridge, and no Pipeline descriptor is invented for the cross-repository verdict.

- [ ] **Step 8: Prove there is no unresolved recovery-target WIP**

Run:

```bash
env -u GIT_INDEX_FILE git diff --quiet
env -u GIT_INDEX_FILE git diff --cached --quiet
env -u GIT_INDEX_FILE git status --short -- \
  AGENTS.md CLAUDE.md ARCHITECTURE.md OPERATIONS.md governance.toml \
  scripts tests docs/protocol docs/superpowers/plans \
  docs/superpowers/specs coordination/capacity/packets
```

Expected: both diff commands exit `0`; the scoped status command prints nothing. Ambient owner-retained untracked roots may remain only when the owner-disposition handoff lists them exactly and this final plan never stages or removes them.

### Task 2: Reconcile descriptive truth and historical plan status

**Files:**

- Modify: every descriptive and historical status file listed under **File Structure**
- Read before editing the manual: `docs/protocol/program-manual-guide.md`
- Test: `tests/unit/test_protocol_doc_integrity.py` and existing documentation/smoke gates; do not change those tests in this docs-only task

**Interfaces:**

- Consumes: Task 1 eligibility table, activated observation, exact final Git ancestry, final call graph, and every canonical Operator report.
- Produces: one docs-only Director commit whose claims match executable truth. It changes no active prompt, production code, schema, packet, mailbox, cursor, lock, ref, or runtime state.

- [ ] **Step 1: Route one docs-only truth reconciliation**

Through the authenticated compact writer, the coordinator appends exactly one coordinator route transition at the current epoch-1 activation/event tip. It binds the exact docs base commit, descriptive/historical path allowlist above, Director principal/binding, `operator-doc-sync` verifier principal/binding, finite commands/questions, join condition, and exclusions: no production or active-prompt edits, provider, legacy packet/mailbox mutation, cleanup, publication, or Lane-V shipping descriptor. Capture the route transition event OID from the publisher result and validate it through compact current-state/capacity/doctor before the Director starts. Exact-old event CAS failure, activation drift, or a second matching route blocks; there is no legacy coordinator route commit or Markdown mailbox event.

- [ ] **Step 2: Inventory unchecked claims before editing**

Run:

```bash
rg -n '^Status:|^\*\*Status:\*\*|^- \[ \]' \
  docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md \
  docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md \
  docs/superpowers/plans/2026-07-08-coordination-hardening-subagent-capacity.md \
  docs/superpowers/plans/2026-07-09-codex-agent-toml-consolidation.md \
  docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md \
  docs/superpowers/plans/2026-07-11-typed-route-authority-slice1.md \
  docs/superpowers/plans/2026-07-12-route-lineage-cas-slice2.md \
  docs/superpowers/plans/2026-07-12-consumable-capabilities-slice3.md \
  docs/superpowers/plans/2026-07-12-packet-state-derivation-slice4.md \
  docs/superpowers/plans/2026-07-13-chatgpt-pro-browser-consultation.md \
  docs/superpowers/plans/2026-07-14-existing-session-bridge-repair.md \
  docs/superpowers/plans/2026-07-14-pipeline-level5-execution.md \
  docs/superpowers/plans/2026-07-15-capability-baseline-runtime-collector.md \
  docs/superpowers/plans/2026-07-15-capability-phase1-surface-inventory-closure.md \
  docs/superpowers/plans/2026-07-15-capability-compact-reducer-phase2.md \
  docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md \
  docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md \
  docs/superpowers/plans/2026-07-15-pre-trigger-append-only-candidate-range.md \
  docs/superpowers/plans/2026-07-15-targeted-web-research-default.md
```

Expected: a complete location inventory. Do not turn an unchecked historical task into a checked task unless the exact implementation commit, executed evidence, and required verdict prove that exact task. Superseded work stays unchecked and receives a terminal supersession note instead.

- [ ] **Step 3: Update architecture, operations, manual, and ADR truth**

Read `docs/protocol/program-manual-guide.md`, then only the manual sections it routes for architecture and operating-mode maintenance. Do not load or rewrite unrelated manual sections.

Make these exact semantic changes:

- `ARCHITECTURE.md` names the current compact writer, the activation-ref CAS as writer-mode authority, the active reducer/readers, the read-only v1 decoder path, and the current rollback rule. Every file/line anchor comes from fresh `rg -n`, not copied old line numbers.
- `OPERATIONS.md` documents the exact `kernel_activation.py validate-observation` command from Task 1, live ref/object inspection, newer-epoch rollback, retained-history validation, separate push/cleanup authorization, and the fact that a main-only remote is a non-runnable code/docs mirror until separately authorized protocol refs/objects are imported and validated.
- `docs/PROGRAM-MANUAL.md` states that the compact kernel is the current governance path only when the activated observation proves it; it preserves user-principal authority and does not treat compatibility artifacts or advisory providers as authority.
- Append one ADR to `DECISIONS.md` recording the selected compact writer, monotonic activation ref, indefinite Git retention for read-only v1 decoding/golden histories, retirement of duplicate live authority, and separate publication/cleanup consent. Do not edit earlier ADRs.

- [ ] **Step 4: Reconcile compatibility-document status**

Update:

- `docs/protocol/route-v1.md` to `retained read-only compatibility decoder/replay input`; it is not route authority, writer selection, or a reason to reintroduce generation-based live routing.
- `docs/protocol/capabilities.md` to state that compact effect reservation/receipt enforcement is live, v1 laws and golden history remain retained, and the standalone v1 CLI has no general live token authority.
- `docs/protocol/packet-state.md` to name the compact mapping/fixture destination and truthfully state whether the standalone module was removed by Phase 4. If the module still exists without a real historical-adapter caller, stop and route its deletion before this docs commit.
- `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md` to check only evidence-proven Phase 1-4 items and cite the committed Phase-1/2, Phase-3, activation, and observation artifacts. Record the ten-unit/three-profile/zero-divergence gate exactly.

- [ ] **Step 5: Add terminal notes to plans without rewriting history**

At the top of each historical plan listed under **File Structure**, add a short `Terminal reconciliation` block with exactly one disposition:

- `implemented and integrated` with the exact accepted head/report;
- `converged into compact kernel` with the exact matrix/head/report;
- `retained compatibility input` with the exact live caller or golden-history path;
- `superseded with equivalent coverage` with the exact successor plan/evidence;
- `withdrawn by owner` with the exact owner handoff.

Do not use `complete` for unexecuted steps, do not erase old checkboxes, and do not describe branch-only code as integrated. The Level-5 plan must map unexecuted duplicate waves to the Opus and compact successor evidence; the final closeout must cite the ChatGPT owner's committed handoff rather than copying its preservation-only plan onto `main`; candidate and targeted-web plans must cite their own Operator reports.

- [ ] **Step 6: Run descriptive-truth checks**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_doc_integrity.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all commands pass. If `check_doc_claims.py` reports a stale anchor, edit only the routed descriptive path that owns it; do not run a broad auto-fix over peer WIP.

- [ ] **Step 7: Commit the exact docs-only range**

Run:

```bash
env -u GIT_INDEX_FILE git diff --name-only
env -u GIT_INDEX_FILE git add -- \
  ARCHITECTURE.md OPERATIONS.md docs/PROGRAM-MANUAL.md DECISIONS.md \
  docs/protocol/route-v1.md docs/protocol/capabilities.md \
  docs/protocol/packet-state.md \
  docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md \
  docs/superpowers/plans/2026-07-08-coordination-hardening-subagent-capacity.md \
  docs/superpowers/plans/2026-07-09-codex-agent-toml-consolidation.md \
  docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md \
  docs/superpowers/plans/2026-07-11-typed-route-authority-slice1.md \
  docs/superpowers/plans/2026-07-12-route-lineage-cas-slice2.md \
  docs/superpowers/plans/2026-07-12-consumable-capabilities-slice3.md \
  docs/superpowers/plans/2026-07-12-packet-state-derivation-slice4.md \
  docs/superpowers/plans/2026-07-13-chatgpt-pro-browser-consultation.md \
  docs/superpowers/plans/2026-07-14-existing-session-bridge-repair.md \
  docs/superpowers/plans/2026-07-14-pipeline-level5-execution.md \
  docs/superpowers/plans/2026-07-15-capability-baseline-runtime-collector.md \
  docs/superpowers/plans/2026-07-15-capability-phase1-surface-inventory-closure.md \
  docs/superpowers/plans/2026-07-15-capability-compact-reducer-phase2.md \
  docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md \
  docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md \
  docs/superpowers/plans/2026-07-15-pre-trigger-append-only-candidate-range.md \
  docs/superpowers/plans/2026-07-15-targeted-web-research-default.md
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git commit -m \
  "docs(protocol): reconcile recovery and compact truth"
```

Expected: the staged list is a subset of the exact paths above and contains every path actually changed. No script, test, active prompt, packet, mailbox, runtime, ref, or owner artifact is in the commit.

### Task 3: Independently verify the final truth range and retention boundaries

**Files:**

- Read: Task 2 docs commit and all cited evidence
- Create through the compact verification publisher: one route-bound specialized `operator-doc-sync` report evidence object and one compact verification transition
- No production or documentation edit in this task

**Interfaces:**

- Consumes: exact Task 2 base/head, the final call graph, activated observation, all predecessor verdicts, and retained compatibility files.
- Produces: one canonical Operator `GO`, `NITS`, or `FAIL` evidence object plus its exact compact verification event OID for factual/status accuracy. It does not grant push or cleanup authority.

- [ ] **Step 1: Refresh the reviewed head and require no post-review edit**

Run:

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
```

Expected: the reviewed head is exactly the docs-only commit and the routed paths are clean. A newer edit invalidates the review binding.

- [ ] **Step 2: Verify every terminal row against Git and evidence**

For each plan/status row, run the cited ancestry command, inspect the cited Operator report body, and verify the cited log/handoff is committed at the reviewed head. Reject:

- a checked item without matching execution evidence;
- branch-only work called integrated;
- smoke/capacity substituted for component correctness;
- an advisory provider result called a verdict;
- a supersession note without equivalent coverage;
- a packet status that disagrees with its binding report;
- any completion claim that omits the actual target repository for PPL.

Expected: all rows are evidence-backed or the verdict is NITS/FAIL.

- [ ] **Step 3: Verify retained and retired compatibility surfaces**

Run:

```bash
rg -n "route_manifest|route_lineage|route_capability|packet_state" \
  scripts tests docs AGENTS.md .agents .codex
env -u GIT_INDEX_FILE git ls-files \
  'tests/fixtures/*route*' 'tests/fixtures/*capability*' \
  'tests/fixtures/*packet*' 'logs/capability-first/*'
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/integration/test_protocol_e2e.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py \
  validate-observation \
  --path logs/capability-first/phase4-compact-activation-2026-07-16/observation.json \
  --root .
```

Expected: live authority uses the compact path; retained v1 references are decoder, replay, test, or history only; no standalone orphan is mislabeled live; unit and integration suites pass; observation validation passes. `scripts/packet_state.py`, if retained, must have a real historical-adapter caller named in docs and tests; otherwise this review returns FAIL for incomplete retirement.

- [ ] **Step 4: Verify remote publication and cleanup remain unauthorized**

Inspect the docs diff, binding compact route/evidence bodies, and content-addressed historical predecessor bodies for any push, branch deletion, worktree removal, ref deletion/lowering, provider attempt, or cleanup claim. Expected: none occurred; publication and cleanup appear only as later consent gates.

- [ ] **Step 5: Publish one findings-first compact doc-sync verdict**

Use the compact verification publisher named by the Task-2 route. The signed specialized report names the route event OID, activation OID/epoch, exact docs base/head, every command above with observed outcome, all evidence paths and digests, historical-join dispositions, retention decisions, and exclusions. It binds the authenticated Operator principal/binding and verdict `GO|NITS|FAIL`. The publisher appends exactly one verification transition at the exact-old event tip and returns the report evidence OID, report blob OID, report SHA-256 digest, and verification event OID. Capture those four values directly as `DOC_SYNC_EVIDENCE_OID`, `DOC_SYNC_BLOB_OID`, `DOC_SYNC_DIGEST`, and `DOC_SYNC_EVENT_OID`; never rediscover them from ambient `HEAD`, a path glob, or legacy mailbox. `GO` means the docs/status range is truthful only; it grants no production GO, activation, push, publication, or cleanup authority.

- [ ] **Step 6: Validate the compact report/event binding**

Run the compact evidence/event validators from the authoritative common directory after the publisher returns:

```bash
: "${DOC_SYNC_EVIDENCE_OID:?capture publisher result}"
: "${DOC_SYNC_BLOB_OID:?capture publisher result}"
: "${DOC_SYNC_DIGEST:?capture publisher result}"
: "${DOC_SYNC_EVENT_OID:?capture publisher result}"
for oid in "$DOC_SYNC_EVIDENCE_OID" "$DOC_SYNC_BLOB_OID" \
  "$DOC_SYNC_EVENT_OID"; do
  printf '%s\n' "$oid" | grep -Eq '^[0-9a-f]{40}$'
done
printf '%s\n' "$DOC_SYNC_DIGEST" | grep -Eq '^[0-9a-f]{64}$'
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py \
  --current --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py inspect \
  --root .
```

Read the exact event object and specialized evidence bytes through the committed compact readers. Recompute the blob and SHA-256 identities; require the event binds that evidence, the Task-2 route OID, exact reviewed base/head, activation OID, Operator binding, and one verdict. Require the current event chain contains the returned event exactly once and stable A1/event/A2 agrees. Legacy mailbox and join-packet trees remain byte-identical. NITS/FAIL remains immutable evidence but blocks Task 4; only canonical GO continues.

### Task 4: Record historical dispositions and create the compact final closeout

**Files:**

- Read only: the four historical coordinator-join packets listed under **Coordinator closeout state**
- Create: `docs/HANDOFF-coordinator-2026-07-16-pipeline-recovery-final-closeout.md`
- Append through the compact writer: one route transition authorizing the handoff-only commit, then one terminal closeout transition after that commit

**Interfaces:**

- Consumes: Task 3 compact Operator GO evidence/event, every predecessor report/handoff/event, historical packet states, activated observation, and clean current HEAD.
- Produces: one route-bound coordinator handoff candidate commit and one terminal compact closeout event that content-addresses it. It authorizes no push or cleanup.

- [ ] **Step 1: Refresh hot state after the doc-sync verdict**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -8
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py \
  validate-observation \
  --path logs/capability-first/phase4-compact-activation-2026-07-16/observation.json \
  --root .
find coordination/locks -type f ! -name .gitkeep -print
```

Expected: all checks pass, locks print nothing, and no newer compact event changes a terminal disposition. Read every relevant compact event/evidence body. Legacy mailbox and packet files are historical projections and are not consumed or mutated.

- [ ] **Step 2: Derive immutable historical-join dispositions without rewriting them**

Apply these exact terminal semantics:

- Control-plane join: record `excepted-by-compact-supersession`, not `done`; cite `tests/fixtures/compact_kernel/control_plane_convergence.json`, `logs/capability-first/phase3-control-plane-convergence.json`, Phase-3 handoff, and the independent compact Phase-3 GO. Preserve every old FAIL/CONTRADICTION and the unmerged preservation branch.
- PPL join: record `done-by-target-verdict` only if its target-aware handoff and cumulative target Operator GO bind the exact corrected evidence-ledger range. Copy that target base/head/range into the final handoff without inventing Pipeline descriptor authority.
- Level-5 Wave-0 join: record `excepted-by-successor-coverage`; map unexecuted duplicate work to accepted Opus/compact successors and never rewrite old failures as GO.
- Opus Stage-A join: record `done-by-recovery-chain` only if canonical Stage-A Operator GO and later B-D closeout prove the exact recovery chain. Cite their content-addressed committed historical reports/events.

For each historical packet, capture path, committed blob OID, SHA-256 digest, last historical status, and derived final disposition in memory for the handoff and closeout transition. Do not edit `status`, `done_evidence`, `handoff_artifact`, or any other packet field. A disagreement between old projection and accepted successor evidence is described in the handoff; it is not repaired after compact activation.

- [ ] **Step 3: Freeze the cleanup-candidate inventory before writing the handoff**

Run:

```bash
env -u GIT_INDEX_FILE git worktree list --porcelain
env -u GIT_INDEX_FILE git branch \
  --format='%(refname:short)|%(objectname)|%(worktreepath)' | sort
rg -n "codex/|\.worktrees/" \
  coordination/capacity/packets coordination/mailbox/sent docs/HANDOFF-*.md
```

For every worktree/branch, record absolute path, branch, full head, clean/dirty state, main ancestry, current packet/handoff references, and exactly one class: `retain-history`, `eligible-after-publication`, or `unmerged-preservation-retain`. A referenced, dirty, advancing, unmerged-preservation, or activation-bearing worktree is never classified deletion-safe. This is inventory only; no branch or worktree changes.

- [ ] **Step 4: Create the final disposition handoff**

Create `docs/HANDOFF-coordinator-2026-07-16-pipeline-recovery-final-closeout.md` with:

1. findings first;
2. current full HEAD, activated head, activation ref/object, epoch, writer mode, and observation digest;
3. one row for every item in umbrella-design Section 7 with exactly one final disposition, exact implementation/convergence head, Operator report, current ancestry result, live-use status, retained history, and packet outcome;
4. a compatibility table for `route/v1`, `capability/v1`, `packet_state.py`, route lineage, existing-session bridge, ChatGPT consultation, Codex role TOMLs, and subagent-capacity policy;
5. a worktree/branch cleanup-candidate table recording exact full heads and one of `retain-history`, `eligible-after-publication`, or `unmerged-preservation-retain`;
6. a publication boundary stating that the post-closeout commit OID will be captured and bound only in a later side-effect executor token, and that remote state remains unchanged until separate consent; the handoff must not attempt to contain its own future commit OID;
7. a cleanup boundary stating that no branch, worktree, runtime, receipt, owner artifact, or activation ref was removed;
8. literal lines `Doc-sync evidence OID:`, `Doc-sync evidence blob:`, `Doc-sync evidence digest:`, and `Doc-sync transition OID:` followed by the exact Task-3 values, plus exact commands and observed results for smoke, compact capacity/current-state, doctor, observation, component verdicts, and doc-sync GO;
9. `## Exact Next Trigger`: after the closeout commit exists, user either leaves the repository local-only or separately names one publication executor for that exact captured commit OID; cleanup remains a second later decision.

The umbrella design's terminal-status edit already belongs to the Task-2 Director docs range and its independent doc-sync verdict. The coordinator does not edit that spec after GO. The handoff cannot contain its own future commit OID or the future closeout event OID.

- [ ] **Step 5: Append the compact handoff route and commit only the candidate handoff**

Through the authenticated compact coordinator publisher, append one route transition at the exact current activation/event tip. It binds Task 3's four evidence identities, the exact current `main` base, the sole path `docs/HANDOFF-coordinator-2026-07-16-pipeline-recovery-final-closeout.md`, coordinator principal/binding, handoff-only action, historical packet path/blob/digest inventory, and exclusions for packet/mailbox mutation, production, active prompts, refs, provider, push, and cleanup. Capture the returned route event OID as `CLOSEOUT_ROUTE_EVENT_OID`; exact-old CAS failure or activation drift stops.

Validate that transition through compact current-state/capacity/doctor. Create the handoff from Step 4, require its working-tree and staged path set to equal only the literal handoff path, run `git diff --check`, and commit it with subject `docs(coordinator): record recovery final closeout candidate`. Capture `HANDOFF_PARENT_HEAD`, `HANDOFF_COMMIT`, `HANDOFF_BLOB_OID`, and the SHA-256 `HANDOFF_DIGEST` directly from that commit. Require one-parent topology and exact route-base ancestry.

Expected: the commit changes exactly the candidate handoff. It contains the doc-sync evidence identities and historical dispositions but neither its own commit OID nor a future closeout event OID. No legacy packet/mailbox file changes.

- [ ] **Step 6: Append one terminal compact closeout transition**

Through the authenticated compact coordinator publisher, append exactly one `pipeline-recovery-closeout/v1` transition with exact-old event-tip CAS. It content-addresses `HANDOFF_COMMIT`, the handoff path, `HANDOFF_BLOB_OID`, and `HANDOFF_DIGEST`; Task 3's report evidence/blob/digest/event identities; `CLOSEOUT_ROUTE_EVENT_OID`; the observation path/blob/digest and compact GO event; every fixed predecessor handoff path/commit/blob/digest and terminal event; and all four historical packet path/blob/digest/derived-disposition rows. Its status is `done`, its exclusions prohibit publication, cleanup, provider use, and ref lowering, and its returned event OID is the sole terminal `done_evidence`.

Capture the returned OID as `CLOSEOUT_EVENT_OID` directly from the publisher result. Read the exact event and require one first-parent inclusion, matching activation OID/epoch, matching previous tip, exact content identities, authenticated coordinator binding, and no legacy packet/mailbox payload or mutation. A collision, uncertainty, or mismatched event stops without blind retry. Do not patch or recommit the handoff after this append.

- [ ] **Step 7: Prove compact closeout and historical immutability**

Require `CLOSEOUT_ROUTE_EVENT_OID` and `CLOSEOUT_EVENT_OID` to be full Git OIDs. Run compact capacity/current-state, `protocol_doctor.py --current --wave 2`, `kernel_activation.py inspect`, the observation validator, `ci_smoke.py`, and `git diff --check`. For each of the four historical packet paths, compare its blob OID at `HANDOFF_PARENT_HEAD` with the blob OID at `HANDOFF_COMMIT`; every pair must be equal. Require an empty index and read the closeout event through stable A1/event/A2.

Expected: compact current-state, doctor, activation, observation, and smoke pass; each historical packet is byte-identical across the handoff commit; and the exact closeout event binds the handoff/report/predecessor set. These structural results do not replace component GO evidence.

- [ ] **Step 8: Stop without a post-event patch or implicit publication**

Record `HANDOFF_COMMIT` and `CLOSEOUT_EVENT_OID` in the coordinator in-memory reconciliation result and report them to the user. The compact event OID, not a rewritten packet, Markdown mailbox path, or handoff patch, is terminal `done_evidence`. Do not create another commit merely to write the event OID into the handoff. Remote publication and cleanup remain separately unauthorized.

### Task 5: Publish a non-runnable code/docs `main` mirror only under a separate user-named executor token

**Files:**

- No repository file mutation required
- External target: `origin` `refs/heads/main`

**Interfaces:**

- Consumes: final closeout commit, current local/remote ref evidence, explicit user publication approval, and exactly one named executor.
- Produces: at most one fast-forward push of the exact user-authorized full object ID to `origin` `refs/heads/main`, plus a read-only remote-ref postcheck. It publishes no compact protocol ref or protocol-only object, creates no runnable replica, and produces no cleanup authority.

- [ ] **Step 1: Stop unless the user separately authorizes publication and names the executor**

The approval must be later than the final closeout commit and name one executor. Record a side-effect executor token with:

- `side_effect_id`: `pipeline-recovery-publication-2026-07-16`;
- `target`: `origin refs/heads/main`;
- `authorized_head`: the exact 40-lowercase-hex closeout commit copied verbatim from the later user authorization; it must never be derived from ambient `HEAD`;
- `allowed_command_class`: `git push origin <authorized-head>:refs/heads/main`;
- preflight: exact local head, live remote head, fast-forward ancestry, clean index, final handoff, compact doc-sync GO evidence/event, activated observation PASS, terminal compact closeout event, and no newer superseding compact event;
- stop condition: any local HEAD, remote head, activation ref/object, compact event tip/evidence, lock, or retained-owner boundary drift;
- postcheck: live `refs/heads/main` equals the intended full local head;
- observer seats: read-only contradiction reporters;
- final closeout owner: coordinator;
- remote classification: code/docs/history mirror only, not a serving or recovery replica;
- non-goals: force, tag, branch deletion, worktree cleanup, provider, activation, retry, fallback, protocol-ref/object replication, or another remote ref.

If the user does not name an executor, remain local-only.

- [ ] **Step 2: Perform the live remote preflight immediately before push**

Run:

```bash
set -euo pipefail
: "${AUTHORIZED_HEAD:?copy the exact full SHA from the user-approved executor token}"
printf '%s\n' "$AUTHORIZED_HEAD" | grep -Eq '^[0-9a-f]{40}$'
test "$(env -u GIT_INDEX_FILE git symbolic-ref --short HEAD)" = main
env -u GIT_INDEX_FILE git cat-file -e "${AUTHORIZED_HEAD}^{commit}"
LOCAL_HEAD="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
test "$LOCAL_HEAD" = "$AUTHORIZED_HEAD"
REMOTE_HEAD="$(env -u GIT_INDEX_FILE git ls-remote --exit-code origin \
  refs/heads/main | awk '{print $1}')"
test -n "$REMOTE_HEAD"
env -u GIT_INDEX_FILE git merge-base --is-ancestor "$REMOTE_HEAD" "$AUTHORIZED_HEAD"
env -u GIT_INDEX_FILE git diff --quiet
env -u GIT_INDEX_FILE git diff --cached --quiet
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py \
  validate-observation \
  --path logs/capability-first/phase4-compact-activation-2026-07-16/observation.json \
  --root .
printf 'authorized=%s\nlocal=%s\nremote=%s\n' \
  "$AUTHORIZED_HEAD" "$LOCAL_HEAD" "$REMOTE_HEAD"
```

Expected: remote is an ancestor of local, tracked/index state is clean, observation validation passes, and printed SHAs match the publication token. Re-read the activation object/ref, compact event tip, bound doc-sync/closeout evidence, locks, and retained-owner state after these commands; any drift stops the push. Historical mailbox/packet files are not current authority.

- [ ] **Step 3: Execute exactly one authorized fast-forward push**

After rereading the compact closeout event/evidence, locks, activation object/ref, and event tip, the named executor performs one final exact local/remote comparison and runs:

```bash
set -euo pipefail
test "$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')" = \
  "$AUTHORIZED_HEAD"
test "$(env -u GIT_INDEX_FILE git ls-remote --exit-code origin \
  refs/heads/main | awk '{print $1}')" = "$REMOTE_HEAD"
env -u GIT_INDEX_FILE git push origin \
  "$AUTHORIZED_HEAD:refs/heads/main"
```

Expected: one successful fast-forward update. On rejection, uncertainty, or transport failure, do not force, retry, switch remotes, or use another executor; return to the user with the terminal evidence.

- [ ] **Step 4: Verify the remote ref read-only**

Run:

```bash
set -euo pipefail
PUBLISHED_HEAD="$(env -u GIT_INDEX_FILE git ls-remote --exit-code origin \
  refs/heads/main | awk '{print $1}')"
test "$PUBLISHED_HEAD" = "$AUTHORIZED_HEAD"
printf 'published=%s\n' "$PUBLISHED_HEAD"
```

Expected: the published full SHA equals the intended final closeout head. This remote ref proves only code/docs/history publication. It does not prove, publish, or authorize the compact activation/event/cursor/recovery/archive refs or protocol-only objects; a fresh clone remains non-runnable and must fail closed until a separate authenticated protocol-state replication/import procedure is designed, approved, executed, and stable-view validated. Do not create a second local commit that would immediately make `main` ahead again.

### Task 6: Revalidate the frozen cleanup inventory for a separate authorization

**Files:**

- Read: cleanup-candidate table in `docs/HANDOFF-coordinator-2026-07-16-pipeline-recovery-final-closeout.md`
- Local targets: none in this plan; the final handoff inventories candidates for a later exact cleanup authorization

**Interfaces:**

- Consumes: final closeout, current worktree/branch inventory, exact full heads, and all remaining packet/handoff references.
- Produces: a read-only comparison verdict against the already committed cleanup-candidate table and a hard stop. It edits and removes nothing; an exact later cleanup plan is written only after the user names targets and one executor.

- [ ] **Step 1: Snapshot the live cleanup state read-only**

Run:

```bash
env -u GIT_INDEX_FILE git worktree list --porcelain
env -u GIT_INDEX_FILE git branch --format='%(refname:short)|%(objectname)|%(worktreepath)' | sort
rg -n "codex/|\.worktrees/" \
  coordination/capacity/packets coordination/mailbox/sent docs/HANDOFF-*.md
```

Expected: every candidate has an exact current full head and every remaining protocol reference is visible. This output is comparison input only; it is not written back to the already committed handoff.

- [ ] **Step 2: Compare every live row with the committed handoff**

For every row printed by Step 1, require the committed handoff already to contain its absolute worktree path, branch, full head, clean/dirty state, main ancestry, current packet/handoff references, and exactly one class:

- `retain-history` for read-only compatibility, activation evidence, or still-referenced branches;
- `eligible-after-publication` only for clean branches whose full heads are ancestors of `main` and have no active reference;
- `unmerged-preservation-retain` for owner/control-plane/root-WIP preservation branches not integrated wholesale.

Expected: no live row is absent, changed, or differently classified; no committed row disappeared; and no unmerged preservation head is presented as deletion-safe. Any mismatch blocks cleanup and requires a new, separately reviewed inventory commit; Task 6 does not edit the handoff.

- [ ] **Step 3: Prove retention and activation authority remain intact**

Run:

```bash
env -u GIT_INDEX_FILE git show-ref --verify refs/protocol/kernel-activation
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py \
  validate-observation \
  --path logs/capability-first/phase4-compact-activation-2026-07-16/observation.json \
  --root .
env -u GIT_INDEX_FILE git cat-file -e HEAD:scripts/route_manifest.py
env -u GIT_INDEX_FILE git cat-file -e \
  HEAD:logs/capability-first/phase4-compact-activation-2026-07-16/observation.json
env -u GIT_INDEX_FILE git worktree list --porcelain
```

Expected: activation ref and observation remain valid; read-only route/v1 decoder and committed observation remain reachable; no worktree or branch changed during this task.

- [ ] **Step 4: Stop at the cleanup authority boundary**

The next cleanup prompt must name one executor and copy exact worktree paths, branch names, and full heads from the final handoff. Only then write a new cleanup plan containing literal commands for those exact targets and safe ancestry checks. Generic approval to publish, finish, close, or clean does not authorize any removal, and this plan deliberately runs no `git worktree remove`, `git branch -d`, or branch force-delete command.

## Completion Evidence

The recovery sequence is terminally reconciled only when:

1. the Phase-4 observation validator passes on the current activated head;
2. every umbrella Section-7 item has one evidence-bound final disposition;
3. descriptive docs and historical plan statuses receive independent doc-sync GO;
4. the four legacy joins remain immutable historical projections, their evidence-derived dispositions are content-addressed by the final handoff/compact closeout transition, and that transition validates;
5. read-only v1 decoding, mapping/receipt laws, golden histories, and activation evidence remain committed;
6. the final closeout commit is structurally green and leaves no recovery-target index/worktree ambiguity;
7. publication either remains explicitly local-only or has one separately authorized, verified fast-forward push classified as a non-runnable code/docs mirror; protocol-state replication remains separately unauthorized;
8. cleanup either remains unauthorized or removes only separately approved clean/merged targets without force or history loss.

## Exact Next Trigger

After the final coordinator closeout commit and terminal compact closeout event, the user chooses independently between continued local-only retention and one named publication executor for the exact authorized full SHA to `origin` `refs/heads/main` as a non-runnable code/docs mirror. Publishing compact protocol refs/objects to a serving or recovery replica requires a new authenticated replication design and separate authorization. Branch/worktree cleanup requires a later, separate approval naming exact paths, branches, full heads, and one cleanup executor.
