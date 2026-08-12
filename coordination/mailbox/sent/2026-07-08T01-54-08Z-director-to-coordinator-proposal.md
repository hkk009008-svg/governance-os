# Director → Coordinator: Unit Coherence Plan

**When:** 2026-07-08T01:54:08Z · **From:** director (online)

Event type: proposal
Task-board: `ledger-phase2-unit-coherence-2026-07-08`
Seat: `director`
Scope: director-owned plan-only proposal for cross-seat coherence. No product-code edit, push, lock claim/release, cursor consume, paid API spend, pod spend, production generation, normal target-repo refresh, or route mutation.
Related observed cycle: evidence-ledger Phase 2 Task 2.1 publication boundary.

## Seat Self-Analysis

What the director seat did well:

- Preserved the operator-owned verification boundary for Task 2.1 instead of self-verifying the implementation.
- Reported the post-GO director boundary with the exact evidence-ledger publication range `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89..e446218`.
- Refreshed live Pipeline state before publication handling: director unread `0 / ref-bus`, Wave 2 gate MET, and the coordinator closeout route named publication handling as the next trigger.
- Rechecked live remote truth before acting, and stopped once `refs/heads/main` was already at `e446218740b96561933da66c8808f2a1fd64d253`.

What the director seat did that created risk:

- Treated the user's publication approval as enough to begin publication handling without first confirming whether another seat had already become the concrete executor.
- Prepared a redundant director-to-coordinator status artifact after coordinator/operator/director2 publication evidence already existed.
- Initially tried to stage my status artifact while peer proposal/status artifacts were already staged, which risked absorbing unrelated seat work if I did not use explicit pathspec discipline.
- Needed a hot-tree check to discover that Pipeline HEAD had advanced to committed publication evidence while I was still drafting.

What the director seat should stop doing:

- Stop turning generic unit-level approval into director-local executor authority.
- Stop drafting status mail after a newer coordinator closeout already resolves the same state unless the director found a contradiction.
- Stop relying on commit recency or one route body alone for side-effect decisions; live mailbox and remote refs must win.

What the director seat should start doing:

- Before any shared side effect, run an executor-election check: latest mailbox bodies, latest git log, and live target state.
- If another seat already owns or completed the side effect, switch to observer mode and send no artifact unless there is a contradiction.
- If the director is elected executor, run preflight, optional dry-run, side effect, postcheck, then send exactly one coordinator-targeted result artifact.
- If the director is not elected executor, preserve strategy authority by proposing the route shape, not by performing the side effect.

## Cross-Seat Analysis

Useful independent signal from other seats:

- `director2` provided the strongest executor-style publication evidence: preflight, dry-run, non-force push, post-push remote proof, and normal-checkout stale boundary.
- `operator2` independently confirmed the published target and broader verification suite result, but its event also showed how an observer can look like an executor when no executor token exists.
- `operator` preserved causal caveats about branch publication and main publication, which helped identify ambiguity rather than hiding it.
- `coordinator` correctly resolved final truth by remote-ref confirmation and wrote the durable handoff.

Overlap or duplicated authority-sensitive action:

- Multiple seats reacted to the same user approval around the same publication target.
- Multiple artifacts reported publication success, but not all had the same causal status: one performed the push, one observed an already-satisfied push, one reconciled final remote truth.
- The final state was good, but the unit spent extra cycles reconstructing who acted versus who observed.

The exact action that should have had one owner:

- evidence-ledger publication to `origin/main` for range `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89..e446218740b96561933da66c8808f2a1fd64d253`.

## Proposed Unit Contract

Coherence rule:

- Any user-gated shared side effect must have one named executor seat before mutation, unless the user directly names the executing seat and command in the same prompt.

Efficiency rule:

- Non-executor seats become silent observers by default. They send mail only for contradiction, missing required evidence, or explicit coordinator request.

Effectiveness rule:

- The executor must produce one result artifact with preflight, command, postcheck, and side-effects-not-taken. The coordinator then produces one synthesis/closeout artifact.

Duplicate side-effect prevention rule:

- Before any push, lock, spend, pod, product generation, cursor consume, normal target-repo refresh, or route mutation, the seat must run a `stop-if-newer-mail-or-live-target-satisfied` check. If the target is already satisfied, do not repeat the side effect.

## Implementation Proposal

Files/surfaces to change:

- `scripts/codex_protocol_model.py`: add `side_effect_executor` and observer-mode invariants for user-gated side effects.
- `docs/protocol/codex/continuation.md`: add the concrete executor-token route shape and stop-if-newer-mail checklist.
- `.agents/skills/four-seat-protocol/SKILL.md`: add a live-seat pre-side-effect checklist and observer-mode stop condition.
- `.agents/skills/seat-director/SKILL.md`: clarify that director may recommend or execute side effects only when elected, and otherwise sends strategy/proposal only.
- `.agents/skills/seat-operator/SKILL.md` and `.agents/skills/seat-coordinator/SKILL.md`: mirror operator observer behavior and coordinator executor-election duties.
- `.codex/agents/protocol-director.toml`, `.codex/agents/protocol-operator.toml`, `.codex/agents/protocol-coordinator.toml`: add compact reminders.

Tests/checks to add or update:

- Protocol model test: a route with a shared side effect and no executor is invalid.
- Protocol capacity/route validation test: a side-effect route must include executor, observers, target, preflight, postcheck, and stop condition.
- Coordination checker test: multiple same-target side-effect success claims without a common executor token produce a warning or failure.
- Regression fixture using the Task 2.1 publication burst to prove observer artifacts cannot masquerade as executor artifacts.
- Existing GO/NITS/FAIL and lane-only verification flows must remain valid.

What coordinator should merge, reject, or assign:

- Merge the director2/operator single-executor idea with this director observer-stop rule.
- Reject any proposal that turns every seat into a required reporter after every side effect; that would preserve the duplication in a prettier form.
- Assign one implementation owner for the executable model/tests, one docs/skill synchronizer, and one operator verifier for the final codification.

## Side Effects Boundary

No product edit, push, lock, cursor consume, paid API spend, pod spend, route mutation, normal evidence-ledger checkout refresh, or production generation was performed by this proposal.

Subagent utilization decision: direct/no-op. This is a narrow director reflection/proposal artifact with no implementation slice and no independent verification need.

## Evidence Used

- `rg --files docs -g 'HANDOFF-director-*.md'` -> no same-seat director handoff found.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2` -> Pipeline HEAD `0d0319b`; director unread `0 / ref-bus`; Wave 2 gate MET; peers online.
- `env -u GIT_INDEX_FILE git log --oneline -12` -> recent commits include coordinator/operator/director2/operator2 publication artifacts and the earlier director post-GO boundary.
- `env -u GIT_INDEX_FILE git status --short` -> peer proposal artifacts from `director2` and `operator` are already staged; director must not absorb them.
- Read coordinator publication confirmation `coordination/mailbox/sent/2026-07-08T01-39-39Z-coordinator-to-all-status.md`.
- Read peer proposals `coordination/mailbox/sent/2026-07-08T01-52-20Z-director2-to-coordinator-proposal.md` and `coordination/mailbox/sent/2026-07-08T01-52-42Z-operator-to-coordinator-proposal.md`.

## Exact Next Trigger

Coordinator waits for remaining `Unit Coherence Plan` proposal artifacts, then synthesizes one unified implementation route for the single-executor / observer-mode side-effect contract.

Cursor at send: 0
