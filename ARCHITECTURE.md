# Architecture

Pipeline connects three interactive desktop apps to one repository without
creating a standing hierarchy. The harness has four small layers.

## 1. Desktop bindings

| App | Binding | Member label |
|---|---|---|
| Codex | `.codex/config.toml` | `codex` |
| Claude | `.mcp.json` | `claude` |
| AGY | `.agents/plugins/pipeline-team/` | `agy` |

The labels select message routes. They are not cryptographic app or model
attestation because processes owned by the same local account can edit local
state.

## 2. Team transport

`pipeline/team.py`, `team_mcp.py`, `team_messages.py`, and `team_store.py`
provide three MCP tools: `team_status`, `team_send`, and `team_wait`.

Messages live in `pipeline-team/messages.sqlite3` under the repository's Git
common directory, so linked worktrees share one queue without committing chat
to Git. The store rejects symlinks, replacement inodes, hardlinks, and
group/world-accessible files. That protects against other OS users and
accidental replacement, not the repository owner.

The transport distinguishes queued, returned, acknowledged, replied, and
substantively answered. None of those states grants repository or external
authority.

## 3. Repository work

The apps use normal Git worktrees, files, builds, and tests. Read-only or
file-disjoint work may run concurrently; shared writes have one integration
owner. `bin/pipeline` dispatches deterministic local commands and
`pipeline/harness_preflight.py` checks app bindings and adapter handshakes. It
does not launch a model or prove an app window is live.

## 4. Formal review and admission

Most changes stop after proportionate verification. Two risk classes create a
formal boundary:

- `material-behavior`: one non-author Codex or Claude review.
- `high-risk-control`: the same, with different model families and explicit
  abuse-class analysis.

The author publishes one exact-range `verify-request`; the reviewer publishes
one bound `verification-report` with GO, NITS, or FAIL. Both use the fixed
writer behind `bin/pipeline mail send` and live in
`coordination/mailbox/sent/`. Published artifacts are append-only. Retain the
original request/report chain when superseding a verdict; do not prune it.
Admission checks artifact changes throughout the supplied range, including
mailbox-only commits and intermediate changes hidden by a later restoration.
They cannot recover evidence discarded from that supplied Git history.

`pipeline/compact_pair_loop.py` validates the two artifacts, range ancestry,
publisher/model-family bindings, evidence, and FAIL supersession.
`pipeline/ci_admission_gate.py` requires high-risk coverage for changes to
authority surfaces. Runtime reviewer identity is externally attested by the
desktop task; repository text alone cannot prove which app generated it.

AGY is an equal interactive engineering member and may author changes or
requests, but formal acceptance is restricted to non-author Codex or Claude.
The separate parent-owned AGY helper is advisory and has no team identity or
effect authority.

## Authority boundary

Review establishes evidence about code. It never authorizes push, merge,
release, spend, destructive action, or live-data mutation. Those effects need
exact current user authority for their executor, target, effect, and scope.
