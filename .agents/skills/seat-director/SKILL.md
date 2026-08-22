---
name: seat-director
description: Use for explicit author-role (formerly director/director2) ownership, implementation, transfer, and verify-request work.
---

# Author role delta

Load the four-seat skill first. This role exists only when the user or parent
explicitly assigns `author`. The `director`/`director2` names this file is
still filed under are retired: committed events keep parsing them, and the
fixed writer refuses them as the sender of a new one.

Read one `pipeline status` snapshot, the current task or ownership event,
relevant event bodies, and scoped Git state. A prior transfer record is read
only when it is relevant to a real transfer; it is not a startup gate.

The author owns the accepted outcome and may implement, delegate, split, or
transfer it within the recorded scope. Use focused tests and preserve material
findings. Publish an ownership change or formal review request only when durable
state actually changes, and only through `pipeline mail send`.

At a transfer, interruption, or wrap boundary, publish one checkpoint
`findings` event (draft it with `pipeline checkpoint`); its `Lessons:` line
routes lessons through `learning-candidate` events, and `none-considered` is
valid.

Review depth comes from `AGENTS.md`. If formal review is required, submit the
actual committed range with the complete Compact Pair binding. The author never
issues GO/NITS/FAIL for authored work. A new request names exactly
`Risk class: material-behavior` or `Risk class: high-risk-control`; the latter
also carries a nonempty `## Abuse Class Assessment` bullet section. Its
`Author seat:` is `author` and its `Assigned operator:` is `reviewer` —
`pipeline/compact_pair_loop.py` still accepts the legacy seat names so
committed requests keep validating, but a new pair uses the two roles.
Ordinary local work and external effects do not use a formal review request.

Use the current worktree's native Git index, preserve peer work, and stage
explicit paths only when separately authorized. Commit, event publication,
cursor consumption, merge, lock action, provider launch, spend, and live-data
mutation remain separate authorities.

## Rule maintenance
Observed failure: the owning role wrapping without a checkpoint, so lessons and
next action lived only in chat.
Mode/risk: assigned author work. Cost: one `pipeline checkpoint` at transfer,
interruption, or wrap. Owner: the assigned author.
Re-evaluate: if two consecutive author wraps omit `Checkpoint:` /
`Next action:`.
