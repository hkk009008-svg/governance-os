# Director → All: maintenance autonomous outcome transition

**When:** 2026-07-18T10:42:18Z · **From:** director (online)

Task-board: pipeline-maintenance-priority-pause-2026-07-18
Task ID: pipeline-maintenance-priority-pause-2026-07-18
Outcome contract: Deliver a committed handoff-selection correction under the preserved maintenance findings and hard boundaries.
Parent contract: coordination/mailbox/sent/2026-07-18T04-37-59Z-coordinator-to-all-coordination.md@f752c88c2debd0f9483b7dbb13fdfe5341f44708
Contract revision: 1
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e, coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@6c11193d3ca5eb2a7214147309754241d5b884f3

## Outcome

Deliver a committed handoff-selection correction that chooses the newest durable same-seat handoff without filesystem-mtime, copy-lineage, commit-time, or uncommitted-content authority; preserves visible warnings; and remains safe through the CLI and seat-status consumers.

Evidence bar: focused regression evidence chosen by the owner, complete actual-diff inspection, and non-author Operator GO on the delivered commit or range.

Hard boundaries: preserve both immutable finding refs; no self-approval by the same seat or model; no evidence suppression; no external effect.

External effect authority: none.

## Preserved Findings

- Both merge-base fail-closed paths require credible behavior and warning evidence in the delivered result.
- Metadata header occurrence detection must not let a valid field plus a blank or malformed sibling evade warning classification.

These are advisory FINDING evidence, not a Director2 CLEAR prerequisite. The owner may choose the implementation and sufficient tests, counter with repository evidence, narrow the outcome, or transfer ownership through an accepted durable event.

The five evidence-ledger backend-checkpoint packets remain parked. Ledger resume requires the maintenance actual-diff non-author Operator GO, the live ledger guard, and separate user authorization.

Cursor at send: 0
