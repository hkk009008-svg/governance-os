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

## ADR-013: Multi-target binding registry (governance.toml) — amends ADR-008

**Status:** Accepted

**Context:**
ADR-008 designated evidence-ledger as THE bound target, and the binding was
implemented as hard-coded machine paths (`scripts/ledger_start_guard.py:12-14`
held `PIPELINE_KERNEL`/`FORBIDDEN_KERNEL`/`TARGET_REPO` as `/Users/...`
constants). The 2026-07-11 governance-brief audit deferred multi-target
binding as conflicting with ADR-008; the user-principal overrode that
deferral on 2026-07-11: the kernel must be able to govern FUTURE works, not
just evidence-ledger, so new projects can be started from this governance OS
without editing kernel source.

**Decision:**
(1) Add `governance.toml`, a declarative target registry: `[targets.<name>]`
tables (repository, path, route_keywords, description), a
`[binding].default_target`, and `[paths].forbidden_roots`. (2) Add
`scripts/target_binding.py`: fail-closed resolver (missing file, unknown
target, missing/unknown keys all raise with corrective messages) with
resolution order CLI `--target` > `GOVERNANCE_TARGET` env >
`default_target`, plus a `GOVERNANCE_TARGET_PATH` checkout override and a
read-only `--check` CLI wired into `scripts/protocol_doctor.py`
(`base_commands`). (3) Rewire `scripts/ledger_start_guard.py` to resolve its
kernel (script location), target paths, route keywords, and forbidden roots
through the registry; behavior for the default binding is unchanged (pinned
by the pre-existing tests in tests/unit/test_codex_ledger_bridge.py, which
pass unmodified). (4) ADR-008 is AMENDED, not revoked: evidence-ledger stays
the default target and the product/governance boundary (§8.8) is unchanged;
what changes is that additional targets register declaratively.
Decided by the user-principal on 2026-07-11.

**Consequences:**
- A future work is onboarded by adding a `[targets.<name>]` table (see
  OPERATIONS.md §5.1) — no Python edits; unknown/missing bindings fail
  closed.
- `verified via $ .venv/bin/python -m pytest tests/unit -q → 294 passed`
  (271 pre-existing + 23 new in tests/unit/test_target_binding.py);
  `$ scripts/ci_smoke.py → OK`; `$ scripts/protocol_doctor.py --wave 2 →
  PASS` (now including the registry check).
- ARCHITECTURE.md module-map anchor for `build_guard` moved (133 → 152,
  auto-fixed by `check_doc_claims.py --fix`) and a `resolve_target` row was
  added; the parked Task2U worktree also carries ARCHITECTURE.md edits, so a
  small merge reconciliation there is expected.
- The guard's user-facing strings still say "Ledger seat start guard"; a
  cosmetic generalization is deferred until a second target actually exists.
- `.codex/agents/*.toml` and codex_protocol_model prose still name
  evidence-ledger paths — correct for the default target; regenerating that
  prose per-target is future work when a second target is registered.

## ADR-014: Typed route manifests (route/v1) — JSON authority, Markdown projection

**Status:** Accepted (compatibility layer only; live cutover requires a follow-up ADR)

**Context:**
Route authority is regex-parsed Markdown prose: headings, field aliases, modal
verbs, per-physical-line negation boundaries, and side-effect phrase tables
(`scripts/protocol_capacity.py:58-123,1075-1125,1396-1448`). Because negation
scanning is per-line, wrapping a prohibition across lines changes its machine
meaning (false side-effect demands; the fail-open direction exists too). The
2026-07-11 workbook-refresh campaign and the external improvement brief
(2026-07-11 transfer) both surfaced this class. The only automatic
current-route resolver is reverse-lexicographic filename sort
(`scripts/ledger_start_guard.py:67`), and `Supersedes route:` prose is parsed
by nothing.

**Decision:**
1. Introduce `governance.route/v1`: a strictly-validated JSON object
   (`scripts/route_manifest.py`, documented by `schemas/route-v1.schema.json`).
   Canonical bytes come from `threeway.canon.canonicalize` (RFC 8785) — reuse
   of threeway code AS A LIBRARY; this does not activate the dormant signed
   bus and does not touch `refs/threeway/*` (ADR-010 boundary intact).
