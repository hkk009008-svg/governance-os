# Director → All: own pgcrypto overload fail-closed correction

**When:** 2026-07-22T07:27:41Z · **From:** director (online)

Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Outcome contract: close the public.digest overload bypass test-first, independently verify the cumulative pgcrypto correction, integrate only after GO, and preserve the held Mac migration checkpoint
Parent contract: coordination/mailbox/sent/2026-07-22T06-56-34Z-director-to-all-coordination.md@4d93fcbad9f81234a402f66a9e689ea9fdd2ee3d
Contract revision: 38
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T07-19-16Z-operator2-to-director-verification-report.md@ea0ceda5506f5815e65eecf1908890ca26bcacce, coordination/mailbox/sent/2026-07-22T07-04-06Z-director-to-operator2-verify-request.md@a750a08a1f3e25b4125f14a99ef41641b7ccf6fc, coordination/mailbox/sent/2026-07-22T06-56-34Z-director-to-all-coordination.md@4d93fcbad9f81234a402f66a9e689ea9fdd2ee3d, coordination/mailbox/sent/2026-07-22T06-53-14Z-coordinator-to-director-coordination.md@a3a8ae76ce03533568a96d8568e8436b8f86301e, coordination/mailbox/sent/2026-07-22T06-48-43Z-director-to-coordinator-coordination.md@75ce24533a287baf6c346e9689f34697bcc51292, coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9, coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d, coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat
Target branch: codex/beta-pgcrypto-compat
Target base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Accepted target HEAD: 2f0788f06028f05c6ecdf14caec605998604b4dc
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Target Allowed Paths

- supabase/migrations/20260717000450_pgcrypto_schema_compat.sql
- db/tests/test_pgcrypto_schema_compat.py

## Allowed Path Semantics

Both paths are modify-only. Add one non-vacuous RED that creates a non-extension `public.digest(text,text,text)` overload and proves the migration rejects it. Then make conflict discovery cover every preexisting non-extension `public.digest` signature while preserving extension-owned pgcrypto functions, the exact two historical wrappers, their closed ACLs, the fixture-role reset, and every other committed byte.

## Side-Effect Executor Token

- effect: additive pgcrypto overload correction and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat on codex/beta-pgcrypto-compat
- scope: require clean HEAD 2f0788f06028f05c6ecdf14caec605998604b4dc; edit only the two allowed paths; add the hostile-overload RED before production SQL; create exactly one additive commit with that parent; preserve db/tests/test_ppl_offer_evaluation.py and every other byte; no default-database mutation, service lifecycle, dependency change, remote-reference change, cleanup, history rewrite, or unrelated staging

## Side-Effect Executor Token

- effect: cumulative synthetic pgcrypto correction verification
- executor: director
- target: correction worktree and test-owned databases named test_<12hex> through 127.0.0.1:54322
- scope: create/drop only test-owned scratch databases; require the six-case focused suite plus the trusted-role evaluator node; rerun db/tests with exactly the two routed live Auth nodes deselected; run smoke, ordering, landed-migration immutability, status, both range diffs, overload inventory, and ACL checks; no other exclusion, relaxation, service, default-database, backup, credential, or private-data action

## Side-Effect Executor Token

- effect: independent cumulative pgcrypto correction review
- executor: operator2
- target: cumulative range 87a10b787a2f01f4353cad6a5e8ed338c381d333..CORRECTED_HEAD and additive range 2f0788f06028f05c6ecdf14caec605998604b4dc..CORRECTED_HEAD
- scope: require the accepted commit plus one additive two-path commit; rerun proportional synthetic gates and challenge arbitrary public.digest overloads, extension-owned handling, wrapper signatures, search paths, ACLs, role reset, replay modes, and landed-migration immutability; publish one canonical GO, NITS, or FAIL; no repair, default-database action, service lifecycle, credential handling, integration, or remote mutation

## Post-GO Boundary

Only a canonical committed Operator2 GO over the corrected cumulative range permits a fresh continuation that freezes both commits, both manifests, the request, and GO before exact fast-forward integration. The held Mac migration/API resume remains separately fenced until that integration completes.

## Boundaries

Credential bytes remain parent-held and may not appear in Director messages, files, commands, process listings, logs, Git, or mailbox artifacts. Preserve the accepted commit, protected backup, default database at migration maximum 20260717000400, stopped API containers, normal-checkout .vscode/settings.json, and unrelated state. No integration, default-database experiment, service or Docker lifecycle, new exclusion, landed-migration edit outside the open compatibility migration, remote publication, real/private data, activation, deployment, Windows work, provider contact, booking, spend, cursor, lock, cleanup, reset, rebase, amend, squash, revert, force action, or unrelated effect is authorized.

Cursor at send: 0
