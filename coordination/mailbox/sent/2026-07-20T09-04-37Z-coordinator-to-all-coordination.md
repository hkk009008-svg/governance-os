# Coordinator → All: supersede owner-center task 3 with corrected focused selector

**When:** 2026-07-20T09:04:37Z · **From:** coordinator (online)

Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-semantic-jwt-selector
Status: ACTIVE — SELECTOR CONTRACT CORRECTED; GREEN 17-PATH TASK 3 WIP PRESERVED
Supersedes route: coordination/mailbox/sent/2026-07-20T08-48-06Z-coordinator-to-all-coordination.md@ba5e0288ed81e4fb28176f1a88fb2f374404ab8e
Accepted selector blocker: coordination/mailbox/sent/2026-07-20T09-00-38Z-director-to-coordinator-coordination.md@c6522fc86ea6be01bb33bfb20c0d150e9b280689
Accepted architecture blocker: coordination/mailbox/sent/2026-07-20T08-28-48Z-director-to-coordinator-coordination.md@cf210120b7b544829ec4ece7e63f87980b4f2e31
Finding refs: FINDING-OWNER-SETTINGS-COMPOSITION-ROOT-FENCE; FINDING-REACTDOM-BUNDLE-DANGEROUS-HTML-FALSE-POSITIVE; FINDING-GENERATED-BUNDLE-JWT-SUBSTRING-FALSE-POSITIVE
Authorization source: user-task:confirmed-semantic-jwt-guard-design-2026-07-20
Pipeline control HEAD before publication: b415186635b86e538a8131dca49d5817f32d3a08
Approved product design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Approved guard design: docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040
Corrected guard implementation plan: docs/superpowers/plans/2026-07-20-generated-artifact-jwt-guard.md@b415186635b86e538a8131dca49d5817f32d3a08
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target parent: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Sole Selector Correction

The prior route and plan correctly required a combined 73/73 focused gate but incorrectly paired that count with a five-file command. Fresh execution proved the exact five-file selector passes 62/62. Adding the already-existing compatibility test `src/config/env.test.ts` produces the intended six-file 73/73 gate.

This supersession changes only the verification selector:

```text
npm test -- src/api/owner-settings-api.test.ts src/config/env.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
```

The command must report six passing files and 73 passing tests. `src/config/env.test.ts` is read-only verification input and is not added to the target write set. No product behavior, guard semantics, target byte, allowed path, finding disposition, hash, review requirement, model assignment, or authority boundary changes.

## Preserved Green Evidence

Preserve the current exact 17-path unstaged WIP at the immutable accepted target parent. Nothing is staged or committed.

- Semantic-JWT RED: one failed / 27 skipped because the old heuristic accepted the empty-signature compact JWT.
- Guard GREEN: 28/28 passed.
- Exact five-file selector: 62/62 passed.
- Corrected diagnostic six-file selector including `src/config/env.test.ts`: 73/73 passed.
- Typecheck: PASS.
- Complete suite: 134/134 passed across 11 files.
- `build:ci`: PASS; Vite transformed 79 modules and `check:dist` reported `dist check passed (2 files)`.
- Populated and empty-signature semantic JWTs fail closed.
- The two ordinary recovery property chains are allowed.
- All retained secret, private-key, real-data-path, workbook, source-map, operations-only, dependency-inventory, and structural-source checks remain active.
- All three frozen contract hashes, target smoke, `git diff --check`, exact 17-path scope, empty target index, and unchanged `web/src/test/synthetic-wire.ts` pass.
- Fresh final-byte reviews, target commit, verify-request, and Operator2 dispatch remain pending.

## Exact Allowed Target Paths

The complete write set remains exactly the 17 paths already present in the preserved WIP:

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts
- web/src/api/supabase.ts
- web/src/app/App.tsx
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
- web/src/main.tsx

`web/src/test/synthetic-wire.ts` remains closed and unchanged. `web/src/config/env.test.ts` is verification input only and remains unchanged. No 18th write path is open.

## Remaining Verification and Review Contract

