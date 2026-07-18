# Codex continuation adapter

This file translates Pipeline doctrine into Codex-native runtime actions. It is
an adapter, not a second protocol specification. Lifecycle grammar and triggered
contracts live in `scripts/codex_protocol_model.py`; shared policy lives under
`docs/protocol/agents/`.

## Source order

Use the newest applicable source in this order:

1. Explicit user instruction and authorization.
2. Current code, Git commits, and signed ref-bus facts when a three-way route is
   active.
3. Relevant committed mailbox bodies and the concrete seat's cursor.
4. Current locks, gate output, logs, and operator reports.
5. Same-seat handoff and `STATE.md` as orientation aids, never overrides.
6. Defaults in this adapter.

Read bodies and files, not counts or chat summaries. Refresh HEAD and mailbox
state immediately before a protocol write or decision.

## Mode selection

- **Readiness bridge** is the default. Inspect and report durable state; do not
  consume cursors, send mail, claim a lock, route work, publish a verdict, push,
  spend, or author production changes.
- **Live seat** requires an explicit `director`, `director2`, `operator`, or
  `operator2` assignment. Use the concrete seat for handoff, mailbox, cursor,
  event addressing, and Git-index identity.
- **Coordinator** requires an explicit reconciliation, routing, capacity, or
  gate assignment. It has all-scope read access and no cursor; it does not
  author behavior-changing production fixes.
- **Subagent** is bounded by its parent prompt and returns evidence to the
  parent. It does not become a seat.

Behavior sources are separate from concrete identities.
Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.

The root risk tiers in `AGENTS.md` decide whether this adapter is needed at all.
Ordinary conversation and read-only inspection do not become live-seat work.
`tier-0-conversational` and `tier-1-read-only` avoid implementation workflow;
`tier-2-local-mutation` uses focused checks and one completion pass;
`tier-3-governed-side-effect` refreshes every triggered authority guard. Do not
repeat Lane V for the same unchanged commit without a different, pre-stated
question. Deterministic artifact evidence may be reused only with unchanged HEAD
and relevant paths. Tier 3 requires fresh signed-bus, mailbox/cursor, lock,
approval, and external-state checks; reuse never relaxes a triggered guard.

## Claude Function Harmonization:

- core stance: adapt Claude functions to Codex-native primitives; do not transplant Claude-only mechanics
- AskUserQuestion discipline: ask only for cross-cutting, policy, or
  hard-to-reverse choices; use repo convention and durable state for ordinary
  file, naming, and routing choices
- background work discipline: let long verification run in an exec session
  while independent read-only context gathering continues, then read the result
  before claiming status
- dispatch-template minimalism: give subagents only the relevant rule IDs,
  allowed paths, evidence checks, side-effect limits, and env-u git hygiene
  instead of inherited doctrine
- reviewer evidence rigor: reviewers use pass | issues | unable_to_verify,
  U1-U5 unverifiable reasons, reviewed-head checks, clean-tree checks, and
  command evidence
- adversarial verification: verification agents actively try to make the gate
  or proof fail with non-vacuous RED, --runxfail, sibling, and
  touched-script/hook checks

**R-INDEPENDENCE:** Before implementation, classify adversarial-surface work and
capture an independent design-time enumeration as enforced-and-tested acceptance
criteria. Before completion, an independent reviewer must verify the actual diff.
This classification occurs before implementation. R-VERIFY-TIER prevents
redundant same-question passes.

## Start commands

For a fresh or transplanted named seat, first locate the newest
`docs/HANDOFF-<concrete-seat>-*.md`. A coordinator first locates the newest
`docs/HANDOFF-coordinator-*.md`. If none exists, say so and continue.

Readiness bridge:

```bash
.venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
```

Live seat:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave <wave>
env -u GIT_INDEX_FILE git log --oneline -5
```

Coordinator:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave <wave>
env -u GIT_INDEX_FILE git log --oneline -5
```

Run `scripts/wave_gate_check.py <wave>` only for an actual wave, inventory, or
gate claim. Run `scripts/ci_smoke.py` only when the task touches runtime/topology
invariants or its completion profile requires full project smoke.

