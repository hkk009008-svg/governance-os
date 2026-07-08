---
name: four-seat-protocol
description: Use in this repo when asked to continue, inspect, hand off, or operate the four-seat director/operator protocol from Codex; covers readiness bridge mode, seat orientation, mailbox rules, Wave gates, and Codex-specific mechanics. Do not use for ordinary feature work unless the user mentions a seat, mailbox, handoff, wave, continuation, readiness, or protocol.
---

# Four-Seat Protocol for Codex

This is the Codex runtime checklist for Pipeline's four-seat protocol.
The executable kernel is `scripts/codex_protocol_model.py`; the short operating
adapter is `docs/protocol/codex/continuation.md`.

Central invariant: durable shared state beats chat memory. Read git commits,
current files, mailbox bodies, cursors, locks, logs, gate evidence, and
operator reports before trusting chat or stale summaries.

Anti-ceremony invariant: every seat, including coordinator, must actively
eliminate theater behavior. A status, route, handoff, receipt, or no-op report
is useful only when it preserves real transfer state, changes enforcement,
or cites executable evidence; do not create green-looking prose or receipt
churn that substitutes for proof.

## Source order

1. User direct instruction
2. Git commits and current filesystem
3. Mailbox events in `coordination/mailbox/sent/`
4. Handoffs and `STATE.md` cache
5. Defaults

When artifacts disagree, current git and mailbox bodies win over stale prose.

## Mode selection

- Readiness bridge: default mode. Orient and report only.
- Live seat: only when the user or parent prompt explicitly names `director`,
  `director2`, `operator`, or `operator2`.
- Coordinator: only when explicitly asked to reconcile, route, gate, or operate
  cross-seat state.
- Subagent: bounded by the parent prompt and its allowed mutation scope.

Never silently upgrade from bridge mode into a seat.

## Claude Function Harmonization:

- core stance: adapt Claude functions to Codex-native primitives; do not transplant Claude-only mechanics.
- AskUserQuestion discipline: ask only for cross-cutting, policy, or
  hard-to-reverse choices; use repo convention and durable state for ordinary
  file, naming, and routing choices.
- background work discipline: let long verification run in an exec session
  while independent read-only context gathering continues, then read the result
  before claiming status.
- dispatch-template minimalism: give subagents only the relevant rule IDs,
  allowed paths, evidence checks, side-effect limits, and env-u git hygiene
  instead of inherited doctrine.
- reviewer evidence rigor: reviewers use `pass | issues | unable_to_verify`,
  U1-U5 unverifiable reasons, reviewed-head checks, clean-tree checks, and
  command evidence.
- adversarial verification: verification agents actively try to make the gate
  or proof fail with non-vacuous RED, `--runxfail`, sibling, and
  touched-script/hook checks.

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

## Reviewer Result Handling

- Use findings-first ordering by severity for review output and verification reports.
- When relaying reviewer or verifier output, preserve verdict, findings, and next steps.
- separate uncertainty, inference, and follow-up so readers can tell evidence from hypothesis.
- do not auto-fix after a review; route or request the next implementation action instead.
- failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.

## Live-seat behavior sources

Concrete live-seat identity and canonical behavior source are separate.
Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.

Mailbox, cursor, heartbeat, event-addressing, and git-index operations use the concrete seat, not the behavior source.
For example, `CODEX_SEAT=operator` uses operator mailbox/cursor/index paths
while following the `operator2` behavior source.

## Same-seat handoff first

On a fresh/transplanted instance, if the user or parent prompt names a live
seat or coordinator, first locate the newest handoff from that same concrete
role before ordinary orientation:

- Live seat: newest `docs/HANDOFF-<concrete-seat>-*.md`.
- Coordinator: newest `docs/HANDOFF-coordinator-*.md`.

Use the concrete seat, not the behavior source. If no same-seat handoff exists,
say so and continue with the relevant checklist.

## Readiness bridge checklist

```bash
.venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
```

The bridge may report durable state and blockers. It must not consume cursors,
send mailbox events, edit inventory, claim locks, push, spend, or author
production changes.

Optional read-only awareness:

```bash
.venv/bin/python scripts/mailbox_monitor.py --once
.venv/bin/python scripts/mailbox_monitor.py --watch --interval 5
```

Optional handoff scaffold:

```bash
.venv/bin/python scripts/draft_handoff.py <seat> --wave 2 --smoke --output
```

Refresh live state before finalizing any handoff.

## Live seat checklist

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
```

Always check mail before protocol decisions or state-asserting writes. Read the
relevant mailbox bodies; do not decide from unread counts alone.

If the live seat intentionally consumes mail:

```bash
coordination/bin/consume-events <seat>
```

That command mutates and stages `coordination/mailbox/seen/<seat>.txt`. Inspect
staged scope before committing cursor-only state.

## Coordinator checklist

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
.venv/bin/python scripts/wave_gate_check.py 2
.venv/bin/python scripts/ci_smoke.py
```

