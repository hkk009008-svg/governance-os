# Pipeline Recovery Sequence Design

**Status:** User-approved recovery architecture; umbrella design authorized for
commit on 2026-07-16.

**Purpose:** Recover every planned-only, branch-only, blocked, compatibility-only,
and already-live protocol item without losing owner work, activating competing
authority models, or weakening the four-seat verification boundary.

**Scope:** This is a sequencing and disposition design. It authorizes this design
document only. It does not authorize a production edit, coordinator route,
mailbox consume, lock, provider call, canary, merge, push, activation, branch
deletion, or worktree cleanup.

## 1. Decision

Use a **bounded two-track recovery**:

1. Stabilize ownership while completing the only active governed implementation
   lane.
2. Restore the Opus path end to end.
3. Add and independently verify the Pipeline-owned target-aware evidence-ledger
   review bridge required by the binding PPL hold.
4. Install the append-only candidate policy that gives seats room for review
   corrections.
5. Run the evidence-ledger product correction only after candidate-policy
   integration and the distinct post-candidate target-bridge compatibility GO.
6. Close planned instruction work and non-authoritative compact-kernel work in
   separate lanes.
7. Converge legacy authority foundations into one compact kernel instead of
   activating them independently.
8. Activate once, last, with explicit user authority and one named executor.
9. Retire superseded compatibility surfaces only after equivalent compact
   coverage and observation evidence exist.

The unit of completion is not “a plan checkbox changed.” A unit is complete only
when current Git state, its exact reviewed range, executed evidence, and the
required Operator GO agree.

## 2. Alternatives considered

### Fully serial stabilization

This is simplest to reason about, but it leaves a second pair idle even when the
work is cross-repository and write-set disjoint. It is retained as the fallback
whenever ownership or path boundaries cannot be proved.

### Candidate policy first

Rejected. The candidate implementation touches the Opus bridge/receipt boundary
and the same instruction surfaces currently occupied by owner WIP. Starting it
first would violate its own ownership gate and create avoidable rebases.

### Bounded two-track recovery

Selected. It keeps a single pair on shared Pipeline files while allowing a second
pair to work only on a separately routed, independently reviewable deliverable.
The coordinator owns convergence and stops either track when paths, authority, or
activation boundaries overlap.

## 3. Approval-time state binding

This design was approved against the following repository state:

- Pipeline `main` at
  `dc0fb551476928e0b6ea5a207208040092a5aa7b`.
- Wave 2 process gate MET with zero remediation rows.
- Protocol capacity valid with three blocked coordinator joins:
  `coord-control-plane-authority-foundation-join`,
  `coord-ledger-ppl-recommendation-evaluation-join`, and
  `coord-pipeline-opus-transport-first-recovery-stage-a-join`.
- Director2 owns the active Opus Stage-A diagnostic packet; Operator2 remains
  blocked without a lawful descriptor/request trigger.
- The root worktree contains distinct ChatGPT local-reprepare and compact-kernel
  WIP on files needed by later plans.
- The capability Phase-2 shadow worktree advanced during reconciliation and
  design review to `1306c157ac434389444e77935d24db8b3189ee2c`, is clean, and is
  not an ancestor of `main`. That commit dispositioned the previously dirty
  `scripts/capability_v1_adapter.py` and
  `tests/unit/test_capability_v1_adapter.py` blobs, but no exact owner handoff
  has yet frozen the branch for integration review.
- The Stage-A branch head is
  `16c4f83aef4130d977a91d623a9254c4fd46980a` and is not an ancestor of `main`.
- The control-plane worktree remains at
  `6983673db60bff0d21548a90ab1db2fcbbfa377a` with uncommitted work and is not an
  ancestor of `main`.

Evidence commands used to bind and recheck this snapshot:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -8
.venv/bin/python scripts/wave_gate_check.py 2
.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git worktree list --porcelain
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase2-shadow-2026-07-15 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/opus-transport-first-stage-a-director2 \
  status --short --branch
for sha in \
  1306c157ac434389444e77935d24db8b3189ee2c \
  16c4f83aef4130d977a91d623a9254c4fd46980a \
  6983673db60bff0d21548a90ab1db2fcbbfa377a; do
  if env -u GIT_INDEX_FILE git merge-base --is-ancestor "$sha" main; then
    echo "$sha in-main"
  else
    echo "$sha not-in-main"
  fi