Before an active coordinator task-board route:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md
```

Use the capacity board only for an actual multi-seat route. A narrow or
shared-file task stays on the single-pair fast path.

Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Coordinator promotion question: can this route produce two independently reviewable deliverables?
- If yes: director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.
- The two active chunks must name disjoint write sets, explicit interfaces,
  focused tests, forbidden side effects, and separate
  verify-request/verification-report loops.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types.
- coordinator owns convergence: capacity packets, one consolidated route, join
  condition, conflict handling, and final closeout evidence.

For evidence-ledger work, remain in `/Users/hyungkoookkim/Pipeline` until
`docs/protocol/codex/ledger-cli-adoption.md` directs the transition. Run its
ledger start guard before entering the target repo; do not start from Content.

## Mailbox and cursor boundary

Before a live-seat or coordinator protocol decision, route, handoff, or
state-asserting write:

1. Refresh seat status and recent Git history.
2. Identify relevant sent events.
3. Read their bodies and referenced artifacts.
4. Apply the newest binding event before acting.

Only the concrete live seat may deliberately consume its cursor:

```bash
coordination/bin/consume-events <seat>
```

Readiness bridges and subagents do not consume. Coordinators have no cursor and
never consume coordinator mail. Send one consolidated route when cross-seat
coordination is actually needed; do not create receipt or status churn.

Authority-bearing events use the fixed writer:

```bash
coordination/bin/send-event <from> <to|all> <kind> <subject...>
```

The body arrives on standard input. This command creates and stages a mailbox
event, so only an authorized live seat or coordinator runs it and then inspects
the staged path. Only operator seats may publish `verification-report`.

## Git and shared-tree boundary

Prefix ordinary Git and pytest commands with `env -u GIT_INDEX_FILE`. Use a
seat-local or temporary index only when deliberately maintaining it. Refresh
`git log --oneline -3` and scoped status immediately before writes because
another seat may move HEAD.

Preserve unrelated dirty files. Use explicit pathspecs and do not run broad
auto-fix or staging over peer work. A commit, push, merge, cursor consume, lock,
route mutation, and paid action are separate authority boundaries.

## Authority and side effects

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Mailbox decisions remain body-first: read relevant mailbox bodies before
acting; live seat cursors are intentional per-seat state, and the coordinator
has no cursor. The verifying operator must be a non-author and alone issues
GO/NITS/FAIL from repository evidence. The coordinator may route and reconcile
but not author behavior-changing production fixes. Push, merge, paid spend, and
every other side effect are separately gated and require explicit authority.

The executable model owns the complete pair lifecycle and the triggered
contracts below. Gate output is process evidence, not an operator verdict.

### Side-Effect Executor Token:

- Required fields: `side_effect_id`, `executor`, `target`,
  `allowed_command_class`, `preflight`,
  `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`, `observer_seats`,
  `final_closeout_owner`, and `non_goals`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation
  unless the user directly names the executing seat in the same prompt.
- side effects covered: remote-ref update, force update, lock action,
  paid-service spend, pod action, production generation, target-repo checkout
  refresh, cursor consume, and route mutation.
- observer seats default to observer mode: read live state only, do not repeat
  the side effect, and report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.
- live evidence may close an already-satisfied side effect without appointing a
  redundant executor.
- multiple same-target side-effect success claims need a common side_effect_id;
  otherwise route validation fails.

### Triggered exception contracts

- **Emergency:** Scope is exactly one of Production-affecting OR
  user-data-integrity issue; Security-critical; Active bleed-rate; External
  time-pressure. The first-noticer claims initial response, applies
  stop-the-bleed first, and may use cross-seat authority only while acting under
  v5 §E temporary authority. The coordinator no-production-code boundary remains
  in force; close with a post-incident note.
- **Disagreement:** States the disagreement explicitly, supplies
  project-data-grounded evidence, and chooses one of counter-refinement, defer to
  v(N+1), or acceptance criterion. silent-accept is the receiver's own
  acceptance; the 2-cycle escalation limit routes persistence to the user.
- **Blocked wave:** Require wave-gate evidence before asserting blocked, immediate
  pod-off when a director gate-request is unserviced, and one consolidated
  mailbox event naming blocker, owner, and SLA. If the coordinator is absent,
  escalate to user with the acting-coordinator path. Use a pre-brief skeleton
  only, no gate-relaxing or suppressive pins, and treat the transition as
  verified only from operator GO.
- **Reviewer result:** Use findings-first ordering by severity; preserve verdict,
  findings, and next steps; separate uncertainty, inference, and follow-up; do
  not auto-fix after a review. failed, incomplete, or unable_to_verify runs are
  not permission to invent substitute output.

## Subagents

Subagents never inherit live-seat or coordinator authority. Subagents do not
consume cursors, send mailbox events, issue GO, route coordinator work, claim
locks, push, start pods, or spend paid budget.

Use a bounded helper only when it adds independent signal or parallel capacity.
The parent keeps synthesis and every authority-bearing action. Do not run
parallel implementers on shared files or behind one push-gated lock. Direct work
requires no utilization report or no-op artifact.

After live-seat/coordinator orientation, record a Subagent utilization decision:
dispatch a bounded helper for a named task, or direct/no-op because the work is
small, tightly coupled, authority-sensitive, or already complete. This is a
working choice, not a required standalone artifact.

Project roles are available for bounded assignments:
`protocol-director`, `protocol-operator`, `protocol-coordinator`,
`lane-v-verifier`, and `money-gate-reviewer`.

## Optional read-only tools

- `scripts/mailbox_monitor.py --once` or `--watch --interval 5`: mailbox
  awareness without claiming a seat.
- `scripts/draft_handoff.py <seat> --wave <wave> --smoke --output`: draft a
  transfer scaffold; refresh live state before using it.
- `scripts/protocol_capacity_board.py --wave <wave>`: capacity evidence and
  route validation for an active coordinator route.
- `scripts/protocol_doctor.py --wave <wave>`: strict protocol diagnostics; add
  `--route coordination/mailbox/sent/<event>.md` for a specific route.
- `.codex/agents/agentNN.toml`: optional guardrail extensions. They never
  replace seat authority, cursors, or user-gated effects.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.

## Stop and transfer

Coordinator and seat chains continue internally and stop only at completion, a
genuine blocker, scope expansion, or a separately user-gated effect. Write a
narrow handoff only at a real transfer/context boundary or when explicitly
requested. At a real stop, state the blocking boundary or plain next authority
without a prescribed heading or returning seat commands to the user.

## Verification

Run the narrow command that proves the current claim. For protocol-surface
changes, the usual closeout is:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

These commands do not grant GO, push, merge, or other side-effect authority.

## Related files

- `.agents/skills/four-seat-protocol/SKILL.md`: triggered orientation.
- `.agents/skills/seat-director/SKILL.md`: director delta.
- `.agents/skills/seat-operator/SKILL.md`: operator delta.
- `.agents/skills/seat-coordinator/SKILL.md`: coordinator delta.
- `docs/protocol/codex/ledger-cli-adoption.md`: evidence-ledger transition.
- `docs/protocol/agents/director-operator.md`: universal seat doctrine.
- `scripts/codex_protocol_model.py`: executable lifecycle and invariant source.
