# Coordinator → All: route four-item coordination friction cleanup

**When:** 2026-07-21T01:21:34Z · **From:** coordinator (online)

Task-board: pipeline-coordination-friction-delta-2026-07-21
Task ID: pipeline-coordination-friction-delta-2026-07-21
Status: ACTIVE — FOUR-ITEM SIMPLIFICATION ROUTE
Route generation: 8
Supersedes route: coordination/mailbox/sent/2026-07-20T23-19-55Z-coordinator-to-all-coordination.md
Expected control HEAD: 7b16985e74201fe572e32c132f2678c498aa5c65
Superseded route ref: coordination/mailbox/sent/2026-07-20T23-19-55Z-coordinator-to-all-coordination.md@00ff5a7af8f4beea3ea119165d358da592b92eca
Authorization source: user-task:approved-coordination-friction-cleanup-2026-07-21; user-task:include-fourth-item-2026-07-21
Accepted lineage repair GO: coordination/mailbox/sent/2026-07-21T00-02-40Z-operator2-to-all-verification-report.md@bdf4372819f20a2040f829ed56fb5fd21da9680b
Accepted Packet 2 GO: coordination/mailbox/sent/2026-07-21T01-15-02Z-operator2-to-all-verification-report.md@7b16985e74201fe572e32c132f2678c498aa5c65
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Outcome Contract

Reduce the four observed coordination frictions with one small standard-library-only patch:

1. reject autonomous route candidates whose committed parent, task identity, or revision arithmetic is inconsistent before publication;
2. make fast resume resolve from the same complete route graph already used by global lineage;
3. prove the complete consumer path for known cross-task ancestry, unknown parents, sibling forks, and later unrelated successors;
4. make task monitoring use one explicit fallback sequence: wait with cursor, one bounded thread snapshot only when the wait handler is missing or unavailable, then bounded immutable Git/mailbox reconciliation without redispatch.

This route does not create a registry, broker, monitoring service, new event type, package, framework, or additional approval ceremony.

## Director Autonomous Contract Revision 9

Before any implementation edit, Director publishes exactly one fresh director-to-all coordination event through the fixed writer and commits only that event. It uses:

- Task ID: pipeline-coordination-friction-delta-2026-07-21
- Outcome contract: Implement and verify the four-item coordination-friction delta exactly within this route, then submit the one-commit actual range to Operator2.
- Parent contract: this committed generation-8 Coordinator route's exact path at its full commit SHA
- Contract revision: 9
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: the full immutable refs of this route, the accepted lineage-repair GO, and the accepted Packet 2 GO

Director proves the contract effective and global route lineage valid before production edits. A child implementer is outside scope; Director owns all files.

## Target Allowed Paths

- scripts/protocol_capacity.py
- scripts/ledger_start_guard.py
- scripts/codex_protocol_model.py
- tests/unit/test_protocol_capacity.py
- tests/unit/test_ledger_fast_resume.py
- tests/unit/test_protocol_prompt_sync.py
- AGENTS.md
- .agents/skills/seat-coordinator/SKILL.md
- docs/protocol/codex/continuation.md

## Exact Implementation Contract

### 1. Parent-aware route preflight

Extend the existing G7 route validator; do not add a second validator.

For an autonomous pair-seat candidate:

- retain the current structural checks;
- if Parent contract is none, require Contract revision 0;
- otherwise load that exact committed parent through the existing RouteBatchReader proof path and require an effective parent, identical Task ID, and Contract revision equal to parent revision plus one;
- report each mismatch as a clear G7 issue before publication;
- keep proposal, acceptance, ownership-evidence, and final committed-effectiveness checks in their existing authoritative implementation; this preflight grants no route authority.

Pin valid parent continuity plus unknown/unreadable parent, task mismatch, and revision mismatch. Do not require the candidate itself to be committed, because this validator is intentionally used before publication.

### 2. One complete graph for fast resume

