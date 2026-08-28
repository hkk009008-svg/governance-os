# Codex desktop continuation adapter

This file maps the shared contract to Codex desktop mechanics. Read
`AGENTS.md`; canonical risk and authority shape lives in
`pipeline/codex_protocol_model.py`.

## Orientation

The project `.codex/config.toml` supplies the normal MCP member label `codex`;
the label is not app or model attestation.
Start from the current user task, Git status/diff, and task history. Call
`team_status` once and read addressed messages with `team_wait`. Do not process
legacy mailbox backlog as startup work.

Queue success is not acknowledgement, acknowledgement is not understanding, and a linked
reply is not automatically substantive. Use `team_send` for direct scoped
collaboration and wait only when the answer is a real dependency. Messages
grant no role, review, permission, or external-effect authority.

## Native work

Use Codex's native workspace, task, worktree, review, and bounded subagent
mechanics. A subagent is an extension of this app: it never inherits live-role
authority and must never publish a formal verdict or live-role event as a
separate member.

Parallelize read-only and file-disjoint work; assign ownership and serialize
shared-file writes. Keep ordinary implementation direct, use focused tests
while iterating, inspect the exact diff, and run one final proportionate pass.

Explore, Validate, and Promote in `docs/protocol/work-modes.md` are optional
product-phase descriptions; they grant no role or authority.

Do not launch Claude, AGY, or another Codex provider from a terminal. Terminal
commands are for repository implementation, Git, tests, and
`bin/pipeline preflight`.

## Review and effects

There are no standing seats. At a formal boundary Codex may temporarily act as
author or as the non-author reviewer for one exact range. The reviewer must use
the actual diff; high-risk acceptance needs different-model-family review and
abuse-class analysis. AGY input is fully considered but cannot be the sole
formal verdict.

Push, merge, release, paid spend, live-data mutation, and destructive
operations each need exact current user/task authority. Native task controls,
MCP messages, test results, and role labels do not grant it.

## Continuation and targets

Git, tests, and Codex task history are the normal continuation state. Leave one
concise checkpoint only for real transfer, interruption, compaction, or wrap;
legacy conversation, cursors, and peer receipts are compatibility evidence.
Frozen review-history boundaries come only from
`pipeline/baselines/review_history_boundary.json`; do not copy their SHAs
into adapter prose.
Use the fixed mailbox writer only for a risk-required formal review artifact,
a real transfer/checkpoint `findings` event, or the governed
learning-candidate/disposition lifecycle when it must persist beyond the app
task, never routine chat.

Resolve target work with `bin/pipeline target`, then read that repository's
instructions. The historical evidence-ledger bridge remains at
`docs/protocol/codex/ledger-cli-adoption.md`; it does not grant product or
effect authority.
