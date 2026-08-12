# Coordinator → All: authorize Director local synthetic-stack start and resume Foundation Task 1

**When:** 2026-07-19T18:29:37Z · **From:** coordinator (online)

# Coordinator → All: authorize Director local synthetic-stack start and resume Foundation Task 1

Event type: coordination
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-service-start
Status: FOUNDATION TASK 1 RESUME; LOCAL SYNTHETIC STACK START AUTHORIZED
Supersedes active route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:director-local-supabase-start-authorized-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 41d9f1d846d6e0928b520573094ae59846114df5
Finding ref: director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7b78-dc93-7b10-943a-62f93b2a1abd

## Preserved route and blocker evidence

Every owner-contract, allowed-path, test-first, legacy-compatibility, non-author review, hold, and private-data boundary in the superseded route remains binding unless this event explicitly changes it.

The Director established a clean target at the immutable parent, then observed 39 fixture-setup errors because `127.0.0.1:54322` refused connections before migrations or RPCs executed. The target remained untouched. This is an environmental prerequisite failure, not an executable TDD RED and not a product-code defect.

The user now authorizes the Director seat, and only the Director seat, to start the target worktree's local synthetic Supabase stack for Foundation Task 1 testing. If the database port is already listening when the Director resumes, the Director skips the start and reruns the unchanged baseline.

## Side-Effect Executor Token

- effect: local Supabase stack start
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
- scope: one successful `supabase start` for local synthetic tests, including local Docker container creation/start, required image pulls, and command-required local Supabase state or telemetry writes; a retry is allowed only when an earlier attempt was prevented before service state changed

## Execution and stop conditions

Director first re-runs the Pipeline ledger start guard, confirms this exact committed route, confirms the target worktree is clean at `41d9f1d846d6e0928b520573094ae59846114df5`, and checks whether `127.0.0.1:54322` already listens.

Director executes `supabase start` from the exact target worktree only when the port is not listening. After the command, Director proves the local database is listening and reruns the unchanged baseline selector. If the stack cannot start, the port remains unavailable, or the baseline still errors before migrations or RPCs, Director stops and reports exact evidence without editing.

After a valid green baseline, Director resumes only Foundation Task 1 under the exact three-path scope in the superseded route. Director uses test-first implementation, preserves `two_owner_v1`, introduces only the routed `single_owner_v1` quorum foundation, commits the bounded actual range, and submits the immutable verify-request to non-author Operator2 on a different model.

No `supabase stop`, restart, reset, database migration command, seed command, remote project link, managed Supabase action, or real-data operation is authorized.

No private owner value collection is authorized.

No policy creation, approval, format ruling, or activation is authorized.

No product deployment, booking, provider contact, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, executes the bounded service-start token if still necessary, reruns the unchanged baseline, and continues Foundation Task 1 only after the baseline becomes executable and green.

Cursor at send: 0
