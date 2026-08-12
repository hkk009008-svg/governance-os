# Address Cross-Model Analyst Verdict — Remediation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking. Tasks 1–4 are production/shared
> surfaces: each goes through the pair loop (implementer commit → operator
> verification-report GO before the push task). Task 0 already landed in the
> authoring session.

**Goal:** Land the verified subset of the 2026-07-17 cross-model analyst verdict —
honest CI, the real drift fixes, ref-bus wording reconciliation, the route/v1
decision — with the smallest sufficient change set and no new ceremony.

**Architecture:** No new machinery. Every task is a deletion, a test-portability
fix, or a one-sentence wording correction on an existing surface. The one
decision point (route/v1) deletes a dormant island rather than wiring a second
authority.

**Tech stack:** Python 3.13, pytest, GitHub Actions, repo governance scripts.

## STOP-THE-LINE — the tree moved under this plan (2026-07-18 recheck)

During authoring, the shared tree advanced from `8c7f129` to `75fde1d` and was
pushed (`origin/main == main`, 0/0). Three facts override the original premises:

1. **`main` is RED, and the red is NEW.** Local `tests/unit` = **16 failed, 656
   passed, 1 xfailed** at `75fde1d`; CI run `29586188194` = **20 failed** (the 16
   + 2 HOME-path bridge tests + 2 Linux fault-injection). Verified via
   `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q`. This is NOT
   the analyst's pre-compaction 4-failure picture — it is a fresh regression.
2. **The red commit was never verified at its shipped HEAD.** The operator GO in
   `coordination/mailbox/sent/2026-07-17T13-17-10Z-operator-to-director-verification-report.md`
   covers `9766e7c` ("680 passed, 1 xfailed"). `75fde1d`
   ("docs(codex): compact protocol behavior surfaces") was stacked ON TOP of the
   GO'd commit and pushed. `git diff --stat 9766e7c 75fde1d` = the compaction
   alone (AGENTS.md −655, four `.agents/skills/*`, `docs/protocol/codex/continuation.md`
   −498). The 16 failures are `test_protocol_prompt_sync.py` assertions that the
   stripped Codex surfaces no longer satisfy (missing `R-INDEPENDENCE`,
   `Capacity Split Default:`, the behavior-source-map, the "continue internally"
   phrase, etc.). So: **shipped (`75fde1d`) ≠ verified (`9766e7c`)**, an
   R-VERIFY-THEN-PUSH gap.
3. **The break is in the Codex-side active work zone.** The stripped surfaces and
   the sync tests are Codex's compaction; a Codex director/operator pair is
   actively cycling on it (mailbox 13:10–13:17Z). Per the concurrent-collision
   discipline (defer to first-writer; complement disjoint paths only), the Claude
   side does NOT repair AGENTS.md / `.agents/skills` / codex continuation.md.

**Sequencing consequence (FINAL):** every task that could be cleanly
*differential-verified* against the red baseline landed early rather than waiting
for green — the 16 pre-existing Codex prompt-sync failures are orthogonal to
these diffs, so "the failing set is unchanged before/after" is a sound safety
signal even on a red tree. Landed this session (local `main`, 5 commits ahead of
origin, **not pushed**):

- Task 0 (Claude-side doc sync) → `16410e4`
- Task 1 (bridge env-independence) → `dbf36d9`
- Task 2 (delete `--runxfail` step + R4; `.github` staleness) → `341aa95`
- Task 3 (retire descriptor in assembly map) → `ea7cdf4`
- Task 6 (delete dormant route/v1 machinery) → `06e796c`

Independent verification over the whole range `75fde1d..06e796c`: a fresh-context
Lane-V pass returned **GO** (no NITS), and an adversarial pass found **no defects**
in the gate removal, the route deletion, or the bridge-test rewrite (it proved a
strict XPASS still hard-fails the normal run, that no config suppresses it, that
`route_lineage`'s live consumers still import, and that the bridge assertions are
non-vacuous). Suite throughout: 16 failed / 550 passed / 0 xfailed — the 16 are
the Codex desync only.

Still open: **Task 4** (ref-bus wording) is Codex-lane (their executable model;
the Claude side is already conditional). **Task 5** (push) is user-gated and
additionally blocked on Priority 0. The DECISIONS terminal-cleanup closeout
(separate from the route/v1 ADR added here) remains for the coordinator.
**Priority 0 (below) is not ours to execute; it gates the push.**

