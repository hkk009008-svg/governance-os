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
hook allows one sequence:

1. one empty `ListAgents`;
2. one exact live address, or one prefix that resolves to exactly one live
   non-self peer;
3. one `SendMessage` whose target, summary, and body match the armed request.

Everything else is denied. The target keeps its displayed `[ref]`; offline,
ambiguous, missing, self, altered, repeated, and `local_*` targets fail closed.
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
`$1.00` ceiling when Codex and Claude need to communicate. The bridge name,
working directory, SDK version, model selection, and executable are not
caller-substitutable. Stop the existing instance instead of starting a
duplicate.

## Five-tool contract

| Tool | Purpose |
|---|---|
| `claude_bridge_start` | Start the named bridge explicitly; budget defaults to and cannot exceed `$1.00`. |
| `claude_bridge_status` | Read bridge state and optionally one relay receipt. |
| `claude_bridge_send` | Lazily start and queue one idempotent exact/prefix relay. |
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

Events live in a bounded ring. If a slow reader falls behind, `truncated=true`
and `dropped_before_cursor` expose the gap without killing the relay. A restart
creates a new generation and rejects old cursors.

## Reply convention

Claude addresses the full native peer name shown by `ListAgents`, for example
`pipeline-codex-bridge [ref]`. Inbound `origin.kind=peer` and
`task-notification` / `peer-send-message` shapes become `peer_message` events.
The SDK body and routing attribution are preserved but labeled routing-only,
not governance identity. Repeated native message IDs are emitted once; reuse
with different content stops the bridge.

For durable or formal work, use `coordination/bin/send-event`, commit the
artifact, and follow the repository's review rules. The relay carries the
request; it does not authorize it.
