# Presence files

Each concurrently-running seat publishes a **presence file** here (`<seat>.md`) and a
**heartbeat** (`<seat>-heartbeat.ts`, an ISO-8601 timestamp written each loop). Together
they let any other seat answer "who is online, what are they doing, and is their view of
the tree stale?" without interrupting them — signal via artifacts, not chat.

- **Presence files are runtime state**, regenerated every cycle. They are gitignored
  (see the repo `.gitignore`); only `SEAT.md.template` and this README are committed.
- Copy `SEAT.md.template` to `<your-seat>.md` and keep it current as you work.
- A presence file is a **snapshot** — a peer can come online mid-session. Trust git
  (`git log`), the mailbox, and the coordinator inventory over any presence prose.

## Seat names

The protocol is specialization, not hierarchy — N seats, one team, all serving the
user-principal. A common layout is two pairs plus an on-demand coordinator:
`director` / `operator` (Lane-1) and `director2` / `operator2` (Lane-2), with
`coordinator` spawned at multi-pair-wrap boundaries for read-only cross-pair audit.
Adapt the seat set to `<PROJECT>`.

See `docs/protocol/` for the full seat doctrine and `coordination/README.md` for the
mailbox + event-bus mechanics.
