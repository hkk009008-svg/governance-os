# Codex and Claude task connector

Pipeline's supported direct cross-app path is a named, persistent Claude Agent
SDK peer owned by Codex. It is intentionally a thin adapter over Claude's
native cross-session messaging, not another task registry or mailbox.

```text
Codex task
  -> project MCP server (local, no provider launch at startup)
  -> persistent Agent SDK session named pipeline-codex-bridge
  -> bridge-side Claude ListAgents observation
  -> exact bridge-visible ref-qualified address
  -> Claude SendMessage

Claude Desktop/Code task
  -> native SendMessage to pipeline-codex-bridge
  -> attributed SDK UserMessage origin
  -> Codex cursor read/wait
```

## Why this is the supported shape

Claude exposes `claude agents --json` for read-only host session inventory and
the Agent SDK for a supported bidirectional, long-lived client. A named SDK session is a
native Claude peer, so an in-app Claude task can message it without GUI
automation. The connector restricts that peer to `ListAgents` and
`SendMessage`, uses `dontAsk`, loads no project/user settings or MCP servers,
does not expose the `Skill` tool, keeps peer traffic on the same machine, and
opts only the unattended bridge into `crossSessionInbound: accept`.

A supported Agent SDK `PreToolUse` hook is the mechanical send gate. With no
outbound Codex relay armed it denies every tool call, including calls prompted
by an inbound peer message. For one armed relay it allows exactly one empty
`ListAgents` call, requires its matching `PostToolUse` completion to contain the
exact requested target, and then allows exactly one `SendMessage` whose `to`,
`summary`, and `message` fields equal the validated request. The pinned Claude runtime
derives compatibility fields `recipient`, `content`, and `type`; the gate
accepts them only when the recipient repeats the exact target, the content is
a true prefix preview of the exact message, and the type is `message`.
Redirected aliases, altered bodies/previews, unknown fields, repeated calls,
and every other tool are denied before execution. A `PostToolUse` hook records
the native `ListAgents`/`SendMessage` tool response before Codex reports it.

Claude Desktop's injected `mcp__ccd_session_mgmt__*` tools are private host
tools, not an external task API. Their `local_*` task IDs do not map through a
supported API to native Claude session UUIDs. Desktop also does not launch Code
tasks with the preview channel flags required for channel push. The connector
therefore rejects those paths instead of depending on them. Native
`SendMessage` is model-only, so the small transport model intermediary is an
irreducible part of this supported design.

## Install and load

Install the separately locked optional runtime in the Python environment used
by the repository:

```bash
coordination/bin/pipeline-python -m pip install -r requirements-connector.txt
```

`.codex/config.toml` registers `coordination/bin/claude-task-connector`. The
wrapper pins the current or primary checkout's `.venv`; it accepts no ambient
Python override. Restart Codex after installing or changing project MCP
configuration.

MCP startup imports only the standard-library connector and performs no Claude
launch, authentication, or spend. Capability and native-session discovery stay
available even before the bridge starts. Missing SDK state is reported with the
exact install remedy.

## Tool contract

| Tool | Effect |
|---|---|
| `claude_connector_capabilities` | Read supported/blocked paths and SDK availability. |
| `claude_list_sessions` | Read the host `claude agents --json` inventory. Its aliases are candidates, not target guarantees. |
| `claude_bridge_start` | Launch the pinned named provider peer. Requires exact authority, `launch_authorized=true`, and a finite explicit per-instance budget. |
| `claude_bridge_status` | Read state, generation, cursor, queue, and error facts. |
| `claude_bridge_list_peers` | Provider effect: call native `ListAgents` once and expose its structured `PostToolUse` result through the event cursor. |
| `claude_bridge_send` | Queue one idempotent relay to either an exact address or a restart-stable prefix that must resolve to one live peer. |
| `claude_bridge_operation_status` | Read scheduling, native-tool, terminal, and no-ack facts for one operation without waiting on its SDK query. |
| `claude_bridge_read` | Read normalized attributed events for an exact bridge generation after a cursor. |
| `claude_bridge_wait` | Wait up to 300 seconds for events in an exact bridge generation after a cursor. |
| `claude_bridge_stop` | Stop the locally owned SDK peer. |

