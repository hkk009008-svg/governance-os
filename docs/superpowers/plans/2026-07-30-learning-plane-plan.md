# Learning Plane — target-state specification and file-level implementation plan

Status: PLAN. This document commits the design; it lands no runtime.
Baseline: main at 29e06d4. ADR: assigned at Stage 0 landing; ADR-067 was free
at plan time (repo-wide grep, zero matches), and ADR-035 requires re-running
that grep in the same change that assigns the number.

Provenance and verification. The research input is the codex-side study of
Hermes 0.19.0 (branch marker `codex/repository-unification-2026-07-30` points
at main; the study text is uncommitted input). Load-bearing claims were
verified twice: an eight-agent read-only survey of every Pipeline seam, then a
three-skeptic adversarial pass on this plan's own draft (authority-invariant,
repo-reality, subtraction) that returned 25 findings. Every finding is folded
in below. Two corrections that pass through the whole document:

- Baselines were first measured on the survey's checkout, an ancestor 56
  commits behind main, and reported 824 events / 175 verify-requests / 151
  reports and "7 drifted skill pairs." The reality skeptic caught the drift.
  Corrected at 29e06d4 by `git ls-tree -r HEAD coordination/mailbox/sent/`:
  847 sent events; kinds coordination 430, verify-request 186,
  verification-report 162; reports-per-request 162/186; 9/9 mirrored
  `.claude`↔`.agents` skill pairs differ (plus 2 `.agents`-only skills,
  antigravity-harness and kurogane-metahuman-explore; 0 Claude-only);
  `logs/claims/ledger.jsonl` rows 1; `memory-candidate` instances 0. The
  wrong-tree measurement surviving into a draft is itself the
  environment-of-record failure this repo keeps re-teaching, so Stage 0
  re-runs every count in the same change that records it.
- The authority skeptic found two structural defects the draft asserted past:
  the candidate lifecycle's "fail-closed, exact-hash-bound" property had no
  owning enforcement point in Stages 2–5, and the two largest builds (skill
  manifest + materializer) rested on an unverified prose premise. Both are
  resolved below by subtraction, not by adding machinery.

## 1. Purpose and non-goals

Build the missing learning lifecycle (observe → extract → candidate → evaluate
→ promote → distribute → measure → supersede) on the existing governance
spine, provider-neutral across Claude, Codex, AGY, Cursor.

Non-goals, binding on every stage: no Hermes transplant; no autonomous
canonical writes; no embeddings before FTS is measured insufficient; no new
approval machinery where the compact pair already is one; no
"most-sessions-should-update-something" bias — candidates come from evidence
triggers only.

## 2. Authority model — honest about where enforcement binds

The draft listed I1–I7 as "testable obligations." The authority skeptic showed
several had no enforcement point: the mailbox writer payload-validates only
`verify-request` and `verification-report`
(`scripts/mailbox_writer.py:165-209`); every other kind — including `decision`
and a new `learning-candidate` — publishes durably on envelope checks alone,
and read-side parsers refuse nothing that no consumer runs (the
correct-but-uncalled class). So this section states plainly which invariants
are **mechanized** and which are **doctrine enforced by review**, rather than
selling every one as fail-closed.

- I1 (mechanized where it counts). Recalled memory, index results, skills, and
  candidates are advisory inputs. The one hard clause — no learning output is
  consumed by the two validation kernels — is enforced by a Stage 2 import
  test asserting `scripts/mailbox_writer.py` and `scripts/compact_pair_loop.py`
  import no `learning_*` module. Everything else in I1 is a doctrine invariant
  in the Stage 0 contract, enforced by review of any future import into those
  files. Live task state is read from Git/mailbox/status
  (`scripts/codex_protocol_model.py:17`).
- I2 (mechanized by absence). No memory/skill/candidate grants a seat,
  approval, push, merge, spend, or launch. Enforcement is that the fixed
  writer and compact-pair validators consume no candidate authority field
  (`scripts/mailbox_writer.py:165-209`), not a parser-shape assertion — the
  draft's `test_candidate_cannot_carry_authority` was struck as vacuous
  (a text classifier over agent prose is exactly what guard admission forbids,
  `docs/protocol/agents/core.md:179-182`).
- I3 (mechanized at the real boundary). Autonomous learning produces immutable
  candidates only. Canonical writes travel the existing governed path: an
  ordinary git change plus a compact-pair review at the change's risk class.
  Promotion IS the compact pair; there is no second approval object.
