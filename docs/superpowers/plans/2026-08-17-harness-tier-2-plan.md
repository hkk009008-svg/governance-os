# Harness Tier 2 — plan

Status: PLAN. Nothing here is runtime. Tier 1 (`tools/mailbox_ref.py`,
`tools/vacuity.py`, `tools/composes.py`, `tools/instrument.py`) landed
2026-08-16/17 and is runtime but opt-in. This document exists because
Tier 2 was agreed between the Claude director and the Codex operator in
conversation on 2026-08-16 and was never written anywhere: it survived
only in two session contexts, one of which has already been compacted.
That is the failure the durable-state doctrine names, committed by the
people who wrote the doctrine.

Placement: `docs/superpowers/plans/` is not in
`ci_admission_gate.AUTHORITY_SURFACES`. This is ordinary work. Promoting
any item into `docs/protocol/`, `.claude/skills/`, `.agents/skills/`,
`CLAUDE.md`, or `scripts/` is a separate risk-classed Compact Pair
change and is not authorized by this plan.

Provenance: items I1-I5 are the conversational agreement, reconstructed
from the director's session record; I6-I7 were added 2026-08-17 and were
not part of it. **Codex reviewed this reconstruction on 2026-08-17 and
declined to countersign the first draft**, accepting the themes of I1-I5
while requiring the corrections now folded into the text. Each correction
is marked at the point it applies. Section 4 restores agreed work the
reconstruction dropped; section 7 records what the rounds cost.
**Countersigned by Codex on 2026-08-17 after three review rounds**, at the
commit this sentence lands in; see section 8 for what each round changed
and which claims are reproduced here versus supplied by Codex.

## 1. What Tier 1 fixed, and what it did not (measured)

Window 2026-08-14 09:59 to 2026-08-17 09:27, on `main`:

| measure | count |
|---|---|
| commits on main | 134 |
| pull requests merged | 19 |
| review requests issued | 30 |
| verdicts published | 24 |
| FAIL | 12 |
| NITS | 6 |
| GO | 6 |
| requests open at the tail | 4 |

Command, with the pattern calibrated against a known-matching and a
known-non-matching line before use:

```
git log --oneline --since=2026-08-14 main --format='%s' \
  | grep -c '^mail(operator): FAIL'
```

The last row was first written as "requests with no verdict: 6", derived
by subtracting verdicts from requests. That subtraction is arithmetically
correct and semantically wrong, and pairing the two streams
chronologically shows why: requests supersede each other mid-iteration
(`da4a5917` and `6741f5b8` were both replaced by `3afd20c1` before any
ruling), and some verdicts answer no single request (`bb011fd5` follows
`15757a7d` with no request between them). The difference between the two
totals is therefore not a backlog. Four requests are genuinely open, and
they are consecutive at the tail: `b6721b4a`, `a12d7ee5`, `25eb22e0`,
`9bd06f32`.

This correction is itself an instance of I1. The published number came
from a count that could not distinguish "unanswered" from "superseded",
and nothing in the sentence recorded which instrument produced it.

The FAIL rate is 50 percent of published verdicts. Tier 1 gave four
instruments that each refuse a specific wrong reading. It did not change
that rate, because the tools are opt-in and the operator has to remember
them. Measured instance, 2026-08-17: with `tools/instrument.py` on `main`
and its test suite green, the director wrote a liveness check as
`if ps -p "$pid" ... | head -1 | cut -c1-140; then :; else echo DEAD; fi`,
in which the `if` reads the exit status of `cut` and the DEAD branch is
unreachable. The correct reading was recovered from absent output, not
from the guard. The instrument existed and was not used.

Tier 2 is therefore about **boundaries and defaults**, not about more
instruments.

## 2. The agreed items

### I1 — Default enrollment in the claim ledger that already exists

**Corrected 2026-08-17 after Codex review. The first draft of this item
proposed building a "formation card" and a "living claim inventory".
Both already exist and have since 2026-07-27.**

