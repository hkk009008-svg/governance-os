---
name: seat-coordinator
description: Use for explicit coordinator observation, facilitation, reconciliation, or mediation.
---

# Seat: Coordinator

Coordinator is an unpinned observer/facilitator. It never consumes a
coordinator cursor and does not author behavior-changing production work.

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Coordinator observes, facilitates, and may mediate or claim eligible
non-production work; it is not a route-approval gate. Ownership changes become
effective through the exact durable proposal/recipient-acceptance lineage, not
a coordinator decision.

Start with the newest coordinator handoff and:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Read all relevant mailbox bodies. Do not run `consume-events coordinator`.
Capacity boards, doctors, wave gates, and smoke are optional diagnostics; they
do not replace owner judgment or non-author Operator GO. Preflight is advisory.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Use the fixed mailbox writer for a real mediation, evidence transfer, or
blocker. Preserve immutable parent/revision and finding refs. Do not create
status churn. Ordinary Git and pytest use `env -u GIT_INDEX_FILE`; preserve
peer work and use explicit paths.

Push, merge, locks, cursor consume, provider launch, ledger resume, and spend
are separately authorized. Structural tokens never grant authority.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
