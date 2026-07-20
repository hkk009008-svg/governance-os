# Coordinator → All: supersede owner-center task 3 with exact composition-root fence correction

**When:** 2026-07-20T07:29:49Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-session-recovery-fence-correction
Status: ACTIVE — ROOT CAUSE CONFIRMED; TWO-PATH FENCE CORRECTION OPEN; TASK 3 WIP PRESERVED
Supersedes route: coordination/mailbox/sent/2026-07-20T06-54-52Z-coordinator-to-all-coordination.md@63edecd75ed4730ff277d6010ff1e4d2ee89f1df
Accepted blocker report: coordination/mailbox/sent/2026-07-20T07-26-15Z-director-to-coordinator-coordination.md@b556105a48693543824ef7b7f6868e6666d86fea
Authorization source: user-task:continue-beta-critical-owner-center-task3-2026-07-20
Pipeline control HEAD before publication: b556105a48693543824ef7b7f6868e6666d86fea
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Task-5 Windows plan: docs/superpowers/plans/2026-07-17-ppl-offer-task5-windows-pwa.md@8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target parent: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra
Finding ref: FINDING-OWNER-SETTINGS-COMPOSITION-ROOT-FENCE

## Root-Cause Classification

The stopped full gate is deterministic and independently reproduced. `web/src/main.tsx` must construct the existing strict owner-settings adapter so the authenticated controller can load owner-settings status before exposing controls. The accepted `web/scripts/check-pwa-dist.mjs` instead rejects an `owner-settings-api` import from every production path whose filename does not contain `owner-settings`, including the one application composition root.

This is a source-fence overbreadth plus route-scope defect, not a reason to add a wrapper, bypass the fence, weaken the adapter inventory, or remove the runtime owner-settings capability. The Task 2 route prohibited exposure through ordinary PPL or selling-package consumers and required absence of operations-only names from feature/app sources; it did not prohibit the application composition root from constructing the reviewed third adapter. Owner-center Task 3 explicitly consumes all three literal adapters and requires owner-settings status after authentication.

The minimal causal correction changes the existing fence and its existing focused test. It permits exactly one static import of `./api/owner-settings-api` from exact `web/src/main.tsx`. Dynamic import, re-export, aliasing, imports from any other production path, operations-only names, direct `.rpc(` or `.from(` calls outside the accepted adapters, persistence/network sinks, and adapter-inventory drift remain rejected.

## Preserved TDD State

The target remains at the accepted parent with nothing staged or committed. Preserve the current 15 unstaged routed paths exactly as Task 3 work in progress:

- web/src/app/App.tsx
- web/src/main.tsx
- web/src/api/supabase.ts
- web/src/app/AppContext.tsx
- web/src/app/AppController.test.ts
- web/src/app/AppController.ts
- web/src/app/sensitive-state.ts
- web/src/features/auth/LoginView.tsx
- web/src/features/auth/session.test.ts
- web/src/features/auth/session.ts
- web/src/features/recovery/RecoveryPanel.tsx
- web/src/features/recovery/command-runner.test.ts
- web/src/features/recovery/command-runner.ts
- web/src/features/recovery/pending-journal.test.ts
- web/src/features/recovery/pending-journal.ts

The original focused RED remains valid: four collection failures caused only by missing routed production modules. Current focused GREEN is 25/25 and typecheck passes. The stopped complete suite is 113/115: the out-of-scope composition-root fence failure and the in-scope direct-call `App()` compatibility failure. Preserve this evidence; do not manufacture a second initial RED or discard/recreate the WIP.

## Superseding Target Allowed Paths

The complete allowed set is the prior 16 paths plus exactly these two causal correction paths:

- web/src/api/supabase.ts
- web/src/app/AppController.ts
- web/src/app/AppContext.tsx
- web/src/app/sensitive-state.ts
- web/src/features/auth/LoginView.tsx
- web/src/features/auth/session.ts
- web/src/features/recovery/pending-journal.ts
- web/src/features/recovery/command-runner.ts
- web/src/features/recovery/RecoveryPanel.tsx
- web/src/features/auth/session.test.ts
- web/src/features/recovery/pending-journal.test.ts
- web/src/features/recovery/command-runner.test.ts
- web/src/app/AppController.test.ts
- web/src/app/App.tsx
- web/src/main.tsx
- web/src/test/synthetic-wire.ts
- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts

No other target path is opened.

## Test-First Fence Correction

Before editing the guard, add focused assertions to `web/src/api/owner-settings-api.test.ts` that prove:

1. One exact static import of `./api/owner-settings-api` is accepted only when the inspected path is exact `web/src/main.tsx` or its normalized absolute equivalent.
2. The same import remains rejected from `App.tsx`, AppController, owner-settings feature files acting as ordinary consumers, PPL/selling adapters, and every other production path.
3. Dynamic imports, template imports, re-exports, export-star, computed paths, aliases, and alternate owner-adapter specifiers remain rejected even from `main.tsx`.
4. `main.tsx` gains no direct `.rpc(`, `.from(`, raw operations-only PPL name, command body persistence, or unreviewed transport construction.
5. The complete production-source scan passes only with the exact composition-root exception and still rejects a synthetic second import edge elsewhere.

Record the focused RED against the unchanged guard. Then implement one narrow guard change. Prefer an explicit static-import/composition-root decision over filename-substring bypasses or a new wrapper module. Do not exempt all files named `owner-settings`, all app files, all feature files, or all relative imports.

## In-Scope App Compatibility Correction

Preserve the accepted direct-call fail-closed shell contract used by `src/config/env.test.ts`: calling `App()` without a provider must return only `설정을 확인할 수 없습니다` and must not invoke a React context hook. Export a separate configured/provider-dependent component for runtime use and update `main.tsx` to render that component. Do not edit `src/config/env.test.ts`, suppress the test, catch an invalid hook call, or weaken the unavailable-state assertion.

## Resume and Verification Contract

1. Refresh Pipeline and target status. Require the target parent, the exact 15-path unstaged WIP above, nothing staged, and no unrecognized target change.
2. Add only the fence regression assertions and record their non-vacuous RED against the unchanged guard.
3. Implement only the narrow guard correction and the in-scope App static/configured split, then rerun the fence test, the four focused Task 3 tests, and typecheck.
4. Run complete `npm run test`, `npm run build:ci`, and the distribution/source guard. Require zero failures.
5. Repeat the route's persistence, RPC/from-call, dynamic/aliased import, operations-only name, private-value/logging, auth-persona, and client-economics negative scans.
6. Recompute the three frozen contract hashes and require exact equality with the prior route. Run target `scripts/ci_smoke.py`, `git diff --check`, and prove the actual diff is a subset of the 18 allowed paths with no package, lockfile, dependency, backend, docs, iOS, generated, build, real/private-data, or unrelated change.
7. Obtain fresh read-only specification/abuse and code-quality review of the complete final bytes. The specification review must explicitly decide whether the composition-root exception is exact and non-bypassable; the quality review must inspect normalized-path behavior, import/export syntax coverage, App hook safety, and all current Task 3 code.
8. Resolve every Critical or Important finding before commit. Preserve immutable finding refs and record every disposition.
9. After all gates pass, Director may stage with an explicit pathspec and create exactly one local target Task 3 commit containing the causal fence correction and completed Task 3. Publish one canonical Pipeline verify-request assigned to Operator2 and bind the exact base/head, actual paths, both REDs, all GREEN/full-gate evidence, frozen hashes, reviews, and this finding ref.

Operator2 independently reviews the actual combined Task 3 range and is the only seat that may issue GO, NITS, or FAIL. A GO accepts only this local range. Owner-center Task 4, Korean `필요 정보` UI, ordinary product workflow UI, integration, installation, real private values, policy activation, deployment, and publication remain held.

## Authority and Boundaries

Local target editing is authorized only for Director within the 18 routed paths, preserving the current Task 3 WIP.

Explicit-path staging is authorized only for Director after every required gate passes.

One local target Task 3 commit is authorized only for Director after every required gate passes.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes every required gate.

No wrapper/bootstrap module outside the 18 paths is authorized.

No dependency, service lifecycle, managed database/Auth, real/private-value, formula/risk policy, approval, ruling, activation, booking, or spend action is authorized.

No Korean owner-center page, ordinary decision-workflow UI, service worker, offline cache, deployment, or Windows installation is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, amend, or target-main update is authorized.

## Exact Next Trigger

Director reads this complete committed superseding route, verifies the exact preserved 15-path WIP at target parent `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, adds the two-path test-first composition-root fence correction, completes the in-scope App compatibility correction and every required Task 3 gate/review, creates the one authorized local target commit, publishes the canonical immutable verify-request to Operator2, dispatches the existing compatible Operator2 task automatically, and stops for its verdict. If the correction cannot remain exact within the 18 paths or any hard gate fails, Director stops without committing and reports the exact blocker to Coordinator.

Cursor at send: 0
