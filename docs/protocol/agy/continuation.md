# AGY desktop continuation adapter

This file maps the shared contract to AGY (Antigravity) desktop mechanics. Read
`AGENTS.md`; canonical risk and authority shape lives in
`pipeline/codex_protocol_model.py`.

## Orientation

The workspace plugin at `.agents/plugins/pipeline-team/mcp_config.json` supplies
the normal MCP member label `agy`; the label is routing configuration, not app
or model attestation. Begin with the current user task, Git status/diff, and AGY
task history. Call `team_status` once, then read addressed messages with
`team_wait`. Do not process historical mailbox logs as routine startup work.

Queued, returned, acknowledged, replied, and substantively answered are distinct states. Use `team_send`
directly for scoped collaboration with Codex and Claude. Wait only when an answer
is a real dependency; no transport state or activity timestamp grants role,
review, permission, or effect authority.

## Native work

Use AGY's native strengths: rapid mapping and root-cause debugging, premise and
test-evasion challenges, browser actuation, rich visual artifacts, generative UI
widgets, and multi-model advisory reasoning. Ground all findings in current
code, the actual diff, and local test executions.

Subagents invoked via `invoke_subagent` are bounded extensions of this app: they
inherit no live-role authority, cannot publish a formal verdict, and never
execute external effects independently.

Parallelize read-only investigation and file-disjoint work where helpful. Assign
clear implementation ownership and serialize writes to shared paths or mutable
resources through one integrator. Keep ordinary work direct, use focused tests
while iterating, inspect the exact diff, and run one proportionate final
verification pass.

Explore, Validate, and Promote in `docs/protocol/work-modes.md` are optional
product-phase descriptions; they grant no role or authority and are unnecessary
for ordinary repository work.

Do not launch Codex, Claude, or another AGY provider from a terminal. Terminal
commands are for deterministic repository operations, Git, builds, tests, and
`bin/pipeline preflight`.

## Review and effects

There are no standing seats. AGY may investigate, challenge, test, and advise
across every risk profile. Material AGY findings must be considered and answered
on their merits, but AGY cannot be the sole formal reviewer or independent
accepting verdict for material behavior or high-risk controls (which require a
non-author Codex or Claude reviewer).

Push, merge, release, paid spend, live-data mutation, and destructive operations
require exact current user/task authority for executor, target, effect, and
scope. Review results, transport messages, app configurations, and test passes do
not grant execution.

## Continuation and targets

Git, executed tests, and AGY task history are the normal continuation state.
Write one concise checkpoint only at a real ownership transfer, interruption,
compaction, or wrap where another member must resume. Legacy mailbox
conversations, cursors, and peer receipts remain compatibility evidence. Use the
fixed mailbox writer only for a risk-required formal review artifact, a real
transfer/checkpoint `findings` event, or the governed
learning-candidate/disposition lifecycle when it must outlive the app task,
never routine chat.

Resolve target work with `bin/pipeline target`, then read that repository's
instructions.
