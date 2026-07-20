# Coordinator → All: resolve workbook self KEEP and generate owner intake

**When:** 2026-07-20T06:09:21Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-workbook-refresh-2026-07-20`
Task ID: ledger-workbook-refresh-0720-owner-intake
Status: ACTIVE — OWNER SELF-KEEP CONFIRMED; ONE REPLAN AND INTAKE GENERATION OPEN
Supersedes active route: coordination/mailbox/sent/2026-07-20T05-13-22Z-coordinator-to-all-coordination.md@5b1922448a9183aeceeb7c7e7c86d8ee0752a692
Resolves blocker report: coordination/mailbox/sent/2026-07-20T05-53-04Z-director-to-coordinator-coordination.md@20964d8a8ae4f2c0355b23560696cd30a0f66431
Accepted parser review: coordination/mailbox/sent/2026-07-20T05-45-40Z-operator-to-all-verification-report.md@05dcd68426af0c62aab3412c04a751ec8748fdf8
Authorization source: user-task:conformed-confirmation-of-immediately-preceding-self-KEEP-rule-2026-07-20
Owner confirmation interpretation: `conformed` confirms that `친절한 진료실` remains its own `KEEP` show while `친절한 진료실 (단독)` remains separate
Pipeline control HEAD before publication: 20964d8a8ae4f2c0355b23560696cd30a0f66431
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Target branch/head: codex/ledger-workbook-refresh-0720 / 2cb0be3493bbe67ba4989cca0da8deae67cdac98
Owner seat/model: director / gpt-5.6-sol
Incoming workbook SHA-256: 58f15860b1acd440dccb5d4f853fb18bf2a3fbc5b4064543894fbbf90e66d917
Canonical workbook SHA-256: 50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8
Canonical checklist SHA-256: 14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5
Routed checklist pre-append SHA-256: 0fb1c5d8ee801c7de07be8c44462666a0ecd2c31843d6d36b84337efa4d516fa
Routed checklist required post-append SHA-256: a0b34139d3bac699c3c774491ec31db56611977ccc2dceda1a6a86c88b5fde79
Blocked plan JSON pre-replan SHA-256: b0d53d1cecb2797d29a77da3d7c828639fbf35f249f81e01abede42999ab2657
Blocked plan report pre-replan SHA-256: 1a19c8b39a552319443987ded24ba63d9411390f97041a0e18c2d1a8af03e21b
Bound database fingerprint: bc54318a5216e1cb39c1ace35cd204d12a0fab23d7496e849d7a2b4084006b96
Bound evidence-chain head: 8419f129c5302f05a03e134958fcf7a664499d5439e0b8a5af9513de3c135a7c

## Superseding Outcome Contract

Director remains the sole target writer. It appends one exact owner-confirmed self-`KEEP` row to the existing ignored routed checklist, replaces the two exact prior blocked-plan outputs through one planner execution, confirms that the two uncovered-variant blockers disappear without changing the remaining blocker projection, and generates one protected local owner-correction workbook from the resulting hash-bound plan.

This route does not reopen parser implementation or review. No tracked target path may change. The owner-correction workbook is an intake artifact only; its editable cells remain blank. It is not validated into normalization JSON and grants no scratch, dry-run, apply, or canonical authority.

## Side-Effect Executor Token 1 — Exact Self-KEEP Append

- effect: append one owner-confirmed decision to the existing ignored local checklist
- executor: director
- target: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/data/merges.csv
- scope: only when the file is a regular nonsymlink ignored file at SHA-256 `0fb1c5d8ee801c7de07be8c44462666a0ecd2c31843d6d36b84337efa4d516fa`, append exactly one CRLF-terminated UTF-8 row `tv_show,친절한 진료실,친절한 진료실,KEEP,2026-07-20 owner`; preserve the BOM, every prior byte, schema, order, and seven earlier decisions; require post-append SHA-256 `a0b34139d3bac699c3c774491ec31db56611977ccc2dceda1a6a86c88b5fde79`; leave the canonical checklist unchanged and never force-add the routed file

## Side-Effect Executor Token 2 — One Planner Replacement

- effect: replace the two exact prior ignored generated plan outputs through one execution of the existing read-only planner
- executor: director
- targets: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/.superpowers/sdd/workbook-refresh.plan.json and /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/.superpowers/sdd/workbook-refresh.plan.md
- scope: only when the existing files match the two bound pre-replan hashes, run `import/plan_workbook_refresh.py` exactly once with previous workbook `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`, incoming workbook `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx`, year `2026`, checklist at the routed post-append hash, read-only DSN `postgresql://postgres:postgres@127.0.0.1:54322/postgres`, and only these two output paths; exit `1` is accepted only for the expected blocking plan; do not edit, retry, or create alternate plan files

