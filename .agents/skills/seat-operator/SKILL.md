---
name: seat-operator
description: Use for explicit reviewer-role (formerly operator/operator2) implementation or independent review and GO/NITS/FAIL.
---

# Reviewer role delta

Load the four-seat skill first. This role exists only when the user or parent
explicitly assigns `reviewer`. The `operator`/`operator2` names this file is
still filed under are retired: committed events keep parsing them, and the
fixed writer refuses them as the sender of a new one.

Read one `pipeline status` snapshot, the relevant event bodies, and scoped Git
state. A reviewer may own and implement accepted work, but never reviews
anything it authored.

For an assigned formal review, bind the committed verify-request and exact
base/head before testing. Confirm outcome, author identity, assigned reviewer,
allowed paths, and immutable finding refs. Select evidence from the risk
profile in `AGENTS.md`; high-risk-control review additionally requires a
different model family and explicit abuse-class assessment, and every model a
single CLI can select is one family — so that counterparty is the other CLI.
Disposition every carried finding and issue GO/NITS/FAIL only for the actual
range. The report's shape is `verification-report-format.md` beside this file.

At a wrap boundary, confirm the owning role's checkpoint `findings` event
exists and note a gap as a finding. Never author that checkpoint yourself: a
checkpoint's Owner must equal its envelope sender.

Publish a formal report only through `pipeline mail send`. Subagents may
gather evidence but cannot issue the role verdict. Do not edit while acting as
reviewer.

Use the current worktree's native Git index. Commit, event publication, cursor
consumption, merge, lock action, provider launch, spend, and live-data
mutation remain separate authorities.

## Rule maintenance
Observed failure: review of authored work; wrap without routing lessons.
Mode/risk: assigned reviewer work.
Cost: bind the request and exact range; confirm the owner's checkpoint exists.
Owner: the assigned reviewer.
Re-evaluate: if a reviewer issues GO/NITS/FAIL on a range they authored.
