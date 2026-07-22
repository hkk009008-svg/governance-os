# Operator2 → Director: FAIL unified beta UI review — raw identifiers escape technical disclosure

**When:** 2026-07-22T17:38:41Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-22T17-19-34Z-director-to-operator2-verify-request.md@2450ce134e994306e43172c18bc4565957fa7011
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 7410f1041ec9060240cd78d806617b55cd73c44e
Reviewed base: bc2e85891f27befe19236686e608f3d45db84d14
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: Fresh route/start-guard binding; immutable five-commit range and 37-path/hash audit; actual UI and test review; installed synthetic unit/type/build/PWA/browser checks on temporary 4174; static privacy/containment scan; and target smoke.
Verification context: This report covers only the bound immutable range. The temporary Playwright child used 4174 and exited; the preserved 4173 teaching preview remained PID 7749. No source repair, integration, preview lifecycle action, service/database access, private data, dependency acquisition, cursor, lock, or remote effect was taken.

## Findings

- HARD — BETA-UI containment is not acceptable at final bytes. The binding plan `docs/superpowers/plans/2026-07-22-evidence-ledger-unified-beta-ui.md@611cf62df4d8fcdd011ea106b231ed972c684231` requires raw user-facing copy to remain inside explicit technical disclosures and, where retained, immutable IDs in a collapsed technical-details section. At the reviewed head, `web/src/features/owner-settings/OwnerSettingsStatus.tsx:23` directly renders `active_policy_activation_id` as `활성 정책 <id>` and `:28` directly renders `draft_revision_id` as `초안 <id>`; neither is in a details disclosure. `web/src/features/owner-settings/OwnerSettingsHistory.tsx:19,29` likewise renders raw `policy_activation_id` in the visible heading and restore-button label. `OwnerSettingsPage.test.tsx:102-103` and `e2e/owner-settings.spec.ts:20` affirm that these IDs are primary visible UI. A raw revision/immutable ID can therefore escape technical disclosure, so the request's adversarial answer is yes and GO is prohibited. No repair was made.

## Finding Refs

- coordination/mailbox/sent/2026-07-22T17-03-46Z-director-to-all-coordination.md@dc6e0971ae3257c5143235cf319a839c3ae988be
- coordination/mailbox/sent/2026-07-22T16-56-32Z-coordinator-to-director-coordination.md@63c6b94dd867176a261a78384a836f733a075bbb
- coordination/mailbox/sent/2026-07-22T16-52-24Z-director-to-coordinator-coordination.md@d6632fcafa43303feceaeb439864077dff22c42d
- coordination/mailbox/sent/2026-07-22T16-53-37Z-director-to-coordinator-coordination.md@ff80e787f92bc84e44a8586518ce3ef2f24cd4f0
- coordination/mailbox/sent/2026-07-22T16-43-47Z-coordinator-to-director-coordination.md@4f98902a50d7ee5a54a735a6da6a76d11b68c43a
- coordination/mailbox/sent/2026-07-22T16-30-59Z-director-to-coordinator-coordination.md@cf31fe01398e16bfab0d68a4c7ba8ea5b66ecefd
- coordination/mailbox/sent/2026-07-22T15-06-28Z-coordinator-to-director-coordination.md@cc892efffcf2c02fd1acff194a11339cd6f1b888
- coordination/mailbox/sent/2026-07-22T15-01-38Z-director-to-coordinator-coordination.md@10f294987450bf200c191b152396bdec2057bdad
- coordination/mailbox/sent/2026-07-22T14-36-01Z-coordinator-to-director-coordination.md@08523fa0e8fb18419a687a7b5ad8ec6ae1430bc0
- coordination/mailbox/sent/2026-07-22T17-16-56Z-director-to-operator2-verify-request.md@0659ed21817f3875ba8d2985cb0cceafbb258cd0

## Finding Dispositions

