# Pipeline desktop-team architecture

> This file records current repository facts. Executable code wins when prose
> drifts, and stale prose must be corrected with the implementation.

*Last verified against working tree based on: 2026-08-27 @ b1390a24*

## Purpose

Pipeline lets the Codex, Claude, and AGY desktop apps collaborate as one
software-engineering team in a shared Git repository. All three can reason,
direct, implement, test, and challenge. The harness adds a small communication
transport and proportional governance; it does not replace each app's native
workspace, task, browser, or artifact capabilities.

The supported interactive boundary is app-exclusive. Pipeline does not launch
model providers from a shell, invoke another app as a headless child, or use a
human relay. Shell processes serve local MCP and run reproducible repository
commands only.

## Runtime flow

```text
user task
  -> Codex / Claude / AGY desktop app
  -> configured project MCP member label
  -> team_status, team_send, team_wait
  -> direct or delegated repository work
  -> focused tests and exact diff inspection
  -> temporary author/reviewer only if risk requires formal review
  -> separately authorized external effect, if requested
```

Routine work does not declare a seat, publish an event, or create a handoff.
Read-only and nonoverlapping work may run in parallel. Writes to the same path
or mutable resource are serialized through one owner.

## App and transport topology

| Surface | Current responsibility |
|---|---|
| `.codex/config.toml` | Binds the Codex app to `pipeline-team` as member `codex`. |
| `.mcp.json` | Binds the Claude app to `pipeline-team` as member `claude`. |
| `.agents/plugins/pipeline-team/plugin.json`, `mcp_config.json` | Register the AGY workspace plugin and bind `pipeline-team` as member `agy`. |
| `bin/pipeline` and `pipeline/cli.py` | Resolve the repository interpreter and dispatch local harness commands. |
| `pipeline/team.py` | Stable desktop-team entry point; serves one configured member-label adapter. |
| `pipeline/team_mcp.py` | Minimal MCP/JSON-RPC surface exposing the three team tools. |
| `pipeline/team_messages.py` | Validates send, wait, reply, status, cursor, and idempotency behavior. |
| `pipeline/team_store.py` | Secures and initializes the repository-scoped SQLite store. |
| `pipeline/harness_preflight.py` | Checks app bundles, project bindings, and real adapter initialization without launching a model. |
| `pipeline/native_app_readiness.py` | Checks Codex/Claude native config views, Antigravity workspace registration, and AGY's explicit team-tool permission. |
| `pipeline/codex_protocol_model.py` | Defines closed risk profiles, model-family diversity, and external-effect token shape. |
| `pipeline/compact_pair_loop.py` | Binds formal author/reviewer results to an exact committed range. |
| Git, tests, app task history | Normal implementation and continuation state. |
| `coordination/mailbox/` | Historical conversation/cursors plus the fixed durable carrier for required formal-review artifacts, real transfer checkpoints, and the governed learning-candidate/disposition lifecycle. |
| `coordination/peer/` | Compatibility-only peer-launch receipts; never current transport. |

Each app config supplies its normal member label, and the tool schema exposes
no sender argument. This is routing convenience, not provenance: any process
running as the repository owner can launch an adapter under another label or
edit local state. The store is under the repository's Git common directory at
`pipeline-team/messages.sqlite3`, so linked worktrees share one conversation
without tracking message data in commits. Its directory and database are
owner-only, real filesystem objects; symlinks and group/world access are
rejected, as are hardlinks and replacement inodes. The owner-only boundary
protects against other OS users, not the same local account.

## The three tools

`team_status` reports the adapter's configured label, declared capabilities,
pending counts, sent-message acknowledgement/reply state, and recent activity. A
`last_seen` value is activity evidence only, not app liveness or authority.

`team_send` appends one validated message to another member or `all`. Every
call requires a non-empty sender-scoped `idempotency_key`, reusable only for
the identical recipient, body, and `reply_to`; `reply_to` itself is optional.
A successful call means the message is queued.

