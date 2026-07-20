# Coordinator → All: supersede owner-center task 3 with semantic JWT artifact guard

**When:** 2026-07-20T08:48:06Z · **From:** coordinator (online)

Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-semantic-jwt-guard
Status: ACTIVE — ARCHITECTURE DESIGN CONFIRMED; SEMANTIC JWT ARTIFACT GUARD OPEN; TASK 3 WIP PRESERVED
Supersedes route: coordination/mailbox/sent/2026-07-20T07-43-25Z-coordinator-to-all-coordination.md@cd24fdc613ec91ebdf3c74d1981c5cb1507e125e
Accepted blocker report: coordination/mailbox/sent/2026-07-20T08-28-48Z-director-to-coordinator-coordination.md@cf210120b7b544829ec4ece7e63f87980b4f2e31
Carries finding refs: FINDING-OWNER-SETTINGS-COMPOSITION-ROOT-FENCE; FINDING-REACTDOM-BUNDLE-DANGEROUS-HTML-FALSE-POSITIVE
New finding ref: FINDING-GENERATED-BUNDLE-JWT-SUBSTRING-FALSE-POSITIVE
Authorization source: user-task:confirmed-semantic-jwt-guard-design-2026-07-20
Pipeline control HEAD before publication: a9ff9fecea92ae7b0e4c52a76b5445fd1e392193
Approved product design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Approved guard design: docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040
Guard implementation plan: docs/superpowers/plans/2026-07-20-generated-artifact-jwt-guard.md@a9ff9fecea92ae7b0e4c52a76b5445fd1e392193
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target parent: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Architecture Decision

The third stopping failure is deterministic and is not a credential leak. The generated-bundle expression `[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}` recognizes only three long dotted identifiers. It falsely matched these ordinary minified application property chains:

- `dependencies.commandRunner.retryConfirmedAbsent`
- `dependencies.commandRunner.retireConfirmedAbsent`

Generated output must still fail when it embeds a real compact JWT. A dotted string is now only a candidate. The guard classifies it as a JWT only when the first two segments are canonical unpadded Base64URL values, both decode as fatal UTF-8 JSON, and both decoded values are non-null objects rather than arrays or scalars. The third segment may contain Base64URL characters or be empty, so an unsecured compact JWT cannot evade the gate. This is credential-format detection, not signature verification.

Generated-output checks continue to own real credential and private-artifact formats. Structural application-source checks continue to own behavior and import boundaries. No generated filename, hash, byte offset, property name, occurrence count, React version, or current bundle is allowlisted.

## Preserved State and Evidence

Preserve the current exact 17-path unstaged WIP at the immutable accepted target parent. Nothing is staged or committed.

- All nine specification/abuse and code-quality findings from the prior final-byte reviews were addressed test-first within the 17 paths.
- Combined focused fix-wave suite: 72/72 passed.
- Complete suite: 133/133 passed.
- Typecheck: PASS.
- `git diff --check`: PASS.
- Build compilation and Vite bundling: PASS.
- Stopping gate: only `check:dist`, with exactly the two false-positive property chains above.
- `sb_secret_`, private-key, real-data-path, and `.xlsx` generated-output checks produced zero matches on the bundle and remain mandatory.
- The corrected bytes have not received the two fresh final reviews because the prior route required immediate stop at this architecture boundary.
- The three frozen domain-contract hashes remain unchanged.

## Exact Allowed Target Paths

The complete write set is narrowed to the 17 paths already present in the preserved WIP:

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

The semantic-JWT correction may newly edit only the already-open guard and guard-test paths:

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts

Fresh-review corrections may edit another path only if it is already one of the 17 above. `web/src/test/synthetic-wire.ts` is closed and must remain unchanged. No 18th path is open.

## Test-First Semantic JWT Correction

Follow the committed implementation plan exactly.

Before changing the guard, replace the current synthetic dotted-string expectation with focused assertions proving:

1. the two observed property chains and an ordinary long dotted identifier are allowed;
2. a realistic populated-signature compact JWT is rejected;
3. a compact JWT with an empty signature is rejected;
4. noncanonical Base64URL, invalid UTF-8, non-JSON, scalar-JSON, and array-JSON candidates are not classified as JWTs;
5. ReactDOM's internal raw-HTML token remains allowed in generated third-party output while application source remains structurally prohibited from using it; and
6. `sb_secret_`, private-key, real-data-path, and `.xlsx` patterns remain hard failures.

Record a non-vacuous RED against the unchanged dotted-string regex. Then make one coherent correction:

