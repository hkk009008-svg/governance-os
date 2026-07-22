# Director → All: freeze Mac beta local identities

**When:** 2026-07-22T06:14:16Z · **From:** director (online)

Task-board: ledger-beta-mac-activation-2026-07-22
Task ID: ledger-beta-mac-activation-2026-07-22
Outcome contract: integrate the reviewed Task 6 head and prepare the exact local Mac beta runtime through a private-provisioning checkpoint and final loopback teaching URL
Parent contract: coordination/mailbox/sent/2026-07-22T06-09-15Z-director-to-all-coordination.md@7f3d741a579461133febbc68183e4fcf0e5c4a11
Contract revision: 36
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T06-09-15Z-director-to-all-coordination.md@7f3d741a579461133febbc68183e4fcf0e5c4a11, coordination/mailbox/sent/2026-07-22T06-03-28Z-coordinator-to-all-coordination.md@da36b21029303939ddbd7d8ec1eace0ffcd8e7b2, coordination/mailbox/sent/2026-07-22T02-19-59Z-operator2-to-director-verification-report.md@1f2cdb9040e18bc3ffdd0a617d00e61691139f51
Authorization source: user-task:mac-first-beta-activation-approved-2026-07-22
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: 171617635a7043ad5814edcc250cda3bc3474f75
Accepted target HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Reviewed integration head: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Protected local settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Private provisioning executor: coordinator

## Integrated Target Proof

Local evidence-ledger main fast-forwarded exactly from `171617635a7043ad5814edcc250cda3bc3474f75` to reviewed Task 6 head `87a10b787a2f01f4353cad6a5e8ed338c381d333`. The range is exactly 24 paths and `git diff --check` is silent. Index and tracked worktree are clean. Preserved `.vscode/settings.json` remains SHA-256 `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`.

## Docker And Network Identity

- Docker Desktop bundle: `com.docker.docker`, version `4.82.0`, build `233772`; launched once by revision 35 because the daemon was unavailable; daemon is ready as Docker Desktop server `29.6.1`.
- Network: `supabase_network_evidence-ledger`, full ID `96e5907462506f229c6dfad4644444f3e6ad835968b1196e8363b49cf55d62a4`, local bridge.
- Database: `supabase_db_evidence-ledger`; ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`; image `public.ecr.aws/supabase/postgres:17.6.1.140`; restart `unless-stopped`; state running/healthy; network ID `96e5907462506f229c6dfad4644444f3e6ad835968b1196e8363b49cf55d62a4`; IP `172.18.0.2`; ports `0.0.0.0:54322->5432/tcp` and `[::]:54322->5432/tcp`.
- Auth: `supabase_auth_evidence-ledger`; ID `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`; image `public.ecr.aws/supabase/gotrue:v2.192.0`; restart `unless-stopped`; state exited/unhealthy; frozen network ID above; no assigned IP or published port.
- PostgREST: `supabase_rest_evidence-ledger`; ID `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`; image `public.ecr.aws/supabase/postgrest:v14.14`; restart `unless-stopped`; state exited/no health object; frozen network ID above; no assigned IP or published port.
- Kong: `supabase_kong_evidence-ledger`; ID `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`; image `public.ecr.aws/supabase/kong:2.8.1`; restart `unless-stopped`; state exited/unhealthy; frozen network ID above; no assigned IP or published port.

## Complete Sibling State

- `supabase_analytics_evidence-ledger`: ID `7763e94a237f8b5ed4670d1a154ba6c620635dc26aa83c9ec94977c70b4e3c5e`; image `public.ecr.aws/supabase/logflare:1.45.6`; restart `unless-stopped`; exited/unhealthy.
- `supabase_auth_evidence-ledger`: ID `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`; image `public.ecr.aws/supabase/gotrue:v2.192.0`; restart `unless-stopped`; exited/unhealthy.
- `supabase_db_evidence-ledger`: ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`; image `public.ecr.aws/supabase/postgres:17.6.1.140`; restart `unless-stopped`; running/healthy.
- `supabase_edge_runtime_evidence-ledger`: ID `49af5bb868494b21b2a8ab4f3916fba942aaf346cf21519d005ac3fe5ffd385a`; image `public.ecr.aws/supabase/edge-runtime:v1.74.2`; restart `no`; exited/no health object.
- `supabase_inbucket_evidence-ledger`: ID `34c4728242d09e681fe0050ef9130d28e5177234bcd35bf7afd2133cdf3d6a19`; image `public.ecr.aws/supabase/mailpit:v1.30.2`; restart `unless-stopped`; exited/unhealthy.
- `supabase_kong_evidence-ledger`: ID `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81`; image `public.ecr.aws/supabase/kong:2.8.1`; restart `unless-stopped`; exited/unhealthy.
- `supabase_pg_meta_evidence-ledger`: ID `04cb8e471d6cb604396f53feb3417afc73c96ddfbb439440b359403f63682661`; image `public.ecr.aws/supabase/postgres-meta:v0.96.6`; restart `unless-stopped`; exited/unhealthy.
- `supabase_realtime_evidence-ledger`: ID `94fe8fb7118c155adae707dddaf33b2c34a0a39e90f40da6d40a6ac8e948a901`; image `public.ecr.aws/supabase/realtime:v2.112.1`; restart `unless-stopped`; exited/unhealthy.
- `supabase_rest_evidence-ledger`: ID `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`; image `public.ecr.aws/supabase/postgrest:v14.14`; restart `unless-stopped`; exited/no health object.
- `supabase_storage_evidence-ledger`: ID `82074a126596eb1b5ef7b8cea0b99e305e6be74dd9e77b043e14e55810cfb8f4`; image `public.ecr.aws/supabase/storage-api:v1.61.7`; restart `unless-stopped`; exited/unhealthy.
- `supabase_studio_evidence-ledger`: ID `5c13b551207b13871447dcc3747611283566727f212c5414db786bf349d67213`; image `public.ecr.aws/supabase/studio:2026.06.29-sha-20290c7`; restart `unless-stopped`; exited/unhealthy.
- `supabase_vector_evidence-ledger`: ID `67202a96e785d9c5b2b9d66e2cbfb4eeaaf1f3dc63e9e808728e68d26c7fd06b`; image `public.ecr.aws/supabase/vector:0.53.0-alpine`; restart `unless-stopped`; exited/unhealthy.

