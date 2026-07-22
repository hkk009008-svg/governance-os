# Coordinator → All: correct pgcrypto schema compatibility and resume Mac beta

**When:** 2026-07-22T06:30:45Z · **From:** coordinator (online)

Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Program board: ledger-beta-activation-2026-07-22
Status: ACTIVE — TEST-FIRST PGCRYPTO COMPATIBILITY CORRECTION, INDEPENDENT REVIEW, AND EXACT BETA RESUME
Route generation: 35
Supersedes route: coordination/mailbox/sent/2026-07-22T06-03-28Z-coordinator-to-all-coordination.md
Superseded route ref: coordination/mailbox/sent/2026-07-22T06-03-28Z-coordinator-to-all-coordination.md@da36b21029303939ddbd7d8ec1eace0ffcd8e7b2
Expected control HEAD: cd27af423803682f11a06de3de5de468d881310d
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Binding blocker: coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d
Held Mac contract: coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
Accepted Task 6 GO: coordination/mailbox/sent/2026-07-22T02-19-59Z-operator2-to-director-verification-report.md@1f2cdb9040e18bc3ffdd0a617d00e61691139f51
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Accepted target HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Correction worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat
Correction branch: codex/beta-pgcrypto-compat

## Coordinator Disposition

The Mac activation stopped correctly after a protected backup and five successful
migrations. The failing migration rolled back completely. The local default database
now has migration maximum `20260717000400`; database remains healthy; Auth,
PostgREST, and Kong remain stopped; no credential was handled.

The root cause is a replay-environment mismatch. The first historical migration uses
unqualified `create extension if not exists pgcrypto`: an empty scratch database installs
the extension in `public`, while the real Supabase default database already has the same
extension in `extensions`, making that statement a no-op. Later landed migrations
hard-code `public.digest`, so the first SQL-language function that resolves the symbol
fails on the real Supabase layout. Live evidence proves pgcrypto is in `extensions`, is
relocatable, and has the expected `digest(bytea,text)` and `digest(text,text)` overloads.

Do not edit any landed migration. Add one ordered compatibility migration before
`20260717000500` and one focused live replay test. This is the smallest correction that
preserves migration history, normalizes both replay environments, and keeps the public
compatibility surface explicitly privilege-closed.

## Outcome Contract

Create an isolated two-file correction at the exact accepted head using RED then GREEN.
The new migration normalizes pgcrypto to `extensions`, provides only the two historical
`public.digest` signatures as narrow fully-qualified invoker wrappers, and revokes client
execution. Prove a Supabase-shaped preinstalled-extension replay and the ordinary full DB
suite, obtain one binding Operator2 GO/NITS/FAIL, integrate only a GO-bound correction by
fast-forward, then resume the held Mac contract from its preserved backup and exact
partially migrated state.

## Director Autonomous Contract Revision 36

Before correction setup, Director publishes exactly one fresh director-to-all
coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-beta-pgcrypto-compat-2026-07-22
- Outcome contract: implement and independently verify the two-file pgcrypto schema compatibility correction, integrate only after GO, and resume the held Mac migration checkpoint
- Parent contract: this committed generation-35 Coordinator route exact path at its full commit SHA
- Contract revision: 36
- Previous owners: none
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: this route, the binding Mac migration blocker, the held revision-36 Mac contract, and the accepted Task 6 GO

Director proves the child effective, route validation true, global lineage valid,
Pipeline smoke green, and both Pipeline and target state exact before any mutation.

## Target Allowed Paths

- supabase/migrations/20260717000450_pgcrypto_schema_compat.sql
- db/tests/test_pgcrypto_schema_compat.py

## Allowed Path Semantics

Both paths are create-only and are the complete tracked correction write set. No landed
migration, fixture, application source, documentation, config, lockfile, ignored backup,
or private data may be edited. Create exactly one correction commit after all tests pass.

## Required RED And Root Fix

Add the focused test first. Its smallest failing case creates a test-owned scratch
database, precreates schema `extensions` and pgcrypto there as Supabase does, then replays
the repository migrations in order. Before the new migration exists, it must reproduce
the missing `public.digest(bytea,text)` failure at `20260717000500`. Preserve that RED
output as synthetic evidence only.

The new `20260717000450_pgcrypto_schema_compat.sql` then:

- requires pgcrypto to exist, be relocatable, and reside only in `public` or `extensions`;
- creates `extensions` when needed and moves a public-installed pgcrypto extension to
  `extensions`, while leaving an already-correct Supabase installation unchanged;
- fails closed on a missing extension, unexpected schema, non-relocatable extension, or
  conflicting non-extension `public.digest` signature;
- creates only `public.digest(bytea,text)` and `public.digest(text,text)`, both immutable,
  strict, parallel-safe, security-invoker SQL wrappers that call the corresponding fully
  qualified `extensions.digest` overload with a fixed safe search path;
- revokes all execution on both wrappers from PUBLIC, `anon`, and `authenticated`; and
- adds comments identifying the wrappers as historical migration compatibility, not a
  supported client RPC surface.

The GREEN test must prove the complete Supabase-shaped replay, normalized extension
namespace, exact two wrappers, digest equivalence, denied anon/authenticated execution,
and absence of any broader public digest overload. The ordinary full DB suite must also
pass, proving that moving the empty-scratch extension does not break historical triggers,
functions, RLS, or current APIs.

## Side-Effect Executor Token

- effect: isolated pgcrypto correction worktree implementation and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat on codex/beta-pgcrypto-compat
- scope: require normal main and HEAD exactly 87a10b787a2f01f4353cad6a5e8ed338c381d333 with only preserved `.vscode/`; create exactly the named worktree and branch from that head; write only the two create-only allowed paths using test-first discipline; create exactly one commit with parent 87a10b787a2f01f4353cad6a5e8ed338c381d333; no edit to an existing migration, default database mutation, dependency change, remote-reference change, worktree cleanup, history rewrite, or unrelated staging

