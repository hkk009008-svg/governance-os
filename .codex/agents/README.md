# Optional Agent Selection Matrix

The core role agents are `protocol-director`, `protocol-operator`,
`protocol-coordinator`, `lane-v-verifier`, `money-gate-reviewer`, and
`readiness-bridge`.

These agents do not replace protocol-director, protocol-operator, or protocol-coordinator.

Use the optional `agentNN` files only when the parent prompt explicitly names
one or when a parent seat wants a bounded helper with that shape:

| Agent | Use For | Do Not Use For |
|---|---|---|
| `agent01` | Mailbox-aware, capacity-minded continuation when all-seat awareness is the main need | Live seat authority, operator GO, cursor consume, push, locks, or spend |
| `agent02` | A concrete protocol worker after the parent names `director`, `director2`, `operator`, `operator2`, `coordinator`, or `readiness` | Seatless work that would silently choose a role |
| `agent03` | General senior repo work that must stay readiness-aware and protocol-bound | Replacing a specialized role agent for an authoritative route or verification verdict |
| `agent04` | Read-first protocol hygiene, routing advice, stale-index diagnosis, and capacity preparation | Authoritative coordinator routing or production fixes |

When seat authority is required, choose the matching core role agent instead.
Subagents remain bounded helpers: they do not consume cursors, send mailbox
events, issue GO, route coordinator work, push, claim locks, start pods, or
spend paid API budget.
