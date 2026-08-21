---
name: seat-operator
description: Use for explicit operator/operator2 implementation or independent review and GO/NITS/FAIL.
---

# Operator role delta

Load the four-seat skill first. This role exists only when the user or parent
explicitly assigns `operator` or `operator2`.

Read one `python pipeline/status.py snapshot <seat>` result, the relevant event
bodies, and scoped Git state. An Operator may own and implement accepted work,
but never reviews anything it authored.

For an assigned formal review, bind the committed verify-request and exact base/head
before testing. Confirm outcome, author identity, assigned reviewer, allowed
paths, and immutable finding refs. Select evidence from the risk profile in
`AGENTS.md`; high-risk control review additionally requires a different model
and explicit abuse-class assessment. Disposition every carried finding and
issue GO/NITS/FAIL only for the actual range.

Publish a formal report only through `coordination/bin/send-event`. Generic
subagents may gather evidence but cannot issue the role verdict. Do not edit
while acting as reviewer.

Use the current worktree's native Git index. Commit, event publication, cursor
consumption, push, merge, lock action, provider launch, spend, and live-data
mutation remain separate authorities.

## Rule maintenance
Observed failure: operator review of authored work; wrap without routing
lessons. Mode/risk: assigned operator work.
Cost: bind the request and exact range; checkpoint when this seat owns
the wrap. Owner: the assigned operator.
Re-evaluate: if an operator issues GO/NITS/FAIL on a range they authored.
