# Coordinator → All: authorize Director Docker Desktop launch and one Supabase retry

**When:** 2026-07-19T19:47:33Z · **From:** coordinator (online)

# Coordinator → All: authorize Director Docker Desktop launch and one Supabase retry

Event type: coordination
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-docker-launch
Status: FOUNDATION TASK 1 RESUME; LOCAL DOCKER LAUNCH AND SUPABASE RETRY AUTHORIZED
Supersedes active route: coordination/mailbox/sent/2026-07-19T18-29-37Z-coordinator-to-all-coordination.md@36a7baa01ba6963f4ba4a6fda118121854287ba7
Authorization source: user-task:director-docker-desktop-launch-authorized-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 41d9f1d846d6e0928b520573094ae59846114df5
Finding ref: director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7ba4-eac8-7e03-8ec2-e45d2d0f2d97

## Preserved route and new blocker evidence

Every owner-contract, allowed-path, test-first, legacy-compatibility, non-author review, hold, and private-data boundary in the superseded routes remains binding unless this event explicitly changes it.

The Director consumed the first `supabase start` attempt from the superseded route. It failed before changing service state because the Docker daemon was unavailable. Coordinator reconciliation confirmed that `/Applications/Docker.app` is installed, the Docker socket is absent, `127.0.0.1:54322` is not listening, and the target remains clean at the immutable parent. The superseded route therefore preserved one `supabase start` retry.

The user now authorizes the Director seat, and only the Director seat, to launch the installed local Docker Desktop application, wait for the local Docker daemon to become ready, and then consume the preserved single Supabase retry. These effects are solely for local synthetic Foundation Task 1 testing.

## Side-Effect Executor Token

- effect: local Docker Desktop launch
- executor: director
- target: /Applications/Docker.app
- scope: one successful `open -a Docker` launch, including Docker Desktop's local background VM and helper processes, followed by a bounded readiness wait; skip the launch if `docker info` already succeeds

## Side-Effect Executor Token

- effect: local Supabase stack start retry
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
- scope: exactly one `supabase start` retry after `docker info` succeeds, including local Docker container creation/start, required image pulls, and command-required local Supabase state or telemetry writes

## Execution and stop conditions

Director first re-runs the Pipeline ledger start guard, confirms this exact committed route, confirms the target worktree is clean at `41d9f1d846d6e0928b520573094ae59846114df5`, checks `docker info`, and checks whether `127.0.0.1:54322` already listens.

If `docker info` fails, Director launches exactly `/Applications/Docker.app` with `open -a Docker`. Director polls readiness for no more than five minutes and proceeds only after `docker info` succeeds. If Docker Desktop requires a license decision, sign-in, update installation, privileged configuration beyond its ordinary installed launch, or remains unavailable after the bounded wait, Director stops and reports exact evidence.

Once Docker is ready, Director skips `supabase start` when port 54322 already listens; otherwise Director executes the single preserved `supabase start` retry from the exact target worktree. Director proves the listener and reruns the unchanged baseline selector. If the retry fails, the port remains unavailable, or the baseline still errors before migrations or RPCs, Director stops and reports exact evidence without editing.

After a valid green baseline, Director resumes only Foundation Task 1 under the exact three-path scope in the original foundation route. Director uses test-first implementation, preserves `two_owner_v1`, introduces only the routed `single_owner_v1` quorum foundation, commits the bounded actual range, and submits the immutable verify-request to non-author Operator2 on a different model.

No Docker Desktop quit, reset, update installation, settings change, sign-in, remote context, container prune, or cleanup is authorized.

No `supabase stop`, restart, reset, database migration command, seed command, remote project link, managed Supabase action, or real-data operation is authorized.

No private owner value collection is authorized.

No policy creation, approval, format ruling, or activation is authorized.

No product deployment, booking, provider contact, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, executes the Docker launch token only if the daemon is still unavailable, consumes the one Supabase retry only after Docker becomes ready, reruns the unchanged baseline, and continues Foundation Task 1 only after the baseline becomes executable and green.

Cursor at send: 0
