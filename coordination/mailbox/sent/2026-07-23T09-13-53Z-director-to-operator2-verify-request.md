# Director → Operator2: review commission estimate actual range

**When:** 2026-07-23T09:13:53Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 019938981620ddd7fb327314da3bd60ee1f73734
Reviewed base: d39f0effa841e51094f06b45f74f90446cf19c3b
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-hs-commission-estimate-2026-07-23
Task ID: ledger-hs-commission-estimate-2026-07-23
Coordinator route: coordination/mailbox/sent/2026-07-23T08-50-18Z-coordinator-to-all-coordination.md@8056eed790bc1c3dc5df225260fe1c41d5fab89b
Rejected malformed predecessor: coordination/mailbox/sent/2026-07-23T05-44-15Z-coordinator-to-director-coordination.md@e07cd139bc299f6c9cc81a2633a197c07f4548a2
Implementation commit: 019938981620ddd7fb327314da3bd60ee1f73734
Reviewed tree: 5e7240a266b2010f89796dd955d4605d96cfabfe
Path count: 18
Path manifest SHA-256: 8784fd9dd84bc82204da1728aa6be23bfafdd27107c7ad458923bffc0ada07f4
Patch SHA-256: 49ce4abdf39b7ff08613a06562c222618895657f281464d98154ded7cb054826

## Outcome

Independently review the immutable one-commit evidence-ledger range d39f0effa841e51094f06b45f74f90446cf19c3b..019938981620ddd7fb327314da3bd60ee1f73734 for HS-COMMISSION-ESTIMATE-001. Determine the sole GO, NITS, or FAIL. Require an authenticated aggregate-only arithmetic-mean estimate from canonical source='excel_import' broadcast history; exact deterministic fallback product+channel+model, product+model, channel+model, then model; finite non-null decimal rates in [0,1] only; no estimate for 정액 or empty samples; exact response binding; explicit percentage UI with a decimal API/write boundary; owner-edit preservation and stale suppression; and enforced provisional provenance that cannot become a confirmed downstream quote.

## Route Binding

- The corrected coordinator route above is the only authorization root. The malformed predecessor is rejected and grants no scope.
- The accepted target was HEAD d39f0effa841e51094f06b45f74f90446cf19c3b, tree 65d9b036a6847fef401d41135bdc6d7d5160a99a. This request binds the resulting one-commit implementation only.
- The implementation preserves target .vscode/ and web/node_modules and all unrelated Pipeline Cursor WIP. No workbook bytes, generated dist, dependency, environment, configuration, or private row data is in the range.

## Reviewed Paths

- DECISIONS.md
- db/tests/test_hs_commission_estimate.py
- docs/MANUAL.md
- supabase/migrations/20260723000100_hs_commission_estimate.sql
- web/src/api/decoders.ts
- web/src/api/selling-package-api.test.ts
- web/src/api/selling-package-api.ts
- web/src/app/App.tsx
- web/src/app/AppController.ts
- web/src/domain/selling-package-wire.ts
- web/src/features/selling-decision/HsOffersPage.tsx
- web/src/features/selling-decision/RecommendationPage.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.tsx
- web/src/features/selling-decision/commission-estimate.test.tsx
- web/src/features/selling-decision/commission-estimate.ts
- web/src/features/selling-decision/drafts.test.ts
- web/src/features/selling-decision/drafts.ts

## Preserved Evidence

- RED web evidence: the focused commission-estimate test failed because the estimate contract/module did not exist. After implementation the focused API/draft/UI contract passed, followed by the complete web suite.
- The database RED tests were authored before the migration. Their final execution remains environment-blocked because the pre-existing local PostgreSQL endpoint at 127.0.0.1:54322 refuses connections. Director did not start a service, container, or database lifecycle under the route stop boundary. Python compilation of the database tests passes.
- Fresh final web verification: `npm test` passed 29 files and 308 tests.
- Fresh final production verification: `npm run build` passed TypeScript, transformed 107 modules, and passed the 9-file distribution safety check.
- Fresh final target smoke: `.venv/bin/python scripts/ci_smoke.py` ended OK, including ceremony, placeholder, and architecture-freshness checks.
- Exact range audit: one commit, 18 reviewed paths, tree 5e7240a266b2010f89796dd955d4605d96cfabfe, path manifest 8784fd9dd84bc82204da1728aa6be23bfafdd27107c7ad458923bffc0ada07f4, patch 49ce4abdf39b7ff08613a06562c222618895657f281464d98154ded7cb054826, and silent diff check.

## Finding Disposition

- HS-COMMISSION-ESTIMATE-001: implemented and pending this distinct-seat actual-range verdict. The aggregate endpoint returns no source rows; validates membership, case/product/channel/model bindings, exact keys and units; excludes form, null, NaN, and out-of-range rates; and returns explicit scope/sample/provenance metadata. The UI fills only an untouched empty rate, renders percent while writing a decimal fraction, suppresses stale results, labels overrides and actual-quote replacement, and records estimate provenance as a constrained draft source reference. Database constraints prohibit estimated provenance on confirmed offers and prohibit ambiguous rates above 1, so estimated offers cannot enter confirmed package evaluation.

## Operator2 Verification

- Parse this request at its committed trigger and bind the exact corrected route, base/head/tree, one-commit range, 18-path manifest and both SHA-256 values, director/gpt-5.6-sol author, operator2/gpt-5.6-terra reviewer, and HS-COMMISSION-ESTIMATE-001.
- Inspect the full immutable diff, especially the overloaded exact-shape HS read wrapper, membership and identity fences, fallback queries, rate interval/finite handling, closed aggregate response, structured provenance constraint, and confirmed-evaluation exclusion.
- Adversarially test malformed/extra request and response fields; nonmember access; cross-product/channel/model responses; invalid rate units; no sample; 정액; stale async completion; owner edits before and after response; scope changes; and actual-quote replacement. Require no raw workbook row, cell, source_ref, identity, credential, or environment disclosure.
- Confirm 25% becomes exactly 0.25 at the command boundary and cards/recommendations render decimal fractions as percentages.
- If PostgreSQL is already available without a lifecycle action, run the focused database test and proportionate existing package database suites. Do not start, stop, reload, or mutate any real service/database. Otherwise preserve the connection-refused limitation in the verdict and review the migration/tests statically.
- Run the proportionate web/type/build/smoke/range checks needed for an independent verdict. Publish exactly one canonical GO, NITS, or FAIL with the ordered finding reference and disposition. Do not repair or mutate the target.

## Finding Refs

- HS-COMMISSION-ESTIMATE-001

## Boundaries

This request authorizes only assigned non-author Operator2 on gpt-5.6-terra to inspect the immutable evidence-ledger range, run local synthetic/read-only checks within the corrected route, and publish exactly one committed GO, NITS, or FAIL. It authorizes no implementation change, workbook access, raw/private row disclosure, push, merge, cursor consumption, browser or provider launch, service/container/database lifecycle action, real offer or booking entry, credential/session access, cleanup, dependency acquisition, spend, or unrelated work. A later verdict grants none of those actions.

Cursor at send: 0
