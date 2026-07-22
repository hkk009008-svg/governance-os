# Coordinator → All: resume Task 6 after SQL GO and authorize Auth gate

**When:** 2026-07-22T00:20:15Z · **From:** coordinator (online)

Task-board: ledger-beta-task6-final-acceptance-2026-07-22
Task ID: ledger-beta-task6-final-acceptance-2026-07-22
Program board: ledger-one-user-local-beta-2026-07-21
Status: ACTIVE — INTEGRATE REVIEWED SQL PREREQUISITE, RUN AUTH-AVAILABLE TASK 6 GATE ONCE, AND OBTAIN FINAL OPERATOR2 VERDICT
Route generation: 32
Supersedes route: coordination/mailbox/sent/2026-07-21T23-27-42Z-coordinator-to-all-coordination.md
Superseded route ref: coordination/mailbox/sent/2026-07-21T23-27-42Z-coordinator-to-all-coordination.md@52c8c4e4ae0a0ff5fd363353b3658a68c8645272
Expected control HEAD: 6a07885773f1aed1cfc2a18dc85e1633fdb21bb1
Authorization source: user-task:authorized-both-2026-07-22; user-task:proceed-task6-2026-07-22; user-authorized-continuation-through-local-beta
Task 6 aggregate blocker: coordination/mailbox/sent/2026-07-21T23-08-21Z-director-to-coordinator-coordination.md@a049264d2cbecada0bea2e1ff8334e95cbf20491
SQL prerequisite effective child: coordination/mailbox/sent/2026-07-21T23-37-06Z-director2-to-all-coordination.md@88a861aae4e1f464e80033c4db60a14c6ef91107
SQL prerequisite verify-request: coordination/mailbox/sent/2026-07-21T23-53-22Z-director2-to-operator-verify-request.md@e5008f9acb759ca61925a2a661dc2a292e597461
SQL prerequisite GO: coordination/mailbox/sent/2026-07-21T23-59-46Z-operator-to-all-verification-report.md@6a07885773f1aed1cfc2a18dc85e1633fdb21bb1
Reviewed SQL prerequisite commit: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Reviewed SQL prerequisite tree: 29101e73cec459ef2b91bfdf36f1860505b9e8c5
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
Target branch: codex/beta-task6-local-acceptance
Target base before integration: 171617635a7043ad5814edcc250cda3bc3474f75
Accepted target HEAD before integration: 171617635a7043ad5814edcc250cda3bc3474f75
Required post-integration HEAD: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Task 6 focused review base: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Cumulative milestone review base: b9547db4e47c2d867f7f4c3168e55df33c6d2fa9
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra
Task 6 plan: /Users/hyungkoookkim/evidence-ledger/docs/superpowers/plans/2026-07-17-ppl-offer-task6-acceptance.md
Task 6 input-plan SHA-256: 8dc1806fc7e672a7ccd63d7590d6ec659f28d44435f28461b58a410711ac3799
Frozen PPL API SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6
Frozen Selling Package API SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Approved one-user design SHA-256: d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208
Approved owner-center plan SHA-256: 8fad121fdc3888155fae06867d5524d4c347bbf29d8ba83e3cd39991195e6f8f

## Coordinator Disposition

The immutable one-path SQL prerequisite has non-author Operator GO. The only remaining aggregate failures were the two auth-posture probes that stopped before their assertions because 127.0.0.1:54321 was unavailable under the earlier service-lifecycle prohibition.

The user now authorizes both exact local effects: fast-forward only the reviewed prerequisite commit into the preserved Task 6 branch, and temporarily start the evidence-ledger Auth/Kong runtime for the existing probes and final Task 6 cycle before restoring the prior stopped state.

No target-main integration or remote publication follows.

## Outcome Contract

Fast-forward the preserved Task 6 branch to the reviewed prerequisite commit without touching its allowed untracked WIP. Start only Auth and Kong while preserving the existing healthy database container. Prove both auth-posture tests, restart the complete corrected Task 6 acceptance sequence once, synchronize one-user/manual_only truth, create exactly one Task 6 commit, obtain one immutable Operator2 GO, NITS, or FAIL, restore Auth/Kong, and report the reviewed local state.

## Director Autonomous Contract Revision 33

Before target mutation or service lifecycle, Director publishes exactly one fresh director-to-all coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-beta-task6-final-acceptance-2026-07-22
- Outcome contract: integrate the reviewed SQL prerequisite, execute the Auth-available Task 6 acceptance once, create the one Task 6 commit, obtain Operator2 verdict, and restore Auth/Kong
- Parent contract: this committed generation-32 Coordinator route exact path at its full commit SHA
- Contract revision: 33
- Previous owners: none
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: this route, the Task 6 blocker, the SQL prerequisite verify-request, and SQL prerequisite GO