- use a compact three-segment candidate matcher with an empty-or-populated Base64URL signature segment;
- canonically decode and re-encode each of the first two Base64URL segments;
- decode with fatal UTF-8 and parse JSON;
- require both values to be non-null objects and reject arrays or scalar JSON;
- preserve the existing built-content failure message and every non-JWT built-content check; and
- expose only the smallest testable helper needed by the existing guard test.

Do not substitute an `eyJ` prefix regex, remove JWT detection, add a generated-output allowlist, weaken another bundle check, add a dependency, or change a third target file for this correction.

## Verification and Review Contract

1. Refresh Pipeline and target state. Require target `HEAD` at `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, exactly the 17 unstaged paths above, an empty target index, and no unrecognized path.
2. Record the semantic-guard RED, implement the approved correction, and require the complete owner guard file to pass 28/28.
3. Run the five-file combined focused suite from `web`; require 73/73.
4. Run `npm run typecheck`, complete `npm run test`, and `npm run build:ci`; require typecheck PASS, 134/134 tests, compilation PASS, Vite build PASS, and `check:dist` PASS.
5. Repeat the complete persistence, transport, operations-only, private-surface, signup/switcher, logging, client-economics, and source-structure audits from the original Task 3 route.
6. Recompute the three frozen hashes exactly:
   - `docs/domain/ppl-offer-api-v1.md`: `1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6`
   - `docs/domain/selling-package-api-v1.md`: `cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d`
   - `docs/domain/owner-settings-api-v1.md`: `21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40`
7. Run target `scripts/ci_smoke.py`, `git diff --check`, an exact 17-path audit, and prove `web/src/test/synthetic-wire.ts` is unchanged.
8. Obtain fresh read-only specification/abuse and code-quality review of all final 17-path bytes. Reviews must cover semantic-JWT false positives and false negatives, preservation of other generated checks, the source/bundle boundary, owner import/RPC fences, auth epoching, browser Web Locks atomicity and fail-closed support, metadata-only recovery, recovery reachability, Korean two-step retirement, lifecycle races, and test adequacy.
9. Resolve every Critical or Important finding test-first within the 17 paths. Repeat every focused and full gate on the final bytes. Preserve all prior and fresh findings with dispositions.
10. After every gate passes, Director may stage the exact 17 paths with explicit pathspecs and create exactly one local combined Task 3 target commit.
11. Director publishes one canonical immutable actual-range verify-request assigned to Operator2. It binds this route, approved design and plan commits, target base/head, exact paths, author/reviewer models, all RED/GREEN and full-gate evidence, build output, hashes, review findings/dispositions, and every carried finding ref.
12. Director automatically reuses the existing compatible Operator2 Codex task, sends the committed exact trigger once, waits without duplicate dispatch, and stops for its verdict.

If a real semantic JWT or any retained credential/private-data pattern appears, a target path expands, a contract hash changes, another materially distinct generated-artifact assumption fails, or any Task 3 hard gate remains red, stop without staging or committing and report the exact blocker to Coordinator.

Operator2 independently reviews the actual combined range and is the only seat that may issue GO, NITS, or FAIL. A GO accepts only this local Task 3 range. Owner-center Task 4 and the Korean `필요 정보` page remain held until Coordinator reconciles the committed verdict.

## Authority and Boundaries

Local target editing is authorized only for Director within the exact 17 routed paths.

Explicit-path staging is authorized only for Director after every required gate and both final-byte reviews pass.

One local target Task 3 commit is authorized only for Director after every required gate and both final-byte reviews pass.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes every required gate.

No dependency or package change is authorized.

No service lifecycle or managed database/Auth action is authorized.

No real or private value is authorized.

No policy creation, ruling, approval, or activation is authorized.

No Korean owner-center page or ordinary decision-workflow UI is authorized.

No service worker, offline cache, deployment, Windows installation, provider contact, real-data access, booking, or spend is authorized.

Evidence-ledger merge is not authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

Cursor consumption is not authorized.

No protocol lock action is authorized.

Cleanup, reset, rebase, amend, and target-main update are not authorized.

## Exact Next Trigger

Director reads this complete committed superseding route and the approved design and implementation plan, verifies the exact preserved 17-path WIP at target parent `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, implements only the test-first semantic-JWT generated-artifact correction within the already-open guard/test paths, reruns every Task 3 gate and both fresh final-byte reviews, creates the one authorized local target commit, publishes the canonical immutable verify-request to Operator2, dispatches the existing compatible Operator2 task automatically, and stops for its verdict. On any 18th path, materially distinct generated-artifact assumption, changed contract hash, real credential/private-data finding, or hard failure, Director stops without committing and reports the exact blocker to Coordinator.

Cursor at send: 0
