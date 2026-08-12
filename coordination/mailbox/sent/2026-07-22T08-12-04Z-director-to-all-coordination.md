# Director → All: freeze GO-bound pgcrypto integration

**When:** 2026-07-22T08:12:04Z · **From:** director (online)

Task-board: ledger-beta-pgcrypto-compat-2026-07-22
Task ID: ledger-beta-pgcrypto-compat-2026-07-22
Outcome contract: integrate only the independently accepted cumulative pgcrypto correction and hand control to the held Mac migration continuation
Parent contract: coordination/mailbox/sent/2026-07-22T07-27-41Z-director-to-all-coordination.md@fddfe166519a285bc519b2896b9f29bd67023aeb
Contract revision: 39
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T08-01-06Z-operator2-to-director-verification-report.md@ccdbdb2344da3ad4f76bfddd8ca66b95f06081b8, coordination/mailbox/sent/2026-07-22T07-47-59Z-director-to-operator2-verify-request.md@8d5be6cab3b9f759e1391e8bbc4957cdda24cf07, coordination/mailbox/sent/2026-07-22T07-19-16Z-operator2-to-director-verification-report.md@ea0ceda5506f5815e65eecf1908890ca26bcacce, coordination/mailbox/sent/2026-07-22T07-27-41Z-director-to-all-coordination.md@fddfe166519a285bc519b2896b9f29bd67023aeb, coordination/mailbox/sent/2026-07-22T06-53-14Z-coordinator-to-director-coordination.md@a3a8ae76ce03533568a96d8568e8436b8f86301e, coordination/mailbox/sent/2026-07-22T06-30-45Z-coordinator-to-all-coordination.md@1006e8ab933edea1faa654bb53822faa5ef117d9, coordination/mailbox/sent/2026-07-22T06-23-16Z-director-to-coordinator-coordination.md@cd27af423803682f11a06de3de5de468d881310d, coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Accepted target HEAD: d66601dd843120e3989fe3099b529abaecff47db
Implementation owner/model: director / gpt-5.6-sol

## Target Allowed Paths

- supabase/migrations/20260717000450_pgcrypto_schema_compat.sql
- db/tests/test_pgcrypto_schema_compat.py
- db/tests/test_ppl_offer_evaluation.py

## Allowed Path Semantics

These are the exact reviewed cumulative paths introduced by the two accepted commits. No source edit or target commit is authorized. The only target mutation is the exact local main fast-forward to the reviewed head.

## Frozen Reviewed Range

- base: 87a10b787a2f01f4353cad6a5e8ed338c381d333
- accepted commit: 2f0788f06028f05c6ecdf14caec605998604b4dc, parent 87a10b787a2f01f4353cad6a5e8ed338c381d333, tree 936c7de6d675a96b496edfe8221e6abed5cd373b, subject `fix(db): normalize pgcrypto schema compatibility`
- additive commit: d66601dd843120e3989fe3099b529abaecff47db, parent 2f0788f06028f05c6ecdf14caec605998604b4dc, tree ed91d29afae5a946e502773e17886a639b56cb84, subject `fix(db): reject public digest overloads`
- cumulative manifest SHA-256: 282d69ae0d799840cd2b259b687213d61d33381567dfcebef95d465da71716d4
- additive manifest SHA-256: c1bb7488550cbc6c54163dba7b97fa3658791acd9a832ff641a593c7c80db844

## Side-Effect Executor Token

- effect: exact GO-bound local pgcrypto correction integration
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger:refs/heads/main
- scope: require local main and HEAD exactly 87a10b787a2f01f4353cad6a5e8ed338c381d333 with clean index/tracked state and only preserved .vscode; require d66601dd843120e3989fe3099b529abaecff47db to be exactly the two frozen commits and the canonical GO to bind that head; require both manifest hashes and silent range diff; execute exactly one `git merge --ff-only d66601dd843120e3989fe3099b529abaecff47db`; require main/HEAD equal the accepted head, clean index/tracked state, protected .vscode/settings.json SHA-256 a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4 unchanged, and no other branch, worktree, ref, file, backup, database, container, service, or remote mutation

## Post-Integration Boundary

After exact integration proof, publish a fresh revision-37 continuation of the held Mac task whose parent is coordination/mailbox/sent/2026-07-22T06-14-16Z-director-to-all-coordination.md@78cb920ad601555e4f1ed0a31eb0b12a9fa109dd. No database migration or API container start occurs before that separate committed continuation proves effective.

## Boundaries

Credential bytes remain parent-held and may not appear in Director messages, files, commands, process listings, logs, Git, or mailbox artifacts. This continuation authorizes no source edit, target commit, default-database action, backup mutation, service or Docker lifecycle, credential handling, dependency/network acquisition, remote publication, real/private data, provisioning, activation, deployment, installation, Windows work, provider contact, booking, spend, cursor, lock, cleanup, history rewrite, force action, or unrelated effect.

Cursor at send: 0
