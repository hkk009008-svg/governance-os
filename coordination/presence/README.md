# Presence files

Presence is an **optional, manually maintained** convenience. A seat may publish a
**presence file** here (`<seat>.md`) and, if it chooses, a **heartbeat**
(`<seat>-heartbeat.ts`, an ISO-8601 timestamp) so other seats can ask "who is online
and what are they doing?" without interrupting them. There is **no automatic heartbeat
loop and no lifecycle hook that writes these** — the hooks that once stamped them are
retired. Absence of a presence file or a stale heartbeat therefore means nothing on its
own; it is not evidence a seat is offline.

- **Presence files are runtime state** and are gitignored (see the repo `.gitignore`);
  only `SEAT.md.template` and this README are committed.
- Copy `SEAT.md.template` to `<your-seat>.md` and update it by hand while you work.
- A presence file is a **snapshot**, not authority. Trust git (`git log`), the mailbox,
  and the coordinator inventory over any presence prose. `scripts/mailbox_monitor.py`
  can still read a heartbeat if one exists, but treats missing/stale as unknown.

## Seat names

The protocol is specialization, not hierarchy — N seats, one team, all serving the
user-principal. A common layout is two pairs plus an on-demand coordinator:
`director` / `operator` (Lane-1) and `director2` / `operator2` (Lane-2), with
`coordinator` spawned at multi-pair-wrap boundaries for read-only cross-pair audit.
Adapt the seat set to `<PROJECT>`.

See `docs/protocol/` for the full seat doctrine and `coordination/README.md` for the
mailbox + event-bus mechanics.
