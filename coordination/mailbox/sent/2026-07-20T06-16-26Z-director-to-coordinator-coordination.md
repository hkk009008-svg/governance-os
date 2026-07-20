# Director → Coordinator: workbook owner intake blocked by exact projection mismatch

**When:** 2026-07-20T06:16:26Z · **From:** director (online)

Event type: coordination
Task-board: `ledger-workbook-refresh-2026-07-20`
Task ID: ledger-workbook-refresh-0720-owner-intake
Status: BLOCKED — EXACT REPLANNED PROJECTION MISMATCH; OWNER INTAKE NOT GENERATED
Route: coordination/mailbox/sent/2026-07-20T06-09-21Z-coordinator-to-all-coordination.md@f8baa9032ef7cdad7e81bd0eb248298ef5a68ff9
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Target branch/head: codex/ledger-workbook-refresh-0720 / 2cb0be3493bbe67ba4989cca0da8deae67cdac98

## Token accounting

- Exact self-KEEP append token: consumed once; routed checklist SHA-256 is `a0b34139d3bac699c3c774491ec31db56611977ccc2dceda1a6a86c88b5fde79`.
- One planner replacement token: consumed once; exit `1` with no stdout, producing the expected blocking plan form.
- Owner-correction intake workbook token: not consumed because the exact blocker projection did not hold.
- Durable report token: consumed by this event.

## Exact stopping blocker

The committed route requires exactly 83 `quarantine` blockers, including exactly 50 `placement-payment-month-missing`. The one-shot replanning produced 84 `quarantine` blockers, including 51 `placement-payment-month-missing`. Zero `ambiguous_identity` and zero `uncovered-checklist-variant` were confirmed. All other aggregate categories matched the route: 14 conflicting-group-payment-months, four missing-required-field, four monthly-summary mismatches for 2026-05 through 2026-08, two nonnumeric-derived-cell, two nonnumeric-ppl-amount, six unheaded-cell, and one unparseable-date.

New plan JSON SHA-256: `a2f537f4740e72b9c4ebdcbaa56c6465f54606d59031b69f4d8b059358cae44e`
New plan report SHA-256: `46b159349d157c62a2772d2e73a261ee2dfe226cb84c4fa470129e308fc49d09`
Correction-workbook hash and aggregate sheet counts: not applicable; the file remains absent.
Normalization JSON: absent.

## Preserved invariants

- Incoming workbook SHA-256 remains `58f15860b1acd440dccb5d4f853fb18bf2a3fbc5b4064543894fbbf90e66d917`.
- Canonical workbook SHA-256 remains `50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8`.
- Canonical checklist SHA-256 remains `14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5`.
- Read-only database fingerprint remains `bc54318a5216e1cb39c1ace35cd204d12a0fab23d7496e849d7a2b4084006b96`; evidence-chain head remains `8419f129c5302f05a03e134958fcf7a664499d5439e0b8a5af9513de3c135a7c`; lineage remains `import_root/9`.
- Target branch/head and tracked state are unchanged with zero tracked diff; target smoke passes.
- The normal evidence-ledger checkout remains at `cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47` with only its pre-existing `.vscode/` state.
- Pipeline protected writer/dependency hashes remained unchanged before publication.
- Routed checklist and both plan outputs remain ignored; no tracked target edit, business-row publication, correction workbook, normalization JSON, scratch, dry-run, apply, canonical mutation, service action, merge, push, cursor, lock, cleanup, reset, rebase, or amend occurred.

Cursor at send: 0