Director proves the child effective, capacity route validation true, global route lineage valid, Pipeline smoke green, and the ordinary Director ledger start guard bound to that exact child. Each negative shared-effect boundary in the child begins on its own line with exactly `No `.

## Exact Fast-Forward Contract

Before integration, prove the Task 6 branch HEAD is exactly 171617635a7043ad5814edcc250cda3bc3474f75, its tracked index and tracked diff are empty, and only the route-authorized Task 6 create-only WIP is untracked. Prove the prerequisite parent, tree, subject, and one-path range match the immutable GO.

Execute exactly from the Task 6 worktree:

`env -u GIT_INDEX_FILE git merge --ff-only 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0`

Postcheck HEAD equals the reviewed prerequisite commit and the untracked Task 6 manifest is unchanged. Any mismatch stops without reset, stash, rebase, or conflict resolution.

## Side-Effect Executor Token

- effect: git merge
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance branch codex/beta-task6-local-acceptance
- scope: fast-forward only exact reviewed commit 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0 from exact parent 171617635a7043ad5814edcc250cda3bc3474f75; preserve the authorized untracked Task 6 WIP; no target-main, other branch, conflict resolution, history rewrite, or remote ref change

## Exact Auth/Kong Lifecycle Contract

Fresh pre-state:

- `supabase_db_evidence-ledger` is Up and healthy.
- `supabase_auth_evidence-ledger` is Exited.
- `supabase_kong_evidence-ledger` is Exited.
- Every other named local Supabase service is stopped or absent.
- No listener exists at 127.0.0.1:54321.

After the fast-forward, execute exactly from the Task 6 worktree:

`supabase start --exclude analytics,db,edge-runtime,functions,imgproxy,inbucket,meta,realtime,rest,storage,studio,vector`

Use existing local images only. Stop if the command requests download, network access, reset, migration, seed, or broader action. Prove with `docker ps -a`, `supabase status`, and the 54321 listener that only Auth and Kong changed to running while the same database container remains healthy. If another stopped container starts, restore only that newly changed container, preserve the database, and publish a blocker.

Run `db/tests/test_auth_posture.py -q` first and require both assertions pass. Keep Auth/Kong running through Director acceptance and Operator2 review.

After the committed Operator2 verdict, execute exactly:

`docker stop supabase_kong_evidence-ledger supabase_auth_evidence-ledger`

Prove both authorized containers Exited, 54321 has no listener, the same database container remains Up and healthy, and no other service state changed. Restore this pre-state after an earlier blocker too, once no in-flight review needs the runtime.

## Side-Effect Executor Token

- effect: local Supabase service start
- executor: director
- target: supabase_auth_evidence-ledger and supabase_kong_evidence-ledger for /Users/hyungkoookkim/evidence-ledger
- scope: run only the exact exclusion-bound supabase start command from the Task 6 worktree using existing local images; preserve supabase_db_evidence-ledger and every other service; no reset, migration, seed, network acquisition, managed service, or configuration change

## Side-Effect Executor Token

- effect: local Supabase service stop
- executor: director
- target: supabase_kong_evidence-ledger and supabase_auth_evidence-ledger for /Users/hyungkoookkim/evidence-ledger
- scope: after final verdict or earlier blocker, stop exactly the two authorized containers and prove restoration; conditionally stop only a newly started unexpected evidence-ledger Supabase container to restore pre-state; never stop, restart, reset, or mutate supabase_db_evidence-ledger

## Target Allowed Paths

Create only:

- scripts/extract_ppl_offer_api_golden.py
- tests/unit/test_ppl_offer_api_golden.py
- tests/fixtures/ppl_offer_api_v1/normal-command.json
- tests/fixtures/ppl_offer_api_v1/normal-response.json
- tests/fixtures/ppl_offer_api_v1/replay-response.json
- tests/fixtures/ppl_offer_api_v1/empty-read.json
- tests/fixtures/ppl_offer_api_v1/stale-head-error.json
- tests/fixtures/ppl_offer_api_v1/policy-inactive-error.json
- tests/fixtures/ppl_offer_api_v1/unknown-field-error.json
- tests/fixtures/ppl_offer_api_v1/payload-limit-error.json
- tests/fixtures/ppl_offer_api_v1/confirmed-absent.json
- tests/fixtures/ppl_offer_api_v1/comparison-missing-scenario.json
- db/tests/test_ppl_offer_m1_e2e.py
- import/tests/test_ppl_offer_contract_parity.py
- web/vitest.acceptance.config.ts
- web/acceptance/golden-contract.test.ts
- web/acceptance/db-artifact.test.ts

Modify only:

- ARCHITECTURE.md
- OPERATIONS.md
- docs/MANUAL.md
- README.md
- docs/superpowers/plans/2026-07-17-ppl-offer-decision-engine-milestone1.md
- docs/superpowers/plans/2026-07-17-ppl-offer-task6-acceptance.md

