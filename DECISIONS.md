# Current architecture decisions

This file records only decisions that still shape the executable harness. The
full decision history remains available in Git.

## D1 — Native desktop apps are the team

Codex, Claude, and AGY are the three interactive members. Pipeline does not
launch model providers from the shell or create provider-backed terminal seats.
Native subagents inherit their parent app's scope and no separate authority.

## D2 — Routine communication is local and uncommitted

The three MCP tools use a repository-scoped SQLite store under the Git common
directory. Git is not a chat bus. Queued, acknowledged, replied, and substantive
are separate facts, and none grants authority.

## D3 — Work is direct and proportional

Ordinary work uses Git, focused tests, exact diff inspection, and one final
proportionate pass. No standing roles, lifecycle modes, capacity packets,
handoff chains, or planning ceremonies are required.

## D4 — Formal review has one pair of artifacts

Material changes use one exact-range `verify-request` and one bound
`verification-report`. The reviewer is a non-author Codex or Claude member.
High-risk controls require a different model family and abuse-class analysis.
AGY remains a full engineering member but not the formal accepting reviewer.

Current formal artifacts live in `coordination/mailbox/sent/`; Git history is
the archive. The fixed writer accepts no other workflow kind.

## D5 — Authority-surface admission is executable

The admission gate discovers authority-changing commits independently of the
review files and admits only exact high-risk GO/NITS coverage. Active FAILs
block until valid remediation supersedes them. Repository fields cannot attest
which desktop runtime actually performed a review, so runtime identity remains
an external task fact.

## D6 — Review never grants an external effect

Push, merge, release, paid spend, destructive operations, and live-data
mutation require exact current user authority for executor, target, effect,
and scope. No transport state, artifact, or green test can manufacture it.
