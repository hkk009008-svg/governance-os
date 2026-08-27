---
name: seat-coordinator
description: Use for explicit Claude coordinator observation, facilitation, or mediation — a retired position whose work now routes to author or reviewer.
---

# Coordinator: a retired position

Protocol SEMANTICS are canonical in `.agents/skills/seat-coordinator/SKILL.md`;
this file is the intentional Claude-native adaptation, not drift (O2
ruling 2026-07-31, ADR-067 Stage 3a). Where the two disagree on protocol
semantics, the `.agents` side wins and this file is corrected in the same
change.

A review has two positions, `author` and `reviewer`. There is no third party
left to mediate between them, so no task assigns coordinator work any more.
`coordinator`/`coordinator2` stay readable in committed history and are refused
as the sender of any new event; they were always cursorless, as current app
members and temporary formal roles now are.

When a prompt still names coordinator work, say so, then do the work as the
position that owns it:

- Observation, reconciliation, and status reading need no role. Read
  `bin/pipeline status` plus the relevant event bodies and report to whoever asked.
  Diagnostics are evidence only; preflight is advisory.
- A real transfer checkpoint is published by the owning Codex, Claude, or AGY
  app member; its Owner must equal its envelope sender. Checking its existence
  is ordinary observation.
- Formal exact-range artifacts use `author` and `reviewer`; governed learning
  records use app-member identities through `bin/pipeline mail send`. Mediation is
  not a route-approval gate.

Canonical Compact Pair Invariant: pipeline/codex_protocol_model.py

Preserve exact lineage and finding refs. Use `env -u GIT_INDEX_FILE` for
ordinary Git and explicit paths; `bin/pipeline` clears that variable itself.
Push, merge, release, paid spend, live-data mutation, and destructive
operations remain separately authorized. Structural tokens do not grant authority.
