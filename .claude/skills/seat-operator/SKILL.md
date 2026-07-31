---
name: seat-operator
description: Use for explicit Claude operator/operator2 work and independent verdicts.
---

# Seat: Operator

Protocol SEMANTICS are canonical in `.agents/skills/seat-operator/SKILL.md`;
this file is the intentional Claude-native adaptation, not drift (O2
ruling 2026-07-31, ADR-067 Stage 3a). Where the two disagree on protocol
semantics, the `.agents` side wins and this file is corrected in the same
change.

Load the Claude four-seat skill first.

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
authored. As reviewer, read the committed request, confirm actual base/head,
outcome, author and reviewer identity, allowed paths, and immutable finding refs.
Select evidence from the risk profile in `AGENTS.md`; high-risk control review
additionally requires a different model and an explicit abuse-class assessment.
Inspect the actual range and issue GO/NITS/FAIL with explicit finding
dispositions through `coordination/bin/send-event`.

Preflight is advisory. A preference or missing checklist is not itself FAIL.
Use `env -u GIT_INDEX_FILE` and stay read-only while reviewing.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Helpers provide evidence but never issue the seat verdict. Push, merge, locks,
consume, provider launch, ledger resume, and spend remain separately authorized.
