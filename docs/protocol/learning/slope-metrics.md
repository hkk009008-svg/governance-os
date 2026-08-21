# Quality-slope metrics — advisory lens contract

> Instrument: `pipeline/slope_metrics.py`. Tests:
> `tests/unit/test_slope_metrics.py`. Routed from learning-plane work
> (ADR-067): slope reports are an evidence-trigger source for
> `learning-candidate` events. Advisory under contract I1/I2 — output binds
> no decision and grants no authority; the exit code is always 0.

## Failure this instrument addresses

Scaffolding decisions — adding a rule, keeping a gate, retiring ceremony —
were made from memory and anecdote because nothing measured how execution
health moves over time. The work-modes rule-maintenance clause
(`docs/protocol/work-modes.md`) requires each rule to name its observed
failure, cost, and re-evaluation signal; this instrument supplies the
measured signal side of that clause: slopes of review outcomes, rework,
overclaim vocabulary, deferred-defect pins, and intended-vs-landed
divergence, computed from durable state only.

## What it measures, from where

One resolved commit; committed bytes only (mailbox events, Git history,
committed logs); never a live worktree. Events bucket by filename UTC
timestamp; window boundaries count back from the measured commit's committer
time. Each output line names its measurement source. Full metric-by-metric
sources are in the module docstring; the load-bearing ones:

- **Verdict mix and first-pass GO rate** — light field scan of committed
  verification reports; first-pass means the earliest report a request
  received is GO.
- **FAIL chains** — each FAIL joined to its *recorded* closure
  (`Supersedes:`, same-request re-report, or `Remediates failed report:`),
  with `head_changed` separating rework that changed the reviewed range from
  same-head re-review. `no_recorded_closure` means no scanned field joins the
  FAIL to a follow-up — pre-schema chains that continued under a fresh
  request path land there by design, so the counter is only meaningful as a
  slope under the current schema.
- **Reviewed-head landing** — whether each request's head is reachable from
  the measured commit; unresolvable heads are reported, never coerced.
- **Overclaim flags** — `claim_check.sweep_range` between consecutive window
  boundary commits; vocabulary pointers, not judgments.
- **Open regression pins** — anchored strict-xfail decorators under `tests/`
  at each boundary commit.
- **Claims-ledger provenance mix** — premise statuses per window; an ASSUMED
  premise is a recorded blank cell, not a failure.
- **Continuity coverage** — committed checkpoint records (findings events
  carrying the canonical `Checkpoint:`/`Next action:` shape,
  `protocol_mailbox.checkpoint_intent`) per window, with boundary kinds and
  the Lessons answer split (refs vs `none-considered`). Coverage, not
  quality: it shows whether long-horizon boundaries left a durable
  continuation record.
- **Learning throughput** — learning-candidate events and
  `Candidate:`/`Disposition:` decisions per window, with median
  candidate-to-disposition latency. A window of zeros is a valid state,
  not a deficit (anti-sediment); the slope is for noticing when the plane
  stops being used at all while execution-health signals degrade.

## What it deliberately does not measure

The report carries a `not_measurable` block naming requirement retention
over steps, recovery *quality* after context compaction, and hook-approval
intervention precision, each with the reason. Checkpoint records made
compaction-boundary *coverage* measurable (continuity series above);
recovery quality stays unmeasured because no durable artifact ties a
resumed session to the checkpoint it resumed from, and mandating a resume
receipt would be ceremony (I7 guard admission). Absence is reported, never
silently approximated. Creating durable state for the remaining dimensions
is future work that must pass guard admission on its own; this instrument
must not grow a write path to manufacture its own inputs.

## Interpretation discipline

- These are slopes, not gates. No threshold in this report authorizes or
  blocks anything; wiring any number here into a blocking check is a
  contract change and reviews as one (I7 guard admission).
- A FAIL closed with a changed head is the strongest available signal that a
  review intervention prevented a landed defect. A FAIL closed at the same
  head is re-review that changed nothing. A high first-pass GO rate is
  ambiguous on its own: healthy execution and vacuous review look identical
  in this metric, so pair it with the overclaim and pin slopes before
  drawing a conclusion.
- Severity is not modeled. A control that fires rarely can still carry its
  cost many times over on one prevented irreversible effect; precision and
  cost counts from this report must not vote on irreversible-effect gates
  (push, merge, spend, live-data mutation).

## Route into the learning plane

A session proposing to add or retire ceremony cites the slope report in a
`learning-candidate`: `Evidence provenance: MEASURED`, with the producing
command (for example `python pipeline/slope_metrics.py --windows 6
--window-days 14 --json` at the named commit) in the evidence cell.
Promotion of any resulting rule change stays a separately reviewed compact
pair (contract I3); the report is evidence for that decision, not authority
to make it.

## Rule maintenance (work-modes clause applied to this instrument)

1. Observed failure prevented: ceremony add/retire decisions made without a
   measured trend (2026-08-09 audit of the intervention-on-risk proposal).
2. Mode and risk: advisory in every mode; the instrument is ordinary local
   tooling whose output binds nothing.
3. Operating cost: one read-only command; ~1 s at 204 requests / 180 reports
   / 885 committed events (measured 2026-08-09 at `c9ccb30b8624`).
4. Owner: learning plane (ADR-067).
5. Re-evaluation: after the first learning-candidates citing slope evidence
   are disposed, or if two consecutive review cycles find the report unused,
   keep, adjust, or retire it per the rule-maintenance clause.
