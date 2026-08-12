# Coordinator → All: open reliability implementation plan

**When:** 2026-07-20T02:38:51Z · **From:** coordinator (online)

Task-board: pipeline-coordination-reliability-2026-07-20
Task ID: coordinator-reliability-implementation-plan
Status: WRITTEN DESIGN APPROVED; IMPLEMENTATION PLAN OPEN; BEHAVIOR CHANGES HELD
Supersedes active route: coordination/mailbox/sent/2026-07-20T02-26-33Z-coordinator-to-all-coordination.md@4e36dfb98d58399eba166852e629fe410427319e
Authorization source: user-task:written-reliability-spec-approved-2026-07-20
Repository: /Users/hyungkoookkim/Pipeline
Accepted target HEAD: 4729126755f03cba353c03160c1f6bea9cbec054
Approved design: docs/superpowers/specs/2026-07-20-coordination-reliability-friction-reduction-design.md@4729126755f03cba353c03160c1f6bea9cbec054
Plan execution parent: this route's committed full trigger SHA
Owner seat/model: coordinator / gpt-5.6-sol

## Outcome

Coordinator writes and self-reviews one implementation plan for the user-approved reliability design. The plan translates the accepted three-part design into exact TDD tasks without changing runtime behavior:

1. task-scoped fast-resume selection, issue attribution, and a complete read-only full-orientation capsule;
2. synchronized Codex guidance for first-attempt supported-profile fixed-writer publication in the known managed context; and
3. synchronized wait-first, bounded snapshot fallback guidance that preserves dispatch identity and forbids redispatch.

The plan must use existing dependencies, preserve the fixed writer and fence, keep legacy routes ineligible for fast resume, and require a distinct-model non-author Operator review of the eventual behavior-changing range.

## Target Allowed Paths

- docs/superpowers/plans/2026-07-20-coordination-reliability-friction-reduction.md

## Required planning evidence

- exact current definitions, callers, interfaces, and focused tests for scripts/ledger_start_guard.py and scripts/route_lineage.py;
- exact synchronized protocol-model and prompt surfaces for fixed-writer launch and task-monitor fallback;
- RED to GREEN test steps with concrete test names, commands, expected failures, minimal implementation shapes, and explicit-path commits;
- scope, error handling, authority invariants, rollback, and final independent-review verification;
- an explicit no-dependency and no-product-repository constraint.

Coordinator may inspect repository evidence read-only and may write, self-review, stage, and commit exactly the one plan path above. No behavior-changing source, test, prompt, protocol, product, dependency, or generated artifact may change in this phase.

## Seat state

- Coordinator: active only for the implementation plan and its local commit.
- Director: standby; no implementation packet exists.
- Director2: standby; no packet.
- Operator: standby; no verification request.
- Operator2: standby; no packet.

## Boundaries

No behavior-changing implementation is permitted by this route.

No evidence-ledger file or Git state may change.

No dependency installation or update is permitted.

No network action, service lifecycle, provider launch, backend access, or private-data access is permitted.

No merge is permitted.

No push is permitted.

No cursor consumption is permitted.

No lock action is permitted.

No cleanup, reset, rebase, or amend is permitted.

## Exact next trigger

Coordinator commits the one validated implementation plan, offers the user the execution choices required by the writing-plans workflow, and stops. No Director implementation packet or Operator verification request exists until the user chooses an execution approach.

Cursor at send: 0

Cursor at send: 0