`scripts/claim_check.py` (29,860 bytes) derives premises from a claim's
shape, records structured entries to `logs/claims/ledger.jsonl`
(`DEFAULT_LEDGER`), and exposes `premises`, `probe`, `record`, `audit`,
`sweep`, and `lottery`. It is the tool the portable formation gate names
by absolute path for exactly this purpose.

So there is nothing to build. The item is **adoption**, not construction:

- default enrollment — a load-bearing claim gets a ledger entry without
  the author electing to make one;
- re-execution — recorded premises are re-run rather than trusted, which
  is `audit`'s existing behaviour bound to governed evidence;
- STALE marking — a claim whose premise no longer reproduces is marked,
  not silently retained.

Paid for by: on 2026-08-16 the director's own memory recorded
"the provider accepts a send and never delivers it" as settled fact. It
was false in its causal reading for approximately 24 hours. Nothing
re-checked it, because nothing recorded what it had rested on. Second
instance, same day: the director wrote to Codex that `pipeline-84` is
"a real, live, seven-hour-old session" — `started 7h ago` is registration
age and carries no liveness premise at all. A third, in this document:
the row corrected in the commit above.

Q2, answered by Codex: use the existing hybrid. `claim_check` derives the
premise skeleton; the author supplies commands, outputs, provenance, and
falsification attempts; `audit` re-derives rather than trusting the
record. Tier 2's contribution is binding that to governed evidence and
re-running or marking stale premises — not a parallel artifact.

### I2 — Same-axis escalation rule

When N consecutive findings land on the same axis, stop fixing and change
the boundary.

Paid for by: PR #32's store work took, in order, store-root then
home-state then home-anchor then canonical-chain then ACL then ACL-budget
then ACL-sequence then sentinel-order. Every round fixed the finding and
the next round found the same class one layer out. Separately, the
director committed check-then-use three times in a single file
(`O_NOFOLLOW` plus `fstat` with the descriptor closed before sqlite3
re-resolved the name; the chain proved by name and then reached by name;
the owner lock tested once and released before the read).

This rule was in fact applied during the campaign — by the user, manually,
after more than a day: "more than day spent millions of token spent this
means the harness is wrong and needs fixing asap." It worked. The
proposal is to make it mechanical rather than dependent on a human
noticing.

Q3, answered by Codex, replacing the draft's definition. The draft said
"same file plus same finding category, three times." That keys the axis to
a **filename**, which is an artifact of how code is laid out rather than
of what is being protected. The axis is instead keyed, within one work
item, as:

> claim/property + protected resource or consequential operation +
> abuse class / resource chain

Trigger on the third finding in that lineage, or **earlier when an evasion
moves one layer outward**. On trigger, stop point repair and require an
endpoint/boundary map. This is an explicit escalation trigger with
reviewed classification — not an automatic filename verdict.

### I3 — Standing publication grants

Every verdict publication in this campaign required its own user
authorization: "publish the NITS", "publish the GO", once per range. At
24 published verdicts in three days that is 24 interrupts, each of which
stops the reviewing seat until a human answers.

A standing grant pre-authorizes publication within a declared scope while
keeping the per-action gate on everything with an external effect — merge,
provider launch, paid spend, destructive operations.

Codex's proposal, omitted from the draft and restored here: alongside the
publication grant, a **revocable push grant scoped to branch + session +
remote, with force-push excluded**. Push is the effect this campaign hit
most often and the one whose blast radius is bounded by that scoping;
merge, provider launch, spend, and destructive effects stay separately
gated per action.

**This item is not the director's to implement.** It is a change to the
user's own authority delegation, and an author cannot grant its reviewer's
authority. The plan records the proposal and the measured cost; the grant
itself requires an explicit user decision, and its scope should be written
down where the gate can read it rather than carried in conversation.

### I4 — Governance events written off implementation HEAD

**Corrected 2026-08-17 after Codex review.** The draft asserted that "a
review request commit becomes part of the range it requests review of."
That is false, and checking it takes one command:

```
$ git log --oneline -3 9bd06f32
9bd06f32 mail(director): request review of the bounded run diagnostic
8612af79 feat(relay): leave a bounded record of a run that stop() would erase
b937d94a Merge pull request #44 ...
```

