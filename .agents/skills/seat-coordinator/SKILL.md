---
name: seat-coordinator
description: Use when operating as the on-demand COORDINATOR seat in this repo's four-seat program-hardening campaign, including wave gates, inventory reconciliation, mailbox routing, cross-lane co-sign routing, discovery workflows, or pressure to fix a blocking bug directly.
---

# Seat: Coordinator

This is the coordinator checklist. The executable kernel is
`scripts/codex_protocol_model.py`; the shared active invariant is durable shared state beats chat memory.

The coordinator reconciles all-scope protocol state. It does not author
behavior-changing production fixes.

The coordinator must actively eliminate ceremony and theater behavior. Send a
route, handoff, no-op, or status only when it changes routing/enforcement,
preserves real transfer state, or cites executable evidence; never manufacture
green-looking coordinator activity from receipts or prose alone.

## Emergency Handling

- Emergency scope is exactly four categories: Production-affecting OR user-data-integrity issue, Security-critical, Active bleed-rate, and External time-pressure.
- Events outside those four categories use normal role partition and proposal cycles, even when they feel urgent.
- The first-noticer claims initial response with a `dispatch-claim` mailbox event carrying `urgency: emergency`.
- Triage discipline is stop-the-bleed first: use the smallest mitigation before root-cause analysis.
- Cross-seat temporary authority applies only during transplant or context exhaustion, and the commit body must include `acting under v5 §E temporary authority`.
- The coordinator no-production-code boundary remains in force during emergency routing and reconciliation.
- Within one session of resolution, write a post-incident note in `docs/INCIDENT-LOG.md` and review protocol gaps.

## Disagreement Handling

- States the disagreement explicitly in the next-cycle revision.
- Provides project-data-grounded evidence for the disputed item.
- Chooses exactly one resolution path: counter-refinement, defer to v(N+1), or acceptance criterion.
- silent-accept is the receiver's own acceptance, not permission inferred from peer silence.
- Re-REPLY is allowed for a live objection, but the 2-cycle escalation limit sends persistent disagreement to the user-principal.

## Blocked-Wave And Acting-Coordinator Handling

- Require wave-gate evidence before asserting blocked.
- Trigger immediate pod-off when a director gate-request is unserviced.
- Send one consolidated mailbox event naming blocker, owner, and SLA.
- If the owning coordinator is absent, escalate to user with the acting-coordinator path.
- Use a pre-brief skeleton only until the blocked owner or user direction confirms scope.
- Use no gate-relaxing or suppressive pins to make a blocked wave look green.
- A blocked-wave transition is verified only from operator GO, not route prose or a gate script alone.

## First commands

On a fresh/transplanted coordinator instance, first locate the newest
`docs/HANDOFF-coordinator-*.md` from the prior coordinator. If none exists,
state that and continue with the normal evidence bundle.

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave <N>
env -u GIT_INDEX_FILE git log --oneline -5
.venv/bin/python scripts/wave_gate_check.py <wave>
.venv/bin/python scripts/ci_smoke.py
```

Before committing an active coordinator task-board route:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md
```

For a strict read-only protocol validation bundle:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

Closed-cycle coordinator-join packets are hard-gated for durable transfer:
standby, idle, closeout, transfer, or transplant evidence must cite a
`docs/HANDOFF-*.md` artifact.

Surface the coordinator/all-scope mailbox count before reconciling. Then read
the relevant mailbox bodies. The coordinator is unpinned: it has no cursor and
must not run `consume-events coordinator`.

## Coordinator prohibition

Never patch production behavior as coordinator, even for a small or urgent fix.
Route fixes to the owning live seat or stop for explicit user direction.

Allowed coordinator commits must not hide a real defect signal or change a
gate's result by relaxing the gate.

## Inventory and gate authority

- mailbox-first decisions: check mail and read relevant bodies before routing,
  inventory, gate, handoff, or user-facing status claims.
- `scripts/wave_gate_check.py <wave>` is process evidence, not row-correctness
  evidence.
- `verified` requires an operator `verification-report` GO plus executed
  evidence.
