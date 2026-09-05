# Team message contract

The stable filename is retained for links. Current communication uses the
repository-scoped MCP transport.

The interactive members are `codex`, `claude`, and `agy`. Their project
bindings fix the normal local label; labels are routing conveniences, not
cryptographic app or model attestation.

- `team_status` reports configured identity, capabilities, pending counts, and
  recent sent-message previews (up to 256 UTF-8 bytes each), with acknowledgement,
  reply, and marker metadata. `team_status(message_id=<id>)` reads one own sent
  message in full, including older messages; it cannot read another member's
  sent message or advance inbound acknowledgement. Activity is not liveness.
- `team_send` queues bounded UTF-8 text and requires a sender-scoped
  idempotency key. Success means queued only.
- `team_wait` returns messages after an explicit cursor. Advancing the cursor
  acknowledges addressed messages through it; acknowledgement is not
  understanding.

A linked reply proves that a response was queued, not that it answered the
question. Read it. An empty wait proves only that the call observed no later
matching message.

Messages should name the objective, relevant paths or commits, observed facts,
and requested response. They do not transfer hidden files, task history,
permissions, formal review responsibility, or effect authority.

The SQLite store lives under the Git common directory with owner-only,
non-symlinked state. This protects against other OS users and accidental
replacement, not the repository owner. Run `bin/pipeline preflight` for binding
or handshake failures.
