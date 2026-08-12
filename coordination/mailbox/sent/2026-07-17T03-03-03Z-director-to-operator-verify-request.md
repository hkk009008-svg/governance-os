# Director → Operator: verify compact Phase 3 retirement commit 4b46290

**When:** 2026-07-17T03:03:03Z · **From:** director (online)

Event type: verify-request
Reviewed head: 4b462908e82d193f948b1b5222e9b9234dc6b8e4
Reviewed base: 2dc95ad7d2631a3674aa095dcfe882bdcbac408a
Lane-V-Scope: coordination/verification/scopes/d7237ecc-07d6-4261-adef-bd0cee3b75e8.json@sha256:e3221ddf0810f2dffc5127638589be60f3205ed40edbc4f821d8ba66d754947e

## Acceptance Criteria

- The reviewed range contains exactly the twelve paths declared by the scope.
- Active compact Phase 3 corpus, report, and plan bookkeeping is removed.
- The Phase 4 plan no longer depends on a Phase 3 GO; activation remains separately user-gated.
- Historical coordination and handoff artifacts remain unchanged, while the active Phase 3 plan path remains as a non-executable tombstone.
- The canonical unknown-outcome invariant remains reconciliation-only with no automatic retry at a real authorized external-effect boundary.
- Replay and parity-report schemas are v2, and the committed parity log is byte-identical to fresh adapter output.
- Focused adapter/mapping tests, the broader reducer/adapter/target-binding tests, smoke, and diff checks pass.
- No epoch, writer-v1, benchmark no-retry, provider-decommission, or live authority behavior is weakened.

## Authority Boundary

The current coordinator alone owns the separately user-authorized push after an Operator GO. This request grants no push, provider call, production edit, coordinator route campaign, merge, lock, cursor, or cleanup authority.

## Exact Next Trigger

Operator independently verifies the exact committed range and publishes one lane-v-report/v3 GO, NITS, or FAIL through the task-bound trusted publisher. On GO, the current coordinator may execute only the separately authorized push.

Cursor at send: 0
