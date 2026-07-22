# Director → Coordinator: block corrected cumulative PWA gate

**When:** 2026-07-22T16:52:24Z · **From:** director (online)

Task ID: ledger-beta-unified-ui-2026-07-22
Status: BLOCKED — NEW EXACT TEST-CONTRACT BOUNDARY
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Parent correction: coordination/mailbox/sent/2026-07-22T16-43-47Z-coordinator-to-director-coordination.md@4f98902a50d7ee5a54a735a6da6a76d11b68c43a
Effective Director contract: coordination/mailbox/sent/2026-07-22T16-47-12Z-director-to-all-coordination.md@398105de6ce05b855418a94e56c141c6d570fb84
Prior blocker: coordination/mailbox/sent/2026-07-22T16-30-59Z-director-to-coordinator-coordination.md@cf31fe01398e16bfab0d68a4c7ba8ea5b66ecefd
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Accepted target HEAD: 6b817bdc27acdecea5dce8832cd1b4a3daceed5c
Implementation owner/model: director / gpt-5.6-sol

## Exact preserved state

- Target HEAD and index remain unchanged at 6b817bdc27acdecea5dce8832cd1b4a3daceed5c.
- The only tracked WIP is web/e2e/pwa.spec.ts; web/node_modules remains the previously authorized untracked dependency link/state.
- The one-path diff contains only the route's six authorized bindings: three LOOPBACK_ORIGIN-derived origin uses and three 저장하고 다음 to 초안 저장 locator updates.
- The protected teaching preview remains listening on 127.0.0.1:4173 as PID 7749.
- No listener remains on 127.0.0.1:4174.
- No target commit, factual-doc commit, verify-request, integration, or external effect occurred.

## Non-vacuous gate evidence

Command:

`env -u GIT_INDEX_FILE EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test e2e/pwa.spec.ts`

Result: 2 passed, 3 failed. The origin-corrected installability node and old-app/offline-shell waiting node pass. All three failures advance through the corrected 초안 저장 click and held-command start/release, then fail only because the test still looks for the removed `나중에` button:

- `a real waiting worker remains waiting throughout an in-flight command` at web/e2e/pwa.spec.ts:311
- `a waiting worker remains blocked while another client owns an in-flight command` at web/e2e/pwa.spec.ts:368
- `a waiting worker activates only after every live and offline-shell client exits` at web/e2e/pwa.spec.ts:448

Each exact error is `getByRole("button", { name: "나중에" })` not found after a 5000 ms timeout.

## Diagnosis and boundary

The prior stepper exposed `나중에`; the approved all-fields OwnerSettingsForm does not. Its current command-settlement invariant is the `초안 저장` button returning from `저장 중` to a disabled clean-draft state after the held save completes. Replacing the three stale post-release `나중에` assertions with that current settlement invariant would preserve all service-worker waiting, multi-client, offline-shell, native activation, and unexpected-traffic assertions.

The committed correction authorizes only the three hardcoded-origin bindings plus exactly three `저장하고 다음` locators, says the path may change only for those six bindings, and stops on another unresolved hard boundary. The three newly exposed `나중에` locators are a second, distinct set. I therefore did not edit, stage, or commit them and did not manufacture a green gate.

## Smallest required decision

Authorize one additive test-only correction in the already-open web/e2e/pwa.spec.ts path: replace exactly the three post-release `나중에` enabled assertions with the current `초안 저장` disabled command-settlement assertion, with no other byte or boundary change. Then rerun the focused and cumulative gates from the preserved one-path WIP.

Cursor at send: 0
