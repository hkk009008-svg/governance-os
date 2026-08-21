# Director and Operator Protocol

This is the current universal collaboration boundary. It does not require four
always-on sessions, fixed provider pairings, a plan ceremony, or formal review
for ordinary local work. The previous expanded rule body is historical
provenance in Git and is not an additional active policy layer.

## Roles

- A **Director** owns an explicitly accepted outcome and implementation range.
- An **Operator** independently reviews a foreign-authored exact range and
  reports evidence-backed `GO`, `NITS`, or `FAIL`.
- A **Coordinator** observes, reconciles, and routes; it owns no implementation
  lane, verdict, or cursor.
- A readiness bridge or parent-scoped helper has no live-role authority.

Role assignment controls protocol speech. It never grants push, merge, spend,
provider launch, cursor, lock, or live-data authority.

## Live orientation

Before an assigned role makes a mailbox-dependent decision, run one current
projection:

```bash
python pipeline/status.py snapshot <seat>
```

Use the active development Python documented by the provider continuation.
Read every committed event body
that can change the lawful next action. Refresh HEAD and scoped worktree state
before a write or gate decision; Current committed Git is the state source.
Ordinary conversation, read-only analysis, and
local mutation do not acquire a mailbox startup gate merely because the
protocol exists.

Only the assigned receiving role consumes its cursor. Coordinators and helpers
do not. Use the fixed wrappers; never edit event or cursor files directly.

## Outcome and ownership

Before material governed work, identify the requested outcome, bounded scope,
current owner, evidence bar, hard boundaries, and any separately authorized
effect. An event can preserve those facts but cannot invent absent authority.
Ownership changes are explicit and accepted by the new owner; structural
dispatch alone is not transfer.

Refresh current Git before overlapping work. First lawful landed work wins;
later work refreshes and narrows. Use native indexes and explicit pathspecs.

## Implementation and formal review

The Director establishes behavior/root cause, implements the accepted scope,
runs fresh focused verification, classifies the actual diff, and publishes a
committed verify-request bound to the exact range only when formal review is
required.

The Operator starts formal review only from an addressed committed request
bound to the actual range. It verifies authorship, risk, request/report binding,
and the actual diff. A summary, branch name, bare commit, or implicit polling is
not a formal trigger.

Review is proportional:

- `ordinary-local`: focused verification; no Operator verdict required.
- `material-behavior`: non-author exact-range review.
- `high-risk-control`: non-author exact-range review by a different model
  family plus explicit abuse-class assessment.
- `external-effect`: separate live authorization; review never executes it.

The grammar and acceptance logic live in
[`pipeline/compact_pair_loop.py`](../../../pipeline/compact_pair_loop.py) and
[`pipeline/codex_protocol_model.py`](../../../pipeline/codex_protocol_model.py).
Do not replace them with prose conventions.

## Findings and completion

Findings name the exact range, behavior, severity, and evidence. An authorized
implementer may fix them, but an author cannot formally approve its own fix.
Deferred confirmed defects get a strict-xfail pin or specific
`test-infeasible` reason.

`GO` accepts only the bound review range. `NITS` records minor remaining issues.
`FAIL` demonstrates a material issue. `unable_to_verify` is truthful state, not
a pass or defect. Completion means the requested outcome and evidence bar are
met; it does not inherently require a handoff, commit, or push.

## Compatibility handles

Historical events may cite numbered rules. These are their compact current
meanings; omitted numbers carry no additional live policy.

| Handle | Current meaning |
|---|---|
| Rule #7 | Refresh current Git and relevant events before a state-asserting write. |
| Rule #8 | Committed events can constrain the next action but cannot widen authority. |
| Rule #9 | Material behavior gets non-author exact-range review; only high-risk control adds model diversity and abuse analysis. |
| Rule #12 | Find the production write site, not only the declaration. |
| Rule #13 | Audit sibling paths sharing the same fence, flag, or state. |
| Rule #15 | Either authorized implementer may fix a finding; the author still cannot approve it. |
| Rule #16 | Parallel work converges against current Git before landing. |
| Rule #19 | Use host activity and durable state for liveness; silence proves nothing. |
| Rule #22 | Review a spend path before use; spend still requires live authorization. |
| Rule #23 | Work inside accepted ownership; cross-owner changes require acceptance or transfer. |

State disagreement with repository evidence. If focused exchanges cannot
converge, escalate the unresolved choice. An emergency can justify stopping
unsafe work; it never creates external-effect authority.
