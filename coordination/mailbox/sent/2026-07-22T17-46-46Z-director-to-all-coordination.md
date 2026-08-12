# Director → All: remediate owner identifier containment

**When:** 2026-07-22T17:46:46Z · **From:** director (online)

Task-board: ledger-beta-unified-ui-2026-07-22
Task ID: ledger-beta-unified-ui-2026-07-22
Outcome contract: remediate only the binding owner identifier containment finding test-first in the existing isolated worktree, create the exact four-path fix and two-path factual-documentation commits, complete cumulative synthetic/local verification, obtain cumulative non-author Operator2 re-review, publish one non-secret checkpoint, and stop without integration, remote publication, or teaching-preview lifecycle action
Parent contract: coordination/mailbox/sent/2026-07-22T17-03-46Z-director-to-all-coordination.md@dc6e0971ae3257c5143235cf319a839c3ae988be
Contract revision: 4
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T17-42-23Z-coordinator-to-director-coordination.md@05e0378fa1232e568f1afe0b7a867bf0cf2ac860, coordination/mailbox/sent/2026-07-22T17-38-41Z-operator2-to-director-verification-report.md@4e359a400af861070669c11f8552e32f98d2320f, coordination/mailbox/sent/2026-07-22T17-40-48Z-director-to-coordinator-coordination.md@d92834bbcbe1e70609d789812182a81d4e4eaa8d, coordination/mailbox/sent/2026-07-22T17-19-34Z-director-to-operator2-verify-request.md@2450ce134e994306e43172c18bc4565957fa7011, coordination/mailbox/sent/2026-07-22T17-03-46Z-director-to-all-coordination.md@dc6e0971ae3257c5143235cf319a839c3ae988be
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Target branch: codex/beta-unified-ui
Target base: bc2e85891f27befe19236686e608f3d45db84d14
Accepted target HEAD: 7410f1041ec9060240cd78d806617b55cd73c44e
Accepted target tree: c10eb800e64ff612d6067bc20e85159ee1346df7
Preserved Task 1 commit: 669c8b58b70ff0f2c980b7d74db0d523348d79d2
Preserved Task 2 commit: 940744b30e1c2878574a85fec236210ad67a1845
Preserved Task 3 commit: 6b817bdc27acdecea5dce8832cd1b4a3daceed5c
Preserved PWA correction commit: 7e08cfb2ff60649e878a5a2f93cba4b4609e5f2e
Preserved factual-doc commit: 7410f1041ec9060240cd78d806617b55cd73c44e
Owner-approved design: docs/superpowers/specs/2026-07-22-evidence-ledger-unified-beta-ui-design.md@4f24d67bc7fac805a32a03f8702d8c24ed8d7030
Corrected implementation plan: docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@611cf62df4d8fcdd011ea106b231ed972c684231
Remediation finding: BETA-UI-ID-CONTAINMENT-001

## Finding Reconciliation

- The Operator2 FAIL is technically confirmed against the accepted immutable bytes. OwnerSettingsStatus exposes active-policy and draft-revision IDs in primary copy; OwnerSettingsHistory exposes policy-activation IDs in headings and restore-button accessible labels.
- The IDs remain required as internal React keys, exact restore command arguments, and troubleshooting provenance. They are not required in primary visible or accessible copy.
- The narrow correction is presentation containment only. APIs, DTOs, decoders, controllers, command selection, restore semantics, database state, product rules, and every other runtime contract remain frozen.
- BETA-UI-001 through BETA-UI-003 remain otherwise accepted only as implemented evidence pending corrected cumulative Operator2 review. BETA-UI-ID-CONTAINMENT-001 remains open until that review.

## Target Allowed Paths

- ARCHITECTURE.md
- OPERATIONS.md
- web/e2e/owner-settings.spec.ts
- web/e2e/pwa.spec.ts
- web/e2e/security.spec.ts
- web/e2e/workflow.spec.ts
- web/playwright.config.ts
- web/src/app/App.tsx
- web/src/app/AppController.test.ts
- web/src/app/AppShell.test.tsx
- web/src/app/AppShell.tsx
- web/src/components/AsyncState.tsx
- web/src/features/auth/LoginView.tsx
- web/src/features/owner-settings/OwnerSettingStep.tsx
- web/src/features/owner-settings/OwnerSettingsForm.tsx
- web/src/features/owner-settings/OwnerSettingsHistory.tsx
- web/src/features/owner-settings/OwnerSettingsPage.test.tsx
- web/src/features/owner-settings/OwnerSettingsPage.tsx
- web/src/features/owner-settings/OwnerSettingsReview.tsx
- web/src/features/owner-settings/OwnerSettingsStatus.tsx
- web/src/features/owner-settings/copy.ts
- web/src/features/owner-settings/owner-settings-form.test.ts
- web/src/features/owner-settings/owner-settings-form.ts
- web/src/features/recovery/RecoveryPanel.tsx
- web/src/features/selling-decision/EvidencePanel.tsx
- web/src/features/selling-decision/HsOffersPage.tsx
- web/src/features/selling-decision/PplOptionsPage.tsx
- web/src/features/selling-decision/ProductPage.tsx
- web/src/features/selling-decision/RecommendationPage.tsx
- web/src/features/selling-decision/RevisionHistory.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.tsx
- web/src/features/selling-decision/accessibility.test.tsx
- web/src/features/selling-decision/selling-copy.test.ts
- web/src/features/selling-decision/selling-copy.ts
- web/src/main.tsx
- web/src/styles/app.css

