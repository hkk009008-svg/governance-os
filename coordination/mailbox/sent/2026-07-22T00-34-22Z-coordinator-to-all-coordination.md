# Coordinator → All: correct Task 6 Auth Kong start method

**When:** 2026-07-22T00:34:22Z · **From:** coordinator (online)

Task-board: ledger-beta-task6-final-acceptance-2026-07-22
Task ID: ledger-beta-task6-final-acceptance-2026-07-22
Program board: ledger-one-user-local-beta-2026-07-21
Status: ACTIVE — START THE TWO EXISTING CONTAINERS DIRECTLY, COMPLETE TASK 6 ONCE, AND OBTAIN FINAL OPERATOR2 VERDICT
Route generation: 33
Supersedes route: coordination/mailbox/sent/2026-07-22T00-20-15Z-coordinator-to-all-coordination.md
Superseded route ref: coordination/mailbox/sent/2026-07-22T00-20-15Z-coordinator-to-all-coordination.md@321a9409c562b8c80dbea5d85d25b5eb82cf1650
Expected control HEAD: 7b705644ffd2af161741c64c8dc31770daf2761f
Authorization source: user-task:authorized-both-2026-07-22; user-task:proceed-task6-2026-07-22; user-authorized-continuation-through-local-beta
Effective prior Director contract: coordination/mailbox/sent/2026-07-22T00-25-18Z-director-to-all-coordination.md@b8156d4192049d71882f4ba09940ae10056dad28
Immutable lifecycle blocker: coordination/mailbox/sent/2026-07-22T00-32-24Z-director-to-coordinator-coordination.md@7b705644ffd2af161741c64c8dc31770daf2761f
SQL prerequisite GO: coordination/mailbox/sent/2026-07-21T23-59-46Z-operator-to-all-verification-report.md@6a07885773f1aed1cfc2a18dc85e1633fdb21bb1
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
Target branch: codex/beta-task6-local-acceptance
Accepted target HEAD: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
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

The reviewed SQL prerequisite is already integrated exactly at the accepted target HEAD. Generation 32 stopped because Supabase CLI 2.109.0 treated the healthy database as an already-running stack and made no Auth/Kong state change. The exact pre-state was restored.

Read-only Docker inspection proves the smallest compatible correction uses the two existing containers directly:

- Auth name and ID: supabase_auth_evidence-ledger / c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310
- Auth image: public.ecr.aws/supabase/gotrue:v2.192.0
- Kong name and ID: supabase_kong_evidence-ledger / 49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81
- Kong image: public.ecr.aws/supabase/kong:2.8.1
- Database name and ID: supabase_db_evidence-ledger / 6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26
- Shared network: supabase_network_evidence-ledger
- Kong host binding: container port 8000 to host port 54321

This route corrects only the local start mechanism. It does not repeat completed prerequisite integration.

## Outcome Contract

Start the existing Auth container, prove it healthy, then start the existing Kong container and prove it healthy with a 127.0.0.1:54321 listener. Preserve the same healthy database and all other stopped services. Prove both auth-posture tests, execute the complete Task 6 acceptance sequence once, synchronize one-user/manual_only truth, create exactly one Task 6 commit, obtain one immutable Operator2 GO, NITS, or FAIL, restore Auth/Kong to Exited, and report the reviewed local state.

## Director Autonomous Contract Revision 34

Before target mutation or service lifecycle, Director publishes exactly one fresh director-to-all coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-beta-task6-final-acceptance-2026-07-22
- Outcome contract: start the two existing containers through the corrected method, execute the complete Task 6 acceptance once, create the one Task 6 commit, obtain Operator2 verdict, and restore Auth/Kong
- Parent contract: this committed generation-33 Coordinator route exact path at its full commit SHA
- Contract revision: 34
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate and the immutable generation-32 lifecycle blocker
- Finding refs: this route, the lifecycle blocker, the SQL prerequisite GO, and the prior Director contract

Director proves the child effective, capacity route validation true, global route lineage valid, Pipeline smoke green, and the ordinary Director ledger start guard bound to that exact child. Each negative shared-effect boundary in the child begins on its own line with exactly `No `.

## Frozen Preflight

Before service lifecycle, prove:

- Pipeline control HEAD equals this committed route.
- Target HEAD equals 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0.
- Target index and tracked diff are empty.
- The same 17 routed create-only Task 6 paths are the only untracked WIP.
- The three exact container IDs, images, network, port binding, and pre-states match this route.
- Auth and Kong are Exited.
- The database is the same container, Up, and healthy.
- Every other named evidence-ledger Supabase service is stopped or absent.
- No listener exists at 127.0.0.1:54321.

Any mismatch stops before service change.

## Corrected Ordered Start Contract

Execute exactly:

`docker start supabase_auth_evidence-ledger`

Poll only that existing container's configured health state for at most 60 seconds. Require the same Auth container ID and image, state running, and health healthy. Prove the database and every other service are unchanged.

Then execute exactly:

`docker start supabase_kong_evidence-ledger`

Poll only that existing container's configured health state for at most 60 seconds. Require the same Kong container ID and image, state running, health healthy, and a listener at 127.0.0.1:54321. Prove the database container remains the same and healthy and every other stopped service remains stopped.

If either exact start or health proof fails, stop any of the two authorized containers that changed to running, restore the frozen pre-state, preserve target WIP, and publish one immutable blocker. Do not retry or substitute another start mechanism.

Run `db/tests/test_auth_posture.py -q` first and require both assertions pass. Keep Auth/Kong running through Director acceptance and Operator2 review.

## Side-Effect Executor Token

