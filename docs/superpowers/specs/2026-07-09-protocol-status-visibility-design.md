# Protocol Status Visibility Design

## Goal

Make the protocol startup and standby loop easier to operate without creating
new mailbox/status ceremony.

## Context

The audit found five useful optimizations:

- integrate the already-reviewed `agent-toml-consolidation` branch;
- provide one read-only all-seat status command;
- downgrade monitor alert noise when the cycle is closed and unblocked;
- mechanize newest same-seat handoff selection;
- preserve the no-op boundary when all seats are standby.

`main` currently has the TOML consolidation plan and spec, but not the
implemented `AGENT_EXTENSION_ROUTING_CONTRACT`. The completed branch
`agent-toml-consolidation` contains the implementation and verification, while
`main` has one newer governance commit (`5302951`) that must remain preserved.

## Design

### Agent TOML Consolidation Integration

Merge the completed `agent-toml-consolidation` branch into the new
`protocol-status-visibility` worktree branch. The merge must preserve the newer
`main` SHA-baseline quieting work and the consolidation branch's executable
model, prompt tests, prompt TOMLs, and architecture anchor refresh.

### All-Seat Status

Extend `.agents/skills/four-seat-protocol/scripts/seat_status.py` with
`--all`. It remains read-only and prints one consolidated orientation:

- HEAD and `origin/main` divergence once;
- recent commits once;
- mailbox cursor/unread summary for every receiving seat;
- pair-seat heartbeat summary;
- optional wave gate output;
- capacity board next-action/stop-condition lines when `--wave` is supplied;
- optional latest same-seat handoff line for each seat.

The single-seat path must keep its current output shape enough that existing
startup guidance remains valid.

### Monitor Alert Downgrade

Keep all mailbox monitor facts visible, but classify receipt-unknown and stale
heartbeat as notes instead of alerts when all of the following are true:

- all seats have unread `0`;
- the capacity board for the requested wave is closed and has no blocking
  issues;
- `check_coordination.py` passes.

Unread mail, unconsumed broadcast receipts, active/open packets, or coordination
failures still produce alerts. The monitor remains read-only.

### Latest Handoff Helper

Add `scripts/latest_handoff.py <seat>` to select the newest canonical
same-seat handoff:

- live seats use `docs/HANDOFF-<seat>-*.md`;
- coordinator seats use `docs/HANDOFF-coordinator-*.md`;
- concrete seat identity wins over behavior source;
- near-matches that do not satisfy the canonical pattern are reported as
  warnings, not selected.

Integrate this helper into `seat_status.py` as a short read-only line; a
missing canonical handoff is reported explicitly.

### No-Op Boundary

The new helpers must not send mail, consume cursors, stage files, claim locks,
push, start pods, or spend API budget. The all-seat status and monitor
downgrade should make standby clearer, not generate new artifacts.

## Acceptance

- Existing protocol smoke stays green.
- Prompt-sync tests stay green after the TOML integration.
- New tests prove `seat_status.py --all` is read-only and renders every
  receiving seat.
- New tests prove monitor downgrade preserves facts while moving closed-cycle
  receipt/heartbeat noise out of `alerts`.
- New tests prove `latest_handoff.py` selects only canonical same-seat files
  and warns on noncanonical near-matches.
- No mailbox, cursor, or coordination event files are created or changed by the
  new read-only commands.
