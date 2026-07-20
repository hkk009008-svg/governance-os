# Coordinator → All: supersede Task 3 with final-review corrections

**When:** 2026-07-20T10:09:22Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-center-2026-07-20
Task ID: coordinator-owner-center-task3-final-review-corrections
Status: ACTIVE — APPROVED CORRECTION PLAN ROUTED; PRESERVED 17-PATH WIP REMAINS UNSTAGED
Supersedes route: coordination/mailbox/sent/2026-07-20T09-04-37Z-coordinator-to-all-coordination.md@e2b6992a3bdb076c1160f4ea06f5035cabc7a08d
Accepted blocker: coordination/mailbox/sent/2026-07-20T09-21-17Z-director-to-coordinator-coordination.md@1f07af86bfa85a99129a686d65b1ed48ea389d8d
Authorization source: user-task:approved-task3-final-review-corrections-and-proceed-2026-07-20
Pipeline control HEAD before publication: d65ea564731c62c27b9cb8c80aa84241571a2f47
Approved correction design: docs/superpowers/specs/2026-07-20-task3-final-review-corrections-design.md@035fc1e75bc2eefcf01ec10ee4b00f49458057f3
Approved correction plan: docs/superpowers/plans/2026-07-20-task3-final-review-corrections.md@d65ea564731c62c27b9cb8c80aa84241571a2f47
Prior semantic-guard design retained where not superseded: docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target HEAD: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

Finding refs:
- FINDING-TASK3-CONSTANT-RECONSTRUCTED-JWT
- FINDING-TASK3-SAME-ACTOR-RETRY-REACHABILITY
- FINDING-TASK3-TERMINAL-RETRY-STALE-RECOVERY
- FINDING-TASK3-COMPUTED-DYNAMIC-CODE
- FINDING-TASK3-ACTOR-TRANSACTION-RACES
- FINDING-TASK3-LOGOUT-ABSENCE-FENCE
- FINDING-TASK3-ORDINARY-DIRECT-TRANSPORT
- NIT-TASK3-TRANSPORT-MUTATES-RETAINED
- NIT-TASK3-NO-WEB-LOCKS-REGRESSION
- NIT-TASK3-LIFECYCLE-LISTENER-DEFERRED

## Coordinator Decision

The binding final-byte review overrides the earlier green counts as acceptance evidence. The current bytes remain preserved and ineligible for a target commit until all seven Important findings and the two accepted related Minor gaps are corrected test-first under the approved design and plan.

The reviewer suggestion to require a JOSE alg member is rejected. Canonical Base64URL object/object compact serialization remains credential-like even without alg, and populated or empty signatures remain forbidden.

The lifecycle-listener/disposal Minor remains recorded but deferred because no production remount path was demonstrated and pagehide disposal would conflict with the existing back-forward-cache recovery path. If a fresh reviewer demonstrates a real production lifecycle failure, Director stops and reports it rather than opening another file or behavior.

The complete focused baseline is six files and 73/73 tests. The complete suite baseline is 134/134. The corrected final contract is six files and exactly 79/79 tests, with the complete suite exactly 140/140.

## Correction Files

Director may newly edit only these eight existing WIP files:

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts
- web/src/app/AppController.test.ts
- web/src/app/AppController.ts
- web/src/features/recovery/command-runner.test.ts
- web/src/features/recovery/command-runner.ts
- web/src/features/recovery/pending-journal.test.ts
- web/src/features/recovery/pending-journal.ts

The other nine routed Task 3 files remain at their current preserved WIP bytes. web/src/config/env.test.ts is read-only verification input. web/src/test/synthetic-wire.ts remains closed and unchanged. A ninth correction file, a new edit to web/src/main.tsx, or an eighteenth target path requires a new design and route.

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

## Implementation Contract

