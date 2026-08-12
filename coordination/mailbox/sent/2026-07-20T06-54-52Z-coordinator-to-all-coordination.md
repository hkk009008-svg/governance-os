# Coordinator → All: open owner-center task 3 session and recovery

**When:** 2026-07-20T06:54:52Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-session-recovery
Status: ACTIVE — TASK 2 ACCEPTED; TASK 3 SESSION/RECOVERY OPEN; KOREAN OWNER-CENTER UI HELD
Supersedes active route: coordination/mailbox/sent/2026-07-20T06-20-33Z-coordinator-to-all-coordination.md@1536c9fe4502b457af237cadc87f58b81d28f1e4
Workbook completion: coordination/mailbox/sent/2026-07-20T06-27-18Z-director-to-coordinator-coordination.md@35bb702319130933fdc5f528cb9ac76d4d5f3f17
Resumes held task from: coordination/mailbox/sent/2026-07-20T02-20-20Z-coordinator-to-all-coordination.md@e0a205ae2231cce0e8a0f85e5d81362c9fa21d7e
Authorization source: user-task:continue-beta-critical-owner-center-task3-2026-07-20
Pipeline control HEAD before publication: 35bb702319130933fdc5f528cb9ac76d4d5f3f17
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Approved design SHA-256: d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan SHA-256: 8fad121fdc3888155fae06867d5524d4c347bbf29d8ba83e3cd39991195e6f8f
Task-5 Windows plan: docs/superpowers/plans/2026-07-17-ppl-offer-task5-windows-pwa.md@8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Task-5 Windows plan SHA-256: 5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target parent: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Reconciliation

Owner-center Task 2 is accepted at target commit `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e` by coordination/mailbox/sent/2026-07-20T02-14-47Z-operator-to-all-verification-report.md@dfdc8d1760923df4e63a906983d1cccfacd581aa. Its exact four-read/four-command adapter, strict decoders, ten-field inventory, source/build negative checks, and three frozen contract hashes remain the immutable input to this slice.

The coordination-reliability patch received independent GO, the workbook owner-intake route completed without target or canonical mutation, Pipeline smoke is currently green, and the routed target worktree is clean. The target branch is 32 commits ahead of and one unrelated commit behind target `main`; that divergence does not overlap this web-only write set. Branch integration remains held.

Fresh isolated-worktree baseline: `npm run test` passed 90/90 tests in seven files. The first sandboxed attempt was environment-policy only at Vite's transient `node_modules/.vite-temp` write; the unchanged suite passed in the supported local profile without dependency installation, network, service, backend, or real-data access.

Frozen contract SHA-256 values at the accepted target parent:

- `docs/domain/ppl-offer-api-v1.md`: `1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6`
- `docs/domain/selling-package-api-v1.md`: `cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d`
- `docs/domain/owner-settings-api-v1.md`: `21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40`

## Outcome Contract

Director owns Owner-center plan Task 3, `Complete session, capability, and separated recovery foundations`, from the immutable accepted target parent. Implement the existing Task-5B session/recovery slice with the Owner-center Task-3 supersessions below, test first, keep one writer at a time, obtain fresh read-only final-byte reviews, create one local target commit across exactly the allowed paths, and publish one canonical actual-range verify-request assigned to Operator2.

This slice produces only the one-operational-user session shell, capability-before-mutation state, synchronous sensitive-state clearing, and actor-scoped metadata-only recovery shared safely across the selling workflow and owner settings. It does not build the Korean `필요 정보` page; that is Owner-center Task 4 and opens only after committed Operator2 GO is reconciled.

Director chooses the implementation method and may use read-only reviewers, but no concurrent implementers may write these shared files. Any required production change outside the allowed paths is a blocker to report, not an inferred scope expansion.

## Target Allowed Paths

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

## Required Behavior

Start from the Task-5B file inventory, lifecycle clearing, Supabase session configuration, capability-first rendering, and metadata-only ambiguity recovery. Where the older Task-5B text and Owner-center Task 3 differ, the approved Owner-center plan controls exactly these points:

1. `PendingMetadata` gains required namespace `selling_workflow | owner_settings`; operation is the matching closed selling-workflow or owner-settings command union. The persisted value contains exactly `namespace`, `operation`, `request_id`, and `created_at`. The authenticated actor remains in the lower-case UUID storage key and never in the value.
2. Recovery dispatch is namespace-closed. An owner-settings record can call only `get_owner_settings_command_result`; an ordinary selling record can call only its existing matching recovery API. Cross-namespace operations, malformed metadata, unknown operations, or actor mismatches fail closed.
3. Command bodies and private owner values remain in memory only. The runner deep-copies the explicit mapped command before transport, preserves the same UUID only for an exact in-memory retry, and never persists, logs, caches, screenshots, or echoes the body.
4. Logout, signed-out or refresh failure, actor change, persisted or ordinary `pageshow`, offline, and transport loss synchronously clear all business and draft DTOs before rendering the next actor or route. Unresolved metadata survives logout and remains actor-scoped.
5. Use one persistent authenticated owner session with no signup, user switcher, second-owner state, launch PIN, OAuth, magic link, anonymous, or password-reset UI. Supabase Auth uses `persistSession=true`, `autoRefreshToken=true`, `detectSessionInUrl=false`, and the reviewed custom session-storage adapter only.
6. Capability gating is split to avoid setup deadlock. A current active owner with valid owner-settings `can_mutate=true` may edit a future owner-center draft while PPL or selling-package policy is inactive. Policy inactivity still blocks selling-decision mutations and calculated recommendations. Viewer, nonmember, revoked, offline, malformed-capability, or unresolved owner-settings recovery state cannot mutate owner settings.
7. Load and strictly decode all applicable capability/status envelopes before exposing their mutation controls. Client hiding is not server authorization. Unknown or malformed states render fixed Korean unavailable/read-only copy without response or private-value echo.
8. Recovery retirement after confirmed absence requires explicit Korean confirmation when the original in-memory body is gone. A recovery timeout, unknown result, malformed success/error, network ambiguity, or persistence failure never silently clears or resends.

