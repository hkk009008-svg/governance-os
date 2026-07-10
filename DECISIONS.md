# DECISIONS — Architecture Decision Record Log

This file is the append-only ADR log for Governance OS. Each entry records an
architectural or governance decision at the moment it was made, together with
the context that made it necessary and the consequences (positive and negative)
accepted at that time. **Append-only — never edit prior entries.** If a
decision is superseded, add a new entry that references the old one by number
and explains what changed and why; leave the original entry exactly as written.

---

## ADR Template

```
## ADR-NNN: <Short imperative title>

**Status:** Proposed | Accepted | Superseded by ADR-NNN

**Context:**
[1–3 sentences: what situation, constraint, or problem forced a decision?]

**Decision:**
[1–3 sentences: what was decided, stated unambiguously.]

**Consequences:**
- [Positive consequence]
- [Negative consequence / accepted tradeoff]
- [Follow-on work created, if any]
```

---

## ADR-001: Adopt the 4-seat governance operating system

**Status:** Accepted

**Context:**
As Governance OS grows, uncoordinated parallel edits and unverified claims have
caused repeated integration failures. A lightweight governance model is needed
that enforces independent verification without slowing routine work.

**Decision:**
Governance OS operates with a 4-seat model (two director seats, two operator seats
per pair). Director seats author briefs and make strategy calls; operator seats
independently verify every commit before it is considered landed. No commit is
treated as complete until the responsible operator seat issues a GO report.

**Consequences:**
- Defects are caught by a second set of eyes before they compound.
- Every cross-cutting change requires a co-sign, adding latency to large refactors.
- Seat discipline (mailbox protocol, presence files, lock claims) must be kept
  current; letting it drift negates the benefit.

---

<!-- Append new ADR entries below this line. Do not edit entries above. -->

## ADR-002: Gate adoption placeholders in CI (fail-closed allowlist)

**Status:** Accepted

**Context:**
The governance OS ships as a transfer bundle with skeleton docs that deliberately
contain adoption-placeholder tokens (`<PROJECT>`, `<fill-in>`, etc.). These
placeholders can be read by agents as if they were real doctrine, and a half-bound
repo (some skeletons filled, some not) currently passes the green smoke check —
there is no gate that catches un-replaced placeholders.

**Decision:**
Add an allowlist-based fail-closed placeholder scan (`scripts/check_placeholders.py`
+ `scripts/placeholder_allowlist.txt`). The script fails (exit 1) when any
placeholder token appears in a non-allowlisted file. The initial baseline allowlist
is generated empirically from the live repo (every file currently containing a token
is allowlisted). As adopters fill skeletons, they remove paths from the allowlist;
an empty allowlist with a clean scan is the definition of "fully bound." The gate is
wired into CI smoke in task A-WIRE.

**Consequences:**
- A half-bound repo will fail CI rather than silently passing green.
- Filling a skeleton now requires a mechanical step: remove its path from the
  allowlist, confirm the scan is still clean, then commit.
- An empty allowlist + clean scan is a machine-checkable definition of "fully bound."

---

## ADR-003: Make GO-evidence and ARCHITECTURE-freshness machine-checkable

**Status:** Accepted

**Context:**
High-value soft rules (GO reports must carry real evidence; ARCHITECTURE facts must
be re-verified when changed) were prose-only, enforced by the same class of agent
they govern ("the enforcer is the enforced"). Agents could issue a GO citing only
`wave_gate_check` (which reads an inventory string, not a test execution) or edit
`ARCHITECTURE.md` without bumping its `*Last verified:*` stamp — leaving stale
provenance on the truth layer — with no mechanical backstop.

**Decision:**
Promote them to fail-closed scripts: `scripts/check_go_schema.py` (task A2 — a GO
verification-report must carry verdict + command/output + a commit SHA (or a `logs/`
artifact ref); a GO citing only `wave_gate_check` fails) and
`scripts/check_arch_freshness.py` (task A3 — editing
`ARCHITECTURE.md` without bumping its `*Last verified:*` stamp fails). Both are
wired into smoke/CI in task A-WIRE.

**Consequences:**
- GO reports and ARCHITECTURE edits now have teeth in CI; ceremony-only evidence
  is blocked at the gate rather than caught (if at all) in post-hoc review.
- Adopters must bump the `*Last verified:*` stamp on every substantive ARCHITECTURE.md
  edit — a small but non-zero friction increase for truthful updates.
- Verify-then-push machine-checkability remains deferred (see ADR-005 / task A7).

---

## ADR-004: Python runtime floor

**Status:** Accepted

