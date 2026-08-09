# Universal Protocol Core

This is the small provider-neutral policy layer. Provider adapters translate it
into host mechanics; they do not redefine authority.

## Sources of truth

Use the source that owns the claim:

1. The user or authorized parent decides permission and task scope.
2. Executable code and current Git decide runtime facts and enforcement.
3. [`ARCHITECTURE.md`](../../../ARCHITECTURE.md) records verified topology.
4. This directory records universal policy; provider continuations record only
   host-specific mechanics.
5. Plans, handoffs, reviews, dashboards, and chat are evidence or history, not
   authority.

The canonical executable seams are:

- [`scripts/codex_protocol_model.py`](../../../scripts/codex_protocol_model.py):
  identity, ownership, work modes, review risk, and effect shape.
- [`scripts/compact_pair_loop.py`](../../../scripts/compact_pair_loop.py): formal
  request/report parsing and exact-range review binding.
- [`scripts/mailbox_writer.py`](../../../scripts/mailbox_writer.py), reached
  through [`coordination/bin/send-event`](../../../coordination/bin/send-event)
  and [`coordination/bin/consume-events`](../../../coordination/bin/consume-events):
  validated, serialized event and cursor writes with staging.
- [`scripts/status.py`](../../../scripts/status.py): read-only current-state
  projection.

When prose and an executable seam disagree, follow the seam for runtime facts,
preserve the user authority boundary, and repair the owning prose.

## Proportional startup

| Tier | Intended work | Minimum orientation |
|---|---|---|
| `tier-0-conversational` | Supplied context is sufficient | Do not orient the repository. |
| `tier-1-read-only` | Inspect or report | Read only evidence needed for the claim. |
| `tier-2-local-mutation` | Reversible scoped edits | Confirm the checkout; refresh scoped status and affected-path history. |
| `tier-3-governed-side-effect` | Publication, cursor consumption, provider launch, push, merge, spend, or live-data mutation | Refresh exact live authority, executor, target, scope, and external state immediately before acting. |

Full smoke is a completion check when a change affects runtime/governance
topology or relies on an architecture invariant. It is not a session-start
ritual.

## Evidence and implementation

- Measure factual inventory claims at the scope claimed. A focused command
  proves only its focused scope.
- Before changing a symbol, find its definition, writes, callers, imports,
  string references, and relevant siblings.
- For behavior change, begin with a failing behavior test when feasible;
  otherwise retain characterization evidence or a `test-infeasible` reason.
- Establish root cause before changing behavior after an unexpected failure.
- A confirmed defect deliberately deferred gets a strict-xfail pin or a
  specific `test-infeasible` reason.
- Run fresh, smallest-sufficient verification. A green check proves only the
  path it executed.
- Gate-controlling numbers come from a committed, citable instrument.

No plan, handoff, status file, broad smoke run, or commit is required merely to
make a small reversible edit. Create an artifact only when it preserves state
that Git, tests, and committed event bodies do not already carry.

## Guard admission

A new blocking guard is accepted only when it names the decision or effect it
protects, sits on the production call path, and has both a reversion control and
an evasion or bypass control. Missing or ambiguous evidence stays non-success.
A source-code marker, duplicated checker, or descriptive test name is not an
enforced control. Prefer strengthening the existing owning seam over adding a
parallel approval object or startup ritual.

## Work mode is not review risk

[`docs/protocol/work-modes.md`](../work-modes.md) controls iteration phase:

- `explore`: cheap reversible learning; no canonical mutation.
- `validate`: reproduce one frozen candidate and its evidence.
- `promote`: move a reviewed candidate toward canonical state with a rollback
  point and separate effect authority.

Review depth is classified independently by `review_profile_for()`:

| Risk | Required evidence |
|---|---|
| `ordinary-local` | Focused verification. |
| `material-behavior` | Non-author review of the exact committed range. |
| `high-risk-control` | Non-author exact-range review by a different model family, plus abuse-class assessment. |
| `external-effect` | Live authorization for the exact executor, target, effect, and scope. |

Different-model-family review is not a universal tax. A verdict never grants
an external effect.

## Authority and durable state

- A role, route, task structure, event schema, capability label, green test, or
  commit cannot widen user or parent authority.
- Current committed Git and committed event bodies outrank summaries and chat
  recollection for the facts they own.
- Transport ambiguity remains visible and fails closed; it is not an empty
  queue or implicit approval.
- Formal events and cursors use the fixed writers. Do not edit them directly.
- Editing, staging, committing, publishing, consuming, locking, pushing,
  merging, launching, spending, and live-data mutation are separate actions.
- Use the worktree's native Git index; do not create shared or per-seat indexes.

## Collaboration without ceremony

Delegate bounded independent work when it reduces latency or context load.
Give each implementer explicit ownership and never run concurrent implementers
on shared files. Helpers inherit task scope only: no live role, publication,
cursor, verdict, lock, or effect authority.

Material behavior receives non-author actual-diff review. Reviews, handoffs,
and status reports are produced at real decision or transfer boundaries, not
after every local step. Provider entrypoints and ownership are mapped in
[`protocol-assembly-map.md`](../protocol-assembly-map.md).
