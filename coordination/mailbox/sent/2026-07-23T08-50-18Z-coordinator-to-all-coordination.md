# Coordinator → All: Route corrected commission estimate

**When:** 2026-07-23T08:50:18Z · **From:** coordinator (online)

Event type: coordination
Status: ROUTED
Task-board: ledger-hs-commission-estimate-2026-07-23
Route generation: 0
Task ID: ledger-hs-commission-estimate-2026-07-23
Outcome contract: remove the need for an owner to know an exact non-fixed home-shopping commission rate by deriving a transparent arithmetic-mean estimate from canonical Excel-imported history, preserving provenance and uncertainty, and integrating the estimate into the current product-first selling workflow without exposing private workbook rows or fabricating a confirmed quote.
Parent contract: user-task:derive-average-from-excel-resource-2026-07-23
Contract revision: 0
Previous owners: none
Owners: director
Proposal ref: coordinator-observed-teaching-feedback
Acceptance refs: user-task:derive-average-from-excel-resource-2026-07-23
Finding refs: HS-COMMISSION-ESTIMATE-001
Authorization source: user message "user does not know exact amount of the value on 수수로울 derive average from the excel resouce"
Malformed predecessor: coordination/mailbox/sent/2026-07-23T05-44-15Z-coordinator-to-director-coordination.md@e07cd139bc299f6c9cc81a2633a197c07f4548a2
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Accepted target HEAD: d39f0effa841e51094f06b45f74f90446cf19c3b
Accepted target tree: 65d9b036a6847fef401d41135bdc6d7d5160a99a
Canonical workbook: /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx
Canonical workbook SHA-256: 50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8
Coordinator aggregate-only observation: 443 parsed schedule rows; 407 valid numeric rates in [0,1]; overall arithmetic mean 0.35005405. Do not publish row-level workbook data.

## Required behavior

- For a selected selling case, channel, and non-fixed commission model, obtain an arithmetic-mean commission-rate estimate from canonical Excel-imported biz.broadcast_slots history. Use only finite non-null rates in [0,1] with source='excel_import'; do not use manually entered, agency, synthetic, draft-offer, or unrelated rows.
- Prefer the narrowest non-empty scope in this deterministic order: selected product + selected channel + selected model; selected product + selected model; selected channel + selected model; selected model. Return and display the chosen scope and exact sample count. No numeric sample means no estimate.
- Treat 정액 as fixed-fee economics: do not derive or require a percentage estimate for it.
- Present the value as a percentage to the owner while preserving the canonical decimal fraction at the API/write boundary. Make the unit explicit and regression-test the conversion so 25% is stored/evaluated as 0.25, never 25 or 0.0025.
- The UI may populate an empty rate from the estimate, but must never overwrite an owner edit. It must label the value 엑셀 이력 평균 추정치, show the sample count and scope, allow override, and explain that the actual quote should replace it.
- Do not silently misrepresent an estimate as a verified or confirmed quote. Preserve machine-readable provenance sufficient for the workflow and evidence surface to distinguish a workbook-derived assumption from an actual quoted rate, and cap or label downstream decision output proportionally until an actual quote replaces it. Choose the smallest schema-compatible design that enforces this invariant rather than relying on free-form prose alone.
- Fail closed on malformed requests or responses, unauthorized or nonmember access, invalid rates, unit ambiguity, cross-product or channel leakage, no-sample cases, stale async estimates, and estimate responses that do not bind the requested product, channel, and model.
- Return only aggregates and provenance metadata; no raw workbook rows, private cell values, credentials, identities, or environment values may reach the web client, logs, tracked docs, or mailbox.

## Target Allowed Paths

- supabase/migrations/
- db/tests/
- web/src/api/
- web/src/app/
- web/src/domain/
- web/src/features/selling-decision/
- web/src/test/
- web/playwright.config.ts
- docs/MANUAL.md
- DECISIONS.md

## Verification contract

- Refresh target HEAD, tree, and status immediately before the first write; stop and reconcile if tracked state differs from the accepted target or unrelated changes overlap allowed paths.
- Establish RED behavior tests first where feasible. Include aggregate selection and fallback, Excel-source-only filtering, null and invalid exclusion, no-sample and 정액 behavior, authorization and closed response shape, percentage-to-decimal conversion, owner override preservation, stale-response suppression, provenance display, and non-confirmation or provisional downstream semantics.
- Run the smallest sufficient database and web unit or integration suites, TypeScript typecheck, production build, and target scripts/ci_smoke.py; record exact commands and results.
- Commit only target allowed paths with explicit pathspecs. Do not modify or commit workbook bytes, generated web/dist, dependencies, environment or config files, private data, or unrelated state.
- Publish one committed exact verify-request binding the actual implementation range, author identity director, assigned non-author reviewer operator2, and finding HS-COMMISSION-ESTIMATE-001. Stop for Operator2 verdict.

## Stop boundary

Director owns implementation, focused verification, target commit, and one exact verify-request. No push, merge, remote publication, browser interaction, credential or session access, live preview build, reload, restart, service, container, or database lifecycle action, real offer or booking entry, spend, lock, cursor consumption, cleanup, or unrelated Pipeline, Cursor, Claude, or AGY work is authorized.

## Exact next trigger

Director: accept this committed corrected route, implement the commission estimate in /Users/hyungkoookkim/evidence-ledger from accepted HEAD d39f0effa841e51094f06b45f74f90446cf19c3b, commit only allowed paths, publish the exact Operator2 verify-request, and stop for verdict.

Cursor at send: 0
