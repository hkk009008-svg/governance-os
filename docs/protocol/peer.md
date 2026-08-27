# Desktop-team communication contract

The filename is retained for stable links. Current communication is the
repository-scoped MCP team transport, not one-shot CLI peer invocation.

## Members and binding

The only interactive members are `codex`, `claude`, and `agy`. Each desktop
app loads one project config that supplies its normal member label:

- Codex: `.codex/config.toml`
- Claude: `.mcp.json`
- AGY: workspace plugin manifest and binding under
  `.agents/plugins/pipeline-team/{plugin.json,mcp_config.json}`

The label comes from adapter args, never from a tool argument. It is not app or
model attestation: the same local account can launch another label or edit the
database. Each adapter serves the same local `pipeline-team` MCP server over
stdio. The server launches no model provider and holds no provider credential.

## Tools

### `team_status`

Returns the caller's configured member label, capabilities, activity
timestamps, pending counts, and recent sent-message acknowledgement/reply state.
Activity is not liveness. The result grants no authority.

### `team_send`

Queues UTF-8 text to another member or `all`. Every call must provide a
non-empty sender-scoped `idempotency_key`; retrying the identical recipient,
body, and `reply_to` reuses it safely, while different content must use a new
key. The sender may link a reply to a message addressed to it, but cannot
address itself, select another label through this tool, or reply to an
unrelated message.

Success means only that the row is queued in the repository-scoped store.

### `team_wait`

Returns messages after an explicit cursor. The same `after_id` replays them;
advancing `after_id` acknowledges addressed messages through that cursor. The
wait is bounded. An empty result means only that this call observed no later
matching message. It is not global absence, refusal, agreement, or authority.
Consumers deduplicate by the stable message id. Cursor acknowledgement is not
a lease or worker election.

## State model

```text
queued
  -> returned by team_wait
  -> acknowledged by a later cursor advance
  -> optional linked reply
  -> human/model judgement that the reply is substantive
```

The arrows are not automatic equivalences. Queue success does not prove
acknowledgement. Acknowledgement does not prove reading or understanding. A reply id does not
prove the question was answered. If a task depends on a response, the sender
must inspect the reply or report the precise missing state.

Broadcast acknowledgement is tracked separately for each recipient. `last_seen` is a
tool-activity observation and cannot prove an app remains open.

## Content contract

Keep messages bounded and actionable. Name the objective, repository evidence
or paths, what response is requested, and whether independent work can continue.
Do not assume the transport includes files, task history, terminal output, or
permission context; cite them explicitly.

All three members may propose direction, implementation, tests, review
findings, and next steps. Material AGY findings are considered and answered on
their merits. AGY remains ineligible to be the sole independent formal verdict
or an authority source.

No message may grant or imply:

- user intent or scope not already present in the task;
- formal author or reviewer acceptance;
- push, merge, release, spend, live mutation, or destructive authority;
- acknowledgement, understanding, or assent that the recorded state does not show.

Routine task-scoped communication is allowed without a new approval and should
not be relayed through the user. Effects named above still require exact
current user/task authority.

## Storage and recovery

`pipeline/team_store.py` places the SQLite database under the Git common
directory, outside tracked files, so linked worktrees share it. The directory
and file must be real, owner-only, single-link objects; permissive modes,
symlinks, and replacement inodes fail closed. This protects against other OS
users and accidental replacement, not the repository owner's account. Messages
are local coordination state, not signatures or attestations.

If configuration or handshake fails, run `bin/pipeline preflight`. If a message
is queued but unacknowledged, continue independent work or wait at a natural
boundary; do not launch a headless provider as a fallback. Legacy files under
`coordination/mailbox/` and `coordination/peer/` remain historical evidence and
are not a fallback conversation transport. The mailbox fixed writer remains
available only for three durable uses: a risk-required formal artifact, a real
checkpoint, or the governed learning-candidate/disposition lifecycle.