done
```

Every future route must refresh these facts. This binding is evidence of the
decision context, not permission to act on stale SHAs.

## 4. Global invariants

1. **No work loss.** Do not stash, reset, rewrite, absorb, or overwrite owner
   WIP. Each dirty unit must be committed and handed off by its owner or
   explicitly withdrawn by that owner.
2. **Coordinator boundary.** The coordinator may reconcile, design, route, and
   close protocol state. It does not implement behavior-changing production
   fixes.
3. **One authority model at a time.** Markdown/v1 remains live until the compact
   activation gate. Compatibility primitives do not gain independent live
   authority on the way to that gate.
4. **One active writer per shared path.** Parallel work requires disjoint
   write sets, separate review ranges, and separate Operator verdicts.
5. **Evidence before state.** Green smoke or a valid capacity board does not
   substitute for the relevant executed tests and Operator GO.
6. **Side effects remain separate.** Commit authorization in this design does
   not imply merge, push, provider, canary, lock, activation, publication, or
   cleanup authority.
7. **Freshness before action.** Refresh HEAD, mailbox bodies, capacity, locks,
   target status, and branch ancestry immediately before every route, review
   request, integration, or activation decision.
8. **No mega-plan execution.** Each independently rejectable subsystem receives
   its own spec/plan or uses its already approved one.

## 5. Dependency graph

```text
0A owner/WIP reconciliation ───────────────┐
                                           ├─> 2A candidate policy
0B Opus Stage-A correction ─> 1A Opus B-D ─┘          │
                               │                       ├─> post-candidate bridge GO
                               └─> 1B target-aware ledger bridge ─┘
                                                               │
                                                               └─> 2B PPL correction ─> 3A web default

0A canonical compact branch ─> 3B compact Phases 1-2
                                │
control-plane salvage ──────────┴─> 4 compact Phase 3 ─> 5 Phase 4 activation
                                                              │
compatibility inputs ─────────────────────────────────────────┘
                                                              │
                                                              └─> 6 retirement/publication
