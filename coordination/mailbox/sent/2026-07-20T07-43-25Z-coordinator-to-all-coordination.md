# Coordinator → All: supersede owner-center task 3 with source-level raw-html guard correction

**When:** 2026-07-20T07:43:25Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-reactdom-source-guard
Status: ACTIVE — REACTDOM FALSE POSITIVE CONFIRMED; SOURCE-LEVEL GUARD CORRECTION OPEN; TASK 3 WIP PRESERVED
Supersedes route: coordination/mailbox/sent/2026-07-20T07-29-49Z-coordinator-to-all-coordination.md@4126a40ba8e3d9370320aee4f85b7e3b7aac86bf
Accepted blocker report: coordination/mailbox/sent/2026-07-20T07-40-42Z-director-to-coordinator-coordination.md@1e60781a636baf0ebb0d19cfa358c8e6dff45b58
Carries finding ref: FINDING-OWNER-SETTINGS-COMPOSITION-ROOT-FENCE
New finding ref: FINDING-REACTDOM-BUNDLE-DANGEROUS-HTML-FALSE-POSITIVE
Authorization source: user-task:continue-beta-critical-owner-center-task3-2026-07-20
Pipeline control HEAD before publication: 1e60781a636baf0ebb0d19cfa358c8e6dff45b58
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target parent: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Root-Cause Classification

The stopped build is deterministic. Typecheck and Vite compilation succeed, then the accepted distribution guard rejects the literal token `dangerouslySetInnerHTML` anywhere in generated JavaScript. Task 3 lawfully makes ReactDOM reachable, so the bundled third-party ReactDOM implementation contains 12 instances. The complete routed production source contains zero instances.

The security requirement is that application source must never use React's raw HTML injection surface. A generated-bundle substring scan cannot express that boundary once ReactDOM is bundled because it cannot distinguish application code from the library implementing React. The causal correction moves this one prohibition to structural scanning of production TypeScript/TSX source while preserving the bundle checks that remain meaningful for secrets, credentials, private keys, real-data paths, source maps, and operations-only RPC names.

This correction does not authorize HTML injection, a sanitizer, raw HTML rendering, a new dependency, a bundle allowlist keyed to a generated hash, deletion of the distribution guard, or suppression of `check:dist`.

## Preserved Green Evidence and WIP

Preserve the current exact 17-path unstaged WIP at the immutable accepted parent. Nothing is staged or committed.

- Composition-root fence correction: 22/22 passed.
- App static/configured compatibility: 21/21 passed.
- Task 3 focused suite: 25/25 passed.
- Typecheck: PASS.
- Complete test suite: 119/119 passed across 11 files.
- Build compilation: PASS; Vite transformed 78 modules and emitted the bundle.
- Stopping gate: `check:dist` only, with 12 ReactDOM-internal `dangerouslySetInnerHTML` tokens and zero routed production-source occurrences.
- The three frozen domain-contract hashes remain unchanged.

The complete allowed write set remains the same 18 paths in the superseded route. The only files this second correction may newly edit are the already-open:

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts

No 19th path is opened.

## Test-First Source-Guard Correction

Before changing the guard, add focused assertions to the existing guard test proving:

1. A production-source JSX attribute named `dangerouslySetInnerHTML` is rejected.
2. Identifier, string-literal, no-substitution-template, computed-property, and trivially split constant-string forms that resolve to that exact property remain rejected.
3. Comments and unrelated Korean/English copy do not create false positives.
4. The complete current production source tree passes the structural prohibition and contains no raw HTML injection surface.
5. Standard ReactDOM bundle output containing its own internal token is not rejected solely for that token, while all other existing bundle prohibitions remain active.

Record a non-vacuous RED against the unchanged guard. Then make one causal guard change:

- remove only the `dangerouslySetInnerHTML` literal from the generated-bundle forbidden-content list;
- add a scanner-backed prohibition across every production `src/**/*.ts` and `src/**/*.tsx` file excluding tests;
- keep dynamic-code, owner-settings import, persistence/network, literal RPC inventory, secret/credential/private-key/real-data, source-map, dependency-inventory, and operations-only checks unchanged;
- expose only the smallest testable helper needed by the existing guard test.

Do not special-case the emitted filename, minified byte offsets, current count of 12, React version, or bundle hash. Do not replace the guard with a regex-only generated-bundle exception.

## Resume and Verification Contract

1. Refresh Pipeline and target state. Require accepted parent, exact 17-path WIP, nothing staged, and no unrecognized path.
2. Add only the new source-guard regressions and record their RED against the unchanged guard.
3. Implement the one guard correction, then rerun the focused guard test.
4. Rerun App compatibility, Task 3 focused tests, typecheck, complete 119-test-or-greater suite, and `npm run build:ci`. Require all green, including `check:dist`.
5. Repeat every negative scan and contract-hash check from the superseded route. Run target smoke, `git diff --check`, and exact allowed-path audit.
6. Obtain fresh read-only specification/abuse and code-quality review of all final bytes. Reviewers must inspect source-scanner completeness, false-positive/false-negative behavior, preservation of remaining bundle checks, the exact composition-root exception, App hook safety, session/recovery behavior, persistence boundaries, and the actual 17-or-fewer changed paths.
7. Resolve all Critical or Important findings before commit. Preserve both immutable finding refs and every disposition.
8. After all gates pass, Director may stage with an explicit pathspec and create exactly one local Task 3 target commit. Publish the canonical actual-range verify-request to Operator2 and bind both RED sequences, every GREEN/full-gate result, build output, source/bundle evidence, hashes, reviews, base/head, paths, author/reviewer models, and finding refs.

If a third distinct distribution-guard assumption fails after this correction, stop without another piecemeal patch and report an architecture-level guard finding to Coordinator.

Operator2 independently reviews the actual combined range and is the only seat that may issue GO, NITS, or FAIL. A GO accepts only this local Task 3 range. Owner-center Task 4, Korean `필요 정보` UI, ordinary product workflow UI, integration, installation, real private values, policy activation, deployment, and publication remain held.

## Authority and Boundaries

Local target editing is authorized only for Director within the same 18 routed paths, preserving the current WIP.

Explicit-path staging is authorized only for Director after every required gate passes.

One local target Task 3 commit is authorized only for Director after every required gate passes.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes every required gate.

No dependency, service lifecycle, managed database/Auth, real/private-value, policy, approval, ruling, activation, raw HTML, booking, or spend action is authorized.

No Korean owner-center page, ordinary decision-workflow UI, service worker, offline cache, deployment, or Windows installation is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, amend, or target-main update is authorized.

## Exact Next Trigger

Director reads this complete committed superseding route, verifies the exact preserved 17-path WIP at target parent `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, implements only the test-first production-source raw-HTML guard correction within the already-open guard/test paths, reruns every Task 3 gate and both fresh final-byte reviews, creates the one authorized local target commit, publishes the canonical immutable verify-request to Operator2, dispatches the existing compatible Operator2 task automatically, and stops for its verdict. On any third distinct guard assumption, 19th path, or hard failure, Director stops without committing and reports the exact architecture-level blocker to Coordinator.

Cursor at send: 0
