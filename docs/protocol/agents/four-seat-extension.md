# Four-Seat Compatibility Vocabulary

The shared role IDs are `director`, `director2`, `operator`, and `operator2`,
with `coordinator` and `coordinator2` as cursorless coordination roles. They are
mailbox and review vocabulary, not a staffing or fixed-lane requirement.

## Capacity and ownership

The two Director/Operator pairs provide optional independent capacity. Use only
the roles the accepted work and risk require. Lanes come from the task and
current ownership record, not a permanent global mapping, provider, branch,
environment value, or capacity packet.

Any supported provider may hold a formal role when explicitly assigned through
its adapter. Native helpers remain parent-scoped and do not become roles.
Provider mechanics and ownership are summarized in
[`protocol-assembly-map.md`](../protocol-assembly-map.md).

## Mailbox

The live role and event-kind registry is
[`scripts/protocol_mailbox.py`](../../../scripts/protocol_mailbox.py).

- Direct addressing is point-to-point. `all` is a recipient only.
- Receiving roles consume only their own cursor through the fixed wrapper.
- Coordinators hold no cursor.
- Events stage through `coordination/bin/send-event`; commits are separate.
- Transport ambiguity remains an explicit error.

A committed event preserves scoped protocol state. It never grants push,
merge, spend, provider launch, live-data mutation, or another external effect.

## Shared work and review

Refresh scoped Git state before overlapping edits. First lawful landed work
wins. Cross-owner changes require explicit acceptance or transfer. Delegation
and ownership rules live in [`orchestration.md`](orchestration.md); there is no
mandatory cross-director co-sign or pre-dispatch report.

Material behavior receives exact-range non-author review. Only high-risk
control work adds a different model family and abuse-class assessment.
Coordinators may reconcile evidence but cannot approve authored behavior.

No alternate per-seat index, standing coordinator, mandatory handoff, lock
ritual, or full-suite startup is part of this compatibility layer.