2. Authority-vs-projection: the object lives in a sidecar
   `<route-id>.route.json` whose bytes ARE the canonical serialization; the
   Markdown event carries a `route_hash:` pin. Embedding JSON inside the
   route body was rejected because the live prose lint scans every body line
   for side-effect directives and would false-match token field values
   (e.g. `"allowed_command_class": "git push"`).
3. Forward-compatibility fields are REQUIRED from day one so later slices are
   additive-minor, not major bumps (brief §12.2/§12.3): `generation`,
   `parent_route_id`, `expected_control_head` (P0.3 — validated for shape,
   CAS-unenforced in this slice), `packet_delta` (P1.3 — must be null),
   `capability_refs` (P0.4 — must be []).
4. Unknown top-level fields are REJECTED except under an explicit
   `extensions` object. Readers reject unsupported `schema` values.
5. Route identity = mailbox filename stem (zero migration, Rule #8 binding
   preserved). ULIDs were considered and rejected for now.
6. Compatibility only: Markdown routes remain the live authority. The
   comparator (`scripts/route_compat.py`) must show legacy/structured
   equivalence over the fixture corpus (divergences triaged as
   legacy-formatting defects vs regressions) before any cutover ADR.
7. Property-style formatting-invariance is tested with deterministic mutation
   fixtures; adopting `hypothesis` is deferred to the P1.4 slice ADR.

**Consequences:**
- Reformatting prose can no longer change what a structured reader believes;
  during compatibility the legacy validator still governs live routes.
- Known legacy wrapped-negation defect is pinned as a strict xfail
  (R-VERIFY-TIER) rather than fixed in the prose parser.
- Sidecar placement for LIVE routes (mailbox naming-lint interaction) is
  explicitly deferred to the cutover ADR; this slice writes pairs only in
  tests and fixtures.

## ADR-015: Route currency from typed lineage (generation + parent + compare-and-swap)

**Status:** Accepted

**Context:**
The only automatic current-route resolver is reverse-lexicographic filename
sort (`scripts/ledger_start_guard.py` `find_latest_ledger_route`), so a
transient filesystem observation or a stale writer whose artifact name sorts
later could appear authoritative. `Supersedes route:` / `Supersedes active
route:` parent pointers exist in live coordinator routes but are parsed by no
code. Slice 1 (ADR-014) added `generation` / `parent_route_id` /
`expected_control_head` to route/v1 and its renderer emits them, but nothing
consumes them for selection.

**Decision:**
1. Add `scripts/route_lineage.py`: parse the lineage headers (`Route
   generation:`, `Supersedes route:` and its `Supersedes active route:`
   alias, backtick-optional; `Expected control HEAD:`), resolve the
   authoritative route as the lineage TIP (highest-generation route no other
   route supersedes), and offer a compare-and-swap check returning a
   structured `stale_parent` result when a proposed route's parent is not the
   current tip or its generation is not current+1.
2. Rewire `find_latest_ledger_route` lineage-first with a legacy fallback:
   when no candidate route carries a generation header, resolution is
   byte-identical to the prior reverse-lex behavior. The live campaign (zero
   generation headers) is unaffected.
3. `expected_control_head` is parsed and reported, not gated on whole-repo
   HEAD equality (audit modification) — parent + generation are the hard gate.
4. A `route_lineage.py --check` CLI, wired into `scripts/protocol_doctor.py`,
   fails only on lineage inconsistency among generation-bearing routes (any
   fork — multiple unsuperseded generation-bearing tips, whether at the same
   or different generations; a cycle — no tip; or a dangling parent — a
   superseded route absent from the set). It passes on the all-legacy live
   set.
5. This does not activate the dormant signed bus (ADR-010); lineage lives in
   the git-committed mailbox route bodies.

**Consequences:**
- Two concurrent coordinators cannot both become authoritative once routes
  carry generations: a fork is detected (structured issue) and CAS rejects
  the stale writer with a `stale_parent` result to rebase.
- Route ancestry is auditable from parent pointers; resolution is
  deterministic and independent of filename timestamp for
  generation-bearing routes.
- No behavior change for legacy routes; the pre-existing start-guard tests
  pass unmodified.

## ADR-016: Consumable side-effect capabilities (capability/v1 + receipt/v1)

**Status:** Accepted (primitive only; live token authority not cut over in this slice)

