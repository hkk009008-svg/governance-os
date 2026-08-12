# Coordinator → Director: unified Mac teaching beta UI

**When:** 2026-07-22T14:36:01Z · **From:** coordinator (online)

# Coordinator → Director: implement unified Mac teaching-beta UI

Event type: coordination
Task ID: ledger-beta-unified-ui-2026-07-22
Status: AUTHORIZED REQUEST — IMPLEMENT AND REQUEST INDEPENDENT REVIEW
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Supersedes completed route for the next owned outcome: coordination/mailbox/sent/2026-07-22T12-10-27Z-director-to-all-coordination.md@99be69093af0655ee12734c2c26756a479440f52
Prior integrated checkpoint: coordination/mailbox/sent/2026-07-22T12-13-46Z-director-to-coordinator-coordination.md@122d8af
Owner-approved design: docs/superpowers/specs/2026-07-22-evidence-ledger-unified-beta-ui-design.md@4f24d67
Implementation plan: docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@4f24d67
Target repository and accepted base: /Users/hyungkoookkim/evidence-ledger@bc2e85891f27befe19236686e608f3d45db84d14
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Finding refs: BETA-UI-001, BETA-UI-002, BETA-UI-003

This is a non-secret Coordinator request for a fresh Director autonomous root
with `Parent contract: none`. Coordinator retains observation and integration
facilitation only; Coordinator receives no evidence-ledger product authorship
or review-verdict authority.

## Confirmed acceptance findings

- `BETA-UI-001`: the current ready application is visually fragmented and
  does not present a coherent professional Korean business-tool shell.
- `BETA-UI-002`: the owner page renders only one server-selected field even
  though the teaching session requires all ten unknown business inputs to be
  visible and fillable on one page.
- `BETA-UI-003`: several primary surfaces expose internal state or operation
  labels and dense technical output instead of an answer-first Korean view.

The owner selected design direction A, `차분한 업무도구`, and approved the
complete nine-screen written design. Fresh baseline verification on the normal
target at the accepted base passed `npm run typecheck` and Vitest 25 files,
264 tests. The normal target retains only pre-existing untracked `.vscode/`
and `web/node_modules`; the existing loopback teaching preview remains a
separate runtime boundary.

## Required next outcome

1. Publish and validate one fresh Director autonomous root bound to this
   request, the immutable design and plan, accepted base, exact owner/model,
   assigned reviewer/model, and immutable finding refs.
2. Use `superpowers:using-git-worktrees` to create exactly
   `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui` on
   branch `codex/beta-unified-ui` from the accepted base. Stop if either exact
   identity already exists with incompatible state.
3. Use `superpowers:executing-plans`, `superpowers:test-driven-development`,
   and `superpowers:verification-before-completion` to execute the approved
   plan in order. Preserve RED evidence before production changes and keep
   implementation limited to the allowed paths.
4. Build the shared application shell, two-field login, consistent static and
   recovery states, all-ten-fields owner editor using sequential existing
   commands, unified product-first workflow, dedicated evidence/history
   destination, answer-first recommendation, Korean copy containment,
   responsive behavior, accessibility, and focused synthetic tests.
5. Preserve all current APIs, DTOs, decoders, command-runner and journal
   ordering, database/RPC contracts, product calculations, authorization,
   service-worker security, private-state fences, and external-effect
   boundaries. Add no dependency.
6. Run the exact focused and cumulative commands from the plan, update factual
   `ARCHITECTURE.md` and `OPERATIONS.md` summaries from terminal evidence, and
   create the planned local target commits.
7. Publish one exact cumulative verify-request assigning Operator2 on
   gpt-5.6-terra. Bind the accepted base, shipping commit, actual range, path
   manifest, immutable design/plan/request refs, RED evidence, all final
   command summaries, and every finding above.
8. Reconcile the canonical Operator2 GO/NITS/FAIL and publish one non-secret
   Director checkpoint to Coordinator. Do not integrate the branch or replace
   the live preview within this outcome.

