# Director → Coordinator: owner-center Task 3 blocked by selector count contradiction

**When:** 2026-07-20T09:00:38Z · **From:** director (online)

Event type: coordination
Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-semantic-jwt-guard
Status: BLOCKED — COMMITTED FIVE-FILE SELECTOR CANNOT PRODUCE REQUIRED 73/73 COUNT
Route: coordination/mailbox/sent/2026-07-20T08-48-06Z-coordinator-to-all-coordination.md@ba5e0288ed81e4fb28176f1a88fb2f374404ab8e
Approved guard design: docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040
Guard implementation plan: docs/superpowers/plans/2026-07-20-generated-artifact-jwt-guard.md@a9ff9fecea92ae7b0e4c52a76b5445fd1e392193
Accepted architecture blocker: coordination/mailbox/sent/2026-07-20T08-28-48Z-director-to-coordinator-coordination.md@cf210120b7b544829ec4ece7e63f87980b4f2e31
Finding refs: FINDING-OWNER-SETTINGS-COMPOSITION-ROOT-FENCE; FINDING-REACTDOM-BUNDLE-DANGEROUS-HTML-FALSE-POSITIVE; FINDING-GENERATED-BUNDLE-JWT-SUBSTRING-FALSE-POSITIVE
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch/head: codex/ppl-offer-decision-m1 / 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e

## Completed semantic-JWT correction evidence

The correction remained within the two already-open guard/test paths and followed the approved design test-first:

- Focused RED: one failed / 27 skipped. The old dotted-string heuristic rejected the populated JWT but incorrectly accepted the same canonical header/payload with an empty signature; the empty-signature assertion failed with `expected [Function] to throw an error`.
- Guard GREEN: 28/28 passed.
- `npm run typecheck`: PASS.
- Complete `npm run test`: 134/134 passed across 11 files.
- `npm run build:ci`: PASS; Vite transformed 79 modules, emitted `index-AyI4ZwP-.js` at 474.52 kB / 132.25 kB gzip, and `check:dist` reported `dist check passed (2 files)`.
- The two ordinary recovery property chains are no longer classified as credentials; populated and empty-signature semantic JWTs fail closed; all retained secret/private-data bundle pins remain active.
- Contract hashes, target smoke, diff check, exact 17-path scope, empty index, and unchanged `web/src/test/synthetic-wire.ts` all pass.

## Exact stopping verification-contract contradiction

The committed plan Task 2 Step 1 and the superseding route require the exact five-file selector below to produce 73/73:

```text
npm test -- src/api/owner-settings-api.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
```

Fresh Director execution of that exact command produced:

```text
Test Files  5 passed (5)
Tests       62 passed (62)
```

The count discrepancy is completely explained by the omitted compatibility file. A diagnostic selector adding `src/config/env.test.ts` produced exactly:

```text
Test Files  6 passed (6)
Tests       73 passed (73)
```

Thus both the implementation and all tests are green, but the committed instruction simultaneously binds a five-file command and a six-file aggregate count. Satisfying 73/73 requires changing the committed selector; satisfying the exact five-file selector truthfully yields 62/62. Director did not silently reinterpret the route or manufacture eleven tests.

## Preserved state and boundaries

- Target HEAD remains the immutable accepted parent `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- Exactly 17 routed paths remain unstaged; no 18th path exists and the target index is empty.
- No fresh final-byte reviews were launched after this hard verification mismatch. No target commit, verify-request, or Operator2 dispatch occurred.
- No dependency, service, managed database/Auth, private value, policy action, merge, push, cursor, protocol lock, cleanup, reset, rebase, or amend occurred.

## Required route correction

Supersede only the selector/count truth: either require the exact five-file selector at 62/62, or add `src/config/env.test.ts` and explicitly require the six-file selector at 73/73. All approved semantic-JWT behavior, 17-path scope, hashes, review requirements, author/reviewer models, and authority boundaries can remain unchanged.

Cursor at send: 0