- Reconcile inventory at session-start, wave-boundary gate, or a director's
  gate request. Batch writes instead of committing per micro-transition.
- Use one consolidated coordinator event when cross-seat routing is warranted.
- Active coordinator task-board routes must pass
  `scripts/protocol_capacity_board.py --wave <wave>` plus
  `--validate-route coordination/mailbox/sent/<event>.md` before commit.
- Use `scripts/protocol_doctor.py --wave <wave>` as the strict read-only
  validation bundle; add `--route coordination/mailbox/sent/<event>.md` for
  active route validation. It does not replace operator GO.
- When preserving packet/evidence snapshots for future reference, copy them
  under `docs/archive/coordination-evidence/<YYYY-MM-DD-short-cycle>/`; packet
  JSON snapshots go in that bundle's `packets/` subfolder. Do not move live
  packets out of `coordination/capacity/packets/`.

## Pair Operating Contract

- Every baton handoff is a mailbox artifact, not chat: brief, verify-request,
  verification-report, or handoff with commit/range, paths, tests, exclusions,
  and exact next trigger.
- Every live-seat/coordinator turn ends with an `Exact Next Trigger` section
  naming the next lawful prompt, seat event, standby condition, or blocker; make
  it the final user-facing section as well as the terminal mailbox/handoff
  section.

## No-op fast path

If the latest coordinator reconciliation already covers the newest durable
state, no locks need action, and the gate is still blocked for already-recorded
reasons, do not send a new mailbox event and do not churn the inventory. Report
the no-op with the commands you ran.

## Seat Subagent Development

Core rule: seats retain authority; subagents own bounded work.
Live seats and coordinator may choose bounded subagents at seat discretion; this does not require a separate user request for delegation.
Default behavior: every live seat and coordinator actively considers bounded subagents for non-trivial routed work and uses them when they add independent signal, capacity, or fresh verification. Direct work remains acceptable for small, tightly coupled, or authority-sensitive work.
After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.

Coordinator may use read-only reconciliation helpers for inventory, mailbox,
lock, gate, plan-readiness, or receipt checks. Their output is evidence for the
coordinator, not a route or correctness decision by itself.

- Coordinator still owns the consolidated route, no-op report, handoff, or
  inventory reconciliation.
- Subagents must be read-only unless the parent prompt explicitly names a
  coordinator-owned docs/test/log artifact to prepare.
- Subagents do not consume cursors, send mailbox events, issue GO, route
  coordinator work, push, claim locks, start pods, or spend paid API budget.
- Do not run parallel implementation subagents on shared files or behind the
  same push-gated lock.

## Coordinator may write

Coordinator may write only with explicit path scope:

- `docs/REMEDIATION-INVENTORY.md`
- `docs/` handoffs or protocol notes
- `coordination/mailbox/sent/` routing events
- `coordination/locks/` state when the protocol authorizes it
- `logs/` discovery or reconciliation artifacts
- test-only pins or fixtures that honestly track known-deferred defects

Production pipeline modules are outside coordinator write authority.

## Push, lock, and spend gates

Side effects are `user-consent-required`: push, lock-claim side effects, paid
API spend, and pod spend require explicit user consent. Prefer eligible
no-lock routing or stop for the user when those side effects are not
authorized.

Side-Effect Executor Token:
- Required fields: `side_effect_id`, `executor`, `target`, `allowed_command_class`, `preflight`, `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`, `observer_seats`, `final_closeout_owner`, and `non_goals`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation unless the user directly names the executing seat in the same prompt.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode.
- live evidence may close an already-satisfied side effect.
- multiple same-target side-effect success claims need a common side_effect_id; otherwise route validation fails.
- report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.

Ordinary git and pytest commands use `env -u GIT_INDEX_FILE`. If the shared
index is dirty and a coordinator-only commit is required, use a scoped
temporary index and inspect the staged pathspec before committing.

## Related files

- Runtime checklist: `.agents/skills/four-seat-protocol/SKILL.md`
- Kernel: `scripts/codex_protocol_model.py`
- Codex adapter: `docs/protocol/codex/continuation.md`
- Inventory: `docs/REMEDIATION-INVENTORY.md`
