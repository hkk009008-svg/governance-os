# Recovery Owner/WIP Disposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve every recovery-relevant dirty blob on an owner-controlled branch, freeze the committed branch-only ranges, and publish exact owner handoffs so later routes can start without overwriting, stashing, resetting, or silently absorbing work.

**Architecture:** The coordinator first records and routes ownership but never edits behavior-changing files. Each existing owner performs one sequential preservation action: root WIP is extracted by an in-place branch switch and exact pathspec commit, committed snapshots are frozen by full SHA, and the dirty control-plane worktree moves to a preservation branch before its exact blobs are committed. Owner handoffs remain distinct from the final coordinator disposition record; no preservation commit or newly observed descendant is integration or correctness authority.

**Tech Stack:** Git branches and worktrees, Markdown handoffs, Python 3.14, pytest, Pipeline capacity/mailbox guards, and exact Git blob identities.

## Global Constraints

- The authority source is `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` at commit `426744766711d4d6057a4698f5bb19d454ad621d`.
- This plan resolves Phase 0A only. It grants no product implementation, integration, merge, push, provider call, canary, activation, publication, branch deletion, worktree removal, cursor consume, or lock mutation.
- The coordinator may inspect, route, reconcile, and commit coordinator-owned handoff state. It must not author, stage, commit, amend, restore, or withdraw another owner's production WIP.
- Every ordinary Git and pytest command starts with `env -u GIT_INDEX_FILE`. Use exact pathspecs and inspect the staged set before every commit.
- Do not use `git stash`, `git reset`, `git restore`, `git checkout --`, `git clean`, history rewriting, patch-copying, or a bulk working-tree copy. Root WIP leaves `main` only through an owner-controlled branch switch, exact commit, and switch back to `main`.
- Only one owner may manipulate the shared root at a time. Before each branch switch, refresh HEAD, mailbox bodies, worktrees, locks, and root status; stop if another seat is writing or the relevant byte set changed.
- A preservation branch is not an accepted implementation branch. Its commit records bytes and provenance only; later implementation plans still require their own reviews, Lane-V authority, Operator verdict, and integration decision.
- Owner handoffs must name the exact full source base, implementation or preservation head, branch, path set, Git blob IDs, tests actually executed, known failures, exclusions, and next lawful trigger. A branch name, clean status, or short SHA alone is insufficient.
- A clean branch freezes only when its owner handoff is committed. Any later branch advancement invalidates the handoff and blocks downstream review until the owner publishes a replacement.
- Execution order inside Phase 0A is intentionally non-numeric for throughput: after Task 1, execute the read-only checks and handoff commit in Task 6 before Tasks 2-5. Once the exact `16c4f83a...` Opus owner handoff is committed and the Opus correction route has consumed its path/commit/blob/digest, the separately routed `Q` append may proceed in the Stage-A worktree while disjoint root and control-plane preservation continues. That exact-old, route-bound `Q` advancement does not retroactively erase the handoff's predecessor evidence; any unbound or different Stage-A advancement still invalidates it and stops the route.
- Hot-tree refresh on 2026-07-16 observed eight Phase-2 paths change at `ae24effb8734cd92e418ae2f032724428d0df94a`, then become one clean direct-child commit `2d5b23f819694f2abe39d4aed6cac318a4f9019d` (`fix: close shadow adapter review gaps`). The eight paths are `ARCHITECTURE.md`, `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md`, `logs/capability-first/phase2b-shadow-parity.json`, `scripts/capability_v1_adapter.py`, `tests/fixtures/compact_kernel/v1_to_v2_replay.json`, `tests/fixtures/compact_kernel/v2_replay_vectors.json`, `tests/unit/test_capability_reducer_replay.py`, and `tests/unit/test_capability_v1_adapter.py`. This proves preservation, not ownership or acceptance. No durable mailbox artifact identified the commit's current owner or supplied Operator GO; stop for the user-principal to name the owner if durable evidence remains absent.
- The ambient untracked `.agents/` teamwork-preview trees, `.codex/runtime/`, `ORIGINAL_REQUEST.md`, and `PROJECT.md` are outside this recovery plan. They remain byte-for-byte untouched and excluded from every staged pathspec; their eventual cleanup needs a separate owner disposition and cleanup authorization.
- The current Stage-A range remains `40fd0a5e43c6b28330ced9ddffe01483cde42b65..16c4f83aef4130d977a91d623a9254c4fd46980a`, with immutable implementation commits `56091d107382abfe9f06df1aa4cd003d71be7b5e` and `16c4f83aef4130d977a91d623a9254c4fd46980a`. This plan adds no commit to that branch.
- Commit permission for a preservation or handoff commit does not imply merge, push, publication, cleanup, or later implementation permission.

---

## File And Branch Structure

### Durable handoffs created by this plan