The request is the **later** commit. It sits after the reviewed head and
does not enter the range it requests.

The real problem is **branch advancement and new authority debt**: writing
the request onto the implementation branch advances that branch past the
reviewed head, so the next range inherits commits nobody ruled on. Two
further facts, kept from the draft because they hold:

- ordinary merges **preserve** the SHAs a published report cites; rebase
  and squash **rewrite** them. This is why squash is forbidden here —
  reports cite `reviewed_base` and `reviewed_head` by SHA.
- a verdict published on one side can fail to reach `main` at all.
  Measured: `a12d7ee5 mail(director): request review of the growth
  accounting change` sits on `main` unanswered although Codex ruled on it;
  the FAIL was committed operator-side and never landed. Separately,
  `739f6d51..77d0fe26` is verified as not an ancestor of `main` —
  unlanded and unruled.

### I5 — Dual-tip prototype

The mechanism for I4. **Design supplied by Codex 2026-08-17**, replacing
the director's placeholder. Same repository, one range, two immutable
OIDs:

```
B ... H                 implementation branch remains exactly H
      \
       R -- V           governance-only linear branch, G = V
```

`R` introduces the request, `V` introduces the report. Deterministic
prototype ref `refs/heads/governance/reviews/<H>`. **The implementation
ref never advances beyond H** — which is what removes the branch
advancement and new authority debt named in I4.

New common fields on request and report, and only these:

```
Review schema:       compact-pair-dual-tip/v1
Work item:           <lowercase-slug>
Subject repository:  <stable registry identity, not a machine-local path>
Subject branch:      refs/heads/<branch>
```

`Subject branch` is routing metadata only; no authority decision resolves
the moving ref. Everything else **reuses existing bindings rather than
duplicating them**: exact subject base/head are `Reviewed base` /
`Reviewed head`; actor and role are the fixed envelope plus Author/Reviewer
seat and model, Assigned operator, Risk class; the report's semantic
parent is `Verification request: <path>@<introduction-commit>`; lineage is
`Remediates` and `Supersedes`.

Codex's constraint, recorded because it is the load-bearing part: the
agreed notions "parent event", "authority scope" and "content hash" do
**not** justify three self-declared body fields. Physical lineage is the
single-parent Git chain. Semantic lineage is the existing
request/remediation/supersession refs. The canonical event ID is already
`<event-path>@<introduction-commit>`, and the projection records and
drift-checks the introduction blob OID — that *is* the content hash.
**Authority cannot be manufactured by an event body.** A free-text
"Authority scope" field would appear to prove itself. Once I3 creates a
durable grant, bind `Publication grant: <immutable-event-ref>`; until
then, authority binding is a stated dependency and the external
publication grant remains required.

Admission takes three explicit inputs, `--base B --head H
--governance-head G`, and trusted gate code must:

1. resolve B, H, G once to full OIDs and report both H and G in the outcome;
2. require H ancestor-of G;
3. require every commit in `H..G` to be a one-parent linear successor
   adding exactly one canonical sent event and changing nothing else;
4. project mailbox/history at pinned G **without checkout or execution of G**;
5. load events introduced in `H..G` and validate exact introduction bytes,
   ancestry, and schema/work-item/subject bindings;
6. compute authority commits only from `B..H`;
7. compute report coverage from existing `Reviewed base..Reviewed head`
   and union admitting GO/NITS coverage as today;
8. remain read-only — "consume" means project reports into coverage, never
   advance a cursor or ref.

This is a surgical split of `ci_admission_gate`: `authority_commits(B,H)`
stays, evidence discovery moves from reports added in `B..H` to governance
events in `H..G`, and the coverage union stays. The `pull_request_target`
job explicitly fetches the deterministic governance ref, pins G, and lets
trusted-base code object-read it. **Never execute code from G.**

Publication must become compare-and-swap before promotion: the fixed
writer accepts `expected_governance_tip`, creates the one-event commit,
and does `update-ref <ref> <new> <expected-old>` under the common writer
fence. The current publish-and-stage-then-commit sequence is not atomic
and lets two publishers fork from the same G.

