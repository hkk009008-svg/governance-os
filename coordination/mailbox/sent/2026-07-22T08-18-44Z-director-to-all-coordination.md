# Director → All: resume corrected Mac beta migration

**When:** 2026-07-22T08:18:44Z · **From:** director (online)

Task-board: ledger-beta-mac-activation-2026-07-22
Task ID: ledger-beta-mac-activation-2026-07-22
Outcome contract: resume the corrected local Mac beta runtime through the non-secret migrated-and-ready checkpoint only
Parent contract: coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
Contract revision: 37
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T08-01-06Z-operator2-to-director-verification-report.md@ccdbdb2344da3ad4f76bfddd8ca66b95f06081b8, coordination/mailbox/sent/2026-07-22T08-12-04Z-director-to-all-coordination.md@46d70ff9462438cf150f52b30db59fa3477b5ba3, coordination/mailbox/sent/2026-07-22T07-47-59Z-director-to-operator2-verify-request.md@8d5be6cab3b9f759e1391e8bbc4957cdda24cf07, coordination/mailbox/sent/2026-07-22T07-27-41Z-director-to-all-coordination.md@fddfe166519a285bc519b2896b9f29bd67023aeb, coordination/mailbox/sent/2026-07-22T06-53-14Z-coordinator-to-director-coordination.md@a3a8ae76ce03533568a96d8568e8436b8f86301e, coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9, coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d, coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
Authorization source: user-task:mac-first-beta-activation-approved-2026-07-22
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Accepted target HEAD: d66601dd843120e3989fe3099b529abaecff47db
Protected local settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Private provisioning executor: coordinator

## Corrected Integration Proof

Local evidence-ledger `main` fast-forwarded exactly from `87a10b787a2f01f4353cad6a5e8ed338c381d333` to independently accepted correction head `d66601dd843120e3989fe3099b529abaecff47db`. The reviewed cumulative range is two commits and exactly three paths with name-only manifest SHA-256 `282d69ae0d799840cd2b259b687213d61d33381567dfcebef95d465da71716d4`. Main and HEAD equal the accepted head, the index and tracked worktree are clean, and preserved `.vscode/settings.json` remains SHA-256 `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`.

## Preserved Migration Checkpoint

- Backup: `/Users/hyungkoookkim/evidence-ledger/data/local-beta/mac-beta-pre-migration-20260722.dump`; custom format; mode `0600`; SHA-256 `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`.
- Current migration maximum: `20260717000400`.
- The prior failed `20260717000500` ledger row and `decision._formula_contract_digest(jsonb)` remain absent.
- The six and only six pending migrations authorized here are `20260717000450`, `20260717000500`, `20260717000600`, `20260718000100`, `20260718000200`, and `20260720000100`, in that exact order.
- No correction migration has yet been applied to the default database. No API container has been started. No credential has been handled or recorded.

## Frozen Runtime Identities

- Network: `supabase_network_evidence-ledger`, ID `96e5907462506f229c6dfad4644444f3e6ad835968b1196e8363b49cf55d62a4`.
- Database: `supabase_db_evidence-ledger`, ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, image `public.ecr.aws/supabase/postgres:17.6.1.140`, required running and healthy on `127.0.0.1:54322`.
- Auth: `supabase_auth_evidence-ledger`, ID `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, image `public.ecr.aws/supabase/gotrue:v2.192.0`, required stopped before its one authorized start.
- PostgREST: `supabase_rest_evidence-ledger`, ID `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, image `public.ecr.aws/supabase/postgrest:v14.14`, required stopped before its one authorized start.
- Kong: `supabase_kong_evidence-ledger`, ID `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`, image `public.ecr.aws/supabase/kong:2.8.1`, required stopped before its one authorized start.
- Every other `supabase_*_evidence-ledger` sibling must remain stopped and byte-for-byte outside this continuation.

## Target Allowed Paths

- data/local-beta
- web/.env.local
- web/dist

## Allowed Path Semantics

These are the inherited ignored runtime locations. This continuation creates no tracked source edit or target commit. The protected backup is read-only. The web runtime paths remain held until a later Coordinator provisioning closeout.

## Side-Effect Executor Token

- effect: exact remaining default-database migration advance
- executor: director
- target: frozen `supabase_db_evidence-ledger` ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26` through `127.0.0.1:54322`
- scope: require target HEAD `d66601dd843120e3989fe3099b529abaecff47db`, protected settings hash, backup path/mode/hash, database identity/health, current maximum `20260717000400`, absent failed objects, and pending set exactly the six listed versions; execute exactly once `env SUPABASE_TELEMETRY_DISABLED=1 supabase migration up --local --yes` from the target checkout; require the six versions to apply in exact order and final maximum `20260720000100`; do not create, replace, delete, or rewrite the backup and perform no reset, seed, rollback, schema workaround, migration outside the set, real-data import, or remote-database action

## Side-Effect Executor Token

- effect: exact existing local API container starts
- executor: director
- target: frozen Auth, PostgREST, and Kong identities above on frozen network ID `96e5907462506f229c6dfad4644444f3e6ad835968b1196e8363b49cf55d62a4`
- scope: only after migration postcheck, execute at most once and only if stopped `docker start supabase_auth_evidence-ledger`, require its exact ID/image/network and healthy state; then execute at most once and only if stopped `docker start supabase_rest_evidence-ledger`, require its exact ID/image/network and ready/running state; then execute at most once and only if stopped `docker start supabase_kong_evidence-ledger`, require its exact ID/image/network and healthy state plus listener `127.0.0.1:54321`; require database still healthy and every other sibling unchanged/stopped; no retry, pull, create, recreate, restart, reset, configuration change, network change, or substitute

## Side-Effect Executor Token

- effect: exact two deferred Auth posture checks
- executor: director
- target: `/Users/hyungkoookkim/evidence-ledger/db/tests/test_auth_posture.py` against the frozen loopback runtime
- scope: after all three API readiness checks, run exactly `env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest db/tests/test_auth_posture.py::test_email_provider_is_enabled_password_login_reachable db/tests/test_auth_posture.py::test_self_signup_is_disabled -q -p no:cacheprovider`; require exactly two passes; use no private credential, owner account, browser session, default-database mutation, dependency, network acquisition, or extra test

## Side-Effect Executor Token

- effect: restore route-started API state on blocker
- executor: director
- target: only the frozen Auth, PostgREST, and Kong containers newly started by this continuation
- scope: if an API start, readiness check, or Auth posture check fails after migration, execute at most once `docker stop supabase_kong_evidence-ledger supabase_rest_evidence-ledger supabase_auth_evidence-ledger` limited to containers this continuation actually started; preserve the migrated database and protected backup; never stop Docker Desktop, the database, or any sibling, and never retry or substitute

## Checkpoint And Stop Boundary

After all six migrations, three API readiness checks, and both Auth nodes pass, publish exactly one committed non-secret migrated-and-ready checkpoint addressed to Coordinator. It records the integrated head, frozen IDs/images and states, protected backup path/mode/hash, migration before/after versions, listener health, the two-pass Auth result, sibling-state preservation, and confirmation that no credential was requested, inferred, received, handled, or recorded. Stop there for the parent-owned private provisioning token.

No provisioning, credential handling, web configuration/build/preview, source edit, target commit, target-main integration beyond the completed correction fast-forward, remote-reference publication, dependency or image acquisition, service action outside the exact tokens, default-database action outside the six migrations, real/private business data, policy activation, deployment, installation, Windows work, provider contact, booking, spend, cursor, lock, cleanup, history rewrite, force action, or unrelated effect is authorized.

Cursor at send: 0
