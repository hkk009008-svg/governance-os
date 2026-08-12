# Automatic Seat-Task Routing Design

**Date:** 2026-07-19

**Status:** Approved for planning

## Purpose

Make direct Codex task coordination the coordinator's default behavior. When a
committed route or review artifact identifies the next seat, the coordinator
delivers that trigger to the seat's Codex task and follows its result. The user
does not copy prompts between tasks.

This is transport behavior, not new authority. Route, ownership, review, and
external-effect boundaries remain exactly as they are.

## Problem

Pipeline already records the authoritative next actor and immutable trigger,
but the coordinator doctrine does not say how Codex should move that trigger
between user-visible tasks. A coordinator can therefore stop after printing a
prompt for the user to relay. That creates unnecessary work, delays
convergence, and can produce duplicates when the user and coordinator both
send the same trigger.

Personal memory is not a sufficient fix. It may not be present in another
task, model, checkout, or provider, and it cannot enforce duplicate handling.
The behavior belongs in the canonical Pipeline protocol with thin Codex-facing
references.

## Decision

For coordinator-owned Codex orchestration:

1. Discover recent Codex tasks before asking the user to relay anything.
2. Reuse one unambiguous task whose seat identity and Pipeline checkout match
   the committed trigger.
3. If no suitable task exists, or existing candidates are ambiguous or bound
   to incompatible work, automatically create a new local task in the saved
   Pipeline project for the required seat.
4. Send the committed immutable trigger directly. Apply the trigger's required
   model when distinct-model review is part of the contract.
5. Monitor the task and reconcile its committed result without requiring a
   user status prompt.
6. Route a correction or next seat directly when the result names one. Do not
   turn a finding into a new universal preflight cycle.

The coordinator must never instruct the user to copy a seat trigger when Codex
task routing is available.

## Routing Algorithm

The coordinator derives a dispatch identity from:

- the canonical immutable trigger path and full commit;
- the assigned concrete seat;
- the Pipeline project and checkout; and
- when applicable, the exact reviewed base/head and required reviewer model.

Before dispatch, the coordinator lists recent tasks and inspects plausible seat
matches. It then applies these rules:

- If the same dispatch identity is already in progress, do not send it again;
  monitor that task.
- If the same dispatch identity already produced its terminal committed
  artifact, reconcile that artifact and continue from it.
- If exactly one compatible seat task exists, send the trigger there.
- If none exists, automatically create the missing seat task and send the
  trigger as its initial prompt.
- If multiple tasks are ambiguous, create one fresh task rather than guessing
  which stale context is authoritative.

No persistent task registry, receipt, replay token, approval schema, or daemon
is added. Duplicate suppression uses the immutable trigger plus current Codex
task state and committed mailbox truth.

## Task Creation and Model Choice

Automatically created tasks use the saved Pipeline project and the local
shared checkout because live four-seat mailbox chronology and first-landed
commits belong to the hot tree. A separate worktree is used only when the
governing route explicitly requires one.

The concrete seat comes from the committed artifact. Model choice follows that
artifact and the proportional-independence rule:

- implementation keeps the routed author model unless the route says
  otherwise;
- actual-diff review uses a non-author Operator seat and a model different from
  the author; and
- an existing task may receive an explicit model override for the dispatched
  turn when needed to satisfy the committed request.

Task creation does not confer live-seat authority by itself. The task must read
and follow the committed route or compact-pair artifact before acting.

## Authority and Safety Boundaries

Direct task routing authorizes only delivery and observation of already
authorized local work. It never grants:

- push, merge, reset, rebase, or amend;
- cursor consumption or lock action;
- provider, service, database, or dependency actions;
- ledger resume or target mutation outside the committed route;
- booking, spend, deployment, cleanup, or other external effects; or
- permission for a coordinator to author behavior-changing production work.

Parent-scoped subagents remain unsuitable for live-seat mailbox publication or
formal GO. User-visible Codex seat tasks are the mechanism for concrete live
seat work. A task-tool failure is reported as a tooling blocker; it is not
converted into a request for the user to manually relay the prompt.

## Canonical Surfaces

The behavior should have one canonical definition in
`scripts/codex_protocol_model.py`, with concise references in:

- `AGENTS.md`;
- `.agents/skills/seat-coordinator/SKILL.md`; and
- `docs/protocol/codex/continuation.md`.

The references should state the decision order—discover, deduplicate, reuse or
create, send, wait, reconcile—and the existing effect boundaries. They should
not copy mailbox schemas, seat checklists, or task-tool API documentation.

## Failure Handling

- Missing task: create it automatically.
- Stale or incompatible task: create a fresh task.
- Duplicate in-flight trigger: monitor the existing task.
- Completed trigger: consume the committed result, not old chat narration.
- Send/create/wait tool unavailable: preserve the exact trigger, report one
  concrete tooling blocker, and do not fabricate delivery or ask for manual
  relay.
- Seat returns NITS/FAIL: route the exact finding back to the implementation
  owner; do not restart preflight.

## Verification

Focused tests must prove that:

- the canonical model contains the full routing decision order;
- all three thin adapters remain synchronized with that source;
- automatic creation is required when no compatible task exists;
- duplicate triggers are monitored rather than resent;
- formal Operator work is routed to a concrete task, not a parent-scoped
  subagent; and
- routing text never implies push, merge, cursor, ledger-resume, spend, or
  other effect authority.

The implementation should use existing Codex task tools directly. It should
not introduce a new task broker or persistent protocol entity.

## Acceptance

The change is accepted when a coordinator can receive a committed next-seat
artifact and, without user relay:

1. reuse or create the correct seat task;
2. deliver the exact immutable trigger once;
3. monitor that task to a committed result; and
4. continue convergence while preserving every separate authority boundary.