**Context:**
`pyproject.toml` pinned `requires-python = ">=3.13"`, a steep adoption bar for a
governance-OS bundle that uses only stdlib plus two third-party dependencies. All
three wave-1 scouting audits flagged the floor as unnecessarily restrictive. An
exhaustive grep of all first-party `*.py` files was required before lowering.

**Decision:**
Lower `requires-python` from `">=3.13"` to `">=3.11"`. Grep across every
`scripts/*.py`, `threeway/*.py`, and `tests/**/*.py` file confirmed zero usage of
3.12-/3.13-only features: `itertools.batched`, `typing.override`/`@override`,
PEP 695 type-alias (`type X = ...`) or generic (`def f[T]`, `class C[T]`) syntax,
`typing.ReadOnly`, `typing.TypeIs`, `warnings.deprecated`, and
`sys.version_info >= (3, 12/13)` guards all returned empty results. `tomllib` (the
sole stdlib import that could have blocked lowering) has been available since 3.11.

Grep evidence (task A5, 2026-06-30):

```
$ grep -rn 'itertools\.batched' --include='*.py' .               → (no output)
$ grep -rn 'typing\.override\|@override' --include='*.py' .      → (no output)
$ grep -rn '^type [A-Z]' --include='*.py' .                      → (no output)
$ grep -rn 'def [a-zA-Z_]*\[' --include='*.py' .                 → (no output)
$ grep -rn 'class [A-Z][a-zA-Z_]*\[' --include='*.py' .          → (no output)
$ grep -rn 'except\*\|ExceptionGroup' --include='*.py' .         → (no output)
$ grep -rn 'typing\.ReadOnly\|typing\.TypeIs\|warnings\.deprecated' --include='*.py' . → (no output)
$ grep -rn 'sys\.version_info.*3.*1[23]' --include='*.py' .      → (no output)
```

All commands excluded `.venv/` and `__pycache__`. CI smoke (`scripts/ci_smoke.py`)
exits 0 after the change.

**Consequences:**
- Adoption floor drops from Python 3.13 (released Oct 2024) to 3.11 (Oct 2022),
  widening the compatible install base significantly.
- No functional change to the code; the 3.13 CI runner in `.github/workflows/ci.yml`
  is unchanged (matrix builds are out of scope for this task).
- If a future change genuinely requires a 3.12/3.13-only feature, a new ADR
  superseding this one should raise the floor back and document the specific feature.

---

## ADR-005: commit↔GO linking convention (pre-push gate deferred)

**Status:** Accepted

**Context:**
R-VERIFY-THEN-PUSH ("no push before an operator GO") is prose-only. Making it a
fail-closed gate needs a reliable commit↔GO link.

**Decision:**
DOCUMENT the existing convention (a `verification-report` GO references the reviewed
commit SHA — via the grandfathered `related-commits:` field or the v6.0 H1
``commit `<sha>` ``). DEFER building the pre-push gate
(`scripts/check_verify_then_push.py`) to a future session, because: (a) the link is
semi-structured (v6.0 SHA-in-prose vs grandfathered YAML field) so a blocking gate
risks false-blocks; (b) the mailbox is empty (nothing to gate yet); (c) a pre-push
hook is per-clone + policy-setting in the current single-operator deployment. Decided
by the user-principal on 2026-06-30.

**Consequences:**
- R-VERIFY-THEN-PUSH stays SOFT (agent-discipline) for now; the next session can build
  the gate once GO events exist and the link is normalized.
- The proposed gate shape: given the commits being pushed, if any touch production
  paths and no matching-SHA GO `verification-report` exists, block.
- No false-block risk introduced today; the gate can be made fail-closed in a later
  session with real GO events to validate against.

---

## ADR-006: Origin-repo ADR numbers are provenance citations, resolved here

**Status:** Accepted

**Context:**
Code and docs imported with the transfer bundle cite ADR numbers from the origin
repo's DECISIONS.md (239 KB, deliberately excluded per TRANSFER-MANIFEST.md):
`ADR-027/028/032` in `scripts/{ci_smoke,check_no_ceremony,consume_reviewer_result,
wave_gate_check,pin_reconciler,continuation_readiness}.py`, `docs/templates/claude/
reviewer.md`, `AGENTS.md`, and `.github/workflows/ci.yml`; the `ADR-034..064`
signed-bus series in `docs/protocol/threeway/` and `tests/unit/test_reducer.py`.
This log holds only ADR-001..005, so those citations dangle. Rewriting every site
would churn dozens of imported files; renumbering is forbidden (append-only log).

**Decision:**
Keep the imported citations as **origin-repo provenance markers** and resolve them
here. What the cited numbers decided in the origin repo:

- **ADR-027** — the remediation-inventory `status` column is display-only;
  "verified" must be backed by executed strict-xfail regression pins (run with
  `--runxfail`); `wave_gate_check.py` reads inventory strings and is never
  correctness evidence by itself.