Rollout is two stages: trusted-base parser and gate support through the
current embedded-review path first; a later range exercises external G.
A feature cannot depend on gate code that exists only on the candidate
governance tip.

For the controlled prototype a dedicated linked worktree on the governance
ref is sufficient.

## 3. Added 2026-08-17

### I6 — Automatic Tier 1

User directive, 2026-08-17: "propose change for harness with the auto
tier 1 you found and work with codex to make that land."

The four tools must fire without being remembered. They divide into two
groups, and the distinction matters because one group is achievable and
the other is not, in the form it is usually stated:

- **Artifact-boundary, achievable.** `mailbox_ref` already has a
  writer-side guard (branch `claude/finding-ref-resolvability-guard`
  refuses composing a finding ref that resolves to nothing); extend it so
  no unresolvable reference can be committed. `vacuity` becomes a
  requirement on the control-adding path: a change that adds a test
  covering an authority surface carries a vacuity receipt. `composes`
  becomes a requirement on any claim of ancestry or mergeability in a
  published report.
- **Call-boundary, not achievable as stated.** `instrument.measured()`
  cannot intercept a seat's shell calls; a seat runs Bash directly and no
  wrapper sits in that path. Automating it therefore has to happen at the
  **evidence** boundary, not the call boundary. This is weaker than the
  usual framing of the item and is stated as a concession rather than
  promised as interception.

Q4, answered by Codex: the concession is correct, and the draft's proposed
rule was wrong in a way that would have shipped. The draft said "refuse a
citation whose output is empty." **Do not blanket-refuse empty stdout** —
`git diff --check` and `git cat-file -e` succeed empty *by contract*, and
a blanket rule would reject valid evidence.

The receipt is typed instead, enforced at the **fixed-writer and CI**
boundaries, and carries:

| field | |
|---|---|
| command | what was run |
| exit code | expected and actual |
| stdout/stderr | state, not merely presence |
| semantic outcome | what the reading means |
| calibration | the known value the instrument reproduced |

Intentional emptiness is allowed where the command's contract says so.
CI must **also scan committed events**, because direct Git bypasses the
writer entirely.

Note the shape of this correction: `tools/instrument.py` already carries
`allow_empty` for exactly this case. The draft's prose would have
regressed a distinction the tool already makes — the same error as I1,
where the plan proposed rebuilding runtime that exists. Both are adoption
failures wearing the costume of feature proposals.

### I7 — Sender-bound reply addressing — **LANDED**

Committed by Codex as `a9c53c4658757ac8c3fc5ec6469e0facdf07767e`, merged
to `main` as PR #49 (`f547656e`) on 2026-08-17. Replies bind to the
provider-attested sender address carried on an inbound event, not to a
display name resolved from a listing.

Evidence: a two-leg echo across two processes. Leg 1 delivered to
`pipeline-d7 [33d8cd]` by display name (`msg_id ce7d5504`); leg 2
delivered to `uds:/tmp/cc-socks/14717.sock` by attested address
(`msg_id 35893c9c`); both arrived, both with `resolved_target` recording
what was actually used. Reviewer-verified before merge: `verifiedPeerPid`
confirmed a real provider field against production data, growth net 96
from `6f21b40a`, `tests/unit` 1701 passed.

Paid for by: for a full day, Codex's messages to `pipeline-84 [844aad]`
returned `success=true` with real `msg_id` values and never arrived.
`pipeline-84` is PID 44924 — a fork of the receiving session itself
(`--resume` of the same session id, `--fork-session`, `--tools` empty,
`--setting-sources=` empty, `--no-session-persistence`). With no setting
sources it cannot load `crossSessionInbound: "accept"`, which exists only
in `~/.claude/settings.json`. `ListAgents` excludes self, so the only
`pipeline-*` row visible to the receiving session was its own fork under a
confusable name.

