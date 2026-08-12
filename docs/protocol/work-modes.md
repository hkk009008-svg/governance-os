# Work modes

Pipeline separates the phase of product work from its review risk. The closed
profiles live in `scripts/codex_protocol_model.py` under `work_profile_for`;
this document explains how to apply them.

Work mode is separate from review risk:

- mode controls iteration, record granularity, and the candidate boundary;
- risk controls review depth, reviewer independence, and external authority.

Neither a mode name nor a profile grants a write, seat, provider launch,
canonical mutation, publication, merge, push, spend, or other external effect.

## Ordinary work carries no mode

Ordinary, reversible, repository-local work is not a work mode and declares
nothing: no campaign brief, no mode object, no per-task selection ceremony.
A mode object exists only at its boundary — a long-running exploratory
campaign begins an Explore record, freezing one candidate for acceptance
begins Validate, and moving a reviewed candidate into canonical or live state
begins Promote.

## Choose the smallest useful mode when a boundary applies

| Mode | Use it for | Proportionate record | Review boundary |
|---|---|---|---|
| `explore` | Cheap, reversible learning in a declared sandbox | One campaign brief plus automatic attempt logs | No formal review inside Explore; review begins only on transfer or phase change |
| `validate` | A frozen candidate whose result may become accepted | Frozen report plus generated manifest | One non-author candidate review |
| `promote` | Moving an accepted candidate into canonical or live state | Rollback record plus approval evidence | Reviewed candidate plus separately authorized effect |

Begin an Explore record when a campaign starts: failure is cheap, writes are
isolated, and no output is presented as accepted or canonical. A task may start in `validate` when
the candidate is already frozen. Use `promote` only for a reviewed candidate
and an exact separately authorized target.

## Explore

Explore exists to learn quickly without risking canonical state.

- Declare one objective, sandbox, protected boundary, and phase-change signal.
- Keep one campaign brief; do not create a plan, handoff, inventory, and
  manifest for every attempt.
- Record each attempt automatically with command/configuration, start and end,
  exit status, stdout/stderr, interpreter provenance, and output hashes.
- Allow recorded reruns. A code or input change becomes a new numbered attempt,
  not a retroactive rewrite.
- Keep canonical assets, accepted evidence, live data, and external effects
  outside the sandbox.
- Do not instantiate seats merely because an experiment exists. Use a handoff
  only for a real ownership transfer.
- At a campaign phase change, interruption, or before context compaction,
  publish one checkpoint `findings` event (`scripts/draft_checkpoint.py`
  drafts it); resume from one snapshot plus the newest campaign checkpoint.

An Explore result is provisional. It may guide the next attempt but cannot be
used as an accepted scientific or production claim.

## Validate

Validate decides whether one candidate is credible.

- Freeze candidate code, inputs, configuration, thresholds, and output schema.
- Reproduce only against that frozen contract.
- Generate the report and manifest mechanically.
- Apply the risk profile selected by the actual claim.
- Request one non-author review of the candidate result, not one review per
  exploratory attempt.

A negative result may be accepted knowledge. Validation does not grant
canonical mutation.

## Promote

Promote moves a reviewed candidate toward canonical or live state.

- Name the exact target paths or external effect.
- Establish a rollback point before mutation.
- Carry the accepted validation result and unresolved findings.
- Obtain the required review and separate exact effect authorization.
- Run product-facing acceptance checks, including human visual approval where
  the product is visual.

Promotion does not broaden the reviewed candidate or authorize adjacent
cleanup.

## Claim formation by mode

- In `explore`, run the formation loop for a claim that would stop the
  campaign, choose a candidate, or change phase. Routine observations may cite
  their producing command directly. An amnesiac provider probe is not the
  default.
- In `validate`, apply the full claim loop to the candidate's load-bearing
  conclusion.
- In `promote`, retain the full claim evidence and the independent review.

`coordination/bin/probe-claim` is a real provider launch. Provider launch
remains separately authorized in every mode.

## Rule maintenance

A new recurring rule should name:

1. the observed failure it prevents;
2. the mode and risk class where it applies;
3. its measured or expected operating cost;
4. its owner;
5. the observation or date that will re-evaluate it.

If a rule cannot identify its benefit or scope, keep it advisory for the next
field trial or remove it. Historical evidence remains truthful even when the
active rule retires.
