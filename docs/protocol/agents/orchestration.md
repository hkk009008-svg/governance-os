# Orchestration - agent neutral

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py

Delegation is an owner-chosen capacity tool, not a task-count, line-count, or
provider mandate. The owner may work directly, use one bounded helper, split
independently reviewable write sets, or exchange ownership through a durable
accepted handoff without coordinator approval.

Choose delegation when it adds fresh context, independent signal, or genuinely
parallel capacity. Stay direct for tightly coupled, authority-sensitive, or
small changes. Never run concurrent implementers on shared files or behind the
same collision-prone lock.

A helper receives the exact outcome, allowed paths, useful evidence bar,
applicable hard boundaries, immutable finding refs, and forbidden external
effects. It uses `env -u GIT_INDEX_FILE` for ordinary Git and pytest and
preserves peer/user edits.

Helpers do not inherit seat authority. They do not consume cursors, send
mailbox events, issue GO/NITS/FAIL, claim locks, push, merge, start pods, spend,
or authorize external effects. Their output is evidence for the owning seat.

Preflight is advisory. Preserve a material finding, but do not require CLEAR
before implementation. The owner synthesizes the actual result and submits the
committed range. Behavior-changing acceptance requires non-author Operator GO
from a distinct seat and different model; that Operator cannot verify anything
it authored.

Ownership changes bind the exact task, immutable parent/revision, previous and
new owners, and finding refs through recipient-authored durable acceptance.
Coordinator may facilitate but is not a route-approval or convergence gate.

Use sequential implementation for overlapping write sets. Independent
read-only investigations may run concurrently when they ask distinct questions.

## One mailbox across provider sides

Seat names are provider-agnostic identities. Any side — Claude, Codex, AGY, or
Cursor — may hold any seat, and the standing pair may span two different apps.
Work passes between seats, and therefore between providers, through the same
durable surfaces on every side:

- committed mailbox events through the fixed writer
  (`coordination/bin/send-event`; Cursor app seats use their bound wrappers);
- ownership exchange through a durable accepted handoff
  (`scripts/draft_handoff.py` drafts one from live evidence);
- the committed verify-request / verification-report Compact Pair for review.

The receiving seat needs no knowledge of which app authored an event; the
committed body and Git state carry everything load-bearing. Cross-provider
review is first-class: a Director hosted on one side may assign its
verify-request to an Operator hosted on another, and the different-model
independence requirement is often easiest to satisfy that way.

Communication never launches anything. Passing work is publishing an event,
not spawning a process; provider launch stays a separately authorized external
effect on every side.
