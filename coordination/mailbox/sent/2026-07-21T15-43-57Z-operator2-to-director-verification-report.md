# Operator2 → Director: NITS Task 5C retained build artifact

**When:** 2026-07-21T15:43:57Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-07-21T15-27-31Z-director-to-operator2-verify-request.md@5b4639f0a7c0211bd5a41b4ddc6e722eab843cb7
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: ef4f42a902dd1ce5866e6ba82651d4514da80b94
Reviewed base: 68566090b2904b86f48e42ffb5f3216856b8ac1c
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: Fresh immutable-binding, actual-diff, synthetic test, static-boundary, target-state, and carried-finding reconciliation.
Verification context: No target repair, cleanup, integration, push, cursor, lock, service lifecycle, managed/private data access, booking, spend, deployment, or other external effect was taken.

## Allowed Paths

- web/src/app/App.tsx
- web/src/app/AppController.ts
- web/src/components/AsyncState.tsx
- web/src/components/ConfirmDialog.tsx
- web/src/components/FieldError.tsx
- web/src/components/LoadMoreButton.tsx
- web/src/components/StatusBadge.tsx
- web/src/components/format.test.ts
- web/src/components/format.ts
- web/src/features/recovery/command-runner.test.ts
- web/src/features/recovery/command-runner.ts
- web/src/features/selling-decision/EvidencePanel.tsx
- web/src/features/selling-decision/HsOffersPage.tsx
- web/src/features/selling-decision/OwnerDecisionPanel.tsx
- web/src/features/selling-decision/PplOptionsPage.tsx
- web/src/features/selling-decision/ProductPage.tsx
- web/src/features/selling-decision/RecommendationPage.tsx
- web/src/features/selling-decision/RevisionHistory.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.test.tsx
- web/src/features/selling-decision/SellingDecisionWorkspace.tsx
- web/src/features/selling-decision/accessibility.test.tsx
- web/src/features/selling-decision/drafts.test.ts
- web/src/features/selling-decision/drafts.ts
- web/src/features/selling-decision/pagination.test.ts
- web/src/features/selling-decision/pagination.ts
- web/src/styles/app.css

## Findings

MINOR — The packet's final hygiene condition is not met: the exact required `npm run build:ci` and `npm run test:e2e` commands retain ignored `web/dist`, while the request explicitly requires no `dist` after verification and grants no cleanup authority. The directory remains after all checks; no test-results, Playwright report/media, retained listener, or tracked target change exists. This blocks GO on the packet's literal final-state condition but does not negate the functional/security evidence below.

## Finding Refs

- coordination/mailbox/sent/2026-07-21T14-34-43Z-coordinator-to-all-coordination.md@cebef9da7d61428b804879cc58fd4a1dd17e28de
- coordination/mailbox/sent/2026-07-21T14-27-25Z-director-to-coordinator-coordination.md@e1217d2f57913adb46e2d8b644d35a2803f69959
- coordination/mailbox/sent/2026-07-21T14-38-43Z-director-to-all-coordination.md@05c017ed1b50faf678e4400a1c094137640e0062
- coordination/mailbox/sent/2026-07-21T11-32-35Z-coordinator-to-all-coordination.md@00677e02887cf84eafc630b24ce60dd60d581f42
- coordination/mailbox/sent/2026-07-21T11-38-32Z-director-to-all-coordination.md@111266573da8b8d92eba29108b1e39c7fd181f7b
- coordination/mailbox/sent/2026-07-21T11-30-11Z-director-to-all-coordination.md@952ad5cfc1d6382fc3ace4100e0ff7f91355ef1a
- coordination/mailbox/sent/2026-07-21T10-52-10Z-operator2-to-director-verification-report.md@3a53358d27b564d1391465497d74c0efad1d96ca
- sha256:d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208
- sha256:3620a332470ce8f572f972e91d96059b23828f1607b15ca2556889cb0bb1046d
- sha256:f803ab54d0b72bed5b0958bbd1cf2acbc113d581cac3d603bc7daa6d86369632
- sha256:5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e

## Finding Dispositions

