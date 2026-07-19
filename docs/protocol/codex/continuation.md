# Codex continuation adapter

This file maps Pipeline's governed protocol to Codex mechanics. Policy lives in
the executable model; this adapter keeps only mode, startup, mailbox, Git, and
target-repo consequences.

## Modes

- Readiness bridge: read-only orientation; no seat claim or durable mutation.
- Live seat: only when `director`, `director2`, `operator`, or `operator2`
  is explicitly named.
- Coordinator: only for explicit reconciliation or facilitation.
- Subagent: parent-scoped and never inherits seat authority.

Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.

## Startup

Fresh/transplanted named roles first locate the newest same-concrete-seat
`docs/HANDOFF-<seat>-*.md`; state when none exists. Then run:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Surface unread count, then read relevant mailbox bodies before decisions.
Consume only when intentionally authorized:

```bash
coordination/bin/consume-events <seat> [--to <last-read-timestamp>]
```

Fast resume is optional only for a named seat or coordinator continuing an
unchanged already-routed local implementation or review by passing its exact
current route ref. Fresh, transplanted, ambiguous, or external-effect work uses
ordinary fresh orientation. The classifications are `FAST RESUME: PASS`,
`FULL ORIENTATION REQUIRED`, and `START GUARD: FAIL`; full orientation is an
advisory fallback to ordinary startup, not `BLOCKED`, and fast resume grants no
external-effect authority.

Coordinator is unpinned and never consumes a cursor. Ordinary Git and pytest
use `env -u GIT_INDEX_FILE`; a seat index is only for deliberate cursor/status
staging. Refresh HEAD, relevant mail, and scoped status before a write or gate.

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

Automatic Seat-Task Routing: scripts/codex_protocol_model.py
For a committed next-seat trigger, use Codex task tools to discover/deduplicate,
reuse one compatible task or automatically create a fresh missing task, send
the exact trigger, wait, and reconcile. Never ask the user to relay a seat
prompt. Task routing grants no seat or external-effect authority.

Director/director2 may implement, split, transfer, or exchange accepted work
and submits the actual commit/range and outcome for review. Operator/operator2
may implement accepted work but cannot review anything it authored; as reviewer
it chooses sufficient evidence and issues GO/NITS/FAIL. Coordinator observes,
facilitates, and may mediate or claim eligible non-production work; it is not a
route-approval gate and does not author behavior-changing production work.
Readiness bridge reports the active outcome and owner without claiming work.

Preflight is advisory and may preserve a material finding without blocking
implementation. Ownership and review events go through the fixed mailbox
writer:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <body-file>
```

Subagents never inherit live-seat or coordinator authority. Subagents do not
consume cursors, send mailbox events, issue GO, claim locks, push, start pods,
or spend paid budget. Delegation is optional and owner-chosen.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

One committed verify-request binds reviewed base/head, outcome, author
seat/model, assigned non-author Operator, allowed paths, and finding refs. The
assigned distinct-seat, different-model Operator alone issues one GO/NITS/FAIL
report against the actual range through the fixed mailbox writer.

External effects remain separately gated. A structural token never grants
execution authority; require explicit user authorization for the exact
effect/executor/target/scope. Push, merge, lock, cursor consume, paid spend,
provider launch, and ledger resume are separate effects.

## Evidence-ledger bridge

For work routed to `/Users/hyungkoookkim/evidence-ledger`, read
`docs/protocol/codex/ledger-cli-adoption.md`. Start from:

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2
```

Do not start ledger work from `/Users/hyungkoookkim/Content`. Pipeline remains
the Codex four-seat governance kernel; evidence-ledger owns product-local truth.
Read evidence-ledger `CLAUDE.md` and `AGENTS.md` before product edits. Cross-
repo Git and pytest use `env -u GIT_INDEX_FILE`.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
