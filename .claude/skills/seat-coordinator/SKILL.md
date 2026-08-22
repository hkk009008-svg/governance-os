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
as the sender of any new event; they were always cursorless, as both live roles
now are.

When a prompt still names coordinator work, say so, then do the work as the
position that owns it:

- Observation, reconciliation, and status reading need no role. Read
  `pipeline status` plus the relevant event bodies and report to whoever asked.
  Diagnostics are evidence only; preflight is advisory.
- Confirming that each owning role's checkpoint `findings` event exists at a
  wrap belongs to the reviewer (`seat-operator`), which notes a gap as a finding
  and never authors the checkpoint itself — its Owner must equal its envelope
  sender.
- Anything that changes durable state is authored by `author` and reviewed by
  `reviewer`, through `pipeline mail send`. Ownership becomes effective through
  the recorded owner/recipient lineage, not through a third party's approval.

Canonical Compact Pair Invariant: pipeline/codex_protocol_model.py

Preserve exact lineage and finding refs. Use `env -u GIT_INDEX_FILE` for
ordinary Git and explicit paths; `bin/pipeline` clears that variable itself.
Merge, locks, consume, provider launch, ledger resume, and spend remain
separately authorized. Structural tokens do not grant authority.