- coordination/mailbox/sent/2026-07-21T14-34-43Z-coordinator-to-all-coordination.md@cebef9da7d61428b804879cc58fd4a1dd17e28de: unresolved-hard-boundary
- coordination/mailbox/sent/2026-07-21T14-27-25Z-director-to-coordinator-coordination.md@e1217d2f57913adb46e2d8b644d35a2803f69959: addressed
- coordination/mailbox/sent/2026-07-21T14-38-43Z-director-to-all-coordination.md@05c017ed1b50faf678e4400a1c094137640e0062: addressed
- coordination/mailbox/sent/2026-07-21T11-32-35Z-coordinator-to-all-coordination.md@00677e02887cf84eafc630b24ce60dd60d581f42: addressed
- coordination/mailbox/sent/2026-07-21T11-38-32Z-director-to-all-coordination.md@111266573da8b8d92eba29108b1e39c7fd181f7b: addressed
- coordination/mailbox/sent/2026-07-21T11-30-11Z-director-to-all-coordination.md@952ad5cfc1d6382fc3ace4100e0ff7f91355ef1a: addressed
- coordination/mailbox/sent/2026-07-21T10-52-10Z-operator2-to-director-verification-report.md@3a53358d27b564d1391465497d74c0efad1d96ca: addressed
- sha256:d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208: addressed
- sha256:3620a332470ce8f572f972e91d96059b23828f1607b15ca2556889cb0bb1046d: addressed
- sha256:f803ab54d0b72bed5b0958bbd1cf2acbc113d581cac3d603bc7daa6d86369632: addressed
- sha256:5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e: addressed

## Evidence

$ .venv/bin/python -c 'compact_pair_loop.parse_verify_request(...)'
→ Request parse PASS: reviewed repository /Users/hyungkoookkim/evidence-ledger, exact base/head, director/gpt-5.6-sol, assigned operator2, and 11 ordered finding refs.
$ git show --format=fuller --name-status --stat ef4f42a902dd1ce5866e6ba82651d4514da80b94; git rev-list --count 68566090b2904b86f48e42ffb5f3216856b8ac1c..ef4f42a902dd1ce5866e6ba82651d4514da80b94; git diff --name-only; git diff --check
→ Exact parent 68566090b2904b86f48e42ffb5f3216856b8ac1c, subject feat(web): add product-first selling workflow, one commit, exact 26-path manifest, and silent whitespace check.
$ git cat-file -e '<commit>^{commit}' and git cat-file -e '<commit>:<path>' for all seven path-at-commit refs
→ All seven immutable path refs resolve to their named committed paths.
$ npm test -- six focused files; npm test; npm run typecheck; npm run build:ci; npm run test:e2e
→ Focused 6 files/71 tests, complete 20 files/213 tests, typecheck pass, 102 transformed modules with three-file dist guard, and loopback-only Playwright 5/5.
$ /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_owner_settings_api.py db/tests/test_owner_settings_security.py db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_evaluation.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py -q; /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ Exact database selector 148 passed; target smoke ended OK.
$ command-runner direct/retry mismatch regressions and final runner source inspection
→ Operation-aware strict response decode and exact request-ID equality occur before clearTerminal; mismatched direct/retry responses remain ambiguous with the journal retained.
$ caseScopeKey review in SellingDecisionWorkspace and product/PPL/HS/recommendation/owner source review
→ Product form resets by selected revision; hidden visited HS, PPL, and recommendation pages are keyed by selling_case_id:selling_case_revision_id, so they remount and clear case-scoped drafts, including owner intent.
$ added production-line abuse scan; persistence inventory; raw PPL operation scan
→ No prohibited added production match; only the reviewed pending-journal Local Storage and auth Session Storage adapters exist; raw PPL formula/policy/activation operations have zero matches.
$ sha256 checks for routed one-user design at e091c436b86551efa7a9fe62b55c923818ac3eae, three target design/plan files, and protected settings
→ d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208, 3620a332470ce8f572f972e91d96059b23828f1607b15ca2556889cb0bb1046d, f803ab54d0b72bed5b0958bbd1cf2acbc113d581cac3d603bc7daa6d86369632, 5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e, and a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4 exactly match.
$ git status --short --untracked-files=no; git status --short; find web -maxdepth 2 -type d \( -name dist -o -name test-results -o -name playwright-report \); lsof -nP -iTCP:4173 -sTCP:LISTEN
→ Tracked target state is clean and web/node_modules is the sole untracked donor symlink, but ignored web/dist remains; no test-results, Playwright report/media, or listener remains. No cleanup was authorized or performed.

Cursor at send: 0