- I4 (honest scope correction). Exact-hash, fail-closed disposition is **not**
  available until the separately-governed writer-side promotion lands; until
  then a stale or self-approved `decision` publishes and is caught only if a
  reader runs the parser. The plan states this rather than implying the
  refusals bind at publication. Two concrete fixes to the draft's CAS: the
  target base hash is compared at the disposition event's own commit, never
  against a live worktree (which promotion changes by design, retroactively
  invalidating every accepted candidate); and the writer-side promotion moves
  from "unscheduled" to a named Stage 2b (below), because without it I4 is
  aspirational.
- I5 (correction: the floor lives in operator judgment, not candidate code).
  A `governance-rule` candidate carries a `high-risk-control` review floor —
  but that floor is enforced by the assigned operator's risk-class judgment on
  the promoting verify-request (`AGENTS.md` authority floor), not by candidate
  machinery, because `_finding_refs` is a shape-only regex
  (`scripts/compact_pair_loop.py:250-266`) that does not resolve the ref,
  confirm accepted disposition, or match risk floors. The plan says so.
- I6 (correction: the cited pattern is fail-open). `scripts/archive_handoffs.py`
  silently falls back from `git mv` to `shutil.move` and takes no backup — it
  is not a fail-closed-backup pattern. The archive item is removed from this
  plan entirely (see §5 Stage 6) and filed as standalone maintenance; where it
  eventually lives, backup-failure-blocks and recoverability are **new**
  behavior to build, not an inherited pattern.
- I7 (mechanized as a design filter). Every guard or lint this plan proposes
  passes guard admission — names the effect it blocks, survives the bypass
  question — or is not built (`docs/protocol/agents/core.md:163-191`).
  ADR-066's single explicit non-build (a `check_no_ceremony.py` preventive-hook
  rule, `DECISIONS.md:1396`) is binding; this plan re-proposes it nowhere. The
  draft's "phrase-absence lints are an ADR-066 non-build" was wrong (that lint
  is queued to build, `DECISIONS.md:1392`) and is struck.

## 3. Taxonomy and storage classes

Labels for every recalled item: `fact`, `preference`, `procedure`, `episode`,
`current-task-state`, `governance-rule`. Current-task-state is never stored in
semantic memory (I1); governance-rule is never auto-promoted (I5).

