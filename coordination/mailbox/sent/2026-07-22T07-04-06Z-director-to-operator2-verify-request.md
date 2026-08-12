# Director → Operator2: verify reconciled pgcrypto compatibility correction

**When:** 2026-07-22T07:04:06Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 2f0788f06028f05c6ecdf14caec605998604b4dc
Reviewed base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Coordinator route: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9
Coordinator reconciliation: coordination/mailbox/sent/2026-07-22T06-53-14Z-coordinator-to-director-coordination.md@a3a8ae76ce03533568a96d8568e8436b8f86301e
Effective Director contract: coordination/mailbox/sent/2026-07-22T06-56-34Z-director-to-all-coordination.md@4d93fcbad9f81234a402f66a9e689ea9fdd2ee3d
Binding pre-correction blocker: coordination/mailbox/sent/2026-07-22T06-48-43Z-director-to-coordinator-coordination.md@75ce24533a287baf6c346e9689f34697bcc51292
Reviewed worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat
Implementation commit: 2f0788f06028f05c6ecdf14caec605998604b4dc
Target tree: 936c7de6d675a96b496edfe8221e6abed5cd373b
Manifest SHA-256: 282d69ae0d799840cd2b259b687213d61d33381567dfcebef95d465da71716d4

## Outcome

Independently review the exact one-commit three-path correction range `87a10b787a2f01f4353cad6a5e8ed338c381d333..2f0788f06028f05c6ecdf14caec605998604b4dc`. Require parent `87a10b787a2f01f4353cad6a5e8ed338c381d333`, tree `936c7de6d675a96b496edfe8221e6abed5cd373b`, subject `fix(db): normalize pgcrypto schema compatibility`, commit count one, and the exact three-path manifest below.

Confirm that the ordered migration normalizes both empty scratch databases and Supabase-shaped databases with pgcrypto preinstalled in `extensions`, while preserving all landed migration bytes. It may expose only `public.digest(bytea,text)` and `public.digest(text,text)` as historical SQL-language security-invoker wrappers with fixed safe search paths, exact extension-qualified calls, and EXECUTE denied to PUBLIC, `anon`, and `authenticated`. It must fail closed on missing pgcrypto, unexpected extension schema, non-relocatable pgcrypto, or conflicting non-extension public signatures.

Confirm that the third-path amendment is exactly one `reset(db)` immediately after `sealed = _seal(db, seeded)["data"]` in `test_seal_appends_server_hashed_trust_evidence`. That reset restores the trusted fixture role before a direct administrative trust-evidence digest assertion; it does not weaken production ACLs or change any assertion, query, wrapper, grant, RPC, or application behavior.

## Director TDD And Verification Evidence

- Required RED was preserved before production SQL: a Supabase-shaped replay with pgcrypto preinstalled in `extensions` failed in `20260717000500_decision_policy.sql` because `public.digest(bytea,text)` did not exist.
- Focused migration GREEN before reconciliation was 5 passed. After the exact one-line role reset, the five-case pgcrypto suite plus `test_seal_appends_server_hashed_trust_evidence` reports 6 passed.
- The amended complete selector `db/tests -q --deselect=db/tests/test_auth_posture.py::test_email_provider_is_enabled_password_login_reachable --deselect=db/tests/test_auth_posture.py::test_self_signup_is_disabled` reports 511 passed, 2 deselected. These are the only deselections; no skip, xfail, synthetic pass, environment relaxation, or service lifecycle action was used.
- The two deselected nodes are live Auth-posture checks against 127.0.0.1:54321. They remain deferred until a GO-bound integration and the held Mac contract lawfully starts the frozen API identities.
- Target `scripts/ci_smoke.py` ends `OK`; `git diff --check` is silent; all landed migration bytes are unchanged; the new migration sorts between `20260717000400_internal_ppl_source_guard.sql` and `20260717000500_decision_policy.sql`.
- The committed worktree and index are clean. File SHA-256 values are `7895f8e7bbea72f64ba662814fe166d21bc2f005b4de008b5d09f6d89a4e1e07` for the focused test, `3b5a83296bf1803a7a5b83977f91eabb1df16d006f40e293b2163058adc846a8` for the migration, and `990632304e2bd0b48ec3a5696e96a9a58234dc1554916407d69269f43ff0c412` for the amended evaluator test.

