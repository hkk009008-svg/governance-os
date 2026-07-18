# Claude continuation adapter

Claude seats use the same executable outcome contract and durable mailbox as
Codex. This file contains only Claude-local orientation and authority effects.

## Startup and modes

Claude starts read-only unless the user names `director`, `director2`,
`operator`, `operator2`, or coordinator. A Claude subagent is never a seat.
Fresh/transplanted roles first find the newest same-seat handoff, then run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .claude/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Surface unread count and read relevant mailbox bodies before decisions.
Only the concrete live seat may consume its cursor; coordinator has no cursor.
Use `coordination/bin/consume-events <seat>` only with intentional authority.
Use `coordination/bin/send-event` as the fixed mailbox writer. Ordinary Git
and pytest use `env -u GIT_INDEX_FILE`.

## Governed outcome

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored.

Director/director2 may implement, split, transfer, or exchange accepted work
and submits the actual commit/range. Operator/operator2 may implement accepted
work but cannot review authored work; as reviewer it chooses sufficient
evidence and issues GO/NITS/FAIL. Coordinator observes and facilitates, is not
a route-approval gate, and does not author behavior-changing production work.
Readiness mode reports the active outcome and owner without claiming work.

Preflight is advisory; material findings remain immutable inputs. Delegation is
an owner-chosen capacity tool. Subagents do not consume cursors, send mailbox
events, issue GO, claim locks, push, start pods, or spend.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

The committed verify-request binds actual base/head, outcome, author
seat/model, assigned non-author Operator, allowed paths, and finding refs. Only
the distinct-seat, different-model assigned Operator issues GO/NITS/FAIL through
the fixed mailbox writer.

External effects are separately user-gated for the exact
effect/executor/target/scope. Structural tokens do not grant authority.

## Provider mechanics

Use Claude Read/Grep/Glob for inspection, Edit/Write for scoped local changes,
and Bash for commands. Background commands must be read before claims.
Read-only verifier agents may inspect but never edit or issue the seat verdict.

For evidence-ledger work, start from `/Users/hyungkoookkim/Pipeline`, read
`docs/protocol/claude/ledger-cli-adoption.md`, run
`env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2`,
then read the target repo instructions. Pipeline remains the governance kernel;
evidence-ledger owns product-local truth.
