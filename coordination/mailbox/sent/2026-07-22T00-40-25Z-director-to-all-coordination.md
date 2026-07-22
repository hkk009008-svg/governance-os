# Director → All: continue Task 6 with exact Auth Kong starts

**When:** 2026-07-22T00:40:25Z · **From:** director (online)

Task-board: ledger-beta-task6-final-acceptance-2026-07-22
Task ID: ledger-beta-task6-final-acceptance-2026-07-22
Outcome contract: start only the frozen existing Auth and Kong containers, execute the Auth-available Task 6 acceptance once, create the one Task 6 commit, obtain Operator2 verdict, restore Auth/Kong, and report durably
Parent contract: coordination/mailbox/sent/2026-07-22T00-25-18Z-director-to-all-coordination.md@b8156d4192049d71882f4ba09940ae10056dad28
Contract revision: 34
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T00-32-24Z-director-to-coordinator-coordination.md@7b705644ffd2af161741c64c8dc31770daf2761f, coordination/mailbox/sent/2026-07-22T00-20-15Z-coordinator-to-all-coordination.md@321a9409c562b8c80dbea5d85d25b5eb82cf1650
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
Target branch: codex/beta-task6-local-acceptance
Target base: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Accepted target HEAD: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Focused review base: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Cumulative review base: b9547db4e47c2d867f7f4c3168e55df33c6d2fa9
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Target Allowed Paths

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
- ARCHITECTURE.md
- OPERATIONS.md
- docs/MANUAL.md
- README.md
- docs/superpowers/plans/2026-07-17-ppl-offer-decision-engine-milestone1.md
- docs/superpowers/plans/2026-07-17-ppl-offer-task6-acceptance.md

The first seventeen paths are create-only. The final six paths are modify-only. The integrated prerequisite path `import/alias_integrity.py` is an immutable reviewed ancestor and is not a Task 6 write path.

## Frozen lifecycle identities

- Auth: `supabase_auth_evidence-ledger`, container ID `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, image `public.ecr.aws/supabase/gotrue:v2.192.0`.
- Kong: `supabase_kong_evidence-ledger`, container ID `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`, image `public.ecr.aws/supabase/kong:2.8.1`.
- Database: `supabase_db_evidence-ledger`, container ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`.
- Network: `supabase_network_evidence-ledger`.

## Side-Effect Executor Token

- effect: start existing local Auth container
- executor: director
- target: exact existing container `supabase_auth_evidence-ledger` at frozen ID/image on `supabase_network_evidence-ledger`
- scope: execute exactly `docker start supabase_auth_evidence-ledger` once, poll its configured health for at most 60 seconds, and require the frozen ID/image running and healthy while the frozen database and every other local Supabase service remain unchanged; no pull, create, recreate, restart, configuration change, reset, migration, seed, network acquisition, managed action, or retry

## Side-Effect Executor Token

- effect: start existing local Kong container
- executor: director
- target: exact existing container `supabase_kong_evidence-ledger` at frozen ID/image on `supabase_network_evidence-ledger`
- scope: only after Auth is proven healthy, execute exactly `docker start supabase_kong_evidence-ledger` once, poll its configured health for at most 60 seconds, and require the frozen ID/image running and healthy with a listener at 127.0.0.1:54321 while the frozen database and every other local Supabase service remain unchanged; no pull, create, recreate, restart, configuration change, reset, migration, seed, network acquisition, managed action, or retry

## Side-Effect Executor Token

- effect: restore local Auth and Kong pre-state
- executor: director
- target: exact existing containers `supabase_kong_evidence-ledger` and `supabase_auth_evidence-ledger`
- scope: after committed Operator2 verdict or any earlier blocker, execute exactly `docker stop supabase_kong_evidence-ledger supabase_auth_evidence-ledger`; prove both Exited, port 54321 closed, the same frozen database Up and healthy, and every other service unchanged; if Auth alone was newly started before a Kong failure, the same exact two-target stop command restores pre-state; no retry, substitute, database lifecycle, or other-container mutation

## Side-Effect Executor Token

- effect: local synthetic Task 6 acceptance execution
- executor: director
- target: the routed evidence-ledger worktree, test-owned scratch databases on 127.0.0.1:54322, frozen Auth/Kong on 127.0.0.1:54321, ignored acceptance directory, test-owned preview, and installed Chromium
- scope: after Auth/Kong health, run auth posture first and then the unchanged complete Task 6 acceptance sequence once; use synthetic data, preserved offline dependencies, and the installed browser only; create and force-drop only test-owned scratch databases; write only Task 6 allowed paths and ignored synthetic evidence; no default/managed database mutation, seed, dependency/browser acquisition, network, real/private data, deployment, or activation

## Side-Effect Executor Token

- effect: Task 6 local source implementation and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
- scope: preserve the already-green focused WIP, synchronize only the authorized one-user/manual_only truth, resolve only in-scope Task 6 findings test-first, stage only the Task 6 allowed paths, and create exactly one commit with subject `test: accept PPL offer decision milestone locally`; preserve the immutable prerequisite ancestor; no target-main or another-branch integration, history rewrite, or remote ref change

## Side-Effect Executor Token

- effect: local synthetic Task 6 independent review
- executor: operator2
- target: immutable focused range `5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0..TASK6_HEAD`, cumulative range `b9547db4e47c2d867f7f4c3168e55df33c6d2fa9..TASK6_HEAD`, the routed worktree, Operator2-owned scratch databases, already-running frozen Auth/Kong, test-owned preview, and installed Chromium
- scope: inspect both immutable ranges and rerun sufficient synthetic acceptance using existing local services and preserved offline dependencies only; publish one canonical GO, NITS, or FAIL; no source repair, service lifecycle, default/managed database mutation, seed, dependency/browser acquisition, network, real/private data, integration, remote ref change, deployment, or activation

## Shared-effect boundaries

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

Start and restore only the frozen existing Auth and Kong containers using the exact commands above. Keep them running through Director acceptance and immutable Operator2 review. On any lifecycle mismatch, restore pre-state and publish one blocker without retry or substitute.

Cursor at send: 0
