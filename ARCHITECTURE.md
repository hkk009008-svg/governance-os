# Architecture

Pipeline connects three interactive desktop apps to one repository without a
standing hierarchy. Four small layers:

## 1. Desktop bindings

| App | Binding | Member label |
|---|---|---|
| Codex | `.codex/config.toml` | `codex` |
| Claude | `.mcp.json` | `claude` |
| AGY | `.agents/plugins/pipeline-team/` | `agy` |

Labels select message routes. They are not cryptographic app or model
attestation, because any process under the same local account can edit local
state.

## 2. Team transport

`pipeline/team.py`, `team_mcp.py`, `team_messages.py`, and `team_store.py`
provide three MCP tools: `team_status` (activity, focus notes, pending
counts, the caller's resume cursor, handoff, and own-sent previews),
`team_send` (bounded text under a sender-scoped idempotency key), and
`team_wait` (messages after a cursor; advancing acknowledges through it, and
skipping unread mail is refused). Fixed semantics live in the tool
descriptions, not in payloads.

Messages, receipts, and notes live in `pipeline-team/messages.sqlite3` under
the Git common directory, so linked worktrees share one queue and nothing is
committed. The store refuses symlinks, replaced inodes, hard links, and
group/world-accessible files, which protects against other OS users and
accidents, not the repository owner. Queued, returned, acknowledged, replied,
and substantively answered are distinct states; none grants authority.

## 3. Repository work

The apps use normal worktrees, files, builds, and tests. `bin/pipeline`
dispatches deterministic commands. `orient` and `status` are read-only
digests; `status` caches validated review state per repository fingerprint,
which `check` and the gate never read. `preflight` checks bindings and
adapter handshakes without launching a model.

## 4. Formal review and admission

`material-behavior` needs one non-author Codex or Claude review;
`high-risk-control` also needs different model families and explicit
abuse-class analysis. The author publishes one exact-range `verify-request`
and the reviewer one bound `verification-report` (GO, NITS, or FAIL), both
through the fixed writer behind `bin/pipeline mail send` into
`coordination/mailbox/sent/`, append-only.

`pipeline/compact_pair_loop.py` validates artifacts, range ancestry,
publisher and model-family bindings, evidence, and supersession.
`pipeline/ci_admission_gate.py` requires exact high-risk coverage for every
commit that touches an authority surface, inspecting every parent diff so a
mailbox-only or restored commit cannot hide a mutation; a merge inherits
coverage only as a byte-clean landing of the reviewed chain. Runtime reviewer
identity is attested by the desktop task, never by repository bytes.

## Authority boundary

Review establishes evidence about code. It never authorizes push, merge,
release, spend, destructive action, or live-data mutation.
