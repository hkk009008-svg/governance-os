# Coordinator → All: authorize one existing database-container start and resume Foundation Task 1

**When:** 2026-07-19T19:53:49Z · **From:** coordinator (online)

# Coordinator → All: authorize one existing database-container start and resume Foundation Task 1

Event type: coordination
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-db-container-start
Status: FOUNDATION TASK 1 RESUME; ONE LOCAL DATABASE-CONTAINER START AUTHORIZED
Supersedes active route: coordination/mailbox/sent/2026-07-19T19-47-33Z-coordinator-to-all-coordination.md@73fbd79011e73256552e0c8fe70c3880ed70fbe5
Authorization source: user-task:director-existing-supabase-db-container-start-authorized-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 41d9f1d846d6e0928b520573094ae59846114df5
Finding ref: director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7bec-3279-7303-b3b7-b5e538317ab8

## Preserved route and recovery evidence

Every owner-contract, allowed-path, test-first, legacy-compatibility, non-author review, hold, and private-data boundary in the superseded routes remains binding unless this event explicitly changes it.

The prior Docker Desktop launch token completed. The prior `supabase start` retry token was consumed and failed because the existing local stack was stale; neither token is renewed here. Read-only inspection established that all local Supabase containers exited together, PostgreSQL was accepting connections immediately beforehand, the database container reports `OOMKilled=false`, its named data volume remains attached, and the target worktree remains clean at the immutable parent.

Task 1's focused tests require only PostgreSQL on local port 54322. The user now authorizes the Director seat, and only the Director seat, to start exactly the existing database container and then rerun the unchanged baseline.

## Side-Effect Executor Token

- effect: existing local Supabase database-container start
- executor: director
- target: docker-container:supabase_db_evidence-ledger
- scope: exactly one `docker start supabase_db_evidence-ledger` command against the existing container and attached named volume; skip the command if the container is already running

## Execution and stop conditions

Director first re-runs the Pipeline ledger start guard, confirms this exact committed route, confirms Docker is ready, confirms the target worktree is clean at `41d9f1d846d6e0928b520573094ae59846114df5`, and reads the exact container and port state.

If the database container is still exited, Director executes exactly `docker start supabase_db_evidence-ledger` once. Director waits conditionally for no more than two minutes for the container health check and local port 54322. If the command fails, the container exits again, health does not become healthy, or the port stays closed, Director stops and reports exact inspect/log evidence without any second mutation.

After database health and port readiness are proved, Director reruns the unchanged baseline selector. If the baseline errors before migrations or RPCs or is otherwise non-green, Director stops and reports the exact evidence without editing.

After a valid green baseline, Director resumes only Foundation Task 1 under the exact three-path scope in the original foundation route. Director uses test-first implementation, preserves `two_owner_v1`, introduces only the routed `single_owner_v1` quorum foundation, commits the bounded actual range, and submits the immutable verify-request to non-author Operator2 on a different model.

No second `docker start` attempt is authorized.

No other container start, stop, restart, removal, prune, cleanup, or volume mutation is authorized.

No `supabase start`, stop, restart, reset, database migration command, seed command, remote project link, managed Supabase action, or real-data operation is authorized.

No private owner value collection is authorized.

No policy creation, approval, format ruling, or activation is authorized.

No product deployment, booking, provider contact, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, starts only the existing database container if still necessary, proves database readiness, reruns the unchanged baseline, and continues Foundation Task 1 only after the baseline becomes executable and green.

Cursor at send: 0
