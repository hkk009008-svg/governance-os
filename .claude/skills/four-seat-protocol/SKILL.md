---
name: four-seat-protocol
description: Use for explicit Claude seat, mailbox, handoff, wave, continuation, or protocol decisions.
---

# Claude four-seat protocol

Choose readiness, named seat, coordinator, or subagent only from the explicit
prompt. Fresh roles find the newest same-seat handoff, then run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .claude/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Surface unread count and read mailbox bodies. The mailbox is authoritative
unless a live signed-bus event ref and matching seat cursor ref are both
verified; transport ambiguity fails visibly rather than resolving to the
convenient source. Only a concrete live seat consumes its cursor; coordinator
has no cursor. Durable events use the fixed mailbox writer
`coordination/bin/send-event`, never raw mailbox or cursor edits.

Optional ChatGPT Pro consultation is parent-only and advisory: follow the
`chatgpt-pro-consultation` skill; it grants no protocol or side-effect
authority.

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Director may implement or transfer. Operator may implement but cannot review
authored work; as reviewer it issues GO/NITS/FAIL. Coordinator facilitates but
does not approve routes or author behavior-changing production work. Readiness
reports without claiming.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Subagents do not consume cursors, send mailbox events, issue verdicts, claim
locks, push, merge, start pods, or spend. Ordinary Git/pytest use
`env -u GIT_INDEX_FILE`. External effects remain separately authorized.