- **ADR-028** — anti-ceremony: appearance-of-verification-without-substance is
  forbidden and mechanically detected; `scripts/check_no_ceremony.py` is the
  enforcement arm and hard-fails smoke/CI.
- **ADR-032** — the machine-readable `reviewer-result/1` schema
  (`docs/templates/claude/reviewer.md`) plus its consumer
  (`scripts/consume_reviewer_result.py`); severity map critical→CRITICAL,
  important→MAJOR, minor→MEDIUM; a GO must cite an executed pin run.
- **ADR-034..064** — the threeway signed-bus hardening series: mailbox→bus
  migration (034), forgery hardening (036/037/038), TOTAL fail-closed gate +
  authority-aware reducer (039/040/041), pair-namespaced candidate ids (042),
  legacy projection/divergence (044/045), and related decisions cited across
  `docs/protocol/threeway/`.

New local decisions continue sequentially from this entry (ADR-007, …). Origin
numbers ≥ 027 are never reused for local decisions and never renumbered.

**Consequences:**
- Every dangling `ADR-0NN` (NN ≥ 27) citation in imported code/docs now resolves
  to this entry without editing the imported files.
- Local numbering stays permanently discontinuous with origin citations; this
  entry is the signpost that numbers ≥ 027 mean "origin repo."
- If an origin rule is materially changed in this repo, write a new local ADR
  that names the origin number it supersedes.

---

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

---

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

## ADR-011: Advisory review of thin-evidence Rules #17–#20 — all kept fully active

**Status:** Accepted

**Context:**
docs/protocol/advisory-candidates.md parks four thin-evidence rules for a
user-principal review. The review ran 2026-07-07 with fresh read-only
evidence: Rule #17's trigger had already fired and been discharged
(2026-06-09 v5.6 retro, ~18 documented workflow runs, "net-positive and
retained as-is" — docs/protocol/claude/director-operator.md:1160-1209) while
the parking list was never updated; Rules #18/#19/#20 remain at their
codification N-counts (0/1/1) with triggers unfired (Rule #19's related
Candidate #9 incident is explicitly not counted toward its N=2 per
docs/PROTOCOL-RULES-LOG.md:576-580).

**Decision:**
User-principal verdicts, 2026-07-07: Rule #17 — keep fully active and DELIST
from the advisory-candidates list (graduated; no longer thin-evidence).
Rules #18, #19, #20 — keep fully active, stay listed, revisit triggers
unchanged. No rule body or HARD/SOFT tag changes.

**Consequences:**
- The stale parking-list entry for Rule #17 is corrected; the list again
  matches the rule bodies it indexes.
- Rules #19/#20 get their first real field exposure now that 4-seat
  operation is active (ADR-009); a recurrence would meet their N=2 triggers.
- No enforcement surface changed — this is a record-keeping decision.

## ADR-012: Claude-tree Tier-2 reconciliation — §E push subordinated to the side-effect gate; origin-provenance banners

**Status:** Accepted (user-principal: "tier2 proceed", 2026-07-11)

**Context:**
A 7-agent verification audit of the Claude-side adaptation (`9ba5387`,
`27ae0c3`) left Tier-2 items needing principal judgment: the §E emergency text
in docs/protocol/claude/director-operator.md still allowed "commit + push if
needed"; the claude-tree rule bodies cite origin-project SHAs/ADRs/modules as
empirical bases; four-seat-extension.md's lane slots carried a contradictory
origin "FINAL (2026-06-13)" badge alongside ADR-009's 2026-07-07 lane record.

**Decision:**
1. Emergency §E never overrides the side-effect gate: mitigation COMMITS are
   allowed under temporary authority, but push remains user-gated in ALL cases
   (aligns with the three-way non-negotiable and R-VERIFY-THEN-PUSH).
2. The claude-tree rule bodies carry a provenance banner: origin-project
   empirical bases stay verbatim (SHA-ref baseline frozen); Pipeline-live
   specifics are governed by docs/protocol/claude/continuation.md.
3. ADR-009 remains the operative lane record; four-seat-extension.md's lane
   slots stay unbound per ADR-009's own instruction, now with explicit
   pointers to ADR-009 at each lane mention.
4. Product-knowledge placeholders are bound from documented side-effect/spend
   classes (money-gate-reviewer phase list) or generalized to their lesson
   class (core.md caching false-fail) rather than left as dead TODOs.

**Consequences:**
- .claude/agents/money-gate-reviewer.md and docs/protocol/claude/core.md
  become placeholder-clean and leave the ADR-002 allowlist.
- The SHA-ref baseline digest refreshes (line shifts only; the citation set
  and count are unchanged).
