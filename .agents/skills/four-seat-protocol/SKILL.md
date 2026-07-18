---
name: four-seat-protocol
description: Use in this repo when asked to continue, inspect, hand off, or operate the four-seat director/operator protocol from Codex. Do not use for ordinary feature work unless the user mentions a seat, mailbox, handoff, wave, continuation, readiness, or protocol decision.
---

# Four-seat protocol for Codex

Use this skill to orient, choose the lawful mode, and load the concrete seat
delta. It is a checklist, not a copy of the protocol. The runtime adapter is
`docs/protocol/codex/continuation.md`; the executable lifecycle is
`scripts/codex_protocol_model.py`.

## 1. Choose mode

- **Readiness bridge:** default; inspect and report only.
- **Live seat:** only when the user or parent names `director`, `director2`,
  `operator`, or `operator2`.
- **Coordinator:** only for an explicit reconcile, route, capacity, or gate
  assignment.
- **Subagent:** bounded by its parent; never silently becomes a seat.

Concrete identity controls handoff, mailbox, cursor, event addressing, and Git
index. Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.

## 2. Read durable state

User instruction wins. Then use current Git/code, applicable signed ref-bus
facts, relevant mailbox bodies/cursors, locks and executed evidence, same-seat
handoff, and finally cache/defaults. Read bodies rather than deciding from
counts. Refresh HEAD and mail immediately before a protocol decision or write.

## 3. Run the smallest orientation

Run the selected mode's orientation block in
`docs/protocol/codex/continuation.md`; that adapter owns same-seat handoff lookup
and startup commands.

- A readiness bridge reports durable state and blockers only.
- A live seat reads relevant mailbox bodies, then loads its concrete skill:

- Director/director2: `.agents/skills/seat-director/SKILL.md`
- Operator/operator2: `.agents/skills/seat-operator/SKILL.md`
- A coordinator loads `.agents/skills/seat-coordinator/SKILL.md`; the adapter
  makes gate, smoke, and capacity commands conditional on the actual claim.

## 4. Respect shared boundaries

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Apply the authority, mailbox, Git, subagent, and side-effect boundaries in the
continuation adapter. Local consequences: only the concrete live seat may
consume its cursor; only a non-author operator issues GO/NITS/FAIL; coordinator
does not author production fixes; separately gated effects need explicit
authority. Inspect staged scope after any authorized consume or event send.

The model owns pair lifecycle and the triggered contracts in the compact sync
capsule below. Apply them only when triggered; do not copy them into seat
artifacts.

### Model-backed contract capsule

Claude Function Harmonization: adapt Claude functions to Codex-native primitives; do not transplant Claude-only mechanics. Preserve AskUserQuestion discipline, background work discipline, dispatch-template minimalism, reviewer evidence rigor, and adversarial verification.

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

## 5. Keep artifacts proportional

Create a status, route, handoff, receipt, or verdict artifact only when it
changes ownership, carries authority, preserves a real transfer, records an
executed result, or states an actual blocker. Do not create chat-only green
prose or duplicate Lane V for an unchanged commit and question.

Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.
At a real stop, state the blocking boundary or plain next authority without a prescribed heading or returning seat commands to the user. Write a narrow handoff only at a real transfer/context boundary or explicit request.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.

## Optional read-only tools

```bash
.venv/bin/python scripts/mailbox_monitor.py --once
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

`scripts/draft_handoff.py <seat> --wave <wave> --smoke --output` may draft a
transfer scaffold; refresh live state before finalizing it. Diagnostics and
gate scripts are evidence, not operator GO.

## Target and reference adapters

- Evidence-ledger route: read `docs/protocol/codex/ledger-cli-adoption.md`
  before leaving Pipeline. Do not start ledger work from Content.
- Codex mechanics: `docs/protocol/codex/continuation.md`
- Lifecycle and triggered contracts: `scripts/codex_protocol_model.py`
- Universal doctrine: `docs/protocol/agents/`
- Folder ownership: `docs/protocol/protocol-assembly-map.md`
