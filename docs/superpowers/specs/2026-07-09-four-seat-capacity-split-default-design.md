# Four-Seat Capacity Split Default Design

## Goal

Make full four-seat utilization the default for divisible or preplanned larger
work while preserving the existing director -> operator fast path for narrow,
tightly coupled, or shared-file tasks.

## Context

The existing pair contract is efficient for a single implementation slice:
director scopes and lands the smallest sufficient artifact, then operator
verifies the named artifact or commit. That loop should remain the default when
parallel work would create shared-file conflicts or fake coordination.

For larger work, director2 and operator2 should not default to idle observer
state when the coordinator can split the work into two independently reviewable
deliverables. The protocol needs an explicit promotion rule so coordinator
routes use both pairs without weakening ownership, evidence, or verification.

## Design

Coordinator applies one promotion question before routing:

Can this route produce two independently reviewable deliverables?

If yes, coordinator opens a dual-pair route:

- director owns Chunk A implementation.
- operator verifies Chunk A.
- director2 owns Chunk B implementation.
- operator2 verifies Chunk B.
- each chunk names disjoint write sets, explicit interfaces, focused tests,
  forbidden side effects, and its own verify-request/verification-report loop.

If no, coordinator keeps the single-pair fast path:

- one pair implements and verifies the active slice.
- Pair B performs bounded planning or preflight instead of idle standby.
- planning/preflight can include next-brief drafting, owner-question packets,
  environment checks, schema checks, likely selector discovery, or route-risk
  review.
- Pair B does not issue GO, edit the active shared files, or duplicate success
  mail for the active lane.

Coordinator owns convergence in both cases: capacity packets, one consolidated
route, join condition, conflict handling, and final closeout evidence.

## Acceptance

- The executable Codex model exposes a capacity split default renderer.
- The capacity board rejects active Pair B `idle` observer packets; Pair B must
  have planning, preflight, implementation, or verification work.
- Active coordinator routes must include the Capacity Split Default decision and
  the correct single-pair or dual-pair details.
- Codex continuation docs and coordinator/four-seat skills include the default.
- Coordinator, director, and operator-facing Codex agent prompts include the
  default.
- AGENTS.md records the agent-agnostic rule.
- A prompt-sync regression fails if these surfaces drift.
- Readiness output includes the default so fresh sessions see it during
  orientation.
- The active Task 2.4 route has a newer addendum that moves director2/operator2
  from observer-standby to bounded planning/preflight.

## Non-Goals

- Do not allow parallel implementation on shared files.
- Do not let subagents inherit seat, mailbox, cursor, GO, route, lock, push, or
  spend authority.
- Do not require dual-pair routing for small or tightly coupled fixes.
- Do not turn observer seats into duplicate verification reporters.
