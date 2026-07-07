# Close the User-Principal Items — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every open item from the 2026-07-07 "needed from the user-principal" audit, per the user's five recorded decisions: bind target = evidence-ledger (already partially executed there), MIT license for this repo, push gate stays deferred, threeway/Antigravity stay deferred with documented triggers, 4-seat env activates **in Pipeline**.

**Architecture:** Two repos. Pipeline (`/Users/hyungkoookkim/Pipeline`, public `hkk009008-svg/governance-os`) stays the generic transfer bundle — it gets a license, ADRs recording the decisions, a staleness fix to the handoff, the Rules #17–20 advisory intake, and local 4-seat env wiring. Evidence-ledger (`/Users/hyungkoookkim/evidence-ledger`, private) already carries an "Option B partial bind" (its ADR-001, 2026-07-03, on `origin/phase1-foundation`, merged to `origin/main` @ `a5fb526`); the local checkout is 21 commits behind — it gets a reconcile plus closure of its remaining 4-entry placeholder debt.

**Tech Stack:** Markdown docs, JSON config, bash, the repos' own committed Python gate scripts (`ci_smoke.py`, `check_placeholders.py`, `check_coordination.py`, pytest).

## Global Constraints

- One commit per task; clean scope confirmed via `git show --stat` before finishing a task (CLAUDE.md impact-analysis section).
- All git mutators and pytest in subagent dispatches carry the `env -u GIT_INDEX_FILE` prefix (CLAUDE.md Git-tooling sharp edges).
- `DECISIONS.md` is append-only in both repos — new entries go below the marker comment `<!-- Append new ADR entries below this line. Do not edit entries above. -->`; never edit prior entries.
- R-EVIDENCE: every factual claim written into a doc cites its producing command + output (`verified via $ <cmd> → <result>`).
- Pipeline's next free ADR number is **ADR-007** (current highest: ADR-006 at DECISIONS.md:188; ADR-006 reserves origin numbers ≥027).
- **No `git push` in any task.** Pushes are user-authorized per instance (standing consent gate). The plan ends with push checkpoints for the user.
- Work inside `/Users/hyungkoookkim/evidence-ledger` follows THAT repo's doctrine (its CLAUDE.md, `env -u GIT_INDEX_FILE` discipline, RUNBOOK-DAILY controller→verify→GO loop). Its user-facing Korean docs use plain-text markers, never emoji.
- Pipeline placeholder gate invariant: after every Pipeline commit, `.venv/bin/python scripts/ci_smoke.py` exits 0. Editing an allowlisted file (README.md, DECISIONS.md, the handoff) does NOT require allowlist changes — `check_placeholders.py` exempts whole files (scripts/check_placeholders.py:115-117).

---

### Task 1: MIT license for the public bundle repo (Pipeline)

**Files:**
- Create: `/Users/hyungkoookkim/Pipeline/LICENSE`
- Modify: `/Users/hyungkoookkim/Pipeline/README.md:71-73` (License section)
- Modify: `/Users/hyungkoookkim/Pipeline/DECISIONS.md` (append ADR-007)

