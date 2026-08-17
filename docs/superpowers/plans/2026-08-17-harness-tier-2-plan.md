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
reconstruction dropped; section 7 records what the round cost. Round-2
questions in section 8 are outstanding, so this document is still not
countersigned.

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

The mechanism for I4: carry an implementation tip and a governance tip
separately, so the range under review stays byte-stable while the record
advances. Prototype on one range before proposing it as protocol.

**Incomplete.** Codex requires this item to name the agreed event binding
fields and to state how admission projects and consumes a separate
governance tip. The director does not hold those field names and will not
invent them; they are requested from Codex and this section is a
placeholder until they arrive. Written down as a gap rather than filled
with a guess.

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

Codex identified these as agreed work the director's reconstruction
dropped entirely. They are recorded with status rather than rebuilt,
because several are partly landed. Status is Codex's characterisation; the
director has not independently verified which parts exist.

| item | status |
|---|---|
| public-path / threat-model formation | partly landed — needs gap analysis |
| one coherent review plus a final cumulative review | proposed |
| direct Git / ledger handoff | proposed |
| current-state projection | partly landed |
| policy consolidation | proposed |
| growth / ceremony work | partly landed (PRs #38, #42) |

Each needs an existing / gap / proposed breakdown before it becomes a work
item. That breakdown is not written yet and is the next thing owed on this
document.

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

I7 is landed. Next: I4 and I5 together, since I5 is I4's mechanism and the
review debt they address is accumulating now — four requests are open at
the tail. Then I6's artifact-boundary half, mostly an extension of the
guard already on `claude/finding-ref-resolvability-guard`. Then I1, which
is now adoption work against `claim_check.py` rather than construction and
is correspondingly cheaper than the draft assumed. Then I2, which changes
how seats work rather than what the repo refuses and most needs a second
opinion first. I3 waits on a user decision and can land at any point. The
section 4 items need their existing/gap/proposed breakdown before they can
be ordered at all.

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

That suggests the Tier 2 list is missing an item, and that the missing
item is not a control: **an inventory of what the harness already
enforces, consulted before anything is proposed.** It is not added to the
numbered list here, because adding it unreviewed would repeat the error
this section describes.

## 8. Open questions for Codex

Round 1 (answered 2026-08-17): reconstruction accuracy, I1 authorship,
I2 axis definition, I6 call-boundary concession. All four answered and
folded into the text above.

Round 2, outstanding:

1. I5: the agreed event binding field names, and how admission projects
   and consumes a separate governance tip. Requested, not guessed.
2. Section 4: which parts of each restored item already exist, so the
   existing/gap/proposed breakdown can be written from fact rather than
   from Codex's one-word status.
3. Section 7: is "an inventory of what the harness already enforces" the
   right response to the four repeated errors, or is that itself another
   artifact proposed where adoption is the actual gap?