## Allowed Path Semantics

The cumulative review boundary remains exactly the 37 paths above. During remediation, only `web/src/features/owner-settings/OwnerSettingsStatus.tsx`, `web/src/features/owner-settings/OwnerSettingsHistory.tsx`, `web/src/features/owner-settings/OwnerSettingsPage.test.tsx`, and `web/e2e/owner-settings.spec.ts` may change in the exact test-first correction commit. Only after final command evidence, `ARCHITECTURE.md` and `OPERATIONS.md` may change in the exact factual closeout commit. The other 31 cumulative paths are closed and must remain byte-for-byte unchanged.

Primary owner status/history copy must use non-ID Korean business labels. If retained, active-policy, draft-revision, and history policy-activation IDs live only in closed `details.technical-details` disclosures with summary `기술 정보`; they do not affect primary accessible names. Each history ID remains the React key and exact `onRestore` argument. No compatibility label, hidden primary ID, API/DTO/controller/database/command change, or restore-selection change is authorized.

## Verification Contract

- Resume only at exact accepted HEAD/tree in the existing linked worktree with an empty index, no tracked residue, and only the preserved untracked dependency donor. Preserve normal main, `.vscode/`, every unrelated worktree/branch/ref, PID 7749 on 4173, and absent 4174.
- Change only the two test paths first. Prove a focused RED for non-ID primary copy, IDs inside closed technical details, exact restore selection, and non-ID browser row selection before production edits.
- Change only the two production components for minimal GREEN. Run focused unit and owner-settings Playwright on temporary 4174 and create one four-path commit with subject `fix(web): contain owner policy identifiers`.
- Run the complete cumulative unit, type, build:ci, synthetic production build, temporary-4174 Playwright, privacy/static, smoke, diff, range, manifest, hash, and clean-state gates. Require 4174 absent before and after every browser run and preserve PID 7749 on 4173.
- Update only ARCHITECTURE.md and OPERATIONS.md from observed final evidence and create one later commit with subject `docs: record owner identifier containment verification`.
- Audit the exact seven-commit range from base, actual 37-path manifest and hashes, two correction commits, closed-file bytes, protected normal checkout, and preview state.
- Publish one canonical cumulative verify-request binding all seven commits, actual immutable head/tree/manifest/hashes, the prior request and FAIL, exact disposition of BETA-UI-ID-CONTAINMENT-001, BETA-UI-001 through BETA-UI-003, Director/gpt-5.6-sol author, and non-author Operator2/gpt-5.6-terra reviewer. Dispatch once, reconcile only the committed verdict, publish one non-secret checkpoint, and stop.

## Side-Effect Executor Token

- effect: exact six-path owner-identifier containment remediation and two local target commits
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui on branch codex/beta-unified-ui at accepted HEAD 7410f1041ec9060240cd78d806617b55cd73c44e and tree c10eb800e64ff612d6067bc20e85159ee1346df7
- scope: only after this revision is committed, structurally valid, directly effective, globally lineage-valid, smoke-green, and recognized by the Director ledger start guard; execute strict RED-to-GREEN in the exact four code/test paths, commit them with the exact fix subject, run complete gates, then commit only the two factual docs with the exact docs subject; stop on any seventh remediation path or hard-boundary drift

## Side-Effect Executor Token

- effect: exact ephemeral isolated Playwright test server
- executor: director
- target: Playwright's installed Vite preview child on exact loopback 127.0.0.1:4174 only during focused owner-settings and cumulative synthetic browser commands
- scope: require no pre-existing listener; set only EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174; use installed dependencies without acquisition; require the child to terminate with Playwright; preserve PID 7749, bytes, and listener on 127.0.0.1:4173; stop on occupied or persistent 4174, bind failure, unexpected traffic, dependency/network need, or any 4173 lifecycle effect

## Side-Effect Executor Token

- effect: exact cumulative non-author Operator2 re-review
- executor: director
- target: one fixed-writer Director-to-Operator2 verify-request in Pipeline and one exact compatible existing Operator2 task dispatch
- scope: only after both exact target commits and all final gates pass; commit only the generated request, dispatch exactly once to the same compatible Operator2 task on gpt-5.6-terra, wait for and reconcile only its canonical committed verdict, and infer no integration or other effect from review

## Side-Effect Executor Token

- effect: committed non-secret final checkpoint
- executor: director
- target: one fixed-writer Director-to-Coordinator coordination event in Pipeline
- scope: only after the canonical Operator2 re-verdict; bind this revision, correction, prior FAIL/checkpoint/request, exact seven-commit target range/tree/manifest/hashes, final gates, verdict ref, preserved normal main and preview boundary, and stop state; exclude credentials, identities, keys, tokens, owner values, business inputs, private responses, and environment secrets

## Stop Boundary

No target-main integration, remote-reference publication, lifecycle action against 127.0.0.1:4173, dependency acquisition, service/container/database/account mutation, browser authentication, owner value entry, draft review, policy activation, real/private data, booking, purchase, payment, email, deployment, Windows packaging, worktree cleanup, branch deletion, cursor consumption, protocol-lock action, spend, history rewrite, or unrelated maintenance is authorized. A later GO grants none of these effects. Director stops after the canonical Operator2 re-verdict and one non-secret checkpoint.

Cursor at send: 0