**Interfaces:**
- Consumes: nothing.
- Produces: `LICENSE` file at repo root; ADR-007 (referenced by Task 2's ADR-008 as a sibling decision).

- [ ] **Step 1: Confirm current state (evidence for the ADR)**

Run: `ls /Users/hyungkoookkim/Pipeline/LICENSE* 2>/dev/null; gh repo view hkk009008-svg/governance-os --json visibility -q .visibility`
Expected: no LICENSE match; `PUBLIC`.

- [ ] **Step 2: Write `LICENSE`** (standard MIT text, verbatim):

```
MIT License

Copyright (c) 2026 Hyungkook Kim (hkk009008-svg)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Fill the README License section.** Replace README.md lines 71-73:

Old:
```
## License

<fill-in: license name and link>
```
New:
```
## License

MIT — see [LICENSE](LICENSE).
```

- [ ] **Step 4: Append ADR-007 to DECISIONS.md** (below the append marker):

```markdown
## ADR-007: License the public transfer bundle under MIT

**Status:** Accepted

**Context:**
The repo is PUBLIC on GitHub (`hkk009008-svg/governance-os`; verified via
`$ gh repo view --json visibility → PUBLIC`) but carried no LICENSE file —
legally "all rights reserved", contradicting its stated purpose as a transfer
bundle adopters copy into their own repos (TRANSFER-SETUP.md §1).

**Decision:**
License the repository under the MIT License (LICENSE at repo root; README §License
filled). Decided by the user-principal on 2026-07-07.

**Consequences:**
- Adopters can lawfully copy, modify, and embed the bundle.
- No patent grant (Apache-2.0 was declined as heavier than needed).
- README.md remains on the placeholder allowlist — its other skeleton sections
  are deliberate adopter fill-ins per ADR-002.
```

- [ ] **Step 5: Verify gates stay green**

Run: `cd /Users/hyungkoookkim/Pipeline && .venv/bin/python scripts/ci_smoke.py; echo "exit=$?"`
Expected: output ends `OK`, `exit=0` (README/DECISIONS are whole-file allowlisted; LICENSE contains no tokens).

- [ ] **Step 6: Commit**

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE git add LICENSE README.md DECISIONS.md
env -u GIT_INDEX_FILE git commit -m "docs(adr): MIT license for the public bundle repo (ADR-007)"
env -u GIT_INDEX_FILE git show --stat HEAD   # confirm exactly 3 files
```

---

### Task 2: Record the binding + fix the now-stale Track-B claims (Pipeline)

**Files:**
- Modify: `/Users/hyungkoookkim/Pipeline/DECISIONS.md` (append ADR-008)
- Modify: `/Users/hyungkoookkim/Pipeline/docs/HANDOFF-governance-hardening-2026-06-30.md` (pointer line in §5 + dated addendum at end of file)

**Interfaces:**
- Consumes: ADR-007 (Task 1) for sequential numbering.
- Produces: ADR-008 — cited by Task 3's ADR-009/010 and by the handoff addendum.

- [ ] **Step 1: Re-verify the binding evidence (fresh, for citation)**

```bash
cd /Users/hyungkoookkim/evidence-ledger
git fetch origin --quiet
git log --oneline origin/phase1-foundation | grep -m1 fee5207
git log --oneline -1 origin/main
git show origin/phase1-foundation:scripts/placeholder_allowlist.txt | grep -cv '^#'
```
Expected: `fee5207 feat(governance): Option B partial bind — fail-closed gates, session hooks, CI, doctrine (ADR-001)`; `a5fb526 merge: Phase 1 + governance — phase1-foundation -> main`; `5` (allowlist entries).

- [ ] **Step 2: Append ADR-008 to Pipeline DECISIONS.md:**

```markdown
## ADR-008: Binding target designated — evidence-ledger (bind already executed there); Pipeline stays the generic bundle

**Status:** Accepted

**Context:**
The 2026-06-30 handoff blocked Track B ("fill the truth docs, real
`_project_smoke()`") behind a HARD NO-GO until a concrete target repo existed.
On 2026-07-07 the user-principal designated `hkk009008-svg/evidence-ledger`
(private) as the bound target — and inspection showed the bind was already
executed there on 2026-07-03 as that repo's ADR-001 "Option B partial bind"
(commit `fee5207` on its `phase1-foundation`, merged to its main @ `a5fb526`;
verified via `$ git log --oneline origin/phase1-foundation` in that repo).
Its ARCHITECTURE.md/OPERATIONS.md were filled 2026-07-04; its placeholder
allowlist is down to 5 entries (verified via `$ git show
origin/phase1-foundation:scripts/placeholder_allowlist.txt | grep -cv '^#'
→ 5`).

**Decision:**
(1) evidence-ledger is the bound deployment of this governance OS; Track B
lives there and is largely complete under its own ADR log. (2) Pipeline
remains the generic transfer bundle: its skeleton placeholders and
`TODO(<PROJECT>)` sites stay deliberately unfilled per ADR-002 — they are
adopter fill-ins, not debt. (3) Items resolved by evidence-ledger's ADR-001
baked defaults are closed without further action here: PROGRAM-MANUAL content
(their intent doc = the approved design spec + docs/MANUAL.md),
money-gate-reviewer (no AI-spend lane in their Phase 1; revisit at their
Phase-2 AI-spend lane), threeway/seat machinery (deliberately skipped there).
Decided by the user-principal on 2026-07-07.

**Consequences:**
- The handoff's "Track B BLOCKED / HARD NO-GO" claims are stale → fixed by the
  dated addendum in docs/HANDOFF-governance-hardening-2026-06-30.md (same
  change as this entry, per the staleness rule).
- Pipeline's `docs/PROGRAM-MANUAL.md` skeleton stays allowlisted by design; an
  adopter-facing manual for the governance OS itself remains possible future
  work if the user requests it.
- Remaining binding debt is tracked in evidence-ledger's own allowlist (4 real
  entries + 1 intentional test fixture) — closed by a follow-on task in that
  repo, under that repo's doctrine.
```

- [ ] **Step 3: Add the pointer line in the handoff.** Directly under the heading `## §5 Track B — deferred (DO NOT ATTEMPT THIS SESSION)` (docs/HANDOFF-governance-hardening-2026-06-30.md:276), insert:

```markdown
> **2026-07-07 update:** the unblock trigger has FIRED — see the dated addendum
> at the end of this file. The table and HARD NO-GO below are preserved as
> written for the historical record.
```

- [ ] **Step 4: Append the addendum at the very end of the handoff file:**

```markdown
---

## Addendum 2026-07-07 — Track B unblocked and relocated

The user-principal designated `hkk009008-svg/evidence-ledger` as the bound
target repo (Pipeline ADR-008). Inspection showed the bind was already
executed there on 2026-07-03 (that repo's ADR-001 "Option B partial bind",
commit `fee5207`, merged to its main @ `a5fb526`) with the truth docs filled
2026-07-04. Track B items therefore live in that repo and are largely
complete; Pipeline remains the generic transfer bundle per ADR-002/ADR-008.
The §5 HARD NO-GO is satisfied — a bound target exists; the co-evolution
contract (§N-smoke ↔ `_project_smoke()`) now applies in the bound repo. The
"next trigger" recorded at the wrap (bind to target repo → unblock Track B)
is consumed.
```

- [ ] **Step 5: Verify + commit**

```bash
cd /Users/hyungkoookkim/Pipeline && .venv/bin/python scripts/ci_smoke.py && \
env -u GIT_INDEX_FILE git add DECISIONS.md docs/HANDOFF-governance-hardening-2026-06-30.md && \
env -u GIT_INDEX_FILE git commit -m "docs(adr): record evidence-ledger binding + unblock Track B (ADR-008)" && \
env -u GIT_INDEX_FILE git show --stat HEAD
```
Expected: smoke `OK`; commit touches exactly 2 files.

---

### Task 3: Activate the 4-seat environment in Pipeline (env wiring + ADR-009/ADR-010)

**Files:**
- Create: `/Users/hyungkoookkim/Pipeline/.env` (gitignored — verify, do not commit)
- Modify: `/Users/hyungkoookkim/Pipeline/.claude/settings.local.json` (gitignored — register the update-state hook)
- Create: four per-seat git index files under `.git/` (untracked)
- Modify: `/Users/hyungkoookkim/Pipeline/DECISIONS.md` (append ADR-009 and ADR-010)

**Interfaces:**
- Consumes: ADR-008 numbering.
- Produces: working per-seat env; ADR-009 lane table (the PRINCIPAL-CONFIRMED lane record for this deployment); ADR-010 deferral register.

- [ ] **Step 1: Confirm `.env` and `settings.local.json` are gitignored**

Run: `cd /Users/hyungkoookkim/Pipeline && git check-ignore -v .env .claude/settings.local.json`
Expected: both paths print a matching `.gitignore` rule. If either is NOT ignored, STOP and report — do not create the file.

- [ ] **Step 2: Create `.env`** — copy of `.env.example` with two deliberate edits (seat identity stays per-terminal; consent posture pinned):

```bash
cd /Users/hyungkoookkim/Pipeline
sed -e 's/^CLAUDE_SEAT=director$/# CLAUDE_SEAT is set per-terminal at launch — see coordination\/README.md "Per-seat launch"/' \
    -e 's/^CODEX_SEAT=director$/# CODEX_SEAT is set per-terminal at launch/' \
    .env.example > .env
grep -n 'CODEX_SIDE_EFFECT_POLICY=user-consent-required' .env
```
Expected: the grep prints the line (already the example default).

- [ ] **Step 3: Register the update-state PostToolUse hook.** Overwrite `.claude/settings.local.json` with exactly (merging the existing `outputStyle` + `permissions` keys, per coordination/README.md:269-283):

```json
{
  "outputStyle": "Explanatory",
  "permissions": {
    "allow": [
      "Read(//Users/hyungkoookkim/evidence-ledger/**)",
      "Bash(supabase start *)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/hyungkoookkim/Pipeline/.claude/hooks/update-state.sh"
          }
        ]
      }
    ]
  }
}
```

First read the current file — if its `permissions.allow` has grown beyond the two entries above, preserve every existing entry. Validate: `python3 -c "import json;json.load(open('/Users/hyungkoookkim/Pipeline/.claude/settings.local.json'))" && echo VALID` → `VALID`.

- [ ] **Step 4: Seed the four per-seat git indexes** (a fresh GIT_INDEX_FILE is an empty index → 555 phantom deletions without seeding, coordination/README.md:336-340):

```bash
cd /Users/hyungkoookkim/Pipeline
GITDIR="$(git rev-parse --absolute-git-dir)"
for seat in director director2 operator operator2; do
  idx="$GITDIR/index-$seat"
  [ -f "$idx" ] || env GIT_INDEX_FILE="$idx" git read-tree HEAD
done
env GIT_INDEX_FILE="$GITDIR/index-director" git status --short | head -5
```
Expected: the final `git status` prints nothing tracked-deleted (empty output or only `??` untracked lines).

- [ ] **Step 5: Smoke-test the presence stamp**

```bash
cd /Users/hyungkoookkim/Pipeline
echo '{}' | CLAUDE_SEAT=director bash .claude/hooks/update-state.sh
cat coordination/presence/director-heartbeat.ts
```
Expected: heartbeat file contains `<ISO-UTC-timestamp> <short-head>`. (Heartbeat files are gitignored; if the hook exits non-zero, read its stderr and fix before proceeding.)

- [ ] **Step 6: Append ADR-009 to DECISIONS.md:**

```markdown
## ADR-009: Activate 4-seat concurrent operation in Pipeline; lane definitions

**Status:** Accepted

**Context:**
The 4-seat machinery (mailbox, seat skills, per-seat index guard, presence
hooks) ships live in this repo but the per-clone env was never wired (.env
absent, update-state hook unregistered — verified 2026-07-07). The
user-principal chose to activate it HERE; the bound product repo
(evidence-ledger) deliberately runs a 2-seat model per its own ADR-001, which
stands.

**Decision:**
4-seat concurrent operation is active for governance-OS work in this repo.
Lanes (PRINCIPAL-CONFIRMED 2026-07-07 via plan approval):

| Pair | Director | Operator | Lane |
|---|---|---|---|
| A | `director` | `operator` | **Coordination layer** — coordination/ (mailbox, presence, locks, workflows), scripts/protocol_mailbox.py, scripts/check_coordination.py, the update-state hooks (.claude/.codex twins). Integrity concerns: cursor/event schema, presence freshness, lock discipline. |
| B | `director2` | `operator2` | **Verification & signing layer** — threeway/, .github/workflows/ci.yml, the gate scripts (ci_smoke, check_placeholders, check_go_schema, check_arch_freshness, wave_gate_check, check_no_ceremony, check_doc_claims), seat skills + dispatch templates. Main orchestrator path: scripts/ci_smoke.py. |

Shared seam (.claude/settings.json, guard-git-index.sh) is Rule #23 co-sign
territory. The generic lane placeholders in
docs/protocol/claude/four-seat-extension.md:28-29 stay untouched — they are
adopter fill-ins (ADR-002); THIS table is the operative lane record for the
Pipeline deployment.

**Consequences:**
- Launch procedure: coordination/README.md "Per-seat launch" (per-terminal
  CLAUDE_SEAT + GIT_INDEX_FILE exports; indexes pre-seeded 2026-07-07).
- STATE.md auto-maintenance is now active via the registered PostToolUse hook.
- Physically opening the four terminals remains a user action; nothing in the
  repo can spawn peer seats.
```

- [ ] **Step 7: Append ADR-010 to DECISIONS.md:**

```markdown
## ADR-010: Deferral register — push gate, threeway bus, Antigravity regime

**Status:** Accepted

**Context:**
Three subsystems sit deferred with their triggers scattered across the
handoff, ADR-005, and protocol docs. The user-principal reviewed all three on
2026-07-07.

**Decision:**
(1) **Pre-push gate** (ADR-005) stays deferred — re-affirmed by the
user-principal on 2026-07-07 despite 4-seat activation (ADR-009). Revisit
trigger: the first push contention incident between concurrent seats, or any
push that lands without a matching operator GO. (2) **Threeway signed bus**
stays dormant. Trigger: a second human principal or second machine exists
(user-declared). Activation then needs: keys bootstrap + committed .pub files,
GitHub repo variable THREEWAY_BUS_LIVE=true and Actions secret
THREEWAY_CI_KEY (.github/workflows/ci.yml:146,168-171 — owner-only), and the
user-confirmed authority-flip cutover. (3) **Antigravity regime** undecided by
design. Trigger: first intended Antigravity use on this repo; the seat-vs-
seatless choice and cross-provider verification routing are reserved to the
user (docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md:92-147).

**Consequences:**
- Every deferral now has one authoritative home with an owner (user-principal)
  and a concrete trigger; agents cite this entry instead of re-deriving.
- No keys, secrets, or GitHub settings change until a trigger fires.
```

- [ ] **Step 8: Verify + commit** (only DECISIONS.md is tracked):

```bash
cd /Users/hyungkoookkim/Pipeline && .venv/bin/python scripts/ci_smoke.py && \
env -u GIT_INDEX_FILE git status --short   # expect ONLY M DECISIONS.md
env -u GIT_INDEX_FILE git add DECISIONS.md && \
env -u GIT_INDEX_FILE git commit -m "docs(adr): 4-seat activation + lanes, deferral register (ADR-009, ADR-010)"
```

---

### Task 4: Advisory-review intake — Rules #17–#20 (Pipeline)

**Files:**
- Modify: `/Users/hyungkoookkim/Pipeline/docs/protocol/advisory-candidates.md` (append dated review-outcome section)
- Modify: `/Users/hyungkoookkim/Pipeline/docs/PROTOCOL-RULES-LOG.md` (append a dated review note to each of the four rule entries)
- Modify: `/Users/hyungkoookkim/Pipeline/DECISIONS.md` (append ADR-011)
- Possibly Modify: `/Users/hyungkoookkim/Pipeline/docs/protocol/claude/director-operator.md` + `/Users/hyungkoookkim/Pipeline/docs/protocol/agents/director-operator.md` (status tags — ONLY for rules the user moves to advisory)

**Interfaces:**
- Consumes: ADR-010 numbering; docs/protocol/advisory-candidates.md:26-31 (the candidate table with stated revisit triggers).
- Produces: ADR-011; per-rule status record consumed by future sessions.

- [ ] **Step 1: Gather trigger evidence per rule** (the four stated triggers, advisory-candidates.md:28-31):

```bash
cd /Users/hyungkoookkim/Pipeline
# Rule 17 (trigger: first real workflow run) — look for recorded wf_ run ids:
grep -rn 'wf_[a-z0-9]' docs/ scripts/ coordination/ --include='*.md' --include='*.py' | head -10
# Rule 18 (trigger: first doc-maintenance dispatch):
grep -rn 'doc-maintenance' docs/PROTOCOL-RULES-LOG.md docs/protocol/ | head -5
# Rules 19/20 (trigger: recurrence beyond the single N=1 incident):
grep -n 'Rule #19\|Rule #20' docs/PROTOCOL-RULES-LOG.md | head -10
```

For each rule, read its PROTOCOL-RULES-LOG.md entry and record: trigger fired? (yes/no + evidence line). Known already: scripts/check_coordination.py:219 area cites capacity-audit run `wf_6be2ee18-f4b` — real workflow runs HAVE happened, so Rule #17's trigger has plausibly fired; confirm and note where.

- [ ] **Step 2: Ask the user for verdicts** — one AskUserQuestion call, four questions (one per rule), each with options: **Keep fully active** / **Move to advisory** / **Revise (user supplies direction via Other)**. Present the gathered evidence in each question (trigger fired or not, N-count today). Do not recommend moving a rule whose trigger has not fired — recommend "Keep fully active" for those.

- [ ] **Step 3: Record the outcomes.** Append to `docs/protocol/advisory-candidates.md`:

```markdown
## Advisory review 2026-07-07 (user-principal verdicts)

| Rule | Trigger evidence at review | Verdict |
|---|---|---|
| Rule #17 | <evidence + citation from Step 1> | <verdict> |
| Rule #18 | <evidence + citation from Step 1> | <verdict> |
| Rule #19 | <evidence + citation from Step 1> | <verdict> |
| Rule #20 | <evidence + citation from Step 1> | <verdict> |

Rules kept active remain candidates; their next revisit trigger is unchanged.
Rules moved to advisory carry the status change in their rule body + a dated
note in docs/PROTOCOL-RULES-LOG.md (this review = the authorizing event).
```

Fill `<evidence>`/`<verdict>` cells from Steps 1–2 — the committed table must contain the actual findings and the user's actual answers, never the angle-bracket placeholders (which would also trip `check_placeholders` on the `<ref>`-style token scan if left literal).

- [ ] **Step 4: Apply status changes (only if any rule moved).** For each moved rule: edit its body's status/enforcement tag in `docs/protocol/claude/director-operator.md` AND the `docs/protocol/agents/` twin to `ADVISORY (principal review 2026-07-07)`, and append a dated note to its PROTOCOL-RULES-LOG.md entry. If ALL rules stay active, skip this step and say so in the commit body.

- [ ] **Step 5: Append ADR-011** recording the batch (use the ADR template; Context = the advisory-review phase reserved to the user by advisory-candidates.md:3-7; Decision = the four verdicts verbatim; Consequences = which docs changed).

- [ ] **Step 6: Verify + commit**

```bash
cd /Users/hyungkoookkim/Pipeline && .venv/bin/python scripts/ci_smoke.py && \
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q && \
env -u GIT_INDEX_FILE git add docs/protocol/advisory-candidates.md docs/PROTOCOL-RULES-LOG.md DECISIONS.md && \
# add the two director-operator.md twins ONLY if Step 4 changed them:
env -u GIT_INDEX_FILE git commit -m "docs: advisory-review verdicts for Rules #17-#20 (ADR-011)"
```
Expected: smoke `OK`; unit tests pass (the ceremony/placeholder gates cover these docs).

---

### Task 5: Reconcile the evidence-ledger local checkout (no commit)

**Files:**
- Modify (working tree only): `/Users/hyungkoookkim/evidence-ledger` — fast-forward pull; no new commits.

**Interfaces:**
- Consumes: nothing from prior tasks (independent of Pipeline work; ordered here only for narrative).
- Produces: a current local tree at `origin/phase1-foundation`; the gate-verification evidence Task 6 builds on.

- [ ] **Step 1: Fast-forward the local branch**

```bash
cd /Users/hyungkoookkim/evidence-ledger
git fetch origin
git status -sb          # expect: ## phase1-foundation...origin/phase1-foundation [behind 21]
git pull --ff-only      # expect: Fast-forward, 21 commits
git log --oneline -3    # expect tip commits from origin (T14 lane / truth-doc fill family)
git worktree list       # expect 3 worktrees under .claude/worktrees/ still listed, no errors
```
If `--ff-only` refuses (diverged), STOP and report — do not merge or rebase; divergence means another session worked locally and the user must arbitrate.

- [ ] **Step 2: Bootstrap the governance deps that arrived with the pull**

```bash
cd /Users/hyungkoookkim/evidence-ledger
.venv/bin/pip install -r requirements-dev.txt
```
Expected: pytest>=8.0 satisfied (venv already exists with Python 3.14).

- [ ] **Step 3: Run the bound repo's own gates**

```bash
cd /Users/hyungkoookkim/evidence-ledger
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py; echo "smoke=$?"
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py
```
Expected: `smoke=0`; unit tests pass; placeholder check PASS (5 allowlisted files). The hermetic import tests (`env -u GIT_INDEX_FILE .venv/bin/python -m pytest import/tests -q`) may need the local supabase stack for 2 files — run them; if stack-dependent tests fail with connection errors, note it (expected without `supabase start`) rather than treating it as breakage.

- [ ] **Step 4: Read the current handoff to learn the working-branch convention** — `git show HEAD:docs/HANDOFF-phase1-2026-07-02.md | tail -40` (or the newest `docs/HANDOFF-*.md` at the new tip). Record for Task 6: which branch new commits should land on (default: `phase1-foundation` if it is still the active line; if the handoff says work moved to `main`, use a short-lived branch off `main` per their conventions).

---

### Task 6: Close evidence-ledger's remaining placeholder debt (4 real entries)

**Files (all under `/Users/hyungkoookkim/evidence-ledger`):**
- Modify: `docs/protocol/claude/core.md` (domain caching bullet)
- Modify: `docs/PROTOCOL-RULES-LOG.md` (R-SKILL trigger slot + `<ref>` tokens)
- Modify: `coordination/bin/claim-lock` (placeholder token in comment/example)
- Modify: `.claude/skills/create-regression-pin/SKILL.md` (placeholder examples)
- Modify: `scripts/placeholder_allowlist.txt` (remove the 4 filled paths; the `tests/unit/test_check_placeholders.py` entry stays — intentional fixture)

**Interfaces:**
- Consumes: Task 5's reconciled tree + branch decision.
- Produces: allowlist shrunk 5 → 1; the repo reaches its "fully bound except intentional fixture" state.

- [ ] **Step 1: Read each of the four sites first** — `grep -n '<PROJECT>\|<entrypoint>\|<domain-skill>\|<fill-in\|<ref>\|TODO(' <file>` per file, then Read the surrounding lines. The fills below are drafts against the Pipeline twins; adapt phrasing to the actual site, but the committed result must contain zero scanner tokens (the 9 tokens listed in their scripts/check_placeholders.py).

- [ ] **Step 2: Fill `docs/protocol/claude/core.md`** — replace the domain-graph caching bullet (Pipeline twin at core.md:186-189) with this repo's real false-fail caching surfaces:

```markdown
- **xcodebuild and the local Supabase stack cache aggressively** — a re-run
  with identical inputs may return a cached result instead of fresh output
  (false-fail, not a real error). Xcode reuses DerivedData
  (`~/Library/Developer/Xcode/DerivedData/EvidenceLedger-*`); a still-running
  `supabase` container serves the previously-applied migrations. Cache-bust
  before concluding the code is broken: delete the DerivedData folder /
  `supabase db reset`. Note `db/tests/conftest.py` already isolates by
  creating a scratch DB per test.
```

- [ ] **Step 3: Fill `docs/PROTOCOL-RULES-LOG.md`** — at the R-SKILL entry's TODO slot, state this repo's actual skill inventory truthfully (one committed skill):

```markdown
evidence-ledger domain-skill triggers: the repo ships one project skill —
`create-regression-pin` (.claude/skills/create-regression-pin/SKILL.md);
invoke it before authoring any strict-xfail regression pin in tests/unit.
No domain-graph skill exists yet; when a Phase-2 subsystem gains one, add its
trigger here in the same commit that lands the skill.
```

Replace any `<ref>` tokens in the same entry with real citations (this repo's binding commit `fee5207` / its ADR-001) or, where the origin evidence does not apply here, the literal text `origin-repo evidence; see hkk009008-svg/governance-os PROTOCOL-RULES-LOG` — whichever the surrounding sentence actually needs. No token may remain.

- [ ] **Step 4: Fill `coordination/bin/claim-lock`** — replace the placeholder in its comment/usage example with a real lock name for this repo, e.g. `claim-lock supabase-migrations "adding migration 20260705..."` (match the script's existing comment style; keep it one line).

- [ ] **Step 5: Fill `.claude/skills/create-regression-pin/SKILL.md`** — replace `<entrypoint>`-style example paths with real ones from this repo: `import/run_import.py` for the pipeline example, `tests/unit/` for the pin location. Keep every rule sentence intact; only the example nouns change.

- [ ] **Step 6: Shrink the allowlist + verify after EACH removal**

```bash
cd /Users/hyungkoookkim/evidence-ledger
# remove the 4 filled paths from scripts/placeholder_allowlist.txt (keep the
# tests/unit/test_check_placeholders.py line and its comment), then:
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py; echo "exit=$?"
```
Expected: `PASS`, `exit=0`, with only the intentional fixture entry remaining. If FAIL, a token survived — fix the file, not the allowlist.

- [ ] **Step 7: Full gate run + commit** (on the branch from Task 5 Step 4):

```bash
cd /Users/hyungkoookkim/evidence-ledger
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py && \
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q && \
env -u GIT_INDEX_FILE git add docs/protocol/claude/core.md docs/PROTOCOL-RULES-LOG.md coordination/bin/claim-lock .claude/skills/create-regression-pin/SKILL.md scripts/placeholder_allowlist.txt && \
env -u GIT_INDEX_FILE git commit -m "docs(governance): close placeholder debt — 4 skeleton fills (allowlist 5 -> 1)"
```

- [ ] **Step 8: Independent verification per THEIR doctrine** — this repo's RUNBOOK-DAILY loop is controller → independent verify → GO/NITS/FAIL → push, with Codex as the standing read-only verifier (their AGENTS.md R-CODEX-VERIFY). Request the Codex verification pass on this commit (`codex exec` lane-v style, read-only, re-derives the verdict from the diff + a fresh gate run). Record the GO/NITS/FAIL. Do NOT push.

---

## Final checkpoints — user actions (nothing here is agent-executable)

1. **Authorize the Pipeline push** (Tasks 1–4 commits on `main`) — or decline; commits are complete and CI-equivalent gates ran locally either way.
2. **Authorize the evidence-ledger push** (Task 6 commit) after its Codex verdict is GO.
3. **Launch the four seats when you want them live** — four terminals, same directory:

```bash
cd /Users/hyungkoookkim/Pipeline
export CLAUDE_SEAT=director        # then director2 / operator / operator2 in the other three
export GIT_INDEX_FILE="$(git rev-parse --absolute-git-dir)/index-$CLAUDE_SEAT"
claude
```
(Indexes are pre-seeded by Task 3; the hook + guard are live. Pairs: A = director+operator, B = director2+operator2.)

## Item-disposition map (audit trail against the 2026-07-07 sixteen-item list)

| # | Original item | Disposition |
|---|---|---|
| 1 | Designate binding target | User decided (evidence-ledger); already executed there → recorded, Task 2 |
| 2 | PROGRAM-MANUAL intent content | Resolved by evidence-ledger ADR-001 (design spec + MANUAL.md = intent doc); Pipeline skeleton intentional → Task 2 ADR-008 |
| 3 | TODO(<PROJECT>) doctrine items | Pipeline: adopter fill-ins by design (ADR-008); evidence-ledger remnants → Task 6 |
| 4 | Pair-A/Pair-B lane confirmation | Pipeline lanes PRINCIPAL-CONFIRMED via ADR-009 → Task 3; evidence-ledger N/A (2-seat by its ADR-001) |
| 5 | License | MIT → Task 1; evidence-ledger is PRIVATE (verified) — none needed |
| 6 | Pre-push gate un-defer? | User: keep deferred; refreshed trigger → Task 3 ADR-010 |
| 7 | Advisory review Rules #17–20 | Decision intake → Task 4 |
| 8 | Threeway bus activation | Deferred with trigger + activation checklist → Task 3 ADR-010 |
| 9 | 4-seat concurrent env | Activated in Pipeline → Task 3 + final checkpoint 3 |
| 10 | Antigravity regime | Deferred with trigger → Task 3 ADR-010 |
| 11 | README/OPERATIONS adoption content + secrets | Filled in evidence-ledger 2026-07-04 (471-line OPERATIONS); Pipeline skeletons intentional → recorded in ADR-008 |
| 12 | Per-instance push/spend authorization | Standing duty — unchanged; enforced by checkpoints above |
| 13 | update-state.sh edit authorization | Standing duty — unchanged (no edits planned; Task 3 only *registers* the existing committed hook, which is per-clone config, not a hook-body edit) |
| 14 | Coordinator commit/push gating | Standing duty — unchanged |
| 15 | Mailbox retroactive audit | Standing duty — sent/ currently empty; becomes live once seats run |
| 16 | Deadlock arbitration | Standing duty — none open |
