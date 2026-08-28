---
name: seat-coordinator
description: Use for explicit coordinator observation, facilitation, reconciliation, or mediation — a retired position whose work now routes to author or reviewer.
---

# Coordinator: a retired position

Load the four-seat skill first. A review has two positions, `author` and
`reviewer`. There is no third party left to mediate between them, so no task
assigns coordinator work any more.

What is mechanically true today:

- `coordinator` and `coordinator2` remain lawful identities for READING
  committed history. `pipeline/protocol_mailbox.py` keeps them in the receiving
  roster so existing events still parse.
- They cannot publish. `pipeline/mailbox_writer.py` admits `author`/`reviewer`
  for formal artifacts and Codex/Claude/AGY app identities for checkpoints and
  learning records, so a coordinator envelope is refused before publication.
- They were always cursorless, and now both live roles are too. Never consume a
  coordinator cursor and never invent a coordinator receipt.

When a prompt still names coordinator work, say so, then do the work as the
position that owns it:

- Observation, reconciliation, and status reading need no role at all. Read
  `bin/pipeline status` plus the relevant event bodies and report to whoever asked.
- A real transfer checkpoint is published by the owning desktop app member;
  its Owner must equal its envelope sender. Checking whether it exists is
  ordinary observation, not a reviewer responsibility.
- Formal exact-range artifacts use `author` and `reviewer`; governed learning
  records use app-member identities. Mediation is not a route-approval gate.

Push, merge, release, paid spend, live-data mutation, and destructive
operations remain separate authorities.

## Rule maintenance
Observed failure: a coordinator authoring a checkpoint (Owner must equal the
envelope sender), and the position surviving in prose after the writer stopped
accepting it as a sender.
Mode/risk: any prompt that still names coordinator. Cost: one sentence naming
the retirement before doing the work as author or reviewer.
Owner: the app member that received the prompt.
Re-evaluate: if a coordinator-sent event is ever accepted for publication.
