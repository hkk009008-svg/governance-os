# Coordinator → All: open coordination reliability design note

**When:** 2026-07-20T02:26:33Z · **From:** coordinator (online)

Task-board: pipeline-coordination-reliability-2026-07-20
Task ID: coordinator-reliability-design-note
Status: RELIABILITY DESIGN NOTE OPEN; IMPLEMENTATION AND REVIEW HELD
Supersedes active route: coordination/mailbox/sent/2026-07-20T02-20-20Z-coordinator-to-all-coordination.md@e0a205ae2231cce0e8a0f85e5d81362c9fa21d7e
Authorization source: user-task:proceed-with-approved-reliability-slice-2026-07-20
Repository: /Users/hyungkoookkim/Pipeline
Accepted target HEAD: e0a205ae2231cce0e8a0f85e5d81362c9fa21d7e
Design execution parent: this route's committed full trigger SHA
Owner seat/model: coordinator / gpt-5.6-sol

## Outcome

Coordinator writes and self-reviews one design note for the already-approved narrow reliability slice. The note covers only three observed coordination frictions:

1. use the supported scoped execution profile on the first fixed-writer attempt in the known managed Pipeline context while preserving the existing fixed writer, lock, and security checks;
2. scope fast-resume route defects to the expected task and provide a complete read-only orientation capsule when legacy/current-route shape requires ordinary orientation;
3. use cursor-based task waiting first, then a bounded read-only thread snapshot when the live wait handler is unavailable, without redispatch or duplicate work.

The design must preserve the confirmed classifications: the real-checkout writer denial is environment-policy rather than a mailbox-writer source defect; full orientation remains advisory rather than blocked; task fallback is observation only. It must prefer existing dependencies and explicitly reject new brokers, agent frameworks, history rewrites, weakened locks, broad sandbox bypasses, or dependency migration.

## Target Allowed Paths

- docs/superpowers/specs/2026-07-20-coordination-reliability-friction-reduction-design.md

## Required design evidence

- current definitions, callers, tests, and documented contracts for the fixed writer and Codex launch path;
- current fast-resume expected-route selection, malformed-route handling, capsule inputs, and route-label conventions;
- current automatic task-routing wait/deduplication contract and the observed missing-handler fallback boundary;
- explicit error handling, tests, non-goals, authority boundaries, and rollout/rollback behavior;
- a clear statement that this design installs no dependency and changes no product repository.

Coordinator may write, self-review, stage, and commit exactly the design path above after confirming the route and smoke gates. Coordinator then asks the user to review the committed spec and stops. No implementation plan is written until the user approves the written spec.

## Seat state

- Coordinator: active only for the one design note and its local commit.
- Director: standby; no implementation packet.
- Director2: standby; no packet.
- Operator: standby; no verification request.
- Operator2: standby; no packet.

## Boundaries

No behavior-changing implementation is permitted by this route.

No evidence-ledger file or Git state may change.

No dependency installation, dependency update, network action, service lifecycle, provider launch, backend access, or private-data access is permitted.

No merge is permitted.

No push is permitted.

No cursor consumption is permitted.

No lock action is permitted.

No cleanup, reset, rebase, or amend is permitted.

## Exact next trigger

Coordinator commits the one validated design note, asks the user to review that exact file, and stops. User approval of the written spec is required before a planning route or implementation packet exists.

Cursor at send: 0
