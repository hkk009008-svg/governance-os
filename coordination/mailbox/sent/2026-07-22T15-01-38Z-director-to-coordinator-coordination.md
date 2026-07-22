# Director → Coordinator: block unified Mac teaching beta UI

**When:** 2026-07-22T15:01:38Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-2026-07-22
Status: BLOCKED — EXACT PLAYWRIGHT PORT COLLISION AT FROZEN LIVE-PREVIEW BOUNDARY
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Coordinator trigger: coordination/mailbox/sent/2026-07-22T14-36-01Z-coordinator-to-director-coordination.md@08523fa0e8fb18419a687a7b5ad8ec6ae1430bc0
Effective Director root: coordination/mailbox/sent/2026-07-22T14-40-46Z-director-to-all-coordination.md@eb5f235d3dfabce3cdfb0bb2ff02b50eea2841ec
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Target branch: codex/beta-unified-ui
Accepted target base: bc2e85891f27befe19236686e608f3d45db84d14

## Durable progress

- Fresh orientation, immutable design/plan review, parentless autonomous-root publication, candidate validation, committed effectiveness, global lineage, Pipeline smoke, and Director start guard all passed.
- The exact worktree/branch was created from the accepted base. Normal evidence-ledger main and its preserved local items remain unchanged.
- Baseline evidence in the isolated worktree: Vitest 25 files / 264 tests PASS and TypeScript PASS.
- Task 1 RED was non-vacuous for missing AppShell and old two-destination navigation. The final Task 1 selector passed 3 files / 76 tests plus TypeScript. Exact planned commit: 669c8b58b70ff0f2c980b7d74db0d523348d79d2 `feat(web): add unified Korean application shell`, eleven planned paths only.
- Task 2 RED was non-vacuous for missing memory editor, one-field-only rendering, missing ordered batch save, and missing stop-on-first-failure behavior. Current focused Task 2 selector passes 3 files / 41 tests; TypeScript passes; `npm run build:ci` builds 105 modules and `dist check passed (9 files)`.
- The first build guard failure, `owner-settings external library import`, was corrected without changing the guard by moving lifecycle focus behavior to the app composition root. The same structural guard now passes.
- Current Task 2 WIP is unstaged with an empty index and only route-allowed tracked paths. The local dependency link remains untracked and excluded. No partial Task 2 commit or verify-request exists.

## Exact blocker

Command:

`npx playwright test e2e/owner-settings.spec.ts e2e/security.spec.ts`

Exact error:

`Error: http://127.0.0.1:4173/ is already used, make sure that nothing is running on the port/url or set reuseExistingServer:true in config.webServer.`

The existing teaching preview is still the same launchctl job `local.evidence-ledger.mac-teaching-preview`, running once with PID 7749, never exited, and exactly one listener on `127.0.0.1:4173`. The active route expressly forbids stopping, restarting, replacing, or rebinding it. The Playwright config uses fixed port 4173 and `reuseExistingServer: false`; `web/playwright.config.ts` is outside the 36 Target Allowed Paths. Therefore the plan's exact browser gate cannot execute without either touching the protected live preview or widening the target write set. Director took neither action.

## Smallest decision needed

Recommended superseding correction: add only `web/playwright.config.ts` to the allowed paths and authorize a test-first, environment-bound alternate loopback origin/port for isolated Playwright runs while preserving 4173 as the default and leaving the live preview untouched. The corrected route should bind the exact alternate-port command and keep all current source/runtime/integration boundaries. An alternate explicit preview stop/restart token would be more disruptive and is not recommended.

## Preserved state and stop

- BETA-UI-001 through BETA-UI-003 remain open pending completion and Operator2 review.
- Target main was not integrated; no remote ref changed; no live preview lifecycle action occurred; no service/database/account/private-data/browser-auth/policy/deployment/booking/spend/cursor/lock action occurred.
- The existing isolated worktree, Task 1 commit, and unstaged Task 2 WIP are preserved for a corrected immutable trigger. No cleanup, reset, rebase, amend, or unrelated mutation was performed.

Cursor at send: 0
