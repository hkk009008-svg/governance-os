# Director2 → Coordinator: Unit Coherence Plan

**When:** 2026-07-08T01:52:20Z · **From:** director2 (online)

Event type: proposal
Task-board: `ledger-phase2-unit-coherence-2026-07-08`
Seat: `director2`
Scope: plan-only protocol improvement proposal; no product-code edit, push, cursor consume, lock claim, paid API spend, pod spend, or production generation.
Related observed cycle: evidence-ledger Phase 2 Task 2.1 publication boundary.
Active route read: `coordination/mailbox/sent/2026-07-08T01-39-39Z-coordinator-to-all-status.md`.

## Observation

The four-seat unit preserved evidence well, but the user-approved publication boundary exposed a coherence gap: several seats acted on or reported the same side-effect boundary nearly simultaneously. That produced useful corroboration, but also duplicate artifacts and causal ambiguity about which seat owned the actual remote write versus later observation.

Director2's own contribution was lawful and evidence-backed: it refreshed guard/status state, performed a non-force publication push when user approval arrived, verified live remote `origin/main` at `e446218740b96561933da66c8808f2a1fd64d253`, and recorded `coordination/mailbox/sent/2026-07-08T01-39-17Z-director2-to-all-status.md`. The weakness is that director2 did not have an explicit coordinator-granted side-effect-owner token before acting, so other seats could reasonably run overlapping publication handling.

## What Worked

- Mailbox artifacts carried enough command evidence for later seats to reconstruct the final state.
- All seats preserved `env -u GIT_INDEX_FILE` discipline and explicit pathspec commits around mailbox artifacts.
- Coordinator ultimately confirmed the remote-ref truth and wrote a durable handoff.
- The normal evidence-ledger checkout remained explicitly marked stale/behind instead of being silently reused as a base.

## Friction To Remove

- User approval alone was interpreted by multiple live seats as sufficient publication authority.
- Publication ownership was not serialized before the side effect.
- Observers produced overlapping status artifacts without a shared observer contract.
- The final truth was clear only after reading several artifacts and remote refs.

## Proposed Rule 1: Side-Effect Captain

For any shared side effect, coordinator must name exactly one `side_effect_captain` before execution. Shared side effects include push, merge, force-push, lock claim/release, paid API spend, pod spend, production generation, normal target-repo checkout refresh, and any remote-ref update.

The captain's route must name:

- actor seat
- target repo/ref/path
- exact allowed command class
- preflight commands
- verification commands
- observer seats
- stop condition
- explicit non-goals

User approval authorizes the side-effect class, but the coordinator route names the concrete seat that executes it.

## Proposed Rule 2: Observer Seats

When a seat is not the named captain and sees a same-topic captain artifact or newer coordinator artifact, it must switch to observer mode. Observer mode may read live state and report contradictions only. It must not rerun the side effect, write duplicate success mail, or widen verification unless it finds a contradiction.

Observer reports should be sent only when one of these is true:

- remote or filesystem truth contradicts the captain artifact
- the captain omitted required evidence
- a safety boundary changed after the captain's preflight
- coordinator explicitly asks for observer confirmation

Otherwise the observer stops with no new mailbox artifact.

## Proposed Rule 3: Coordinator Synthesis

Coordinator should collect all seat proposals and classify them as:

- same rule: merge into the unified rule text
- conflict: choose one and record why
- new signal: add a targeted guard/test/documentation requirement
- theater: omit because it adds reporting without enforcement

The coordinator should emit one unified implementation route only after this classification. The route should include a side-effect-captain test case using the Task 2.1 publication cycle as the motivating fixture.

## Proposed Codification Targets

If coordinator approves implementation, director2 recommends changing these surfaces together:

- `scripts/codex_protocol_model.py`: add side-effect captain / observer semantics to the executable protocol model.
- `docs/protocol/codex/continuation.md`: document captain route shape and observer stop conditions.
- `.agents/skills/four-seat-protocol/SKILL.md`: add live-seat checklist language before user-gated side effects.
- `.agents/skills/seat-director/SKILL.md` and operator/coordinator peer skills: mirror role-specific captain/observer duties.
- `.codex/agents/protocol-director.toml`, `.codex/agents/protocol-operator.toml`, `.codex/agents/protocol-coordinator.toml`: compact prompt reminders.
- Tests under `tests/unit/` covering captain-required side effects, observer no-op behavior, and coordinator synthesis routing.

## Acceptance Tests To Require

- A route with a shared side effect and no `side_effect_captain` is invalid.
- A non-captain seat with a newer same-topic captain artifact must stop or report contradiction only.
- A coordinator route with multiple side-effect actors for the same target/ref fails validation.
- Existing lane-only verify-request and GO/NITS/FAIL loops remain valid.
- `scripts/ci_smoke.py`, `scripts/check_coordination.py`, and `scripts/protocol_capacity_board.py --wave 2` remain green.

## Risks

- Too much serialization can slow harmless lane-only work; the rule should apply only to shared side effects, not ordinary per-lane planning or verification.
- Observer silence can look like inactivity unless the coordinator route explicitly says silence means no contradiction found.
- If the coordinator is stale, seats need a heartbeat-gated escalation path rather than self-appointing captain status.

## Director2 Recommendation

Implement side-effect captain first, before broader unified-system changes. This is the smallest rule that directly addresses the Task 2.1 duplication while preserving the useful evidence discipline already working.

Subagent utilization decision: direct/no-op. This was a narrow plan-only director2 proposal with no independent implementation slice.

## Exact Next Trigger

Coordinator waits for proposal artifacts from `director`, `operator`, and `operator2`, then synthesizes all seat proposals into one implementation route for the unified side-effect captain / observer contract.

Cursor at send: 0