- Create: `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md` — exact preservation branch and local-reprepare blob manifest.
- Create: `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md` — exact root compact preservation branch, canonical Phase-2 overlap, and evidence-only log disposition.
- Create: `docs/HANDOFF-owner-2026-07-16-capability-phase1.md` — freeze of `codex/capability-phase1-closure-2026-07-15` at `8149df28b45bd2b0b159b243923d0ab439c3d815`.
- Create: `docs/HANDOFF-owner-2026-07-16-capability-phase2.md` — freeze of committed canonical branch `codex/capability-phase2-shadow-2026-07-15` at clean live head `2d5b23f819694f2abe39d4aed6cac318a4f9019d`, integration snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`, and explicit exclusion/disposition of post-snapshot commits `ae24eff...` and `2d5b23f...`.
- Create: `docs/HANDOFF-owner-2026-07-16-control-plane-wip.md` — preservation-only child branch for the nine parked Task2U working blobs.
- Create: `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md` — owner freeze of the clean Stage-A diagnostic range without branch advancement.
- Create: `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md` — aggregate disposition and downstream ownership gate.
- Create before compact convergence: `docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md` — exact user-directed terminal integrate-or-withdraw result for the preserved ChatGPT range.

### Branches

- Create: `codex/chatgpt-local-reprepare-flexibility-2026-07-16` — owner-preserved ChatGPT local-reprepare implementation and its untracked plan.
- Create: `codex/recovery-compact-root-wip-2026-07-16` — preservation-only root compact and measurement blobs; it is not the canonical integration branch.
- Retain and freeze: `codex/capability-phase1-closure-2026-07-15` at `8149df28b45bd2b0b159b243923d0ab439c3d815`.
- Retain and freeze: `codex/capability-phase2-shadow-2026-07-15` at live head `2d5b23f819694f2abe39d4aed6cac318a4f9019d`; this is the canonical compact implementation branch. Downstream replay remains frozen at `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`. Neither post-snapshot commit `ae24eff...` nor `2d5b23f...` enters replay without a revised allowlist, dedicated review, and replacement handoff.
- Create from the parked worktree without changing the old ref: `codex/recovery-control-plane-wip-2026-07-16` — preservation-only control-plane WIP.
- Retain and freeze: `codex/director2-opus-transport-stage-a` at `16c4f83aef4130d977a91d623a9254c4fd46980a`.

### Recovery units

| Unit | Exact source | Required disposition |
|---|---|---|
| `ROOT-CHATGPT` | Shared-root ChatGPT changes plus `docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md` | Exact preservation branch and owner handoff; no provider execution |
| `ROOT-COMPACT` | Live dirty composite `ARCHITECTURE.md` and `logs/capability-first/`, plus clean comparison evidence from the compact mirror, mappings, fixtures, and tests | Preserve only the dirty doc/log roots; record four checkpoint matches and three contained-`main` advances; retain distinct logs as evidence-only |
| `CAP-PHASE1` | Clean branch/worktree at `8149df28b45bd2b0b159b243923d0ab439c3d815` | Exact owner freeze and handoff |
| `CAP-PHASE2` | Clean live head `2d5b23f819694f2abe39d4aed6cac318a4f9019d`; replay snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`; post-snapshot chain `ae24eff... -> 2d5b23f...` | Freeze the full live chain, name its owner and executed evidence, and exclude both post-snapshot commits from current replay pending revised allowlist and review |
| `CONTROL-PLANE` | Dirty nine-path worktree based at `6983673db60bff0d21548a90ab1db2fcbbfa377a` | Freshly routed preservation branch and owner handoff; never merge wholesale |
| `OPUS-STAGE-A` | Clean branch at `16c4f83aef4130d977a91d623a9254c4fd46980a` | Exact owner freeze and handoff; no branch commit and zero provider attempts |

---

### Task 1: Establish the coordinator inventory and exclusive-owner sequence

**Files:**

- Read: `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md`
- Read: newest coordinator and recovery-unit mailbox bodies
- Read: `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director-task2u-fail-closed-closure.json`
- Read: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-director2-diagnostics.json`
- No file mutation in this task

**Interfaces:**

- Consumes: current shared-root status, worktree heads/statuses, mailbox ownership, locks, and the six recovery units above.
- Produces: one in-memory sequencing decision naming one current owner per unit and proving that only the named owner will touch each source checkout. It produces no route or commit by itself.

- [ ] **Step 1: Refresh governed state and read the relevant bodies**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -8
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE git worktree list --porcelain
find coordination/locks -type f ! -name .gitkeep -print
```

Expected: capacity and doctor pass, the current worktrees are enumerated, and the lock command prints nothing. Read every newer coordinator, Director2 Stage-A, capability-owner, and control-plane owner body. If a newer artifact changes ownership or a lock exists, stop before any branch switch.

- [ ] **Step 2: Capture the exact root and parked-worktree path inventories**

Run:

```bash
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase1-closure-2026-07-15 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase2-shadow-2026-07-15 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/opus-transport-first-stage-a-director2 \
  status --short --branch
```

Expected: root shows the known ChatGPT and compact WIP plus excluded ambient untracked paths; control-plane shows exactly the nine paths named in Task 5; Phase 1 and Opus are clean; Phase 2 is clean at `2d5b23f...`. Any additional or changed recovery-target path blocks execution until its owner classifies it.

- [ ] **Step 3: Confirm no preservation branch already exists**

Run:

```bash
! env -u GIT_INDEX_FILE git show-ref --verify --quiet \
  refs/heads/codex/chatgpt-local-reprepare-flexibility-2026-07-16
! env -u GIT_INDEX_FILE git show-ref --verify --quiet \
  refs/heads/codex/recovery-compact-root-wip-2026-07-16
! env -u GIT_INDEX_FILE git show-ref --verify --quiet \
  refs/heads/codex/recovery-control-plane-wip-2026-07-16
```

Expected: exit `0` from all three negated checks. If a ref exists, inspect its full head and committed handoff; reuse it only when the exact blobs and owner evidence already satisfy this plan. Never force-move or overwrite it.

- [ ] **Step 4: Record the subagent and owner decision before mutation**

The coordinator records that preservation must be sequential because all root units share one checkout. Assign `ROOT-CHATGPT`, `ROOT-COMPACT`, `CAP-PHASE1`, `CAP-PHASE2`, `CONTROL-PLANE`, and `OPUS-STAGE-A` to their actual current owners from durable evidence. If durable evidence cannot identify an owner, stop and ask the user-principal to name one; do not infer ownership from file contents or process IDs.

### Task 2: Extract and hand off `ROOT-CHATGPT`

**Files:**

- Preserve on `codex/chatgpt-local-reprepare-flexibility-2026-07-16`:
  `.agents/skills/chatgpt-pro-consultation/SKILL.md`
- Preserve on the same branch: `.agents/skills/four-seat-protocol/SKILL.md`, `.agents/skills/seat-coordinator/SKILL.md`, `.agents/skills/seat-director/SKILL.md`, `.agents/skills/seat-operator/SKILL.md`
- Preserve on the same branch: `.codex/agents/protocol-coordinator.toml`, `.codex/agents/protocol-director.toml`, `.codex/agents/protocol-operator.toml`, `.codex/agents/readiness-bridge.toml`
- Preserve on the same branch: `AGENTS.md`, `docs/protocol/codex/continuation.md`
- Preserve on the same branch: `scripts/chatgpt_pro_consult.py`, `scripts/codex_protocol_model.py`
- Preserve on the same branch: `tests/unit/test_chatgpt_pro_consult.py`, `tests/unit/test_protocol_prompt_sync.py`
- Preserve on the same branch: `docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md`
- Create on `main`: `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md`

**Interfaces:**

- Consumes: the exact dirty/untracked bytes in the sixteen paths above and the current owner assignment.
- Produces: one frozen preservation branch, one exact owner handoff, and a root in which all sixteen paths are clean. The branch remains unapproved for shipping until a dedicated approved design and writing-plans-compliant plan exist.

- [ ] **Step 1: Recheck only this unit and the shared-root branch**

Run:

