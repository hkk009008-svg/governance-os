---
name: probe-a-claim
description: Formation-time discipline for load-bearing claims — derive the premises from the claim's shape, cite each with the command that measured it, attack only the claim sentence with a native reduced-context desktop subagent, and record the blank cells. Use BEFORE writing "verified", "enforced", "complete", "never", "measured", or citing a reference as provenance; prove-a-control is for the mechanism, this is for the belief.
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
reduced-context reader, from an exit code — none of which is sourced from the
author's recall, because recall is the broken faculty.

## The loop, per load-bearing claim

1. **Premises from shape, not memory.**
   ```bash
   bin/pipeline claim premises "<claim>"
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

4. **Probe with a native amnesiac subagent.** Build the local prompt:
   ```bash
   bin/pipeline probe "<claim>"
   ```
   This command prints premises and a prompt; it never starts a model or sends
   a team message. Give only that prompt to the current desktop app's native
   `amnesiac-prober` subagent. The read is same-family and reduced-context by
   instruction, not by a process boundary, so label it weaker than independent
   review. Never include the code, diff, repository path, or your reasoning —
   context is contamination. If the app cannot create a native subagent, record
   that blank rather than substituting a terminal provider command.

5. **Record, so the blank cells exist.**
   ```bash
   bin/pipeline claim record \
     --claim "..." \
     --premise invoked-on-path MEASURED '$ grep -n caller → main:12' \
     --kill "deleted the call site; test failed"
   ```
   (JSON on stdin still works; the flag form exists because stdin-JSON was
   clunky enough to skip under pressure, and pressure is when it matters.)
   `record` refuses duplicate keys, unknown keys, strong statuses with empty
   citations, and blank kills — the laundering shapes an audit once believed.
   Unsupplied grammar premises are written ASSUMED by construction. `audit`
   lists them and every claim nothing tried to kill; `lottery` samples recorded
   claims for fresh probes later.

6. **Sweep the range — an optional lens, not a publication step.**
   ```bash
   bin/pipeline claim sweep --base <base> --head <head>
   ```
   Flags overclaim vocabulary with no citation on the same line. Scoped to
   where claims live — prose files whole-line, code and extensionless files on
   comment lines, data files never — because its first run returned 73 flags
   of mention-not-use noise from code literals. Vocabulary only: a finding
   means "a strong word with no instrument in sight", not "false".

## What counts as a kill
An attempt to make the claim fail while believing it true: delete the call
site, restore the defect, run the divergent input, feed the parser the case
your pattern assumes away. Confirmations by the claim's own author agreeing
with the claim's own artifact count zero — same source, no information.

## A hedge you wrote is an unrecorded ASSUMED row

"Judge whether this is circular", written in the author's own review brief,
shipped beside the circular assertion it doubted; the finding came back MAJOR
one round later. A doubt you can write down is a premise you already know is
unverified — writing it is the timestamp, not the discharge. Before submitting
anything, sweep your own outgoing text (brief, outcome, commit message) for
hedge vocabulary — "possibly", "may be", "I suspect", "judge whether", "should
probably" — and give each the treatment any premise gets: resolve it with an
instrument, or record it as ASSUMED so the blank cell is visible instead of
shipped.

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
- The sweep is a vocabulary heuristic over prose, scoped to comment and
  document lines; docstring prose inside code is missed here, and code
  semantics are `prove-a-control` trap 3's business.
- The native subagent is reduced-context by instruction, not isolated by a
  process boundary. It remains same-family and may share model blind spots.
  A different-family formal review, when risk requires one, is a separate
  desktop-team responsibility over the exact committed range.
- The ledger is self-reported. Its audit catches what you wrote down, not what
  you didn't; the lottery plus probes exist to attack exactly that gap.
- The premise keys were authored by the same mind whose blind spots they
  guard against. A native amnesiac subagent adds another context window, not
  another model family; skipping it collapses the loop back to one context.

## Desktop migration evidence (2026-08-27)

The frozen three-case discovery pack is
`tests/skill_packs/pack-004-desktop-claim-probe.json`; focused tests cover the
local prompt-only command and reject the retired execution flag. No live
cross-family probe was run for this revision because the desktop-exclusive
harness has no terminal provider-launch lane. Residual risk: same-family
instruction isolation may miss a shared model blind spot, so it cannot replace
risk-required independent review.

## Rule maintenance
Observed failure: nine 2026-07-26/27 defects where the author verified the
property they were thinking about, not the property the claim rested on.
Mode/risk: claim formation in every mode. Cost: premises command, one
embarrassing command, and an optional native same-family subagent read.
Owner: the claim's author. Re-evaluate: if a load-bearing claim lands with
blank cells and no recorded kill.
