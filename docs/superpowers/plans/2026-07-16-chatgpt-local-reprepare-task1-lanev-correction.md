# ChatGPT Local Re-prepare Task 1 Singular Lane-V Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Seat execution note:** candidate, route, provider, receipt, and verdict
> actions are authority-sensitive and remain owned by the named live seat.
> Subagents may perform bounded read-only evidence work only; they do not
> inherit mailbox, ref, merge, descriptor, provider, receipt, or verdict
> authority.

**Goal:** replace the impossible two-head Task 1 review with one lawful
singular `P..C` Lane-V range that mechanically incorporates both immutable
frozen heads, receives one independent Pair-A Operator review, and leaves the
original heads—not the candidate lineage—as the only later integration inputs.

**Architecture:** a future coordinator route `R` binds its first parent as
candidate base `P`. Director constructs review-only merge commits `M1` and `C`
from the two immutable heads, then commits one descriptor `D` and one canonical
verify-request `T`. After Opus Stage A terminally clears, a second coordinator
route activates Pair-A Operator with one exact trigger-bound provider token;
the resulting report is structurally bound only to `C/P`.

**Tech Stack:** Git merge/worktree plumbing, `lane-v-scope/v1`, Pipeline
mailbox/capacity tooling, pytest, the provider-free Lane-V resolver, the
receipt-backed Opus bridge, and the lane-v-report/v2 publisher.

**Design:**
`docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction-design.md`

## Global Constraints

- Separate explicit user approval of both correction documents is required
  before Task 1 begins. Their existence or commit is not approval.
- Preserve these immutable heads exactly:
  - `H_CODEX=3dcff96948003d510451266b017895b42bd73c2e`;
  - `H_CLAUDE=233ef8126bc75dc6a2a13adcb70810b619faa85c`.
- Preserve their exact source parents:
  - `B_CODEX=560a95d70cde463913cae6fdbc355f7478c25498`;
  - `B_CLAUDE=96aa0b2e2885d85501fc4fd8e8ffd452710e3b4a`.
- Descriptor task ID is fixed as
  `f1e1ad5f-cb1b-4650-93ad-bf8701069f32`; no replacement UUID is permitted.
- Candidate branch is fixed as
  `codex/chatgpt-task1-singular-lanev-candidate-2026-07-16`.
- Candidate worktree is fixed as the absolute path
  `/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16`;
  every candidate-sensitive command binds that path explicitly.
- Candidate descriptor path is fixed as
  `coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json`.
- Candidate range is exactly 22 paths. No `ARCHITECTURE.md`, capacity packet,
  route, descriptor, request, receipt, report, or runtime path belongs to
  `P..C`.
- All git and pytest commands use `env -u GIT_INDEX_FILE`.
- No merge conflict is hand-resolved. No rebase, cherry-pick, squash, rerere,
  patch replay, restore, checkout of individual paths, or equivalent-tree
  substitute is allowed.
- `ci_smoke.py` is not a candidate-range command because exact `P..C` leaves
  the expected architecture-anchor update to the original plan's Task 5.
- No provider attempt occurs before Opus Stage A terminally clears and a later
  coordinator route names Pair-A Operator as executor for one exact command.
- Provider retries, transport fallback, credential entry, receipt deletion or
  reset, push, remote publication, deployment, and candidate cleanup are
  forbidden. After activation, the only allowed publication is one canonical
  local verification-report followed by its report-only local commit.
- The already approved ChatGPT design and plan remain byte-for-byte unchanged.
- Consultation during drafting was prohibited by the user scope and had zero
  provider attempts and zero receipts.

---

### Task 1: User approval and candidate-construction route (`coordinator`)

**Files:**

- Read:
  `docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction-design.md`
- Read:
  `docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction.md`
- Create:
  `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-director-candidate.json`
- Create:
  `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-operator-lanev.json`
- Create:
  `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-coordinator-join.json`
- Create: one canonical coordinator route under `coordination/mailbox/sent/`

**Interfaces:**

- Consumes: separate user approval of both correction documents, clean current
  Pipeline `main`, immutable frozen refs, and no existing candidate artifacts.
- Produces: one route commit `R`; its first parent is `P`; Director is active
  only for candidate/descriptor/request construction; Operator remains blocked.

- [ ] **Step 1: Prove separate approval and refresh live state.**

The coordinator must bind the user instruction that explicitly approves both
correction paths. Then run:

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE .venv/bin/python \
  .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git status --porcelain=v1
find coordination/locks -mindepth 1 -type f ! -name .gitkeep -print
env -u GIT_INDEX_FILE git show-ref --verify refs/heads/codex/chatgpt-local-reprepare-flexibility-2026-07-16
env -u GIT_INDEX_FILE git show-ref --verify refs/heads/codex/chatgpt-pro-claude-surface-wip-2026-07-16
```

Expected: current mailbox has no superseding ChatGPT route; shared index and
locks are empty; both refs equal the two full SHAs in Global Constraints.

- [ ] **Step 2: Require all future candidate names to be absent.**

```bash
test ! -e /Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16
! env -u GIT_INDEX_FILE git show-ref --verify --quiet \
  refs/heads/codex/chatgpt-task1-singular-lanev-candidate-2026-07-16