```bash
env -u GIT_INDEX_FILE git branch --show-current
env -u GIT_INDEX_FILE git status --short -- \
  .agents/skills/chatgpt-pro-consultation/SKILL.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/readiness-bridge.toml \
  AGENTS.md docs/protocol/codex/continuation.md \
  scripts/chatgpt_pro_consult.py scripts/codex_protocol_model.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md
```

Expected: branch is `main`, and status lists only the sixteen named paths. Any extra path within the unit or a non-`main` branch is a hard stop.

- [ ] **Step 2: Switch the shared root to the owner preservation branch**

Run:

```bash
env -u GIT_INDEX_FILE git switch -c \
  codex/chatgpt-local-reprepare-flexibility-2026-07-16
```

Expected: the new branch is created at the then-current full `main` head and every dirty/untracked byte remains present. No other owner may use the shared root until Step 7 completes.

- [ ] **Step 3: Stage exactly the local-reprepare unit**

Run:

```bash
env -u GIT_INDEX_FILE git add -- \
  .agents/skills/chatgpt-pro-consultation/SKILL.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/readiness-bridge.toml \
  AGENTS.md docs/protocol/codex/continuation.md \
  scripts/chatgpt_pro_consult.py scripts/codex_protocol_model.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git diff --cached --check
```

Expected: the staged-name output is exactly the sixteen paths listed under **Files**, and `git diff --cached --check` prints nothing. `ARCHITECTURE.md`, compact paths, logs, and ambient untracked paths remain unstaged.

- [ ] **Step 4: Execute the preservation-level checks**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: both commands pass. Record the exact pass counts in the owner handoff. Failure does not erase the branch candidate; record it as a known failure and route a later correction instead of modifying scope here.

- [ ] **Step 5: Commit the exact preserved bytes**

Run:

```bash
env -u GIT_INDEX_FILE git commit -m \
  "fix(consult): preserve local reprepare correction"
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
```

Expected: one commit containing exactly the sixteen paths and no provider or runtime-state artifact.

- [ ] **Step 6: Capture the branch and blob evidence**

Run:

```bash
env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r HEAD
env -u GIT_INDEX_FILE git ls-tree -r HEAD -- \
  .agents/skills/chatgpt-pro-consultation/SKILL.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/readiness-bridge.toml \
  AGENTS.md docs/protocol/codex/continuation.md \
  scripts/chatgpt_pro_consult.py scripts/codex_protocol_model.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md
```

Expected: one full commit SHA, the exact sixteen-path change set, and one mode/type/blob-ID line per path. Preserve this output for the handoff.

- [ ] **Step 7: Return the shared root to `main` without touching other WIP**

Run:

```bash
env -u GIT_INDEX_FILE git switch main
env -u GIT_INDEX_FILE git status --short -- \
  .agents/skills/chatgpt-pro-consultation/SKILL.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/readiness-bridge.toml \
  AGENTS.md docs/protocol/codex/continuation.md \
  scripts/chatgpt_pro_consult.py scripts/codex_protocol_model.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py \
  docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md
```

Expected: the branch is `main` and the status command prints nothing. Compact and ambient paths remain exactly as they were before Task 2.

- [ ] **Step 8: Create and commit the owner handoff on `main`**

Create `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md` with:

- the actual owner identity and `Disposition: commit-and-handoff`;
- the full source `main` base and full preservation commit from Steps 2 and 6;
- canonical branch `codex/chatgpt-local-reprepare-flexibility-2026-07-16`;
- all sixteen paths with the exact blob IDs from Step 6;
- exact test commands and observed results;
- `Integration authority: none`, `Provider attempts: zero`, and `Push authority: none`;
- an explicit statement that the untracked 2026-07-15 plan is preserved context, not sufficient shipping authority;
- `Exact Next Trigger`: user approval of a dedicated design and compliant implementation plan, followed by a routed independent review of the frozen commit.

Stage and commit only this handoff:

```bash
env -u GIT_INDEX_FILE git add -- \
  docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git commit -m \
  "docs(recovery): hand off local reprepare WIP"
```

Expected: the staged-name check shows one handoff path and the commit changes no production, mailbox, packet, or runtime path.

### Task 3: Extract and hand off `ROOT-COMPACT`

**Files:**

- Preserve on `codex/recovery-compact-root-wip-2026-07-16`: `ARCHITECTURE.md`
- Preserve on the same branch: `logs/capability-first/`
- Compare only; do not stage or preserve: `governance.toml`, `scripts/target_binding.py`, `tests/unit/test_target_binding.py`, `tests/fixtures/compact_kernel/v1_misuse_vectors.json`
- Compare only; do not stage or preserve: `scripts/compact_state_mapping.py`, `tests/fixtures/compact_state_mapping/v1.json`, `tests/unit/test_compact_state_mapping.py`
- Create on `main`: `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md`

**Interfaces:**

- Consumes: the exact live dirty `ARCHITECTURE.md` and `logs/capability-first/` bytes remaining after Task 2, the canonical root-blob comparison checkpoint `1306c157ac434389444e77935d24db8b3189ee2c`, and the three contained-`main` advance commits named below.
- Produces: one preservation-only branch containing only the dirty doc/log roots, a root clean of compact WIP, and a handoff proving four clean checkpoint matches plus three clean contained-history advances. Distinct root measurements remain preserved but do not become accepted Phase-1 evidence.

- [ ] **Step 1: Prove the clean comparison set before extraction**

Run:

```bash
for item_path in \
  governance.toml \
  scripts/target_binding.py \
  tests/unit/test_target_binding.py \
  tests/fixtures/compact_kernel/v1_misuse_vectors.json; do
  work_blob="$(env -u GIT_INDEX_FILE git hash-object "$item_path")"
  checkpoint_blob="$(env -u GIT_INDEX_FILE git rev-parse \
    "1306c157ac434389444e77935d24db8b3189ee2c:$item_path")"
  head_blob="$(env -u GIT_INDEX_FILE git rev-parse "HEAD:$item_path")"
  test "$work_blob" = "$checkpoint_blob" || exit 1
  test "$work_blob" = "$head_blob" || exit 1
  printf 'checkpoint-match %s %s\n' "$work_blob" "$item_path"
done

check_contained_advance() {
  local advance_commit="$1"
  local item_path="$2"
  local expected_blob="$3"
  local work_blob
  local head_blob
  local advanced_blob
  local checkpoint_blob
  work_blob="$(env -u GIT_INDEX_FILE git hash-object "$item_path")"
  head_blob="$(env -u GIT_INDEX_FILE git rev-parse "HEAD:$item_path")"
  advanced_blob="$(env -u GIT_INDEX_FILE git rev-parse \
    "$advance_commit:$item_path")"
  checkpoint_blob="$(env -u GIT_INDEX_FILE git rev-parse \
    "1306c157ac434389444e77935d24db8b3189ee2c:$item_path")"
  test "$work_blob" = "$expected_blob" || return 1
  test "$work_blob" = "$head_blob" || return 1
  test "$work_blob" = "$advanced_blob" || return 1
  test "$work_blob" != "$checkpoint_blob" || return 1
  env -u GIT_INDEX_FILE git merge-base --is-ancestor \
    "$advance_commit" HEAD || return 1
  printf 'contained-main-advance %s %s %s\n' \
    "$work_blob" "$advance_commit" "$item_path"
}

check_contained_advance \
  484b16a27f45eb6f4b973894499ea1e5edf704c4 \
  scripts/compact_state_mapping.py \
  ff9118cbc509ae1a3e5a5f15816f907316f06218
check_contained_advance \
  be1488a41b6174b4503fb23f8885794fa37528fc \
  tests/fixtures/compact_state_mapping/v1.json \
  65e3bf1ec847c3b556f752198c00ba7647fd3a34
check_contained_advance \
  7151cee977693bcdf0dda262d68bd9e0253f7aa2 \
  tests/unit/test_compact_state_mapping.py \
  f9905658de63cce75f51a57414f5c211abdac665
```

Expected: four `checkpoint-match` lines and three `contained-main-advance` lines with exit `0`. The checkpoint matches are `governance.toml` at `da0d444ceef156c577636b2bc7d0fc168cff66bd`, `scripts/target_binding.py` at `bc8a1a210e1b56d197282c61b6bb5d679368c55b`, `tests/unit/test_target_binding.py` at `0fba3865772e8905eec9c795baee86aea6cb842a`, and `tests/fixtures/compact_kernel/v1_misuse_vectors.json` at `2ed1c69a4700edd9e87f18b436f36f0573917a56`. The contained-history advances are `scripts/compact_state_mapping.py` at `ff9118cbc509ae1a3e5a5f15816f907316f06218` through `484b16a27f45eb6f4b973894499ea1e5edf704c4`, `tests/fixtures/compact_state_mapping/v1.json` at `65e3bf1ec847c3b556f752198c00ba7647fd3a34` through `be1488a41b6174b4503fb23f8885794fa37528fc`, and `tests/unit/test_compact_state_mapping.py` at `f9905658de63cce75f51a57414f5c211abdac665` through `7151cee977693bcdf0dda262d68bd9e0253f7aa2`. All seven paths are clean comparison evidence and must remain outside the preservation commit. `ARCHITECTURE.md` is deliberately excluded from comparison because it contains a composite anchor refresh; preserve its exact blob but do not claim canonical equality.

- [ ] **Step 2: Switch the shared root to the compact preservation branch**

Run:

```bash
env -u GIT_INDEX_FILE git branch --show-current
env -u GIT_INDEX_FILE git switch -c \
  codex/recovery-compact-root-wip-2026-07-16
```

Expected: the first command prints `main`; the second creates the preservation branch without changing any tracked or untracked compact byte.

- [ ] **Step 3: Stage only the live dirty compact doc and evidence roots**

Run:

```bash
env -u GIT_INDEX_FILE git add -- \
  ARCHITECTURE.md \
  logs/capability-first
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git diff --cached --check
```

Expected: every staged path is exactly `ARCHITECTURE.md` or beneath `logs/capability-first/`. The seven clean comparison paths, ambient `.agents/`, `.codex/runtime/`, `ORIGINAL_REQUEST.md`, and `PROJECT.md` are absent. The check prints nothing.

- [ ] **Step 4: Execute the focused compact preservation checks**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_target_binding.py \
  tests/unit/test_compact_state_mapping.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: both commands pass. Record exact results; they prove only this dirty snapshot's focused behavior and structural health, not Phase-2 GO or measurement acceptance.

- [ ] **Step 5: Commit the preservation snapshot and capture its tree**

Run:

```bash
env -u GIT_INDEX_FILE git commit -m \
  "chore(recovery): preserve compact root WIP"
env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r HEAD
env -u GIT_INDEX_FILE git ls-tree -r HEAD -- \
  ARCHITECTURE.md \
  logs/capability-first
```

Expected: one full commit SHA and an exact preservation tree containing only `ARCHITECTURE.md` plus paths beneath `logs/capability-first/`. No clean compact code, fixture, or test path appears, and no output is interpreted as integration or accepted measurement evidence.

- [ ] **Step 6: Return to `main` and prove the compact targets are clean**

Run:

```bash
env -u GIT_INDEX_FILE git switch main
env -u GIT_INDEX_FILE git status --short -- \
  ARCHITECTURE.md governance.toml \
  scripts/target_binding.py scripts/compact_state_mapping.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_compact_state_mapping.py \
  tests/fixtures/compact_kernel/v1_misuse_vectors.json \
  tests/fixtures/compact_state_mapping/v1.json \
  logs/capability-first
```

Expected: no output across both preserved roots and all seven clean comparison paths. This is branch extraction, not deletion: the exact dirty `ARCHITECTURE.md` and `logs/capability-first/` bytes remain reachable from `codex/recovery-compact-root-wip-2026-07-16`; the seven comparison paths remain supplied by contained `main` history.

- [ ] **Step 7: Create and commit the compact root owner handoff**

Create `docs/HANDOFF-owner-2026-07-16-compact-root-wip.md` with:

- actual owner, full source base, full preservation head, and `Disposition: commit-and-handoff`;
- the preserved `ARCHITECTURE.md` and `logs/capability-first/` roots and exact blob IDs;
- the four checkpoint-match results and the three contained-`main` advance results from Step 1, including every exact blob and advance commit;
- an explicit finding that all seven clean code, fixture, and test paths were comparison evidence and are absent from the preservation commit;
- a finding that the `ARCHITECTURE.md` snapshot is composite preservation and must be regenerated against whichever feature range is integrated;
- a finding that the root `logs/capability-first/` cohorts are evidence-only until the Phase-1/2 integration plan explicitly accepts or supersedes them;
- canonical implementation branch `codex/capability-phase2-shadow-2026-07-15`, clean live implementation head `2d5b23f819694f2abe39d4aed6cac318a4f9019d`, integration snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`, excluded post-snapshot chain `ae24effb8734cd92e418ae2f032724428d0df94a -> 2d5b23f819694f2abe39d4aed6cac318a4f9019d`, and root-blob comparison checkpoint `1306c157ac434389444e77935d24db8b3189ee2c`;
- `Authority: epoch 0, writer v1, no activation`, plus no merge/push/cleanup authority;
- `Exact Next Trigger`: execute `docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md` only after the Phase-1 and Phase-2 handoffs in Task 4 are committed.

Commit only the handoff path on `main` with message `docs(recovery): hand off compact root WIP`.

### Task 4: Freeze the canonical Phase-1 and Phase-2 committed branches

**Files:**

- Create: `docs/HANDOFF-owner-2026-07-16-capability-phase1.md`
- Create: `docs/HANDOFF-owner-2026-07-16-capability-phase2.md`
- Read: `.worktrees/capability-phase1-closure-2026-07-15/`
- Read: `.worktrees/capability-phase2-shadow-2026-07-15/`

**Interfaces:**

- Consumes: clean Phase-1 head `8149df28b45bd2b0b159b243923d0ab439c3d815`, clean canonical Phase-2 live head `2d5b23f819694f2abe39d4aed6cac318a4f9019d`, frozen replay snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`, the post-snapshot commits `ae24effb8734cd92e418ae2f032724428d0df94a` and `2d5b23f819694f2abe39d4aed6cac318a4f9019d`, their branch-local plans, and current owner confirmations.
- Produces: committed Phase-1 and Phase-2 owner freezes that retain the full live Phase-2 chain while excluding both post-snapshot commits from current replay and integration.

- [ ] **Step 1: Reverify heads, ancestry, and the exact clean Phase-2 chain**

Run:

```bash
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase1-closure-2026-07-15 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase1-closure-2026-07-15 \
  rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase2-shadow-2026-07-15 \
  status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase2-shadow-2026-07-15 \
  rev-parse 'HEAD^{commit}'
test "$(env -u GIT_INDEX_FILE git rev-parse \
  '2d5b23f819694f2abe39d4aed6cac318a4f9019d^')" = \
  ae24effb8734cd92e418ae2f032724428d0df94a
test "$(env -u GIT_INDEX_FILE git rev-parse \
  'ae24effb8734cd92e418ae2f032724428d0df94a^')" = \
  bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  8149df28b45bd2b0b159b243923d0ab439c3d815 main
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  2d5b23f819694f2abe39d4aed6cac318a4f9019d main
env -u GIT_INDEX_FILE git diff --raw \
  872aa67341e500f1a87f99111611077be3d3fde6..8149df28b45bd2b0b159b243923d0ab439c3d815
env -u GIT_INDEX_FILE git diff --raw \
  8149df28b45bd2b0b159b243923d0ab439c3d815..2d5b23f819694f2abe39d4aed6cac318a4f9019d
```

Expected: both worktrees are clean at their exact heads; `2d5b23f...` directly parents `ae24eff...`, which directly parents `bea4cb9...`; both ancestry checks exit `1`; and committed-range raw diffs print exact mode/blob/path identities. A moved head, dirty byte, staged path, or continuing writer blocks the handoff until the owner refreshes the route.

- [ ] **Step 2: Resolve the Phase-2 owner without inferring authority**

Read current mailbox bodies again. If no durable artifact names the owner of the Phase-2 branch and both post-snapshot commits, stop and ask the user-principal to name that owner; do not infer it from authorship, content, process IDs, timestamps, or this plan. No new preservation branch is needed because all eight successor paths are already committed and the source worktree is clean. The owner confirmation binds the exact live head, the two-commit post-snapshot chain, and the exclusion-only outcome; it grants no implementation, merge, replay, provider, activation, push, or cleanup authority.

- [ ] **Step 3: Run branch-focused evidence without mutating either branch**

Run:

```bash
(
  cd .worktrees/capability-phase1-closure-2026-07-15
  env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
    tests/unit/test_capability_baseline_runtime.py -q
)
(
  cd .worktrees/capability-phase2-shadow-2026-07-15
  env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
    tests/unit/test_capability_reducer.py \
    tests/unit/test_capability_reducer_replay.py \
    tests/unit/test_capability_v1_adapter.py \
    tests/unit/test_compact_kernel_surface_inventory.py \
    tests/unit/test_compact_state_mapping.py -q
)
```

Expected: both commands pass. These are freshness checks for the handoff; independent review and integration remain owned by the Phase-1/2 integration plan.

- [ ] **Step 4: Create the Phase-1 owner handoff on `main`**

Create `docs/HANDOFF-owner-2026-07-16-capability-phase1.md` recording owner, branch, full head `8149df28b45bd2b0b159b243923d0ab439c3d815`, base `872aa67341e500f1a87f99111611077be3d3fde6`, exact branch status, focused test result, committed cohort paths, no activation, no integration, and no push. Its `Exact Next Trigger` is the Phase-1 portion of `docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md`.

Commit only this handoff with message `docs(recovery): freeze capability phase 1`.

- [ ] **Step 5: Refresh and create the Phase-2 canonical owner handoff on `main`**

Immediately re-run the Phase-2 status and `rev-parse` commands from Step 1. Then create `docs/HANDOFF-owner-2026-07-16-capability-phase2.md` recording:

- actual owner and `Disposition: commit-and-handoff`;
- canonical branch `codex/capability-phase2-shadow-2026-07-15`;
- immutable clean live implementation head `2d5b23f819694f2abe39d4aed6cac318a4f9019d` and its full ordered commit range after Phase 1;
- integration replay snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`, whose preceding chain includes `c4aea47bf1c370b89d4f41c79929d9722a44225a` and `1306c157ac434389444e77935d24db8b3189ee2c`;
- post-snapshot chain `ae24effb8734cd92e418ae2f032724428d0df94a -> 2d5b23f819694f2abe39d4aed6cac318a4f9019d`, exact path/blob identities for both commits, and disposition `retained on canonical branch but excluded from current replay pending revised allowlist and fresh review`;
- the exact branch-local plans `docs/superpowers/plans/2026-07-15-capability-compact-reducer-phase2.md` and `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md`;
- focused test results, `epoch 0`, `writer v1`, shadow-only authority, no provider attempt, and no merge/push/activation;
- a freeze rule that any branch advance replaces this handoff;
- `Exact Next Trigger`: execute `docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md` against replay snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`; do not include either `ae24effb...` or `2d5b23f...` without a revised allowlist, dedicated review, and replacement handoff.

