# AGY (Antigravity) continuation adapter

This adapter is AGY-specific. It does not import, propagate, or translate
Codex, Claude, Cursor, or Antigravity compatibility identity. The cross-provider
doctrine is the source of authority: AGY is advisory/read-only by default.

## Modes

### Default: advisory readiness

`coordination/bin/agy-seat --dry-run <profile>` emits a read-only AGY identity
for inspection. The profile selects a local model and a resolved
`.git/index-agy-<profile>` path only; it does not claim a shared Pipeline seat,
mailbox, cursor, lock, verdict, or fixed-writer authority. Advisory mode never
launches the AGY provider.

### Explicit exception: independent single-model unit

`coordination/bin/agy-seat --mode single-model-autonomous <profile>` is the
only launchable AGY mode. It is an explicitly selected, independently routed
unit, not a Codex/Claude/Cursor `director`, `operator`, or `coordinator` seat.
The launcher namespaces its identity as `agy-unit-<profile>` so it cannot be
mistaken for shared-seat occupancy. Selecting the mode does not itself grant a
provider launch, a write, a review verdict, a mailbox action, or any external
effect; those require their own route and user authority.

## Read-only startup

An advisory AGY session may inspect repository and durable route evidence with
ordinary read-only commands. It does not consume a cursor, create a per-seat
index, publish a mailbox event, claim a lock, or use a shared provider seat.

## Fixed-writer syntax

The fixed writer receives the event body on standard input. This is syntax, not
authorization for AGY to publish:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <subject...> < body.md
```

## AGY launcher mechanics

`coordination/bin/agy-seat` is backed by `scripts/agy_seat_launcher.py` and
uses the AGY-only adapter `scripts/agy_protocol_model.py`. It removes inherited
`CLAUDE_*`, `CURSOR_*`, `CODEX_*`, `ANTIGRAVITY_*`, and `GIT_*` authority before
building a child environment. Ordinary process settings and the narrowly scoped
`AGY_API_KEY` credential may remain. The child receives only controlled
`AGY_SEAT`, `AGY_AGENT_MODE`, `AGY_AGENT_ROLE`, `AGY_BEHAVIOR_SOURCE`,
`AGY_GIT_INDEX_FILE`, and `GIT_INDEX_FILE` values.

Local profile configuration lives at `~/.agy/pipeline-seat-launcher.toml`:

```toml
[seats.director] # local profile label, not a shared Pipeline seat
model = "gemini-2.5-pro"
service_tier = "default"

[seats.director2]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.operator]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.operator2]
model = "gemini-2.5-pro"
service_tier = "default"

[seats.coordinator]
model = "gemini-2.5-flash"
service_tier = "fast"
```

An independent single-model unit must receive a separate, explicit route before
entering another repository. It must not borrow the Pipeline shared mailbox,
cursor, lock, or seat identity.

## Automatic Seat-Task Routing via Subagents

In Single-Model Autonomous Unit mode, AGY sessions dispatch recipient seats (`director`, `operator`, `coordinator`) automatically upon emitting mailbox trigger events (such as `verify-request` or `route`):
1. **Emitter Tooling**: Use `.venv/bin/python scripts/agy_emit.py --to <seat> --kind <kind> --subject <subj> --body <body>` or `invoke_subagent`.
2. **Subagent Execution**: When a next seat is assigned, spawn a background subagent (`invoke_subagent` with `TypeName: "self"`) to execute that seat's verification or edits asynchronously without asking the user to relay prompts.
3. **Reactive Wakeup & Reconciliation**: AGY resumes automatically when the subagent completes. Read the committed mailbox artifact (`coordination/mailbox/sent/`), verify the GO verdict, and issue convergence automatically.