! env -u GIT_INDEX_FILE git log --all --format=%H -- \
  coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json | grep -q .
```

Expected: all commands exit zero; there is no branch, worktree, descriptor, or
prior use of this task ID.

- [ ] **Step 3: Create the three capacity packets.**

Use `apply_patch` to create the exact packet paths named above with cycle
`chatgpt-local-reprepare-task1-singular-lanev-2026-07-16`, Wave 2, empty lock
and remediation-row lists, and these initial states:

- Director packet: owner `director`, type `director-implementation`, status
  `active`, allowed paths limited to the absolute candidate worktree root, the
  22 frozen paths, the fixed descriptor, and one Director-to-Operator request;
  the fixed branch identity belongs in acceptance text rather than
  `allowed_paths`.
- Operator packet: owner `operator`, type `operator-verification`, status
  `blocked`, dependency on the Director packet, `verify_request: null`,
  `target_commit: null`, and `commit_range: null`.
- Coordinator packet: owner `coordinator`, type `coordinator-join`, status
  `blocked`, dependency on the Operator packet, allowed paths limited to the
  three packets, routes, and the terminal ChatGPT disposition handoff.

Each packet's acceptance text must repeat the immutable heads, exact 22-path
range, no-conflict rule, candidate-not-integration rule, zero-provider boundary,
and the next recipient. Do not repurpose an Opus Stage-A packet.

- [ ] **Step 4: Commit one candidate-construction route `R`.**

The route must state exactly once:

```text
Candidate base: $P_SHA
Frozen Codex head: 3dcff96948003d510451266b017895b42bd73c2e
Frozen Claude head: 233ef8126bc75dc6a2a13adcb70810b619faa85c
Descriptor task ID: f1e1ad5f-cb1b-4650-93ad-bf8701069f32
Provider process attempts authorized: 0
Receipt mutations authorized: 0
```

`Candidate base` is runtime-bound: construct the route on the current parent
`P`, commit the three packets plus the one route, then prove the committed
value equals `git rev-parse R^`. The route's Side-Effect Executor Token names
Director and authorizes only one candidate branch/worktree, the two mechanical
merge commits, focused tests, descriptor-only `D`, request-only `T`, and
provider-free/state-free validation. Its non-goals repeat every prohibited
effect from Global Constraints.

- [ ] **Step 5: Validate and postcheck `R`.**

```bash
R_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
P_SHA="$(env -u GIT_INDEX_FILE git rev-parse "${R_SHA}^1")"
ROUTE_PATH="$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r "$R_SHA" | grep '^coordination/mailbox/sent/.*-coordinator-to-all-coordination\.md$')"
printf '%s\n' "$R_SHA" "$P_SHA" | grep -Ec '^[0-9a-f]{40}$' | grep -qx 2
test "$(env -u GIT_INDEX_FILE git show "${R_SHA}:${ROUTE_PATH}" | sed -n 's/^Candidate base: //p')" = "$P_SHA"
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
  --wave 2 --validate-route "$ROUTE_PATH"
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py \
  --wave 2 --route "$ROUTE_PATH"
