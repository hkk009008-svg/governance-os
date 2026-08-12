# Learning Plane — normative contract

> Routed here from the learning-plane line in `CLAUDE.md` and the placement
> table in `docs/protocol/protocol-assembly-map.md` when learning-plane work
> (index, candidates, extraction, metrics, skill distribution) is named.
> Normative copy of the plan's §2/§3/§4/§7
> (`docs/superpowers/plans/2026-07-30-learning-plane-plan.md`); the plan is
> provenance, this file is the contract. Current code wins when it drifts —
> fix this file in the same change that exposes the drift.

Purpose: the learning lifecycle (observe → extract → candidate → evaluate →
promote → distribute → measure → supersede) on the existing governance spine,
provider-neutral across Claude, Codex, AGY, Cursor. Non-goals, binding on
every stage: no autonomous canonical writes; no embeddings before FTS is
measured insufficient; no new approval machinery where the compact pair
already is one; no "most-sessions-should-update-something" bias — candidates
come from evidence triggers only.

## 1. Authority model — where enforcement binds

Each invariant below is labeled **mechanized** (a named executable check) or
**doctrine** (enforced by review). Selling a doctrine invariant as fail-closed
is itself a contract violation.

- **I1 — learning outputs are advisory inputs.** Recalled memory, index
  results, skills, and candidates never bind a decision. Mechanized core —
  landed with Stage 2 as the named check
  `tests/unit/test_learning_candidate.py::test_kernel_validators_import_no_learning_module`
  — asserting `scripts/mailbox_writer.py` and `scripts/compact_pair_loop.py`
  import no `learning_*` module. Everything else in I1 is doctrine: any
  future import of a learning module into those two files is a contract
  change and reviews as one. Live task state is read from durable shared
  state — Git, mailbox, status — never from the index
  (`scripts/codex_protocol_model.py:17`, CENTRAL_INVARIANT).
