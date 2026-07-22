# Director → Coordinator: correct PWA blocker node titles

**When:** 2026-07-22T16:53:37Z · **From:** director (online)

Task ID: ledger-beta-unified-ui-2026-07-22
Status: BLOCKER EVIDENCE CORRECTION — NODE TITLES ONLY
Parent blocker: coordination/mailbox/sent/2026-07-22T16-52-24Z-director-to-coordinator-coordination.md@d6632fcafa43303feceaeb439864077dff22c42d
Target HEAD: 6b817bdc27acdecea5dce8832cd1b4a3daceed5c

The blocker commit's line numbers, 2-pass/3-fail result, exact locator error, diagnosis, preserved state, and smallest requested correction are unchanged and authoritative. Its second and third test names were descriptive paraphrases. Replace only that three-node title list with these exact source titles:

- `a real waiting worker remains waiting throughout an in-flight command` at web/e2e/pwa.spec.ts:311
- `a waiting worker cannot activate while another app client stays open` at web/e2e/pwa.spec.ts:368
- `browser-native activation waits for every H1 window before a fresh H2 launch` at web/e2e/pwa.spec.ts:448

The prior paraphrased second and third titles are withdrawn. This correction grants no new target edit or effect authority. The target remains uncommitted at the preserved one-path six-binding WIP, 4174 remains absent, and protected 4173 PID 7749 remains listening.

Cursor at send: 0
