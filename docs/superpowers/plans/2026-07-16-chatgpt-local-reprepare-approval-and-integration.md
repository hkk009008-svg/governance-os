# ChatGPT Local Re-prepare Approval-and-Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Seat execution note:** this is a governance-integration plan. Tasks name
> the responsible seat (coordinator / director / operator). A seat executes its
> task inside its own authority (its `.claude/skills/` or `.codex/agents/`
> role); a dispatched subagent may run read-only evidence steps only.

**Goal:** lawfully review and integrate the two frozen halves of the ChatGPT
Pro local re-prepare change — `codex/chatgpt-local-reprepare-flexibility-2026-07-16`
@ `3dcff96` (guard + Codex surfaces) and
`codex/chatgpt-pro-claude-surface-wip-2026-07-16` @ `233ef81` (Claude-tree
mirror) — into `main`, closing the recovery plan's terminal ChatGPT
disposition as `integrated-reviewed`.

**Architecture:** no new code. The change is already implemented, tested, and
frozen; this plan adds the required independent cross-model review, two
`--no-ff` merges in dependency order (canonical model first, mirror second),
and one coherence commit (sync-test tuple extension + `ARCHITECTURE.md`
anchors) so `main` ends drift-free in both trees.

**Tech Stack:** git (shared hot tree discipline), pytest, `scripts/ci_smoke.py`,
four-seat coordination mailbox.

**Design:** `docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-design.md`
(problem evidence, lifecycle boundary, detector split, abuse-case table E1-E9,
accepted residual).

## Global Constraints

- **Approval gate:** execution starts only after the user-principal explicitly
  approves the design document and this plan (Frozen ChatGPT Approval
  Firewall, mailbox event 2026-07-16T04:59:40Z). This plan's existence is not
  approval.
- **Sequencing:** the coordinator sequences this plan relative to the recovery
  campaign (`docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md`);
  it must not preempt the ROOT-COMPACT release or Stage-A corrections without
  an explicit coordinator route.
- **Frozen heads are immutable:** integrate by merge only — no rebase, no
  cherry-pick, no history rewrite, no re-commit of equivalent diffs.