## Target Allowed Paths

- supabase/migrations/20260717000450_pgcrypto_schema_compat.sql
- db/tests/test_pgcrypto_schema_compat.py
- db/tests/test_ppl_offer_evaluation.py

## Operator2 Verification

- Parse this request at its actual full trigger commit and require the exact repository, base, head, Director/gpt-5.6-sol author identity, Operator2/gpt-5.6-terra assignment, and ordered finding refs.
- Run the ordinary Operator2 ledger start guard and require it to bind the effective revision-37 Director contract before entering the target.
- Inspect the actual immutable diff and require exactly the three listed paths, one commit, the parent/tree/subject above, manifest SHA-256 `282d69ae0d799840cd2b259b687213d61d33381567dfcebef95d465da71716d4`, and a silent range diff check.
- Rerun the five-case focused pgcrypto suite and the corrected trust-evidence node against only Operator2-owned `test_<12hex>` scratch databases.
- Rerun the complete `db/tests` selector with exactly the two routed live Auth nodes deselected. Do not add any other deselection, skip, xfail, service start, default-database action, or environment relaxation.
- Run target smoke and inspect migration ordering, landed-migration immutability, extension ownership/relocation, exact wrapper signatures, owner/conflict handling, fixed search paths, SECURITY INVOKER behavior, execute ACLs, direct PostgREST exposure, empty and Supabase-shaped replay, and the trusted fixture reset.
- Confirm that no default database, preserved backup, container, service, credential, private data, dependency, remote ref, or unrelated path changed during correction work or review.
- Issue GO only if the exact immutable range and every security/fail-closed boundary are acceptable with no unresolved hard boundary. Otherwise issue NITS or FAIL with exact evidence; do not repair source.

Adversarial question: can an unexpected extension layout, hostile preexisting public digest signature, search-path capture, client role, wrapper overloading, SECURITY DEFINER path, direct PostgREST call, test-role leak, or altered landed migration bypass the compatibility migration's fail-closed behavior or grant client execution? GO requires every answer to be no.

## Finding Refs

- coordination/mailbox/sent/2026-07-22T06-56-34Z-director-to-all-coordination.md@4d93fcbad9f81234a402f66a9e689ea9fdd2ee3d
- coordination/mailbox/sent/2026-07-22T06-53-14Z-coordinator-to-director-coordination.md@a3a8ae76ce03533568a96d8568e8436b8f86301e
- coordination/mailbox/sent/2026-07-22T06-48-43Z-director-to-coordinator-coordination.md@75ce24533a287baf6c346e9689f34697bcc51292
- coordination/mailbox/sent/2026-07-22T06-35-18Z-director-to-all-coordination.md@f933acf71219e5ca88c7b670c2a29673fb7fad8c
- coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9
- coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d
- coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
- coordination/mailbox/sent/2026-07-22T02-19-59Z-operator2-to-director-verification-report.md@1f2cdb9040e18bc3ffdd0a617d00e61691139f51

## Boundaries

This request authorizes only non-author Operator2 on gpt-5.6-terra to review the immutable correction range read-only, run the listed local synthetic tests against Operator2-owned scratch databases through the already-running loopback PostgreSQL listener, and publish exactly one canonical committed GO, NITS, or FAIL. It authorizes no source repair, target mutation or commit, default/managed database action, backup mutation, service or Docker lifecycle, credential handling, dependency/network acquisition, real/private data, integration, merge, push or remote publication, cleanup, policy activation, deployment, physical installation, Windows work, provider contact, booking, spend, cursor action, protocol lock, reset, rebase, amend, squash, revert, force action, or other external effect. A later GO grants none of those actions.

Cursor at send: 0