```

The arrows are hard prerequisites. Items on the same horizontal phase may run
in parallel only after the coordinator proves repository and write-set
separation.

## 6. Ordered recovery phases

### Phase 0A — Owner and WIP reconciliation

**Owner:** Coordinator for reconciliation; existing WIP owners for any mutation.

**Actions:**

- Produce an exact-path disposition for every dirty target: owner, source head,
  intended destination, allowed paths, tests already run, and one of
  `commit-and-handoff` or `withdraw`.
- Keep ChatGPT local-reprepare changes separate from compact-kernel changes.
- Require a dedicated approval/spec/plan before treating ChatGPT local-reprepare
  as a shippable feature; its current untracked plan is not durable authority.
- Move or hand off compact root WIP to one canonical compact branch; do not
  duplicate it across root and feature worktrees.
- Obtain an exact owner handoff for the clean Phase-2 head `1306c157`; a clean
  commit does not by itself freeze ownership or authorize integration review.
- Freeze each handed-off branch at an exact full SHA. Later advancement requires
  a new handoff and invalidates earlier review bindings.

**Exit gate:** Every target needed by the Opus, candidate-policy, targeted-web,
and compact plans is clean or represented by an exact-blob owner handoff. No
branch in the recovery set is both actively advancing and owner-ambiguous.

**Why first:** Uncommitted instruction text already affects sessions, and owner
ambiguity blocks every later shared-surface plan.

### Phase 0B — Correct and verify Opus Stage A

**Owner:** Director2 implements; Operator2 verifies; coordinator corrects route
authority only.

**Actions:**

- Preserve `M0=56091d1` and `F=16c4f83` byte-for-byte.
- Issue one bounded append-only correction authorizing a `Q` commit after `F`.
- In `Q`, address both confirmed Important findings:
  - fail closed on contradictory diagnostic field combinations;
  - distinguish broker cleanup failure from broker startup failure without
    leaking raw diagnostic text or discarding a completed provider result.
- Add non-vacuous tests before the fix, then rerun the complete provider-free
  suite and fresh independent spec and quality reviews.
- Create descriptor and verify-request authority only after both reviews pass.

**Exit gate:** Operator2 returns one canonical Stage-A GO, NITS, or FAIL for the
lawful `R..Q` range. GO proves diagnostics only. Real provider attempts remain
zero.

**Why parallel with 0A:** Its isolated branch and four-file aggregate scope do
not require the dirty root instruction surfaces.

### Phase 1A — Restore Opus through Stages B, C, and D

**Owner:** A freshly routed Director/Operator pair; coordinator owns stage
transitions.

**Actions:**

1. Stage B fixes only the first boundary proven by Stage A and verifies it
   provider-free.
2. Stage C requires a fresh route-bound identity and separately authorized
   executor for exactly one existing-session canary.
3. The canary must produce a terminal receipt, an effective Opus model, and no
   retry, fallback, credential entry, browser substitution, or API substitution.
4. Stage D requires independent Operator2 GO and merged-tree verification before
   any separately authorized push.

**Exit gate:** The replacement Opus path has final GO and authorized local
integration, or it has a durable FAIL with a bounded next owner. A provider
attempt is never inferred from design approval.

**Why before candidate policy:** The candidate implementation changes the same
bridge/receipt boundary. Finishing Opus prevents competing histories and makes
the general provider path available to the separate target-aware extension.
Generic Opus GO is necessary but not sufficient for PPL.

### Phase 1B — Build the target-aware evidence-ledger review bridge

**Owner:** A separately routed Pipeline Director/Operator pair. The bridge is
Pipeline-owned and advisory-only; it receives no evidence-ledger edit, seat,
verdict, route, lock, publication, or side-effect authority.

**Binding source:**
`coordination/mailbox/sent/2026-07-13T11-38-14Z-coordinator-to-all-coordination.md`
under “Successor Workflow Boundary.”

**Actions:**

- Extend the verified Pipeline Opus bridge rather than stretching the generic
  bridge across repositories without a target contract.
- Bind each request, receipt, response, and reconciliation to the Pipeline
  route/Wave/committed authority artifacts and to the exact evidence-ledger
  repository, root, linked-worktree Gitdir, Git common directory, cumulative
  base, correction base, and eventual immutable reviewed head.
- Bind the correction write allowlist initially to `recommendation/cli.py`,
  `recommendation/tests/test_cli.py`, and `ARCHITECTURE.md` only when behavior
  makes its claims stale.
- Limit challenge context to committed code, synthetic tests, and content-free
  command metadata. Exclude mutable canonical databases, workbooks, resources,
  and business data.
- Bind exact requirement paths, verification commands, Git blob identities,
  canonical relevant-paths hash, and a mailbox snapshot hash over the named
  committed authority artifacts.
- Version the prompt, response, receipt, namespace, question kind, and monotonic
  challenge sequence. The two questions are distinct:
  `design-time/1` before the first product edit and `actual-diff/2` after the
  additive correction commit.
- Permit at most one provider attempt per question with no retry or fallback;
  keep finding reconciliation with the Operator.
- Add negative tests proving that successful, malformed, stale, or mismatched
  reviews cannot write either worktree, stage or commit Git, publish mailbox
  events, mutate routes/cursors/locks, acquire a seat, invoke arbitrary
  commands, emit a binding GO/NITS/FAIL, or authorize lock release.
- Add prompt-sync tests proving that no provider-facing prompt assigns a seat,
  controller identity, verdict role, or side-effect authority.

**Exit gate:** The target-aware extension has independent GO for its exact
Pipeline range and a fresh coordinator route binds the extension before any PPL
product edit. Receipt presence proves only an advisory attempt.

**Why separate:** The binding PPL hold explicitly forbids treating generic Opus
hardening as target-aware review. Without this phase, the PPL entry gate has no
producer.

### Phase 2A — Implement append-only candidate policy

**Owner:** One Director/Operator pair using the approved candidate-policy design
and implementation plan.

**Actions:**

- Rerun the plan's exact ownership check; any output blocks routing.
- Self-host this implementation under the legacy one-off four-commit plus one
  reviewer-fix boundary. It cannot rely on the validator it is creating.
- Implement the shared candidate range validator, CLI, descriptor v2 support,
  prompt/doc mirrors, abuse cases, and v1 compatibility exactly as already
  specified.
- Require independent Operator GO before integration.

**Exit gate:** The validator and descriptor contract are integrated and future
eligible routes can opt into one-to-five append-only commits. Existing v1 routes
remain compatible.

**Why here:** It is the highest-leverage workflow fix, but becomes safe only
after Opus and owner conflicts clear.

### Phase 2B — Correct PPL publication and cleanup races

**Owner:** The target-repository controller named by a corrected Pipeline route,
with the target-aware independent verifier named separately. Codex remains
read-only in the target unless that corrected route and the target repository's
own instructions explicitly grant edit authority.

**Entry gate:** Phase 1B has independent GO and a fresh coordinator route binds
its immutable cross-repository contract while preserving the target
repository's controller-authority boundary. Generic Opus restoration alone does
not satisfy this gate.

**Actions:**

- Reproduce the recorded post-open relocation, late publication substitution,
  and cleanup-time foreign-path deletion windows.
- Fix every reproduced race with non-vacuous tests.
- Replay the exact candidate range, ordinary suites, and the adversarial race
  probes before cumulative Operator verdict.

**Exit gate:** A target-repository-aware cumulative Operator GO covers the exact
corrected range. Publication remains a separate decision.

**Why after 2A:** Candidate policy changes the generic bridge/receipt dependency.
The target-aware bridge therefore receives a distinct post-candidate compatibility
GO before PPL product work begins; this prevents a stale advisory boundary from
authorizing target edits.

### Phase 3A — Implement targeted public web-research default

**Owner:** One Director/Operator pair using the already approved design and plan.

**Actions:**

- Start only after candidate policy is integrated, its target-bridge compatibility
  GO is binding, PPL is terminal, and prompt surfaces are clean.
- Keep the feature instruction-only: public read-only evidence gathering with
  local-source precedence and no login, credential, mutation, provider, or
  side-effect authority.
- Use prompt-sync and doc-integrity tests for all operative mirrors.

**Exit gate:** Operator GO and authorized integration of the instruction/test
range.

**Why after candidate policy and PPL:** Candidate policy and its compatibility
GO must be stable first, and the target-review family must be terminal with no
reserved, in-flight, or unreconciled attempt before prompt-authority surfaces
change. Web research remains lower leverage than both gates.

### Phase 3B — Close compact-kernel Phases 1 and 2

**Owner:** A dedicated compact-kernel Director/Operator pair.

**Actions:**

- Select one canonical branch and freeze its exact review range.
- Verify and integrate Phase-1 baseline closure before Phase-2 authority claims.
- Finish Phase-2 shadow adapter inventory, durable parity artifact, and closeout
  review.
- Preserve epoch `0`, writer `v1`, and structural prohibition of shadow GO,
  DONE, and effects.

**Exit gate:** Phase-1 and Phase-2 exact ranges have independent GO, zero
authority/effect-eligibility divergence across the complete corpus, and
authorized integration. No compact path is authoritative.

**Why parallel with 3A:** Compact implementation uses a separate bounded write
set once root ownership is reconciled; it must stop if prompt/doc paths overlap.

### Phase 4 — Salvage control-plane guarantees and build compact Phase 3

**Owner:** One Pipeline Director/Operator pair; coordinator closes the legacy
join only after acceptance mapping.

**Actions:**

- Do not merge the dirty control-plane branch wholesale.
- Diff its current state against `main` and the compact design.
- Map every still-valid identity, snapshot, fail-visible scan, publication,
  principal, and privileged-verifier invariant to a compact Phase-3 acceptance
  criterion and adversarial test.
- Explicitly mark each old criterion `carried-forward`, `already-satisfied`, or
  `superseded-with-equivalent-coverage`.
- Add real but inactive compact callers for principal binding, scoped
  verification, effects, provider/advisory dispatch, and recovery.
- Delete or route every helper that still has no real caller; do not keep a
  second dormant authority framework.

**Exit gate:** Compact Phase 3 passes principal-spoofing, stale-GO,
duplicate-delivery, ambiguous-effect, duplicate-spend, and unavailable-provider
tests while live v1 semantics remain unchanged. The legacy control-plane join
may then close as superseded with evidence.

**Why before activation:** These are the identity and effect boundaries on which
the compact writer relies.

### Phase 5 — Compact Phase 4 reader migration and activation

**Owner:** Routed implementer/verifier pair; exactly one user-approved activation
executor.

**Actions:**

- Migrate capacity, mailbox, ledger-start, continuation, seat-status, doctor,
  and operative-doc readers with dual-read/single-v1-write behavior first.
- Run mixed-version, replay, canary, fencing, stale-epoch, duplicate-effect, and
  rollback-rehearsal evidence.
- Complete, cancel, or explicitly migrate every in-flight v1 unit.
- After independent GO and explicit user authorization, CAS one monotonic
  compact-writer epoch through `refs/protocol/kernel-activation`.
- Observe the activated head before pruning. Rollback is a newer epoch, never an
  in-place downgrade.

**Exit gate:** Exactly one writer mode, all cutover evidence green on the
activated head, and a completed observation window with no authority or effect
divergence.

**Why last:** This is the sole live authority cutover and the hardest operation
to reverse safely.

### Phase 6 — Retirement, documentation truth, and publication

**Owner:** Coordinator for reconciliation; routed owners for any code deletion;
user-named executor for external side effects.

**Actions:**

- Reconcile plan checkboxes and status prose against Git ancestry and executed
  evidence.
- Retire historical worktrees/branches only with explicit cleanup authority.
- Keep read-only v1 decoding and golden histories for the documented retention
  period.
- Push only after merged-tree verification and separate user authorization.

**Exit gate:** Every item in Section 7 has one durable final disposition and no
active packet or plan points to removed authority.

## 7. Item-by-item disposition

| Item | Required outcome |
|---|---|
| Opus Stage A | Correct both Important findings, obtain provider-free GO |
| Opus Stages B-D | Fix first proven boundary, one authorized canary, GO, integration |
| Target-aware evidence-ledger bridge | Implement immutable cross-repo binding and two advisory checks before PPL edits |
| Candidate policy | Implement and integrate after Opus/ownership gates |
| Targeted web default | Implement after candidate policy on clean prompt surfaces |
| ChatGPT local-reprepare WIP | Obtain owner handoff and dedicated approval/plan, or withdraw |
| Capability Phase 1 | Verify closure evidence and integrate before Phase 2 claims |
| Capability Phase 2 | Complete parity/closeout, integrate as non-authoritative shadow |
| Compact Phases 3-4 | Connect real inactive callers, then perform one explicit cutover |
| PPL recommendation path | Correct all reproduced publication/cleanup races and obtain GO |
| Control-plane authority branch | Extract unsuperseded guarantees; close old join as superseded |
| `route/v1` | Retain as decoder/replay input; never independently activate |
| `capability/v1` | Carry receipt/CAS laws forward; never independently become live token authority |
| `packet_state.py` | Carry mapping laws/fixtures into compact adapter; retire standalone module after coverage |
| Route-lineage CAS | Retain for legacy guard selection; replace with compact activation-ref CAS |
| Level-5 unexecuted work | Map unmet acceptance criteria forward; retire duplicate/superseded waves |
| Existing-session bridge worktrees | Preserve until replacement Opus path is GO; then retire with authority |
| ChatGPT consultation | Preserve current live implementation and regression coverage |
| Codex role TOMLs | Preserve current live implementation and prompt-sync coverage |
| Subagent-capacity policy | Preserve current live behavior and regression coverage |

“Address” therefore has four lawful meanings: implement, correct/integrate,
converge into the compact kernel, or retire with equivalent coverage. It does
not mean blindly execute every historical unchecked task.

## 8. Compatibility convergence rules

### `route/v1`

Keep it as historical input and a deterministic decoder. Do not introduce new
generation-based live authority merely to remove it later. Its comparator may
be retired after compact readers cover the same histories and no caller relies
on standalone output.

### `capability/v1`

Preserve command binding, one-time receipt CAS, non-vacuous evidence, and stale
route refusal as compact effect-boundary requirements. Do not make its CLI the
general live token executor. Retire the standalone consumer only after the
compact effect path proves equivalent or stronger behavior.

### `packet_state.py`

Preserve its work/verdict mapping laws and replay fixtures. Part B does not wire
the legacy module directly into current G1/G5/G6 gates. Compact readers consume
the tested mapping; the standalone diagnostic can then be removed if it has no
remaining real caller.

### Route lineage

Legacy lineage remains a guard and compatibility input until compact activation.
The new activation reference becomes the monotonic writer-mode authority. No
new live route generation scheme is required before that cutover.

## 9. Failure and stop behavior

- **Dirty-path recurrence:** stop the affected route and request a new exact-blob
  handoff. Do not absorb the diff.
- **Branch advancement after handoff:** invalidate the old range and repeat
  review binding; do not infer that the new commit is included.
- **Review returns issues:** the owner either lands an authorized append-only
  correction or returns to the coordinator. Prose cannot convert issues to pass.
- **Operator returns NITS or FAIL:** stop integration and keep the exact evidence
  durable. Do not auto-fix as coordinator.
- **Provider unavailable or uncertain:** persist terminal evidence, perform no
  retry/fallback, and return to the coordinator or user as specified by the
  active route.
- **PPL controller-authority contradiction:** preserve target HEAD and stop for a
  corrected evidence-ledger-aware route.
- **Target-aware binding mismatch:** fail before provider launch; do not repair a
  stale root, Gitdir, common directory, base/head, blob, route, or mailbox hash
  by inference.
- **Compact divergence:** keep epoch `0`/writer `v1`; no partial activation.
- **Activation drift:** abort before CAS if HEAD, mailbox, route, in-flight units,
  or writer state changed.
- **Post-activation regression:** use a newer rollback epoch and preserve the
  activated evidence; never delete/lower the activation reference in place.

## 10. Verification architecture

Each implementation plan must name:

- exact base/head and allowed paths;
- RED and GREEN focused tests;
- abuse/race/replay cases required by its authority boundary;
- full regression commands;
- independent spec and quality review where applicable;
- lawful Lane-V descriptor/request or evidence-ledger verification bridge;
- Operator GO/NITS/FAIL owner;
- merge, push, provider, publication, and activation exclusions;
- a merged-tree or activated-head postcheck when the phase reaches that boundary.

The umbrella closeout additionally requires:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE git diff --check
```

