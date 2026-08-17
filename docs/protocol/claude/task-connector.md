# Codex and Claude task connector

Pipeline's direct cross-app path is one Codex-owned Claude Agent SDK session
named `pipeline-codex-bridge`:

```text
Codex -> local MCP -> named SDK peer -> ListAgents -> SendMessage -> Claude
Claude -> SendMessage -> named SDK peer -> attributed event -> Codex
```

It uses Claude's supported SDK and native peer tools. It does not use Desktop
private RPC, `local_*` task IDs, transcript scraping, GUI automation, or local
socket injection.

## Boundary

The peer can use only `ListAgents` and `SendMessage`. An SDK `PreToolUse`
hook allows one listed-peer sequence:

1. one empty `ListAgents`;
2. only when that result has no live peer rows, one registration-lag retry;
3. one exact live address, or one prefix that resolves to exactly one live
   non-self peer;
4. one `SendMessage` whose target, summary, and body match the armed request.

Everything else is denied. The target keeps its displayed `[ref]`; offline,
ambiguous, missing after the retry, self, altered, repeated, and `local_*`
targets fail closed.
For a reply, `reply_to_message_id` instead derives the exact UDS target from
the stored provider-attributed sender, refuses an unverified or shared socket,
and permits one matching `SendMessage` without consulting `ListAgents`.
Socket existence is not a liveness proof; the receipt still reports no
end-to-end acknowledgement.
`PostToolUse` records the native response before it is exposed to Codex.

The connector is transport only. It cannot assign a seat, grant authority,
publish durable evidence, or issue GO/NITS/FAIL. Native `SendMessage` has no
end-to-end acknowledgement, so a queued request or observed native send is
never reported as delivered.

## Install and start

```bash
coordination/bin/pipeline-python -m pip install -r requirements-connector.txt
coordination/bin/claude-task-connector capabilities
coordination/bin/claude-task-connector mcp
```

`.codex/config.toml` starts the MCP server through
`coordination/bin/claude-task-connector`. MCP startup itself launches no
provider. The first `claude_bridge_send` lazily starts the named peer; an
explicit `claude_bridge_start` is available for diagnostics.

The user's standing authority permits one bridge instance with a hard
per-instance `$1.00` ceiling when Codex and Claude need to communicate. The bridge name,
working directory, SDK version, model selection, and executable are not
caller-substitutable. Stop the existing instance instead of starting a
duplicate.

## Five-tool contract

| Tool | Purpose |
|---|---|
| `claude_bridge_start` | Start the fixed named bridge explicitly. |
| `claude_bridge_status` | Read bridge state and optionally one relay receipt. |
| `claude_bridge_send` | Queue one listed-peer relay, or reply to an attributed inbound message. |
| `claude_bridge_wait` | Read or wait by generation/cursor and optionally include the relay receipt. |
| `claude_bridge_stop` | Stop the locally owned bridge. |

`send` returns a generation and `after_cursor`. Pass both to `wait`; include
the `message_id` as `operation_id` when a summarized receipt is useful.
`timeout_seconds=0` is a non-blocking read, so separate list-peers, read, and
operation-status tools are unnecessary.

Only one relay may be pending. The model re-lists peers for that relay, and the
gate stays armed until its terminal SDK result. A stalled or failed operation
quarantines the bridge until `stop`, preventing late hooks from being
attributed to a later message. Duplicate message IDs with identical payloads
are idempotent; reuse with different bytes fails.

A newly bound native socket can take several seconds to appear in another
session's registry. Therefore an initial `No reachable agents` during startup
means not-ready, not absent. Confirm that exactly one named bridge process or
socket exists, allow the bounded second listing, and refuse only if that retry
still cannot resolve the target. Never answer registration lag by starting a
second bridge.

Events live in a bounded ring. If a slow reader falls behind, `truncated=true`
and `dropped_before_cursor` expose the gap without killing the relay. A restart
creates a new generation and rejects old cursors.

## Reply convention

Codex replies with `reply_to_message_id` so the connector uses the inbound
sender attribution rather than guessing a rotating display name. A new
conversation may still address the full native peer shown by `ListAgents`.
Inbound `origin.kind=peer` and
`task-notification` / `peer-send-message` shapes become `peer_message` events.
The SDK body and routing attribution are preserved but labeled routing-only,
not governance identity. Repeated native message IDs are emitted once; reuse
with different content stops the bridge.

For an end-to-end test, the receiver echoes the sender's probe token and native
message ID, and the sender returns an attributed acknowledgement. Display
names and bracketed refs are routing hints that rotate on restart; the echoed
native message ID is the cross-side evidence that the exact payload was read.

For durable or formal work, use `coordination/bin/send-event`, commit the
artifact, and follow the repository's review rules. The relay carries the
request; it does not authorize it.