Commit only this handoff with message `docs(recovery): freeze canonical capability phase 2`.

### Task 5: Preserve the dirty control-plane WIP on a non-shipping branch

**Files:**

- Preserve in `.worktrees/control-plane-authority-foundation-2026-07-10` on `codex/recovery-control-plane-wip-2026-07-16`: `ARCHITECTURE.md`, `scripts/bus_unread.py`, `scripts/consume_bus.py`, `scripts/protocol_authority.py`, `scripts/protocol_mailbox.py`
- Preserve on the same branch: `tests/unit/test_coordination_tooling.py`, `tests/unit/test_protocol_authority.py`, `tests/unit/test_protocol_mailbox.py`, `tests/unit/test_threeway_activation_scripts.py`
- Create on `main`: `docs/HANDOFF-owner-2026-07-16-control-plane-wip.md`

**Interfaces:**

- Consumes: the parked exact base `6983673db60bff0d21548a90ab1db2fcbbfa377a`, the nine unstaged paths, and a fresh coordinator preservation-only route.
- Produces: one frozen preservation branch whose head is never treated as Task2U GO or a merge candidate, plus an owner handoff to the Phase-3 convergence plan.

- [ ] **Step 1: Require a fresh preservation-only owner route**

The coordinator must refresh mailbox, capacity, locks, worktree status, and the parked packet body. Generate the current packet coverage, send one preservation-only route, and derive its canonical path from the tool output:

```bash
CAPACITY_JSON="$(env -u GIT_INDEX_FILE .venv/bin/python \
  scripts/protocol_capacity_board.py --wave 2 --json)"
PACKET_COVERAGE="$(printf '%s' "$CAPACITY_JSON" | \
  env -u GIT_INDEX_FILE .venv/bin/python -c \
  'import json,sys; data=json.load(sys.stdin); print("\n".join("- `%s`" % row["id"] for row in data["packets"]))')"
ROUTE_BASE="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
SEND_OUTPUT="$(coordination/bin/send-event coordinator all coordination \
  "preserve control-plane WIP for compact convergence" <<EOF
Event type: coordination
Disposition: CONTROL_PLANE_WIP_PRESERVATION_ONLY
Task-board: pipeline-recovery-owner-wip-disposition-2026-07-16
Protocol wave: 2
Route base before commit: $ROUTE_BASE
Plan: docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md

Director retains ownership of the parked nine-path Task2U working snapshot at
base 6983673db60bff0d21548a90ab1db2fcbbfa377a. Switch only that worktree to
codex/recovery-control-plane-wip-2026-07-16, commit the nine exact paths as
preservation evidence, execute the four named focused test files, and publish
docs/HANDOFF-owner-2026-07-16-control-plane-wip.md. This is not Task2U
acceptance, GO, integration, activation, merge, push, cleanup, or permission to
modify another path. The original control-plane branch ref remains fixed at the
base above.

Join condition: the preservation branch and owner handoff exist at exact full
SHAs, the original branch still equals the base above, and no production
integration or side effect occurred.

## Capacity Split Default

Use the single-pair fast path for this one-owner preservation action; Pair B is
limited to bounded planning or preflight. Reject dual-pair routing because
Chunk A and Chunk B would share the same nine dirty blobs.

## Capacity Packet Coverage

$PACKET_COVERAGE

## Exact Next Trigger

Director preserves the exact nine-path snapshot and stops after the committed
owner handoff. Coordinator then rechecks the original and preservation refs.
EOF
)"
ROUTE_EVENT="${SEND_OUTPUT#created }"
ROUTE_EVENT="${ROUTE_EVENT%% (*}"
case "$ROUTE_EVENT" in
  coordination/mailbox/sent/*-coordinator-to-all-coordination.md) ;;
  *) exit 1 ;;
esac
test -f "$ROUTE_EVENT"
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
  --wave 2 --validate-route "$ROUTE_EVENT"
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py \
  --wave 2 --route "$ROUTE_EVENT"
env -u GIT_INDEX_FILE git add -f -- "$ROUTE_EVENT"
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git commit -m \
  "coord(coordinator): preserve control-plane WIP for convergence"
```

Expected: `send-event` creates and stages exactly one canonical route, the generated body names every current packet ID, both validators pass, the staged-name check shows only the generated route, and the coordinator commit changes only that route. This route is a separate, user-visible protocol mutation and is not implied by the preservation plan commit.

- [ ] **Step 2: Recheck the parked base and exact dirty set**

Run:

```bash
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  status --short
```

Expected: head is exactly `6983673db60bff0d21548a90ab1db2fcbbfa377a`; status lists exactly the nine paths under **Files**. Any mismatch returns to the coordinator without mutation.

- [ ] **Step 3: Switch that worktree to the preservation branch and stage exactly nine paths**

Run:

```bash
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  switch -c codex/recovery-control-plane-wip-2026-07-16
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 add -- \
  ARCHITECTURE.md scripts/bus_unread.py scripts/consume_bus.py \
  scripts/protocol_authority.py scripts/protocol_mailbox.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_authority.py \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_threeway_activation_scripts.py
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  diff --cached --name-only
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  diff --cached --check
```

Expected: exactly nine staged names and no whitespace errors. The original branch ref `codex/control-plane-authority-foundation-2026-07-10` remains at `6983673db60bff0d21548a90ab1db2fcbbfa377a`.

- [ ] **Step 4: Execute focused preservation evidence**

Run:

```bash
(
  cd .worktrees/control-plane-authority-foundation-2026-07-10
  env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
    tests/unit/test_coordination_tooling.py \
    tests/unit/test_protocol_authority.py \
    tests/unit/test_protocol_mailbox.py \
    tests/unit/test_threeway_activation_scripts.py -q
)
```

Expected: record the exact outcome. A failure is preserved in the handoff and remains binding; it does not authorize a fix in this preservation task.

- [ ] **Step 5: Commit the nine blobs and freeze the preservation head**

Run:

```bash
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  commit -m "chore(recovery): preserve control-plane Task2U WIP"
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE git rev-parse \
  codex/control-plane-authority-foundation-2026-07-10^{commit}
env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-authority-foundation-2026-07-10 \
  ls-tree -r HEAD -- \
  ARCHITECTURE.md scripts/bus_unread.py scripts/consume_bus.py \
  scripts/protocol_authority.py scripts/protocol_mailbox.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_authority.py \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_threeway_activation_scripts.py
```

