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
- They cannot publish. `pipeline/mailbox_writer.py` admits exactly `author` and
  `reviewer` as the sender of a new event, so a coordinator envelope is refused
  before publication.
- They were always cursorless, and now both live roles are too. Never consume a
  coordinator cursor and never invent a coordinator receipt.

When a prompt still names coordinator work, say so, then do the work as the
position that owns it:

- Observation, reconciliation, and status reading need no role at all. Read
  `pipeline status` plus the relevant event bodies and report to whoever asked.
- Confirming that each owning role's checkpoint `findings` event exists at a
  wrap belongs to the reviewer (`seat-operator`), which notes a gap as a finding
  and never authors the checkpoint itself — a checkpoint's Owner must equal its
  envelope sender.
- Anything that changes durable state is authored by `author` and reviewed by
  `reviewer`. Mediation was never a route-approval gate: ownership becomes
  effective through the recorded owner/recipient lineage, not through a third
  party's approval.

Commit, event publication, cursor consumption, merge, lock action, provider
launch, spend, and live-data mutation remain separate authorities.

## Rule maintenance
Observed failure: a coordinator authoring a checkpoint (Owner must equal the
envelope sender), and the position surviving in prose after the writer stopped
accepting it as a sender.
Mode/risk: any prompt that still names coordinator. Cost: one sentence naming
the retirement before doing the work as author or reviewer.
Owner: whoever received the prompt.
Re-evaluate: if a coordinator-sent event is ever accepted for publication.
