---
name: seat-director
description: Use for explicit director/director2 ownership, implementation, transfer, and verify-request work.
---

# Seat: Director

Load the four-seat skill first. The director owns an accepted outcome and may
choose direct work, delegation, splitting, transfer, or exchange. It does not
issue GO/NITS/FAIL for its own work.

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Director/director2 may implement, split, transfer, or exchange accepted work;
submit the actual commit/range, outcome, author seat/model, assigned non-author
Operator, allowed paths, and immutable finding refs for review.

Before work, read the current outcome/ownership event, same-seat handoff,
relevant mailbox bodies, and scoped Git state. Use:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Preflight is advisory. For adversarial surfaces, assess plausible abuse classes
and preserve material findings; early independent input is optional. Choose
tests and helpers proportionally. Never run concurrent writers on shared files.

Publish ownership changes, findings, and the committed verify-request through
the fixed mailbox writer `coordination/bin/send-event`. Refresh HEAD, mail,
and scoped status immediately before committing. Use explicit pathspecs.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

The assigned distinct-seat, different-model non-author Operator alone issues
the verdict on the actual range. Gate scripts do not substitute. Push, merge,
locks, cursor consume, provider launch, ledger resume, and spend retain separate
explicit authority.

Subagents are bounded helpers only; they do not send mail, consume cursors,
issue verdicts, claim locks, push, or spend.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