Expected: the first SHA is the preservation child; the second remains exactly `6983673db60bff0d21548a90ab1db2fcbbfa377a`; nine mode/type/blob/path lines bind the handoff. No amend, rebase, or merge occurs.

- [ ] **Step 6: Create and commit the control-plane owner handoff on `main`**

Create `docs/HANDOFF-owner-2026-07-16-control-plane-wip.md` with owner, old branch/ref, base `6983673db60bff0d21548a90ab1db2fcbbfa377a`, preservation branch/full head, the nine path/blob IDs, exact test outcome, prior Operator FAIL and contradiction artifact paths, and `Disposition: commit-and-handoff for salvage only`. State that the branch is not Task2U, not GO, and must never be merged wholesale. Its `Exact Next Trigger` is `docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md` after Phase-1/2 integration closes.

Commit only the handoff with message `docs(recovery): hand off control-plane WIP`.

### Task 6: Freeze the clean Opus Stage-A owner range

**Execution priority:** Run this task immediately after Task 1 and before Tasks 2-5. It is numbered by recovery-unit grouping, not by execution order.

**Files:**

- Read: `.worktrees/opus-transport-first-stage-a-director2/`
- Create: `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md`

**Interfaces:**

- Consumes: clean branch `codex/director2-opus-transport-stage-a`, exact head `16c4f83aef4130d977a91d623a9254c4fd46980a`, and current Director2 ownership.
- Produces: a committed owner handoff without advancing the implementation branch or invoking a provider.

- [ ] **Step 1: Reverify branch identity, cleanliness, and range**

Run:

```bash
env -u GIT_INDEX_FILE git -C \
  .worktrees/opus-transport-first-stage-a-director2 status --short --branch
env -u GIT_INDEX_FILE git -C \
  .worktrees/opus-transport-first-stage-a-director2 rev-parse 'HEAD^{commit}'
env -u GIT_INDEX_FILE git -C \
  .worktrees/opus-transport-first-stage-a-director2 log --oneline \
  40fd0a5e43c6b28330ced9ddffe01483cde42b65..16c4f83aef4130d977a91d623a9254c4fd46980a
env -u GIT_INDEX_FILE git -C \
  .worktrees/opus-transport-first-stage-a-director2 diff --raw \
  40fd0a5e43c6b28330ced9ddffe01483cde42b65..16c4f83aef4130d977a91d623a9254c4fd46980a
```

Expected: clean branch, exact head `16c4f83aef4130d977a91d623a9254c4fd46980a`, exactly the `56091d107382abfe9f06df1aa4cd003d71be7b5e` plus `16c4f83aef4130d977a91d623a9254c4fd46980a` commits, and raw blob/path identities for the exact range. Any advancement blocks this handoff.

- [ ] **Step 2: Create and commit the Stage-A owner handoff on `main`**

Create `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md` recording Director2 ownership, base/full head, the two implementation commits, exact four-file aggregate scope from the active packet, existing review findings, zero provider attempts, and no descriptor/GO/integration claim. Its `Exact Next Trigger` is `docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md` under the current Stage-A owner route.

Commit only the handoff with message `docs(recovery): freeze Opus Stage A range`.

### Task 7: Publish the aggregate coordinator disposition and open later ownership gates

**Files:**

- Create: `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md`
- Read: all six owner handoffs created above
- Read: all six frozen branches/worktrees

**Interfaces:**

- Consumes: committed owner handoffs, exact branch heads/blobs, clean recovery-target paths, current mailbox/capacity/lock state.
- Produces: one coordinator-owned disposition record that downstream plans may cite. It produces no implementation route, integration, or side effect.

- [ ] **Step 1: Refresh hot-tree and handoff ancestry**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -8
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
for handoff in \
  docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md \
  docs/HANDOFF-owner-2026-07-16-compact-root-wip.md \
  docs/HANDOFF-owner-2026-07-16-capability-phase1.md \
  docs/HANDOFF-owner-2026-07-16-capability-phase2.md \
  docs/HANDOFF-owner-2026-07-16-control-plane-wip.md \
  docs/HANDOFF-owner-2026-07-16-opus-stage-a.md; do
  env -u GIT_INDEX_FILE git log -1 --format='%H %s' -- "$handoff"
done
```

Expected: governed checks pass and every handoff prints one committed full SHA/subject. Missing or uncommitted handoffs block aggregation.

- [ ] **Step 2: Prove all recovery-shared target paths are clean**

Run the exact ownership gates from:

```bash
env -u GIT_INDEX_FILE git status --short -- \
  AGENTS.md CLAUDE.md ARCHITECTURE.md OPERATIONS.md governance.toml \
  scripts/chatgpt_pro_consult.py scripts/codex_protocol_model.py \
  scripts/target_binding.py scripts/compact_state_mapping.py \
  scripts/protocol_capacity.py scripts/protocol_capacity_board.py \
  scripts/opus_review_bridge.py scripts/opus_review_receipts.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_compact_state_mapping.py \
  docs/protocol/codex/continuation.md \
  .agents/skills/chatgpt-pro-consultation/SKILL.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .codex/agents/readiness-bridge.toml \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  tests/fixtures/compact_kernel/v1_misuse_vectors.json \
  tests/fixtures/compact_state_mapping/v1.json \
  logs/capability-first
test -z "$(env -u GIT_INDEX_FILE git -C \
  .worktrees/capability-phase2-shadow-2026-07-15 \
  status --porcelain=v1 --untracked-files=all)"
```

Expected: no output. The Phase-2 worktree is clean on its canonical branch at the committed live head. Ambient untracked paths outside this exact list remain out of scope and untouched.

- [ ] **Step 3: Recheck every frozen head against its handoff**

Run:

```bash
env -u GIT_INDEX_FILE git rev-parse \
  codex/capability-phase1-closure-2026-07-15^{commit}
env -u GIT_INDEX_FILE git rev-parse \
  codex/capability-phase2-shadow-2026-07-15^{commit}
env -u GIT_INDEX_FILE git rev-parse \
  codex/director2-opus-transport-stage-a^{commit}
env -u GIT_INDEX_FILE git rev-parse \
  codex/chatgpt-local-reprepare-flexibility-2026-07-16^{commit}
env -u GIT_INDEX_FILE git rev-parse \
  codex/recovery-compact-root-wip-2026-07-16^{commit}
