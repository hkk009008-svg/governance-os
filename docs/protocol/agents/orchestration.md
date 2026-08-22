# Orchestration - agent neutral

Autonomous Seat Outcome Contract: pipeline/codex_protocol_model.py

Delegation is an owner-chosen capacity tool, not a task-count, line-count, or
provider mandate. The owner may work directly, use one bounded helper, split
independently reviewable write sets, or exchange ownership through a durable
accepted event. No third party approves that choice.

Choose delegation when it adds fresh context, independent signal, or genuinely
parallel capacity. Stay direct for tightly coupled, authority-sensitive, or
small changes. Never run concurrent implementers on shared files or behind the
same collision-prone lock.

A helper receives the exact outcome, allowed paths, useful evidence bar,
applicable hard boundaries, immutable finding refs, and forbidden external
effects. It uses `env -u GIT_INDEX_FILE` for ordinary Git, runs kernel tools
through `bin/pipeline` (which clears that variable itself), and preserves
peer/user edits.

Helpers do not inherit role authority. They do not consume cursors, send
mailbox events, issue GO/NITS/FAIL, claim locks, merge, invoke a peer, spend,
or authorize external effects. Their output is evidence for the owning role.

Preflight is advisory. Preserve a material finding, but do not require CLEAR
before implementation. The owner synthesizes the actual result and submits the
committed range. Behavior-changing acceptance requires non-author reviewer
review of the actual range. A different model family and abuse-class assessment
are additionally required for `high-risk-control`. A reviewer cannot verify
anything it authored.

Ownership changes bind the exact task, immutable parent/revision, previous and
new owners, and finding refs through recipient-authored durable acceptance.
No observer is a route-approval or convergence gate.

Use sequential implementation for overlapping write sets. Independent
read-only investigations may run concurrently when they ask distinct questions.

## One mailbox across provider sides

`author` and `reviewer` are provider-agnostic identities. Either supported
side — Claude or Codex — may hold either role, and one review may span the two
CLIs. Work passes between roles, and therefore between providers, through the
same durable surfaces on every side:

- committed mailbox events through the fixed writer, reached by
  `bin/pipeline mail send` (`coordination/bin/send-event`);
- ownership exchange as a durable accepted event of a writable kind —
  `decision`, or `dispatch-claim` for takeover evidence. The older
  `proposal` / `proposal-reply` ownership pair still parses in committed
  history but is no longer publishable (`mailbox_writer.NEW_WRITE_KINDS`);
- a continuity checkpoint (`bin/pipeline checkpoint` drafts one into scratch
  from live evidence) preserves state across a boundary; it is a `findings`
  event and transfers nothing by itself;
- the committed verify-request / verification-report Compact Pair for review.

The receiving role needs no knowledge of which app authored an event; the
committed body and Git state carry everything load-bearing. Cross-provider
review is first-class: an author hosted on one side may assign its
verify-request to a reviewer hosted on another, and the different-model
independence requirement is in practice only satisfiable that way — every
model a Claude session can select is claude-family.

Communication never launches anything. Passing work is publishing an event,
not spawning a process; provider launch stays a separately authorized external
effect on every side.
