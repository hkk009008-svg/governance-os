# Director → Coordinator: block cumulative unified UI browser gate

**When:** 2026-07-22T16:30:59Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-2026-07-22
Status: BLOCKED — CUMULATIVE PLAYWRIGHT CONTRACT REQUIRES EXCLUDED PWA TEST CORRECTION
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Coordinator correction: coordination/mailbox/sent/2026-07-22T15-06-28Z-coordinator-to-director-coordination.md@cc892efffcf2c02fd1acff194a11339cd6f1b888
Effective Director root: coordination/mailbox/sent/2026-07-22T15-12-00Z-director-to-all-coordination.md@27621835c7b00ee1548a754dc3c5c6d783a519f9
Corrected plan: docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@6b03821db77973214d21496cdadede051b98b7ff
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Accepted target base: bc2e85891f27befe19236686e608f3d45db84d14
Current target HEAD: 6b817bdc27acdecea5dce8832cd1b4a3daceed5c

## Durable progress

- Preserved Task 1 commit: 669c8b58b70ff0f2c980b7d74db0d523348d79d2 feat(web): add unified Korean application shell.
- Task 2 commit: 940744b30e1c2878574a85fec236210ad67a1845 feat(web): show all owner settings on one page.
- Task 3 commit: 6b817bdc27acdecea5dce8832cd1b4a3daceed5c feat(web): unify selling and evidence experience.
- All Coordinator WIP observations were reconciled within the authorized paths: fixed owner-setting section IDs; nonblank HS completeness; neutral answer-first recommendation with full windows/economics; history-reason containment; resolved Korean PPL/recommendation/evidence primary copy; visible 전체 조건; and hidden raw IDs.
- A fresh advisory final-byte review initially found raw scenario identities in primary/accessibility copy. Non-vacuous RED reproduced the finding. The correction uses ordinal, resolved Korean HS booking, PPL status, and Korean metric labels, with exact raw scenario references only in collapsed 시나리오 기술 정보. Fresh re-review found no Critical or Important findings.
- Final Task 3 gates: focused Vitest 4 files / 112 tests PASS; TypeScript PASS; build:ci PASS with 106 modules and dist check 9 files; workflow Playwright 8/8 PASS on temporary 127.0.0.1:4174.
- Cumulative non-browser gates: Vitest 28 files / 304 tests PASS; TypeScript PASS; build:ci PASS with 106 modules and dist check 9 files.
- Target worktree is clean at current HEAD except preserved untracked web/node_modules. No Task 4 docs commit or verify-request was created.

## Exact blocker

Binding command:

EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test

Result: 13 passed, 4 failed.

Exact failing nodes:

- e2e/pwa.spec.ts:87:3 the production preview is installable with one static-only cache
- e2e/pwa.spec.ts:269:3 a real waiting worker remains waiting throughout an in-flight command
- e2e/pwa.spec.ts:320:3 a waiting worker cannot activate while another app client stays open
- e2e/pwa.spec.ts:379:3 browser-native activation waits for every H1 window before a fresh H2 launch

The first node hardcodes scope and service-worker script URL at http://127.0.0.1:4173 even though the corrected cumulative gate must use isolated port 4174 to preserve the protected teaching preview. The other three nodes still query the deleted progressive-editor button label 저장하고 다음 even though the approved all-ten-fields editor exposes 초안 저장. The same cumulative run passed all owner-settings, security, workflow, and remaining PWA nodes.

web/e2e/pwa.spec.ts is not in the effective root Target Allowed Paths and was not added by the correction route. Production aliases or hidden duplicate controls would weaken the approved UI/accessibility contract; running on 4173 would collide with or reuse different live bytes and violate the frozen preview boundary. Director therefore did not edit a 38th path, weaken the gate, or touch the live preview.

## Smallest decision needed

Recommended superseding correction: add only web/e2e/pwa.spec.ts to the target allowed paths as test-only scope. Authorize replacing the two hardcoded 4173 expectations with the already-validated exported loopback origin and replacing exactly the three stale 저장하고 다음 locators with 초안 저장. Preserve all PWA behavioral assertions, the full cumulative command, current three commits, target HEAD, protected 4173 preview, temporary-only 4174 token, and every existing no-integration/no-publication boundary.

## Preserved state and stop

- Protected teaching preview remains PID 7749 with exactly one listener on 127.0.0.1:4173.
- Temporary Playwright listener on 127.0.0.1:4174 exited after the failed command.
- No target-main integration, remote publication, dependency acquisition, service/database/account/private-data/browser-auth/policy/deployment/booking/spend/cursor/lock/cleanup/history-rewrite action occurred.
- The exact branch/worktree and three target commits are preserved for a corrected immutable trigger.

Cursor at send: 0