Storage classes mapped to what exists:
- Committed shared knowledge (repository scope): docs/** (DECISIONS.md,
  handoffs, plans, protocol docs), coordination/mailbox/sent/** + kinds.txt,
  logs/** including logs/claims/ledger.jsonl, both skill trees. The `.gitignore`
  partition already annotates durable-committed vs runtime-local paths and is
  the mechanical source for scope labels.
- Private profile memory (user scope): `~/.claude` memory dirs, global
  CLAUDE.md, global skills, session transcripts. Out of repo, deletable; the
  episodic index must not commit it.
- Scoped episodic index (workspace scope): derived, rebuildable, local-only,
  a projection with no authority (alongside the git-common-dir ref-bus,
  presence heartbeats, locks).

## 4. The candidate record (Stage 2 schema)

A learning candidate is one mailbox event of a new kind `learning-candidate`
(a one-line append to `coordination/mailbox/kinds.txt`; the writer and
send-event accept registry kinds with zero code change,
`coordination/bin/send-event:95`, `scripts/mailbox_writer.py:120-122`), typed
at read time by a statement parser following the ownership-record pattern
(`scripts/protocol_mailbox.py:283-369`). Write-time payload validation is
**Stage 2b** below (the seam is the kind dispatch in `validate_event_candidate`,
`scripts/mailbox_writer.py:165-209`), and I4 depends on it.

Body fields (one `Label:` line each, `_single_body_field` discipline):

    Candidate ID: sha256 of the normalized payload (identity / dedup key)
    Category: fact | preference | procedure | episode-summary | governance-rule
    Scope: repository | workspace | user | provider:<name>
    Statement: the lesson or content summary
    Proposed content hash: sha256 of the full proposed artifact, when concrete
    Target: canonical path the candidate would change, when applicable
    Target base hash: sha256 of the target's canonical bytes AT THE DISPOSITION
      EVENT'S COMMIT (never a live worktree — promotion changes those bytes)
    Source refs: immutable `<sent-path>@<40-hex>` or `sha256:<64-hex>`
      (`scripts/protocol_mailbox.py:253-263`)
    Evidence provenance: one of claim_check's PROVENANCE ladder, imported not
      re-declared — MEASURED, RELAYED, REMEMBERED, INFERRED, ASSUMED
      (`scripts/claim_check.py:59`); ASSUMED on a candidate means the producer
      recorded a blank cell, and its disposition may not be `accepted`
    Applicability / Exclusions: required
    Risk class: from the closed set (`scripts/codex_protocol_model.py:33-70`)
    Supersedes: optional `<learning-candidate path>@<commit>` (ADR-066 re-issue
      idiom: never patch in place, name what is replaced)
    Producer seat / Producer model

Dedup is derived from committed `coordination/mailbox/sent/` events at the
pinned commit — Candidate ID is a body field in committed files, a
deterministic scan of the same substrate the parsers read — NOT from the
local index (the draft keyed dedup on the gitignored projection, which gives
checkout-dependent verdicts; struck). Because Candidate ID is a content hash,
a duplicate is byte-idempotent and Supersedes already handles replacement, so
the refusal may simply drop.

Disposition is a `decision` event carrying `Candidate: path@commit` and
`Disposition: accepted | declined | expired`. The director-side authoring
convention is `coordination/README.md:319-322` (the v5 `memory-candidate`
note; the draft cited README:220, which is AGY flag-forwarding prose — fixed).
Refusals, and where each actually binds:

- stale target base hash, self-approval (disposer==producer), changed-content
  replay, unresolvable source ref, governance-rule-below-floor: these bind at
  **Stage 2b** (writer-side), advisory-only before it. The plan does not claim
  otherwise.

## 5. File-level plan by stage

Subtraction first — deliberately NOT built because the mechanism exists: a new
approval path (the compact pair is one); a new supersession lifecycle
(ADR-066 Supersedes + `route_lineage.py` CAS precedents); a new
evidence-strength enum (import claim_check PROVENANCE); a new claim classifier
(import `scripts/claim_check.py`; its exclusive-witness and anchor-table tests
are the paid-for part); a new rotation scheme; a new provider-dispatch
readiness gate (`scripts/harness_preflight.py`, ADR-065); byte-parity-by-default
for skills.

### Stage 0 — Contract and baselines (docs + ADR only)
NEW `docs/protocol/learning/contract.md` (normative copy of §2/§3/§4/§7);
DECISIONS.md ADR (number re-verified in the same change); this plan cited as
provenance. Baselines re-measured at the bound commit and recorded from cited
commands. Also lands here: the one cheap experiment that decides Stage 3
(below) — stub one Claude skill that references its canonical `.agents` file
and confirm the harness discovers and follows it.
Gate: contract merged with review; executable invariant tests land with the
code stages they bind, not as empty ceremony here.

### Stage 1 — Read-only episodic index
NEW `scripts/learning_index.py` (build + FTS5 query), NEW
`tests/unit/test_learning_index.py`, one `.gitignore` line for
`coordination/learning/` (workspace-scope, derived, never committed). Sources:
existing artifacts only — mailbox filenames (`scripts/status.py:56-60`),
verify-request bodies (SHAs/seats/risk), handoffs/plans via
`scripts/latest_handoff.py` extraction, logs/*.json(l) with per-source
timestamp rules; content hash = git blob SHA for tracked files. Every result
row carries source path, scope label (from the `.gitignore` partition),
timestamp, content hash, and the commit the index was built at. Query surface
copies the status.py collector contract: never hangs, every source degrades to
`(unavailable: <reason>)`. No embeddings, no automatic prompt injection.
Session transcripts are out of scope by boundary; the bridge into the repo is
a learning-candidate.
Gate tests: `test_every_result_carries_source_timestamp_scope_hash`;
`test_index_records_built_at_commit`;
`test_absent_index_is_labeled_unavailable_not_empty`
(`scripts/bus_unread.py:19-22` taxonomy); and — moved to the ingest boundary
where it is reachable, per the skeptic — `test_build_refuses_a_user_scope_source_path`.

### Stage 2 — Candidate lifecycle (read-side)
`coordination/mailbox/kinds.txt` +1 line AND retire `memory-candidate` in the
SAME commit (the draft's deprecated-alias limbo contradicted the same-change
stale-claim sweep it cited; struck — one governed change either way). NEW
parsers in `scripts/protocol_mailbox.py`
(`parse_learning_candidate_statement`, `parse_learning_disposition_statement`);
`send-event` sender gate (learning-candidate from pair seats), with the honest
note that this gate is wrapper-side and bypassable until Stage 2b, exactly as
today's non-compact-pair kinds are; README v5 section rewritten with the
same-change doc+docstring sweep. NEW `tests/unit/test_learning_candidate.py`.
Gate tests: the I1 import test (§2); parser round-trips; the dedup-from-
committed-events scan; and the refusal tests marked advisory-until-2b.

### Stage 2b — Writer-side promotion (separate, high-risk-control)
This is what makes I4 real, and it is named rather than left "unscheduled."
Add a `learning-candidate`/`decision` branch to
`scripts/mailbox_writer.py:validate_event_candidate` so the six refusals bind
at publication, base-hash CAS included, evaluated at the disposition commit.
Kernel file → high-risk-control, distinct different-family operator, abuse-class
assessment. Everything before 2b is advisory; the plan says so at every point.
Gate tests (now enforcing, mutation-verified by deleting the call site):
stale-base, self-approval, changed-content, unresolvable-ref,
governance-floor, duplicate-id.

### Stage 3 — Skills: experiment-gated, not a foregone build
The draft unconditionally built a manifest + `scripts/skill_materialize.py` at
high-risk-control on the unverified premise "Claude discovery is
`.claude/skills`-only, so bodies must be mirrored." Discovery-only does not
imply body-mirroring: a discovered `.claude` stub can reference its canonical
`.agents` file, the pattern `.cursor/skills/review-next/SKILL.md:9-11` already
uses. So:
- Stage 0 runs the experiment (stub one skill, run the harness).
- If it succeeds, Stage 3 is **reference stubs** (docs, material-behavior) —
  no manifest transform machinery, no mechanical instruction-surface writer, no
  high-risk-control materializer. The existing prompt-sync corpus keeps pinning
  canonical text; the one byte-parity file stays a hand-reviewed copy as today.
  ADR-066 binds: correct the docs, don't build machinery to match a sentence
  (`core.md:190-191`).
- Only if the experiment FAILS does 3b/3c (manifest + materializer) return, and
  then the manifest's transform-legality references the three concrete
  mechanics actually declared at `docs/protocol/claude/continuation.md:82-86`
  (command prefixing, tool-name substitution, `disable-model-invocation`
  frontmatter) — the draft's "four legal classes" invented two that exist
  nowhere in the repo; struck.
- Independent of the experiment: Stage 3a reconciliation of the **9** drifted
  pairs (not 7) remains, each pair its own material-behavior commit, adjudicated
  by `git log` per pair. Which side's doctrine is intended is O2.

### Stage 4 — Supervised extraction (candidates only)
NEW `scripts/learning_extract.py`, NEW `tests/unit/test_learning_extract.py`.
Triggers are evidence, not counters or a session-update quota (the verified
Hermes sediment machine: bias at `background_review.py:181`, tool-loop counter
at `turn_finalizer.py:634` — both cited): explicit user correction; a reusable
workflow in a handoff; a skill contradicted by evidence; a measured improvement
opportunity; and recurrence detected as an **FTS query over the Stage 1 index**
(the draft's "findings sharing a dedup key" presupposed a keying scheme that
exists nowhere — `grep -rn dedup` finds only unrelated selector code; struck,
replaced by the index the plan already builds). Reuses `claim_check.sweep_range`
and `classify`, not a new keyword list. Capability boundary, executable: writes
exactly one draft candidate body to scratch and prints it; the author runs
send-event. No mailbox-finalize path, no git mutation, no skill-tree write.
Gate tests: `test_extractor_writes_nothing_outside_scratch`,
`test_extractor_output_parses_as_candidate`, `test_no_trigger_no_candidate`
(anti-sediment).

### Stage 5 — Evaluation and promotion
No new promotion machinery (I3): a candidate is promoted by landing its change
as an ordinary commit whose verify-request lists the candidate ref in Finding
Refs, reviewed at the change's risk class. The linkage check is advisory
tooling (a WARN in check_coordination-style reporting), NOT a blocking gate,
because a blocking gate on a shape-only ref would fail guard admission — and
the honest statement is that the governance floor is carried by operator
judgment (I5), not by the ref. NEW `scripts/learning_metrics.py` (read-only
reporter over the index, `logs/claims/ledger.jsonl`, and
`docs/PROTOCOL-RULES-LOG.md` invocation counts), NEW
`logs/learning/outcomes.jsonl`, NEW frozen packs `tests/learning_packs/`
(fixture ranges + expected retrievals + decoy negative controls). Metrics: the
eight from the research, each with its measurement source; the review-friction
baseline is 162/186 (corrected). `learning_metrics.py` also carries the
staleness/contradiction section that the draft had split into a separate
curator (below).

### Stage 6 — dissolved
The skeptics showed Stage 6 held nothing that needed its own stage. The curator
(`learning_curate.py`) was a thin third reporter over two mechanisms Stages 4/5
already build: staleness/contradiction folds into `learning_metrics.py`;
supersession drafts route through Stage 4's skill-contradicted trigger — struck.
The mailbox archive is repository maintenance, not a learning step, rides no
learning dependency, and its cited pattern is fail-open — removed from this plan
and filed as a standalone maintenance change after O3 is ruled, carrying its own
I6 fail-closed-backup obligation. Embeddings remain a Stage-5-gated decision
(O5); any external provider's recall is advisory, never authoritative (the
inverted Hermes default, `agent/memory_manager.py:357`).

## 6. Provider adapter contract
Kernel owns: episode capture, candidate schema and hashes, scope enforcement,
retrieval, dedup, validation fixtures, metrics, promotion binding, supersession.
Adapters own only: discovery/activation (Claude: reference stubs if the Stage 0
experiment passes, else materialized copies; Cursor: command wrapper
referencing canonical paths; Codex/AGY: direct `.agents` reads per
AGENTS.md:10-13), the three real rendering transforms, tool-name translation,
and a per-provider invocation-path proof that fails if the shared kernel is
bypassed. Provider deltas are declared; silent forks are drift.

## 7. Threat model (verified-defect driven)
- Replay-without-preimage (`write_approval.py:120`,
  `skill_manager_tool.py:1354`): Target-base-hash CAS at the disposition commit,
  bound at Stage 2b, mirroring `route_lineage.py` stale-parent and
  `_change_envelope_matches` revision+parent CAS.
- Authoritative recall (`memory_manager.py:357`): I1 labels + scope on every
  result; drift-prone facts rechecked against source before use.
- Sediment (`background_review.py:181`): evidence triggers only;
  `test_no_trigger_no_candidate`; acceptance-rate watched.
- Foreground bypass (Hermes guards bind only the background path,
  `skill_manager_tool.py:310`): canonical writes go through review regardless of
  origin — the guard is at publication, not the author.
- Laundering: reuse claim_check INSTRUMENT_MARK admission on candidate evidence.
- This repo's own vacuity classes (correct-but-uncalled, enumeration-for-
  property, env-of-record): each gate is a named test with a call-site deletion
  mutation in review — and the draft itself exhibited two of these, caught by
  the adversarial pass, which is the argument for keeping it in the process.

## 8. Sequencing and review routing
0 → 1 → 2 → 2b → 3 (experiment-gated) → 4 → 5. Risk: Stage 0 contract
material-behavior (instruction surfaces steer models); Stages 1/4/5 tooling
material-behavior; Stage 2 parser material-behavior; Stage 2b writer
high-risk-control; Stage 3 reconciliation commits material-behavior, the
materializer (only if the experiment fails) high-risk-control. Doctrine-diff
before each range submit; anchor-verify at each session start
(`core.md:25-34`); `harness_preflight` before any provider-dispatched
evaluation.

## 9. Decisions adopted and left open
Adopted: candidates never canonical; `.agents/skills` canonical;
committed-vs-local split; FTS-first; fail-closed exact-hash disposition bound at
Stage 2b; governance rules always independent-review; the dormant Threeway bus
is not required (mailbox carries candidate refs).
Owner ruling 2026-07-31: adopt the plan defaults for every decision that has
one. Recorded per item:
- O1 (Stage 2) — RULED, default adopted: new `learning-candidate` kind, with
  `memory-candidate` retired in the same commit.
- O2 (Stage 3a) — STILL OPEN by construction: no default exists. Adjudication
  is per pair at Stage 3a (git log per pair; where the two trees' doctrine
  genuinely diverges, the owner rules on that pair before its commit lands).
  The blanket "use defaults" ruling deliberately does not cover this.
- O3 (deferred maintenance) — RULED as its default state: the mailbox archive
  change stays out of this plan; retention/cadence are set when that
  standalone change is filed.
- O4 (Stage 4): whether the extractor may ever publish candidates directly.
  RULED, default adopted: drafts only; the author publishes.
- O5 (Stage 5) — RULED as its default state: no embeddings; the threshold
  question is re-opened only when Stage 5 baselines exist to answer it.

## 10. Explicitly rejected (verified reason)
Tool-loop-count triggers and default-on skill updates
(`background_review.py:181`, `turn_finalizer.py:634`); recalled memory as
authoritative (`memory_manager.py:357`); write approvals off by default;
approval-by-replay without base hash (`write_approval.py:120`); best-effort
backup before trusted mutation; usage counts as lifecycle evidence;
cross-profile session scans without scope authority; autonomous bundled-skill
pruning; curator with terminal access; immediate canonical skill edits.