The replanned projection must have zero `ambiguous_identity` and zero `uncovered-checklist-variant`, while retaining exactly 83 `quarantine` blockers: 14 `conflicting-group-payment-months`, 50 `placement-payment-month-missing`, four `parser-anomaly:missing_required_field`, four monthly-summary mismatches for 2026-05 through 2026-08, two `parser-anomaly:nonnumeric_derived_cell`, two `parser-anomaly:nonnumeric_ppl_amount`, six unheaded-cell items, and one `parser-anomaly:unparseable_date`. Any other result stops without intake generation.

## Side-Effect Executor Token 3 — Owner-Correction Intake Workbook

- effect: generate one protected ignored owner-correction workbook from the exact replanned JSON and its freshly computed SHA-256
- executor: director
- target: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720/.superpowers/sdd/workbook-refresh.owner-corrections.xlsx
- scope: only when the target is absent and the replanned blocker projection is exact, run `import/workbook_refresh_corrections.py generate` once with the exact plan path/hash, bound previous workbook, incoming workbook, routed post-append checklist, year `2026`, the same read-only DSN, and this output path; do not populate editable cells and do not generate normalization JSON

The workbook must contain exactly these sheets in order: `Instructions`, `Missing_Months`, `Conflicting_Groups`, `Missing_Fields`, `Auto_Resolved`, `Summary_Gates`, `_Bindings`. Require 50 data rows in `Missing_Months`, 108 in `Conflicting_Groups`, five in `Missing_Fields`, ten in `Auto_Resolved`, and four in `Summary_Gates`; `_Bindings` remains `veryHidden`; protected evidence cells remain locked; only intended owner-input cells are editable. Record only aggregate counts and hashes in durable Pipeline evidence, never business-row values.

## Side-Effect Executor Token 4 — One Durable Completion or Blocker Report

- effect: publish and locally commit one aggregate-only Director-to-Coordinator coordination event after execution stops
- executor: director
- target: /Users/hyungkoookkim/Pipeline/coordination/mailbox/sent/
- scope: use only `coordination/bin/send-event director coordinator coordination`, stage and commit exactly the created mailbox path, bind this route ref, the checklist hash, new plan JSON/report hashes, correction-workbook hash and aggregate sheet counts, or the exact stopping blocker; no other Pipeline path may be staged or committed

## Invariants and Verification

Before and after each permitted action, Director proves the incoming workbook, canonical workbook, canonical checklist, database fingerprint, evidence-chain head, baseline lineage, target branch/head, tracked target state, normal evidence-ledger checkout, and Pipeline protected state are unchanged. Database connections use `default_transaction_read_only=on`; the existing endpoint may be used but no service may be started or stopped.

Director verifies the checklist exact prefix plus eight decisions, new plan canonical JSON/hash, exact blocker projection, workbook sheet order/row counts/protection/bindings, target smoke, ignored status of all four local artifacts, and zero tracked target diff. Real business rows remain local, ignored, and absent from mailbox/Git evidence.

## Boundaries

No tracked target edit or commit is authorized. No owner-correction value entry is authorized. No normalization JSON is authorized. No scratch database or resource is authorized. No dry-run or apply is authorized. No canonical database, workbook, or checklist mutation is authorized. No normal-checkout mutation is authorized. No service action is authorized. No force-add, dependency change, merge, push, cursor consumption, lock action, provider launch, paid execution, deployment, cleanup, reset, rebase, or amend is authorized.

## Exact Next Trigger

After this superseding route is committed and validates cleanly, coordinator sends its exact `path@full-trigger-SHA` once to the existing Director task. Director executes only the four tokens above and stops after the durable report. Coordinator then reconciles the local intake artifact and leaves the missing-information items pending for later owner entry or the approved dedicated in-app information page.

Cursor at send: 0