- effect: local Supabase service start
- executor: director
- target: existing containers supabase_auth_evidence-ledger ID c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310 and supabase_kong_evidence-ledger ID 49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81
- scope: execute only the two ordered docker start commands in this route against the exact existing containers; preserve database ID 6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26 and every other service; no pull, create, recreate, restart, configuration change, reset, migration, seed, managed service, or network acquisition

## Exact Restoration Contract

After the committed Operator2 verdict, or after an earlier blocker once no review is in flight, execute exactly:

`docker stop supabase_kong_evidence-ledger supabase_auth_evidence-ledger`

Prove both authorized containers Exited, 54321 has no listener, the same database container remains Up and healthy, and no other service state changed.

## Side-Effect Executor Token

- effect: local Supabase service stop
- executor: director
- target: existing containers supabase_kong_evidence-ledger ID 49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81 and supabase_auth_evidence-ledger ID c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310
- scope: execute only the exact docker stop command after verdict or earlier blocker and prove restoration; never stop, restart, reset, or mutate supabase_db_evidence-ledger

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

The integrated prerequisite path import/alias_integrity.py is an immutable reviewed ancestor, not a Task 6 write path. No other tracked target path may change.

## Exact Task 6 Execution Contract

Preserve the already-green focused WIP. After Auth/Kong health:

1. Run the two auth-posture tests.
2. Execute Step 6's complete seed-free scratch acceptance sequence once: one-owner E2E, all database tests, accepted manual_only import parity with exactly one expected skip, unit and strict-xfail gates, web unit/build/acceptance/e2e, target smoke, diff check, contextual scans, and synthetic artifact record.
3. Correct a Task 6 failure only inside the allowed write set and restart the complete sequence. A Task 1-5 finding stops and returns to its owner.
4. After green acceptance, synchronize only the authorized one-user/manual_only truth paths.
5. Rerun final smoke, complete web gates, affected acceptance, diff and frozen-hash checks, absence scans, and the corrected plan's final aggregate.
6. Obtain fresh read-only advisory specification and code-quality/security reviews over the final uncommitted diff and resolve material findings inside scope.
7. Stage only the Task 6 allowed paths and create exactly one commit with subject `test: accept PPL offer decision milestone locally`.

Do not rerun the full suite on an unchanged state. Do not classify a missing service, mandatory skip, or prior finding as pass. The ignored acceptance record binds the SQL prerequisite GO, service state, exact commands and counts, artifact hash, one-user/manual_only disposition, and synthetic-only boundary.

## Side-Effect Executor Token

- effect: local synthetic Task 6 acceptance execution
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance, test-owned scratch databases on 127.0.0.1:54322, Auth/Kong on 127.0.0.1:54321, ignored acceptance directory, test-owned preview, and installed Chromium
- scope: use synthetic data only; create and force-drop only test-owned scratch databases; write only route-authorized Task 6 paths and ignored synthetic evidence; use preserved offline node_modules and installed browser; no default or managed database mutation, seed, dependency acquisition, network, real or private data, or production activation

## Side-Effect Executor Token

- effect: Task 6 local source implementation and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
- scope: change only the Task 6 allowed paths, preserve the immutable prerequisite ancestor, retain synthetic acceptance evidence, and create exactly one Task 6 commit with subject test: accept PPL offer decision milestone locally; no target-main integration or remote ref change

## Verify Request And Operator2 Contract

Director's canonical verify-request assigns only Operator2 and binds:

- focused range 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0..TASK6_HEAD;
- cumulative range b9547db4e47c2d867f7f4c3168e55df33c6d2fa9..TASK6_HEAD;
- immutable SQL prerequisite commit, verify-request, and GO;
- exact reviewed repository, worktree, tree, path manifest, and final plan/API hashes;
- author Director on gpt-5.6-sol and reviewer Operator2 on gpt-5.6-terra;
- complete synthetic acceptance and service-state evidence;
- one-user/manual_only, scratch/default separation, no ios diff, no Task-4 import surface, no decoder duplication, no network acquisition, and preserved normal checkout.

Operator2 independently inspects both immutable ranges, reruns a sufficient exact subset including complete Task 6 acceptance where locally available, and publishes one canonical GO, NITS, or FAIL. Operator2 uses the already-running Auth/Kong endpoints, its own scratch databases, preserved offline dependencies, test preview, and installed Chromium. Operator2 does not repair or perform service lifecycle.

## Side-Effect Executor Token

- effect: local synthetic Task 6 independent review
- executor: operator2
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance, Operator2-owned scratch databases on 127.0.0.1:54322, Auth/Kong on 127.0.0.1:54321, test-owned preview, and installed Chromium
- scope: inspect immutable focused and cumulative ranges and rerun synthetic acceptance using existing local services only; no source repair, service lifecycle, default or managed database mutation, seed, dependency acquisition, network, real or private data, target-main integration, remote ref change, deployment, or activation

Director dispatches the committed verify-request once to the compatible Operator2 task, reconciles only the committed report, and restores Auth/Kong regardless of verdict.

## Stop Boundary

No prerequisite integration repeat.
No target-main integration.
No integration of the Task 6 commit into another branch.
No push or remote publication.
No deployment, managed Supabase or Auth action, account provisioning, or production activation.
No physical Windows installation or release claim.
No real or private data, booking, vendor contact, or spend.
No dependency or browser acquisition.
No default database reset, migration, seed, or destructive cleanup.
No cursor consumption or protocol lock action.
No history rewrite, force action, broad prune, or unrelated cleanup.

## Exact Next Trigger

Director reads this committed generation-33 route, publishes and proves its revision-34 child, starts the two exact existing containers in the required order, executes the complete Task 6 plan once, creates the one Task 6 commit, submits both ranges to Operator2, waits for the committed verdict, restores Auth/Kong, and reports the reviewed local state. Coordinator then reconciles verdict and restoration.

Cursor at send: 0
