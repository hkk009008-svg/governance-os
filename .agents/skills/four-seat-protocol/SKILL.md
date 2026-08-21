---
name: four-seat-protocol
description: Use for an explicit Pipeline seat, mailbox, handoff, wave, continuation, or protocol decision.
---

# Pipeline role protocol

Choose readiness bridge, assigned live role, coordinator, or parent-scoped
subagent from the explicit prompt. Do not infer a live role.

Use the executable seam that owns the claim:

- `pipeline/codex_protocol_model.py` for identity, ownership, work mode, risk
  profile, and external-effect shape.
- `pipeline/compact_pair_loop.py` for formal exact-range review.
- `pipeline/mailbox_writer.py` through `coordination/bin/send-event` for
  publication.
- `docs/protocol/codex/continuation.md` for host task routing.

For an assigned role, orient once from current evidence:

```bash
python pipeline/status.py snapshot <seat>
```

Read relevant event bodies before deciding. The mailbox is the configured
coordination transport (`governance.toml` `[coordination]`); a signed-bus
cutover is an explicit reviewed transport change, and malformed configuration
fails closed — transport ambiguity fails visibly. Only the assigned live role consumes its
cursor; coordinator has no cursor. Use `coordination/bin/send-event` and
`coordination/bin/consume-events`, never raw mailbox or cursor edits.

Select the product-work phase through `docs/protocol/work-modes.md` separately
from the review risk. Ordinary Explore work does not instantiate seats or
formal review artifacts. A real transfer, frozen Validate candidate, Promote
boundary, or explicitly assigned role activates only the seats that boundary
needs. Work mode grants no role or external-effect authority.

Role deltas:

- Director owns accepted implementation and submits the actual committed range.
- Operator may implement or independently review, but never reviews authored
  work; only the assigned reviewer issues GO/NITS/FAIL.
- Coordinator observes, reconciles, and mediates without becoming a production
  author or approval gate.
- Readiness bridge reports state without claiming work.
- Subagents return bounded evidence to their parent. They do not publish
  live-role events or verdicts, consume cursors, claim locks, push, merge,
  launch providers, or spend.

Apply the risk-based review policy in `AGENTS.md`. When formal review is
triggered, keep the complete committed Compact Pair binding.

Use the worktree's native Git index, preserve peer work, and stage explicit
paths. External effects remain separately authorized. For evidence-ledger work,
read `docs/protocol/codex/ledger-cli-adoption.md` before entering the target
repo.
