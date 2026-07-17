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

Behavior sources are separate from concrete identities:
`director -> director`, `director2 -> director`, `operator -> operator2`, and
`operator2 -> operator2`.

The root risk tiers in `AGENTS.md` decide whether this adapter is needed at all.
Ordinary conversation and read-only inspection do not become live-seat work.

## Claude Function Harmonization:

Adapt Claude functions to Codex-native primitives; do not transplant
Claude-only mechanics.

- **User questions:** ask only for policy, cross-cutting, or hard-to-reverse
  choices; recover ordinary choices from repo convention and durable state.
- **Background work:** keep long verification in an exec session while doing
  independent reads, then collect its result before claiming status.
- **Dispatch:** send only role, scope, allowed paths, acceptance evidence,
  forbidden effects, and Git hygiene. Do not forward inherited doctrine.
- **Review:** preserve findings, verdict, uncertainty, reviewed HEAD, and
  command evidence. An incomplete reviewer result is not substitute evidence.
- **Adversarial work:** enumerate abuse cases before implementation and test the
  actual diff against them; do not add redundant same-question reviewers.

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

The executable model owns the complete pair lifecycle, capacity split,
emergency/disagreement handling, blocked-wave rules, reviewer-result handling,
and side-effect executor contract. Apply those details when their trigger
fires; do not recreate them here.

Generic user consent for a shared effect does not elect multiple executors.
Use the model's single-executor contract or close the action from fresh evidence
when the target is already satisfied. Gate output is process evidence, not an
operator correctness verdict.

## Subagents

Subagents never inherit live-seat or coordinator authority. Subagents do not
consume cursors, send mailbox events, issue GO, route coordinator work, claim
locks, push, start pods, or spend paid budget.

Use a bounded helper only when it adds independent signal or parallel capacity.
The parent keeps synthesis and every authority-bearing action. Do not run
parallel implementers on shared files or behind one push-gated lock. Direct work
requires no utilization report or no-op artifact.

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

Coordinator and seat chains continue internally until completion, a genuine
blocker, scope expansion, or a separately user-gated effect. Write a narrow
handoff only at a real transfer/context boundary or when explicitly requested.
At a stop, state the actual boundary or next authority in plain language; do
not impose a terminal heading or return seat commands to the user.

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