Consequence for doctrine, to be handled with the fix, not before it: the
global instruction "Resolve the full current bracketed ref for every send"
is the guess-the-display-name path that produced this. It requires
amendment once the sender-bound route is runtime. Amending
`~/.claude/CLAUDE.md` is outside this repo; amending `CLAUDE.md` here is an
authority surface and needs its own reviewed change.

**Corrected 2026-08-17.** The draft said an unreceivable target is silent
and there was "nothing to report." Measured, that is wrong:

```
connect /tmp/cc-socks/99646.sock  ->  errno 61 ECONNREFUSED   (dead listener)
connect /tmp/cc-socks/14717.sock  ->  CONNECTED               (calibration)
```

A **dead or absent socket refuses visibly** — `ECONNREFUSED` or `ENOENT`,
both surfaced by `_native_refusal`. The silent residual is narrower: **live
PID recycling at a reused socket path**, where `connect` succeeds and the
message reaches the wrong session. `st_ino` captured at inbound and
compared at reply closes it. Successor range.

The draft's error came from judging deliverability by `lstat` metadata —
owner, mode, file type — and never attempting the operation that decides
it.

An echo-token requirement with a bounded no-ACK outcome remains the
minimum honest delivery instrument, and remains unbuilt.

## 4. Restored from the 2026-08-16 agreement

Agreed work the director's reconstruction dropped entirely. Breakdown
supplied by Codex 2026-08-17. Every item is **extend what exists**, never
build a parallel artifact — see section 7 for why that phrasing is load
bearing.

### 4.1 Public-path / threat-model formation

- **Existing.** `claim_check` derives public-path, only-route,
  real-argument, deletion-mutation, property and evasion premises.
  High-risk requests already require abuse classes. `prove-a-control`
  already requires a production path plus reversion and evasion.
- **Gap.** These are opt-in, or arrive at review time. `VerifyRequest` has
  no structured public entry point, principals, non-claims, resource
  boundary, or failing public-surface scenario.
- **Proposed.** Extend the existing claim ledger. For security, authority
  or external-effect work, require one **pre-implementation** claim entry
  naming public entry point, property/resource, principals, non-claims,
  abuse classes and a failing public-path scenario; re-audit at closure.
  No second formation card.

### 4.2 One coherent review plus a final cumulative review

- **Existing.** `AGENTS.md` already prescribes focused iteration then one
  final review with full verification. Compact Pair binds exact ranges
  plus remediation and supersession. Admission requires every authority
  commit covered.
- **Gap.** Admission unions any number of admitting report ranges, so
  fragmented round reviews can admit without one composed-range judgment.
- **Proposed.** Keep interim findings, but run one implementation review,
  one batched remediation range, then require a final GO/NITS from PR base
  through final implementation head whenever remediation lineage exists.
  Admission requires that cumulative report **in addition to** union
  coverage.

### 4.3 Direct Git / ledger handoff

- **Existing.** The fixed mailbox and Git projection are durable. `status`
  discovers pending requests. Requests bind repository and base/head.
- **Gap.** No end-to-end operation discovers a request, fetches and checks
  out the subject, assigns a unique worktree, and prepares fixed-writer
  publication. `status` omits reviewed repository/base/head from its
  current-request projection. Connector failure still turns the user into
  a relay — which happened repeatedly on 2026-08-17.
- **Proposed.** One deterministic `next-review` path over the existing
  mailbox: discover, validate and fetch subject, allocate an owned
  worktree, prepare fixed-writer publication. Add only the missing fetch
  and binding fields. Target: **zero user-mediated text relay** for
  committed requests and reports.

### 4.4 Current-state projection

- **Existing.** The `status` snapshot pins Git and mailbox identity and
  exposes unread, pending request, active FAIL, checkpoint, coordination
  gate, blocker and next action in a bounded view.
- **Gap.** No reviewed repository/base/head, no governance tip, no
  verdict/remediation lineage, no merge or composition state, no admission
  covered/uncovered projection. Its gate is coordination state, not
  `ci_admission_gate`.
- **Proposed.** Extend the existing snapshot JSON with those fields. Keep
  the human view bounded, history queryable. **No mutable state file.**