1. Director starts from Pipeline, reads this complete committed route, runs the ledger start guard for director with this exact route ref, reads the evidence-ledger instructions, and rechecks target HEAD, branch, empty index, exact 17-path WIP, and both closed verification files.
2. Director uses the approved implementation plan task by task with test-first RED then minimal GREEN. One correction unit is completed before the next. The target index remains empty and no intermediate target commit is created.
3. The generated-artifact guard reuses only the existing closed constant evaluator. It rejects contiguous, concatenated, templated, and literal-array-join credential-like forms, including empty signatures, while preserving every other artifact prohibition and allowed ordinary dotted code.
4. The source guard rejects direct and closed-constant-composed eval, Function, rpc, fetch, XMLHttpRequest, and sendBeacon names throughout production source. RPC remains permitted only in the three exact API adapters under their existing inventories.
5. PendingJournal exposes one actor-scoped Web Locks transaction. Execute, recover, retry, retirement, and matching removal revalidate and finish within that one transaction without nested acquisition. Unsupported Web Locks fail before persistence or transport.
6. Every transport attempt receives a fresh structured clone of the retained canonical command.
7. Same-actor same-page session application preserves retained command memory while sensitive DTOs still clear. Actor change, sign-out, offline or transport loss, authentication failure, and disposal clear retained command memory.
8. Terminal retry success or expected rejection clears the exact journal entry and revalidates. An ambiguous retry remains unresolved only while the exact pending entry still exists.
9. Logout disables mutation, clears in-memory state, advances the authentication epoch, and remains fenced until a genuine SIGNED_OUT callback or an error-free null-session storage read proves local absence. Late non-SIGNED_OUT callbacks cannot restore a session. Explicit successful password login is the only other in-page fence release.
10. Focused additions are exactly one pending-journal test, three command-runner tests, and two AppController tests. owner-settings-api.test.ts remains 28 tests. Final per-file counts are 28, 11, 4, 6, 11, and 19, totaling exactly 79.
11. Director freshly runs the exact focused selector, typecheck, complete suite, build:ci, source and artifact abuse audits, the three frozen contract hashes, target smoke, diff check, exact-scope checks, empty-index check, and closed-file checks. Required final results are 79/79 focused, 140/140 complete, and every other gate PASS.
12. Any count mismatch, changed accepted HEAD before the target commit, changed frozen hash, credential or private-data match, target path expansion, closed-file change, hidden staged byte, materially distinct generated-artifact assumption, or unresolved hard gate is an immediate stop with exact evidence to Coordinator.

## Final-byte Review and Operator Contract

Director obtains two fresh read-only reviews of all final 17 live paths: one specification and abuse review and one code-quality review. They must cover every finding ref above, constant-reconstruction limits, direct transport and RPC abuse, full actor transaction races, fresh command clones, same-actor reachability, terminal versus ambiguous retry, logout storage proof and late callbacks, the deferred lifecycle Minor, types, storage failure, timeout behavior, async retirement, actor epochs, and test non-vacuity.

Every fresh Critical or Important finding is resolved test-first inside the eight correction files or causes a truthful stop. Every Minor receives an explicit disposition. After any correction, Director repeats all final gates and obtains fresh final-byte conclusions.

Only after every gate and both reviews pass may Director stage exactly the 17 target paths and create one local combined Task 3 commit. Director then publishes one canonical immutable verify-request assigned to Operator2. The request binds this route, both approved documents, target repository/worktree/branch, immutable base and new head, all 17 paths, the eight correction-file boundary, Director and Operator2 identities, every finding and disposition, exact gate evidence, hashes, and final-byte reviews.

Director reuses the existing compatible Operator2 Codex task, sends the exact committed trigger once, monitors without duplicate dispatch, and stops for GO, NITS, or FAIL. Operator2 is the only seat that may issue that verdict on the actual committed range.

## Authority and Boundaries

Local target editing is authorized only for Director and only in the eight correction files above.

Explicit-path staging of the 17 target paths is authorized only after all final gates and both reviews pass.

One local combined Task 3 target commit is authorized only after all final gates and both reviews pass.

One canonical Pipeline verify-request publication and one exact existing-task dispatch to Operator2 are authorized only after the target commit passes every gate.

No dependency, package, lockfile, configuration, framework, new source file, service lifecycle, managed database or Auth action is authorized.

No real or private value, real-data path, policy creation, ruling, approval, activation, booking, spend, deployment, or production generation is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No target-main update is authorized.

No cursor consumption is authorized.

No protocol lock action is authorized.

No cleanup, reset, rebase, or amend is authorized.

## Exact Next Trigger

Director resumes from this complete committed route and approved plan at target HEAD 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e, preserves the exact 17-path WIP and empty index, executes the correction plan test-first only in the eight correction files, requires final 79/79 focused and 140/140 complete results plus every named gate, obtains two fresh final-byte reviews, resolves all Critical or Important findings within scope, creates the one authorized local target commit, publishes the immutable verify-request, dispatches the existing compatible Operator2 task once, and stops for its verdict. On any stop condition, Director preserves the target and reports the exact blocker to Coordinator.

Cursor at send: 0
