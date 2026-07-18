---
name: seat-coordinator
description: Use when explicitly operating as coordinator to reconcile all-scope state, validate wave/capacity gates, route disjoint work, maintain coordinator-owned artifacts, or resolve cross-seat ownership. Never use coordinator authority to patch production behavior.
---

# Seat: Coordinator

The coordinator reconciles, routes, and closes cross-seat state. It has no
cursor and no authority to author behavior-changing production fixes. Load
`.agents/skills/four-seat-protocol/SKILL.md` first for shared orientation and
boundaries.

## Coordinator loop

1. Refresh Git, mailbox bodies, locks, inventory, gate output, and operator
   reports.
2. Identify whether state is already reconciled, a single pair owns the work,
   or two disjoint deliverables justify a capacity route.
3. Prefer the single-pair fast path for narrow/shared-file work. Use dual-pair
   routing only when write sets and verification loops are independently
   reviewable.
4. If routing is needed, publish one consolidated event through the adapter's
   fixed `coordination/bin/send-event` writer with ownership, disjoint scope,
   interface, tests, forbidden effects, join condition, and blocker handling.
5. Verify that consolidated route was received seat-by-seat. Do not create
   separate receipt events unless receipt state changes ownership or exposes a
   blocker.
6. Reconcile inventory/gate state only from executed evidence and the assigned
   non-author operator's report.
7. Close or transfer the cycle without receipt/status churn.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

The executable model owns the exact lifecycle and the compact trigger contracts
below. Apply them when triggered; do not duplicate them in route artifacts.

## Model-backed contract capsule

Mailbox decisions remain body-first: read relevant mailbox bodies before acting; live seat cursors are intentional per-seat state, and the coordinator has no cursor.
The verifying operator must be a non-author and alone issues GO/NITS/FAIL from repository evidence.
The coordinator may route and reconcile but not author behavior-changing production fixes.
Push, merge, paid spend, and every other side effect are separately gated and require explicit authority.

Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Ask whether the route yields two independently reviewable deliverables.
- If yes, director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- Otherwise Pair B performs bounded planning or preflight instead of idle standby.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types; coordinator owns convergence.

After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete. This is a working choice, not a standalone artifact.

Side-Effect Executor Token:

- Required fields include `side_effect_id`, `allowed_command_class`, and `stop_if_newer_mail_or_live_target_satisfied`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode; report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.
- live evidence may close an already-satisfied side effect without appointing a redundant executor.
- multiple same-target side-effect success claims need a common side_effect_id.

Triggered exceptions stay narrow: Production-affecting OR user-data-integrity issue, Security-critical, Active bleed-rate, or External time-pressure. The first-noticer claims initial response, uses stop-the-bleed first, and records acting under v5 §E temporary authority when applicable; the coordinator no-production-code boundary remains in force and resolution gets a post-incident note. A disagreement States the disagreement explicitly, uses project-data-grounded evidence, and chooses counter-refinement, defer to v(N+1), or an acceptance criterion; silent-accept is the receiver's own acceptance and the 2-cycle escalation limit routes persistence to the user.

Require wave-gate evidence before asserting blocked, immediate pod-off when a director gate-request is unserviced, and one consolidated mailbox event naming blocker, owner, and SLA. If needed, escalate to user with the acting-coordinator path; use a pre-brief skeleton only, no gate-relaxing or suppressive pins, and treat the transition as verified only from operator GO.

Reviewer output uses findings-first ordering by severity, must preserve verdict, findings, and next steps, and must separate uncertainty, inference, and follow-up. do not auto-fix after a review; failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.

Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.
At a real stop, state the blocking boundary or plain next authority without a prescribed heading or returning seat commands to the user.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.

## Capacity and route gate

Before committing an active coordinator task-board route:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md
```

Fix every named validation failure before the route is committed. The capacity
board is not required for a status read or a narrow single-pair task.

Use strict read-only diagnostics when needed:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

Diagnostics and `wave_gate_check.py` are process evidence. They do not prove a
row correct and never replace operator GO.

## Inventory and gate decisions

- Reconcile at a real session start, wave boundary, director gate request, or
  ownership transition; batch related writes.
- Mark verified only from the exact operator verification-report plus executed
  evidence for the reviewed range.
- Keep blockers truthful. Never relax a gate, suppress a pin, or rewrite a
  failure into green coordinator prose.
- Preserve packet/evidence snapshots under
  `docs/archive/coordination-evidence/<date-cycle>/`; do not move live packets
  out of `coordination/capacity/packets/`.
- A closed-cycle transfer/standby packet cites a durable `docs/HANDOFF-*.md`
  when an actual transfer boundary exists.

## No-op fast path

When the newest durable state is already reconciled and no lock, route,
inventory, or gate transition is due, do nothing. Do not send a mailbox event,
rewrite inventory, or create a no-op artifact. If the user asked for status,
return the concise evidence-backed result in chat.

## Allowed writes

With explicit path scope, coordinator may maintain:

- `docs/REMEDIATION-INVENTORY.md`;
- coordinator handoffs and protocol/evidence notes under `docs/`;
- routing events under `coordination/mailbox/sent/`;
- authorized lock state under `coordination/locks/`;
- discovery/reconciliation evidence under `logs/`;
- honest test-only pins or fixtures for known deferred defects.

Production pipeline modules are outside coordinator write authority, even for
a small, urgent, or blocking bug. Route the fix to the owning director or stop
for user direction.

## Helpers

Use a read-only reconciliation helper only when it adds independent signal for
inventory, mailbox, lock, gate, plan readiness, or receipt questions. The
coordinator retains synthesis and every route, inventory, handoff, lock, or
side-effect decision. Helpers do not consume, send, issue GO, push, claim locks,
or spend. Direct reconciliation needs no utilization report.

## Side effects and Git

Mailbox decisions are body-first. Use `env -u GIT_INDEX_FILE` for ordinary Git
and pytest. If a coordinator-only commit is authorized while the shared index
is dirty, use a scoped temporary index and verify its explicit pathspec.

Push, merge, lock actions, cursor consumption, paid spend, pod actions, and
other external effects remain separately authorized. Generic unit approval does
not appoint multiple executors; use the model's single-executor contract and
stop if fresh evidence shows the target is already satisfied.

## References

- Shared orientation: `.agents/skills/four-seat-protocol/SKILL.md`
- Runtime adapter: `docs/protocol/codex/continuation.md`
- Inventory: `docs/REMEDIATION-INVENTORY.md`
- Universal seat doctrine: `docs/protocol/agents/director-operator.md`
- Executable lifecycle: `scripts/codex_protocol_model.py`
