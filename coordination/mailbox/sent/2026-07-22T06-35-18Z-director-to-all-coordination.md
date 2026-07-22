# Director → All: own pgcrypto compatibility correction

**When:** 2026-07-22T06:35:18Z · **From:** director (online)

Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Outcome contract: implement and independently verify the two-file pgcrypto schema compatibility correction, integrate only after GO, and resume the held Mac migration checkpoint
Parent contract: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9
Contract revision: 36
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9, coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d, coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd, coordination/mailbox/sent/2026-07-22T02-19-59Z-operator2-to-director-verification-report.md@1f2cdb9040e18bc3ffdd0a617d00e61691139f51
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

## Allowed Path Semantics

Both paths are create-only and form the complete correction write set. The correction is test-first and synthetic-only in the exact isolated worktree. No landed migration, default database, preserved backup, credential, container state, dependency, configuration, ignored owner state, private data, or unrelated path may be edited.

## Side-Effect Executor Token

- effect: isolated pgcrypto correction worktree implementation and one commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-pgcrypto-compat on codex/beta-pgcrypto-compat
- scope: require normal main and HEAD exactly 87a10b787a2f01f4353cad6a5e8ed338c381d333 with only preserved `.vscode/`; create exactly the named worktree and branch from that head; write only the two create-only allowed paths using RED-to-GREEN discipline; create exactly one commit with parent 87a10b787a2f01f4353cad6a5e8ed338c381d333; no edit to an existing migration, default database mutation, dependency change, remote-reference change, worktree cleanup, history rewrite, or unrelated staging

## Side-Effect Executor Token

- effect: synthetic pgcrypto correction verification
- executor: director
- target: correction worktree and test-owned databases named test_<12hex> through the existing local listener at 127.0.0.1:54322
- scope: create and force-drop only test-owned scratch databases; preinstall pgcrypto in extensions only inside the focused reproduction database; run the focused RED/GREEN test, full DB suite, target smoke, diff checks, migration ordering and immutable-old-migration checks; never mutate the default database, existing backup, auth users, app.members, containers, services, real data, or ignored owner state

## Review Boundary

After one verified correction commit, publish one canonical immutable request assigned to non-author Operator2 on gpt-5.6-terra and dispatch its exact trigger once. Integration, held Mac migration resume, and API starts remain fenced until a canonical committed GO and the exact revision-37 continuations required by the parent route.

## Boundaries

This continuation grants no authority beyond the committed parent route. No default database mutation, credential handling, account provisioning, Docker/container lifecycle, landed-migration edit, third target path, remote publication, dependency or image acquisition, real/private data, policy activation, deployment, Windows work, provider contact, booking, spend, cursor action, protocol lock, cleanup, reset, rebase, amend, or unrelated effect is authorized.

Cursor at send: 0
