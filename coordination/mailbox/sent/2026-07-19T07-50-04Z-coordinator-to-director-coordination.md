# Coordinator → Director: route cross-repository review binding

**When:** 2026-07-19T07:50:04Z · **From:** coordinator (online)

Event type: coordination
Task-board: pipeline-cross-repository-review-binding-2026-07-19
Task ID: director-cross-repository-review-binding-implementation
Status: READY
Authorization source: user-task:approve-approach-a-and-written-cross-repository-binding-spec-2026-07-19
Approved design: docs/superpowers/specs/2026-07-19-cross-repository-review-binding-design.md@8cba82a6cc0e1ab05dde679bc9830e2f4f50b3dd
Implementation plan: docs/superpowers/plans/2026-07-19-cross-repository-review-binding.md@1bcc05bf5f3ee61c5c2195ff6766f04c090d4b8a
Operator2 FAIL: coordination/mailbox/sent/2026-07-19T06-39-39Z-operator2-to-all-verification-report.md@1ebadf84a4730f70116634f0f994550d6d604063
Director2 blocker: coordination/mailbox/sent/2026-07-19T06-46-07Z-director2-to-all-coordination.md@ff6ea7bcc481215d21255c1e187327ef007e5ce6
Implementation repository: /Users/hyungkoookkim/Pipeline
Implementation base rule: use this route artifact's committed trigger SHA, supplied in the direct task dispatch, as the exact implementation base
Owner seat/model: director / gpt-5.6-sol
Assigned reviewer seat/model: operator2 / gpt-5.6-terra

## Outcome

Implement the approved Approach A resolver correction test-first. Add one optional canonical Reviewed repository field to compact-pair requests and reports; preserve absent-field Pipeline-local and frozen historical behavior; validate an explicit absolute normalized non-symlink Git worktree root; resolve full base/head commits and strict ancestry there; require the report to reproduce the request-bound repository/base/head tuple exactly; and keep every current identity, finding, evidence, model-independence, fixed-writer, and external-effect boundary.

Use the committed plan task-by-task with superpowers:executing-plans. Commit the bounded runtime and synchronized-surface slices, run the plan's focused and aggregate verification, inspect the actual abuse boundaries, then publish one canonical committed Pipeline-local verify-request assigned to Operator2. Preflight is advisory and no additional CLEAR is required.

## Allowed Paths

- scripts/compact_pair_loop.py
- tests/unit/test_compact_pair_loop.py
- tests/unit/test_coordination_tooling.py
- scripts/codex_protocol_model.py
- tests/unit/test_protocol_prompt_sync.py
- .agents/skills/seat-operator/verification-report-format.md
- .claude/skills/seat-operator/verification-report-format.md
- ARCHITECTURE.md
- one fixed-writer-generated director-to-operator2 verify-request under coordination/mailbox/sent/

The Director may narrow unused paths or transfer or split ownership through a durable accepted handoff without coordinator approval. Do not run concurrent implementers on these shared files.

## Convergence

This correction unblocks canonical review transport only. It does not accept Task 5A or resume the backend lane. After non-author Operator2 GO on the protocol range, the coordinator will automatically dispatch Director2 to issue one replacement Task 5A request with Reviewed repository set to /Users/hyungkoookkim/evidence-ledger and the exact existing target range 16d1e4dfd204bc1344be93cffa20f99ca1a16b43..6782538190675fec9dbda0ea90e6b302377138a2, then return that request to Operator2.

## Boundaries

Do not modify evidence-ledger or its preserved worktree WIP; start or stop services; access a backend, database, Auth, or real data; install dependencies; push; merge; deploy; consume cursors; claim locks; book; spend; clean peer work; reset; rebase; or amend. This event grants no target mutation or external effect.

Cursor at send: 0
