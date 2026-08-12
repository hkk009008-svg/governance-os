# Director → All: continue Task 6 unchanged review after route grammar correction

**When:** 2026-07-22T02:01:34Z · **From:** director (online)

Task-board: ledger-beta-task6-final-acceptance-2026-07-22
Task ID: ledger-beta-task6-final-acceptance-2026-07-22
Outcome contract: correct only the active allowed-path grammar, obtain one unchanged immutable Operator2 review of the accepted Task 6 commit, restore Auth and Kong after verdict or blocker, and report durably
Parent contract: coordination/mailbox/sent/2026-07-22T00-40-25Z-director-to-all-coordination.md@848447cb409b356414896d94587c0129eb5227f0
Contract revision: 35
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T01-56-46Z-operator2-to-director-verification-report.md@ed4c6c0f4b4f6e3226de3b8210ca661adef10f0e, coordination/mailbox/sent/2026-07-22T00-40-25Z-director-to-all-coordination.md@848447cb409b356414896d94587c0129eb5227f0, coordination/mailbox/sent/2026-07-22T00-20-15Z-coordinator-to-all-coordination.md@321a9409c562b8c80dbea5d85d25b5eb82cf1650, coordination/mailbox/sent/2026-07-22T01-43-27Z-director-to-operator2-verify-request.md@bfaee3ae7e94a7d7c14dec48b3cc8dbd2900c40f
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
Target branch: codex/beta-task6-local-acceptance
Target base: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Accepted target HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Focused review base: 5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0
Cumulative review base: b9547db4e47c2d867f7f4c3168e55df33c6d2fa9
Target tree: 025e3480b5d7bdd4d57b07a8e80c345d40e5c098
Focused manifest SHA-256: a7d3e00f94cf8581a91ba4c3aa4759696bf5d5dcd2dde705b0621c31e5d578a4
Cumulative manifest SHA-256: ea393757c8cdbcc22ca800ed04daa12f4f32441ba9a4c987593ce2dbe239e6f1
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

## Allowed Path Semantics

The first seventeen paths are the reviewed create-only Task 6 paths. The final six paths are the reviewed modify-only documentation paths. This continuation authorizes no source change, target mutation, target commit, integration, or replacement of any immutable target byte.

The accepted Task 6 commit remains exactly `87a10b787a2f01f4353cad6a5e8ed338c381d333`, parent `5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0`, tree `025e3480b5d7bdd4d57b07a8e80c345d40e5c098`, and subject `test: accept PPL offer decision milestone locally`. The review ranges remain focused `5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0..87a10b787a2f01f4353cad6a5e8ed338c381d333` and cumulative `b9547db4e47c2d867f7f4c3168e55df33c6d2fa9..87a10b787a2f01f4353cad6a5e8ed338c381d333`.

## Frozen lifecycle identities

- Auth: `supabase_auth_evidence-ledger`, container ID `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, image `public.ecr.aws/supabase/gotrue:v2.192.0`.
- Kong: `supabase_kong_evidence-ledger`, container ID `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`, image `public.ecr.aws/supabase/kong:2.8.1`.
- Database: `supabase_db_evidence-ledger`, container ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`.
- Network: `supabase_network_evidence-ledger`.

## Side-Effect Executor Token

- effect: unchanged local synthetic Task 6 independent review
- executor: operator2
- target: immutable focused range `5fa2dbec5067e1cfcd2f0443dfd9b9728abff4e0..87a10b787a2f01f4353cad6a5e8ed338c381d333`, cumulative range `b9547db4e47c2d867f7f4c3168e55df33c6d2fa9..87a10b787a2f01f4353cad6a5e8ed338c381d333`, the routed worktree, Operator2-owned scratch databases and ignored artifacts, already-running frozen Auth/Kong, test-owned preview, preserved dependencies, and installed Chromium
- scope: inspect both immutable ranges and rerun sufficient synthetic acceptance using only the already-running frozen local services, Operator2-owned scratch databases/artifacts, preserved offline dependencies, test-owned preview, and installed Chromium; publish exactly one canonical GO, NITS, or FAIL; no source repair, target mutation or commit, service start/stop/restart/configuration, default/managed database mutation, seed, dependency/browser acquisition, network, real/private data, integration, remote ref change, deployment, activation, physical installation, booking, spend, cursor action, lock action, or cleanup

## Side-Effect Executor Token

- effect: restore local Auth and Kong pre-state
- executor: director
- target: exact existing containers `supabase_kong_evidence-ledger` and `supabase_auth_evidence-ledger`
- scope: after the committed Operator2 verdict or any earlier blocker, execute exactly `docker stop supabase_kong_evidence-ledger supabase_auth_evidence-ledger`; prove both Exited, port 54321 closed, the same frozen database Up and healthy, and every other service unchanged; no retry, substitute, database lifecycle, service start/restart/configuration, or other-container mutation

## Review correction and boundaries

The prior formal FAIL is binding and is addressed only by the parser-clean structured path section above. The generation-32 Coordinator route and revision 34 remain immutable finding lineage; neither is used as the active review authority after this continuation proves effective.

Do not rerun Director acceptance. Do not repair source, change or recreate the target commit, mutate the target, integrate target main or another branch, push or publish a remote ref, start/restart/configure a service, mutate the default or managed database, acquire a dependency or browser, use network or real/private data, deploy, activate policy, claim physical installation, perform iOS work, contact a provider, book, spend, consume a cursor, take a protocol lock, clean up, reset, rebase, amend, squash, revert, force an action, or perform any unrelated effect. A later GO grants none.

Cursor at send: 0