In _select_resume_task, preserve exact expected-ref loading first, but pass reader.load_all_routes() to resolve_task_routes instead of the task-prefiltered list. Preserve task-scoped malformed-candidate diagnostics.

Do not change global lineage semantics or add a second resolver. Preserve load_task_routes for compatibility unless removal is independently proved safe.

### 3. Consumer-level lineage matrix

Add one production-path fast-resume regression matrix, using committed synthetic routes and the real build_resume path:

- known cross-task ancestor: FAST RESUME remains eligible;
- genuinely unknown legacy parent: FULL ORIENTATION REQUIRED;
- known sibling fork at an ancestor edge: FULL ORIENTATION REQUIRED;
- ordinary later cross-task successor after the selected legacy base: FAST RESUME remains eligible.

The existing route_lineage unit controls remain unchanged and green. These cases must prove the consumer, not only the pure resolver.

### 4. One monitoring fallback

Update the executable protocol model and its existing thin Codex surfaces only.

- Begin with wait_threads and preserve its per-target cursor.
- A normal timeout continues wait_threads with that cursor.
- Only a missing or unavailable wait handler permits exactly one bounded read_thread(turnLimit=1, includeOutputs=false) snapshot of the same task.
- After that one snapshot, reconcile progress at bounded cadence from immutable Git/mailbox artifacts; do not repeat thread snapshots.
- Monitoring failure never redispatches, creates a replacement task, changes seats, or asks the user to relay the trigger.
- If both the one snapshot and immutable artifact reconciliation are unavailable or ambiguous, preserve the dispatch identity, perform at most one normal discovery refresh, and report one tooling blocker.

Pin canonical-model and surface synchronization. Do not add executable polling code, a daemon, journal, service, dependency, or claimed test coverage of the external Codex handler.

## Frozen Boundaries

Preserve coordination/bin/send-event, scripts/mailbox_writer.py, the protocol writer lock and security checks, route effectiveness/ownership policy, side-effect token semantics, target binding, cursor state, and all historical mailbox bytes.

This route authorizes exactly one local Pipeline implementation commit in the nine paths above and one immutable verify-request commit. Stage explicit pathspecs only; preserve peer state.

Target-main integration authority for evidence-ledger Packet 2: none.
Remote-reference publication authority: none.
Network and dependency-installation authority: none.
Service, managed data, private-data, provider, deployment, booking, and spend authority: none.
Cursor and protocol-lock authority: none.
Reset, rebase, amend, squash, revert, and cleanup authority: none.

## Verification And Review

Before committing, and again on committed implementation bytes, run focused RED/GREEN selectors plus:

- tests/unit/test_protocol_capacity.py
- tests/unit/test_ledger_fast_resume.py
- tests/unit/test_protocol_prompt_sync.py
- tests/unit/test_route_lineage.py
- scripts/route_lineage.py --root . --check
- scripts/ci_smoke.py
- git diff --check
- exact nine-path manifest and clean-state checks

Create exactly one local implementation commit with subject:

fix(protocol): unify route and task fallback checks

Director then publishes one immutable verify-request assigned to Operator2 for the exact one-commit implementation range after the Director contract. It binds every RED/GREEN control, the four consumer cases, parent-aware validator outcomes, canonical wait wording, exact manifest, author/reviewer identities, and all frozen boundaries. Director dispatches the existing compatible Operator2 task exactly once and stops.

Operator2 independently reviews the actual commit and is the only seat authorized to issue GO, NITS, or FAIL. No later GO grants integration, remote publication, cleanup, cursor, lock, network, service, private-data, provider, deployment, booking, or spend authority.

## Exact Next Trigger

Director reads this committed generation-8 route, publishes and proves the exact revision-9 autonomous contract, performs the one-commit TDD implementation, proves every gate on committed bytes, publishes the immutable request, dispatches Operator2 once, and stops for its verdict. Any lineage, RED-evidence, scope, test, smoke, manifest, or clean-state failure returns to Coordinator with Pipeline preserved.

Cursor at send: 0