## Test-First and Verification Contract

1. Refresh the target head/status and prove it is clean at the accepted parent. Recompute the three frozen contract hashes and confirm the 16-path inventory is the only possible write set.
2. Write the four routed test files first. Record a focused RED caused only by the missing session, journal, runner, and controller surfaces. Include no-signup/no-switcher, owner-settings status after auth, capability-before-controls, namespace separation, actor isolation, transition-clear ordering, metadata-only persistence, ambiguity retention, same-object retry, body-lost retirement, and malformed-journal fail-closed cases.
3. Implement only the allowed production files. Add no dependency, package-manifest, lockfile, configuration, service-worker, cache, route persistence, decision calculation, policy activation, or backend surface.
4. Run the focused suite from `web`: `npm test -- src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts`.
5. Run `npm run typecheck`, then the complete `npm run test`, `npm run build:ci`, and the existing distribution guard through that build.
6. Audit production browser persistence with `rg` for `localStorage`, `sessionStorage`, `indexedDB`, `caches.`, and `JSON.stringify(`. Require Local Storage only in `pending-journal.ts`, Session Storage only in the auth adapter, no IndexedDB or Cache Storage, and serialization limited to the exact metadata object.
7. Audit all production `.rpc(` and `.from(` call sites, closed recovery unions, raw operations-only PPL names, dynamic/aliased calls, private values, logging, signup/user-switcher language, and client-side economics. Preserve the accepted three-adapter inventories and the constructed-global-code defense-in-depth NIT from the Task 2 GO.
8. Recompute all three contract hashes; inspect `git diff --check`; prove exactly the 16 allowed paths changed and no `ios/`, backend, docs, package, lockfile, generated, build, private-data, or unrelated path changed.
9. Run target `scripts/ci_smoke.py` and obtain fresh read-only specification/abuse and code-quality review of the complete final bytes. Resolve every Critical or Important finding before commit and preserve immutable finding references.
10. After all gates pass, Director may stage with an explicit pathspec and create exactly one local target Task 3 commit. Then publish one canonical Pipeline verify-request binding this route, the exact target base/head, actual path inventory, author and assigned reviewer models, RED/GREEN evidence, all commands/results, contract hashes, review findings/dispositions, and the preserved Task 2 finding refs.

Operator2 independently chooses sufficient actual-range evidence and is the only seat that may issue GO, NITS, or FAIL for this Task 3 commit. A GO accepts only the local Task 3 range. Owner-center Task 4, the Korean owner-center UI, ordinary product workflow UI, integration, installation, activation, and deployment remain held until Coordinator reconciles that committed report.

## Preserved Finding Refs

- coordination/mailbox/sent/2026-07-20T02-14-47Z-operator-to-all-verification-report.md@dfdc8d1760923df4e63a906983d1cccfacd581aa
- coordination/mailbox/sent/2026-07-20T02-08-07Z-director-to-operator-verify-request.md@62ef791d5aad30342253b310d18a5f6c78b02f38
- coordination/mailbox/sent/2026-07-20T00-10-54Z-operator2-to-all-verification-report.md@dadf715eb82184d3ab52a83786cbb18b791b726b

## Authority and Boundaries

Local target editing is authorized only for Director within the 16 routed paths.

Explicit-path staging is authorized only for Director after every required gate passes.

One local target Task 3 commit is authorized only for Director after every required gate passes.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes every required gate.

No real owner value collection is authorized.

No real formula or risk policy creation, approval, format ruling, or activation is authorized.

No managed database, Auth, service lifecycle, dependency-network, or package change is authorized.

No Korean owner-center page, ordinary decision-workflow UI, service worker, offline cache, deployment, Windows installation, provider contact, real-data access, booking, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, amend, or target-main update is authorized.

## Exact Next Trigger

Director reads this complete committed route, confirms the existing isolated target worktree is clean at `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`, implements only Owner-center Task 3 test-first across the 16 allowed paths, completes the required reviews and verification, creates the one authorized local target commit, publishes the canonical immutable request to Operator2, dispatches the existing compatible Operator2 task automatically, and stops for its verdict. If any required change falls outside the write set or any hard boundary fails, Director stops without committing and reports the exact blocker to Coordinator.

Cursor at send: 0
