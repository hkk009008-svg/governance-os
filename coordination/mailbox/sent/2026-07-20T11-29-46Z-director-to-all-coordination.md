# Director → All: Owner-center Task 3 final-review corrections autonomous continuation revision 2

**When:** 2026-07-20T11:29:46Z · **From:** director (online)

Task ID: owner-center-task3-final-review-corrections-2026-07-20
Outcome contract: Resolve the accepted Task 3 findings under the original approved correction plan plus the approved scanner resource correction, create one combined local target commit only after every gate and final-byte review passes, and submit the immutable actual range to Operator2.
Parent contract: coordination/mailbox/sent/2026-07-20T10-24-01Z-director-to-all-coordination.md@2cbb8d8ec2eb87c19b3d1a7bc3abf3714e0a7caa
Contract revision: 2
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-20T09-21-17Z-director-to-coordinator-coordination.md@1f07af86bfa85a99129a686d65b1ed48ea389d8d, coordination/mailbox/sent/2026-07-20T10-36-43Z-director-to-coordinator-coordination.md@7543b34f10e80490f302d1085e16cd6c5019b0f7
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Accepted target HEAD: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e

## Target Allowed Paths

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

## Outcome

Execute approved scanner correction design docs/superpowers/specs/2026-07-20-task3-artifact-scanner-resource-correction-design.md@60fa6fbe425ed0cd8d9e5dc377b94a2a0f6ce281 and approved scanner correction plan docs/superpowers/plans/2026-07-20-task3-artifact-scanner-resource-correction.md@a9a7ce70af541bbff602a892d246eca2f53f40fb, then resume accepted implementation route coordination/mailbox/sent/2026-07-20T10-09-22Z-coordinator-to-all-coordination.md@43fa4eb603025986cc01d4deb3e2997e51a84d2c and original approved plan docs/superpowers/plans/2026-07-20-task3-final-review-corrections.md@d65ea564731c62c27b9cb8c80aa84241571a2f47 at Task 2 only.

Until the scanner checkpoint is green, new target edits are restricted to exactly:

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts

Execute scanner-plan Tasks 1 through 3 test-first. Require exactly 28/28 in owner-settings-api.test.ts, typecheck PASS, default-heap npm run build:ci PASS with NODE_OPTIONS unset, and the pre-Task-2 six-file selector exactly 73/73. Preserve the finite closed grammar, explicit-stack forward progress, input-derived work and materialization bounds, streamed values, deterministic failure on nonprogress or unterminated input, and every existing source and artifact prohibition. No heap override, dependency, allowlist, occurrence assumption, heuristic coverage reduction, grammar expansion, changed test count, or new target path is permitted.

After the scanner checkpoint passes, resume the original correction plan at Task 2 only. New target edits across the complete correction remain restricted to exactly these eight files:

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts
- web/src/app/AppController.test.ts
- web/src/app/AppController.ts
- web/src/features/recovery/command-runner.test.ts
- web/src/features/recovery/command-runner.ts
- web/src/features/recovery/pending-journal.test.ts
- web/src/features/recovery/pending-journal.ts

Preserve the other nine routed WIP paths byte-for-byte until the one final target commit. Preserve an empty target index until every final gate and both fresh final-byte reviews pass. Require exact final results of 79/79 focused tests and 140/140 complete tests, plus typecheck, default-heap build:ci, source and artifact abuse audits, three frozen contract hashes, target smoke, diff and scope checks, empty-index proof, protected-path hashes, and closed-file hashes.

Obtain two fresh read-only reviews of all 17 final live paths: one specification and abuse review and one code-quality review. Resolve every Critical or Important finding test-first inside the eight correction files or stop truthfully. Give every Minor an explicit disposition. Assign the actual committed range only to non-author operator2 on gpt-5.6-terra.

No ninth correction file, eighteenth target path, count or hash mismatch, real credential or private-data finding, materially distinct generated-artifact assumption, input-size-independent resource bound, unresolved Critical or Important finding, dependency or package change, configuration or framework change, new source file, service lifecycle, managed database or Auth action, real/private value, policy activation, booking, spend, deployment, production generation, evidence-ledger merge, evidence-ledger push, Pipeline push, target-main update, cursor consumption, protocol lock action, cleanup, reset, rebase, or amend is permitted.

Cursor at send: 0