**Context:**
Side-effect executor tokens are a 10-field prose contract
(`scripts/codex_protocol_model.py` `SIDE_EFFECT_EXECUTOR_TOKEN_FIELDS`)
validated by a route-time lint (`scripts/protocol_capacity.py`). Nothing
consumes a token at execution time, nothing prevents a token being replayed,
and route supersession does not revoke an outstanding token — the gap
operator2 flagged as a BLOCKER (mailbox 2026-07-10T01-23-27Z: "no token path
or --executor-token input"). Slices 1-2 (ADR-014/ADR-015) added typed route
identity and lineage, which capability↔route binding needs.

**Decision:**
1. Add `scripts/route_capability.py`: `governance.capability/v1` — carries the
   10-field token's authority contract (`allowed_command_class` as an exact
   command literal, `target`, `observer_seats`, `final_closeout_owner`, the stop
   condition, `preflight`, `postcheck`, `non_goals`, `side_effect_id`) with the
   token's executing seat represented as the enum `subject` (not the literal
   field name `executor`), plus a new `issuer` (the granting seat) and the
   lifecycle/binding envelope (`capability_id`, `bound_route_id`,
   `bound_generation`, `state`, `expires_on`). It is NOT a byte-verbatim superset
   of the token. Canonical bytes and hash come from `threeway.canon.canonicalize`
   (RFC 8785) — library reuse; the dormant signed bus (ADR-010) is not activated.
2. `governance.capability-receipt/v1`: a consume writes a receipt carrying
   NON-VACUOUS executed evidence (command + output + a commit SHA or `logs/`
   artifact ref), mirroring `scripts/check_go_schema.py`. A bare
   `state="consumed"` flip with no evidence is rejected as anti-ceremony.
3. Consumption is ATOMIC and one-time via a filesystem compare-and-swap: the
   complete receipt is written to a temp file (`tempfile.mkstemp`), fsynced, then
   `os.link`-ed to the canonical path keyed by `capability_id`. The `os.link` is
   the CAS — it raises `FileExistsError` iff the path already exists (so the first
   consumer wins; a replay fails `already_consumed`), and the canonical path never
   appears with partial content, so a failed/killed write cannot brick the grant.
4. Revocation-on-supersession reuses Slice-2 lineage: a capability is current
   only while its `bound_route_id`/`bound_generation` equal the authoritative
   route's (Slice-2 `resolve_authoritative`). A capability bound to a
   superseded generation is invalid unless a newer route carries it forward
   via route/v1 `capability_refs`.
5. A `route_capability.py consume` CLI is the mechanical enforcement point (a
   script that accepts a token at execution time and refuses replay). Before it
   writes a receipt, `consume` enforces two authority checks fail-closed: (a) the
   executed evidence command must match the capability's `allowed_command_class`
   (the exact command literal or a `<literal> …` prefix), else
   `command_class_mismatch`; and (b) when `--route-root` is supplied, the
   capability must be current against the authoritative route (Slice-2
   `resolve_authoritative`), else `stale_capability` — this is what makes "a stale
   capability is refused at execution time" (below) true. Exit codes: 0 consumed
   / 3 already_consumed / 4 stale_capability (or a `--route-root` with no lineage
   generation to check against) / 2 other refusal (invalid capability, vacuous
   evidence, `command_class_mismatch`). Wiring `--executor-token` into the dormant
   `execute_threeway_cutover.sh` is a follow-up with the parked signed-bus plan.
6. Compatibility: the prose token blocks and the live route-time token lint
   are UNCHANGED and stay fail-closed; capability/v1 is generated + validated
   alongside, not yet the live authority.
7. ADR-012 invariant preserved: no capability state substitutes for the user
   push gate. A consumed capability is necessary, never sufficient.

**Consequences:**
- Side-effect authority becomes replay-safe and route-bound; a stale or
  already-used capability is refused at execution time by a real script.
- No behavior change to live routes or the token lint; the active campaign is
  unaffected (all new files).
- Full cutover of live token authority to capability/v1 and wiring into the
  signed-bus cutover script are scoped follow-ups.

## ADR-017: Orthogonal packet state — derive work/verification dimensions (Part A: derivation only)

**Status:** Accepted (derivation module only; the gate remap is deferred)

**Context:**
The capacity-packet `status` field (ready|active|blocked|done|excepted,
`scripts/protocol_capacity.py`) overloads three orthogonal facts: what
happened to the work, whether the seat is still represented in the active
cycle, and whether the result was independently accepted. Because G1
exactly-one coverage requires every seat to own exactly one current packet
per active cycle, a work-COMPLETE packet is forced to sit at `blocked` — e.g.
the workbook-refresh director2 preflight carries completion `done_evidence`
yet status is `blocked`. `done` separately doubles as the verification
carrier for G5/G6. This damages semantic truth and blocks future automation.

