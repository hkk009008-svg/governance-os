# Compact Kernel Phase 1-2 Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve, review, and integrate the completed compact-kernel Phase-1 baseline and Phase-2 shadow work into one current-main candidate while proving zero authority or effect-eligibility divergence and retaining epoch `0` with writer `v1`.

**Architecture:** Build one isolated integration candidate from a freshly approved `main`, replay a fixed allowlist of source commits instead of merging either feature branch wholesale, and stop for independent verification after Phase 1 before admitting Phase 2. Complete the missing Phase-2 inventory, durable parity artifact, and truth-doc closeout on the integration branch; no compact path becomes authoritative, and merge to `main` and push remain separate decisions.

**Tech Stack:** Git worktrees and exact-commit cherry-picks, Python 3.14 frozen dataclasses, RFC-8785 canonical JSON, JSON fixtures, pytest, Markdown, and the existing Pipeline Lane-V verification machinery.

## Global Constraints

- The approved umbrella source is commit `426744766711d4d6057a4698f5bb19d454ad621d`, especially Phases 0A and 3B of `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md`.
- Phase 0A is a hard gate, not a branch-name convention. Before creating the integration worktree, consume and validate these four fixed committed artifacts: `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md`, `docs/HANDOFF-owner-2026-07-16-capability-phase1.md`, `docs/HANDOFF-owner-2026-07-16-capability-phase2.md`, and `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md`. The aggregate handoff must bind each owner handoff by path, unique introduction commit, Git blob OID, and SHA-256 digest and its rows must agree exactly with the individual artifacts.
- Source Phase-1 baseline is frozen at branch `codex/capability-phase1-closure-2026-07-15`, base `872aa67341e500f1a87f99111611077be3d3fde6`, head `8149df28b45bd2b0b159b243923d0ab439c3d815`. Its exact first-parent range contains only `01d77653d5b7257bcef7c2517d958824eb8ff8a9` and `8149df28b45bd2b0b159b243923d0ab439c3d815`.
- The seven Phase-1 inventory-closure patches are not ancestors of the Phase-1 branch head. They live on branch `codex/capability-phase2-shadow-2026-07-15` after excluded merge `d07fc4d1b6d986c1201f96a00c39249106530f12`, in the exact patch chain `1cd6646bc7c1d52f178493c232539cd0a2511a96..ff44f9a6b17f11719f3da24e2b397f704e4ad8b4`. Replay them only after the two-commit Phase-1 baseline checkpoint; never describe them as Phase-1-head history.
- Source Phase 2 is frozen as the exact branch snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` from `codex/capability-phase2-shadow-2026-07-15`. Phase-1 head `8149df28b45bd2b0b159b243923d0ab439c3d815` is an ancestor through the excluded source merge, but the integration candidate recreates the lawful content order by replaying baseline, inventory closure, then Phase 2 without either merge commit.
- The owner handoff freezes the clean live Phase-2 head `2d5b23f819694f2abe39d4aed6cac318a4f9019d` while excluding its post-snapshot chain `ae24effb8734cd92e418ae2f032724428d0df94a -> 2d5b23f819694f2abe39d4aed6cac318a4f9019d` from this replay. Do not cherry-pick, merge, or compare either descendant as accepted Phase-2 evidence. A later proposal to use either commit requires a replacement owner handoff, revised allowlist, fresh plan review, and independent Operator verdict.
- The Phase-1 worktree must be clean and exactly at `8149df28b45bd2b0b159b243923d0ab439c3d815`. The Phase-2 worktree may have clean descendants after the frozen `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` snapshot, but the owner handoff must enumerate and exclude every such descendant unless the coordinator approves a revised exact snapshot and allowlist. Branch advancement never silently enlarges this plan.
- The authoring-time live branch advanced after the `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` instruction through `ae24effb8734cd92e418ae2f032724428d0df94a` (`chore: classify compact shadow gate`) to clean head `2d5b23f819694f2abe39d4aed6cac318a4f9019d` (`fix: close shadow adapter review gaps`). Both commits overlap Task 4. This plan deliberately does not evaluate or include either post-snapshot commit. The Phase-2 owner/coordinator must keep both explicitly excluded or revise Task 4 and the allowlist after reviewing the full overlap; never duplicate their changes blindly.
- Root ChatGPT-reprepare and compact-kernel WIP must be committed and handed off or explicitly withdrawn before the integration worktree is created. Do not stash, reset, absorb, overwrite, or reconstruct owner WIP.
- Phase 1 is integrated and independently verified before any Phase-2 commit is applied. A Phase-1 FAIL or NITS stops the plan.
- Replay only the three exact source commit allowlists below. Do not merge or cherry-pick `d07fc4d1b6d986c1201f96a00c39249106530f12`, `5aa321fd710e671a616b802fce5bb91b7910774f`, or `b470cd70b1db35b7d18682af6fcb97fccd1a5729`: they are respectively the redundant Phase-1 source merge, unrelated web-research evidence, and a stale merge of `main`.
- A cherry-pick conflict is an ownership event, not permission to choose semantics. Abort the cherry-pick, preserve the source and target blobs, and obtain an exact-path disposition before retrying.
- Version 1 remains the only live authority. `governance.toml` remains epoch `0`, writer `v1`, and declarative-only. No route, mailbox, cursor, lock, ref, provider, effect, activation, or external side effect is authorized.
- Shadow output has no GO, DONE, terminality, verdict, execution, or effect-grant field. Both more-permissive and more-restrictive authority/effect divergences block.
- All ordinary Git and pytest commands use `env -u GIT_INDEX_FILE`. Use explicit pathspecs for staging. Do not reuse the shared index.
- Every newly authored implementation task follows RED, minimal GREEN, focused regression, and one commit. Integration replay retains one cherry-picked commit per exact source patch.
- Execute with `superpowers:subagent-driven-development`: the parent holds this plan and exact range state; one bounded integration worker performs the sequential source replay, one fresh worker performs Task 4, and fresh specification/code-quality reviewers inspect each actual diff. Never run implementers concurrently on the shared integration files.
- The integration branch, merge to `main`, push, source-branch deletion, and worktree cleanup are distinct actions. This plan ends with a reviewed integration candidate and authorizes none of the latter four actions.

---

## Source Commit Allowlists

Apply the Phase-1 baseline in this exact order:

```text
01d77653d5b7257bcef7c2517d958824eb8ff8a9
8149df28b45bd2b0b159b243923d0ab439c3d815
```

After the baseline checkpoint, apply the Phase-1 inventory-closure patch chain in this exact order:

```text
1cd6646bc7c1d52f178493c232539cd0a2511a96
a32c8f6964daa6d7f5c74175d96992e6da3d5e09
fa3df0e91448c250bdd0c6100d180800dc491768
6abb1447dc1d545118fd394b9368f33aff05d67e
1c3e5fdae3f072743155e2345e40cfe7b8b7df9d
09d2e7f768a0324ace1a6de61afc483ce222dd52
ff44f9a6b17f11719f3da24e2b397f704e4ad8b4
```

Apply Phase 2 in this exact order:

```text
6423e951851a4d71c1dd6e3a69e3566a42a2d4cb
e0bf5b8ccb94bd99d69f8920694cb56df2dce6c7
eb3dc7b314008c043287bf223d8e4cab11d3334c
1dd5e5e6f3bbb174c5d41b3502c8667a3e3caf57
6183b3a544d059d62b6398bafef83235e48e8057
7390c576289adf887d3fa1ca05c49468160d25f2
e78f0a080cf8a3de34d37d8f5326c0ff279cd177
ea9b78f6ebb881eb4cdc0d0c2dcab1c5e4f11f59
8e20e059e3ff22a5f6b95774dd2509e94fa7bbd7
a3214d9e381f8cf9995c142cd10bd7933383134a
5837704eb38c444fc3179b8558e2b397352d5cb3
04c049393658e51626e68f28920cd83b934d2fd8
f17d14c684e1e1a6378e52ab8f151070fb710e07
17645ac15aed10b3353317067b83577f38b5870c
3b4642ac8b4f610a3fb6bf8ffad355be42f604e1
0093048446d2e2040349bc60217739f878d3e217
4b72ab8adcd33cb4472a26ab7afe8ad309965a88
a0646668d52c145a24dce1961de3a40694d0adf4
1306c157ac434389444e77935d24db8b3189ee2c
c4aea47bf1c370b89d4f41c79929d9722a44225a
bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
```

## File and Responsibility Map

| File or path | Responsibility |
|---|---|
| `docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md` | Exact source ownership, source heads, included/excluded commits, integration base, reviewed ranges, and final candidate transfer. |
| `governance.toml` | Declarative epoch `0` / writer `v1` mirror only. |
| `scripts/capability_baseline_runtime.py` | Existing Phase-1 five-profile measurement collector. |
| `scripts/compact_state_mapping.py` | Total v1 lifecycle-to-compact semantic mapping. |
| `scripts/capability_reducer.py` | Pure deterministic epoch-0 shadow reducer. |
| `scripts/capability_v1_adapter.py` | Strict normalized v1 adapter and parity CLI. |
| `schemas/route-v2.schema.json` | Synchronized documentation schema for the shadow transition envelope. |
| `tests/fixtures/compact_kernel/v1_surface_inventory.json` | Complete authority surface and helper classification. |
| `tests/fixtures/compact_kernel/v1_to_v2_replay.json` | Full mapping, misuse, and reducer replay manifest. |
| `tests/unit/test_compact_kernel_surface_inventory.py` | Independent owner/helper/import-direction oracle. |
| `tests/unit/test_capability_v1_adapter.py` | Strict adapter, corpus completeness, parity, and durable-artifact tests. |
| `logs/capability-first/phase2b-shadow-parity.json` | Canonical Phase-2 parity report bytes. |
| `logs/capability-first/phase1-2-integration.json` | Content-free integration inputs, source heads, corpus digests, test summaries, and inactive-writer assertion. |
| `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md` | Truthful Phase-1 and Phase-2 completion state; Phase 3 and activation remain unchecked. |
| `ARCHITECTURE.md` | Current reducer/adapter topology and explicit non-authority boundary. |

## Exact Interfaces Retained

The integrated candidate retains these already implemented interfaces without widening them:

```python
def meaning_for(
    domain: str,
    value: str,
    *,
    context: Mapping[str, object],
) -> compact_state_mapping.StateMeaning: ...


