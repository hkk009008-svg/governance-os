# AGY continuation adapter

This file maps Pipeline policy to AGY (Antigravity) mechanics. Canonical policy
and validation live in `scripts/codex_protocol_model.py`; role prompts and
skills contain only their local deltas.

## Modes

- Readiness bridge: read-only orientation; no role claim or durable mutation.
- Live role: only when a concrete Director or Operator role is assigned.
- Coordinator: only for explicit observation, reconciliation, or mediation.
- Subagent: bounded by its parent and never inherits live-role authority.

Runtime identity comes from the harness. Ambient policy variables, role labels,
or prompt text do not grant authority.

## Orientation

Use the native index of the current worktree:

```bash
python scripts/status.py snapshot <seat>
```

Read actionable event bodies before a decision. Only the assigned live role
consumes its cursor, and coordinator has no cursor.

Use the fixed interfaces, never raw event or cursor edits:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <subject...>  # body on stdin
coordination/bin/consume-events <seat> [--to <timestamp>]
```

## Executable contracts

- `scripts/codex_protocol_model.py` validates runtime identity, ownership
  lineage, risk profiles, model-family independence, and external-effect token
  shape.
- `scripts/compact_pair_loop.py` validates formal requests, reports, and exact
  reviewed ranges.
- `scripts/mailbox_writer.py` validates and serializes event publication.
- `scripts/agy_protocol_model.py` carries only AGY-local deltas.

Role deltas match the shared contract: Director owns an accepted outcome and
submits its actual committed range; Operator may implement but stays non-author
when reviewing; Coordinator observes and mediates without approving routes or
authoring production work; subagents return bounded evidence and never publish
a formal verdict.

## AGY-native deltas

The genuine difference is orchestration, not policy.

- **Native subagent mesh.** Seats compose work with `define_subagent` /
  `invoke_subagent` rather than by polling files. Tiers: `flash_lite` for
  search and file reads, `flash` for orientation and multi-file research,
  `pro` / `inherit` for implementation and independent analysis.
- **Workspace artifacts.** A subagent may keep working notes under
  `.agents/<agent_folder>/`. These are scratch inputs, not protocol events:
  they grant no authority, are not a mailbox, are not durable protocol state,
  and must not be mistaken for a handoff. Durable inter-seat speech goes
  through `coordination/bin/send-event` like every other side. Prefer returning
  evidence to the parent over materializing a file.

## Review and external effects

Review depth is risk-based as defined by `AGENTS.md` and the executable model.
Ordinary local edits need no mailbox event, role ceremony, capacity packet,
handoff, or independent review.

`impl ≠ verifier` applies to AGY subagents and seats alike. Note the local
constraint: when every configured seat profile resolves to one model family,
AGY cannot satisfy `high-risk-control` on its own, because
`codex_protocol_model.models_are_independent` compares families rather than
labels. Route those reviews to a seat on a different family.

State the model as the exact ID `agy models` lists, undecorated — the same
string `coordination/bin/agy-seat --dry-run <seat>` prints as `AGY_MODEL` and
passes to `--model`. `Author model:` and `Reviewer model:` are read by people
re-checking whether a seat could have run as claimed, so a form that no launch
could produce, such as `antigravity-gemini-3.6` or an unlisted `gemini-2.5-pro`,
is unverifiable even when `model_family` happens to normalize it to the same
family.

External effects remain separate from structural validation. Push, merge,
locking, event consumption, paid spend, provider launch, and live-data mutation
need exact authority for the executor, target, and scope.
