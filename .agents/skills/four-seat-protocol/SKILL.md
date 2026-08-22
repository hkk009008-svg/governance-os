---
name: four-seat-protocol
description: Use for an explicit Pipeline seat, mailbox, handoff, wave, continuation, or protocol decision.
---

# Pipeline role protocol

A review has two positions, `author` and `reviewer`, and they are the only
identities a new durable event may come from. Take one only when the user or
parent explicitly assigns it. Do not infer a live role. The six retired seat
names (director, director2, operator, operator2, coordinator, coordinator2)
still parse so committed history stays readable; the fixed writer refuses them
as the sender or the recipient of anything new.

Use the executable seam that owns the claim:

- `pipeline/codex_protocol_model.py` for identity, ownership, work mode, risk
  profile, and external-effect shape.
- `pipeline/compact_pair_loop.py` for formal exact-range review.
- `pipeline/mailbox_writer.py` behind `pipeline mail send` for publication.
- `docs/protocol/peer.md` for reaching the other CLI.

For an assigned role, orient once from current evidence:

```bash
pipeline status
```

Read relevant event bodies before deciding. `pipeline mail send` is the only
write path into the durable mailbox and fails closed on a retired sender, a
retired recipient, or a conversational kind. Both roles are cursorless, and
nobody edits a raw event or cursor file.

Select the product-work phase through `docs/protocol/work-modes.md` separately
from the review risk. Ordinary Explore work instantiates no role and no formal
review artifact; a real transfer, a frozen Validate candidate, a Promote
boundary, or an explicit assignment activates only what that boundary needs.
Work mode grants no role or external-effect authority.

Role deltas:

- Author owns accepted implementation and submits the actual committed range.
- Reviewer may implement or independently review, but never reviews authored
  work; only the assigned reviewer issues GO/NITS/FAIL.
- A readiness-bridge session reports state without claiming work.
- An advisory peer — `pipeline peer ask`, AGY included — supplies evidence
  without becoming a production author or approval gate.
- Subagents return bounded evidence to their parent. They do not publish
  live-role events or verdicts, consume cursors, claim locks, merge, launch
  providers, or spend.

Apply the risk-based review policy in `AGENTS.md`; when formal review is
triggered, keep the complete committed Compact Pair binding. Use the worktree's
native Git index, preserve peer work, and stage explicit paths. External
effects remain separately authorized. For evidence-ledger work, read
`docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.
