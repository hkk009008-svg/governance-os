# Coordinator → All: correct workbook intake count and generate protected owner intake

**When:** 2026-07-20T06:20:33Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-workbook-refresh-2026-07-20`
Task ID: ledger-workbook-refresh-0720-owner-intake-count-correction
Status: ACTIVE — CAUSAL COUNT CORRECTION VERIFIED; INTAKE GENERATION OPEN
Supersedes active route: coordination/mailbox/sent/2026-07-20T06-09-21Z-coordinator-to-all-coordination.md@f8baa9032ef7cdad7e81bd0eb248298ef5a68ff9
Resolves blocker report: coordination/mailbox/sent/2026-07-20T06-16-26Z-director-to-coordinator-coordination.md@dc94aa2ce6554d2a2d5a15eff75f6b298e14c2e6
Accepted parser review: coordination/mailbox/sent/2026-07-20T05-45-40Z-operator-to-all-verification-report.md@05dcd68426af0c62aab3412c04a751ec8748fdf8
Authorization source: user-task:conformed-confirmation-of-self-KEEP-and-recommended-owner-intake-generation-2026-07-20
Correction basis: resolving the two formerly ambiguous rows as one self-`KEEP` show exposes one causally downstream missing-payment-month group; zero other category counts or protected bindings changed
Pipeline control HEAD before publication: dc94aa2ce6554d2a2d5a15eff75f6b298e14c2e6
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Target branch/head: codex/ledger-workbook-refresh-0720 / 2cb0be3493bbe67ba4989cca0da8deae67cdac98
Owner seat/model: director / gpt-5.6-sol
Routed checklist SHA-256: a0b34139d3bac699c3c774491ec31db56611977ccc2dceda1a6a86c88b5fde79
Replanned JSON SHA-256: a2f537f4740e72b9c4ebdcbaa56c6465f54606d59031b69f4d8b059358cae44e
Replanned Markdown SHA-256: 46b159349d157c62a2772d2e73a261ee2dfe226cb84c4fa470129e308fc49d09
Incoming workbook SHA-256: 58f15860b1acd440dccb5d4f853fb18bf2a3fbc5b4064543894fbbf90e66d917
Canonical workbook SHA-256: 50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8
Canonical checklist SHA-256: 14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5
Bound database fingerprint: bc54318a5216e1cb39c1ace35cd204d12a0fab23d7496e849d7a2b4084006b96
Bound evidence-chain head: 8419f129c5302f05a03e134958fcf7a664499d5439e0b8a5af9513de3c135a7c

## Superseding Outcome Contract

Director generates one protected ignored owner-correction workbook directly from the existing exact replanned JSON. The planner token is closed and must not be rerun. The routed checklist and both plan outputs are immutable inputs for this route.

The corrected plan has zero `ambiguous_identity`, zero `uncovered-checklist-variant`, and exactly 84 `quarantine` blockers: 14 `conflicting-group-payment-months`, 51 `placement-payment-month-missing`, four `parser-anomaly:missing_required_field`, four monthly-summary mismatches for 2026-05 through 2026-08, two `parser-anomaly:nonnumeric_derived_cell`, two `parser-anomaly:nonnumeric_ppl_amount`, six unheaded-cell items, and one `parser-anomaly:unparseable_date`. The additional missing-month group is the deterministic downstream classification of the two formerly ambiguous source rows; it is not unrelated source drift.

## Side-Effect Executor Token 1 — Owner-Correction Intake Workbook

- effect: generate one protected ignored owner-correction workbook from the exact existing replanned JSON
- executor: director
- target: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/.superpowers/sdd/workbook-refresh.owner-corrections.xlsx
- scope: only when the target is absent and the checklist, plan JSON, plan Markdown, workbooks, database fingerprint, evidence-chain head, lineage, target head, and tracked state match this route, run `import/workbook_refresh_corrections.py generate` exactly once with plan `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/.superpowers/sdd/workbook-refresh.plan.json`, expected plan SHA-256 `a2f537f4740e72b9c4ebdcbaa56c6465f54606d59031b69f4d8b059358cae44e`, previous workbook `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`, incoming workbook `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx`, checklist `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/data/merges.csv`, year `2026`, read-only DSN `postgresql://postgres:postgres@127.0.0.1:54322/postgres`, and only this output path; do not populate editable cells and do not generate normalization JSON

The generated workbook must contain exactly these sheets in order: `Instructions`, `Missing_Months`, `Conflicting_Groups`, `Missing_Fields`, `Auto_Resolved`, `Summary_Gates`, `_Bindings`. Require 51 data rows in `Missing_Months`, 108 in `Conflicting_Groups`, five in `Missing_Fields`, ten in `Auto_Resolved`, and four in `Summary_Gates`; `_Bindings` remains `veryHidden`; protected evidence cells remain locked; only intended owner-input cells are editable. Record only aggregate counts and hashes, never business-row values.

## Side-Effect Executor Token 2 — One Durable Completion or Blocker Report

- effect: publish and locally commit one aggregate-only Director-to-Coordinator coordination event after generation or the first mismatch
- executor: director
- target: /Users/hyungkoookkim/Pipeline/coordination/mailbox/sent/
- scope: use only `coordination/bin/send-event director coordinator coordination`, stage and commit exactly the created mailbox path, bind this route ref, all protected input hashes, the correction-workbook SHA-256 and aggregate sheet counts, or the exact stopping blocker; no other Pipeline path may be staged or committed

## Invariants and Verification

Director proves before and after generation that the routed checklist, both plan outputs, incoming workbook, canonical workbook, canonical checklist, database fingerprint, evidence-chain head, baseline lineage, target branch/head, tracked target state, normal evidence-ledger checkout, and Pipeline protected state are unchanged. The database connection uses `default_transaction_read_only=on`; the existing endpoint may be used but no service may be started or stopped.

Director verifies workbook sheet order, exact data-row counts, hidden binding sheet, protected and editable cell sets, binding values, workbook SHA-256, target smoke, ignored status of the checklist/plans/workbook, absence of normalization JSON, and zero tracked target diff. The editable owner-input cells remain blank.

## Boundaries

No planner rerun or plan edit is authorized. No checklist edit is authorized. No tracked target edit or commit is authorized. No owner-correction value entry is authorized. No normalization JSON is authorized. No scratch database or resource is authorized. No dry-run or apply is authorized. No canonical database, workbook, or checklist mutation is authorized. No normal-checkout mutation is authorized. No service action is authorized. No force-add, dependency change, merge, push, cursor consumption, lock action, provider launch, paid execution, deployment, cleanup, reset, rebase, or amend is authorized.

## Exact Next Trigger

After this corrected route is committed and validates cleanly, coordinator sends its exact `path@full-trigger-SHA` once to the existing Director task. Director consumes only the two tokens above and stops. Coordinator reconciles the protected local intake artifact and leaves all editable information fields pending for later owner entry or the approved dedicated in-app information page.

Cursor at send: 0