env -u GIT_INDEX_FILE git diff --check "${R_SHA}^1" "$R_SHA"
```

Expected: all validators pass; `R` changes only the three packets and one
route; its parent is `P`; no candidate/ref/provider/receipt effect occurred.

### Task 2: Construct deterministic review candidate `P..C` (`director`)

**Files:**

- Create later by Git: branch
  `codex/chatgpt-task1-singular-lanev-candidate-2026-07-16`
- Create later by Git: worktree
  `/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16`
- Merge mechanically: the 22 exact frozen paths

**Interfaces:**

- Consumes: route `R`, `P=R^`, `H_CODEX`, and `H_CLAUDE`.
- Produces: `M1` with parents `[P,H_CODEX]` and `C` with parents
  `[M1,H_CLAUDE]`, plus deterministic expected-tree evidence.

- [ ] **Step 1: Recover `R` and `P` without inference.**

From shared-root `main` immediately after `R`:

```bash
R_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
P_SHA="$(env -u GIT_INDEX_FILE git rev-parse "${R_SHA}^1")"
ROUTE_PATH="$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r "$R_SHA" | grep '^coordination/mailbox/sent/.*-coordinator-to-all-coordination\.md$')"
test "$(env -u GIT_INDEX_FILE git show "${R_SHA}:${ROUTE_PATH}" | sed -n 's/^Candidate base: //p')" = "$P_SHA"
test "$(env -u GIT_INDEX_FILE git show "${R_SHA}:${ROUTE_PATH}" | grep -Fxc 'Frozen Codex head: 3dcff96948003d510451266b017895b42bd73c2e')" = 1
test "$(env -u GIT_INDEX_FILE git show "${R_SHA}:${ROUTE_PATH}" | grep -Fxc 'Frozen Claude head: 233ef8126bc75dc6a2a13adcb70810b619faa85c')" = 1
```

Expected: all variables are full lowercase SHAs and every route binding occurs
once.

- [ ] **Step 2: Re-prove frozen bases, refs, and base-tree equality.**

```bash
H_CODEX=3dcff96948003d510451266b017895b42bd73c2e
H_CLAUDE=233ef8126bc75dc6a2a13adcb70810b619faa85c
B_CODEX=560a95d70cde463913cae6fdbc355f7478c25498
B_CLAUDE=96aa0b2e2885d85501fc4fd8e8ffd452710e3b4a
test "$(env -u GIT_INDEX_FILE git rev-parse refs/heads/codex/chatgpt-local-reprepare-flexibility-2026-07-16)" = "$H_CODEX"
test "$(env -u GIT_INDEX_FILE git rev-parse refs/heads/codex/chatgpt-pro-claude-surface-wip-2026-07-16)" = "$H_CLAUDE"
test "$(env -u GIT_INDEX_FILE git rev-parse "${H_CODEX}^1")" = "$B_CODEX"
test "$(env -u GIT_INDEX_FILE git rev-parse "${H_CLAUDE}^1")" = "$B_CLAUDE"
env -u GIT_INDEX_FILE git merge-base --is-ancestor "$B_CODEX" "$P_SHA"
env -u GIT_INDEX_FILE git merge-base --is-ancestor "$B_CLAUDE" "$P_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$H_CODEX" "$P_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$H_CLAUDE" "$P_SHA"
```

For every path in `B_CODEX..H_CODEX`, require the `git ls-tree` mode/blob at
`P` to equal `B_CODEX`; repeat for `B_CLAUDE..H_CLAUDE`. A mismatch is base
drift and stops before worktree creation.

- [ ] **Step 3: Create the isolated candidate branch/worktree.**

```bash
test "$(env -u GIT_INDEX_FILE git branch --show-current)" = main
test -z "$(env -u GIT_INDEX_FILE git diff --cached --name-only)"
test -z "$(find coordination/locks -mindepth 1 -type f ! -name .gitkeep -print)"
WT=/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16
env -u GIT_INDEX_FILE git worktree add -b \
  codex/chatgpt-task1-singular-lanev-candidate-2026-07-16 \
  "$WT" \
  "$P_SHA"
test "$(env -u GIT_INDEX_FILE git -C "$WT" rev-parse --show-toplevel)" = "$WT"
```

Expected: shared root stays on `main` at `R`; isolated worktree is clean at
exact `P`.

- [ ] **Step 4: Precompute and commit the first mechanical merge.**

```bash
WT=/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16
EXPECTED_TREE_1="$(env -u GIT_INDEX_FILE git merge-tree --write-tree --no-messages "$P_SHA" "$H_CODEX")"
printf '%s\n' "$EXPECTED_TREE_1" | grep -Eq '^[0-9a-f]{40}$'
env -u GIT_INDEX_FILE git -C "$WT" merge --no-ff --no-commit "$H_CODEX"
test -z "$(env -u GIT_INDEX_FILE git -C "$WT" diff --name-only --diff-filter=U)"
env -u GIT_INDEX_FILE git -C "$WT" diff --cached --check
env -u GIT_INDEX_FILE git -C "$WT" commit -m \
  'merge(review): compose ChatGPT Task 1 Codex half'
M1_SHA="$(env -u GIT_INDEX_FILE git -C "$WT" rev-parse 'HEAD^{commit}')"
test "$(env -u GIT_INDEX_FILE git -C "$WT" rev-list --parents -n 1 "$M1_SHA")" = "$M1_SHA $P_SHA $H_CODEX"
test "$(env -u GIT_INDEX_FILE git -C "$WT" rev-parse "${M1_SHA}^{tree}")" = "$EXPECTED_TREE_1"
```

If merge-tree exits nonzero or does not return one tree OID, stop before
`git merge`; there is no merge state to abort. If the actual merge starts and
reports a conflict, run only `git -C "$WT" merge --abort`, preserve the
conflict evidence, and stop for the bounded contradiction path. Do not edit or
stage a path manually.

- [ ] **Step 5: Precompute and commit the second mechanical merge.**

```bash
EXPECTED_TREE_2="$(env -u GIT_INDEX_FILE git merge-tree --write-tree --no-messages "$M1_SHA" "$H_CLAUDE")"
printf '%s\n' "$EXPECTED_TREE_2" | grep -Eq '^[0-9a-f]{40}$'
env -u GIT_INDEX_FILE git -C "$WT" merge --no-ff --no-commit "$H_CLAUDE"
test -z "$(env -u GIT_INDEX_FILE git -C "$WT" diff --name-only --diff-filter=U)"
env -u GIT_INDEX_FILE git -C "$WT" diff --cached --check
env -u GIT_INDEX_FILE git -C "$WT" commit -m \
  'merge(review): compose ChatGPT Task 1 Claude half'