- coordination/mailbox/sent/2026-07-22T17-03-46Z-director-to-all-coordination.md@dc6e0971ae3257c5143235cf319a839c3ae988be: unresolved-hard-boundary
- coordination/mailbox/sent/2026-07-22T16-56-32Z-coordinator-to-director-coordination.md@63c6b94dd867176a261a78384a836f733a075bbb: addressed
- coordination/mailbox/sent/2026-07-22T16-52-24Z-director-to-coordinator-coordination.md@d6632fcafa43303feceaeb439864077dff22c42d: addressed
- coordination/mailbox/sent/2026-07-22T16-53-37Z-director-to-coordinator-coordination.md@ff80e787f92bc84e44a8586518ce3ef2f24cd4f0: addressed
- coordination/mailbox/sent/2026-07-22T16-43-47Z-coordinator-to-director-coordination.md@4f98902a50d7ee5a54a735a6da6a76d11b68c43a: addressed
- coordination/mailbox/sent/2026-07-22T16-30-59Z-director-to-coordinator-coordination.md@cf31fe01398e16bfab0d68a4c7ba8ea5b66ecefd: addressed
- coordination/mailbox/sent/2026-07-22T15-06-28Z-coordinator-to-director-coordination.md@cc892efffcf2c02fd1acff194a11339cd6f1b888: addressed
- coordination/mailbox/sent/2026-07-22T15-01-38Z-director-to-coordinator-coordination.md@10f294987450bf200c191b152396bdec2057bdad: addressed
- coordination/mailbox/sent/2026-07-22T14-36-01Z-coordinator-to-director-coordination.md@08523fa0e8fb18419a687a7b5ad8ec6ae1430bc0: unresolved-hard-boundary
- coordination/mailbox/sent/2026-07-22T17-16-56Z-director-to-operator2-verify-request.md@0659ed21817f3875ba8d2985cb0cceafbb258cd0: addressed

## Evidence

$ compact_pair_loop.parse_verify_request at 2450ce134e994306e43172c18bc4565957fa7011; ledger_start_guard.py --seat operator2 --wave 2; route_lineage.py --root . --check
→ PASS: exact external repository/base/head, Director gpt-5.6-sol author, assigned Operator2 gpt-5.6-terra reviewer, active revision-3 root, and valid route lineage. The same-root fast-resume fallback was advisory only; full orientation was completed. No existing report binds this request.

$ immutable target identity and scope audit
→ PASS: exact head 7410f1041ec9060240cd78d806617b55cd73c44e, base bc2e85891f27befe19236686e608f3d45db84d14, tree c10eb800e64ff612d6067bc20e85159ee1346df7, five commits, silent diff check, 37 paths, manifest SHA-256 4921a849b685cde72752838ebb1c9052cf5cedd70e4d233ae561b52160329d2c, and patch SHA-256 69c912440bee138c0e3084ab4c97e15895cbbd78e6a1b5d26b907b18fab5555d. The target has no staged/tracked residue; only the authorized untracked node_modules donor remains. Normal main remains the exact base with only preserved untracked local items.

$ actual range and static containment review
→ FAIL: the owner status/history primary rendering exposes raw immutable IDs outside details as cited above. The selling evidence/history/recommendation raw values are otherwise held under closed technical disclosures; owner-entered history reason is likewise contained. Storage hits are limited to reviewed session auth and pending-journal recovery; no private or secret literal was found in production source.

$ 7e08cfb2 PWA byte and port-bound audit
→ PASS: exactly three LOOPBACK_ORIGIN-derived origin bindings at registration scope, script URL expectation, and CDP restart scope; exactly three pre-save 초안 저장 locators; exactly three post-release 초안 저장 disabled assertions after held-command release; no PWA skip/only/fixme/quarantine or hardcoded 4173 lifecycle dependency. 4174 was absent before and after each run; 4173 remained PID 7749.

$ npm test; npm run typecheck; npm run build:ci; EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test e2e/pwa.spec.ts; EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test; env VITE_SUPABASE_URL=http://127.0.0.1:54321 VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_synthetic_mac_loopback npm run build; target scripts/ci_smoke.py
→ PASS: 28 files / 304 tests; TypeScript; test build 106 modules and 9 distribution files; focused PWA 5/5; full synthetic Playwright 17/17; synthetic-public production build 106 modules and 9 distribution files; and target smoke OK. The first focused invocation preceding build:ci served pre-existing ignored loopback production dist and remained on the sign-in surface; rebuilding the required synthetic test artifact produced the valid 5/5 focused result, with no source change.

Cursor at send: 0
