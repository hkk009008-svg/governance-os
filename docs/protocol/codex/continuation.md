# Codex continuation adapter

This file maps Pipeline policy to Codex mechanics. Canonical policy and
validation live in `scripts/codex_protocol_model.py`; role prompts and skills
contain only their local deltas.

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

Read actionable event bodies before a decision. The mailbox is authoritative
unless a live signed-bus event ref and matching seat cursor ref are both
verified; transport ambiguity fails visibly. Only the assigned live role
consumes its cursor, and coordinator has no cursor.

Use the fixed interfaces, never raw event or cursor edits:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <subject...>  # body on stdin
coordination/bin/consume-events <seat> [--to <timestamp>]
```

Refresh HEAD, relevant events, and scoped status before a write or gate. One
fresh snapshot is the orientation path; there is no separate fast-resume
classification or second doctrine dump.

## Executable contracts

- `scripts/codex_protocol_model.py` validates runtime identity, ownership
  lineage, risk profiles, and external-effect token shape.
- `scripts/compact_pair_loop.py` validates formal requests, reports, and exact
  reviewed ranges.
- `scripts/mailbox_writer.py` validates and serializes event publication.
- This adapter owns host task discovery, dispatch, and waiting behavior.

Role deltas:

- Director owns an accepted outcome and submits its actual committed range.
- Operator may implement, but when reviewing stays non-author and issues the
  evidence-backed GO/NITS/FAIL for the assigned range.
- Coordinator observes, reconciles, and mediates; it is not an approval gate
  and does not author behavior-changing production work.
- Readiness bridge reports current evidence without claiming work.
- Subagents return bounded evidence to their parent and never publish a formal
  verdict or live-role event.

Review depth is risk-based as defined by `AGENTS.md` and the executable model.
When formal review is triggered, preserve the complete committed Compact Pair
binding; do not weaken it because a lower-risk task would not have required it.

Host task tools own discovery, dispatch, and waiting. One trigger identifies one
task; monitoring failure does not authorize redispatch, role substitution, or
an external effect.

External effects remain separate from structural validation. Push, merge,
locking, event consumption, paid spend, provider launch, and live-data mutation
need exact authority for the executor, target, and scope.

## Evidence-ledger bridge

For `/Users/hyungkoookkim/evidence-ledger`, read
`docs/protocol/codex/ledger-cli-adoption.md`, then the target repo's instructions.
Start from Pipeline; do not infer product authority from the bridge.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
