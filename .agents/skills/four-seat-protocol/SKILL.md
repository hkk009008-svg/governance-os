---
name: four-seat-protocol
description: Use in this repo when asked to continue, inspect, hand off, or operate the four-seat director/operator protocol from Codex. Do not use for ordinary feature work unless the user mentions a seat, mailbox, handoff, wave, continuation, readiness, or protocol decision.
---

# Four-seat protocol for Codex

Use this skill to orient, choose the lawful mode, and load the concrete seat
delta. It is a checklist, not a copy of the protocol. The runtime adapter is
`docs/protocol/codex/continuation.md`; the executable lifecycle is
`scripts/codex_protocol_model.py`.

## 1. Choose mode

- **Readiness bridge:** default; inspect and report only.
- **Live seat:** only when the user or parent names `director`, `director2`,
  `operator`, or `operator2`.
- **Coordinator:** only for an explicit reconcile, route, capacity, or gate
  assignment.
- **Subagent:** bounded by its parent; never silently becomes a seat.

Concrete identity controls handoff, mailbox, cursor, event addressing, and Git
index. Behavior source mapping is `director -> director`,
`director2 -> director`, `operator -> operator2`, and
`operator2 -> operator2`.

## 2. Read durable state

User instruction wins. Then use current Git/code, applicable signed ref-bus
facts, relevant mailbox bodies/cursors, locks and executed evidence, same-seat
handoff, and finally cache/defaults. Read bodies rather than deciding from
counts. Refresh HEAD and mail immediately before a protocol decision or write.

## 3. Run the smallest orientation

Run the selected mode's orientation block in
`docs/protocol/codex/continuation.md`; that adapter owns same-seat handoff lookup
and startup commands.

- A readiness bridge reports durable state and blockers only.
- A live seat reads relevant mailbox bodies, then loads its concrete skill:

- Director/director2: `.agents/skills/seat-director/SKILL.md`
- Operator/operator2: `.agents/skills/seat-operator/SKILL.md`
- A coordinator loads `.agents/skills/seat-coordinator/SKILL.md`; the adapter
  makes gate, smoke, and capacity commands conditional on the actual claim.

## 4. Respect shared boundaries

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Apply the authority, mailbox, Git, subagent, and side-effect boundaries in the
continuation adapter. Local consequences: only the concrete live seat may
consume its cursor; only a non-author operator issues GO/NITS/FAIL; coordinator
does not author production fixes; separately gated effects need explicit
authority. Inspect staged scope after any authorized consume or event send.

The model owns pair lifecycle, capacity split, executor tokens, emergencies,
disagreements, blocked waves, and reviewer-result handling. Apply that contract
only when its trigger fires; do not restate it in seat artifacts.

## 5. Keep artifacts proportional

Create a status, route, handoff, receipt, or verdict artifact only when it
changes ownership, carries authority, preserves a real transfer, records an
executed result, or states an actual blocker. Do not create chat-only green
prose or duplicate Lane V for an unchanged commit and question.

Continue the seat/coordinator chain internally until completion, a genuine
blocker, scope expansion, or a separately gated effect. Write a narrow handoff
only at a real transfer/context boundary or explicit request.

## Optional read-only tools

```bash
.venv/bin/python scripts/mailbox_monitor.py --once
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

`scripts/draft_handoff.py <seat> --wave <wave> --smoke --output` may draft a
transfer scaffold; refresh live state before finalizing it. Diagnostics and
gate scripts are evidence, not operator GO.

## Target and reference adapters

- Evidence-ledger route: read `docs/protocol/codex/ledger-cli-adoption.md`
  before leaving Pipeline. Do not start ledger work from Content.
- Codex mechanics: `docs/protocol/codex/continuation.md`
- Lifecycle and triggered contracts: `scripts/codex_protocol_model.py`
- Universal doctrine: `docs/protocol/agents/`
- Folder ownership: `docs/protocol/protocol-assembly-map.md`
