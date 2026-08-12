# Coordination Hardening And Subagent Capacity Design

## Purpose

Make the four-seat Pipeline protocol harder to misuse and easier to run at full
team capacity. The system should detect stale or unsafe coordinator routes,
require meaningful end triggers, and give seats a clear, agent-neutral way to
use bounded helper agents without transferring seat authority.

## Current Findings

Three read-only audit lanes found the same pattern: the protocol has good
doctrine, but some high-traffic executable surfaces and prompts do not enforce
that doctrine yet.

- `scripts/protocol_capacity.py` is load-bearing but lacks active unit coverage
  in the model-derived verification command.
- `scripts/protocol_doctor.py --wave` can pass a repo with no capacity packets
  unless a route is provided.
- Route validation does not yet reject some unsafe or weak route text, including
  subagent authority leakage and placeholder next triggers.
- The active Wave 2 capacity board can remain valid even after newer mailbox
  reports supersede old blocked packet evidence.
- `docs/templates/agents/reviewer.md` is referenced by the agent-neutral
  implementer template but does not exist.
- Some Codex-facing director skill text still routes through Claude-specific
  templates.
- Existing subagent guidance says seats should consider helpers, but it does
  not force a durable "dispatch or direct/no-op because ..." utilization
  decision.

## Design

### Lane 1: Executable Protocol Gates

Add focused tests for the capacity and coordination gates before changing
behavior. The first pass should cover:

- capacity board no-packet enforcement through protocol doctor for final claims
- route validation rejects unsupported route paths or weak route bodies
- route validation rejects route text that authorizes subagents to consume
  cursors, send mailbox events, issue GO, create coordinator routes, push, claim
  locks, spend, or start pods
- `Exact Next Trigger` rejects placeholder trigger bodies such as
  "to be decided", "not applicable", "none", or equivalent empty content
- model-derived verification commands include the capacity tests

Stale-route freshness is valuable but should not be mixed into the first
hardening commit unless the packet status model is updated in the same batch.
Treat it as a follow-up after route/doctor/test coverage is in place.

### Lane 2: Prompt And Skill Capacity Sync

Create the missing agent-neutral reviewer template and align Codex-facing skill
text to agent-neutral dispatch paths.

Codify one required utilization decision after live-seat/coordinator
orientation:

```text
Subagent utilization decision: dispatch protocol-operator for ledger
verification review, or direct/no-op because this is a simple status check.
```

This is a planning/traceability requirement, not authority transfer. Subagents
remain unable to consume cursors, send mailbox events, issue GO, route
coordinator work, push, claim locks, start pods, or spend paid API budget.

## Non-Goals

- Do not close the current Stage 0 board in this batch.
- Do not push.
- Do not consume coordinator mail.
- Do not edit evidence-ledger product files.
- Do not rewrite the whole capacity-packet schema in one pass.
- Do not require subagents for tiny, tightly coupled, or authority-sensitive
  no-op checks.

## Acceptance

- New capacity/coordination tests fail before implementation and pass after.
- `protocol_doctor.py` has an explicit final-claim mode that requires capacity
  packets.
- Route validation catches subagent authority leakage and weak route/trigger
  bodies.
- `CODEX_VERIFICATION_COMMANDS` includes the new capacity/coordination tests.
- `docs/templates/agents/reviewer.md` exists and carries the reviewer-result
  schema invariant.
- Codex seat skills use agent-neutral templates for Codex dispatch.
- The executable model and docs require a subagent utilization decision for
  live-seat/coordinator turns.
- `ci_smoke.py` ends `OK`; pre-existing stale-SHA warnings may remain.
