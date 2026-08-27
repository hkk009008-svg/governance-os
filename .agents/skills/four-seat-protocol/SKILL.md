---
name: four-seat-protocol
description: Reserved for explicit formal review of an exact committed range, temporary author or reviewer responsibility, durable ownership transfer or continuation, or inspection of a legacy mailbox handoff.
---

# Pipeline formal-review boundary

Codex, Claude, and AGY are one desktop engineering team. Routine planning,
implementation, challenges, and handoffs use `team_status`, `team_send`, and
`team_wait`; they instantiate no seat and no durable mailbox artifact. Queueing
is not acknowledgement, acknowledgement is not a substantive reply, and transport attribution
is not an attestation or grant of authority.

Only a risk boundary creates temporary responsibilities:

- `author` owns the accepted change and its evidence.
- `reviewer` independently inspects a range it did not author and may issue
  GO/NITS/FAIL when formal review is required.
- AGY may co-direct, implement in isolation, map, debug, challenge, and propose
  findings, but it is not the independent formal verdict source.

Use `pipeline/codex_protocol_model.py` for risk/effect shape and
`pipeline/compact_pair_loop.py` for exact-range binding. `bin/pipeline mail send`
is retained only for a required formal review artifact, real durable transfer,
or governed learning-candidate/disposition record; never use it for
conversation. Legacy seat names and cursor files are read-only history.

Review depth stays proportional: focused verification for ordinary reversible
work, one non-author actual-diff review for material behavior, and a
different-family Codex/Claude review plus explicit abuse classes for high-risk
controls. Subagents and team messages supply evidence but no verdict.

Use the native worktree index, serialize overlapping writes, and stage explicit
paths. Push, merge, release, spend, destructive operations, and live-data
mutation require separate exact user/task authority. Write a concise checkpoint
only at a real transfer, interruption, or compaction boundary.