C_SHA="$(env -u GIT_INDEX_FILE git -C "$WT" rev-parse 'HEAD^{commit}')"
test "$(env -u GIT_INDEX_FILE git -C "$WT" rev-list --parents -n 1 "$C_SHA")" = "$C_SHA $M1_SHA $H_CLAUDE"
test "$(env -u GIT_INDEX_FILE git -C "$WT" rev-parse "${C_SHA}^{tree}")" = "$EXPECTED_TREE_2"
```

The same conflict stop applies. Hooks or ambient tools must not modify the
Git-produced merge result.

### Task 3: Prove candidate exactness and focused behavior (`director`)

**Files:**

- Read: exact `P..C` range
- Test: `tests/unit/test_chatgpt_pro_consult.py`
- Test: `tests/unit/test_protocol_prompt_sync.py`

**Interfaces:**

- Consumes: clean candidate `C`.
- Produces: exact topology/status/tree evidence and focused green tests. No
  descriptor exists yet.

- [ ] **Step 1: Verify ancestry, parent order, and clean status.**

```bash
env -u GIT_INDEX_FILE git -C "$WT" merge-base --is-ancestor "$P_SHA" "$C_SHA"
env -u GIT_INDEX_FILE git -C "$WT" merge-base --is-ancestor "$H_CODEX" "$C_SHA"
env -u GIT_INDEX_FILE git -C "$WT" merge-base --is-ancestor "$H_CLAUDE" "$C_SHA"
test "$(env -u GIT_INDEX_FILE git -C "$WT" rev-list --count --first-parent "$P_SHA..$C_SHA")" = 2
test -z "$(env -u GIT_INDEX_FILE git -C "$WT" status --porcelain=v1)"
env -u GIT_INDEX_FILE git -C "$WT" diff --check "$P_SHA..$C_SHA"
```

- [ ] **Step 2: Verify exact status/path equality, not only names.**

Run a trusted inline Python check that:

1. parses NUL-delimited `git diff --name-status -z --no-renames` for
   `B_CODEX..H_CODEX` and `B_CLAUDE..H_CLAUDE`;
2. requires 16 and 7 entries respectively;
3. permits only the one duplicate
   `tests/unit/test_protocol_prompt_sync.py`, with compatible status;
4. normalizes the union to exactly 22 `(status,path)` entries;
5. parses `P..C` with the same flags and requires exact tuple equality.

Expected: 22 exact entries and no rename/copy status. A mismatch stops before
descriptor creation.

- [ ] **Step 3: Run focused candidate tests.**

```bash
(
  cd "$WT"
  env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
    tests/unit/test_chatgpt_pro_consult.py \
    tests/unit/test_protocol_prompt_sync.py -q
)
```

Expected: all tests pass from the exact candidate worktree. Record the actual
count; do not hard-code a stale count into a verdict.

- [ ] **Step 4: Record the deliberate smoke deferral.**

Do not run `ci_smoke.py` as a candidate gate. Prove instead that `P..C` excludes
`ARCHITECTURE.md` and cite the correction design's anchor-drift explanation.
Smoke remains mandatory after the original plan's architecture-coherence task.

### Task 4: Commit descriptor `D`, request `T`, and provider-free evidence (`director`)

**Files:**

- Create:
  `coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json`
- Create: one canonical
  `coordination/mailbox/sent/*-director-to-operator-verify-request.md`

**Interfaces:**

- Consumes: exact clean `P..C` and focused test evidence.
- Produces: descriptor-only `D`, request-only `T`, exact attempt key, and proof
  of zero provider/receipt mutation.

Set
`WT=/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16`
and require `git -C "$WT" rev-parse --show-toplevel` to equal that exact path.
Every Task 4 file operation and command uses either `git -C "$WT"`, an
absolute `$WT/...` target, or an explicit `cd "$WT"` subshell. Nothing in this
task resolves relative to the shared root.

- [ ] **Step 1: Create the exact descriptor with `apply_patch`.**

Use `apply_patch` against the absolute path
`/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16/coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json`.
Materialize the already validated full `$P_SHA` value into
`reviewed_base.commit`; the literal string `$P_SHA` is invalid. Use exactly
this mapping and no additional field:

```json
{
  "schema_version": "lane-v-scope/v1",
  "task_id": "f1e1ad5f-cb1b-4650-93ad-bf8701069f32",
  "question_id": "chatgpt-local-reprepare-task1-singular-lanev",
  "trigger_kind": "verify-request",
  "verification_mode": "codex-lane-v",
  "verification_harness": "codex:lane-v-verifier",
  "review_profile": "codex-lane-v",
  "reviewed_base": {
    "policy": "exact",
    "commit": "$P_SHA"
  },
  "requirement_paths": [
    "coordination/mailbox/sent/2026-07-16T06-58-35Z-coordinator-to-all-coordination.md",
    "docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md",
    "docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md",
    "docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction.md",
    "docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-design.md",
    "docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction-design.md",
    "scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json"
  ],
  "allowed_path_roots": [
    ".agents/skills/chatgpt-pro-consultation/SKILL.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    ".agents/skills/seat-director/SKILL.md",
    ".agents/skills/seat-operator/SKILL.md",
    ".claude/skills/four-seat-protocol/SKILL.md",
    ".claude/skills/seat-coordinator/SKILL.md",
    ".claude/skills/seat-director/SKILL.md",
    ".claude/skills/seat-operator/SKILL.md",
    ".codex/agents/protocol-coordinator.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/readiness-bridge.toml",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/protocol/claude/continuation.md",
    "docs/protocol/codex/continuation.md",
    "docs/superpowers/plans/2026-07-15-chatgpt-local-reprepare-flexibility.md",
    "scripts/chatgpt_pro_consult.py",
    "scripts/codex_protocol_model.py",
    "tests/unit/test_chatgpt_pro_consult.py",
    "tests/unit/test_protocol_prompt_sync.py"
  ],
  "verification_commands": [
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py tests/unit/test_protocol_prompt_sync.py -q"
  ]
}
```

- [ ] **Step 2: Parse, digest, and commit descriptor-only `D`.**

```bash
(
  cd "$WT"
  DESCRIPTOR_PATH=coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json
  env -u GIT_INDEX_FILE ../../.venv/bin/python -c \
    'from pathlib import Path; import sys; from scripts.opus_review_receipts import ScopeDescriptor, strict_json_loads; ScopeDescriptor.from_mapping(strict_json_loads(Path(sys.argv[1]).read_bytes()))' \
    "$DESCRIPTOR_PATH"
  DESCRIPTOR_DIGEST="$(env -u GIT_INDEX_FILE ../../.venv/bin/python -c \
    'from pathlib import Path; import hashlib,sys; print("sha256:"+hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())' \
    "$DESCRIPTOR_PATH")"
  printf '%s\n' "$DESCRIPTOR_DIGEST" | grep -Eq '^sha256:[0-9a-f]{64}$'
  env -u GIT_INDEX_FILE git add -- "$DESCRIPTOR_PATH"
  test "$(env -u GIT_INDEX_FILE git diff --cached --name-only)" = "$DESCRIPTOR_PATH"
  env -u GIT_INDEX_FILE git commit -m \
    'coord(director): bind ChatGPT Task 1 singular Lane-V scope'
  D_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
  test "$(env -u GIT_INDEX_FILE git rev-parse "${D_SHA}^1")" = "$C_SHA"
  test "$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r "$D_SHA")" = "$DESCRIPTOR_PATH"
)
```

The explicit subshell uses `../../.venv/bin/python` for the trusted root
virtualenv and cannot resolve the descriptor against shared-root `main`.

- [ ] **Step 3: Generate and commit canonical request-only `T`.**

```bash
(
  cd "$WT"
  DESCRIPTOR_PATH=coordination/verification/scopes/f1e1ad5f-cb1b-4650-93ad-bf8701069f32.json
  D_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
  test "$(env -u GIT_INDEX_FILE git rev-parse "${D_SHA}^1")" = "$C_SHA"
  DESCRIPTOR_DIGEST="$(env -u GIT_INDEX_FILE ../../.venv/bin/python -c \
    'from pathlib import Path; import hashlib,sys; print("sha256:"+hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())' \
    "$DESCRIPTOR_PATH")"
  REQUEST_SEND_OUTPUT="$(env -u GIT_INDEX_FILE coordination/bin/send-event \
    director operator verify-request \
    'verify ChatGPT Task 1 singular Lane-V candidate' <<EOF
Event type: verify-request
Task-board: chatgpt-local-reprepare-task1-singular-lanev-2026-07-16
Protocol wave: 2
Reviewed head: $C_SHA
Reviewed base: $P_SHA
Lane-V-Scope: $DESCRIPTOR_PATH@$DESCRIPTOR_DIGEST
Frozen Codex source head (provenance only): 3dcff96948003d510451266b017895b42bd73c2e
Frozen Claude source head (provenance only): 233ef8126bc75dc6a2a13adcb70810b619faa85c
Provider process attempts authorized: 0
Receipt mutations authorized: 0

## Exact Next Trigger

Operator remains blocked until coordinator commits a later activation route
after Opus Stage A terminally clears. That route must bind this exact request,
P/C/D, descriptor digest, request blob, prospective attempt key, and one
complete Operator provider token. No local review, provider attempt, receipt
action, or verdict starts from this request alone.
EOF
  )"
  REQUEST_PATH="${REQUEST_SEND_OUTPUT#created }"
  REQUEST_PATH="${REQUEST_PATH%% (*}"
  case "$REQUEST_PATH" in
    coordination/mailbox/sent/*-director-to-operator-verify-request.md) ;;
    *) exit 1 ;;
  esac
  env -u GIT_INDEX_FILE git add -f -- "$REQUEST_PATH"
  test "$(env -u GIT_INDEX_FILE git diff --cached --name-only)" = "$REQUEST_PATH"
  env -u GIT_INDEX_FILE git commit -m \
    'coord(director): request ChatGPT Task 1 singular verification'
  T_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
  test "$(env -u GIT_INDEX_FILE git rev-parse "${T_SHA}^1")" = "$D_SHA"
  test "$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r "$T_SHA")" = "$REQUEST_PATH"
)
```

- [ ] **Step 4: Resolve structural and prompt authority without state.**

Inside an explicit `(cd "$WT" && ...)` subshell, use the trusted
`../../.venv/bin/python` to run an inline check that constructs one
`ReviewRequest` with `reviewed_head=C`, `reviewed_base=P`, trigger commit `T`,
trigger path `$REQUEST_PATH`, profile `codex-lane-v`, and empty authorization
source. It must:

1. call `resolve_authoritative_scope()`;
2. require the exact descriptor task ID, digest, base, trigger identity,
   seven requirement paths, and 22 changed paths;
3. require exact status/path equality from Task 3;
4. call state-free `resolve_provider_authoritative_scope()` and require its
   prompt authority path/blob/digests agree with the committed content-addressed
   authority object, then compute the exact attempt key and provider-resolved
   scope digest with `compute_attempt_key()` and `compute_scope_digest()` over
   that provider-resolved scope;
5. derive the primary repository root from `git rev-parse --git-common-dir`,
   append `.codex/runtime/opus-review-receipts/v1`, remove the `opr1:` prefix
   from the exact `ATTEMPT_KEY`, and use only `test ! -e` to require prospective
   `ATTEMPT_DIGEST.json` and `ATTEMPT_DIGEST.lock` absent;
6. print only content-free IDs/digests.

It must not call `review()`, enter `ReceiptStore.lock_attempt()`, create a
receipt-store directory, instantiate `ReceiptStore.for_repo()`, invoke Claude,
or mutate runtime state. Capture the exact attempt key and provider-resolved
scope digest for Task 5.

- [ ] **Step 5: Return the exact construction evidence to coordinator.**

Refresh mailbox and HEAD. If unchanged, report `P`, `M1`, `C`, `D`, `T`,
descriptor path/digest, request path/blob, expected tree OIDs, 22-path digest,
focused test result, prospective attempt key, provider-resolved scope digest,
prompt-authority facts, and zero provider/receipt state. `T` itself is the
durable baton; do not create a second verify-request.

### Task 5: Clear Stage A and activate exactly one Operator attempt (`coordinator`)

**Files:**

- Modify:
  `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-director-candidate.json`
- Modify:
  `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-operator-lanev.json`
- Create: one canonical coordinator activation route under
  `coordination/mailbox/sent/`

**Interfaces:**

- Consumes: exact `P/C/D/T`, terminal Opus Stage-A closeout, and absent
  prospective receipt/lock.
- Produces: activation route `A` with Director done, Pair-A Operator active,
  and one complete trigger-bound provider Side-Effect Executor Token.

- [ ] **Step 1: Require terminal Stage-A evidence.**

Read the latest Stage-A verification report and coordinator closeout body, not
counts. Require a terminal durable state that releases Operator2 and leaves no
active Stage-A provider/receipt action. If Stage A is blocked, active, NITS, or
FAIL without terminal coordinator disposition, stop; no ChatGPT provider token
may be authored.

- [ ] **Step 2: Re-resolve exact candidate authority provider-free.**

Repeat Task 4 Step 4 against immutable `T/C/P`. Require the same attempt key,
provider-resolved scope digest, descriptor digest, request blob, prompt
authority, and absent prospective receipt/lock. Any drift stops; do not delete
or repair state.

- [ ] **Step 3: Transition capacity and author activation route `A`.**

Change the Director packet to `done` with exact `P/M1/C/D/T` evidence. Change
the Operator packet to `active` with:

- `verify_request: REQUEST_PATH`;
- `target_commit: C`;
- `commit_range: P..C`;
- `scope_files`: the 22 exact paths plus descriptor path;
- dependency on the now-done Director packet;
- acceptance text covering every design §8 failure case.

The route's Side-Effect Executor Token must contain all required fields:

- `side_effect_id`: `chatgpt-task1-singular-lanev-opus-2026-07-16`;
- `executor`: `operator`;
- `target`: exact candidate worktree, `P/C/D/T`, descriptor digest, request
  path/blob, prospective attempt key, provider-resolved scope digest,
  prompt-authority facts, and the single review command;
- `allowed_command_class`: primary read-only Codex Lane V, exactly one
  `opus_review_bridge.py review`, one reconciliation, one verification-report
  publication, one report-only local commit/candidate-ref advance, and read-only
  postchecks;
- `preflight`: terminal Stage A, exact authority resolution, no newer route,
  clean candidate, absent receipt/lock, and no prior attempt;
- `stop_if_newer_mail_or_live_target_satisfied`: stop on any newer ownership,
  attempt, receipt, ref, descriptor, trigger, candidate, or Stage-A drift;
- `postcheck`: exact receipt/reconciliation/report identities, report commit
  parent/path, one candidate-ref advance from `T` to `V`, and zero retry;
- `observer_seats`: `director`, `director2`, `operator2`, `coordinator2`;
- `final_closeout_owner`: `coordinator`;
- `non_goals`: no retry, fallback, credential entry, implementation edit,
  integration, push, remote publication, cleanup, cursor, lock, unrelated lane,
  or mailbox publication beyond the one verification report.

The token binds exactly this command shape and no second attempt:

```bash
WT=/Users/hyungkoookkim/Pipeline/.worktrees/chatgpt-task1-singular-lanev-candidate-2026-07-16
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  "$WT/scripts/opus_review_bridge.py" review \
  --repo-root "$WT" \
  --head "$C_SHA" \
  --base "$P_SHA" \
  --verify-request-commit "$T_SHA" \
  --verify-request-path "$REQUEST_PATH" \
  --review-profile codex-lane-v \
  --transport-profile anthropic-claude-existing-session-v1
```

No `--authorization-source` is added. The bridge resolves standing policy only
after structural and prompt validation.

- [ ] **Step 4: Validate `A`.**

Run capacity, route validation, Protocol Doctor, Wave 2, mailbox, lock, receipt,
and diff checks. Commit only the two packet transitions plus one route. A
validator failure leaves Operator blocked.

### Task 6: Independently verify `P..C` and publish one verdict (`operator`)

**Files:**

- Read: candidate `P..C`, descriptor `D`, request `T`, correction design/plan,
  original approved design/plan, and activation route `A`
- Create: one canonical Operator verification report under
  `coordination/mailbox/sent/`

**Interfaces:**

- Consumes: one lawful `T` plus activation `A`.
- Produces: exactly one lane-v-report/v2 GO/NITS/FAIL structurally bound to
  `C/P`, committed as report-only child `V` of `T`. Frozen source heads appear
  only as provenance.

- [ ] **Step 1: Re-derive structural authority.**

Operator independently repeats Tasks 2-4 read-only checks: ref identities,
base blobs/modes, merge-tree OIDs, parent order, ancestry, exact normalized
22-status/path union, clean candidate, descriptor schema/digest, request
field counts, prompt authority, prospective attempt key, provider-resolved
scope digest, receipt/lock absence, and all design §8 stop cases. Do not trust
Director's summary.

- [ ] **Step 2: Run the path-equivalent worktree tests and primary Lane V analysis.**

```bash
(
  cd "$WT"
  env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
    tests/unit/test_chatgpt_pro_consult.py \
    tests/unit/test_protocol_prompt_sync.py -q
)
```

Review the actual `P..C` diff against approved design E1-E9, the accepted
whitespace-split unnamed-base64 residual, and the correction design failure
table. This direct command uses the root virtualenv through the fixed worktree
path. The bridge later executes the descriptor's exact `.venv/bin/python`
command inside its immutable snapshot, where it installs the same trusted
virtualenv as `.venv`. Record a provisional Codex verdict internally; do not
expose it to Opus.

- [ ] **Step 3: Run the token's exact Opus command once.**

Run only the command bound in `A`. Do not retry, change transport, add an
authorization source, or launch a substitute. Capture the normalized receipt,
model, status, findings, scope digest, and failure stage.

- [ ] **Step 4: Reconcile every outcome.**

- `pass`: reconcile with the provisional Codex verdict and zero findings.
- `issues`: disposition every finding as confirmed, evidence-backed disproved,
  or unresolved. Confirmed blocking/unresolved relevant findings force FAIL;
  confirmed minor findings force at least NITS.
- `unavailable` or uncertain/partial delivery: reconcile when the bridge
  lawfully permits, record the exact degraded reason, use final verdict FAIL
  for this Task 1 independence gate, and do not retry. A later user-authorized
  alternative non-author harness requires a new route rather than reusing this
  attempt.

The reconciliation guard must agree with the final attestation. No raw prompt
or response is persisted.

- [ ] **Step 5: Publish one canonical report.**

From an explicit `cd "$WT"` subshell, use
`coordination/bin/send-event operator all verification-report` with a subject
ending `commit $C_SHA`, so the generated H1 contains the full reviewed head.
The body has findings first, one exact `VERDICT: GO|NITS|FAIL`, an
`## Evidence` block with literal `$ command` and Unicode `→ result` lines, and
an `## Verification Attestation` block containing:

- `Verification schema: lane-v-report/v2`;
- exactly one `Reviewed head: C` and one `Reviewed base: P`;
- the exact descriptor authority and `T` trigger commit/path/blob;
- the exact Opus receipt ID and Opus scope digest;
- topology/tree/path/test/receipt/provider evidence and the reconciled finding
  disposition.

Include `H_CODEX` and `H_CLAUDE` only under `Source provenance`; never present
either as an additional reviewed head/base. End with `Exact Next Trigger`
returning to coordinator. The publication gate must validate the live receipt
before staging. Capture `send-event`'s one-line output as `REPORT_SEND_OUTPUT`,
then commit only that staged report from the exact candidate worktree:

```bash
(
  cd "$WT"
  REPORT_PATH="${REPORT_SEND_OUTPUT#created }"
  REPORT_PATH="${REPORT_PATH%% (*}"
  case "$REPORT_PATH" in
    coordination/mailbox/sent/*-operator-to-all-verification-report.md) ;;
    *) exit 1 ;;
  esac
  test "$(env -u GIT_INDEX_FILE git diff --cached --name-only)" = "$REPORT_PATH"
  env -u GIT_INDEX_FILE git commit -m \
    'coord(operator): report ChatGPT Task 1 singular verification'
  V_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
  test "$(env -u GIT_INDEX_FILE git rev-parse "${V_SHA}^1")" = "$T_SHA"
  test "$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r "$V_SHA")" = "$REPORT_PATH"
  test -z "$(env -u GIT_INDEX_FILE git status --porcelain=v1)"
)
```

This is the sole authorized candidate-ref advance after `T`. Operator edits no
implementation, descriptor, request, or other candidate artifact.

### Task 7: Consume GO and resume original integration lineage (`coordinator` then `director`)

**Files:**

- Read: Task 6 report and original approved integration plan
- Later merge on `main`: immutable `H_CODEX`, then immutable `H_CLAUDE`
- Never merge: `M1`, `C`, `D`, `T`, or `V`

**Interfaces:**

- Consumes: binding Task 6 GO only.
- Produces: permission to resume the original approved plan at Task 2, subject
  to exact reuse proof. NITS/FAIL does not reach this task.

- [ ] **Step 1: Gate strictly on report outcome.**

Require a schema-valid, committed GO for exact `P..C`, a completed non-author
Opus result, fully reconciled findings, and no newer invalidating route. NITS,
FAIL, unavailable, uncertain delivery, stale receipt, or a different range
stops. A gate script alone is not correctness evidence.

Resolve `V_SHA` from the fixed candidate branch, require `V^1=T`, and require
its diff to contain exactly the one canonical Operator report path. Read that
committed report with `git show "${V_SHA}:${REPORT_PATH}"`; do not substitute a
mutable worktree copy or a chat summary.

- [ ] **Step 2: Prove integration-main equivalence to `P` on all 22 paths.**

Before original Task 2, set `PRE_MAIN` to the current `main` HEAD and run
`git diff --quiet P PRE_MAIN --` with all 22 exact paths. Also compare
`git ls-tree` mode/blob entries. Any difference invalidates review reuse and
requires a new routed question; do not resolve through `C`.

- [ ] **Step 3: Run original Tasks 2 and 3 with stronger parent proofs.**

Merge only `H_CODEX` into `PRE_MAIN` with no fast-forward, producing `I1`; then
merge only `H_CLAUDE` into `I1`, producing `I2`. Require:

```bash
I1_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^1^{commit}')"
I2_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
test "$(env -u GIT_INDEX_FILE git rev-list --parents -n 1 "$I1_SHA")" = "$I1_SHA $PRE_MAIN $H_CODEX"
test "$(env -u GIT_INDEX_FILE git rev-list --parents -n 1 "$I2_SHA")" = "$I2_SHA $I1_SHA $H_CLAUDE"
env -u GIT_INDEX_FILE git merge-base --is-ancestor "$H_CODEX" "$I2_SHA"
env -u GIT_INDEX_FILE git merge-base --is-ancestor "$H_CLAUDE" "$I2_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$M1_SHA" "$I2_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$C_SHA" "$I2_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$D_SHA" "$I2_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$T_SHA" "$I2_SHA"
! env -u GIT_INDEX_FILE git merge-base --is-ancestor "$V_SHA" "$I2_SHA"
```

Compare all 22 mode/blob entries between `C_SHA` and `I2_SHA`; they must be
identical.
Any conflict or mismatch stops with no hand resolution.

- [ ] **Step 4: Complete the original coherence and smoke tasks.**

Resume original Tasks 4 onward. Only after the original architecture-coherence
task may the integrated-main smoke gate run. Candidate `C` is never used as an
integration parent and is not cleaned up without a separate route.

## Failure artifact rule

At any stop condition, the current owning seat emits at most one bounded
coordination artifact naming the exact failed check, owner, immutable inputs,
commands/output, prohibited next actions, and `Exact Next Trigger`. It does not
repair across authority boundaries, fabricate a descriptor/range, or create
green-looking status churn.

## Exact Next Trigger

After this plan and its companion design are committed, coordinator returns the
pair to the user-principal for separate explicit approval. Until approval and a
new validated Task 1 route exist, do not create candidate refs/worktrees,
merges, packets, descriptors, verify-requests, provider attempts, receipts,
reports, or verdicts.
