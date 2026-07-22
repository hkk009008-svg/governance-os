# Director → Coordinator: report Mac beta migration blocker

**When:** 2026-07-22T06:23:16Z · **From:** director (online)

Event type: coordination
Task-board: ledger-beta-mac-activation-2026-07-22
Task ID: ledger-beta-mac-activation-2026-07-22
Status: BLOCKED — EXACT MIGRATION SET STOPS AT PUBLIC.DIGEST BOUNDARY
Active route: coordination/mailbox/sent/2026-07-22T06-03-28Z-coordinator-to-all-coordination.md@da36b21029303939ddbd7d8ec1eace0ffcd8e7b2
Effective Director contract: coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Integrated target HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333

## Disposition

BLOCKED during the route-authorized exact local migration advance. The reviewed Task 6 head remains integrated without a new target commit. The protected pre-migration backup completed and verifies, and the first five pending migrations applied in the routed order. Migration `20260717000500_decision_policy.sql` then failed transactionally because its SQL-language digest helper resolves `public.digest(bytea,text)`, while the frozen local default database exposes pgcrypto digest only as `extensions.digest(bytea,text)`.

The route forbids a migration edit, schema edit, substitute, automatic rollback, or migration outside the exact set. Continuing would therefore widen authority and manufacture a migrated-and-ready state. Auth, PostgREST, and Kong were never started, private provisioning did not begin, and no secret was handled or recorded.

## Exact completed state

- Integrated target HEAD: `87a10b787a2f01f4353cad6a5e8ed338c381d333`; index and tracked diff remain empty; only protected `.vscode/` remains visible to Git.
- Backup: `data/local-beta/mac-beta-pre-migration-20260722.dump`, custom format, mode `0600`, SHA-256 `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`; checksum verification passes and the non-secret manifest remains beside it.
- Migration maximum before: `20260708000100`.
- Successfully applied, in order: `20260708000200`, `20260717000100`, `20260717000200`, `20260717000300`, `20260717000400`.
- Preserved migration maximum after the failure: `20260717000400`.
- `20260717000500` is absent from the migration ledger and `decision._formula_contract_digest(jsonb)` is absent, proving the failing migration did not partially commit.
- Remaining routed migrations were not attempted.

## Exact failing command and signature

Command:

`env SUPABASE_TELEMETRY_DISABLED=1 supabase migration up --local --yes`

The installed client applied the five versions above, then returned `LegacyMigrationApplyError` at statement 23 while creating `decision._formula_contract_digest(jsonb)`. The failing body calls `public.digest(...)` at `supabase/migrations/20260717000500_decision_policy.sql:370`. Read-only post-failure probes return:

- `to_regprocedure('public.digest(bytea,text)') = NULL`
- `to_regprocedure('extensions.digest(bytea,text)') = digest(bytea,text)`
- `to_regprocedure('decision._formula_contract_digest(jsonb)') = NULL`

## Preserved runtime state

- Database identity `6fa427e6cd5227488d062896cd97b15b6a53694020043b73a721e3a224abeb26`, image `public.ecr.aws/supabase/postgres:17.6.1.140`, remains running and healthy on `127.0.0.1:54322`.
- Auth `c2dc09c1e2c5fab6e3c1885f0c3852001b10106a51d19d9d46d58b2693d95310`, PostgREST `9f5a419221fb21de0553ee0210e2e4d08bd81678aac2fdfea9986b3c64a958bb`, and Kong `49665ede10bbab11c6319e3dc847f0aeabca07005409dc1f954a861b1a23ec81` remain exited.
- Port `54321` has no listener. No route-started API container existed to stop.
- Per the post-backup failure contract, the backup and partially migrated database are preserved for diagnosis; no rollback or deletion was attempted.

## Smallest required next decision

A separately reviewed correction must make the committed migration digest contract compatible with the frozen local pgcrypto schema, or an equally exact reviewed route must establish the missing prerequisite without changing private state. Until that durable correction is accepted, the remaining migrations, API starts, private provisioning, PWA build, and teaching URL remain held.

No tracked source edit or target commit.
No remote-reference publication.
No private account provisioning, real workbook import, policy activation, deployment, booking, or spend.
No cursor, protocol lock, dependency, browser, image, or unrelated cleanup action.

Cursor at send: 0