### Priority 0 (Codex lane / user-coordinated): repair `main` to green

Not a Claude-side task — recorded so the plan's ordering is explicit. Either:
(a) Codex forward-fixes the surface↔test desync introduced by `75fde1d` (restore
the required doctrine phrases to the compacted surfaces, or update the
prompt-sync expectations in the same commit), OR (b) revert `75fde1d` to the
verified `9766e7c` and re-land the compaction through a GO that covers the
actually-shipped HEAD. Surfacing this to the user-principal is the immediate
action; the fix authority is the Codex pair's.

## Adjudication basis (what this plan does and does not address)

Verified by 10 read-only verifier agents + 1 completeness critic + main-context
spot-checks in the authoring session (2026-07-17). Full evidence in the session
transcript; key commands cited inline per task.

**Agreed and planned:** CI red/disconnected (12/12 recent runs failed; local main
6 ahead of origin/main); 2 env-dependent bridge tests; suite-wide `--runxfail`
step is logically backwards and R4 enforces the mistake; 4-of-5 cited drift items
real (descriptor authority in the assembly map, `report-v2` comment, "no pins
yet" comment, 234-test baseline); ref-bus wording unconditional in the executable
model while `refs/threeway/*` is empty locally AND on origin; DECISIONS.md lacks
the terminal-cleanup closeout (fixed in Task 0); route/v1 typed machinery fully
dormant (0 sidecars, 0 production callers).

**Rejected (verified false or already correct — do NOT implement):**
- "`GO → push` lacks the user gate" — refuted: the user push-gate is stated in
  `scripts/codex_protocol_model.py` (lines 53–58, 230, 1084–1085, 1112, 1154),
  CLAUDE.md:249, and director-operator.md. No change.
- "Most of the 2,022-line checker can be deleted" — refuted:
  `scripts/check_doc_claims.py` is ~82% live-worktree gating that feeds
  `ci_smoke`/`status.py`; smoke costs 0.79 s. No deletion.
- Cursor-state reconciliation — nothing to reconcile: all six cursors read `0`
  via the missing-ref default; no cursor blobs exist.
- R6 in `check_no_ceremony.py` — keep as-is: documented dormant gate with tests;
  fires when `reviewer-result/1` blocks appear.

**Deferred (real but latent, cheap, do only on demand):** shallow-clone
awareness for the SHA-ref baseline gate (`ci_smoke.py:153–174` /
`check_doc_claims.py:1768`) — CI uses `fetch-depth: 0`, so the hard-fail is
unreachable today; the fix is ~3–6 lines (downgrade to WARNING when
`_repo_state()` reports shallow) if a shallow consumer ever appears.

## Global constraints

- Prefix EVERY git invocation with `env -u GIT_INDEX_FILE ` (seat-index
  corruption vector, 2026-06-12).
- Commit with explicit pathspecs only — never bare `git commit -a` / `git add -A`
  (R-WIP-POLLUTION). Re-run `git log -3` + mailbox check immediately before each
  commit (R-HOT-TREE).
- One commit per task. No push before an operator verification-report GO
  (R-VERIFY-THEN-PUSH); push itself is user-gated (Task 5).
- `scripts/check_no_ceremony.py` is an enforcement gate: Task 2's diff SHOULD get
  cross-model review per R-INDEPENDENCE (the analyst's recommendation itself
  serves as the design-time independent enumeration; the per-task operator GO
  discharges the second point).
- After every task: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
  → `OK`, and `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q`
  → `555 passed, 1 xfailed` (count may shift if a task adds/removes tests; paste
  the literal summary line).

---

### Task 0: Claude-side doc sync (DONE — commit `32c8564`, differential-verified, not pushed)

**Status: landed.** Differential-verified on the red baseline — the
`test_protocol_prompt_sync` failing set was byte-identical (16 failed / 656
passed) before and after, and no test outside prompt-sync reacted. Not pushed
(push waits for green + user gate).

**Files changed (explicit pathspecs):**
- `.claude/skills/seat-coordinator/SKILL.md:69,87` — retired the stale
  "gate executes ZERO tests / until FIX-1 lands" caveat; `wave_gate_check.py`
  now executes pins via `pytest --runxfail` (`_run_pytest_selectors`,
  `scripts/wave_gate_check.py:90–102`; check_no_ceremony R3 PASS, verified). The
  two "continue internally" phrases the file must carry (test
  `test_active_surfaces_continue_internally...`, `:1067`) were preserved.
- `docs/templates/claude/implementer.md:88–90` and
  `docs/templates/claude/reviewer.md:123–125,219–221` — removed the retired
  `Lane-V-Scope` trailer/descriptor instructions; trigger authority is the
  committed compact-pair verify-request ("There is no descriptor"). No
  Rule-12/Rule-13 transplant phrase touched. **Residue flagged:** the agents-side
  twins `docs/templates/agents/implementer.md:21` and `docs/templates/agents/reviewer.md`
  still carry `Lane-V-Scope` — a Codex-side cleanup, not mirrored here.

**DECISIONS.md closeout (still missing — analyst item 5 stands):** the Codex side
added a "Compact ChatGPT Pro browser consultation" entry (2026-07-17), but there
is still NO closeout for the terminal compact/capability deletion. Append one
**un-numbered `## <title>` entry** (matching the two most-recent entries' style —
the last NUMBERED ADR is ADR-025; the recent convention is title-only) recording:
live-caller-only terminal cleanup, plan `d434a0d`, implementation `411c2af`
(−34,957 lines), operator GO `2026-07-17T11-03-28Z`; note it supersedes the
live-mechanism prose (`lane-v-report/v3`, `TaskPublicationStore`) of the
un-numbered 2026-07-16 provider-decommission entry without rewriting it. This
entry is coordinator/joint-owned (records a joint deletion), so route it with the
Codex seat rather than treating it as unilateral Claude-side work; DECISIONS.md is
also currently HOT (Codex touched it in `75fde1d`).

- Created: `docs/superpowers/plans/2026-07-17-address-cross-model-verdict.md`
  (this file — the only artifact produced so far).

---

### Task 1: Make the two bridge tests environment-independent

**Files:**
- Modify: `tests/unit/test_codex_ledger_bridge.py:227-237` and `:240-271`
- Test: same file (this IS the test change; no production code)

**Interfaces:**
- Consumes: `target_binding.forbidden_roots()` (returns `list[Path]`, first entry
  is the Content root from `governance.toml [binding] forbidden_roots`);
  `GOVERNANCE_TARGET_PATH` env override (`target_binding.py:30`, local-checkout
  override for the selected target).
- Produces: a suite that passes under any `$HOME` (CI runner parity).

Why these two: `governance.toml` stores `path="~/evidence-ledger"` and
`forbidden_roots=["~/Content"]`; `target_binding.py:57` calls
`Path(raw).expanduser()`, so on the CI runner they become `/home/runner/*` while
the tests hardcode `/Users/hyungkoookkim/*`. These are the only 2 of 15 tests
that fail under a foreign HOME (empirically: 2 failed, 13 passed). The other 13
tests' `/Users` literals assert committed string constants and are portable —
do NOT touch them.

- [ ] **Step 1: Reproduce the CI failure locally**

Run: `env -u GIT_INDEX_FILE HOME=/tmp/foreign-home .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q --tb=line`
Expected: `2 failed, 13 passed` (the two tests below).

- [ ] **Step 2: Derive the forbidden root instead of hardcoding it**

Replace `test_ledger_start_guard_cli_rejects_content_kernel` (lines 227–237) with:

```python
def test_ledger_start_guard_cli_rejects_content_kernel():
    import ledger_start_guard
    import target_binding

    forbidden = target_binding.forbidden_roots()[0]
    result = ledger_start_guard.build_guard(
        seat="operator2",
        root=forbidden,
        kernel=Path("/Users/hyungkoookkim/Pipeline"),
    )

    assert not result.ok
    assert f"Refusing `{forbidden}`" in "\n".join(result.errors)
```

Match the refusal rendering at `ledger_start_guard.py:204-206` — if the guard
renders with `.as_posix()` or a different quote style, mirror it exactly (the
old assertion was a substring match on the rendered path).

- [ ] **Step 3: Pin the target path through the production env seam**

In `test_ledger_start_guard_cli_prints_route_and_first_commands` (lines
240–271): add `monkeypatch` to the signature, create the ledger dir under
`tmp_path`, and set the override before calling `main`:

```python
def test_ledger_start_guard_cli_prints_route_and_first_commands(tmp_path, capsys, monkeypatch):
    import ledger_start_guard

    ledger = tmp_path / "evidence-ledger"
    ledger.mkdir()
    monkeypatch.setenv("GOVERNANCE_TARGET_PATH", str(ledger))
    ...
    assert f"env -u GIT_INDEX_FILE git -C {ledger} status --short --branch" in out
```

Keep the route-file fixture as-is unless the guard demonstrably prints the
route-body path (the CI log proves it prints the target_binding resolution:
CI printed `/home/runner/evidence-ledger`, not the route body's `/Users/...`).

- [ ] **Step 4: Verify under foreign HOME and normally**

Run: `env -u GIT_INDEX_FILE HOME=/tmp/foreign-home .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py -q`
Expected: `15 passed`.
Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q`
Expected: `555 passed, 1 xfailed`.

- [ ] **Step 5: Commit**

```bash
env -u GIT_INDEX_FILE git add tests/unit/test_codex_ledger_bridge.py
env -u GIT_INDEX_FILE git commit -m "test(bridge): derive paths from target_binding, drop owner-HOME literals"
```

---

### Task 2: Delete the suite-wide `--runxfail` step and R4; fix `.github` staleness

**Files:**
- Modify: `.github/workflows/ci.yml:132-136` (delete step), `:15` (comment)
- Modify: `scripts/check_no_ceremony.py:149-158` (delete R4 fn), `:20` (header
  row), `:296-297` (main() call), `:315` (R3/R4 footnote), `:7` (docstring)
- Modify: `.github/pull_request_template.md:9`

**Interfaces:**
- Consumes: nothing from Task 1 (independent; either order).
- Produces: `check_no_ceremony.py` without `rule_ci_runs_runxfail`; ci.yml with
  a single normal pytest step.

Why: `--runxfail` semantics are the exact opposite of the step's intent — it
converts a landed fix (strict XPASS, which the normal `:130` run already fails)
into a silent pass, and converts the one deliberately-deferred R-VERIFY-TIER pin
(`test_route_render_invariance.py:96`) into a hard failure. The coherent
targeted expect-RED pattern already lives in `wave_gate_check.py:90-102`. R4
(grep for the literal `--runxfail` in workflows) enforces the mistake, so step
and rule must go in ONE commit. R4's FAIL message also asserts fictional
"70+ strict-xfail pins" (actual: exactly 1 decorator,
`test_route_render_invariance.py:96`; `test_ceremony_gates.py` matches are
string fixtures). The step's own comment carries the stale "The suite has no
pins yet". Sequencing note (corrected from the analyst): today the step is
skipped-on-red — after push, CI stays red at the NORMAL step on the two bridge
tests until Task 1 lands; only then would this step become the proximate
blocker. Land Tasks 1+2 before Task 5 regardless of order between them.

- [ ] **Step 1: Delete the ci.yml step**

Remove lines 132–136 exactly:

```yaml
      - name: Execute strict-xfail regression pins (--runxfail)
        # ADR-027 FIX-2: run any strict-xfail regression pins with --runxfail so a
        # landed fix (XPASS) fails CI rather than passing silently. The suite has no
        # pins yet; this wires the gate so the FIRST pin added is executed, not declared.
        run: python -m pytest tests/unit --runxfail -q
```

- [ ] **Step 2: Delete R4 from check_no_ceremony.py**

Remove `rule_ci_runs_runxfail` (lines 149–158), the `R4` header row (line 20),
the main() invocation + print (lines 296–297), and reword the R3/R4 footnote
(line 315) to R3-only. Reword the module docstring's line ~7 claim
("wave_gate_check.py READS the inventory `status` string and runs zero…") to
past tense: that was the ADR-027 defect; R3 now guards against regressing to it.
No test covers R4 (`test_ceremony_gates.py` covers only the R6 helper and R1 AST
helpers — verified), so no test edits.

- [ ] **Step 3: Fix the two stale .github facts**

`ci.yml:15`: replace the `Lane-V report-v2 + exact legacy-hash validator` comment
with the current behavior of `check_go_schema` (compact-pair verification-report
schema + frozen historical-report bytes) — confirm phrasing against
`scripts/check_go_schema.py`'s docstring before writing.
`.github/pull_request_template.md:9`: replace
`` `.venv/bin/python -m pytest tests/unit/ -q` clean (current governance baseline: **234 passed / 0 failed**) ``
with
`` `.venv/bin/python -m pytest tests/unit/ -q` clean — paste the literal summary line under Verification output ``
(actual count today is 556 collected; a frozen number in a template will always
re-stale).

- [ ] **Step 4: Verify gates and suite**

Run: `env -u GIT_INDEX_FILE .venv/bin/python scripts/check_no_ceremony.py`
Expected: all remaining rules PASS; no R4 row.
Run: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
Expected: `OK`.
Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q`
Expected: `555 passed, 1 xfailed`.

- [ ] **Step 5: Commit**

```bash
env -u GIT_INDEX_FILE git add .github/workflows/ci.yml scripts/check_no_ceremony.py .github/pull_request_template.md
env -u GIT_INDEX_FILE git commit -m "fix(ci): drop backwards suite-wide --runxfail step and its R4 enforcement"
```

---

### Task 3: Retire the descriptor from the assembly map; close the two agents-side residues

**Files:**
- Modify: `docs/protocol/protocol-assembly-map.md` (mermaid `Scope` node +
  its 2 edges, the `Lane-V scope authority` table row at ~:46, the Placement
  Rule line at ~:69)
- Modify: `docs/templates/agents/implementer.md:21`

**Interfaces:** none (doc-only).

Why: the compact pair loop (`c44eb1e`, 2026-07-17) declares "There is no
descriptor"; the map (last touched 2026-07-14) still routes Lane-V scope
authority to `coordination/verification/scopes/`. The agents implementer
template carries the same retired trailer instruction the Claude templates shed
in Task 0.

- [ ] **Step 1: Rewrite the three map sites**

Table row (~:46) becomes:

```markdown
| Lane-V trigger authority | `coordination/mailbox/sent/` (verify-request) | `*-director-to-operator-verify-request.md` | The committed compact-pair verify-request is the sole trigger authority (Canonical Compact Pair Invariant, `scripts/codex_protocol_model.py`). There is no descriptor; `coordination/verification/scopes/` holds frozen historical artifacts only. |
```

Placement Rule line (~:69) becomes:
`Lane-V trigger authority?    -> coordination/mailbox/sent/ (compact-pair verify-request)`

Mermaid: delete the `Scope[...]` node and its `Skills --> Scope` /
`Scope --> Evidence` edges (mailbox already appears in the flow).

- [ ] **Step 2: Rewrite the agents implementer bullet**

`docs/templates/agents/implementer.md:21` — replace the `Lane-V-Scope` trailer
bullet with the same wording Task 0 put in the Claude twin: trigger authority is
the committed compact-pair verify-request; no trailer; never invent trigger
authority.

- [ ] **Step 3: Verify and commit**

Run: `grep -rn 'Lane-V-Scope\|verification/scopes' docs/ .agents/ .claude/ --include='*.md' | grep -v archive | grep -v superpowers`
Expected: no live-authority hits (historical/plan mentions allowed).
Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py -q`
Expected: pass.

```bash
env -u GIT_INDEX_FILE git add docs/protocol/protocol-assembly-map.md docs/templates/agents/implementer.md
env -u GIT_INDEX_FILE git commit -m "docs(protocol): retire descriptor authority from assembly map and agents template"
```

---

### Task 4: Condition the ref-bus wording on liveness

**Files:**
- Modify: `scripts/codex_protocol_model.py:33` (ACTIVE_KERNEL_INVARIANTS body),
  `:354` (START_SESSION_STEPS entry)
- Modify: `docs/protocol/codex/continuation.md:6`,
  `docs/protocol/threeway/CODEX-ADOPTION.md:111` (`is now` → `once live`)

**Interfaces:** none new; `git for-each-ref refs/threeway/` is the existing
liveness oracle (already used by the Claude-side surfaces).

Why: `refs/threeway/*` is empty both locally and on origin (verified live), yet
the executable model states the bus "is the load-bearing state source"
unconditionally. CLAUDE.md:242-243 and the Claude skills already condition on
liveness — this converges the Codex surfaces on the same conditional. No test
pins the unconditional wording (verified); the bus code itself stays.

- [ ] **Step 1: Append the liveness condition to both model strings**

Both strings gain the same clause; e.g. line 33's body becomes:

```python
        "the signed three-way ref-bus is the load-bearing state source for "
        "three-way facts once refs/threeway/* is live (git for-each-ref "
        "refs/threeway/ is the oracle; until then the mailbox remains "
        "authoritative); free-form mailbox remains the human coordination channel",
```

Mirror the same clause into the `:354` START_SESSION_STEPS sentence and the two
codex-side docs.

- [ ] **Step 2: Verify and commit**

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q`
Expected: pass — if a sync fragment pins the OLD sentence, update that fragment
in the same commit (sync tests move with the model).
Run: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` → `OK`.

```bash
env -u GIT_INDEX_FILE git add scripts/codex_protocol_model.py docs/protocol/codex/continuation.md docs/protocol/threeway/CODEX-ADOPTION.md
env -u GIT_INDEX_FILE git commit -m "fix(protocol): condition ref-bus authority wording on refs/threeway liveness"
```

---

### Task 5: Push and confirm remote CI green (USER-GATED)

Preconditions: Tasks 1–4 committed, operator verification-report GO in the
mailbox for the range, explicit user push authorization ("fix X" ≠ push-auth).

- [ ] **Step 1:** `env -u GIT_INDEX_FILE git log --oneline origin/main..main` —
  present the range to the user and request push authorization.
- [ ] **Step 2 (after auth):** `env -u GIT_INDEX_FILE git push origin main`
- [ ] **Step 3:** `gh run watch` (or `gh run list --limit 1`) — Expected: the
  first green main run since 2026-07-12. If red, read `--log-failed` before any
  further change (R-EVIDENCE).

---

### Task 6: DONE — deleted the dormant route/v1 typed machinery (`06e796c`)

**User-approved and executed** (both verifiers clean). Original recommendation retained below.

**Recommendation: delete.** Zero `.route.json` sidecars exist, `route_manifest`
has zero production callers (only the ADR-014 comparator, itself run only by its
own test), markdown prose is the live authority (`protocol_capacity.validate_route`
+ `route_lineage`'s regex parser), and the "wire typed enforcement instead"
option lost its foundation when 411c2af deleted capability/v1. This mirrors the
terminal-cleanup precedent: dormant machinery beside a live path is drift
surface, not capability.

If approved, one deletion commit:
- Delete: `scripts/route_manifest.py` (426 LOC), `scripts/route_compat.py`
  (162), `schemas/route-v1.schema.json`, `docs/protocol/route-v1.md`,
  `tests/unit/{test_route_manifest,test_route_render,test_route_render_invariance,test_route_compat,test_route_schema_sync}.py`,
  `tests/fixtures/route_compat/` (20 files), `logs/route-compat-report.json`
- Modify: `tests/unit/test_kernel_properties.py` (~:38-137 route_manifest
  sections only — KEEP route_lineage + packet_state sections),
  `docs/protocol/claude/continuation.md:408` (drop the route-v1 pointer),
  `scripts/route_lineage.py:162` (stale `capability_is_current` comment),
  `DECISIONS.md` (append superseding entry; never edit ADR-014/015)
- Note: deleting `test_route_render_invariance.py` removes the suite's only
  strict-xfail pin — Task 2 must NOT be re-ordered after this on the assumption
  the pin still exists; expected count becomes `~532 passed, 0 xfailed`
  (executor pastes the literal line).
- After deletion, `rfc8785` becomes bus-only — do NOT also remove the dependency
  (the bus stays; see Task 4).
- Verify: smoke `OK`; full suite green; operator GO; then user-gated push.

If declined: no half-measure — leave the island intact and record the keep
decision in DECISIONS.md instead.

---

## Self-review (writing-plans checklist)

- Spec coverage: analyst items 1→Tasks 1+2+5, 2→Tasks 0+2+3, 3→Task 4,
  4→Task 6, 5→Task 0. Rejected/deferred items enumerated with evidence. ✓
- No placeholders: every step has exact text/code or an exact verification
  command with expected output. ✓
- Type consistency: only `forbidden_roots() -> list[Path]` and the
  `GOVERNANCE_TARGET_PATH` env seam cross task boundaries; both cited from
  source. ✓
