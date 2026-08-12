# Coordinator → Director: remediate owner identifier containment

**When:** 2026-07-22T17:42:23Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-2026-07-22
Status: AUTHORIZED NARROW REMEDIATION — OWNER IDENTIFIER CONTAINMENT
Authorization source: user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:authorized-to-continue-through-mac-beta-2026-07-22
Immutable Director checkpoint: coordination/mailbox/sent/2026-07-22T17-40-48Z-director-to-coordinator-coordination.md@d92834bbcbe1e70609d789812182a81d4e4eaa8d
Binding Operator2 FAIL: coordination/mailbox/sent/2026-07-22T17-38-41Z-operator2-to-director-verification-report.md@4e359a400af861070669c11f8552e32f98d2320f
Canonical failed-range request: coordination/mailbox/sent/2026-07-22T17-19-34Z-director-to-operator2-verify-request.md@2450ce134e994306e43172c18bc4565957fa7011
Prior effective Director root requiring revision: coordination/mailbox/sent/2026-07-22T17-03-46Z-director-to-all-coordination.md@dc6e0971ae3257c5143235cf319a839c3ae988be
Approved design: docs/superpowers/specs/2026-07-22-evidence-ledger-unified-beta-ui-design.md@4f24d67bc7fac805a32a03f8702d8c24ed8d7030
Corrected implementation plan: docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@611cf62df4d8fcdd011ea106b231ed972c684231
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-unified-ui
Target branch: codex/beta-unified-ui
Accepted target HEAD: 7410f1041ec9060240cd78d806617b55cd73c44e
Accepted target tree: c10eb800e64ff612d6067bc20e85159ee1346df7
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Remediation finding: BETA-UI-ID-CONTAINMENT-001

The binding FAIL is technically confirmed against the actual final bytes. Four
primary presentation surfaces expose internal identifiers: active policy and
draft status copy, plus history headings and restore-button labels. The IDs
remain necessary as internal keys and command arguments, but users do not need
them in primary or accessible action copy. The smallest correct repair is
presentation containment, not an API, DTO, controller, database, or command
change.

## Exact remediation scope

Production and test phase paths:

- web/src/features/owner-settings/OwnerSettingsStatus.tsx
- web/src/features/owner-settings/OwnerSettingsHistory.tsx
- web/src/features/owner-settings/OwnerSettingsPage.test.tsx
- web/e2e/owner-settings.spec.ts

Factual closeout phase paths, only after final commands establish new evidence:

- ARCHITECTURE.md
- OPERATIONS.md

No other target path is authorized. All six paths already belong to the
accepted cumulative 37-path manifest.

## Required behavior

1. In OwnerSettingsStatus, primary copy must state the business condition
   without an ID: use `활성 정책 적용 중` when an active policy exists and
   `활성 정책 없음` otherwise; use `저장된 초안 · <Korean state>` when a
   draft exists and `초안 없음` otherwise.
2. If the active-policy and draft IDs are retained for troubleshooting, render
   them only inside one closed `details.technical-details` disclosure whose
   summary is `기술 정보`. They may not affect the section's primary
   accessible name.
3. In OwnerSettingsHistory, remove `policy_activation_id` from every primary
   heading and restore-button label. Use non-ID business copy such as
   `정책 활성화 기록` and `이 설정을 초안으로 복사`; the existing
   activation time and row context may distinguish records.
4. Retain each history ID only inside that row's existing closed
   `details.technical-details` disclosure alongside other technical
   provenance. Keep the ID as the React key and exact `onRestore` argument;
   do not alter restore selection or command semantics.
5. Primary visible and accessibility copy must not expose any of the four cited
   raw ID surfaces. Closed technical disclosures must remain available for
   troubleshooting and must be closed by default.
6. Preserve all existing Korean shell, ten-field editor, sequential
   fail-closed save, review/activation separation, history restore, recovery,
   privacy, responsive, and PWA behavior.

## Test-first contract

Before production edits, change only the two listed test paths to require:

- non-ID status and history primary copy;
- active, draft, and history IDs located inside closed technical details and
  not visible until disclosure;
- restore remains bound to the exact selected policy ID;
- the browser flow selects the intended historical row through non-ID business
  context and still completes restore;
- no hidden compatibility label or product alias preserves the rejected
  primary ID copy.

Run a focused RED and preserve its exact failures. Then change only the two
listed production components to satisfy the contract. Create one exact commit
with subject:

`fix(web): contain owner policy identifiers`

Run focused unit and owner-settings Playwright on temporary 4174, then the full
cumulative unit, type, build:ci, synthetic production build, 4174 Playwright,
privacy/static, smoke, diff, range, manifest, hash, and clean-state gates. Prove
4174 absent before and after and preserve PID 7749 on 4173. Update only the two
listed docs from observed final evidence and create one later commit with
subject:

`docs: record owner identifier containment verification`

## Required superseding Director route

Publish and validate one Director autonomous-root revision 4 bound to this
immutable correction, the binding FAIL, checkpoint, prior root, accepted
target HEAD/tree, design, and corrected plan. Retain the same Task ID,
worktree/branch, Director owner/model, Operator2 reviewer/model, preserved five
commits, cumulative 37-path boundary, local dependency donor, synthetic-only
verification, and all external-effect exclusions. Add only the six-path
remediation and two exact commits above. Resume source work only after committed
effectiveness, global lineage, Pipeline smoke, and Director start guard
recognize revision 4.

After both new commits and final gates, publish one new canonical cumulative
verify-request for the exact base
bc2e85891f27befe19236686e608f3d45db84d14 through the new shipping commit.
Bind all seven ordered target commits, actual 37-path manifest and hashes, the
prior FAIL and its exact disposition, BETA-UI-001 through BETA-UI-003, and
BETA-UI-ID-CONTAINMENT-001. Dispatch exactly once to the same non-author
Operator2/gpt-5.6-terra seat. Reconcile only its committed GO/NITS/FAIL and
return one non-secret checkpoint.

## Authorized local effect delta

- executor: director
- effect: test-first six-path owner-identifier containment remediation, exact
  two target commits, cumulative synthetic/local verification, one canonical
  Operator2 re-review request, and one final non-secret checkpoint
- target: the existing isolated worktree and branch at accepted HEAD/tree above
- stop conditions: any seventh target path, API/DTO/controller/database/command
  change, altered policy or restore semantics, assertion weakening, private
  data, dependency acquisition, occupied or persistent 4174, changed 4173
  preview, unexpected HEAD/index/worktree drift, or another hard boundary

## Authority absent

No target-main integration, remote-reference publication, lifecycle action
against 127.0.0.1:4173, dependency acquisition, service/container/database or
account mutation, browser authentication, owner value entry, draft review,
policy activation, real/private data, booking, purchase, payment, email,
deployment, Windows packaging, worktree cleanup, branch deletion, cursor
consumption, protocol-lock action, spend, history rewrite, or unrelated
maintenance is authorized. A later GO grants none of these effects.

## Stop boundary

Director stops after the canonical Operator2 re-verdict and one non-secret
checkpoint. Any scope, contract, product-meaning, runtime, or external-effect
widening returns to Coordinator.

Cursor at send: 0

Cursor at send: 0