These commands prove structural health only. Component correctness still comes
from the named tests and binding Operator reports.

## 11. Plan decomposition after design review

Do not create one implementation mega-plan. After the user reviews this committed
design, retain the already approved Opus, candidate-policy, targeted-web, and
compact Phase-2 plans, and author separate plans only where a durable executable
plan is still missing:

1. owner/WIP disposition and canonical-branch handoff;
2. Opus Stage-A `Q` correction and later B-D routing amendments;
3. Pipeline-owned target-aware evidence-ledger Opus bridge;
4. PPL race correction under that independently verified bridge;
5. compact Phase-1/2 integration and closeout;
6. control-plane-to-compact Phase-3 convergence;
7. compact Phase-4 reader migration, activation, observation, and rollback;
8. final supersession/retirement and publication reconciliation.

Each plan must be independently reviewable and must preserve the phase entry and
exit gates in this design.

## 12. Subagent utilization

A bounded read-only dependency helper independently challenged the order and
identified two important inversions to avoid: candidate policy before the Opus
bridge is stable, and independent activation of typed/control-plane primitives
before compact convergence. The coordinator verified both conclusions against
current plans, branches, and protocol docs. The helper edited nothing and held no
route, verdict, mailbox, lock, provider, merge, push, or activation authority.

## 13. Acceptance criteria for this umbrella design

The design is ready for task-level planning after the user reviews the exact
committed wording and requests no correction. This is a written-spec review,
not a repeat decision on the already approved high-level sequence. The design:

1. addresses every audited item with an explicit outcome;
2. preserves all owner WIP and branch evidence;
3. closes the active Opus lane before overlapping validator work;
4. installs candidate policy before later complex shared-surface work;
5. produces the separately verified target-aware bridge before any PPL edit;
6. permits parallelism only across disjoint repositories/write sets;
7. converges compatibility primitives instead of activating competing authority;
8. keeps provider, merge, push, publication, activation, and cleanup separately
   authorized;
9. reserves the sole authority cutover for compact Phase 4;
10. requires independent executed evidence and Operator verdicts at every
   correctness boundary.

## Exact Next Trigger

User reviews the exact committed design for corrections. If no correction is
requested, the next authorized action is the writing-plans workflow for the
separate missing plans in Section 11. Implementation remains unauthorized by
this umbrella document alone.