- **Git hygiene:** every git command prefixed `env -u GIT_INDEX_FILE`; commits
  use explicit pathspecs; immediately before every commit re-run
  `git log --oneline -5` and read `coordination/mailbox/sent/` for newer
  events (Rule #7); bare `git commit`/`git add -A` are forbidden
  (R-WIP-POLLUTION).
- **No push, no publication, no provider attempt, no receipt/runtime
  mutation** anywhere in this plan; push remains user-gated after the
  operator's GO (R-VERIFY-THEN-PUSH).
- **Baselines (verified 2026-07-16 @ 96aa0b2):**
  `pytest tests/unit/test_chatgpt_pro_consult.py` → 249 passed;
  `pytest tests/unit/test_protocol_prompt_sync.py` → 51 passed.
  Frozen-branch evidence (owner handoff): both files together → 309 passed.

---

### Task 1: Independent cross-model review of both frozen heads (coordinator routes; operator-lane reviewer executes)

**Files:**
- Read: `docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-design.md`
- Read: `docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md`
- Create: one mailbox `verification-report` under `coordination/mailbox/sent/`

**Interfaces:**
- Consumes: frozen heads `3dcff96` and `233ef81`; design abuse-case table E1-E9.
- Produces: a committed mailbox verification-report with verdict GO/NITS/FAIL
  naming BOTH heads. Task 2 consumes the GO.

- [ ] **Step 1 (coordinator): route the review.** Trigger:

```bash
coordination/bin/codex-seat coordinator -- "route the independent review defined in docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md Task 1"
```

The coordinator names the reviewer. Independence requirement (ADR-019 /
R-INDEPENDENCE): the frozen implementation was Codex-authored, so the reviewer
must be a non-author harness pass — a Claude cold-context reviewer, or Codex
Lane V paired with its blind-Opus advisory where that machinery is routed. A
Codex-only self-review of its own diff does not discharge the gate.

- [ ] **Step 2 (reviewer): re-derive the evidence, do not trust the handoff.**

```bash
env -u GIT_INDEX_FILE git diff 560a95d..3dcff96 --stat    # expect exactly the 16-path manifest
env -u GIT_INDEX_FILE git diff 96aa0b2..233ef81 --stat    # expect exactly the 7-path mirror
env -u GIT_INDEX_FILE git diff 560a95d..3dcff96           # full read
env -u GIT_INDEX_FILE git diff 96aa0b2..233ef81           # full read
```

- [ ] **Step 3 (reviewer): verify the diff against the design's abuse-case
  table E1-E9** — for each row, locate the enforcing test in the diff and
  confirm the asserted behavior matches the code. Explicitly re-confirm or
  reject the accepted residual (whitespace-split unnamed base64) from design
  §3.

- [ ] **Step 4 (reviewer): fresh test run on the frozen head** (worktree
  checkout; never switch the shared root):

```bash
env -u GIT_INDEX_FILE git worktree add .worktrees/reprepare-review 3dcff96
cd .worktrees/reprepare-review && env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py tests/unit/test_protocol_prompt_sync.py -q
```

Expected: `309 passed`. Then remove the worktree:

```bash
cd /Users/hyungkoookkim/Pipeline && env -u GIT_INDEX_FILE git worktree remove .worktrees/reprepare-review
```

- [ ] **Step 5 (reviewer): land the verification-report** as a committed
  mailbox event naming both heads, the E1-E9 disposition per row, and the
  verdict. **GO is the gate for Task 2.** NITS → fix-forward tasks are added
  to this plan by the coordinator before merging. FAIL → stop; the plan
  returns to the user-principal.

### Task 2: Merge the Codex half `3dcff96` into main (director)

**Files:**
- Modify (via merge): the 16 manifest paths of `3dcff96`

**Interfaces:**
- Consumes: Task 1 GO report (cite its mailbox path in the merge body).
- Produces: merge commit M1 on `main` carrying the guard, model rules, Codex
  surfaces, and the 11-surface local-correction sync test.

- [ ] **Step 1: preflight (Rule #7 + hold compliance).**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
ls -t coordination/mailbox/sent/ | head -3   # read anything newer than the GO
env -u GIT_INDEX_FILE git status --porcelain  # expect: no unclassified entries beyond known ROOT-COMPACT material
```

- [ ] **Step 2: merge.**

```bash
env -u GIT_INDEX_FILE git merge --no-ff 3dcff96 -m "merge: integrate chatgpt local reprepare correction

Reviewed under docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md Task 1 (GO report: coordination/mailbox/sent/<the Task 1 report filename>). Frozen head preserved by docs/HANDOFF-owner-2026-07-16-chatgpt-local-reprepare.md."
```

Expected: clean merge, no conflicts (the branch bases on `560a95d`, contained
in `main`; if a conflict appears, STOP — the tree moved; re-run Task 2 Step 1
and re-assess rather than resolving ad hoc).

- [ ] **Step 3: verify on merged main.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py -q   # expected: 257 passed
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q  # expected: 52 passed
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py                                    # expected: OK
```

### Task 3: Merge the Claude half `233ef81` into main (director)

**Files:**
- Modify (via merge): the 7 mirror paths of `233ef81`

**Interfaces:**
- Consumes: merge commit M1 (Task 2) already on `main`.
- Produces: merge commit M2; `main` now carries the consultation contract in
  both trees.

- [ ] **Step 1: preflight.** Same three commands as Task 2 Step 1.

- [ ] **Step 2: merge.**

```bash
env -u GIT_INDEX_FILE git merge --no-ff 233ef81 -m "merge: integrate chatgpt pro claude-surface mirror

Companion of the reprepare integration (same Task 1 GO report). Claude tree now carries the consultation contract; sync tuples extended on the shared consultation tests."
```

Expected: clean merge. Both branches touch
`tests/unit/test_protocol_prompt_sync.py` in non-overlapping regions (inserted
test ~line 660 vs tuple extensions ~lines 827-930); git auto-merges. On any
conflict: STOP and re-assess (do not hand-resolve without re-running preflight).

- [ ] **Step 3: verify the combined file carries both halves.**

```bash
grep -c 'test_chatgpt_pro_local_correction_boundary_is_surface_synced' tests/unit/test_protocol_prompt_sync.py   # expected: 1
grep -c '".claude/skills/seat-director/SKILL.md"' tests/unit/test_protocol_prompt_sync.py                        # expected: >= 2
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q                      # expected: 52 passed
grep -c 'R-CONSULT' CLAUDE.md                                                                                    # expected: 1
```

### Task 4: Extend the local-correction sync test to the Claude surfaces (director)

**Files:**
- Modify: `tests/unit/test_protocol_prompt_sync.py` (the `surfaces` tuple of
  `test_chatgpt_pro_local_correction_boundary_is_surface_synced`, ~line 671
  post-merge)

**Interfaces:**
- Consumes: M2 (Claude surfaces on `main` already carry the two policy
  sentences).
- Produces: the local-correction boundary becomes drift-enforced on 17
  surfaces (11 Codex + 6 Claude) — the cross-tree gap that let the Claude tree
  silently lack the contract for three days cannot recur for this rule.

- [ ] **Step 1: extend the tuple.** In
  `test_chatgpt_pro_local_correction_boundary_is_surface_synced`, change the
  `surfaces` tuple to:

```python
    surfaces = (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/protocol/codex/continuation.md",
        "docs/protocol/claude/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".claude/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/chatgpt-pro-consultation/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".claude/skills/seat-director/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
        ".claude/skills/seat-coordinator/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".claude/skills/seat-operator/SKILL.md",
        ".codex/agents/readiness-bridge.toml",
        ".codex/agents/protocol-director.toml",
        ".codex/agents/protocol-coordinator.toml",
        ".codex/agents/protocol-operator.toml",
    )
```

(This mirrors exactly how `233ef81` extended the other three consultation
tests; the Claude-path ordering convention is "Claude twin immediately after
its Codex counterpart".)

- [ ] **Step 2: run the extended test.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
```

Expected: `52 passed`. (A red-first cycle is not reproducible here without
un-merging M2 — the guarded behavior already holds; this step is regression
armor. If it FAILS, a Claude surface is missing a sentence: fix the surface,
not the test.)

- [ ] **Step 3: commit (Rule #7 first).**

```bash
env -u GIT_INDEX_FILE git log --oneline -5 && ls -t coordination/mailbox/sent/ | head -3
env -u GIT_INDEX_FILE git commit -m "test(consult): enforce local-correction boundary on claude surfaces" -- tests/unit/test_protocol_prompt_sync.py
```

### Task 5: ARCHITECTURE.md anchor coherence (director, coordinated with the ROOT-COMPACT owner)

**Files:**
- Modify: `ARCHITECTURE.md:64-66` (module-map rows) and `ARCHITECTURE.md:8`
  (freshness stamp)

**Interfaces:**
- Consumes: M1 (the model file gained 2 lines; committed anchors 547/773/857
  became stale).
- Produces: truthful module-map anchors; smoke ARCH-FRESHNESS stays green.

**Coordination precondition:** `ARCHITECTURE.md` currently carries an
uncommitted working-tree edit with exactly this content, classified as
ROOT-COMPACT material (director2). Execute this task only after the
ROOT-COMPACT disposition has preserved or released that dirty state, and
confirm with the coordinator which seat commits it. If the dirty edit is still
present and byte-identical to Step 1's target, committing it here (with the
stamp bump) IS the disposition for this path — record that in the commit body.

- [ ] **Step 1: set the three rows** (final content, matching the merged
  model file — verify first with `grep -n 'LEDGER_CLI_BRIDGE = ' scripts/codex_protocol_model.py`,
  expected `549`):

```markdown
| `LEDGER_CLI_BRIDGE` | `scripts/codex_protocol_model.py:549` | Executable model data for Pipeline-to-evidence-ledger Codex startup. |
| `render_r_independence` | `scripts/codex_protocol_model.py:775` | Renders the standing R-INDEPENDENCE contract into Codex harness output. |
| `render_ledger_start_guard` | `scripts/codex_protocol_model.py:859` | Renders guard guidance into readiness output. |
```

- [ ] **Step 2: bump the stamp** at `ARCHITECTURE.md:8` — replace the current
  short SHA in `*Last verified: 2026-07-16 @ 933871b*` with M2's short SHA
  (from `env -u GIT_INDEX_FILE git rev-parse --short HEAD` after Task 4's
  commit), keeping the date `2026-07-16`.

- [ ] **Step 3: verify + commit.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py   # expected: OK (incl. ARCH-FRESHNESS PASS)
env -u GIT_INDEX_FILE git log --oneline -5 && ls -t coordination/mailbox/sent/ | head -3
env -u GIT_INDEX_FILE git commit -m "docs(arch): refresh codex_protocol_model anchors after reprepare merge" -- ARCHITECTURE.md
```

### Task 6: Operator verification + terminal disposition (operator, then coordinator)

**Files:**
- Create: one operator mailbox `verification-report` (GO/NITS/FAIL over the
  full Task 2-5 range)
- Create/modify: the coordinator's disposition record per the recovery plan's
  terminal-ChatGPT-disposition task

**Interfaces:**
- Consumes: the Task 2-5 commit range on `main`.
- Produces: the closed pair loop (operator GO) and the recovery campaign's
  ChatGPT unit at terminal status `integrated-reviewed` — the prerequisite for
  compact Phase-3 convergence.

- [ ] **Step 1 (operator): independent post-merge verification** of the whole
  range (impl≠verifier): fresh run of the two test files (expected `257` and
  `52` passed), `scripts/ci_smoke.py` (expected OK), and a diff read of
  M1..HEAD confirming scope matches this plan. Land the verification-report.

- [ ] **Step 2 (coordinator): record the terminal disposition**
  `integrated-reviewed` for the ChatGPT unit, superseding the frozen-firewall
  hold for this unit only, and name the exact next trigger for the recovery
  campaign. Push remains user-gated and is NOT part of this plan.