## Side-Effect Executor Token

- effect: synthetic pgcrypto correction verification
- executor: director
- target: correction worktree and test-owned databases named test_<12hex> through the existing local listener at 127.0.0.1:54322
- scope: create and force-drop only test-owned scratch databases; preinstall pgcrypto in extensions only inside the focused reproduction database; run the focused RED/GREEN test, full DB suite, target smoke, diff checks, migration ordering and immutable-old-migration checks; never mutate the default database, existing backup, auth users, app.members, containers, services, real data, or ignored owner state

## Side-Effect Executor Token

- effect: independent pgcrypto correction review
- executor: operator2
- target: the exact one-commit two-file correction range in /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat and Operator2-owned test_<12hex> scratch databases
- scope: inspect the actual immutable diff and migration ordering; independently challenge unexpected extension schemas, extension ownership/relocation, wrapper replacement conflicts, search-path capture, execute grants, SECURITY DEFINER/INVOKER call paths, direct PostgREST exposure, standard scratch replay, Supabase-shaped replay, and old-migration immutability; run sufficient focused and full synthetic tests; publish exactly one canonical GO, NITS, or FAIL; do not repair source, mutate the default database, start or stop services, handle credentials, integrate, or alter a remote ref

## Post-GO Exact Integration Continuation

Only after a committed canonical Operator2 GO, Director publishes and commits one
revision-37 continuation for this correction task. It freezes the exact correction commit,
its parent/tree/subject/two-path manifest, the canonical verify-request and GO refs, and an
exact fast-forward token. It then integrates the one accepted commit into normal local
`main`, proving `.vscode/settings.json` unchanged, tracked/index state clean, and no other
branch, worktree, ref, or file changed.

## Side-Effect Executor Token

- effect: exact GO-bound local pgcrypto correction integration
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger:refs/heads/main
- scope: only under the effective correction revision-37 continuation; require main and HEAD exactly 87a10b787a2f01f4353cad6a5e8ed338c381d333 and the correction head to be its single child with exactly the two allowed paths and a canonical Operator2 GO; execute one git merge with fast-forward-only semantics to that frozen head; require main and HEAD equal that head, index/tracked diff empty, protected `.vscode/settings.json` hash unchanged, and no remote-reference publication or cleanup

## Held Mac Contract Revision 37 Resume

After the reviewed correction is integrated, Director publishes and commits one fresh
revision-37 continuation of the held task `ledger-beta-mac-activation-2026-07-22` whose
parent is
`coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd`.
It binds the correction route, correction commit, canonical GO, integration proof, binding
blocker, preserved backup hash, current migration maximum `20260717000400`, and all frozen
container identities from its parent. Owners remain Director; prior owner remains Director.

That continuation changes only the migration list. It requires the protected backup to
remain byte-identical and applies exactly these six remaining versions in order:

1. `20260717000450`
2. `20260717000500`
3. `20260717000600`
4. `20260718000100`
5. `20260718000200`
6. `20260720000100`

It then reuses the held contract's already-frozen Auth/PostgREST/Kong start token and
publishes the same non-secret migrated-and-ready checkpoint to Coordinator. The private
provisioning executor, ignored web build/preview token, Korean Mac teaching outcome,
failure/restoration contract, and Windows deferral remain unchanged.

## Side-Effect Executor Token

- effect: exact preserved-default-database migration resume
- executor: director
- target: frozen local evidence-ledger default Postgres database at 127.0.0.1:54322 and backup data/local-beta/mac-beta-pre-migration-20260722.dump
- scope: only under the effective held-task revision-37 continuation after the GO-bound correction is integrated; require database healthy, backup mode 0600 and SHA-256 5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793, migration maximum exactly 20260717000400, failed 20260717000500 objects absent, and Auth/PostgREST/Kong still stopped; apply exactly the six listed versions once and require final maximum 20260720000100; no reset, seed, rollback, deletion, real-data import, schema action outside those migrations, managed database, or migration outside this list

## Verification And Review Contract

Director's canonical verify-request binds the reviewed repository/worktree, exact base
and correction head, one-commit two-file manifest, RED evidence, both replay modes, full
DB/smoke/diff results, root-cause evidence, wrapper DDL and ACLs, implementation owner and
model, assigned Operator2 and model, and immutable finding refs. Director dispatches it
once to the existing compatible Operator2 task and reconciles only the committed report.

Any material finding is fixed test-first inside the same two-file write set, with affected
and full suites rerun and a fresh exact verify-request. A finding requiring an old migration
edit, third tracked path, default database experiment, configuration relaxation, or public
client grant stops for Coordinator reconciliation.

## Stop Boundary

No edit to any landed migration.
No source write outside the two new files.
No default database mutation before correction GO and integration.
No credential handling or account provisioning during correction work or review.
No container or Docker Desktop lifecycle action during correction work or review.
No real workbook import, owner-value entry, policy activation, deployment, Windows work,
provider contact, booking, spend, dependency/image acquisition, cursor action,
protocol-lock action, remote-reference publication, or unrelated cleanup.

## Exact Next Trigger

Director reads this committed generation-35 route, publishes and proves the correction
revision-36 child, implements the two-file fix RED-to-GREEN in the isolated worktree,
publishes the canonical verify-request, and dispatches it once to Operator2. After a
canonical GO only, Director freezes and performs the exact local integration, publishes
the held Mac revision-37 continuation, resumes the six exact migrations and frozen API
starts, and stops at the non-secret migrated-and-ready checkpoint for Coordinator's
private one-owner provisioning.

Cursor at send: 0
