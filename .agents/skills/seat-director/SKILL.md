---
name: seat-director
description: Use for explicit director/director2 ownership, implementation, transfer, and verify-request work.
---

# Director role delta

Load the four-seat skill first. This role exists only when the user or parent
explicitly assigns `director` or `director2`.

Read one `python pipeline/status.py snapshot <seat>` result, the current task or
ownership event, relevant event bodies, and scoped Git state. A handoff is read
only when it is relevant to a real transfer; it is not a startup gate.

The Director owns the accepted outcome and may implement, delegate, split, or
transfer it within the recorded scope. Use focused tests and preserve material
findings. Publish an ownership change or formal review request only when durable
state actually changes, and only through `coordination/bin/send-event`.

At a transfer, interruption, or wrap boundary, publish one checkpoint
`findings` event (`pipeline/draft_checkpoint.py`); its `Lessons:` line routes
lessons through `learning-candidate` events, and `none-considered` is valid.

Review depth comes from `AGENTS.md`. If formal review is required, submit the
actual committed range with the complete Compact Pair binding. The Director
never issues GO/NITS/FAIL for authored work. A new request names exactly
`Risk class: material-behavior` or `Risk class: high-risk-control`; the latter
also carries a nonempty `## Abuse Class Assessment` bullet section. Ordinary
local work and external effects do not use a formal review request.

Use the current worktree's native Git index, preserve peer work, and stage
explicit paths only when separately authorized. Commit, event publication,
cursor consumption, push, merge, lock action, provider launch, spend, and
live-data mutation remain separate authorities.

## Rule maintenance
Observed failure: director wrap without a checkpoint, so lessons and next
action lived only in chat.
Mode/risk: assigned director work. Cost: one `draft_checkpoint.py` at
transfer, interruption, or wrap. Owner: the assigned director.
Re-evaluate: if two consecutive director wraps omit `Checkpoint:` /
`Next action:`.