**Decision:**
1. Add `scripts/packet_state.py`: the `work_state` and `verification_state`
   vocabularies, a `work_state` transition table + `is_valid_work_transition`,
   and pure `derive_work_state` / `derive_verification_state` functions that
   read the legacy `status` / `packet_type` / `done_evidence`
   fields. The derivation is READ-ONLY: it writes no packet, adds no field,
   and changes no gate.
2. A report CLI (the default and only action; no `--report` flag) renders legacy status beside the derived states and flags
   divergences (a `blocked` packet whose derived `work_state` is `completed` —
   the overloading made visible). Exit 0 always; it is a diagnostic, never a
   gate.
3. `unable_to_verify` is a verdict, never a stored status; the derivation may
   return it only for a completed operator-verification packet with no
   parseable verdict, and it is never persisted.
4. Part B — accepting orthogonal fields at parse time in `protocol_capacity.py`
   and remapping G1/G5/G6 onto the new dimensions — is DEFERRED. It changes the
   live board's validity and is gated on the active workbook-refresh cycle
   closing.

**Consequences:**
- The completed-vs-blocked overloading becomes machine-visible without any
  change to live gates or packet files; the active campaign is unaffected.
- The derivation is the semantic-truth foundation Part B will wire into the
  gates once the campaign closes.
- No packet ever needs to be mislabeled to satisfy coverage once Part B lands;
  until then the legacy representation is unchanged.

## ADR-018: Property + stateful testing of the kernel validators (hypothesis, dev-only)

**Status:** Accepted

**Context:**
The Slices ADR-014..017 validators (route/v1, lineage, capabilities,
packet-state) are covered by example-based unit tests. Interaction and
edge-case failures (the class an independent Codex pass repeatedly surfaced
on the capability slice) are better caught by generated inputs. The audit
sequenced this after ADR-016/017, which are now complete.

**Decision:**
Add `hypothesis>=6` to `requirements-dev.txt` ONLY — the governance runtime
stays two dependencies (`requirements-governance.txt` unchanged, ADR-004
context). Add property tests driving the four session-owned validators
(no-crash, fail-closed, determinism, no-mutation, vocabulary-membership,
round-trips) and a `RuleBasedStateMachine` over capability consumption (the
one-time invariant). Hypothesis runs under a fixed-seed/derandomized profile
so CI is reproducible (R-MEASURE). Scope excludes the contended live
`protocol_capacity.py` validator (campaign mid-pivot); a property that
surfaces a real defect in an owned validator is fixed the same session or
pinned strict-xfail (R-VERIFY-TIER-B).

**Consequences:**
- The kernel validators gain generated-input coverage; regressions and edge
  cases are caught in CI, not post-hoc.
- Dev/CI installs one more package; runtime install is unchanged.
- Non-determinism is avoided via the seeded profile; failures reproduce.

## ADR-019: Independence-first verification is the OS default (R-INDEPENDENCE)

**Status:** Accepted

**Context:**
The 2026-07-12 governance-improvement retrospective examined why so many
defects surfaced across six kernel-hardening slices. Root cause: for every
slice, one model (in author, implementer, and reviewer hats via subagents)
produced work that passed all internal review, and the only independent
perspective — a cross-model Codex Lane-V pass — ran only at the END, per slice.
Independence-at-the-end-only let a whole change's blind spots accumulate.
Every adversarial defect (control-char injection ×2 in two renderers, a
compound-command bypass, authority that was computable-but-not-enforced at the
point of use, a comparator path escape, a route-id/filename binding gap, a
one-time-token bricking-on-crash, property-test vacuousness, and a
total-function gap in already-shipped code) had been approved by same-model
internal review and was caught only by the different-perspective verifier. The
OS's own four-seat model already prescribes separation of build and verify
(ADR-001) — but nothing forced that independence to (a) fire at DESIGN time or
(b) use a genuinely DIFFERENT model rather than the same model in an operator
seat. The user-principal directed on 2026-07-12 that this behavior become the
OS default.

