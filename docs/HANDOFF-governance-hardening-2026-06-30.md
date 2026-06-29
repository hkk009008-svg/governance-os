# HANDOFF — governance-hardening (turn doctrine into fail-closed gates)

*From:* a three-audit strategy/review pass (director-voice).
*To:* a Claude Code implementer session operating under `CLAUDE.md`.
*Date:* 2026-06-30
*Prereq:* run R-START before any task (smoke green, `git log --oneline -20`, skim `ARCHITECTURE.md` §2). Expected baseline: `.venv/bin/python scripts/ci_smoke.py` → `OK`, exit 0.

---

## §0 How to use this handoff

This is a **roadmap handoff** (operator manual: why + how + acceptance), the
`docs/HANDOFF-roadmap-*.md` shape. It is ≥5 independent sub-tasks, so **R-ORCH
fires**: do NOT implement in main context. Main holds the plan + task state +
a short summary per task; a fresh implementer subagent does each task; a spec
reviewer and a code-quality reviewer review the actual diff per task. One commit
per task, clean `BASE..HEAD` range. Every subagent prefixes git with
`env -u GIT_INDEX_FILE`.

Read the intent in §1 before building — the project warns that agents may comply
mechanically without understanding intent. Each task card is self-contained; pull
the named source files when its trigger fires (load policy), don't pre-read everything.

---

## §1 Why (intent — read this)

Three independent audits converged on one finding: **the system's reliability
rests on ~4 hard Python gates (`ci_smoke`, doc-anchor drift, anti-ceremony R1–R6,
reviewer-schema), while dozens of markdown rules are soft-enforced — by the same
class of unreliable agent they exist to govern.** Two consequences follow, and
this session addresses exactly those, nothing more:

1. **The enforcer is the enforced.** An agent can emit the *form* of compliance
   (`verified via $cmd → result`) without the *substance* of running it. The fix
   is to push the highest-value soft rules into fail-closed scripts that an agent
   cannot satisfy by assertion. (Tasks A2, A3, A6, A7.)
2. **The bundle reads green while inert.** `ci_smoke` passes, but `_project_smoke()`
   is a stub and the truth/ops docs are `<fill-in>` skeletons — green currently
   proves only that the *governance shell* is internally coherent. The fix is to
   make inertness *loud* (a placeholder gate) so a half-bound repo cannot pass CI.
   (Task A1.) Actually *binding* a project is **out of scope** — see §5.

Two things this session must **not** do, with reasons:
- **Do not fabricate project facts.** ARCHITECTURE topology, smoke invariants, and
  OPERATIONS commands cannot be written truthfully against the genericized bundle
  (there is no domain code). Inventing them is the gravest R-EVIDENCE violation
  available. Track B is fenced off (§5).
- **Do not touch the signed bus (`threeway/`).** Ed25519 authenticates *origin*,
  not *correctness*; in a single-operator / single-machine deployment the "rogue
  session" holds a legitimately issued key and signs bad reports perfectly. The bus
  buys nothing until a second principal or second machine exists (§5, Out-of-scope).

---

## §2 Scope split

| Track | Status | What |
|---|---|---|
| **A — bundle-intrinsic** | **BUILD THIS SESSION** | Gates + docs that operate on bundle structure (git/mailbox/doc/CI). No target code needed. |
| **B — adoption-bound** | **BLOCKED — do not attempt** | Filling ARCHITECTURE/README/OPERATIONS, real `_project_smoke()`, measurement. Needs a concrete target repo. |
| **Out-of-scope** | **Do not touch** | `threeway/` signed bus. Revisit only when a 2nd principal or 2nd host exists. |

---

## §3 Orchestration plan (task graph)

A1–A3 and A5–A6 each produce **standalone artifacts** (a `scripts/check_*.py` +
`tests/test_check_*.py`, or a doc/ADR) that share **no files** — implementers may
run sequentially; parallel is permitted only because they touch disjoint paths,
but sequential is recommended for review simplicity.

**A-WIRE is the single shared-file task** (`scripts/ci_smoke.py` + `.github/workflows/ci.yml`)
and MUST run **last, alone** — never concurrently with anything that edits those
files (R-ORCH: no two implementers in parallel on shared files; R-WIP-POLLUTION).

```
A1 placeholder-gate ─┐
A2 GO-evidence ──────┤
A3 arch-freshness ───┼──> A-WIRE (wire all checks into ci_smoke + ci.yml) ──> §7 global acceptance
A5 py-3.13 decision ─┤
A6 HARD/SOFT tagging ┘
A7 push-gate ──> SURFACE the commit↔GO convention decision FIRST (do not implement blind)
```