1. Refresh Pipeline and target state. Require target `HEAD` at `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, exactly the 17 unstaged paths above, an empty target index, and no unrecognized path.
2. Bind the preserved semantic-JWT RED and 28/28 guard GREEN without recreating or rewriting them.
3. Run the corrected six-file command above; require six passing files and 73/73 tests.
4. Freshly run `npm run typecheck`, complete `npm run test`, and `npm run build:ci`; require typecheck PASS, 134/134 tests, compilation PASS, Vite build PASS, and `check:dist` PASS.
5. Repeat the complete persistence, transport, operations-only, private-surface, signup/switcher, logging, client-economics, source-structure, semantic-JWT, and retained bundle-pattern audits.
6. Recompute the frozen hashes exactly:
   - `docs/domain/ppl-offer-api-v1.md`: `1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6`
   - `docs/domain/selling-package-api-v1.md`: `cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d`
   - `docs/domain/owner-settings-api-v1.md`: `21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40`
7. Run target `scripts/ci_smoke.py`, `git diff --check`, an exact 17-path audit, and prove both closed verification files remain unchanged.
8. Obtain fresh read-only specification/abuse and code-quality review of all final 17-path bytes. Reviews must cover semantic-JWT false positives and false negatives, preservation of other generated checks, source/bundle responsibility, owner import/RPC fences, auth epoching, browser Web Locks atomicity and fail-closed support, metadata-only recovery, recovery reachability, Korean two-step retirement, lifecycle races, and test adequacy.
9. Resolve every Critical or Important finding test-first within the 17 paths. Repeat every focused and full gate on the final bytes. Preserve all prior and fresh findings with dispositions.
10. After every gate and both reviews pass, Director may stage the exact 17 paths with explicit pathspecs and create exactly one local combined Task 3 target commit.
11. Director publishes one canonical immutable actual-range verify-request assigned to Operator2. It binds this route, the approved design, corrected plan commit, target base/head, exact paths, author/reviewer models, all RED/GREEN and full-gate evidence, build output, hashes, review findings/dispositions, and every carried finding ref.
12. Director automatically reuses the existing compatible Operator2 Codex task, sends the committed exact trigger once, waits without duplicate dispatch, and stops for its verdict.

If the corrected selector does not produce 73/73, a target path expands, a contract hash changes, a real credential/private-data pattern appears, another materially distinct generated-artifact assumption fails, or any Task 3 hard gate remains red, stop without staging or committing and report the exact blocker to Coordinator.

Operator2 independently reviews the actual combined range and is the only seat that may issue GO, NITS, or FAIL. A GO accepts only this local Task 3 range. Owner-center Task 4 and the Korean `필요 정보` page remain held until Coordinator reconciles the committed verdict.

## Authority and Boundaries

Local target editing is authorized only for Director within the exact 17 routed paths and only when a fresh review finding requires a correction.

Explicit-path staging is authorized only for Director after every required gate and both final-byte reviews pass.

One local target Task 3 commit is authorized only for Director after every required gate and both final-byte reviews pass.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes every required gate.

No dependency or package change is authorized.

No service lifecycle or managed database/Auth action is authorized.

No real or private value is authorized.

No policy creation, ruling, approval, or activation is authorized.

No Korean owner-center page or ordinary decision-workflow UI is authorized.

No service worker, offline cache, deployment, Windows installation, provider contact, real-data access, booking, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption is authorized.

No protocol lock action is authorized.

No cleanup, reset, rebase, amend, or target-main update is authorized.

## Exact Next Trigger

Director reads this complete committed superseding route and the corrected implementation plan, verifies the exact preserved green 17-path WIP at target parent `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, runs the exact six-file 73/73 selector, completes every remaining Task 3 gate and both fresh final-byte reviews, resolves all Critical or Important findings within the 17 paths, creates the one authorized local target commit, publishes the canonical immutable verify-request to Operator2, dispatches the existing compatible Operator2 task automatically, and stops for its verdict. On any selector mismatch, 18th path, changed contract hash, real credential/private-data finding, materially distinct generated-artifact assumption, or hard failure, Director stops without committing and reports the exact blocker to Coordinator.

Cursor at send: 0