def apply_transition(
    state: object,
    event: object,
    *,
    actor: object,
    activation: object,
    resolve_scope: capability_reducer.ScopeResolver,
) -> capability_reducer.KernelState: ...


def reduce_protocol_state(
    events: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
    activation: object,
) -> capability_reducer.KernelReport: ...


def transition_cursor(
    state: object,
    *,
    work_id: object,
    unit_id: object,
) -> tuple[int, int, str]: ...


def adapt_v1_history(
    records: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> tuple[capability_reducer.TransitionEnvelope, ...]: ...
```

`ActivationState` accepts only `epoch=0, mode="shadow"`. `KernelReport` remains observational and contains only mode, state digest, applied/idempotent transition IDs, and units.

### Task 1: Freeze exact owner handoff and create the isolated candidate

**Files:**
- Create: `docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md`
- No production or test file changes.

**Interfaces:**
- Consumes the four fixed Phase-0A handoffs above, including their exact commit/blob/digest references, owner identities, compact-root disposition, frozen Phase-1 head, clean Phase-2 live head, replay snapshot, and explicit post-snapshot exclusions.
- Produces one committed source handoff binding both branch names, the full Phase-1 head, the frozen full Phase-2 snapshot, every later descendant disposition, the three allowlists above, the three excluded history commits, the exact integration base, and clean-worktree evidence.
- Produces integration branch `codex/capability-phase1-2-integration-2026-07-16` in worktree `.worktrees/capability-phase1-2-integration-2026-07-16` from the fresh coordinator-approved `main` head.

- [ ] **Step 0: Validate the fixed Phase-0A handoff chain**

Resolve the aggregate handoff from committed primary `main`, parse exactly one content-addressed reference for each of the three owner handoffs, and validate each referenced commit/path/blob/digest rather than reading current worktree bytes. Require:

- Phase-1 head `8149df28b45bd2b0b159b243923d0ab439c3d815` and its clean-owner evidence;
- Phase-2 clean live head `2d5b23f819694f2abe39d4aed6cac318a4f9019d`, replay snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`, and explicit exclusion of both `ae24effb8734cd92e418ae2f032724428d0df94a` and `2d5b23f819694f2abe39d4aed6cac318a4f9019d` from replay;
- compact-root preservation branch/head and the disposition that its distinct measurements are evidence-only, never silently accepted Phase-1 evidence; and
- identical owner, head, disposition, exclusions, downstream plan, and executed-evidence fields between each individual artifact and the aggregate row.

Prove the aggregate and all three referenced owner-handoff commits are ancestors of the captured current primary `main`. Search commits strictly after the aggregate for any newer artifact containing the same fixed owner-handoff path or recovery-unit ID; any conflicting or superseding handoff blocks until the coordinator reconciles it. Bind the aggregate path/commit/blob/digest and all three validated owner references into the later integration route and final integration handoff. A branch at the expected SHA without this artifact chain does not pass Phase 0A.

- [ ] **Step 1: Recheck source ownership and ancestry**

Run from the primary Pipeline checkout:

```bash
env -u GIT_INDEX_FILE git -C .worktrees/capability-phase1-closure-2026-07-15 status --short --branch
env -u GIT_INDEX_FILE git -C .worktrees/capability-phase2-shadow-2026-07-15 status --short --branch
env -u GIT_INDEX_FILE git rev-parse codex/capability-phase1-closure-2026-07-15
PHASE2_LIVE_HEAD=$(env -u GIT_INDEX_FILE git rev-parse \
  'codex/capability-phase2-shadow-2026-07-15^{commit}')
env -u GIT_INDEX_FILE git show -s --format='%H' \
  bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a \
  "$PHASE2_LIVE_HEAD"
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  8149df28b45bd2b0b159b243923d0ab439c3d815 \
  bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
env -u GIT_INDEX_FILE git log --reverse --first-parent --format='%H' \
  872aa67341e500f1a87f99111611077be3d3fde6..8149df28b45bd2b0b159b243923d0ab439c3d815
```

Expected: both statuses contain no changed paths; Phase-1 HEAD equals `8149df28b45bd2b0b159b243923d0ab439c3d815`; the frozen Phase-2 object prints `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`; both ancestry checks exit `0`; the final command prints exactly `01d77653d5b7257bcef7c2517d958824eb8ff8a9` then `8149df28b45bd2b0b159b243923d0ab439c3d815`. If `PHASE2_LIVE_HEAD` is newer, list every `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a..$PHASE2_LIVE_HEAD` commit in the owner handoff as excluded/unreviewed; do not add it to the replay implicitly.

- [ ] **Step 2: Prove the source commit sets and exclusions**

Run `git show -s --format='%H %P %s'` for every allowlisted commit. Confirm these distinct topology facts instead of claiming one linear source range:

- Phase-1 baseline: `01d77653d5b7257bcef7c2517d958824eb8ff8a9` parents to `872aa67341e500f1a87f99111611077be3d3fde6`; `8149df28b45bd2b0b159b243923d0ab439c3d815` parents to `01d77653d5b7257bcef7c2517d958824eb8ff8a9`.
- Inventory closure: `1cd6646bc7c1d52f178493c232539cd0a2511a96` parents to excluded merge `d07fc4d1b6d986c1201f96a00c39249106530f12`; its six successors are a linear patch chain through `ff44f9a6b17f11719f3da24e2b397f704e4ad8b4`.
- Phase 2: `6423e951851a4d71c1dd6e3a69e3566a42a2d4cb` parents to `ff44f9a6b17f11719f3da24e2b397f704e4ad8b4`; `e0bf5b8ccb94bd99d69f8920694cb56df2dce6c7` parents to excluded merge `b470cd70b1db35b7d18682af6fcb97fccd1a5729`; its successors are linear through `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`.

Then confirm the exclusions:

```bash
env -u GIT_INDEX_FILE git show -s --format='%H %s' \
  d07fc4d1b6d986c1201f96a00c39249106530f12 \
  5aa321fd710e671a616b802fce5bb91b7910774f \
  b470cd70b1db35b7d18682af6fcb97fccd1a5729
```

Expected subjects: Phase-1 merge, bounded-web evidence, and stale main merge respectively. None appears in any replay list. The source-owner handoff must attest that replaying the two post-merge patch roots against the approved current-main integration base does not require either excluded merge's unrelated changes.

- [ ] **Step 3: Create the isolated integration worktree from one captured base**

Use `superpowers:using-git-worktrees`. Immediately before creation, refresh `main`, mailbox/capacity/locks under the live route, obtain coordinator approval for the exact base, then run:

```bash
INTEGRATION_BASE=$(env -u GIT_INDEX_FILE git rev-parse 'main^{commit}')
test -n "$INTEGRATION_BASE"
env -u GIT_INDEX_FILE git worktree add \
  -b codex/capability-phase1-2-integration-2026-07-16 \
  .worktrees/capability-phase1-2-integration-2026-07-16 \
  "$INTEGRATION_BASE"
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase1-2-integration-2026-07-16 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase1-2-integration-2026-07-16 \
  rev-parse 'HEAD^{commit}'
```

Expected: clean new branch; its HEAD equals the captured, approved `INTEGRATION_BASE`. Do not use moving `main` again to define this candidate's ranges.

- [ ] **Step 4: Write both owner sections and the integration-base section**

The handoff must contain these literal bindings and no generalized “latest branch” language:

```markdown
Phase-1 source branch: codex/capability-phase1-closure-2026-07-15
Phase-1 source base: 872aa67341e500f1a87f99111611077be3d3fde6
Phase-1 source head: 8149df28b45bd2b0b159b243923d0ab439c3d815
Phase-1 baseline replay count: 2
Phase-1 inventory-closure patch count: 7
Phase-2 source branch: codex/capability-phase2-shadow-2026-07-15
Phase-2 frozen source snapshot: bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
Phase-2 replay count: 21
Source worktrees: clean
Disposition: exact-commit replay only
Authority: no merge, push, activation, provider, mailbox consume, cursor, lock, or cleanup
```

Add the integration-base line from the integration worktree with this exact derivation before the handoff commit:

```bash
INTEGRATION_BASE=$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')
printf 'Integration base: %s\n' "$INTEGRATION_BASE"
```

Paste the printed line, all three full allowlists, and three explicit exclusions into the handoff. Also copy the validated content-addressed references for the aggregate, compact-root, Phase-1, and Phase-2 Phase-0A handoffs and the route that consumed them. The Phase-1 source owner acknowledges the two-commit baseline. The Phase-2 source owner separately acknowledges the seven closure patches, 21 Phase-2 patches, post-merge patch-root rationale, exact frozen snapshot, and every observed later descendant as excluded or proposed for a separately reviewed revision. Any unenumerated later descendant requires a new owner section and coordinator review.

- [ ] **Step 5: Commit only the handoff as the first integration commit**

```bash
cd .worktrees/capability-phase1-2-integration-2026-07-16
env -u GIT_INDEX_FILE git add -- \
  docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git commit -m "docs: freeze compact phase 1-2 source handoff" -- \
  docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md
```

Expected: the staged list contains exactly the handoff path. Record the resulting full handoff commit SHA; every later review range begins at its parent, the captured `INTEGRATION_BASE`.

### Task 2: Replay and independently close Phase 1

**Files:**
- Replay only the source files named by the two Phase-1 baseline commits and seven inventory-closure patches.
- Modify only on a conflict explicitly dispositioned by the source owner.

**Interfaces:**
- Produces a Phase-1 checkpoint whose tree contains the baseline collector, total mappings, surface inventory, committed 25-run cohort, and declarative epoch-0/v1 mirror.
- The Phase-1 checkpoint is independently reviewed before Phase 2 begins.

- [ ] **Step 1: Replay the exact two-commit Phase-1 baseline**

In the integration worktree, run:

```bash
env -u GIT_INDEX_FILE git cherry-pick \
  01d77653d5b7257bcef7c2517d958824eb8ff8a9
env -u GIT_INDEX_FILE git cherry-pick \
  8149df28b45bd2b0b159b243923d0ab439c3d815
```

Expected: both cherry-picks succeed without conflict. On conflict, run `git cherry-pick --abort` and stop for owner disposition.

- [ ] **Step 2: Establish the Phase-1 baseline checkpoint before closure replay**

```bash
INTEGRATION_BASE=$(LC_ALL=C sed -n 's/^Integration base: \([0-9a-f]\{40\}\)$/\1/p' \
  docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md)
test "$(printf '%s' "$INTEGRATION_BASE" | wc -c | tr -d ' ')" -eq 40
env -u GIT_INDEX_FILE git diff --name-only "$INTEGRATION_BASE"..HEAD
env -u GIT_INDEX_FILE .venv/bin/python scripts/compact_state_mapping.py \
  --check-fixture tests/fixtures/compact_state_mapping/v1.json
env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check
```

Expected: only the setup handoff and two Phase-1 source patches appear; mapping output is `validated 49 mappings across 7 domains`; target binding reports `epoch 0`, `writer v1`, `declarative only`. Capture the full checkpoint SHA in the review request; do not dirty the handoff between setup and final closeout.

- [ ] **Step 3: Replay the seven Phase-1 inventory-closure patches**

Run these commands in order:

```bash
env -u GIT_INDEX_FILE git cherry-pick 1cd6646bc7c1d52f178493c232539cd0a2511a96
env -u GIT_INDEX_FILE git cherry-pick a32c8f6964daa6d7f5c74175d96992e6da3d5e09
env -u GIT_INDEX_FILE git cherry-pick fa3df0e91448c250bdd0c6100d180800dc491768
env -u GIT_INDEX_FILE git cherry-pick 6abb1447dc1d545118fd394b9368f33aff05d67e
env -u GIT_INDEX_FILE git cherry-pick 1c3e5fdae3f072743155e2345e40cfe7b8b7df9d
env -u GIT_INDEX_FILE git cherry-pick 09d2e7f768a0324ace1a6de61afc483ce222dd52
env -u GIT_INDEX_FILE git cherry-pick ff44f9a6b17f11719f3da24e2b397f704e4ad8b4
```

Expected: seven conflict-free patch applications. The excluded `d07fc4d1b6d986c1201f96a00c39249106530f12` merge is absent. A conflict or an unexpected dependency on its first-parent tree stops the plan.

- [ ] **Step 4: Run the complete Phase-1 closure gate**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q \
  tests/unit/test_capability_baseline_runtime.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_target_binding_properties.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check "$INTEGRATION_BASE"..HEAD
```

Expected: all tests pass (the bound source snapshot produced `168 passed`), smoke is `OK`, and diff check is silent. A changed producer constant that breaks mapping parity is a real integration failure; do not regenerate the fixture merely to obtain green.

- [ ] **Step 5: Obtain Phase-1 independent verification**

Create lawful descriptor/request authority for the exact integration-base-to-Phase-1-checkpoint range. The Operator must inspect the changed paths, rerun the Step-4 closure gate, prove the 25-run cohort is committed and internally bound, and return GO/NITS/FAIL. Step 3 is the mutating replay step and is never rerun by the Operator.

Expected: GO is required. NITS or FAIL stops before Task 3. Do not push or merge the Phase-1 checkpoint.

### Task 3: Replay Phase 2 and revalidate the complete shadow corpus

**Files:**
- Replay only the Phase-2 files named by the 21 Phase-2 commits.

**Interfaces:**
- Consumes the verified Phase-1 checkpoint.
- Produces the route-v2 schema, pure reducer, strict v1 adapter, complete replay corpus, and their source plans without importing unrelated branch history.

- [ ] **Step 1: Recheck the Phase-2 source handoff immediately before replay**

```bash
env -u GIT_INDEX_FILE git rev-parse codex/capability-phase2-shadow-2026-07-15
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase2-shadow-2026-07-15 status --short --branch
env -u GIT_INDEX_FILE git show -s --format='%H %P %s' \
  bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
```

Expected: no changed paths; the frozen object is exactly `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` with parent `c4aea47bf1c370b89d4f41c79929d9722a44225a` and subject `fix: bind history references to replay order`. A newer live branch head remains excluded under the owner handoff; if its content should be integrated, stop for a revised plan, exact allowlist, and source review.

- [ ] **Step 2: Replay the 21 Phase-2 patches without either intervening merge**

Run these exact commands in order:

```bash
env -u GIT_INDEX_FILE git cherry-pick 6423e951851a4d71c1dd6e3a69e3566a42a2d4cb
env -u GIT_INDEX_FILE git cherry-pick e0bf5b8ccb94bd99d69f8920694cb56df2dce6c7
env -u GIT_INDEX_FILE git cherry-pick eb3dc7b314008c043287bf223d8e4cab11d3334c
env -u GIT_INDEX_FILE git cherry-pick 1dd5e5e6f3bbb174c5d41b3502c8667a3e3caf57
env -u GIT_INDEX_FILE git cherry-pick 6183b3a544d059d62b6398bafef83235e48e8057
env -u GIT_INDEX_FILE git cherry-pick 7390c576289adf887d3fa1ca05c49468160d25f2
env -u GIT_INDEX_FILE git cherry-pick e78f0a080cf8a3de34d37d8f5326c0ff279cd177
env -u GIT_INDEX_FILE git cherry-pick ea9b78f6ebb881eb4cdc0d0c2dcab1c5e4f11f59
env -u GIT_INDEX_FILE git cherry-pick 8e20e059e3ff22a5f6b95774dd2509e94fa7bbd7
env -u GIT_INDEX_FILE git cherry-pick a3214d9e381f8cf9995c142cd10bd7933383134a
env -u GIT_INDEX_FILE git cherry-pick 5837704eb38c444fc3179b8558e2b397352d5cb3
env -u GIT_INDEX_FILE git cherry-pick 04c049393658e51626e68f28920cd83b934d2fd8
env -u GIT_INDEX_FILE git cherry-pick f17d14c684e1e1a6378e52ab8f151070fb710e07
env -u GIT_INDEX_FILE git cherry-pick 17645ac15aed10b3353317067b83577f38b5870c
env -u GIT_INDEX_FILE git cherry-pick 3b4642ac8b4f610a3fb6bf8ffad355be42f604e1
env -u GIT_INDEX_FILE git cherry-pick 0093048446d2e2040349bc60217739f878d3e217
env -u GIT_INDEX_FILE git cherry-pick 4b72ab8adcd33cb4472a26ab7afe8ad309965a88
env -u GIT_INDEX_FILE git cherry-pick a0646668d52c145a24dce1961de3a40694d0adf4
env -u GIT_INDEX_FILE git cherry-pick 1306c157ac434389444e77935d24db8b3189ee2c
env -u GIT_INDEX_FILE git cherry-pick c4aea47bf1c370b89d4f41c79929d9722a44225a
env -u GIT_INDEX_FILE git cherry-pick bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
```

Do not cherry-pick `5aa321fd710e671a616b802fce5bb91b7910774f` or `b470cd70b1db35b7d18682af6fcb97fccd1a5729` between the first two commands, and do not cherry-pick `d07fc4d1b6d986c1201f96a00c39249106530f12` anywhere. `6423e951851a4d71c1dd6e3a69e3566a42a2d4cb` is the direct child of the inventory-closure tip; `e0bf5b8ccb94bd99d69f8920694cb56df2dce6c7` is replayed as a patch against the approved integration tree after the two excluded source-history commits.

Expected: linear replay with no merge commit and no conflict. Abort and stop on the first conflict.

- [ ] **Step 3: Run the complete Phase-2 corpus gate**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_route_v2_schema_sync.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_route_manifest.py \
  tests/unit/test_route_schema_sync.py \
  tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check
```

Expected: all tests pass (the clean source head `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` produced `456 passed`); the CLI exits `0`; all four blocking divergence arrays are empty; `specialized_event_ids` is empty; counts are 49 mapping rows, 8 Phase-2 misuse vectors, 3 deferred Phase-3 vectors, 19 reducer vectors, and 31 permutations; epoch is `0`, writer is `v1`, declarative only.

- [ ] **Step 4: Prove divergence detection is non-vacuous**

Run the existing mutation selectors that independently alter `_ADAPTER_RULES` in each direction and remove one manifest case. Expected: more-permissive, more-restrictive, effect-permissive, effect-restrictive, and missing-case mutations each fail their intended assertion; restore the source and rerun Step 3 green.

### Task 4: Complete Phase-2 classification and durable parity evidence

**Files:**
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `tests/unit/test_capability_v1_adapter.py`
- Create: `logs/capability-first/phase2b-shadow-parity.json`
- Create: `logs/capability-first/phase1-2-integration.json`
- Modify: `ARCHITECTURE.md`
- Modify: `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
- Modify: `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md`

**Interfaces:**
- Adds inventory component `compact_shadow_reducer_and_v1_adapter` with no writer.
- Freezes an exhaustive producer-class ledger derived from every component whose `writer_paths` is nonempty; every `(component_id, writer_path)` producer pair appears exactly once and every class has an explicit Phase-3/Phase-4 disposition.
- Pins fresh parity-report bytes and integration input metadata.
- Records Phase 2 as `candidate` / `pending_operator_go`; no Phase-2 completion box is checked until the binding GO exists.

- [ ] **Step 1: Write the failing inventory ownership tests**

Add `compact_shadow_reducer_and_v1_adapter` to `COMPONENT_IDS` and `READ_ONLY_COMPONENT_IDS`. Add these exact independent owner bindings:

```python
REQUIRED_PHASE2_PRODUCTION_MODULES = {
    "scripts/capability_reducer.py",
    "scripts/capability_v1_adapter.py",
}

REQUIRED_SURFACE_OWNERS.update({
    "schemas/route-v2.schema.json": "compact_shadow_reducer_and_v1_adapter",
    "scripts/capability_reducer.py": "compact_shadow_reducer_and_v1_adapter",
    "scripts/capability_v1_adapter.py": "compact_shadow_reducer_and_v1_adapter",
    "tests/fixtures/compact_kernel/v1_to_v2_replay.json": (
        "compact_shadow_reducer_and_v1_adapter"
    ),
    "tests/fixtures/compact_kernel/v2_replay_vectors.json": (
        "compact_shadow_reducer_and_v1_adapter"
    ),
})
```

Add exact assertions that the component's `writer_paths == []`, reducer is `runtime_core`, adapter is `historical_adapter`, only adapter `main` is `cli_entrypoint/keep_documented_cli`, adapter imports reducer, and reducer does not import adapter.

Freeze this exact producer-class ledger from the `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` inventory. Each row is normative and must be represented in the fixture with `component_id`, exact ordered `writer_paths` copied from its frozen component, `writer_class`, `phase3_disposition`, and `phase4_disposition`:

| Component ID | Writer class | Phase-3 disposition | Phase-4 disposition |
|---|---|---|---|
| `target_binding` | `configuration_mirror_writer` | `retain_v1_declarative_only` | `fence_and_change_only_in_preparation_commit` |
| `markdown_routes_and_mailbox_writer` | `coordination_authority_writer` | `retain_v1_and_add_inactive_compact_caller` | `fence_and_select_exactly_one_store` |
| `typed_route_compatibility_canary` | `non_authoritative_fixture_writer` | `retain_non_authoritative` | `retain_non_authoritative` |
| `capacity_reducer_and_packet_state_telemetry` | `capacity_packet_writer` | `retain_packet_writer_retire_packet_state_reader` | `fence_and_select_exactly_one_store` |
| `effectiveness_telemetry` | `non_authoritative_measurement_writer` | `retain_non_authoritative` | `retain_non_authoritative` |
| `capability_receipt_recording` | `post_effect_receipt_writer` | `retain_v1_and_add_inactive_effect_caller` | `fence_and_select_specialized_store` |
| `verification_authority_and_publication` | `verification_report_writer` | `retain_v1_and_add_inactive_verification_caller` | `fence_and_select_specialized_store` |
| `chatgpt_guard_and_browser_executor` | `advisory_attempt_state_writer` | `retain_v1_and_add_inactive_advisory_caller` | `fence_intent_and_keep_terminal_store` |
| `opus_reservation_and_bridge` | `advisory_receipt_writer` | `retain_v1_and_add_inactive_advisory_caller` | `fence_intent_and_keep_terminal_store` |
| `capability_baseline_runtime_collector` | `non_authoritative_benchmark_writer` | `retain_non_authoritative` | `retain_for_same_host_measurement` |
| `signed_bus_event_and_cursor_runtime` | `separate_threeway_authority_writer` | `retain_separate_toolchain_and_audit_bridge` | `fence_any_shared_mailbox_cursor_bridge` |
| `live_v1_status_and_runtime_readers` | `optional_local_status_writer` | `retain_non_authoritative_local_output` | `retain_non_authoritative_local_output` |
| `coordination_lock_effects` | `user_gated_lock_writer` | `retain_outside_compact_route_authority` | `retain_separately_authorized_and_audit` |
| `codex_runtime_and_hook_adapter` | `runtime_presence_and_index_writer` | `retain_outside_compact_route_authority` | `retain_outside_compact_route_authority` |

The test computes the set of all components with nonempty `writer_paths`, compares it to these 14 component IDs, compares every row's writer paths byte-for-byte with its component, rejects duplicate/missing `(component_id, writer_path)` pairs, and rejects any unknown or empty disposition. The only intentionally shared physical paths in the frozen snapshot are `coordination/mailbox/sent` (the Markdown-route and verification-publication classes) and `coordination/mailbox/seen` (the human-mailbox and signed-bus bridge classes); both appearances require an explicit shared-domain marker and later converge under the same Phase-4 fence. Any other cross-class shared path is RED. A new writer-bearing component or path is RED until the owner classifies it explicitly; changing the frozen source requires the descendant-disposition gate rather than silently regenerating this ledger. Read-only components, including `compact_shadow_reducer_and_v1_adapter`, must not appear in the producer ledger.

- [ ] **Step 2: Run inventory RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q \
  tests/unit/test_compact_kernel_surface_inventory.py
```

Expected: failure naming the missing component/owners, not a JSON parse or import error.

- [ ] **Step 3: Add the exact read-only inventory component**

Append this component object, preserving the fixture's existing ordering conventions:

```json
{
  "id": "compact_shadow_reducer_and_v1_adapter",
  "authority_status": "non_authoritative_read_only_shadow_compatibility",
  "source_paths": [
    "schemas/route-v2.schema.json",
    "scripts/capability_reducer.py",
    "scripts/capability_v1_adapter.py",
    "tests/fixtures/compact_kernel/v1_to_v2_replay.json",
    "tests/fixtures/compact_kernel/v2_replay_vectors.json"
  ],
  "reader_paths": [
    "tests/fixtures/compact_state_mapping/v1.json",
    "tests/fixtures/compact_kernel/v1_misuse_vectors.json",
    "tests/fixtures/compact_kernel/v1_to_v2_replay.json",
    "tests/fixtures/compact_kernel/v2_replay_vectors.json"
  ],
  "writer_paths": [],
  "executor_boundary": "Epoch-0 shadow reduction is in-memory and observational; it cannot grant GO, DONE, terminality, effect eligibility, execution, or activation.",
  "default_helper_class": "historical_adapter",
  "module_rules": [
    {
      "path": "scripts/capability_reducer.py",
      "default_helper_class": "runtime_core"
    },
    {
      "path": "scripts/capability_v1_adapter.py"
    }
  ],
  "symbol_overrides": [
    {
      "symbol": "scripts.capability_v1_adapter.main",
      "helper_class": "cli_entrypoint",
      "disposition": "keep_documented_cli"
    }
  ]
}
```

- [ ] **Step 4: Run inventory GREEN and reverse-import mutation**

Run the Step-2 command. Expected: pass. In a disposable copy, add `import capability_v1_adapter` to the reducer and prove the reverse-import assertion fails; restore and rerun green.

- [ ] **Step 5: Persist the canonical parity artifact and pin its bytes**

Run the adapter CLI and capture its single canonical JSON line. Add those exact bytes with `apply_patch` to `logs/capability-first/phase2b-shadow-parity.json`. Add a test that calls the same rendering path and compares `read_bytes()` byte-for-byte.

Expected source snapshot values include:

```json
{
  "mode": "shadow",
  "report_digest": "sha256:268968a074d056d62b4115ff1b4b312c73088f6055964dadb7fbaa445d3358be",
  "specialized_event_ids": []
}
```

If integration with current producers changes a bound source digest, stop and review the exact producer change; do not copy the old digest or bless a new one without replay/mutation evidence.

- [ ] **Step 6: Add the integration evidence object**

Create `logs/capability-first/phase1-2-integration.json` with exact fields:

```json
{
  "schema": "compact-kernel-phase1-2-integration/v1",
  "mode": "candidate",
  "phase1_source_base": "872aa67341e500f1a87f99111611077be3d3fde6",
  "phase1_source_head": "8149df28b45bd2b0b159b243923d0ab439c3d815",
  "phase1_baseline_replay_count": 2,
  "phase1_inventory_closure_source_tip": "ff44f9a6b17f11719f3da24e2b397f704e4ad8b4",
  "phase1_inventory_closure_replay_count": 7,
  "phase2_source_head": "bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a",
  "phase2_replay_count": 21,
  "epoch": 0,
  "writer": "v1",
  "authority": "declarative_only",
  "phase1_gate": "go",
  "phase2_gate": "pending_operator_go",
  "blocking_authority_divergences": 0,
  "blocking_effect_divergences": 0,
  "specialized_route_events": 0,
  "merge_authorized": false,
  "push_authorized": false,
  "activation_authorized": false
}
```

Do not put a future candidate SHA or Operator verdict into this pre-review artifact. The Git commit and later verification report bind those facts.

- [ ] **Step 7: Update truth documents as a pending candidate**

In the capability guide, leave both Phase-2 completion boxes unchecked and label the exact implementation range, parity artifact, focused command, and epoch-0/v1 result `candidate / pending Operator GO`. In the Phase-2B plan, leave completion status pending while recording only reproduced candidate facts. Update `ARCHITECTURE.md` with fresh symbol anchors for `reduce_protocol_state`, `transition_cursor`, and `adapt_v1_history`; state the adapter-to-reducer dependency and the absence of live callers/writers without claiming Phase-2 completion.

- [ ] **Step 8: Run Task-4 verification and commit**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_route_v2_schema_sync.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_route_manifest.py \
  tests/unit/test_route_schema_sync.py \
  tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all pass, parity CLI exits `0`, target binding prints epoch `0` / writer `v1` / declarative-only, and smoke is `OK`.

```bash
env -u GIT_INDEX_FILE git add -- \
  tests/fixtures/compact_kernel/v1_surface_inventory.json \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_capability_v1_adapter.py \
  logs/capability-first/phase2b-shadow-parity.json \
  logs/capability-first/phase1-2-integration.json \
  ARCHITECTURE.md \
  docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md \
  docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md
env -u GIT_INDEX_FILE git commit -m "docs: prepare compact shadow phase 2 candidate"
```

### Task 5: Independent Phase-2 review and integration-candidate handoff

**Files:**
- Modify: `docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md`
- Create only after separately authorized local integration: `docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md`
- No production or test changes after the reviewed candidate.

**Interfaces:**
- Produces one exact Operator GO/NITS/FAIL for the integration-base-to-Phase-2-candidate range.
- Produces a docs-only final handoff that names the GO artifact and explicitly withholds merge/push/activation authority.

- [ ] **Step 1: Run final candidate verification**

Run the complete Task-4 command plus:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/compact_state_mapping.py \
  --check-fixture tests/fixtures/compact_state_mapping/v1.json
INTEGRATION_BASE=$(LC_ALL=C sed -n 's/^Integration base: \([0-9a-f]\{40\}\)$/\1/p' \
  docs/HANDOFF-director-2026-07-16-capability-phase1-2-integration.md)
test "$(printf '%s' "$INTEGRATION_BASE" | wc -c | tr -d ' ')" -eq 40
env -u GIT_INDEX_FILE git diff --name-only "$INTEGRATION_BASE"..HEAD
env -u GIT_INDEX_FILE git log --reverse --format='%H %P %s' \
  "$INTEGRATION_BASE"..HEAD
```

Expected: no merge commit. The first candidate commit is the setup handoff. The next source-derived subjects are the two Phase-1 baseline subjects and seven inventory-closure subjects in the three allowlists' exact order. The handoff records the exact Phase-1 verify-request/report authority commits inserted after the closure tip and before `docs: plan compact reducer phase 2a`. The next 21 source-derived subjects are the Phase-2 allowlist in exact order, followed by the single `docs: prepare compact shadow phase 2 candidate` commit. Final-candidate verify-request/report commits are not yet present at this step; the docs-only GO finalization commit is also not yet present. No commit has source SHA `d07fc4d1b6d986c1201f96a00c39249106530f12`, `5aa321fd710e671a616b802fce5bb91b7910774f`, or `b470cd70b1db35b7d18682af6fcb97fccd1a5729`, and no unexpected non-protocol commit appears.

- [ ] **Step 2: Obtain one fresh independent actual-diff review**

The reviewer inspects the exact final candidate range and answers:

> Can source omission, conflict resolution, mixed-version input, actor/scope inference, stale or duplicate identity, specialized-state collapse, corpus omission, either parity direction, reducer I/O, adapter reverse-import, or an activation/effect surface escape the epoch-0 read-only shadow boundary?

Any Critical or Important finding blocks Lane V and is corrected with a focused RED/GREEN test under a fresh authorized commit. Do not repeat this question on an unchanged range.

- [ ] **Step 3: Request and receive the binding Operator verdict**

Create the lawful descriptor/request for the exact current candidate. The Operator reruns the final commands, confirms Phase 1 preceded Phase 2, verifies both source handoffs/heads, and emits one GO/NITS/FAIL.

Expected: GO is required for candidate completion. GO authorizes neither merge nor push.

- [ ] **Step 4: Finalize Phase-2 status and the handoff in one docs-only commit**

Only after GO, check the two Phase-2 guide boxes, mark the Phase-2B plan tasks complete, and append the integration base, setup-handoff commit SHA, two-commit Phase-1 baseline checkpoint SHA, seven-patch Phase-1 closure SHA, exact Phase-1 verification request/report commit SHAs and paths, Phase-2 candidate/reviewed SHA, exact final Operator report path/verdict, parity report digest, and current epoch/writer result. The candidate evidence JSON remains immutable with `mode=candidate` and `phase2_gate=pending_operator_go`; the committed Operator report and this docs-only finalization carry the later GO fact. End with:

```text
Integration candidate: reviewed and handed off
Main merge: not authorized by this handoff
Push: not authorized by this handoff
Activation: not authorized by this handoff
Source branch/worktree cleanup: not authorized by this handoff
```

Commit only the guide, Phase-2B plan, this integration plan if its checkboxes are maintained, and the handoff with subject `docs: finalize compact shadow phase 2 after GO`. Do not change production, tests, fixtures, or logs. This is the final docs-only commit after the reviewed candidate and its final verification authority/report commits; it is not included in the reviewed production head and does not trigger duplicate Lane V for the unchanged production candidate.

- [ ] **Step 5: Obtain separate integration authority and freeze the integrated main**

The umbrella Phase-1/2 exit gate requires accepted local integration, not merely a reviewed side branch. After the final handoff commit, stop for a fresh explicit user-principal authorization naming one local integrator and binding the exact integration base, reviewed production head, docs-only finalization head, target primary `main` head, and action `local integration only`. It grants no push, activation, cleanup, or conflict resolution. The coordinator records but cannot create or execute this authority.

The named integrator refreshes `main`, mail, capacity, locks, both worktrees, and remote divergence; proves the candidate/report/finalization chain unchanged; and integrates locally. A conflict, non-fast-forward surprise, overlapping newer main edit, or changed path stops for a revised reviewed range rather than an improvised resolution. On the merged tree rerun the complete Phase-1 and Phase-2 focused gates, full unit suite, parity/corpus commands, smoke, epoch-0/writer-v1 assertions, exact source-exclusion scan, and diff check. Capture the exact integrated code SHA and prove the reviewed production head is its ancestor with no post-GO production edit.

Only after those gates pass, the coordinator creates and commits only `docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md`. It binds the user authorization correlation, named integrator, candidate base/reviewed/finalization heads, Operator GO path/commit, exact integrated code SHA, merged-tree command results, the four Phase-0A handoff references, excluded `ae24eff...` and `2d5b23f...` descendants, epoch `0`, writer `v1`, and push/activation/cleanup status `not-authorized`. Capture the handoff commit/blob/digest and require its commit changes only that path. Phase 3 must branch from this exact containing main commit; it may not substitute the earlier unmerged candidate.

## Stop Conditions

- Either source worktree is dirty, a frozen source object is missing, or the owner handoff does not explicitly exclude/disposition every descendant after the frozen Phase-2 snapshot.
- Root WIP overlaps an integration path without an exact-blob disposition.
- A cherry-pick conflicts or introduces an excluded commit/path.
- Phase-1 mapping, cohort, inventory, or target-mirror tests fail.
- Phase 2 begins before Phase-1 independent GO.
- Corpus source sets differ without a reviewed producer change.
- Any blocking divergence, specialized route event, reducer I/O, reverse import, active writer, nonzero epoch, or live caller appears.
- Independent review or Operator returns issues/NITS/FAIL.
- The user has not separately authorized the exact local integration, the named integrator differs, or merged-tree verification fails.
- Any step would require mailbox consumption, lock/ref mutation, provider call, effect execution, merge to `main`, push, activation, or cleanup not separately authorized.

## Completion Gate

The plan is complete only when the exact source snapshots and descendant dispositions are preserved, Phase 1 and Phase 2 each have independent GO on the current integration history, the canonical parity artifact has zero authority/effect divergence, the candidate remains epoch `0`/writer `v1`, the final candidate handoff names the exact reviewed head, and the separately authorized local integration plus merged-tree gate are bound by `docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md`. Push, activation, and cleanup remain separate.
