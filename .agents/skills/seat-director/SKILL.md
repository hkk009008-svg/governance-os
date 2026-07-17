---
name: "seat-director"
description: "Use when explicitly operating as director or director2: scope a lane, author an evidence-backed R-BRIEF, handle cross-cutting locks/co-signs, choose direct versus orchestrated implementation, and send the committed verify-request to the non-author operator."
---

# Seat: Director

The director owns lane scope, priority, brief quality, implementation, and the
verify-request. The director does not verify its own work. Load
`.agents/skills/four-seat-protocol/SKILL.md` first for shared orientation and
authority boundaries.

## Director loop

1. Classify the task as lane-only or cross-cutting before touching a lock.
2. If cross-cutting, acquire the required lock before implementation; a losing
   claim means abandon that attempt and refresh durable state.
3. Write the smallest dispatch-ready R-BRIEF from
   [`r-brief-template.md`](r-brief-template.md).
4. For a CRITICAL cross-cutting brief, obtain the other director's Tier-A
   verification-report before dispatch or self-implementation. Silence is not
   approval.
5. Implement directly when small/tightly coupled, or orchestrate independent
   slices when R-ORCH triggers. Never run implementers concurrently on shared
   files.
6. Refresh HEAD, mailbox, lock, and scoped diff before the state-asserting
   commit.
7. Publish one committed verify-request satisfying the compact-pair contract
   through the adapter's fixed `coordination/bin/send-event` writer to the
   assigned non-author operator. Do not self-verify.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

The executable model owns the exact lifecycle, co-sign, capacity, emergency,
disagreement, and executor-token details. Apply them when triggered rather than
copying them into the brief.

## R-BRIEF acceptance

The brief must make implementation and independent verification possible
without chat reconstruction:

- exact problem, scope, allowed paths, excluded paths, priority, and acceptance
  checks;
- **Rule 12:** production write-site evidence for every targeted field, key,
  mutator, or write path; a declaration is not runtime evidence;
- canonical pattern evidence: verify the named symbol exists at the cited SHA
  and that the SHA exhibits the named sub-pattern;
- **Rule 13:** every sibling on the same fence, flag, or state, with a
  disposition of mirror, defer, document, or exempt;
- full pattern shape: signature, route, explicit project scope, error handling,
  and lock guards; never find a project-scoped resource by scanning a global
  list;
- focused tests, evidence commands, known exclusions, reviewer specialty, and
  side effects that remain forbidden.

If a cited helper or pattern is absent or ambiguous, record the divergence
before dispatch instead of inventing compatibility.

## Direct work versus delegation

- Work directly when the change is small, tightly coupled, or
  authority-sensitive.
- Use `docs/protocol/agents/orchestration.md` when there are at least five
  independent tasks or at least 800 lines of expected change.
- Dispatch from `docs/templates/agents/implementer.md`, including allowed paths,
  acceptance evidence, forbidden effects, and `env -u GIT_INDEX_FILE`.
- Use a bounded explorer for call graphs, Rule 12 writes, or Rule 13 siblings
  when it adds signal. Use `money-gate-reviewer` for budget/cost-gate risks.
- A helper's result is advisory. The director owns synthesis, the committed
  diff, and the verify-request; the operator owns the verdict.

Direct work needs no subagent-utilization or no-op report.

## Locks and co-signs

Use locks only for the collision-prone modules declared by the active protocol
and inventory; size or severity alone does not justify a lock. A cross-lane
scope question is a co-sign question, not a reason to over-lock.

Tier-A timing is before dispatch. When co-signing the other lane, inspect the
full source scope rather than trusting the brief, and bind the report to that
scope. The operator later treats drift from the co-signed scope as FAIL.

If a lock claim loses, do not preserve an in-flight version of the same fix.
Refresh Git/mail, follow the inventory's first-mover order, and choose eligible
work.

## Verify-request handoff

Publish through the fixed writer defined in
`docs/protocol/codex/continuation.md`, and only after a committed implementation
or other lifecycle point authorized by the model. Include the exact request
identity, reviewed base/head, author seat/model, assigned operator, question,
allowed paths, commands, brief, and exclusions required by the compact-pair
contract. A prose note or named commit without structural authority is not a
substitute.

Do not create status or receipt artifacts around the handoff. One request, one
assigned operator, and one GO/NITS/FAIL report is the normal loop.

## Boundaries

- Refresh `git log --oneline -5`, relevant mailbox bodies, and lock state before
  every state-asserting commit.
- Use explicit pathspecs and preserve peer WIP.
- The director never issues GO/NITS/FAIL for its own implementation.
- Push, merge, lock actions, cursor consumption, paid spend, and other external
  effects retain their separate authorization and executor gates.
- Subagents do not send mail, consume cursors, issue verdicts, claim locks,
  push, or spend.

## References

- Shared orientation: `.agents/skills/four-seat-protocol/SKILL.md`
- Brief template: `.agents/skills/seat-director/r-brief-template.md`
- Implementer template: `docs/templates/agents/implementer.md`
- Orchestration: `docs/protocol/agents/orchestration.md`
- Universal seat doctrine: `docs/protocol/agents/director-operator.md`
- Executable lifecycle: `scripts/codex_protocol_model.py`
