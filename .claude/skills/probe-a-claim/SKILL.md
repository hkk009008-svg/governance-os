---
name: probe-a-claim
description: Formation-time discipline for load-bearing claims — derive the premises from the claim's shape, cite each with the command that measured it, attack it with a context-free reader, and record the blank cells. Use BEFORE writing "verified", "enforced", "complete", "never", "measured", or citing a reference as provenance; prove-a-control is for the mechanism, this is for the belief.
disable-model-invocation: true
---

# Probe a Claim

## Why this exists
Nine defects in one session (2026-07-26/27) had one mechanism: the author
verified the property they were thinking about, not the property the claim
rested on. "Enforced pre-dispatch" — correct check, nothing called it.
"Measured" — only in the author's checkout. "This ref anchors the report" —
well-formed, resolving to nothing. Every miss was one command from detection,
and a reader holding only the claim caught all nine, because it never made the
assumption. The failure is circularity at belief formation: the claim and its
check both derived from the same artifact, so their agreement carried no
information. The remedy is otherness — from the claim's shape, from a
context-free reader, from an exit code — none of which is sourced from the
author's recall, because recall is the broken faculty.

## The loop, per load-bearing claim

1. **Premises from shape, not memory.**
   ```bash
   env -u GIT_INDEX_FILE .venv/bin/python scripts/claim_check.py premises "<claim>"
   ```
   The grammar (enforced / measured / reference / complete / absence /
   semantics) supplies the terms. You can forget a premise; you cannot forget
   the shape of your own sentence.

2. **Cite each premise with an instrument.** A citation is a command plus its
   real output — `per `git grep -n caller`` — never prose. Tag provenance:
   MEASURED, RELAYED, REMEMBERED, INFERRED. A load-bearing premise resting on
   the last two is a blank cell wearing a label.

3. **Run the one embarrassing command.** Before writing the claim as fact, ask
   "what single command would most embarrass this?" and run it. Every failure
   this skill encodes was one command away.

4. **Probe with an amnesiac.** Cross-family, seconds:
   ```bash
   coordination/bin/probe-claim "<claim>"
   ```
   Same-family fallback: spawn the `amnesiac-prober` agent with ONLY the claim
   sentence. Never include the code, the diff, or your reasoning — context is
   contamination; the probe's value is that the reader has not made your
   assumptions.

5. **Record, so the blank cells exist.**
   ```bash
   echo '{"claim": "...", "premises": [{"key": "...", "status": "MEASURED", "cite": "$ ... → ..."}], "kills_attempted": ["..."]}' \
     | env -u GIT_INDEX_FILE .venv/bin/python scripts/claim_check.py record
   ```
   Unsupplied grammar premises are written ASSUMED by construction. `audit`
   lists them and every claim nothing tried to kill; `lottery` samples recorded
   claims for fresh probes later.

6. **Sweep the range before publishing it.**
   ```bash
   env -u GIT_INDEX_FILE .venv/bin/python scripts/claim_check.py sweep --base <base> --head <head>
   ```
   Flags overclaim vocabulary with no citation marker nearby. Vocabulary only:
   a finding means "a strong word with no instrument in sight", not "false".

## What counts as a kill
An attempt to make the claim fail while believing it true: delete the call
site, restore the defect, run the divergent input, feed the parser the case
your pattern assumes away. Confirmations by the claim's own author agreeing
with the claim's own artifact count zero — same source, no information.

## Division of labour
- `probe-a-claim` — the *belief*: what must be true, who checked, who disagreed.
- `prove-a-control` — the *mechanism*: reversion and evasion controls on guards.
- The compact pair — the *acceptance*: none of the above substitutes for the
  assigned non-author review, and nothing here is a gate.

## Honest limits, so the next session evolves them instead of trusting them
- The grammar covers six shapes derived from nine measured failures; a failure
  of a new shape will not be named until someone adds it. When that happens,
  extend `SHAPES` and add the instance to the fixture in
  `tests/unit/test_claim_check.py` — the fixture is the grammar's tether.
- The sweep is a vocabulary heuristic over prose. That is the honest tool for
  prose, and useless about code semantics — `prove-a-control` trap 3 governs
  there.
- The ledger is self-reported. Its audit catches what you wrote down, not what
  you didn't; the lottery plus probes exist to attack exactly that gap.
- The premise keys were authored by the same mind whose blind spots they
  guard against. The amnesiac probe is the counterweight — it is the one step
  sourced from outside, so skipping it collapses the loop back to one party.