### 4.5 Policy consolidation

- **Existing.** `protocol-assembly-map` names owning seams and says link
  rather than copy. Core says executable seams outrank prose. `549f47f4`
  removed duplicated and retired doctrine.
- **Gap.** Some universal rules are still restated in adapters, intentional
  provider deltas have no general drift classification, and runtime
  docstrings carry successor PR/SHA pointers.
- **Proposed.** Use the existing assembly map. Delete universal
  restatements, replace runtime PR/SHA pointers with stable
  contract/work-item IDs, mechanically sync only true stubs and
  byte-identical artifacts, retain provider adapters as explicit deltas.

### 4.6 Growth / ceremony

- **Existing.** The gate enforces total net 100, existing-file net 80,
  per-file additions 250, the introduced-file exemption, rename-aware
  `-M5%`, and untracked counting. CI supplies the PR base. `549f47f4`
  demonstrates subtraction.
- **Gap.** An aggregate line count still acts as a hard design verdict;
  reviewer-required controls compete with product code for the same
  budget; there is no narrow reviewed-exception path and no advisory
  conceptual, public-surface or policy-branch measure.
- **Proposed.** Retain hard failure for contamination, rename escapes,
  untracked growth and per-file bloat. Make the aggregate 100 a **design
  trigger** requiring rationale plus a narrow reviewed exception. Add
  advisory conceptual/public-surface/policy-branch reporting. Do not
  recreate a `tests/` ledger unless that separation is enforceable — it
  was not, which is why PR #42 collapsed it back into one.

## 5. Constraints

- **C1.** No new ceremonial layers. `549f47f4` removed some; do not
  re-add them. Prefer deleting mechanism to adding it.
- **C2.** The growth gate binds, and the draft stated it wrong.
  **Corrected**: the 80-line net per-file cap applies to **existing**
  files; **introduced files are exempt** — `scripts/check_no_ceremony.py`
  line 271 `_introduced_python(base)`, consumed at line 346 unioned with
  `_untracked_python_paths()`. The 100 net total and the 250 per-file
  additions cap remain, measured from the PR base, counting untracked
  files.

  The director wrote that exemption in PR #42 and then restated the
  constraint without it, which is a third instance of the I1 pattern.

  Anchor every count to an explicit head and show the command:
  ```
  NO_CEREMONY_BASE=<sha> coordination/bin/pipeline-python \
    scripts/check_no_ceremony.py
  ```
  Each item lands as its own merged PR sized to that budget. The gate
  blocked reviewer-required work repeatedly during Tier 1, including
  blocking its own repair twice; do not plan a change that cannot fit.
- **C3.** I3, and the doctrine amendment inside I7, need explicit user
  authority. They are proposals here, not decisions.
- **C4.** This plan is not an authority surface and confers nothing.

## 6. Sequencing

I7 is landed. What follows is a **dependency order**, not a priority list —
supplied by Codex 2026-08-17, replacing a draft ordering that contradicted
I5's own two-stage rollout.

- **Effective immediately, for every Tier 2 proposal**: perform and cite
  the existing-owner lookup from section 7. This is adoption, not a new
  implementation item, and it has no place in the numbered list.
- **I5 stage A** — land trusted-base parser and gate support through the
  current embedded-review path.
- **I5 stage B** — exercise one controlled dual-tip range; promote only
  after compare-and-swap publication exists. **I4 is the problem statement
  this mechanism answers, not a separate code range.**
- **I6** — artifact-boundary automation.
- **I1** — default claim-ledger enrollment.
- **I2** — same-axis escalation.
- **Section 4 follow-ons** — order only after their bounded designs are
  sized.

I3 remains a user decision and may happen at any time. But the durable
`Publication grant` binding is a **dependency for promoting I5 beyond the
externally granted prototype**. Provider, spend, merge and destructive
authority stay separate throughout.

## 7. What this revision cost, and what it says

Codex declined to countersign the first draft. It was right to. Four of
the corrections above were errors of the same kind:

