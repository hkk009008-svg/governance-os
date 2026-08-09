# Codex continuation adapter

This maps Pipeline policy to Codex mechanics; canonical validation lives in `scripts/codex_protocol_model.py`.
Role prompts and skills contain local deltas. Desktop guide: `docs/protocol/app-quickstart.md`.

## Modes

- Readiness bridge: read-only orientation; no role claim or durable mutation.
- Live role: only when a concrete Director or Operator role is assigned.
- Coordinator: only for explicit observation, reconciliation, or mediation.
- Subagent: bounded by its parent and never inherits live-role authority.

Runtime identity comes from the harness; variables, labels, and prompts grant no authority.

## Orientation

Use the native worktree index: `python scripts/status.py snapshot <seat>`.

Read actionable event bodies before a decision. The mailbox is the
configured coordination transport (`governance.toml` `[coordination]`); a
signed-bus cutover is an explicit reviewed transport change; omission can
never activate the bus, and a malformed declaration fails closed — transport
ambiguity fails visibly. Only the assigned live role consumes its cursor, and coordinator has
no cursor.

Use `coordination/bin/send-event <sender> <recipient> <kind> <subject...>`
(body on stdin) and `coordination/bin/consume-events <seat> [--to <timestamp>]`;
never raw event or cursor edits.

Refresh HEAD, relevant events, and scoped status before a write or gate. One
fresh snapshot is the orientation path; there is no separate fast-resume
classification or second doctrine dump.

## Executable contracts

- `scripts/codex_protocol_model.py`: identity, ownership, risk, and effect tokens.
- `scripts/compact_pair_loop.py`: formal requests, reports, and exact ranges.
- `scripts/mailbox_writer.py` validates and serializes event publication.
- This adapter owns host task discovery, dispatch, and waiting behavior.

Role semantics are owned by `.agents/skills/four-seat-protocol/SKILL.md`
and its role skills. Subagents return bounded evidence and never publish a
formal verdict or live-role event.

Review depth follows `AGENTS.md` and the executable model. Once formal review is
triggered, preserve its complete committed Compact Pair binding.

Host task tools own discovery, dispatch, and waiting. One trigger identifies one task;
monitoring failure authorizes neither redispatch, role substitution, nor an effect.

External effects remain separate from structural validation. Push, merge,
locking, event consumption, paid spend, provider launch, and live-data mutation
need exact authority for the executor, target, and scope.

## Review-state history boundary

Review-state projection is bound to the committed history-boundary manifest
`scripts/baselines/review_history_boundary.json` (consumed fail-closed by
`scripts/check_coordination.py`) and to the frozen exception manifest it
names. Both are one-way versioned baselines: never repaired or extended in
place — a future boundary change ships a new schema version through its own
reviewed high-risk-control change. An active FAIL clears only through a valid
GO or NITS report bound to that exact request and explicitly superseding the
FAIL; active failed reviews are repository-global blockers, and the cutover
commit must resolve as an ancestor of HEAD or projection fails closed.

## Evidence-ledger bridge

For the registered `evidence-ledger` target, read
`docs/protocol/codex/ledger-cli-adoption.md`, then the target repo's instructions.
Start from Pipeline; do not infer product authority from the bridge.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
