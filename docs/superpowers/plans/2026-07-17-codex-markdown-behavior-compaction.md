# Codex Markdown Behavior Compaction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace duplicated Codex behavior doctrine with six small, directly usable Markdown surfaces while retaining triggered authority and side-effect safeguards.

**Architecture:** Use `AGENTS.md` as the thin router, the Codex continuation document as the runtime adapter, the four-seat skill as the orientation entrypoint, and each seat skill as a seat-only delta. Shared lifecycle rules point to `scripts/codex_protocol_model.py` or the existing agent-neutral protocol instead of being copied.

**Tech Stack:** Markdown, Git, ripgrep, repository documentation validators, pytest

## Global Constraints

- Modify only the six approved Codex behavior files plus the approved design and plan notes.
- Do not modify Python, TOML, tests, Claude or three-way surfaces, shared doctrine, mailbox state, templates, formats, or target-specific adapters.
- Preserve user authority, mailbox-body truth, operator non-authorship, coordinator no-production-fix authority, `env -u GIT_INDEX_FILE`, and separately gated external effects.
- Use one owner, one pointer, and one local consequence; do not paraphrase removed duplication into new duplication.
- Do not stage, commit, push, merge, consume mail, or create protocol artifacts without separate authority.
- Refresh Git state before each edit because Claude may be changing the shared tree concurrently.

---

### Task 1: Capture the hot-tree baseline

**Files:**
- Read: `AGENTS.md`
- Read: `docs/protocol/codex/continuation.md`
- Read: `.agents/skills/four-seat-protocol/SKILL.md`
- Read: `.agents/skills/seat-director/SKILL.md`
- Read: `.agents/skills/seat-operator/SKILL.md`
- Read: `.agents/skills/seat-coordinator/SKILL.md`

**Interfaces:**
- Consumes: Approved design at `docs/superpowers/specs/2026-07-17-codex-markdown-behavior-compaction-design.md`
- Produces: Current HEAD, working-tree state, baseline line counts, and baseline focused-test result

- [x] **Step 1: Refresh shared-tree state**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -3
```

Expected: identify all concurrent edits before touching a scoped file; never overwrite an unexpected edit.

- [x] **Step 2: Record scoped baseline size**

Run:

```bash
wc -l AGENTS.md docs/protocol/codex/continuation.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md
```

Expected baseline: approximately 1,867 lines across the six files; use the live output as authority.

- [x] **Step 3: Run the current wording sentry**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py -q
```

Expected baseline at approved HEAD `c5ac2a5`: `58 passed`. If HEAD moved, record the live result without fixing non-Markdown files.

### Task 2: Thin the router and runtime adapter

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/protocol/codex/continuation.md`

**Interfaces:**
- Consumes: `scripts/codex_protocol_model.py`, `docs/protocol/agents/`, and the repo doc map as canonical pointers
- Produces: One always-loaded router and one Codex-native runtime adapter with no copied seat lifecycle

- [x] **Step 1: Refresh state and re-read both current files**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -3
sed -n '1,520p' AGENTS.md
sed -n '1,430p' docs/protocol/codex/continuation.md
```

Expected: reconcile any Claude changes before applying the scoped rewrite.

- [x] **Step 2: Rewrite `AGENTS.md` as the thin router**

Retain these responsibilities:

1. Document purpose and precedence with `ARCHITECTURE.md` as factual truth.
2. Codex default readiness-bridge mode and explicit-seat trigger.
3. Four risk tiers and scope-aware skill/tool selection.
4. Repo doc map and pull-on-demand loading.
5. Agent-neutral implementation safeguards that must be active before task discovery: R-EVIDENCE, R-MEASURE, R-VERIFY-TIER, R-INDEPENDENCE, R-ORCH, R-BRIEF, R-PID, R-SKILL, Rules #12/#13, and hot-tree/WIP/push rules.
6. A short four-seat pointer that states only user precedence, body-first mailbox decisions, non-author operator verdict authority, coordinator no-production-fix authority, separately gated side effects, and the canonical model path.

Delete copied Codex lifecycle, pair-contract, capacity, subagent-reporting, emergency, disagreement, and executor-token bodies. Link to the continuation adapter, four-seat skill, and canonical model instead.

- [x] **Step 3: Rewrite `continuation.md` as the runtime adapter**

Use these sections only:

1. Purpose and source order.
2. Mode selection: readiness bridge, live seat, coordinator.
3. Codex-native mapping of Claude-only mechanics.
4. Triggered startup commands for each mode.
5. Mailbox/cursor and Git-index boundaries.
6. Side-effect boundary and subagent non-inheritance.
7. Optional tools and verification commands.
8. Canonical pointers and related files.

Keep the exact ChatGPT Pro advisory pointer once. Keep the compact-pair pointer and local authority consequences once. Replace detailed emergency, disagreement, blocked-wave, reviewer-result, capacity, pair-contract, and token schemas with canonical pointers.

- [x] **Step 4: Check router/adapter structure**

Run:

```bash
git diff --check -- AGENTS.md docs/protocol/codex/continuation.md
rg -n '^#{1,3} ' AGENTS.md docs/protocol/codex/continuation.md
rg -n 'Subagent utilization decision|direct/no-op because' \
  AGENTS.md docs/protocol/codex/continuation.md
```

