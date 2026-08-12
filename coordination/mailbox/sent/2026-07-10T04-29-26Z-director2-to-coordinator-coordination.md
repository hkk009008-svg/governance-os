# Director2 → Coordinator: Task 3 identity repreflight CONTRADICTION

**When:** 2026-07-10T04:29:26Z · **From:** director2 (online)

DISPOSITION: CONTRADICTION — route-changing; this is not Operator GO.

Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `director2-control-plane-authority-foundation-identity-repreflight`
Active route:
`coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
Reviewed Task-3 surfaces: `e9ad5bee34aa14fea556901780490f720bbcc4d6`
Hot-tree HEAD before report: `c10654b`; the reviewed design, plan, route, and
packet are unchanged from `e9ad5be`.

Director2 performed the routed read-only sufficiency pass only. Two bounded
read-only helpers independently audited Tasks 3A-3B and 3C-3D; both returned
CONTRADICTION. Director2 re-read the cited sources and owns this synthesis.

## Findings

1. **CRITICAL — runtime eligibility and executable-token authority do not
   compose for signed-ref/remote publication.** The global constraint requires
   both gates before authoritative-ref or remote-publication mutation
   (`plan:23-25`). Task 3A grants `SIGNED_FACT_EMIT` but omits it from the
   token-required set (`plan:439-478`). It makes `REMOTE_PUBLISH` token-only
   with no default actor and tests that `operation_is_allowed()` remains false
   (`plan:468-503,670-678`), while `authorize_operation()` takes no token and
   the token verifier takes no runtime identity/operation
   (`plan:509-527,548-550`). Task 3C token-parameterizes route/lock/cursor
   operations but not `scripts/seat_emit.py` (`plan:925-965`), even though that
   command defaults `--remote origin` and appends the signed ref
   (`scripts/seat_emit.py:145-189`). Task 3D token-gates only protected-main
   update, not chief/overseer/CI ref publication (`plan:1022-1063`). Add one
   cumulative authorization API, exact signed-fact/remote-publication token
   disposition, CLI wiring, and zero-ref-mutation denials.

2. **HIGH — canonical doctor-gate inclusion is structurally incomplete.**
   Task 3B creates `test_codex_session_binding.py` and Task 3C creates
   `test_runtime_operation_guards.py`, but neither write set includes
   `scripts/codex_protocol_model.py` or a commitment to register those suites
   (`plan:774-787,915-923`). Task 3D says to add
   `test_service_principals.py` to the model-derived doctor gate, yet its write
   set also omits the model (`plan:1013-1020,1057-1063`). The production
   selector lives only in `scripts/codex_protocol_model.py:467-479`; Task 3A
   names only its identity suite for registration (`plan:553-555,746-747`).
   Add exact write ownership and registration for the executor-token,
   session-binding, runtime-guard, and service-principal suites, plus matching
   ledger-bridge assertions.

3. **HIGH — narrow-only policy and supported-subagent role contracts remain
   unpinned.** Current executable truth distinguishes supported spawned roles
   and read-only verifier defaults
   (`scripts/codex_protocol_model.py:127-133,846-925`). The revised matrix
   collapses every subagent to one actor with `REPOSITORY_MUTATE`
   (`plan:435-438,480-489`), while tests cover pair role families and mode/seat
   topology but not each supported spawned role or each policy's
   default/narrow/widen/unknown/conflict matrix (`plan:581-668`). The prose
   requires subset narrowing without literal token vocabularies/default maps or
   serialization grammar (`plan:716-720`). Pin frozen per-role policy maps and
   independent exhaustive tests.

4. **HIGH — the mechanical-principal interface is not exact.**
   `MechanicalPrincipal` exposes one `executor_token_required` boolean, yet
   `merge-gate` has token-free evaluation and token-required protected-main
   update. Task 3D supplies neither an operation-specific token map, exact
   signer map, nor resolver/authorizer signatures
   (`plan:1022-1046,1057-1063`). Pin those interfaces and
   candidate-environment semantics before dispatch.

Confirmed sufficient: pair role-family matching; the frozen field inventory;
strict session-ID/no-follow/atomic-no-replace binding; primary-worktree
interpreter; path-aware PreToolUse plus hook-self zero-mutation;
route/lock/human-cursor/signed-cursor token-denial matrix; sequential GO
boundaries; and named RED/GREEN/non-vacuity flips.

No code/doc edit, implementation, Operator GO, cursor consume, lock, key, ref,
route, push, checkout refresh, spend, pod, generation, or other user-gated side
effect was taken.

## Exact Next Trigger

Coordinator revises the Task-3 plan/write sets/interfaces and reroutes
`director2-control-plane-authority-foundation-identity-repreflight` for one
focused re-preflight. This report does not cancel the separate Task-2 or
Operator2 lanes.

Cursor at send: 0