## Target allowed paths

- ARCHITECTURE.md
- OPERATIONS.md
- web/src/main.tsx
- web/src/app/App.tsx
- web/src/app/AppShell.tsx
- web/src/app/AppShell.test.tsx
- web/src/app/AppController.test.ts
- web/src/components/AsyncState.tsx
- web/src/features/auth/LoginView.tsx
- web/src/features/recovery/RecoveryPanel.tsx
- web/src/features/owner-settings/owner-settings-form.ts
- web/src/features/owner-settings/owner-settings-form.test.ts
- web/src/features/owner-settings/OwnerSettingsForm.tsx
- web/src/features/owner-settings/OwnerSettingStep.tsx
- web/src/features/owner-settings/OwnerSettingsPage.tsx
- web/src/features/owner-settings/OwnerSettingsPage.test.tsx
- web/src/features/owner-settings/OwnerSettingsStatus.tsx
- web/src/features/owner-settings/OwnerSettingsReview.tsx
- web/src/features/owner-settings/OwnerSettingsHistory.tsx
- web/src/features/owner-settings/copy.ts
- web/src/features/selling-decision/selling-copy.ts
- web/src/features/selling-decision/selling-copy.test.ts
- web/src/features/selling-decision/SellingDecisionWorkspace.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx
- web/src/features/selling-decision/ProductPage.tsx
- web/src/features/selling-decision/HsOffersPage.tsx
- web/src/features/selling-decision/PplOptionsPage.tsx
- web/src/features/selling-decision/RecommendationPage.tsx
- web/src/features/selling-decision/EvidencePanel.tsx
- web/src/features/selling-decision/RevisionHistory.tsx
- web/src/features/selling-decision/OwnerDecisionPanel.tsx
- web/src/features/selling-decision/accessibility.test.tsx
- web/src/styles/app.css
- web/e2e/owner-settings.spec.ts
- web/e2e/workflow.spec.ts
- web/e2e/security.spec.ts

`OwnerSettingStep.tsx` may be deleted only when its all-fields replacement is
covered and no caller remains. Every other allowed path may change only for
the exact approved UI design, tests, or factual closeout described in the
plan. `web/package.json`, `web/package-lock.json`, database/import/iOS paths,
generated `web/dist/`, and every unrelated target path remain outside scope.

## Authorized local implementation effects

- executor: director
- effect: create the exact isolated worktree and branch above, edit only the
  allowed target paths, run synthetic local tests/builds, and create the
  planned local commits
- target: accepted evidence-ledger base
  `bc2e85891f27befe19236686e608f3d45db84d14`
- stop conditions: changed target base, unexpected tracked/index state,
  incompatible worktree or branch identity, dependency acquisition request,
  path drift, private/live data requirement, service dependency, or any hard
  test/contract boundary not resolved within the approved paths

## Authorized coordination effects

- executor: director
- effect: publish one validated autonomous root, one exact Operator2
  verify-request, and one final non-secret checkpoint through the fixed writer
- target: Pipeline mailbox only
- content boundary: exclude credentials, owner values, private responses,
  environment secrets, session keys, and raw business data

## Authority absent from this request

There is no authority here for target-main integration, remote-reference
publication, live preview rebuild/restart/rebinding, dependency acquisition,
service/container/database/account mutation, browser authentication, owner
value entry, draft review, policy activation, real/private-data use, booking,
purchase, payment, email, deployment, Windows packaging, worktree cleanup,
branch deletion, cursor consumption, protocol-lock action, spend, history
rewrite, or unrelated maintenance. A later Operator GO grants none of these
effects.

## Stop boundary

Director stops after the canonical Operator2 verdict and the one non-secret
checkpoint to Coordinator. On FAIL, correct only exact cited findings within
the approved paths, create a fresh shipping identity, and request review of
the corrected actual range. Any need to widen contracts, paths, dependencies,
runtime effects, or product meaning returns to Coordinator before action.

Cursor at send: 0