Before committing an active coordinator task-board route:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md
```

Strict read-only protocol validation:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

Closed-cycle coordinator-join packets must also satisfy the executable
handoff gate: standby, idle, closeout, transfer, or transplant evidence must
cite a durable `docs/HANDOFF-*.md` artifact.

Coordinator is unpinned. Read all-scope coordinator mail. Do not consume coordinator mail and do not run `consume-events coordinator`.

The coordinator may reconcile inventory, locks, gate state, mailbox routing,
and handoff state. It may not author behavior-changing production fixes.

## Mailbox and cursor rules

- mailbox-first decisions: check mail and read relevant bodies before protocol
  decisions or state-asserting writes.
- A mailbox-only consume should stage only
  `M coordination/mailbox/seen/<seat>.txt`.
- If `HEAD` advanced, refresh stale seat-local index state before committing a
  cursor-only update.
- Use one consolidated coordinator route when cross-seat routing is warranted.
- Receipt checks are coordination evidence only; they do not prove assigned
  work is complete.

## Git index rule

Use `env -u GIT_INDEX_FILE` for ordinary git and pytest commands. Use a
seat-local or scoped temporary index only when deliberately maintaining cursor,
status, docs, or coordinator-only state.

Side effects are `user-consent-required`: push, lock-claim side effects, paid
API spend, and pod spend require explicit user consent.

Side-Effect Executor Token:
- Required fields: `side_effect_id`, `executor`, `target`,
  `allowed_command_class`, `preflight`,
  `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`,
  `observer_seats`, `final_closeout_owner`, and `non_goals`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation unless the user directly names the executing seat in the same prompt.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode: read live state only, do not repeat
  the side effect, and report only contradiction, missing required evidence,
  changed safety boundary, or explicit coordinator request.
- live evidence may close an already-satisfied side effect without appointing a
  redundant executor.
- multiple same-target side-effect success claims need a common side_effect_id; otherwise route validation fails.
- report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.

## Pair Operating Contract

- director -> operator is the fast path inside each pair: director scopes and
  sends the smallest sufficient artifact; operator verifies only that artifact
  or landed commit.
- Every baton handoff is a mailbox artifact, not chat: brief, verify-request,
  verification-report, or handoff with commit/range, paths, tests, exclusions,
  and exact next trigger.
- Every live-seat/coordinator turn ends with an `Exact Next Trigger` section
  naming the next lawful prompt, seat event, standby condition, or blocker; make
  it the final user-facing section as well as the terminal mailbox/handoff
  section.
- Director sends one verify-request per implementation or brief once scope is
  stable; include commit/range, brief path, evidence commands, known excluded
  workspace state, and expected verdict.
- Operator waits for a fresh verify-request or shipping commit; no duplicate Lane V
  for docs-only, status-only, or handoff-only commits, and no speculative
  verification when phase is ambiguous.
- No receipt/status churn: send mail only when it changes ownership, preserves
  evidence, requests verification, returns GO/NITS/FAIL, or blocks on
  user-gated side effects.
- When both seats are active, do not edit the same files or rerun the same
  task; first commit to land wins and the other seat narrows or stands down
  after git/mailbox refresh.
- At boundaries, stop with exact next trigger and durable handoff only when
  context is transferring; avoid broad recaps when mailbox/gate state already
  proves standby.
- Effectiveness means a closed loop: director artifact -> operator
  verification-report GO/NITS/FAIL -> director consumes the report or
  coordinator closes; gate scripts never substitute for operator
  verification-report GO.

## Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Coordinator promotion question: can this route produce two independently reviewable deliverables?
- If yes: director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.
- The two active chunks must name disjoint write sets, explicit interfaces, focused tests, forbidden side effects, and separate verify-request/verification-report loops.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types.
- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.

## Seat Subagent Development

Core rule: seats retain authority; subagents own bounded work.
Live seats and coordinator may choose bounded subagents at seat discretion; this does not require a separate user request for delegation.
Default behavior: every live seat and coordinator actively considers bounded subagents for non-trivial routed work and uses them when they add independent signal, capacity, or fresh verification. Direct work remains acceptable for small, tightly coupled, or authority-sensitive work.
After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.

- Director seats (`director`, `director2`) may use bounded implementer
  subagents for independent implementation slices, then require spec review,
  quality review, and director-seat synthesis before any verify-request.
- Operator seats (`operator`, `operator2`) may use read-only verifier helpers
  for diff inspection, focused reproduction, or edge-case review, but the
  operator seat still issues GO/NITS/FAIL.
- Coordinator may use read-only reconciliation helpers for inventory, mailbox,
  lock, gate, or plan-readiness checks, but the coordinator still owns the
  consolidated route or no-op report.
- Required loop: implementer -> spec review -> quality review -> seat synthesis.
- Give subagents only the parent prompt, allowed paths, acceptance evidence,
  forbidden side effects, and `env -u GIT_INDEX_FILE` git/pytest hygiene.
- Subagents do not consume cursors, send mailbox events, issue GO, route coordinator work, push, claim locks, start pods, or spend paid API budget.
- Do not run parallel implementation subagents on shared files or behind the
  same push-gated lock.

## Ledger CLI bridge

When the parent prompt routes Codex work to `/Users/hyungkoookkim/evidence-ledger`, read `docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.

- Pipeline remains the Codex four-seat governance kernel.
- Evidence-ledger owns product-local truth.
- Do not start ledger work from `/Users/hyungkoookkim/Content`.
- Start from Pipeline and run `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2` before entering evidence-ledger.
- Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE`.
- Read evidence-ledger CLAUDE.md and AGENTS.md before product edits.
- Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.

## Related files

- Kernel: `scripts/codex_protocol_model.py`
- Codex adapter: `docs/protocol/codex/continuation.md`
- Ledger CLI bridge: `docs/protocol/codex/ledger-cli-adoption.md`
- Seat status: `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- Root process layer: `AGENTS.md`
- Folder intent: `docs/protocol/protocol-assembly-map.md`
- Agent-neutral protocol: `docs/protocol/agents/`
