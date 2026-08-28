# Retired presence files

This directory is retained only so historical references and transferred repositories
remain understandable. Do not create or update per-seat files or heartbeats here.

Current activity belongs to the desktop-team transport:

- `team_status` reports the configured Codex, Claude, and AGY member labels,
  pending messages, and transport timestamps.
- `team_wait` reads messages addressed to the current app member.
- Git state and executed test evidence remain the source of truth for repository work.

An activity timestamp says only that the configured member label touched the local
transport; it does not attest which app or model is open, assign work, or grant
authority. Formal review uses temporary `author` and `reviewer` responsibilities for
one exact committed range. Legacy seat names remain parseable only for old mailbox and
formal-review artifacts.

`SEAT.md.template` is a retired compatibility notice, not a template to instantiate.