- **I1** proposed building a formation card and claim inventory that have
  existed since 2026-07-27 as `scripts/claim_check.py` — the tool the
  portable formation gate names by absolute path.
- **I6** proposed refusing evidence with empty output, which
  `tools/instrument.py` already handles correctly via `allow_empty`, and
  which would have rejected `git diff --check` and `cat-file -e`.
- **C2** restated a growth constraint without the introduction exemption
  the director had written into that same gate in PR #42.
- **I4** asserted a mechanism (request commits entering their own range)
  that one `git log` refutes.

Three of the four are proposals to build or restate something the repo
already had. The document argues that we forget what we already have, and
demonstrated it four times in its own first draft.

The director proposed the obvious response — an inventory of what the
harness already enforces — and deliberately withheld it from the numbered
list pending review. **Codex rejected it, and was right.** It is the same
error a level up.

The sources already exist, at different scopes:

| source | scope |
|---|---|
| `governance_verify_all.CHECKER_REGISTRY` | which checker owns which boundary |
| `ci_admission_gate.AUTHORITY_SURFACES` | which paths need a verdict |
| `ARCHITECTURE.md` | factual topology |
| `docs/protocol/protocol-assembly-map.md` | owning seams; link, do not copy |
| provider and skill maps, with tests | adapter deltas |
| `docs/REPOSITORY-MANUAL.md` | descriptive map, 58 KB |

And the manual forecloses the proposal in its own text:

```
docs/REPOSITORY-MANUAL.md:760  For a file-by-file inventory at any later
                               commit, use `git ls-files`, not this
docs/REPOSITORY-MANUAL.md:762  not promote a descriptive table into an
                               independent policy layer.
```

So the document the director would have duplicated contains a sentence
forbidding the duplication. That is the fifth instance of the pattern in
one document, and the most pointed.

**The missing behaviour is discovery, not an artifact.** Before proposing
mechanism: consult `REPOSITORY-MANUAL` or `ARCHITECTURE` to locate the
owner, then the relevant executable registry or surface map, then inspect
the current definition, its callers, its tests, and Git history — and
**cite that lookup in the proposal**. A proposal without the lookup is
incomplete on its face.

If repeated misses later justify automation, add one **read-only derived
view over the existing constants** — probably an option on
`governance_verify_all` — never a stored union that can drift.

## 8. Open questions for Codex

**Round 1**, answered 2026-08-17: reconstruction accuracy, I1 authorship,
I2 axis definition, I6 call-boundary concession. Folded in above.

**Round 2**, answered 2026-08-17: I5's dual-tip design and admission
contract, section 4's existing/gap/proposed breakdown, and section 7's
rejection of a maintained inventory. Folded in above. Codex stated that
with these folded accurately it has no remaining substantive objection to
the reconstruction.

**Round 3**, 2026-08-17: Codex inspected `e744d9d8` and its full diff from
`a96d27d9`, confirmed the round-two substance was folded accurately, and
raised two wording/sequencing nits — the section 6 dependency order above,
and the provenance sentence below. With those folded, **Codex
countersigned the reconstruction and plan direction.**

**Provenance of the section 4 Existing claims.** Two were independently
reproduced here — `governance_verify_all.py:65 CHECKER_REGISTRY` and
`REPOSITORY-MANUAL.md:760-762` — because section 7's discipline demands a
cited lookup. The remainder were **supplied by Codex after source
inspection, and not independently reproduced by the director.** The seams
Codex reports checking are `claim_check` and Compact Pair formation,
`AGENTS` final-review doctrine, admission's coverage union, `status`'s
committed projection, `protocol-assembly-map`, and the current
no-ceremony accounting.

The earlier phrasing — "recorded on Codex's authority" — was wrong and is
corrected at Codex's own insistence. **Authority does not make a factual
claim true.** A reviewer here is an evidence source, not a truth grantor,
and describing an unreproduced fact as resting on someone's authority
laundered a citation into a permission. That distinction is the same one
I5 enforces when it refuses a self-declared "Authority scope" body field.

**Outstanding.** Nothing from Codex. No PR opens for this countersign
round, by Codex's explicit request.
