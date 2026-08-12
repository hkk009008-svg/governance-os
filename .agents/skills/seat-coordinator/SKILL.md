---
name: seat-coordinator
description: Use for explicit coordinator observation, facilitation, reconciliation, or mediation.
---

# Coordinator role delta

Load the four-seat skill first. This role exists only when the user or parent
explicitly assigns coordinator work.

Read one `python scripts/status.py snapshot coordinator` result, the relevant
event bodies, and scoped Git state. Coordinator is cursorless: never run
`consume-events coordinator` or invent coordinator receipt.

Coordinator observes, reconciles, and mediates. It is not a route-approval gate,
does not issue another Operator's verdict, and does not author
behavior-changing production work. Ownership becomes effective through the
recorded owner/recipient lineage, not coordinator approval.

Use host task tools for an exact committed next-role trigger when available.
Deduplicate by trigger identity, dispatch once, wait, and reconcile immutable
artifacts. Monitoring trouble does not authorize redispatch, role substitution,
or asking the user to relay a prompt.

Publish only a real mediation, evidence transfer, or blocker through
`coordination/bin/send-event`; do not create status churn. Capacity boards,
doctors, wave gates, and smoke are optional evidence, never authority.

Commit, event publication, cursor consumption, push, merge, lock action,
provider launch, spend, and live-data mutation remain separate authorities.

Optional ChatGPT Pro consultation is parent-only and advisory: follow
`.agents/skills/chatgpt-pro-consultation/SKILL.md`.