Per-task review (R-ORCH two-stage): spec reviewer confirms the diff matches this
card; code-quality reviewer reviews the actual diff. Both run **after** the
implementer, on the real diff, not the plan.

---

## §4 Task cards

### A1 — `scripts/check_placeholders.py` (fail-closed adoption gate)

**Goal:** fail CI when an adoption placeholder survives **outside an explicit
allowlist**. The bundle's skeletons are *supposed* to contain placeholders, so a
naive grep would brick the bundle's own green smoke — the allowlist is load-bearing,
not a detail.

**Sources to read first:** the placeholder convention table in `TRANSFER-MANIFEST.md`
(canonical token list) and the acceptance grep in `TRANSFER-SETUP.md` §Acceptance
(the manual behavior you are automating).

**Tokens to scan:** `<PROJECT>`, `<PROJECT_NAME>`, `<entrypoint>`, `<domain-skill>`,
`<domain-lane-A>`, `<domain-lane-B>`, `<fill-in>`, `TODO(<PROJECT>)`, `<ref>`.

**Design constraints:**
- Allowlist file `scripts/placeholder_allowlist.txt` lists paths permitted to
  retain placeholders. Check fails (nonzero exit) on any token in any non-allowlisted,
  non-`.git` file.
- **Produce the initial allowlist empirically, not by guessing** (R-EVIDENCE): run
  the scan, and the set of files that currently contain a token *is* the committed
  baseline allowlist. The script + the allowlist file + the transfer/protocol docs
  that legitimately quote the tokens will appear in this set — that is correct.
- Adoption note (put in the file header and in `TRANSFER-SETUP.md` §Acceptance):
  filling a skeleton means **removing its path from the allowlist**; when the
  allowlist is empty and the scan is clean, the repo is fully bound.

**Test (`tests/test_check_placeholders.py`):** temp tree with (a) an allowlisted
file containing `<fill-in>` → passes; (b) a non-allowlisted file containing
`<PROJECT>` → fails, nonzero exit.

