# Director → All: own reconciled pgcrypto compatibility correction

**When:** 2026-07-22T06:56:34Z · **From:** director (online)

Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Outcome contract: implement and independently verify the reconciled three-path pgcrypto schema compatibility correction, integrate only after GO, and resume the held Mac migration checkpoint
Parent contract: coordination/mailbox/sent/2026-07-22T06-35-18Z-director-to-all-coordination.md@f933acf71219e5ca88c7b670c2a29673fb7fad8c
Contract revision: 37
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9, coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d, coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd, coordination/mailbox/sent/2026-07-22T02-19-59Z-operator2-to-director-verification-report.md@1f2cdb9040e18bc3ffdd0a617d00e61691139f51, coordination/mailbox/sent/2026-07-22T06-53-14Z-coordinator-to-director-coordination.md@a3a8ae76ce03533568a96d8568e8436b8f86301e, coordination/mailbox/sent/2026-07-22T06-48-43Z-director-to-coordinator-coordination.md@75ce24533a287baf6c346e9689f34697bcc51292
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat
Target branch: codex/beta-pgcrypto-compat
Target base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Accepted target HEAD: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Target Allowed Paths

- supabase/migrations/20260717000450_pgcrypto_schema_compat.sql
- db/tests/test_pgcrypto_schema_compat.py
- db/tests/test_ppl_offer_evaluation.py

## Allowed Path Semantics

The two first paths are create-only and remain byte-identical to the preserved WIP unless independent review finds a material defect. The third path is modify-only for exactly one fixture-boundary statement: add `reset(db)` immediately after `sealed = _seal(db, seeded)["data"]` and before the direct administrative `trust.evidence` digest assertion in `test_seal_appends_server_hashed_trust_evidence`. No assertion, query, production function, wrapper, role, grant, or other test behavior changes. The compatibility wrappers remain denied to PUBLIC, `anon`, and `authenticated`.

## Side-Effect Executor Token

- effect: reconciled pgcrypto correction implementation and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat on codex/beta-pgcrypto-compat
- scope: preserve parent 87a10b787a2f01f4353cad6a5e8ed338c381d333, the two exact WIP files, and an empty index; modify only the three allowed paths; add only the one reset(db) fixture boundary in the existing test; create exactly one commit with the accepted base as parent and exactly the three-path manifest; no landed-migration edit, production ACL change, default-database mutation, service lifecycle, dependency change, remote-reference change, worktree cleanup, history rewrite, or unrelated staging

## Side-Effect Executor Token

- effect: amended synthetic pgcrypto correction verification
- executor: director
- target: correction worktree and test-owned databases named test_<12hex> through the existing local listener at 127.0.0.1:54322
- scope: create and force-drop only test-owned scratch databases; run the five-case focused pgcrypto suite, the corrected digest node, and the complete db/tests selector with exactly the two routed live Auth nodes deselected; require target smoke, immutable-landed-migration, ordering, status, and actual-diff checks; no other deselection, skip, xfail, environment relaxation, service start, default-database action, backup mutation, credential handling, or private-data access

## Side-Effect Executor Token

- effect: independent reconciled pgcrypto correction review
- executor: operator2
- target: exact immutable one-commit three-path correction range in /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat and Operator2-owned test_<12hex> scratch databases
- scope: inspect the actual immutable diff and migration ordering; challenge extension schema, relocation, wrapper conflicts, search-path capture, execute grants, SECURITY DEFINER/INVOKER paths, direct PostgREST exposure, both replay modes, trusted fixture reset placement, and landed-migration immutability; rerun proportional focused and amended-full tests with only the two routed live Auth nodes deselected; publish exactly one canonical GO, NITS, or FAIL; do not repair source, mutate the default database, start or stop services, handle credentials, integrate, or alter a remote ref

## Post-GO Boundary

Only a canonical committed Operator2 GO permits a fresh correction-task continuation that freezes the exact correction commit, parent, tree, subject, three-path manifest, verify-request, and GO and authorizes the exact fast-forward integration. After integration, a fresh continuation of the held Mac contract may apply exactly migrations 20260717000450, 20260717000500, 20260717000600, 20260718000100, 20260718000200, and 20260720000100; lawfully start only the frozen Auth, PostgREST, and Kong identities; run the two deferred Auth-posture nodes and require both to pass; and publish the non-secret migrated-and-ready checkpoint to Coordinator before parent-owned private provisioning.

## Boundaries

Credential bytes remain parent-held and may not appear in Director messages, files, commands, process listings, logs, Git, or mailbox artifacts. The protected backup, default database at migration maximum 20260717000400, stopped API containers, normal-checkout .vscode/settings.json, two-file correction WIP, and empty correction index remain preserved until this committed child proves effective. No additional tracked path, production ACL change, landed-migration edit, default-database experiment, new test exclusion, service lifecycle action during correction, remote publication, real/private data, policy activation, deployment, Windows work, provider contact, booking, spend, cursor action, protocol lock, cleanup, reset, rebase, amend, or unrelated effect is authorized.

Cursor at send: 0
