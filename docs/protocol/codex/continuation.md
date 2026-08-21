# Codex continuation adapter

This maps Pipeline policy to Codex mechanics; canonical validation lives in `pipeline/codex_protocol_model.py`.
Role prompts and skills contain local deltas. Reaching the other CLI:
`docs/protocol/peer.md`.

## Modes

- Readiness bridge: read-only orientation; no role claim or durable mutation.
- Live role: only when a concrete Director or Operator role is assigned.
- Coordinator: only for explicit observation, reconciliation, or mediation.
- Subagent: bounded by its parent and never inherits live-role authority.

## Orientation

Use the native worktree index: `coordination/bin/pipeline-python pipeline/status.py snapshot <seat>`.

Read actionable event bodies before a decision. The mailbox is the configured
coordination transport (`governance.toml` `[coordination]`); a signed-bus cutover
is an explicit reviewed transport change. Omission or a malformed declaration
fails closed, so transport ambiguity fails visibly. Only the assigned live role
consumes its cursor; coordinator has no cursor.

Use `coordination/bin/send-event <sender> <recipient> <kind> <subject...>`
(body on stdin) and `coordination/bin/consume-events <seat> [--to <timestamp>]`;
never raw event or cursor edits.

Refresh HEAD, relevant events, and scoped status before a write or gate. One
fresh snapshot is the orientation path; there is no separate fast-resume
classification or second doctrine dump.

At a long-horizon boundary — transfer, interruption, wrap, or compaction —
publish one checkpoint `findings` event (draft: `pipeline/draft_checkpoint.py`;
its `Lessons:` line routes learning candidates, and `none-considered` is valid).
Resume from one snapshot, the newest campaign checkpoint, and its actionable
bodies; unread backlog is not an orientation debt. Episodic recall via
`pipeline/learning_index.py query` is advisory; committed state outranks it.

## Executable contracts

- `pipeline/codex_protocol_model.py`: identity, ownership, risk, and effect tokens.
- `pipeline/compact_pair_loop.py`: formal requests, reports, and exact ranges.
- `pipeline/mailbox_writer.py` validates and serializes event publication.
- `pipeline/peer.py` runs the Claude CLI once as a child process and
  commits a receipt. It grants no authority and holds nothing open.
- This adapter owns host task discovery, dispatch, and waiting behavior.

Role semantics are owned by `.agents/skills/four-seat-protocol/SKILL.md`
and its role skills. Subagents return bounded evidence and never publish a
formal verdict or live-role event.

Review depth follows `AGENTS.md` and the executable model. Once formal review is
triggered, preserve its complete committed Compact Pair binding.

Host task tools own discovery, dispatch, and waiting. One trigger identifies one task;
monitoring failure authorizes neither redispatch, role substitution, nor an effect.

Use native host controls to list tasks, paginate turns, wait on bounded
snapshots, rename or pin work, archive or unarchive it, and fork completed
history. Review panels are presentation; never automate hard deletion or create
a persistent goal without an explicit request. All task metadata grants no role,
review, or effect authority and cannot replace formal exact-range review.

## Reaching the Claude CLI

`pipeline peer ask claude --task <id> --prompt-file <f>` runs it once as a
child process; `--dry-run` prints the argv and launches nothing. The exit code
is the delivery acknowledgement and the receipt under `coordination/peer/`
records what ran. A receipt is evidence, not attestation, and no verdict path
accepts one. Launching a peer is paid spend needing its own exact authority,
and never replaces the committed Compact Pair. Contract:
`docs/protocol/peer.md`.

## Review-state history boundary

Review-state projection is bound to
`pipeline/baselines/review_history_boundary.json` and its frozen exception
manifest, consumed fail-closed by `pipeline/check_coordination.py`. These one-way
baselines change only through a new high-risk-reviewed schema. An active FAIL
clears only through a valid GO/NITS report bound to and superseding it; active
failures block repository-wide, and the cutover must be an ancestor of HEAD.

## Evidence-ledger bridge

For the registered `evidence-ledger` target, read
`docs/protocol/codex/ledger-cli-adoption.md`, then the target repo's instructions.
Start from Pipeline; do not infer product authority from the bridge.