**Acceptance:**
```
.venv/bin/python scripts/check_placeholders.py            # exit 0 on the bundle (all tokens allowlisted)
.venv/bin/pytest tests/test_check_placeholders.py -q      # pass
```
Paste both commands + output in the commit body (cite or don't claim).

**ADR:** append **ADR-002 — Gate adoption placeholders in CI.** Context: placeholder
leakage (agents read skeleton prose as doctrine). Decision: allowlist-based,
fail-closed scan, wired to smoke in A-WIRE. Consequence: skeletons must be
de-allowlisted as filled; the gate is the definition of "fully bound."

---

### A2 — `scripts/check_go_schema.py` (GO-report evidence validator)

**Goal:** a `verification-report` mailbox event carrying a **GO** verdict must
contain command + its output + a commit SHA (or `logs/` artifact ref) + an explicit
verdict token. A **GO whose only evidence is a `wave_gate_check` invocation fails**
(R-GATE-EVIDENCE: the gate reads an inventory string, it does not execute tests).

**Sources to read first (R-BRIEF — do not invent the schema):**
`coordination/mailbox/kinds.txt` (mailbox-kind schema), `scripts/protocol_mailbox.py`
(SEATS/RECEIVING_SEATS + event format), and one real event under
`coordination/mailbox/sent/` if present. Build the validator against the *actual*
field shape, not an assumed one. If the schema is ambiguous, surface the divergence
before implementing.

**Design constraints:**
- Parse `verification-report` events in `coordination/mailbox/sent/`. For each GO:
  require (command, output, SHA-or-artifact, verdict). Missing any → fail with the
  offending file + missing field named.
- Sub-rule: if a GO's evidence section references `wave_gate_check` and contains no
  pytest/regression-pin output, fail with the R-GATE-EVIDENCE reason.

**Test (`tests/test_check_go_schema.py`):** fixtures for (a) well-formed GO → pass;
(b) GO missing output → fail; (c) GO citing only `wave_gate_check` → fail.

**Acceptance:**
```
.venv/bin/python scripts/check_go_schema.py <fixture-dir>   # nonzero on bad fixtures, 0 on good
.venv/bin/pytest tests/test_check_go_schema.py -q
```

**ADR:** fold into **ADR-003** (below) — one ADR for the machine-checkable-doctrine
move, to avoid ADR sprawl.

---

### A3 — `scripts/check_arch_freshness.py` (ARCHITECTURE Last-verified gate)

**Goal:** block a commit that modifies `ARCHITECTURE.md` without bumping its
`*Last verified: <date> @ <sha>*` footer.

**Design constraints:**
- In CI, diff `ARCHITECTURE.md` against the merge-base; if the file changed but the
  Last-verified line did not, fail. Fires **only** when ARCHITECTURE.md is in the
  changeset (so the skeleton's literal `<date> @ <sha>` placeholder is inert until
  someone edits the file — no spurious failure on the unbound bundle).

**Test (`tests/test_check_arch_freshness.py`):** simulated diff touching the body
without footer change → fail; footer bumped → pass.

**Acceptance:**
```
.venv/bin/pytest tests/test_check_arch_freshness.py -q
```

**ADR:** fold into **ADR-003**.

---

### A4 — `RUNBOOK-DAILY.md` (the minimal live loop, one page)

**Goal:** a one-page daily runbook so the common path is small and the seat/wave/bus
superstructure stops being the first thing a contributor meets (onboarding-cliff fix).

**Content:** the single visible loop only — **director brief → operator verify →
GO / NITS / FAIL → push**. State: baton passes are mailbox artifacts not chat; first
commit to land wins after git+mailbox refresh; no push pre-GO (R-VERIFY-THEN-PUSH);
docs/status/handoff-only commits skip Lane V. Everything rarer is a one-line
trigger→reference pointer into `docs/protocol/claude/` — do not restate rule bodies.
Source the loop from the Pair Operating Contract already in `AGENTS.md`; don't invent
new doctrine.

**Acceptance:** file exists, fits one screen, contains no rule bodies (only
trigger→reference pointers for anything beyond the core loop). Add it to the repo doc
map tables in `CLAUDE.md` and `AGENTS.md` in the **same commit** (staleness discipline).

---

### A5 — Resolve the Python `>=3.13` floor

**Goal:** all three audits flagged 3.13 as a steep adoption bar for stdlib-plus-two-deps
governance code.

**Action:** determine whether any governance code (`scripts/*.py`, `threeway/*.py`)
uses a 3.13-only feature. `tomllib` is stdlib since 3.11, so the obvious candidate is
already covered.
- If **nothing** needs 3.13 → lower `requires-python` in `pyproject.toml` to `>=3.11`
  (or `>=3.12`), and note the relaxation.
- If 3.13 **is** required → keep it and append an ADR documenting the specific feature
  and why.
Either branch records the decision (cite the grep that backs "no 3.13-only feature"
per R-EVIDENCE).

**ADR:** **ADR-004 — Python runtime floor** (records the decision + evidence either way).

---

### A6 — Tag every rule HARD or SOFT in `docs/PROTOCOL-RULES-LOG.md`

**Goal:** produce the map that tells future sessions which rules are real gates vs.
honor-system — the prerequisite to all later promotion decisions and the answer to
"the enforcer is the enforced."

**Action:** read the existing entry structure first, then add an **enforcement-class**
field to each rule: `HARD` (a committed script currently enforces it — name the
script) or `SOFT` (prose-only, enforced by agent discipline). Classify by what a
script *actually* checks today, not by intent. After A1–A3 land, the newly promoted
rules flip to HARD with their new script named.

**Acceptance:** every rule entry carries an enforcement-class + (for HARD) the
enforcing script path. No new rule bodies added — this is a metadata pass.

---

### A7 — push-without-GO gate (SURFACE the convention first; do not implement blind)

**Goal:** block a push of production-code commits lacking a matching operator GO
event (R-VERIFY-THEN-PUSH).

**Why this is a decision, not a build:** a static push-gate needs a **commit↔GO
linking convention** (e.g., the GO event references the SHA it verifies). The bundle
may not define one. Per "surface rather than silently decide," do **not** invent a
linking scheme inside an implementer.

**Action:**
1. Check whether a commit↔GO convention exists (read `coordination/mailbox/kinds.txt`
   + a real `verification-report`). 
2. If it does → implement `scripts/check_verify_then_push.py` as a pre-push hook:
   given the commits to be pushed, if any touch production paths and no
   matching-SHA GO event exists, block. Ship a test.
3. If it does **not** → stop. Append **ADR-005 — commit↔GO linking convention**
   proposing the scheme, and leave the hook as the next session's task. Use
   `AskUserQuestion` if the convention is policy-setting / hard to reverse.

**Acceptance:** either a tested hook (path + test + run output cited) **or** ADR-005
+ a one-line `test-infeasible`-style note in this handoff's wrap explaining the block.

---

## §5 Track B — deferred (DO NOT ATTEMPT THIS SESSION)

| Item | Why blocked |
|---|---|
| Fill `ARCHITECTURE.md` (topology, module map, smoke invariants, Last-verified) | No domain code to describe truthfully. |
| Fill `README.md` / `OPERATIONS.md` (copy-pasteable commands) | Commands would be fiction against the unbound bundle. |
| Implement real `_project_smoke()` (import/config/entrypoint/symbol/layout/dry-run) | Asserts facts about code that does not exist here. |
| Measurement instrumentation (gate-catches / defect-escapes / rework / co-sign latency) | Needs real sessions to measure. |

**Unblock trigger:** the bundle is `cp -R`'d into a concrete target repo with real
domain code (TRANSFER-SETUP §1–§5 done).

**HARD NO-GO:** if asked to do any Track B item without a bound target repo, **refuse
and surface** — do not fabricate ARCHITECTURE facts or smoke invariants. When the
target repo exists, the §N-smoke ↔ `_project_smoke()` co-evolution contract applies:
add each invariant to ARCHITECTURE.md **and** its assertion in `_project_smoke()` in
the same commit.

**Out-of-scope (do not touch):** `threeway/` signed bus. Revisit only when a second
principal (another human) or second machine actually exists; until then signatures
add deferred weight, not security.

---

## §6 Measurement (turn on when bound, not now)

The framework is built on R-MEASURE yet never measures its own ROI — the
seat/pair/wave overhead is justified by anecdote. This is **not** Track A work, but
the moment a real project is bound, start counting: gate-catches vs. defect-escapes,
rework commits, co-sign latency. Hardening a machine whose central premise is
unmeasured is the one claim in the bundle that escapes its own evidence discipline;
close it as soon as there is something real to measure.

---

## §7 Global acceptance (run after A-WIRE)

The whole bundle must still boot green with the new gates live (placeholders
allowlisted), mirroring `TRANSFER-SETUP.md` §Acceptance plus the additions:

```
.venv/bin/python scripts/ci_smoke.py              # OK, exit 0  (now invokes check_placeholders + new lints)
.venv/bin/python scripts/check_coordination.py    # no FATALs
.venv/bin/python scripts/check_placeholders.py    # exit 0 (allowlist baseline)
.venv/bin/pytest -q                               # all new tests green; no xfail-strict surprise passes
```

If `ci_smoke.py` goes red after A-WIRE, a gate is mis-wired or the allowlist baseline
is wrong — fix before declaring done. Capture this block's output in the A-WIRE
commit body.

---

## §8 Commit & evidence discipline (every task)

- **One commit per task**, clean `BASE..HEAD`; `git show --stat` to confirm scope
  matches intent before landing.
- **`env -u GIT_INDEX_FILE`** on all git in subagents (seat-index corruption vector);
  scoped/temp index only if the shared index is dirty.
- **Cite or don't claim** (R-EVIDENCE): paste the acceptance command + its output in
  the commit body. No factual/inventory claim without the producing command.
- **DECISIONS.md is append-only.** Add ADR-002…ADR-005; if any supersedes a prior
  entry, reference it by number — never edit a prior ADR.
- **Staleness in the same commit:** if a task exposes a stale claim in `ARCHITECTURE.md`
  / `CLAUDE.md` / `AGENTS.md`, fix it in that commit (or a `docs:` prep commit right
  before).
- **Tier the co-sign** if you pull in a second seat: would their verification change
  which files you touch? Yes → Tier A (mailbox `verification-report` before dispatch);
  no → Tier B awareness heads-up.

---

## §9 ADRs to append this session

| ADR | Title | From task |
|---|---|---|
| ADR-002 | Gate adoption placeholders in CI (fail-closed allowlist) | A1 |
| ADR-003 | Make verify-then-push / GO-evidence / arch-freshness machine-checkable | A2, A3 |
| ADR-004 | Python runtime floor (3.13 kept-with-reason or relaxed-with-evidence) | A5 |
| ADR-005 | commit↔GO linking convention (only if A7 step 3 fires) | A7 |

**Wrap deliverable:** a short report — per-task commit SHAs (clean ranges), the §7
global-acceptance output, the new HARD/SOFT map summary (how many rules flipped to
HARD), and any `test-infeasible`/surfaced-decision notes (A7). End with the exact next
trigger (most likely: "bind to target repo → unblock Track B").