No sibling other than the frozen database is running. No container command, database query/write, backup, or migration occurred before this continuation.

## Target Allowed Paths

- data/local-beta
- web/.env.local
- web/dist

## Allowed Path Semantics

These are the complete ignored runtime write locations. No tracked source edit or new target commit is authorized. Preserve the untracked `.vscode/` directory and protected settings hash exactly.

## Side-Effect Executor Token

- effect: private default-database backup and exact migration advance
- executor: director
- target: frozen `supabase_db_evidence-ledger` ID `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26` through `127.0.0.1:54322` and ignored `data/local-beta`
- scope: create one mode-0600 custom-format backup plus SHA-256 and non-secret manifest in `data/local-beta`; verify current migration maximum is exactly `20260708000100`; apply exactly `20260708000200`, `20260717000100`, `20260717000200`, `20260717000300`, `20260717000400`, `20260717000500`, `20260717000600`, `20260718000100`, `20260718000200`, and `20260720000100` in order; require final maximum `20260720000100`; no reset, seed, rollback, deletion, real-data import, schema edit, remote database, or migration outside this exact set

## Side-Effect Executor Token

- effect: exact existing local API container starts and beta hold-open
- executor: director
- target: Auth ID `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, PostgREST ID `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, and Kong ID `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81` on network ID `96e5907462506f229c6dfad4644444f3e6ad835968b1196e8363b49cf55d62a4`
- scope: after backup and migration postcheck, start once and only if stopped the exact frozen Auth, PostgREST, and Kong containers in that dependency-safe order; require their frozen IDs/images/network, healthy or ready state, database still healthy, and listener at `127.0.0.1:54321`; start no sibling and perform no create, recreate, restart, reset, reconfiguration, image acquisition, network creation, or retry; leave only the freshly frozen database/Auth/PostgREST/Kong set running for the Mac teaching session

## Side-Effect Executor Token

- effect: restore route-created local runtime state on failure
- executor: director
- target: Docker Desktop launched by this route and any of frozen Auth, PostgREST, or Kong newly started by this route
- scope: before successful backup or migration, stop only an API container newly started by this route and quit Docker Desktop because this route launched it; after successful backup or migration, do not roll back or delete the backup, stop only the preview if any and API containers newly started by this route, preserve the migrated database for diagnosis, and report exact non-secret state; never stop, delete, or mutate another sibling or overwrite the backup

## Boundaries

This continuation grants no effect beyond the committed parent route. Coordinator-owned private provisioning remains held until the committed migrated-and-ready checkpoint; the later web phase remains held until the Coordinator closeout. No credential, service-role key, UUID, or browser token is requested, handled, recorded, or authorized here. No tracked source change, target commit, remote-reference publication, dependency or image acquisition, managed service, real/private business data, policy activation, deployment, Windows packaging, provider contact, booking, spend, cursor consumption, shared coordination fence mutation, cleanup outside the exact restoration set, or unrelated action is authorized.

Cursor at send: 0
