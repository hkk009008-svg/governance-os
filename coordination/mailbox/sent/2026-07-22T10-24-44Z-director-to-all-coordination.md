# Director → All: claim Mac biz schema review root

**When:** 2026-07-22T10:24:44Z · **From:** director (online)

Task-board: ledger-beta-mac-biz-schema-review-2026-07-22
Task ID: ledger-beta-mac-biz-schema-review-2026-07-22
Outcome contract: correct the web composition root so every product RPC invoker selects exposed schema biz while Auth remains on the base client, obtain independent non-author Operator2 review of the immutable correction, and stop before integration or private browser acceptance
Parent contract: none
Contract revision: 0
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T10-19-17Z-coordinator-to-director-coordination.md@e38f5d71856e617bfe4a82e4dc214f0d87525cd2, coordination/mailbox/sent/2026-07-22T10-09-21Z-director-to-coordinator-coordination.md@c319cc391ea8c500eef3797716ab290800c91899, coordination/mailbox/sent/2026-07-22T09-48-59Z-operator2-to-director-verification-report.md@91ca275ae0a779c26799f5f83167998ee1211e4d
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Binding finding: MAC-BETA-BIZ-RPC-001
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-biz-schema-review
Target branch: codex/beta-mac-biz-schema-review
Target base: e4ddbf69cf4ed401289d719cc4910cae66e3833b
Accepted target HEAD: e4ddbf69cf4ed401289d719cc4910cae66e3833b

## Evidence Disposition

Accept the committed Coordinator evidence. The authenticated startup RPCs were issued against PostgREST's default `public` schema because `web/src/main.tsx` cast the base Supabase client directly to all three product RPC invoker interfaces. The product functions exist under exposed schema `biz`; Auth itself must remain on the unchanged base client. Existing synthetic browser replacement tests do not exercise this composition boundary.

The approved correction design is one schema-scoped product client derived from the base Supabase client through the literal exposed schema `biz`; all PPL, Selling Package, and Owner Settings adapters receive only that derived client, while `AppController.auth` continues to receive `client.auth`. Strict decoders, literal RPC inventories, transport behavior, and every product rule remain unchanged.

## Target Allowed Paths

- web/src/main.tsx
- web/src/api/supabase.ts
- web/src/api/supabase.test.ts

## Allowed Path Semantics

`web/src/api/supabase.test.ts` is create-only and owns non-vacuous synthetic request-profile and composition-wiring regression evidence. `web/src/api/supabase.ts` may add only the literal `biz` schema-selection helper. `web/src/main.tsx` may only route the three existing product adapters through that helper while preserving Auth on the base client. No adapter, decoder, controller, domain, PWA, configuration, package, lockfile, backend, migration, documentation, or other path may change.

## Side-Effect Executor Token

- effect: isolated test-first Mac biz-schema correction and one local target commit
- executor: director
- target: branch `codex/beta-mac-biz-schema-review` at `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-biz-schema-review`, created only from `e4ddbf69cf4ed401289d719cc4910cae66e3833b`
- scope: only after this autonomous root is committed, structurally valid, directly effective, globally lineage-valid, smoke-green, and bound by the Director ledger start guard; require the branch and path absent before creation and preserve normal main, `.vscode/`, the running local DB/Auth/PostgREST/Kong set, and the teaching preview; create the one isolated worktree without cleanup or broad prune; reuse only the existing dependency donor through one ignored `web/node_modules` symlink and acquire nothing; work strict RED to GREEN only in the three allowed paths; the RED must prove an actual product RPC request lacks the `biz` profile before production correction and the wiring regression must pin one `biz` product client for PPL, Selling Package, and Owner Settings while Auth stays on the base client; implement the smallest literal-schema helper and wiring change; run the focused test, full web suite, typecheck, production build and distribution checks with synthetic public values, diff/scope/secret scans, and target smoke; create exactly one local target commit with subject `fix(web): select biz schema for product RPCs`; if any required change leaves the three paths, any dependency is missing, any private value appears, any service or preview changes, or any hard gate fails, do not commit and publish one exact blocker

## Side-Effect Executor Token

- effect: independent actual-range review of the Mac biz-schema correction
- executor: operator2
- target: the immutable one-commit evidence-ledger range `e4ddbf69cf4ed401289d719cc4910cae66e3833b..CORRECTION_HEAD` in the routed worktree
- scope: only after the Director target commit and canonical committed verify-request exist; reuse or create exactly one compatible Operator2 task and dispatch the exact committed request once; require Operator2/gpt-5.6-terra to bind the exact repository/base/head/author/model/three-path manifest and finding evidence, inspect actual bytes, independently prove all product RPCs select `biz`, Auth remains on the base client, default-public and alternate-schema regressions fail closed, strict decoders and RPC inventories remain unchanged, and no credential/private-data/service boundary was crossed; use only synthetic public values, the existing dependency donor, tests, typecheck, build/distribution/static checks, diff/scope/secret scans, and target smoke; publish exactly one canonical GO, NITS, or FAIL; do not repair, integrate, mutate a service/database/preview, authenticate, handle credentials or private values, acquire dependencies, push, clean, consume cursors, or take locks

## Stop Boundary

Director may create the isolated worktree, implement and commit the exact correction, publish the immutable verify-request, route it once, reconcile the committed Operator2 verdict, and publish durable progress, blocker, or completion evidence. This root grants no target-main integration, preview rebuild/restart, browser authentication, private live acceptance, service lifecycle, default/managed database mutation, source change outside the three paths, dependency or network acquisition, real/private data handling, policy activation, Windows work, deployment, physical installation, remote publication, booking, spend, cursor, lock, cleanup, force action, or history rewrite. The existing services and teaching preview remain running. Coordinator retains the private browser acceptance, including the later proof that the three startup RPCs avoid `PGRST202`, the Korean `필요 정보` page renders, all ten server-ordered fields are visible, and current input remains empty without value entry or policy activation; that acceptance requires separately authorized integration/preview rebinding after a canonical GO.

Cursor at send: 0