The start latch is caller-asserted and does not create or verify authority.
Provider launch and the maximum spend still need exact user authority for this
connector instance. The MCP surface pins the bridge name, repository cwd,
bundled CLI selection, and SDK-default model; callers cannot substitute an
executable, cwd, name, or model. The SDK budget is finite for one bridge
instance but is not a persistent spend ledger: stop/start and MCP-process
restart create a new budget scope and require fresh authority. The bridge has
bounded event and operation-receipt capacity, bounded message and event sizes,
and a restricted tool surface. Capacity exhaustion stops accepting operations
instead of silently evicting observations or receipts.

## Relay and reply semantics

For outbound traffic, Codex supplies a unique `message_id`, text, optional
`correlation_id`/`in_reply_to`, and exactly one of `target` or `target_prefix`.
An exact target must still exist. A prefix is resolved from the relay turn's
fresh `ListAgents` result and is accepted only when exactly one displayed peer
name begins with it; zero or multiple rows (including duplicate names with
different short refs) refuse the send. A unique prefix resolves to the entire
displayed address, including its bracketed short ref, because native
cross-session `SendMessage` requires that ref-qualified address even when the
display name is unique. This makes a stable role prefix safe across Claude
restart-generated suffix changes without turning it into a guess. Duplicate
IDs with the same payload are
idempotent; reusing an ID with different bytes fails. Targets beginning
`local_` fail before any SDK query. The bridge also refuses its own name and
rows explicitly marked offline, disconnected, or stopped. Run
`claude_bridge_list_peers`, then read or wait for its structured `PostToolUse`
observation and use the exact displayed
address, including a supplied `[ref]`. Host inventory aliases can differ from
the bridge's view and must not be promoted into targets. The bridge re-lists
native peers and asks Claude to pass a deterministic envelope byte-for-byte to
`SendMessage`. Only one discovery or outbound relay may be pending at a time.
Its gate remains armed until the SDK emits that turn's terminal result; another
operation fails closed rather than replacing the first authorization. SDK
queries are scheduled asynchronously, so a stalled query cannot monopolize the
MCP server. A pre-scheduling failure clears the unused arm and permits a safe
retry. A timeout or failure after scheduling quarantines the bridge until
`claude_bridge_stop`; this prevents late native hooks from being misattributed
to a later operation. The failure remains visible in its lifecycle receipt.

`queued_to_bridge` means only that the SDK query was scheduled without blocking
the MCP server. Inspect `claude_bridge_operation_status`: a native
`SendMessage` observation is separated from the tool response's accepted or
rejected result, and native messaging exposes no end-to-end delivery
acknowledgement. Tool-use, tool-result, result, rate-limit, and peer-message
observations remain available through the event cursor so Codex can report what
was actually observed without upgrading it to “delivered.”

Idempotence and event cursors are process-local transient state. A bridge
restart creates a new generation and clears message-ID history; read/wait calls
therefore require that exact generation and reject stale cursors.

`claude agents --json` can show an idle or blocked background task that native
`ListAgents` cannot yet address. Cross-session messaging requires Claude Code
2.1.224 or newer and a bound inbox socket; a task left running on an older
binary remains host-visible but unreachable. The native listing is delivery
truth. Under separate restart/launch authority, use the supported
`claude respawn <id>` command to preserve that task's conversation while moving
it to the current installed runtime, or wake/dispatch it through Claude's
supported app/background-task interface. Wait until native discovery sees it,
then use a new message ID. Never reinterpret host inventory, a queued query, or
a terminal refusal as delivery.

For replies, an in-app Claude task sends natively to
`pipeline-codex-bridge`. The SDK attributes injected traffic with
`origin.kind=peer` or a `task-notification` with
`subkind=peer-send-message`. Depending on the SDK turn shape, that origin can
arrive on `UserMessage` or the peer turn's terminal `ResultMessage`; both become
a first-class `peer_message` event while the result/cost event is preserved.
If the SDK exposes both shapes for one native `msg_id`, the connector emits the
peer message once; reuse of that ID with different attributed bytes fails closed.
The connector prefers the SDK's decoded `body` field when present, preserves
the native routing fields, and explicitly labels them as transient routing—not
governance identity. The receiving Codex task uses `claude_bridge_wait` or
`claude_bridge_read` with the returned generation and cursor.

## Governance boundary

The connector cannot assign Director/Operator, transfer ownership, grant a
permission, authorize an effect, publish a review request/report, or establish
a durable decision. Use `coordination/bin/send-event`, commit, land, and
synchronize for formal or durable cross-provider state. A Claude peer message
can carry a human-readable request to perform those steps; it cannot perform or
authorize them merely by being delivered.