**Decision:**
Adopt **R-INDEPENDENCE** as standing doctrine (Scope: both). For an
adversarial-surface change (parses/renders/composes input into a
parseable-or-executable context; enforces authority or a security boundary;
gates a side effect; validates a trust-granting schema), independent
verification is required at TWO points: (1) design-time — an independent
reviewer, preferably a DIFFERENT model/harness than the author, enumerates the
abuse/edge cases before implementation, and the author folds them into the
plan's acceptance criteria as enforced-and-tested behaviors, not aspirational
guarantees; (2) per-task, before "done" — an independent reviewer verifies the
diff against those cases, and for an adversarial surface this SHOULD be
cross-model because same-model review has correlated blind spots and is
near-vacuous on exactly these surfaces (the enforcer-is-enforced anti-pattern,
ADR-003). This EXTENDS ADR-001 / Rule #23 and COMPLEMENTS R-VERIFY-TIER (which
caps redundant same-question passes; R-INDEPENDENCE requires an early
new-perspective pass). The operative stub lives in CLAUDE.md; the full text is
`docs/protocol/claude/independence-first.md`. Non-adversarial / read-only /
hermetic work does not trigger it.

**Consequences:**
- Adversarial-surface changes now carry a design-time cross-model enumeration
  and a per-task cross-model verification, not just an end-stage pass.
- Follow-ups (recorded, not yet done): mechanize the cross-model requirement in
  `scripts/check_go_schema.py` (a same-model review must not be claimed to
  discharge an adversarial-surface task); sync the stub into `AGENTS.md` (the
  Codex twin) once it is not mid-edit by a peer lane; add the design-time
  enumeration step to the dispatch templates in `docs/templates/claude/`.
- This ADR was itself drafted by a Claude seat and is being independently
  reviewed cross-model (dogfooding R-INDEPENDENCE on R-INDEPENDENCE).

## ADR-020: Mandatory blind Opus review after Codex Lane V

**Status:** Accepted (user-approved design, 2026-07-12)

**Context:**
Codex can independently verify a landed change, but implementation and
verification may still share a model family and therefore a correlated blind
spot. The user requires a cross-model Claude Opus pass after every Codex Lane
V verification. The existing protocol also forbids authority leakage, paid
calls without authorization, and redundant third reviews over an unchanged
commit.

**Decision:**
1. After completing its primary analysis, every Codex Lane V verifier attempts
   exactly one verdict-blind Opus review through
   `scripts/opus_review_bridge.py`.
2. The Opus request contains immutable reviewed scope and requirements but no
   Codex verdict, report, findings, or conclusion.
3. The bridge loads verifier text from the explicit reviewed base or the first
   parent of reviewed HEAD, then supplies that immutable pre-HEAD text through
   `--append-system-prompt`. Claude runs with `--safe-mode`,
   `--disable-slash-commands`, an explicit Opus model, top-level turn limit,
   empty setting/MCP sources, disabled edit/agent tools, and no session
   persistence. It validates the Claude `system/init` model metadata, accepts
   only Opus, normalizes output as `opus-review/v1`, and never retries.
4. Every Opus finding receives a `confirmed`, evidence-backed `disproved`, or
   `unresolved` disposition. Unresolved findings block GO.
5. The operator retains GO/NITS/FAIL authority. Opus cannot write protocol
   state, release locks, or authorize side effects.
6. A network-capable outer macOS sandbox denies source/snapshot and persistent
   home writes. One-shot, unguessable broker tokens bind each admitted Bash
   command to pre-registered argv; the broker launches that argv outside the
   inherited outer Seatbelt and inside a second profile that denies network,
   source/sensitive reads, non-scratch writes, and unlisted executables.
7. Pipeline identity and expected commits are proved before authorization or
   other reconcilable unavailability can be returned. Reconciliation receives
   an explicit Pipeline repo root and proves expected commits exist before GO.
8. Parent-supplied recorded authorization permits exactly one bounded Opus
   call; it does not grant inherited paid-spend authority.
9. Missing authorization, sandbox, credentials, network, valid schema,
   matching scope, or proven Opus identity yields an explicit degraded Codex-only fallback;
   it is never silently treated as a pass.
10. Automated tests fake the Claude process. A live model smoke remains a
   separately authorized optional check.

**Consequences:**
- Same-model verifier blind spots receive a mandatory independent model pass
  when Opus is available.
- Verification remains usable when the external provider is unavailable, but
  the reduced assurance is visible in the report.
- The Opus pass is the second reviewer for the same question; R-VERIFY-TIER
  still forbids a third generic pass without a distinct pre-stated question.