- **I2 — no learning artifact grants authority.** Doctrine, held by a
  reviewed absence: the fixed writer and compact-pair validators consume no
  candidate authority field (`scripts/mailbox_writer.py:165-209`), and any
  change that adds one reviews as a contract change. No executable check
  asserts the absence — a text classifier over agent prose is exactly what
  guard admission forbids
  ([`core.md` — Guard admission](../agents/core.md#guard-admission)).
- **I3 — canonical writes travel the governed path.** Doctrine riding an
  existing mechanism: promotion IS the compact pair — an ordinary git change
  whose verify-request lists the candidate ref, reviewed at the change's
  risk class, enforced by the same publication-time validators that govern
  every pair. Autonomous learning produces immutable candidates only; there
  is no second approval object.
- **I4 — fail-closed disposition is mechanized at publication.**
  `scripts/mailbox_writer.py:validate_event_candidate` enforces the refusal
  set through the production finalizer, covered by
  `tests/unit/test_learning_promotion.py`. The
  target-base-hash CAS compares bytes at the disposition event's own commit,
  never a live worktree — promotion changes worktree bytes by design.
- **I5 — the governance floor lives in operator judgment.** Doctrine: a
  `governance-rule` candidate carries a `high-risk-control` review floor,
  enforced by the assigned operator's risk-class judgment on the promoting
  verify-request (`AGENTS.md` Universal contract item 5 — authority and security work needs
  distinct non-author, different-model actual-diff review) — not by
  candidate machinery, because `_finding_refs` is a shape-only regex
  (`scripts/compact_pair_loop.py:250-266`).
- **I6 — trusted mutation needs fail-closed backup.** Doctrine, scoped as a
  non-build constraint: nothing in the learning plane performs archival or
  destructive maintenance. Where such a change is eventually filed
  (standalone, per plan §5 Stage 6), backup failure must block and recovery
  must be explicit. `scripts/archive_handoffs.py` now fails closed when its
  history-preserving `git mv` cannot complete; that narrow behavior is a
  precedent, not a general backup or rollback mechanism.
- **I7 — every proposed guard passes guard admission.** Doctrine applied as
  a design filter at review time: name the effect it blocks, survive the
  bypass question, or do not build it
  ([`core.md` — Guard admission](../agents/core.md#guard-admission)). ADR-066's explicit non-build (a
  `check_no_ceremony.py` preventive-hook rule, `DECISIONS.md:1393-1396`)
  stays not-built.

## 2. Taxonomy and storage classes

Labels for every recalled item: `fact`, `preference`, `procedure`, `episode`,
`current-task-state`, `governance-rule`. `current-task-state` is never stored
in semantic memory (I1); `governance-rule` is never auto-promoted (I5).

Storage classes. The mechanical source for a scope label is tree membership
at the build commit, NOT `.gitignore` — the ignore file cannot serve as the
labeler because `.gitignore:51` (`coordination/mailbox/sent/*`) ignores the
entire mailbox corpus that the fixed writer force-adds past it
(`scripts/mailbox_writer.py` `_stage(root, relative, force=True)`):

- **Committed shared knowledge** (repository scope): any path tracked in the
  committed tree at the build commit — `docs/**`,
  `coordination/mailbox/sent/**` + `kinds.txt`, `logs/**` including
  `logs/claims/ledger.jsonl`, both skill trees.
- **Private profile memory** (user scope): `~/.claude` memory dirs, global
  CLAUDE.md, global skills, session transcripts. Out of repo, deletable; the
  episodic index must not ingest it — absolute paths, `~` expansions, and
  parent escapes are refused at the ingest boundary.
- **Scoped episodic index** (workspace scope): derived, rebuildable,
  local-only, a projection with no authority (alongside the git-common-dir
  ref-bus, presence heartbeats, locks). Never committed; the
  `coordination/learning/` ignore rule lands with Stage 1.

## 3. The candidate record

One mailbox event of kind `learning-candidate` (registry kind:
`coordination/mailbox/kinds.txt`; the writer and `send-event` accept registry
kinds with zero code change, `coordination/bin/send-event:95`,
`scripts/mailbox_writer.py:120-122`), typed at read time by a statement
parser following the ownership-record pattern
(`scripts/protocol_mailbox.py:283-369`). Body fields, one `Label:` line each
(`_single_body_field` discipline):

    Candidate ID: sha256 of the normalized payload (identity / dedup key)
    Category: fact | preference | procedure | episode-summary | governance-rule
    Scope: repository | workspace | user | provider:<name>
    Statement: the lesson or content summary
    Proposed content hash: sha256 of the full proposed artifact, when concrete
    Target: canonical path the candidate would change, when applicable
    Target base hash: sha256 of the target's canonical bytes AT THE
      DISPOSITION EVENT'S COMMIT (never a live worktree)
    Source refs: immutable `<sent-path>@<40-hex>` or `sha256:<64-hex>`
      (`scripts/protocol_mailbox.py:253-263`)
    Evidence provenance: MEASURED | RELAYED | REMEMBERED | INFERRED | ASSUMED
      (claim_check's ladder imported, not re-declared,
      `scripts/claim_check.py:59`); ASSUMED means the producer recorded a
      blank cell, and its disposition may not be `accepted`
    Applicability / Exclusions: required
    Risk class: from the closed set (`scripts/codex_protocol_model.py:33-70`)
    Supersedes: optional `<learning-candidate path>@<commit>` (ADR-066
      re-issue idiom: never patch in place, name what is replaced)
    Producer seat / Producer model (Producer seat must equal the envelope
      sender — no relay allowance exists; a mismatch is refused at parse,
      because a false producer label would pre-defeat the self-approval
      refusal below)

Dedup derives from committed `coordination/mailbox/sent/` events at the
pinned commit — never from the local index, which gives checkout-dependent
verdicts. Candidate ID is a content hash, so a byte-identical republish
carries no new information: the writer refuses it naming the committed
original, and Supersedes is the replacement route.

Disposition is a `decision` event carrying `Candidate: path@commit` and
`Disposition: accepted | declined | expired` (director-side authoring
convention: `coordination/README.md:318-322`). The refusals — stale target
base hash, self-approval (disposer == producer), changed-content replay,
unresolvable source ref, governance-rule-below-floor, duplicate ID — bind at
writer publication (I4).

## 4. Threat model (verified-defect driven)

Sources: the codex-side Hermes 0.19.0 study and this repo's own measured
vacuity classes. The Hermes anchors below are snapshot-relative to the
uncommitted research input and are NOT resolvable from this repository —
they are RELAYED evidence, retained because the survey behind the plan
verified the mechanisms they name; every other citation in this file
resolves in-tree.

- **Replay without preimage** (Hermes `write_approval.py:120`): the
  target-base-hash CAS at the disposition commit, bound by the writer,
  mirroring `route_lineage.py` stale-parent and `_change_envelope_matches`
  revision+parent CAS.
- **Authoritative recall** (Hermes `memory_manager.py:357` labels recalled
  memory authoritative): every index/candidate result carries I1 labels and
  scope; drift-prone facts are rechecked against source before use.
- **Sediment** (Hermes `background_review.py:181` "most sessions produce a
  skill update"; tool-loop counter `turn_finalizer.py:634`): evidence
  triggers only; `test_no_trigger_no_candidate` (lands with Stage 4);
  acceptance rate watched in Stage 5 metrics.
- **Foreground bypass** (Hermes guards bind only the background path,
  `skill_manager_tool.py:310`): canonical writes go through review regardless
  of origin — the guard is at publication, not in the author.
- **Evidence laundering**: candidate evidence cells reuse claim_check's
  INSTRUMENT_MARK admission; prose is not a citation.
- **This repo's vacuity classes** (correct-but-uncalled,
  enumeration-for-property, environment-of-record): every learning-plane gate
  is a named test whose review includes a call-site-deletion mutation; every
  recorded count states the commit it was measured at.

## 5. Continuity checkpoints and skill-use (adjacent, ADR-068)

Checkpoints are not a learning kind. They reuse mailbox kind `findings`
so the writer allowlist does not grow. A body that carries checkpoint
intent (`Checkpoint:` slug plus `Next action:`) is validated at
publication (`scripts/mailbox_writer.py`); ordinary findings prose
without intent still publishes. Drafting is scratch-only
(`scripts/draft_checkpoint.py`, O4). `Lessons:` is required and
`none-considered` always publishes — there is no quota (sediment
threat, contract §4). Resume reads one snapshot plus the newest
campaign checkpoint; recalled state stays advisory (I1).

Skill-use rows in `logs/learning/outcomes.jsonl` (schema:
`docs/protocol/learning/skill-use.md`) are seat wrap judgments.
`scripts/learning_metrics.py` reports them. They never bind accept /
decline / expire / edit / prune. That absence in the two validation
kernels is the same I1 check that already forbids `learning_*` imports;
skill-use counters additionally must not appear in
`mailbox_writer.py`, `compact_pair_loop.py`, `learning_extract.py`,
`learning_index.py`, or `protocol_mailbox.py`
(`tests/unit/test_skill_packs.py::test_usage_counts_are_not_consumed_by_lifecycle_kernels`).

Canonical skill authoring is `.agents/skills/writing-skills/SKILL.md`.
Promotion into a skill path remains I3 (compact pair at the change's
risk class). Evaluation packs live under `tests/skill_packs/` and are
grown, never edited in place.

The mailbox archive stays unexecuted (O3). The standalone proposal is
`docs/protocol/learning/mailbox-archive-proposal.md`; I6 applies when
that change is filed, not before.