`team_wait` reads messages after an explicit cursor, optionally waiting for a
bounded interval. The same `after_id` replays the same log slice; advancing the
cursor records acknowledgement of addressed messages through that id. This
client-driven cursor survives process loss between response flush and client
processing without a lease or worker-election layer. Consumers deduplicate by
the stable message id.

These states are deliberately separate:

```text
queued row
  != returned by team_wait
  != acknowledged by a later cursor advance
  != linked reply
  != substantive answer
```

Only an adapter operating under the recipient label can create its acknowledgement
record; that label is not attested against the same local account. A reply link proves that a
response was queued, not that it answered the question; content determines
substance. When work depends on an answer, the sender waits for it or reports
the precise missing state. Every payload explicitly reports that it grants no
authority.

The transport does not carry files, task history, permission approval, review
admission, or effect authority. Members cite repository paths, commits, tests,
and task context rather than assuming a message transferred hidden state.

## Capability routing

The store advertises current strengths, not exclusive jobs:

| Member | Useful emphasis |
|---|---|
| Codex | parallel task orchestration, isolated worktrees, long-running goals, workspace implementation, tests and integrations |
| Claude | large-context reasoning, independent diff review, workspace implementation, tests and visual review |
| AGY | fast mapping and debugging, premise/evasion challenge, isolated implementation, browser/artifact work, multi-model advice |

Any member may lead or implement. Pair capabilities to reduce weakness: ground
long analysis in executable evidence, validate fast advice locally, and put a
different model family over high-risk authored work. Material AGY findings are
answered on their merits, but AGY cannot be the independent formal accepting
verdict or an authority source.

## Governance boundary

`pipeline/codex_protocol_model.py` keeps four closed review profiles:

- `ordinary-local`: focused verification; no formal reviewer.
- `material-behavior`: focused verification plus non-author exact-range review.
- `high-risk-control`: the material requirements plus a different model family
  and an explicit abuse-class assessment.
- `external-effect`: exact live user/task authorization for the effect; a
  structural review does not grant execution.

There are no standing roles. Formal review temporarily names the candidate
owner `author` and a non-author Codex or Claude member `reviewer` for one exact
range. AGY can inspect, challenge, test, and propose remediation, but cannot be
the sole formal reviewer. The responsibility ends with the review.

Push, merge, release, paid spend, live-data mutation, and destructive
operations are separate effects. Each requires exact authority naming executor,
target, effect, and scope. Team traffic, local config, tests, and review results
cannot manufacture that authority.

## State and compatibility boundary

Current truth is the user task plus fresh Git state, executed tests, current
app task history, and any accepted formal exact-range report. A concise
checkpoint is created only when ownership or context really transfers; it is
not a startup ritual or a second task log.

Old mailbox conversations and cursors, capacity packets, peer-launch receipts,
four-seat names, and older handoffs remain historical evidence. Readers and
validators may keep compatibility support for them. The fixed mailbox writer
has exactly three active durable uses: a risk-required exact-range artifact, a
real ownership-transfer checkpoint, or the governed
learning-candidate/disposition lifecycle. It never carries routine team chat,
and no artifact written there creates a live role or authority.

## Readiness and verification

`bin/pipeline preflight` checks all three application bundles, the checked-in
MCP bindings, an initialize handshake for each configured label in a temporary
Git repository, Codex/Claude native config views, Antigravity's exact workspace
registration, and AGY's team-tool permission. These are configuration proxies,
not proof that a desktop window or Antigravity's server connection is live.
The check neither opens an app nor launches a model provider. AGY's optional
interruption-free permission is global and server-name-scoped, not bound to
this repository.

Focused tests are used during implementation. `bin/pipeline check` is the final
repository aggregate when the changed surface warrants it. A green result
proves only the code paths it executed; app liveness, user intent, message
substance, and external authority remain separate claims.