The integrated prerequisite path `import/alias_integrity.py` is an immutable reviewed ancestor, not a Task 6 write path. No other tracked target path may change.

## Exact Task 6 Execution Contract

Preserve the already-green focused WIP. After fast-forward and Auth/Kong health:

1. Run the two auth-posture tests.
2. Restart Step 6's complete seed-free scratch acceptance sequence once: one-owner E2E, all db tests, accepted `manual_only` import parity with exactly one expected skip, unit and strict-xfail gates, web unit/build/acceptance/e2e, target smoke, diff check, contextual scans, and synthetic artifact record.
3. A Task 6 failure is corrected only inside the allowed write set and restarts the complete sequence. A Task 1-5 finding stops and returns to its owner.
4. After green acceptance, synchronize only the authorized one-user/manual_only truth paths.
5. Rerun final smoke, complete web gates, affected acceptance, diff and frozen-hash checks, absence scans, and the corrected plan's final aggregate.
6. Obtain fresh read-only advisory specification and code-quality/security reviews over the final uncommitted diff and resolve material findings inside scope.
7. Stage only the Task 6 allowed paths and create exactly one commit with subject `test: accept PPL offer decision milestone locally`.

Do not rerun the full suite on an unchanged state. Do not classify a missing service, mandatory skip, or prior finding as pass. The ignored acceptance record binds the prerequisite GO, service state, exact commands/counts, artifact hash, one-user/manual_only disposition, and synthetic-only boundary.

## Side-Effect Executor Token

- effect: local synthetic Task 6 acceptance execution
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance, test-owned scratch databases on 127.0.0.1:54322, Auth/Kong on 127.0.0.1:54321, ignored acceptance directory, test-owned preview, and installed Chromium
- scope: use synthetic data only; create and force-drop only test-owned scratch databases; write only route-authorized Task 6 paths and ignored synthetic evidence; use preserved offline node_modules and installed browser; no default/managed database mutation, seed, dependency acquisition, network, real/private data, or production activation

## Side-Effect Executor Token

- effect: Task 6 local source implementation and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
- scope: change only the Task 6 allowed paths, preserve the immutable prerequisite ancestor, retain synthetic acceptance evidence, and create exactly one Task 6 commit with subject test: accept PPL offer decision milestone locally; no target-main integration or remote ref change

## Verify Request And Operator2 Contract

Director's canonical verify-request assigns only Operator2 and binds:

- focused range 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0..TASK6_HEAD;
- cumulative range b9547db4e47c2d867f7f4c3168e55df33c6d2fa9..TASK6_HEAD;
- immutable prerequisite commit, verify-request, and GO;
- exact reviewed repository/worktree/tree/path manifest and final plan/API hashes;
- author Director on gpt-5.6-sol and reviewer Operator2 on gpt-5.6-terra;
- complete synthetic acceptance and service-state evidence;
- one-user/manual_only, scratch/default separation, no ios diff, no Task-4 import surface, no decoder duplication, no network acquisition, and preserved normal checkout.

Operator2 independently inspects both immutable ranges, reruns a sufficient exact subset including complete Task 6 acceptance where locally available, and publishes one canonical GO, NITS, or FAIL. Operator2 uses the already-running Auth/Kong endpoints without lifecycle action, its own scratch databases, preserved offline dependencies, test preview, and installed Chromium. Operator2 does not repair or integrate.

## Side-Effect Executor Token

- effect: local synthetic Task 6 independent review
- executor: operator2
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance, Operator2-owned scratch databases on 127.0.0.1:54322, Auth/Kong on 127.0.0.1:54321, test-owned preview, and installed Chromium
- scope: inspect immutable focused and cumulative ranges and rerun synthetic acceptance using existing local services only; no source repair, service lifecycle, default/managed database mutation, seed, dependency acquisition, network, real/private data, target-main integration, remote ref change, deployment, or activation

Director dispatches the committed verify-request once to the compatible Operator2 task, reconciles only the committed report, and restores Auth/Kong regardless of verdict.

## Stop Boundary

No target-main integration.
No integration of the Task 6 commit into another branch.
No push or remote publication.
No deployment, managed Supabase/Auth action, account provisioning, or production activation.
No physical Windows installation or release claim.
No real/private data, booking, vendor contact, or spend.
No dependency or browser acquisition.
No default database reset, migration, seed, or destructive cleanup.
No cursor consumption or protocol lock action.
No history rewrite, force action, broad prune, or unrelated cleanup.

## Exact Next Trigger

Director reads this committed generation-32 route, publishes and proves its revision-33 child, performs the exact fast-forward and constrained Auth/Kong start, executes the complete Task 6 plan once, creates the one Task 6 commit, submits both ranges to Operator2, waits for the committed verdict, restores Auth/Kong, and reports the reviewed local state. Coordinator then reconciles verdict and restoration.

Cursor at send: 0
