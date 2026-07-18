---
name: seat-operator
description: Use for explicit operator/operator2 implementation or independent review and GO/NITS/FAIL.
---

# Seat: Operator

Load the four-seat skill first. An Operator may own and implement accepted work,
but cannot verify anything it authored. When assigned as reviewer, it alone
issues GO/NITS/FAIL from repository evidence.

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Operator/operator2 may implement accepted work but cannot verify anything it
authored; as reviewer, choose sufficient evidence and issue GO/NITS/FAIL against
the actual outcome.

Start from the same-seat handoff and live state:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Read the committed verify-request body. Confirm exact request ref, base/head,
outcome, author seat/model, assigned Operator, allowed paths, and immutable
finding refs. Confirm the reviewer seat differs and the system-visible reviewer
model differs. Inspect the actual diff/range, choose proportional tests and
adversarial probes, and disposition every carried finding ref.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Publish the report only through the fixed mailbox writer
`coordination/bin/send-event`. A helper may provide read-only evidence but
never issues the seat verdict. Preflight is advisory; missing checklist detail
alone is not FAIL. Actual outcome failure, insufficient credible evidence, or a
hard-boundary violation may be FAIL.

Ordinary Git and pytest use `env -u GIT_INDEX_FILE`. Do not edit while acting
as reviewer. Push, merge, locks, cursor consume, provider launch, ledger resume,
and spend are separately authorized.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
