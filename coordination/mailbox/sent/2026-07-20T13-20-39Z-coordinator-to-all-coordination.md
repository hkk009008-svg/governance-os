# Coordinator → All: correct ADR collision and reauthorize local merge

**When:** 2026-07-20T13:20:39Z · **From:** coordinator (online)

Task-board: coordinator-owner-center-task3-scanner-resource-correction-2026-07-20
Program board: ledger-one-user-owner-center-2026-07-20
Status: ACTIVE — FIRST MERGE ABORTED CLEANLY; ADR IDENTITY CORRECTION AND LOCAL INTEGRATION ONLY
Route generation: 2
Supersedes route: coordination/mailbox/sent/2026-07-20T13-15-02Z-coordinator-to-all-coordination.md
Expected control HEAD: ae8834c18bce67a7d6ba9807030c78adf5066e73
Superseded route ref: coordination/mailbox/sent/2026-07-20T13-15-02Z-coordinator-to-all-coordination.md@ae8834c18bce67a7d6ba9807030c78adf5066e73
Original approved implementation route: coordination/mailbox/sent/2026-07-20T11-23-58Z-coordinator-to-all-coordination.md@0129a68f6c25460929554252f24b4c158b8d6390
Canonical verify-request: coordination/mailbox/sent/2026-07-20T13-01-51Z-director-to-operator2-verify-request.md@aa25139f7a7e3632199a685293af608c455227c0
Binding Operator2 GO: coordination/mailbox/sent/2026-07-20T13-07-20Z-operator2-to-all-verification-report.md@4a630a9e87061c7f44f324a54b25c714f4a690a7
Authorization source: user-task:approved-local-merge-no-remote-publication-2026-07-20
Target repository: /Users/hyungkoookkim/evidence-ledger
Target feature worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target feature branch: codex/ppl-offer-decision-m1
Reviewed implementation commit: edd148f30b7ba001a8dfb754ebb6856f119ed3a2
Local integration checkout: /Users/hyungkoookkim/evidence-ledger
Local main before integration: cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47
Local origin/main tracking ref before integration: cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47
Merge base: 2b6f3c6242ed87918a4dde17a7db8e887a6020fd

## Coordinator Reconciliation

The generation-1 merge was started only after its committed route validated cleanly. It produced the predicted unmerged set of ARCHITECTURE.md, DECISIONS.md, and OPERATIONS.md, but DECISIONS.md exposed two different accepted decisions both named ADR-008. Because duplicate durable authority IDs require a new explicit choice, the merge was aborted under the route. Main returned exactly to cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47, .vscode/ remained present and untracked, the feature worktree remained clean at edd148f30b7ba001a8dfb754ebb6856f119ed3a2, and no remote action occurred.

The canonical least-change resolution keeps the reviewed product ADR lineage unchanged: ADR-008 direct-sales PPL, ADR-009 immutable decision cutoffs, ADR-010 Windows PWA, ADR-011 product-first selling package, and ADR-012 single-owner policy foundation. The branch-local governance-retirement decision from cdd71c0 becomes canonical ADR-013 and is appended after ADR-012 with a short integration-renumber note. Its decision content and consequences do not change.

Update only governance-retirement references from ADR-008 to ADR-013. Product and PPL references to ADR-008 remain ADR-008. This is an identity collision correction, not a product, policy, or runtime behavior change.

## Resolution Paths

Conflict resolution and truth refresh may edit exactly these five documentation paths:

- ARCHITECTURE.md
- DECISIONS.md
- OPERATIONS.md
- docs/superpowers/plans/2026-07-18-codebase-scan-remediation.md
- docs/superpowers/specs/2026-07-18-codebase-scan-remediation-design.md

ARCHITECTURE.md and OPERATIONS.md must retain the applicable unique truth from both parents. Where old and feature-era counts or line anchors differ, use the merged tree and fresh committed instruments rather than either stale number. The two codebase-scan documents change only their governance ADR identifier references. No other automatically merged path may be edited during resolution.

## Side-Effect Executor Token

- effect: git merge
- executor: coordinator
- target: /Users/hyungkoookkim/evidence-ledger local main
- scope: main at cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47, feature at edd148f30b7ba001a8dfb754ebb6856f119ed3a2, one two-parent local merge commit, exact five-document ADR and truth resolution, preserve untracked .vscode

## Exact Integration Contract

Preflight must show Pipeline at the committed version of this route with route validation, route lineage, Protocol Doctor, and smoke green. The local integration checkout must still be main at cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47, with origin/main locally tracking the same commit, no staged or unmerged paths, and only .vscode/ untracked. The feature worktree must remain clean at edd148f30b7ba001a8dfb754ebb6856f119ed3a2. The canonical GO must still validate against its exact request.

Run exactly:

```text
env -u GIT_INDEX_FILE git merge --no-ff --no-commit edd148f30b7ba001a8dfb754ebb6856f119ed3a2
```

Require the actual unmerged set to be exactly ARCHITECTURE.md, DECISIONS.md, and OPERATIONS.md. Resolve the five named documentation paths under the reconciliation above. Do not edit any application, migration, test, package, lockfile, configuration, or other path.

If the actual unmerged set differs, another authority collision appears, a resolution needs a product or policy choice, any preflight binding changes, or any check fails before commit, coordinator stops and uses git merge --abort to restore exact main cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47 while preserving .vscode/.

Before commit, require no unmerged paths, no conflict markers, diff check clean, unique DECISIONS headings ADR-001 through ADR-013, exactly one ADR-008 and one ADR-013, unchanged product ADR-008 references, corrected governance ADR-013 references, and a staged tree containing only the deterministic merge result plus the five authorized documentation resolutions.

Create one local merge commit with parents exactly cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47 and edd148f30b7ba001a8dfb754ebb6856f119ed3a2.

## Postchecks

Run check_doc_claims for ARCHITECTURE.md and OPERATIONS.md and require clean results. Run the evidence-ledger project smoke and require OK. From web, require the focused 79 tests, typecheck, the complete 140 tests, and default-heap build:ci with the two-file dist check. Recheck the three frozen contract hashes from the verify-request.

Require local main to equal the new two-parent merge commit. Require the feature worktree to remain clean at edd148f30b7ba001a8dfb754ebb6856f119ed3a2. Require the integration checkout to remain clean except for the preserved untracked .vscode/ directory. Require the local origin/main tracking ref to remain cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47.

No push is authorized.
No network action is authorized.
No dependency installation is authorized.
No service lifecycle or managed database/Auth action is authorized.
No real or private value is authorized.
No booking, spend, deployment, or policy activation is authorized.
No cursor consumption or protocol lock action is authorized.
No cleanup, reset, rebase, amend, or feature-worktree mutation is authorized.

## Exact Next Trigger

After this route is committed and validates cleanly, coordinator performs the exact local integration contract once. Success ends with the verified local merge commit on evidence-ledger main, canonical unique ADR identities, preserved .vscode/, unchanged feature head, unchanged local origin/main tracking ref, and no remote publication.

Cursor at send: 0
