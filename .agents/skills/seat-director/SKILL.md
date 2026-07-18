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

The executable model owns the exact lifecycle and the compact trigger contracts
below. Apply them when triggered rather than copying them into the brief.

## Model-backed contract capsule

Mailbox decisions remain body-first: read relevant mailbox bodies before acting; live seat cursors are intentional per-seat state, and the coordinator has no cursor.
The verifying operator must be a non-author and alone issues GO/NITS/FAIL from repository evidence.
The coordinator may route and reconcile but not author behavior-changing production fixes.
Push, merge, paid spend, and every other side effect are separately gated and require explicit authority.

Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Ask whether the route yields two independently reviewable deliverables.
- If yes, director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- Otherwise Pair B performs bounded planning or preflight instead of idle standby.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types; coordinator owns convergence.

After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete. This is a working choice, not a standalone artifact.

Side-Effect Executor Token:

- Required fields include `side_effect_id`, `allowed_command_class`, and `stop_if_newer_mail_or_live_target_satisfied`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode; report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.
- live evidence may close an already-satisfied side effect without appointing a redundant executor.
- multiple same-target side-effect success claims need a common side_effect_id.

Triggered exceptions stay narrow: Production-affecting OR user-data-integrity issue, Security-critical, Active bleed-rate, or External time-pressure. The first-noticer claims initial response, uses stop-the-bleed first, and records acting under v5 §E temporary authority when applicable; the coordinator no-production-code boundary remains in force and resolution gets a post-incident note. A disagreement States the disagreement explicitly, uses project-data-grounded evidence, and chooses counter-refinement, defer to v(N+1), or an acceptance criterion; silent-accept is the receiver's own acceptance and the 2-cycle escalation limit routes persistence to the user.

Reviewer output uses findings-first ordering by severity, must preserve verdict, findings, and next steps, and must separate uncertainty, inference, and follow-up. do not auto-fix after a review; failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.

Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.
At a real stop, state the blocking boundary or plain next authority without a prescribed heading or returning seat commands to the user.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.

## R-BRIEF acceptance

The brief must make implementation and independent verification possible
without chat reconstruction:

- exact problem, scope, allowed paths, excluded paths, priority, and acceptance
  checks;
- **Rule 12:** production write-site evidence for every targeted field, key,
  mutator, or write path; a declaration is not runtime evidence;
- canonical pattern evidence: brief-pattern references are runtime claims when
  they cite canonical sites; verify the named symbol exists at the cited SHA and
  verify the cited SHA exhibits the named sub-pattern;
- **Rule 13:** audit-completeness is not audit-disposition; enumerate every
  sibling on the same fence, flag, or state, use
  `mirror / defer / document / exempt`, and state the disposition for each sibling;
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
