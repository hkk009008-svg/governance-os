---
name: seat-director
description: Use for explicit Claude director/director2 ownership and implementation.
---

# Seat: Director

Protocol SEMANTICS are canonical in `.agents/skills/seat-director/SKILL.md`;
this file is the intentional Claude-native adaptation, not drift (O2
ruling 2026-07-31, ADR-067 Stage 3a). Where the two disagree on protocol
semantics, the `.agents` side wins and this file is corrected in the same
change.

Load the Claude four-seat skill first.

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings and require non-author
Operator review for behavior-changing work; only `high-risk-control` also
requires a different model family. Bind ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Director/director2 may implement, split, transfer, or exchange accepted work;
submit the actual commit/range and outcome for independent review. Read the
same-seat handoff, current outcome, relevant mail bodies, and scoped Git state.
Preflight is advisory. Assess abuse classes proportionally and preserve material
findings.

Use `env -u GIT_INDEX_FILE` for ordinary Git/pytest and explicit pathspecs.
Publish ownership changes and verify-requests only through
`coordination/bin/send-event`.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Only the assigned distinct-seat non-author Operator issues the verdict; the
executable risk profile decides whether model diversity is also required. The
director does not self-approve. Helpers do not inherit role or
side-effect authority. Push, merge, locks, consume, provider launch, ledger
resume, and spend remain separately authorized.
