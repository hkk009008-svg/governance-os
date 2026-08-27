# Claude desktop continuation adapter

This file maps the shared contract to Claude desktop mechanics. Read
`AGENTS.md` and `CLAUDE.md`; canonical risk and authority shape lives in
`pipeline/codex_protocol_model.py`.

## Orientation

The project `.mcp.json` supplies the normal MCP member label `claude`; the
label is not app or model attestation. Begin with
the user task, current Git status/diff, and Claude task history. Call
`team_status` once, then read addressed messages with `team_wait`. Historical
mailbox unread state is not an orientation obligation.

Use `team_send` directly for scoped work with Codex and AGY. Queued, returned,
acknowledged, replied, and substantively answered are distinct states. Wait for the state the
work needs; no transport state grants role, review, permission, or effect
authority.

## Native work

Use Claude's native large-context reasoning, workspace tools, visual review,
and bounded agents. Ground analysis in current code, the actual diff, and
executed tests. Native agents remain parent-scoped helpers; they are not fourth
team members, do not gain another app's identity, and cannot independently
grant a formal verdict or effect.

Parallelize read-only and nonoverlapping work where useful. Give one member
integration ownership and serialize writes to shared paths or resources. Keep
ordinary work direct and run one proportionate final verification pass.

Do not launch Codex, AGY, or another Claude provider from a terminal. Shell
commands exist for Git, builds, tests, deterministic harness operations, and
`bin/pipeline preflight`.

Explore, Validate, and Promote in `docs/protocol/work-modes.md` are optional
product-phase descriptions. They grant no role or authority and are unnecessary
for routine repository work.

## Review and effects

There are no standing seats. At a formal review boundary Claude may temporarily
be author or a non-author reviewer for one exact range. High-risk acceptance
requires a different model family from the author and an abuse-class
assessment. Claude may use AGY challenges as first-class evidence, but AGY
cannot be the sole formal reviewer or authority source.

Push, merge, release, paid spend, live-data mutation, and destructive
operations require exact current user/task authority for executor, target,
effect, and scope. No app message, config, task metadata, role, review, or green
test supplies missing authority.

## Continuation and targets

Git, tests, and Claude task history are normal continuation state. Write one
concise checkpoint only at a real ownership transfer, interruption, compaction,
or wrap. Legacy mailbox conversation, cursors, four-seat state, and peer
receipts remain compatibility evidence. Use the fixed mailbox writer only for
a risk-required formal review artifact, a real transfer/checkpoint `findings`
event, or the governed learning-candidate/disposition lifecycle when it must
outlive the app task, never routine chat.

Resolve target work with `bin/pipeline target`, then read the target
repository's instructions. The historical evidence-ledger adapter remains at
`docs/protocol/claude/ledger-cli-adoption.md`; it cannot grant product or
external-effect authority.
