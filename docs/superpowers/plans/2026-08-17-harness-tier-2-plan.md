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

Provenance: items 1-5 are the conversational agreement, reconstructed
from the director's session record. The agreement itself is not derivable
from repo bytes and Codex has not countersigned this reconstruction.
Items 6-7 were added 2026-08-17 and were not part of it. Treat item
wording as the director's, pending Codex review.

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

### I1 — Formation card and living claim inventory

The formation gate requires deriving a load-bearing claim's premises from
the claim's own shape before writing it as fact. It is followed
inconsistently because it produces no artifact: a claim that passed the
gate and a claim that skipped it are byte-identical afterward.

A **formation card** is a small structured record per load-bearing claim:
the claim sentence, the premises its shape demands, the command run for
each premise, and that command's real output. A **living claim
inventory** is those cards kept and re-checkable, so a claim can be
re-derived later and marked STALE when a premise has moved.

Paid for by: on 2026-08-16 the director's own memory recorded
"the provider accepts a send and never delivers it" as settled fact. It
was false in its causal reading for approximately 24 hours. Nothing
re-checked it, because nothing recorded what it had rested on. Second
instance, same day: the director wrote to Codex that `pipeline-84` is
"a real, live, seven-hour-old session" — `started 7h ago` is registration
age and carries no liveness premise at all.

Open question for Codex: whether the card is written by the author or
produced by a tool from the claim sentence. Author-written cards are
subject to the same forgetting they are meant to correct.

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
noticing. The hard part is defining "same axis" so the rule can fire
without a judgment call; an unsatisfying but honest first version is
"same file plus same finding category, three times."

### I3 — Standing publication grants

Every verdict publication in this campaign required its own user
authorization: "publish the NITS", "publish the GO", once per range. At
24 published verdicts in three days that is 24 interrupts, each of which
stops the reviewing seat until a human answers.

A standing grant pre-authorizes publication within a declared scope while
keeping the per-action gate on everything with an external effect — push,
merge, provider launch, paid spend.

**This item is not the director's to implement.** It is a change to the
user's own authority delegation, and an author cannot grant its reviewer's
authority. The plan records the proposal and the measured cost; the grant
itself requires an explicit user decision, and its scope should be written
down where the gate can read it rather than carried in conversation.

### I4 — Governance events written off implementation HEAD

Mail events are committed onto the implementation branch. Three
consequences, all observed:

- a review request commit becomes part of the range it requests review of;
- rebases and merges move the SHAs that published reports cite, and
  reports cite `reviewed_base` and `reviewed_head` by SHA, which is why
  squash merges are forbidden in this repo;
- a verdict published on one side can fail to reach `main` at all.

Measured: `a12d7ee5 mail(director): request review of the growth
accounting change` sits on `main` with no answer, although Codex did rule
on it — the FAIL was committed on the operator side and never landed.
Separately, `739f6d51..77d0fe26` (a FAIL and its documentation repair) is
verified as not an ancestor of `main`: unlanded and unruled.

### I5 — Dual-tip prototype

The mechanism for I4: carry an implementation tip and a governance tip
separately, so the range under review stays byte-stable while the record
advances. Prototype first, on one range, before proposing it as protocol.

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
  **evidence** boundary, not the call boundary: refuse evidence prose that
  cites a command without its output, and refuse a citation whose output
  is empty. This is weaker than the usual framing of the item and should
  be stated as such rather than promised as interception.

### I7 — Sender-bound reply addressing

Depends on the Codex fix in flight 2026-08-17. Replies bind to the
provider-attested sender address carried on an inbound event, not to a
display name resolved from a listing.

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

Open, and not closed by the routing fix: binding to the attested sender
fixes addressing but not unreceivable targets. A reply to an attested
sender that cannot receive is silent in exactly the same way. The
transport reports no delivery signal, which is why `_native_refusal`
(PR #44) correctly reported nothing all day — there was nothing to
report. An echo-token requirement with a bounded no-ACK outcome is the
minimum honest instrument.

## 4. Constraints

- **C1.** No new ceremonial layers. `549f47f4` removed some; do not
  re-add them. Prefer deleting mechanism to adding it.
- **C2.** The growth gate binds: 100 net Python lines total, 80 per file,
  250 additions per file, measured from the PR base, counting untracked
  files. Each item lands as its own merged PR sized to that budget. The
  gate blocked reviewer-required work repeatedly during Tier 1, including
  blocking its own repair twice; do not plan a change that cannot fit.
- **C3.** I3, and the doctrine amendment inside I7, need explicit user
  authority. They are proposals here, not decisions.
- **C4.** This plan is not an authority surface and confers nothing.

## 5. Sequencing

I7 first — it is already in flight and it unblocks the relay that every
other item's review depends on. Then I4 and I5 together, since I5 is I4's
mechanism and the review debt they address is accumulating now. Then I6's
artifact-boundary half, which is mostly extension of a guard that already
exists on a branch. Then I1 and I2, which are the ones that change how the
seats work rather than what the repo refuses, and are therefore the ones
most likely to need a second opinion before any of it is built. I3 waits
on a user decision and can land at any point.

## 6. Open questions for Codex

1. Does this reconstruction match what was agreed on 2026-08-16, and what
   is missing from it?
2. I1: author-written card, or tool-derived from the claim sentence?
3. I2: is "same file plus same finding category, three times" a workable
   definition of one axis, or does it fire on unrelated work?
4. I6: is the call-boundary concession correct, or is there an
   interception point the director has not found?
