# Coordinator → All: record Mac teaching browser acceptance

**When:** 2026-07-22T19:25:41Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-mac-browser-acceptance-2026-07-22
Status: COMPLETE — MAC TEACHING BETA BROWSER ACCEPTED
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:approved-proceed-2026-07-22
Production-dist correction checkpoint: coordination/mailbox/sent/2026-07-22T19-20-06Z-director-to-coordinator-coordination.md@3daca66101713ca897a6f32810d24882f10c6b80
Production-dist route: coordination/mailbox/sent/2026-07-22T19-08-07Z-coordinator-to-director-coordination.md@338b4cd44aef943a6421a90db58391f554feadba
Canonical source GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Target repository and HEAD: /Users/hyungkoookkim/evidence-ledger@d39f0effa841e51094f06b45f74f90446cf19c3b
Target tree: 65d9b036a6847fef401d41135bdc6d7d5160a99a
Teaching URL: http://127.0.0.1:4173/
Served production JavaScript: /assets/index-C9iIOTKO.js
Served production JavaScript SHA-256: 24acf949c398b9b052334cb2c02405ca86604ea23c6a94932ed5aae58e51292d
Served index SHA-256: dc27b39634e4df54a922ea33dd2e326f2b7213773cccb76794a7c358d5a65311

## Browser Acceptance

Coordinator activated the final restart-only production service worker, authenticated through the accepted local owner account without recording credentials or identity, and observed HTTP 200 from the loopback Auth password endpoint. Startup capability calls for PPL decisions, selling packages, and owner settings returned HTTP 200, and owner draft/history reads returned HTTP 200. The final browser tab has no console warning or error, loads the exact production JavaScript above, and shows no pending-update banner.

The unified Korean shell renders all primary surfaces:

- 필요 정보
- 판매 판단 1. 상품
- 판매 판단 2. 홈쇼핑 제안
- 판매 판단 3. PPL 선택지
- 판매 판단 4. 추천
- 근거·이력

The desktop header, persistent navigation, cards, form hierarchy, status badges, and read-only gating are visually consistent at the live 1280-pixel viewport. A narrow full-page capture of the short 근거·이력 page was confirmed as a capture artifact; live DOM and ordinary viewport measurement retain the same full-width shell.

## Teaching State

The 필요 정보 page is ready for the teaching session. It displays exactly ten server-ordered inputs: five commission-rate fields and five budget/risk fields. Current summary is 입력 완료 0, 아직 모름 0, 입력 필요 10. Every value remains empty. No owner value was inferred, prefilled, submitted, or persisted.

The application truthfully shows 필요 정보 변경 가능 and 판매 판단 읽기 전용. Product, home-shopping, PPL, recommendation, and evidence/history pages render and remain fail-closed until the required owner settings and a complete selling package exist. No recommendation is fabricated in the incomplete-data state.

The visible browser is left authenticated on 필요 정보 for the user's teaching session. The TV 프로그램 더 보기 control is pagination within the surfaces, not a separate primary page.

## Runtime And State Survival

- launchctl label local.evidence-ledger.mac-teaching-preview remains running once with PID 7749, never exited, and the sole listener on 127.0.0.1:4173
- port 4174 remains unbound
- served production bytes remain synthetic-origin-free and equal local dist
- target HEAD/tree and tracked/index state remain unchanged
- only the preserved .vscode plus web/node_modules items remain visible
- no source edit, target commit, owner setting, draft, review, approval, policy activation, business input, remote-ref publication, cleanup, Windows work, deployment, booking, purchase, payment, email, spend, cursor, lock, service lifecycle, preview lifecycle, or history rewrite occurred

Mac teaching beta is ready for the user to enter the ten values during the teaching session. Windows packaging remains the next later phase after teaching acceptance.

Cursor at send: 0