- V1 is Pipeline-scoped and uses no MCP service or new Python dependency.

## ADR-021: consume enforces target, consumable-state, evidence totality, logs_ref confinement, int-only currency

**Status:** Accepted

**Context:**
The design-time independent coverage enumeration mandated by R-INDEPENDENCE
(ADR-019) surfaced — and direct probes CONFIRMED — five defects in the shipped,
three-round-Codex-GO'd `scripts/route_capability.py`: (CRITICAL) `consume`
enforced the command CLASS but not the TARGET, so a capability for
`target: origin/main` accepted `git push attacker/main`; (HIGH) `consume`
accepted any schema-valid `state`, including `revoked`/`expired`/`failed`, and
never consulted `expires_on`; (robustness) `consume` raised `KeyError`/
`AttributeError` on malformed evidence instead of a typed refusal; (MED)
`validate_receipt` accepted a traversing `logs_ref` (`logs/../../etc/passwd`);
(LOW-MED) `capability_is_current` treated a boolean generation of `True` as `1`.
The CRITICAL and HIGH are the exact "computable-but-not-enforced" class an
earlier Codex pass caught for the command field — fixed for the instance, not
the class. None had been caught by same-model review or end-stage manual
cross-model probing; only systematic independent design-time enumeration found
them (the R-INDEPENDENCE thesis, demonstrated).

**Decision:**
`consume` now enforces, fail-closed before any filesystem write, in order:
evidence totality (`_validate_evidence`; never raises) → capability validity →
consumable state (`CONSUMABLE_STATES = {issued, activated}`) → currency (int-only
generations) → command class (unchanged) → target
(`_command_targets_match`: the command's non-flag argument components, split on
whitespace and `/`, must EQUAL the capability's target components in order —
strict/fail-closed, accepting `git push origin main` for `origin/main`,
rejecting `git push attacker/main` and any extra/different ref). `validate_receipt`
rejects a `logs_ref` that is absolute, contains a `..` component, or escapes
`logs/` (pure lexical). This is an authority-semantics change (hence an ADR).
The target rule was author-proposed (the independent Codex design-generation run
was cut off) and adversarially verified cross-model at Lane-V per R-INDEPENDENCE.

**Consequences:**
- A capability now authorizes exactly one command class acting on exactly its
  target, from a consumable state, with total/typed refusal on malformed input.
- Dynamic `expires_on` enforcement still needs a packet-completion signal
  `consume` lacks; deferred (the terminal `expired` state IS refused). The
  capability `non_goals` prose (e.g. "no force-push") remains unenforced —
  `--force-with-lease` is accepted by the target rule; a future increment may
  enforce non_goals. check_cas/parse_lineage/render_markdown parallels flagged
  by the same enumeration are the next re-verification targets.
- `git push` → `git push origin main` updates in existing tests (command must
  now match target) preserve their original invariants (reviewed).

## ADR-022: R-INDEPENDENCE empirically validated — cross-model verification found eight defects same-model review missed

**Status:** Accepted

**Context:**
ADR-019 made independence-first verification (R-INDEPENDENCE) the OS default on
the strength of a retrospective. On 2026-07-12 the user-principal reset the Codex
usage limit and directed re-verifying the shipped, already-"GO"'d adversarial
slices — which produced a controlled test of the doctrine itself. Slice-7 (the
capability-consumption authority, `scripts/route_capability.py`) had passed three
same-model Codex rounds AND a 17-vector author-run adversarial battery that
reported "0 residual." A cross-model Codex Lane-V loop then FAILed it four times
before returning GO on the fifth pass. Each FAIL was a distinct, independently
reproduced, real defect — eight in total: (1) a target-confinement `/`-flattening
differential (`git push /origin/main` accepted for target `origin/main`); (2)
non-UTF-8-string totality (a lone surrogate raised at `canonicalize` after the
store `mkdir`); (3) a sibling JSON-schema doc weaker than the enforced check; (4)
git-argv tokenization non-equivalence (trailing-NBSP-via-`strip`, slash-form,
multi-refspec); (5) a flag smuggled via the command-CLASS prefix
(`allowed_command_class="git push --repo=attacker"`); (6) non-finite-float
totality (NaN/Inf in a validated field); (7) a push-specific target model riding
a non-push command class; (8) out-of-range-integer totality. None was found by
same-model review. The recurring shape: fixing an INSTANCE re-exposed the CLASS
(a `/`-fix led to the whole tokenization class; string-totality led to float-
then int-totality) — ADR-019's "fix the class, not the instance" made concrete.