env -u GIT_INDEX_FILE git rev-parse \
  codex/recovery-control-plane-wip-2026-07-16^{commit}
```

Expected: the first three values are exactly `8149df28b45bd2b0b159b243923d0ab439c3d815`, `2d5b23f819694f2abe39d4aed6cac318a4f9019d`, and `16c4f83aef4130d977a91d623a9254c4fd46980a`; the final three exactly match their committed owner handoffs. The Phase-2 handoff separately binds replay snapshot `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a` and labels both later commits excluded from replay. Any mismatch invalidates only the affected unit and blocks later routes that depend on it.

- [ ] **Step 4: Create the coordinator disposition record**

Create `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md` with findings first and one row per recovery unit. Each row must contain owner, disposition, source base, canonical or preservation branch, full frozen head, handoff path plus its unique introduction commit, Git blob OID, and SHA-256 digest, path roots, executed evidence, downstream plan, and exclusions. Use the parseable reference grammar `<path>@commit:<40-lowercase-hex>@blob:<40-lowercase-hex>@sha256:<64-lowercase-hex>` exactly once per owner handoff so downstream plans never select an artifact by timestamp or ambient `HEAD`. Add a second table for excluded ambient untracked roots with disposition `retained in place; cleanup unauthorized`. State explicitly:

- ChatGPT WIP is preserved but awaits dedicated design/plan approval;
- compact Phase 2 is the only canonical compact implementation branch;
- the clean post-snapshot Phase-2 chain remains retained on the canonical branch, while both `ae24eff...` and `2d5b23f...` are excluded from replay/integration until a revised allowlist and replacement reviewed handoff exist;
- the root compact transfer branch and root logs are preservation/evidence only;
- control-plane WIP is salvage input and not a merge candidate;
- Opus Stage A remains owned by its active correction plan;
- candidate-policy and targeted-web ownership checks may proceed only when their full exact gates print no output;
- no merge, push, provider, activation, or cleanup occurred.

End the artifact with `## Exact Next Trigger`: run the Opus correction plan and the capability Phase-1/2 integration preflight on their disjoint branches; after Opus B-D closes, run the target bridge, then candidate policy, then PPL, then targeted web under their fixed succession wrapper. Compact Phase 3 also remains blocked on the terminal ChatGPT local-reprepare disposition in Task 8.

- [ ] **Step 5: Verify and commit only the aggregate disposition**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check -- \
  docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git add -- \
  docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git commit -m \
  "docs(recovery): reconcile owner WIP dispositions"
```

Expected: diff check and smoke pass; staged scope is the single aggregate handoff; the commit changes no owner branch, production file, packet, mailbox, cursor, lock, or runtime artifact.

### Task 8: Resolve the preserved ChatGPT local-reprepare range before compact convergence

**Files:**
- Read: `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md`
- Create on withdrawal: `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare-withdrawn.md`
- Create after either terminal outcome: `docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md`

**Interfaces:**
- Consumes the content-addressed preservation handoff/branch, current overlapping main paths, and one explicit user-principal choice: `withdraw-preserved` or `plan-review-integrate`.
- Produces one terminal disposition before Phase 3. Preservation by itself is not terminal shipping status.

- [ ] **Step 1: Bind the exact preserved range and request the user decision**

Resolve the preservation handoff from the aggregate's exact path/commit/blob/digest, revalidate its branch/head and path blobs, and inventory overlap with the then-current accepted Opus/bridge/candidate/PPL/web and compact paths. Ask the user-principal to choose withdrawal or a dedicated integration workflow. Do not infer the choice from file contents, age, prior standing approval, or branch existence.

- [ ] **Step 2A: Record withdrawal without deleting evidence**

For `withdraw-preserved`, the owner commits only `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare-withdrawn.md`, binding the user decision correlation, preservation handoff/branch/head/blob set, reason, and status `withdrawn-preserved`. No branch or worktree is deleted. The coordinator then commits only the fixed disposition handoff, content-addressing both owner artifacts and confirming that none of the preserved production blobs entered `main`.

- [ ] **Step 2B: Use a dedicated reviewed integration workflow**

For `plan-review-integrate`, stop until a separately approved design and implementation plan bind the exact preserved range, current main base, overlap resolution, abuse cases, tests, and owner. A routed implementer produces a fresh range; an independent Operator returns GO/NITS/FAIL; and only after GO may a separately user-named local integrator merge the exact reviewed head. Rerun merged-tree provider, prompt-sync, target-bridge, protocol, smoke, and no-side-effect gates. The coordinator then commits only the fixed disposition handoff with status `integrated-reviewed`, the dedicated plan, Operator report, user integration authority, exact integrated main SHA, and merged-tree evidence. NITS/FAIL or conflict leaves status nonterminal and Phase 3 blocked.

- [ ] **Step 3: Validate the fixed disposition**

Capture the coordinator disposition commit/blob/digest and require its commit changes only that path. Exactly one terminal status is present. It grants no push, provider, activation, protocol-ref mutation, cleanup, or branch deletion. Retirement later verifies this already committed decision; it cannot defer or perform the integration after activation.

## Completion Evidence

Phase-0A preservation is complete only when:

1. all six owner handoffs and the aggregate coordinator handoff are committed;
2. all six branch heads match their handoffs;
3. the shared-root recovery target command prints no output;
4. the original control-plane branch still points to `6983673db60bff0d21548a90ab1db2fcbbfa377a` and the parked bytes are reachable from the preservation branch;
5. the Opus Stage-A branch remains exactly `16c4f83aef4130d977a91d623a9254c4fd46980a` with zero new provider attempts;
6. no owner WIP was stashed, reset, restored, cleaned, overwritten, or silently incorporated into another unit;
7. no merge, push, activation, publication, or cleanup occurred.

Full recovery-disposition eligibility additionally requires Task 8's fixed ChatGPT disposition path/commit/blob/digest with terminal status `withdrawn-preserved` or `integrated-reviewed`. Until then, preservation is complete but compact convergence remains blocked; do not mark the full plan terminal merely from the seven preservation checks.

## Exact Next Trigger

After the aggregate handoff commit, execute the separately approved Opus correction plan and capability Phase-1/2 integration plan only against their frozen heads. The target bridge follows Opus; candidate policy follows the bridge; PPL follows the post-candidate compatibility GO; targeted web follows the terminal PPL handoff. Compact Phase 3 additionally waits for Task 8's terminal ChatGPT disposition.
