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

## Review-state history boundary

Current-schema request parsing begins strictly after the committed marker
`coordination/mailbox/sent/2026-07-25T05-45-10Z-coordinator-to-operator-verify-request.md@61786501e26f7e1bac92efbdcd4ff0ea468a7bbb`.
Active-failure continuity is frozen at implementation base
`8d05a76489b8609634e1635ebfad12792abc8119`: the already-active
`e0fbefdb56af03b8c04b6df58245f7533a3d83c0` FAIL remains active, historical
FAILs that were not active at that base do not become retroactive blockers, and
valid FAIL reports introduced after the base receive multi-request tracking,
even when their request predates the base. A newer request for the same Operator
may therefore be pending alongside an older active FAIL. Only a valid GO or NITS
report bound to that exact request and explicitly superseding its FAIL clears
the failure.

Pending/current request display is seat-filtered. Active failed reviews are
repository-global governance blockers, so a seat snapshot may display another
Operator's failure; `assigned_operator` remains explicit in structured output.
The active-failure cutover commit must resolve and be an ancestor of HEAD, or
review-state projection fails closed.

`scripts/baselines/immutable_review_history_exceptions.json` is a frozen,
one-way exception manifest bound to its sole Git introduction. Never repair or
extend that file in place. A future legitimate history exception requires a
new versioned manifest or instrument plus separately reviewed high-risk control
code; the frozen manifest remains byte-for-byte unchanged.

## Evidence-ledger bridge

For `/Users/hyungkoookkim/evidence-ledger`, read
`docs/protocol/codex/ledger-cli-adoption.md`, then the target repo's instructions.
Start from Pipeline; do not infer product authority from the bridge.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