By contrast, the two part-#4 fixes in the SAME session (route_manifest
`next_trigger` structural smuggling; route_lineage `check_cas` int-only
generations) were designed against an INDEPENDENT design-time enumeration BEFORE
implementation and each cleared cross-model verification on the FIRST pass — the
exact difference R-INDEPENDENCE predicts between end-only and design-time
independence.

**Decision:**
Record this as the canonical empirical evidence for ADR-019, and affirm two
operating rules it establishes. (a) Design-time independent enumeration BEFORE
implementation is the load-bearing half of R-INDEPENDENCE: the two first-pass-GO
fixes had it; slice-7's original build did not. (b) A cross-model verification
loop that keeps returning FAIL on genuinely-NEW defects is CONVERGENCE, not
thrashing, and is permitted under R-VERIFY-TIER (which caps redundant
SAME-question passes, not new-question ones); it terminates on GO or on a scope
decision surfaced to the user (here, a restrict-vs-generalize command-class fork
at pass 4). Same-model self-verification — however many rounds, however large the
self-run battery — does NOT discharge an adversarial-surface task (ADR-003
enforcer-is-enforced, now quantified at 8/8 defects missed).

**Consequences:**
- Slice-7 shipped cross-model-clean (`origin/main` through `e13d410`); the
  part-#4 fixes shipped (`75aeb3a`, `c3f2e9c`). Every defect has a committed
  regression test that fails on the pre-fix code.
- Operational fragility recorded, not yet mechanized: cross-model verification
  depends on a single external harness (Codex) whose availability gates "done."
  A fallback independent-verification path for when it is unavailable is a
  follow-up — until then the doctrine can block on that harness.
- Push authority is per-action and user-gated (R-VERIFY-THEN-PUSH): a "fix X"
  authorization does NOT extend to a push, and a cross-model GO satisfies the
  verification gate but NOT the push gate — reaffirmed after the auto-mode
  classifier correctly blocked an inferred push of the part-#4 commits this
  session.
- No renumbering (append-only). This is a LOCAL ADR (022); the 027/028/032/034-064
  markers remain origin-repo provenance per ADR-006, so 022 (not 035) is the
  correct next local number.

## ADR-023: Make Codex R-INDEPENDENCE operative and authorize one standing Lane-V Opus attempt

**Status:** Accepted (user-approved design, 2026-07-12)

**Context:**
ADR-019 made independence-first verification standing doctrine but left the Codex operative stub and executable role surfaces unfinished. ADR-020 required one blind Opus pass after Codex Lane V, yet its task-level authorization rule made that required pass degrade whenever a parent prompt omitted repeated consent. The user-principal directed that R-INDEPENDENCE become the Pipeline Codex default and granted standing consent for only the existing bounded post-Lane-V Opus attempt.

**Decision:**
Pipeline Codex classifies the four ADR-019 adversarial surfaces before implementation. Triggered work requires a committed independent design-time abuse/edge/coverage enumeration and independent actual-diff verification before completion. The Codex executable model and core role prompts carry that default. For the exact `codex-lane-v` review profile, after Pipeline identity, reviewed commits, immutable reviewed-HEAD scope, and command validation, an absent authorization source resolves to `standing-policy:codex-lane-v-opus-v1`. Explicit `user-task:` and `verify-request:` sources remain valid; malformed or explicitly forged standing sources fail closed. The normalized review schema advances to `opus-review/v2` with a required profile; v1 review JSON is rejected rather than inferred, while `opus-reconciliation/v1` remains unchanged. One invocation launches at most one provider process and never retries or substitutes another reviewer. Protocol rules allow one invocation per unchanged Lane V verification. Operator authority and every other paid-spend or side-effect gate remain unchanged.

**Consequences:**
- This extends ADR-019 and supersedes only ADR-020's task-authorization, v1-contract, and separately-authorized-live-smoke details for the named Pipeline Lane V profile.
- Unavailable credentials, network, sandbox, provider, or valid output remain visible degraded Codex-only evidence after standing authorization is recorded.
- The bridge enforces one provider process per invocation. Cross-process uniqueness remains auditable from profile, authorization identity, and reviewed commits rather than adding a mutable global call ledger.
- Standing consent does not authorize design-time Opus or any unrelated paid operation.
