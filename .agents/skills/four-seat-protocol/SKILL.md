---
name: four-seat-protocol
description: Use for an explicit Pipeline seat, mailbox, handoff, wave, continuation, or protocol decision.
---

# Four-seat protocol

Choose readiness bridge, named live seat, coordinator, or parent-scoped
subagent from the explicit prompt. Concrete seat identity controls handoff,
mailbox, cursor, and Git index.
Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.

Fresh/transplanted roles locate the newest same-seat handoff, then run:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Fast resume is optional only for a named seat or coordinator continuing an
unchanged already-routed local implementation or review by passing its exact
current route ref. Fresh, transplanted, ambiguous, or external-effect work uses
ordinary fresh orientation. The classifications are `FAST RESUME: PASS`,
`FULL ORIENTATION REQUIRED`, and `START GUARD: FAIL`; full orientation is an
advisory fallback to ordinary startup, not `BLOCKED`, and fast resume grants no
external-effect authority.
When fast resume falls back after collecting route and state evidence, full
orientation includes that read-only orientation capsule without a second
collection pass or any new authority.

Surface unread count and read relevant mailbox bodies before decisions. Only
the concrete live seat consumes its cursor; coordinator has no cursor. Use
`coordination/bin/consume-events <seat> [--to <timestamp>]` only intentionally.
Use `coordination/bin/send-event` as the fixed mailbox writer.

Codex Fixed-Writer Launch: scripts/codex_protocol_model.py
For an already-authorized exact fixed-writer action in the known managed
Pipeline checkout, use the supported scoped execution profile on the first
attempt. Scope any reusable prefix to coordination/bin/send-event plus the
sender seat. This grants no publication authority; on failure report the exact
writer error, use no alternate writer, and do not weaken the sandbox or fence.
Outside that known context, use ordinary execution and infer no authority from
this guidance.

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Director/director2 may implement, split, transfer, or exchange accepted work
and submits the actual range. Operator/operator2 may implement but cannot review
authored work; as reviewer it chooses sufficient evidence and issues
GO/NITS/FAIL. Coordinator facilitates but is not a route-approval gate and does
not author behavior-changing production work. Readiness bridge reports state
without claiming work.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Subagents do not consume cursors, send mailbox events, issue GO, claim locks,
push, merge, start pods, or spend. Ordinary Git and pytest use
`env -u GIT_INDEX_FILE`; preserve dirty peer work and stage explicit paths.
Push, merge, locks, cursor consume, provider launch, ledger resume, and spend
are separately authorized.

For evidence-ledger work, start in Pipeline and read
`docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