Expected: no whitespace errors; headings match the responsibilities above; the final `rg` returns no matches.

### Task 3: Thin the four-seat entrypoint

**Files:**
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`

**Interfaces:**
- Consumes: Runtime modes from the continuation adapter and seat deltas from the three concrete seat skills
- Produces: A compact triggered orientation checklist

- [x] **Step 1: Refresh state and re-read the current skill**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -3
sed -n '1,380p' .agents/skills/four-seat-protocol/SKILL.md
```

Expected: no unexpected concurrent edit is overwritten.

- [x] **Step 2: Rewrite the umbrella skill**

Use these sections only:

1. Trigger and purpose.
2. Source order and mode selection.
3. Readiness-bridge checklist.
4. Live-seat checklist, including same-seat handoff first.
5. Coordinator checklist.
6. Shared boundaries: body-first mail, cursor ownership, `env -u GIT_INDEX_FILE`, subagent non-inheritance, and separately gated effects.
7. Seat-skill, ledger-adapter, canonical-model, and advisory-tool pointers.

Do not repeat seat lifecycle, capacity split, pair contract, emergency handling, disagreement handling, reviewer handling, executor-token fields, or a recorded subagent/no-op decision.

- [x] **Step 3: Check entrypoint structure**

Run:

```bash
git diff --check -- .agents/skills/four-seat-protocol/SKILL.md
rg -n '^#{1,3} ' .agents/skills/four-seat-protocol/SKILL.md
rg -n 'Subagent utilization decision|direct/no-op because' \
  .agents/skills/four-seat-protocol/SKILL.md
```

Expected: no whitespace errors; the final `rg` returns no matches.

### Task 4: Reduce each concrete seat skill to its local delta

**Files:**
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`

**Interfaces:**
- Consumes: Shared orientation and boundaries from the four-seat skill; lifecycle grammar from `scripts/codex_protocol_model.py`
- Produces: Three directly usable, seat-specific skills

- [x] **Step 1: Refresh state and re-read all three skills**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -3
sed -n '1,300p' .agents/skills/seat-director/SKILL.md
sed -n '1,300p' .agents/skills/seat-operator/SKILL.md
sed -n '1,280p' .agents/skills/seat-coordinator/SKILL.md
```

Expected: reconcile current content before rewriting.

- [x] **Step 2: Rewrite the director skill**

Keep only: trigger/role, first commands, cross-cutting classification, R-BRIEF evidence, implement-versus-orchestrate choice, co-sign/lock duties, verify-request handoff, lost-lock behavior, prohibitions, and canonical/template pointers.

- [x] **Step 3: Rewrite the operator skill**

Keep only: trigger/role, first commands, lawful committed verify-request requirement, non-authorship, Lane V evidence, mutation checks when relevant, NITS recheck, GO/FAIL publication, lock release, prohibitions, and canonical/report-format pointers.

- [x] **Step 4: Rewrite the coordinator skill**

Keep only: trigger/role, first commands, capacity/route validation, reconciliation/gate evidence, no-op fast path, allowed writes, no-production-fix prohibition, side-effect routing boundary, and canonical pointers.

- [x] **Step 5: Check seat-skill structure and removed ceremony**

Run:

```bash
git diff --check -- \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md
rg -n '^#{1,3} ' \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md
rg -n 'Subagent utilization decision|direct/no-op because' \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md
```

Expected: no whitespace errors; every heading is seat-specific; the final `rg` returns no matches.

### Task 5: Verify scope, safety, and expected contract drift

**Files:**
- Verify: all six scoped Markdown files
- Do not modify: tests or executable protocol surfaces

**Interfaces:**
- Consumes: Completed six-file Markdown diff
- Produces: Scope proof, validation results, and a precise Claude-side test-contract handoff

- [x] **Step 1: Refresh state and inspect the exact diff**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git diff --stat
env -u GIT_INDEX_FILE git diff -- \
  AGENTS.md docs/protocol/codex/continuation.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md
```

Expected: only the six approved behavior files and the design/plan notes are modified or untracked by this lane.

- [x] **Step 2: Prove the retained safety anchors**

Run:

```bash
rg -n 'user|mailbox|non-author|GO/NITS/FAIL|production fixes|env -u GIT_INDEX_FILE|push|merge|paid|side effect|Subagent' \
  AGENTS.md docs/protocol/codex/continuation.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md
```

Expected: each safeguard has one canonical owner or a clear local consequence, without a copied doctrine block in every file.

- [x] **Step 3: Run Markdown/document validators**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py \
  AGENTS.md docs/protocol/codex/continuation.md \
  .agents/skills/four-seat-protocol/SKILL.md
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: pass, unless a concurrent Claude change independently alters the baseline; classify any failure by exact file and cause.

- [x] **Step 4: Run focused protocol tests and classify failures**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_codex_ledger_bridge.py -q
```

Expected: assertions that require removed duplicated phrases may fail and belong to Claude's contract update. Any failure showing a lost authority boundary, broken link, stale trigger, or ledger boundary is a Codex defect and must be corrected in the six-file scope.

- [x] **Step 5: Report without staging or committing**

Report: files changed, before/after line counts, retained safeguards, validators, focused-test result, and exact stale duplication assertions for Claude. Do not stage, commit, or push.
