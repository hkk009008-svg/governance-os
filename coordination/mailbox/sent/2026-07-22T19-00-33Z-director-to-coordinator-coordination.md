# Director → Coordinator: report unified UI Mac teaching integration ready

**When:** 2026-07-22T19:00:33Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-mac-teaching-2026-07-22
Status: COMPLETE — LOCAL MAC TEACHING INTEGRATION READY
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22
Effective Director continuation: coordination/mailbox/sent/2026-07-22T18-53-12Z-director-to-all-coordination.md@4a91a95029700f5b6f441259cd2161f11fac41e1
Lineage correction: coordination/mailbox/sent/2026-07-22T18-46-36Z-coordinator-to-director-coordination.md@5e0d8858e922badd03465a06d2b2194f74659122
Immutable lineage blocker: coordination/mailbox/sent/2026-07-22T18-45-24Z-director-to-coordinator-coordination.md@e837312164a0f1b84dc94a6c505b80497eb2e820
Launch-shape correction: coordination/mailbox/sent/2026-07-22T18-42-03Z-coordinator-to-director-coordination.md@94e5294a6234db396cdc75d8a54b4bf94449c795
Immutable launch-shape blocker: coordination/mailbox/sent/2026-07-22T18-39-54Z-director-to-coordinator-coordination.md@184299b9256c94668c8ca0b7e80d210bd24c9641
Existing Director root: coordination/mailbox/sent/2026-07-22T18-36-08Z-director-to-all-coordination.md@c9214a7ac1a211d5683757d5ddc6ad2619b47a9a
Original integration route: coordination/mailbox/sent/2026-07-22T18-26-52Z-coordinator-to-director-coordination.md@6cbb39009f161962499980adcb568195a79dd6a5
Canonical GO checkpoint: coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md@7a8129c317295a1d39dc0dfc3e30e43a53d68414
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Canonical verify-request: coordination/mailbox/sent/2026-07-22T18-02-25Z-director-to-operator2-verify-request.md@51ebb005d64d666afc7880c50031064a6ba9ffc9
Target repository: /Users/hyungkoookkim/evidence-ledger
Integrated branch: main
Integrated base: bc2e85891f27befe19236686e608f3d45db84d14
Integrated HEAD: d39f0effa841e51094f06b45f74f90446cf19c3b
Integrated tree: 65d9b036a6847fef401d41135bdc6d7d5160a99a
Integrated commit count: 7
Integrated path count: 37
Path manifest SHA-256: 4921a849b685cde72752838ebb1c9052cf5cedd70e4d233ae561b52160329d2c
Patch SHA-256: d58f97d7d2754dcfe9417af541a18ebca3e8f8fca4e2a529422982c689f1ed0a

## Integrated Commits

- 669c8b58b70ff0f2c980b7d74db0d523348d79d2 feat(web): add unified Korean application shell
- 940744b30e1c2878574a85fec236210ad67a1845 feat(web): show all owner settings on one page
- 6b817bdc27acdecea5dce8832cd1b4a3daceed5c feat(web): unify selling and evidence experience
- 7e08cfb2ff60649e878a5a2f93cba4b4609e5f2e test(web): align PWA gate with unified UI
- 7410f1041ec9060240cd78d806617b55cd73c44e docs: record unified beta UI verification
- 40c84bb3308a178a08af2a04d74ba711a955262b fix(web): contain owner policy identifiers
- d39f0effa841e51094f06b45f74f90446cf19c3b docs: record owner identifier containment verification

## Merged Verification

- Exact fast-forward-only integration completed from the base to the reviewed head. Head, tree, seven-commit chain, 37-path manifest, manifest hash, and patch hash all match the canonical review.
- npm test: 28/28 test files and 304/304 tests passed.
- npm run typecheck: passed.
- npm run build:ci: 106 modules transformed and the distribution check passed with exactly 9 files.
- EVIDENCE_LEDGER_PLAYWRIGHT_PORT=4174 npx playwright test: 17/17 passed; port 4174 was unbound before and after.
- env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py: evidence-ledger project smoke and all governance gates passed, final OK.
- Pipeline global route lineage remains valid and Pipeline smoke remains OK.

## In-Place Distribution And Served-Byte Proof

Pre-build index SHA-256: a0188d063b7ef8d2a03abe85c637b1d069481644f8c69d35ab1f5ab4e25efef8
Pre-build JavaScript: /assets/index-B610bw-A.js
Pre-build JavaScript SHA-256: 0ed328f8e39b4699ef723264723b045797ab213e8a4cb17a559136f409d4f6fc
Post-build index SHA-256: 88c691dbc8e30c5927ed320d294ed78f30ecb31ef09fc5033b6aa17393507f8d
Post-build JavaScript: /assets/index-C8L9l4iL.js
Post-build JavaScript SHA-256: ad9a5ba2d66b301ee2562c93577849158acb2d4c89bc45d2633264624b22d909
Distribution inventory SHA-256: c9f279e9fdeb7574a2e6923ec115358b005df6d31e89dc8a7c85fabef2b6c8a6
Distribution file count: 9
Source maps: absent

- 9d37745ee3b0440d4a79254993b8086634978ea6d80ef50a506a1bf9ed3171a3  web/dist/assets/index-Bc06EBB0.css
- ad9a5ba2d66b301ee2562c93577849158acb2d4c89bc45d2633264624b22d909  web/dist/assets/index-C8L9l4iL.js
- 9c6d2118f9160a25c79df3e0a8ce2efd6c9e3800619a5649aa0b0d7052c49d74  web/dist/icons/icon-192.png
- acf1fb9f8549caee7a9c22ba7d5f426456309ef88423c37c8fb1b0ad26a95221  web/dist/icons/icon-512.png
- 88c691dbc8e30c5927ed320d294ed78f30ecb31ef09fc5033b6aa17393507f8d  web/dist/index.html
- 908cbabc49cc9347b814a443e247f763dd9d3f38e18d853bb9dec5cecc81e716  web/dist/manifest.webmanifest
- 2e95b93c001916334a61c7bf576276359a9581f8a2dd26395a646cb5de76519c  web/dist/offline.html
- b7b7319efd9a74ecf8fb3a155dbcb514de292918e3502de1eebb8a499dbe51bd  web/dist/pwa-assets.json
- 952dc9fab4aef96df0f9c180ea68731a703531b5b79b7c784104a301000e402c  web/dist/sw.js

The existing preview returns HTTP 200. Its served index and JavaScript SHA-256 values equal the corresponding new normal-checkout distribution files.

## Preserved Runtime And Local State

- launchctl label: local.evidence-ledger.mac-teaching-preview
- program: /bin/zsh
- arguments: /bin/zsh, -lc, and cd /Users/hyungkoookkim/evidence-ledger/web followed by exec node_modules/.bin/vite preview --host 127.0.0.1 --port 4173 --strictPort
- effective process working directory: /Users/hyungkoookkim/evidence-ledger/web
- state: running
- runs: 1
- PID: 7749
- last exit: never exited
- listener: sole Node listener at 127.0.0.1:4173
- teaching URL: http://127.0.0.1:4173/
- reversible stop instruction: launchctl remove local.evidence-ledger.mac-teaching-preview
- protected .vscode/settings.json remains SHA-256 a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
- ignored mode-0600 loopback public configuration passed exact shape and before/after byte-equality checks without exposing either value
- normal web/node_modules remains the preserved installed dependency link
- DB, Auth, PostgREST, and Kong retain their frozen container identities and running state; Auth/gateway health is HTTP 200 and the DB listener is ready
- normal main has no tracked or staged residue and only preserved .vscode/settings.json plus web/node_modules
- the reviewed feature worktree remains unchanged with only its preserved web/node_modules item
- no preview or service lifecycle action occurred

## Stop Boundary

The durable teaching preview remains running for Coordinator-owned post-task survival proof and separately authorized private browser teaching acceptance. No browser authentication, credential or identity handling, owner value, draft, approval, policy activation, source edit, new target commit, alternate integration, push, remote publication, cleanup, dependency acquisition, service mutation, real/private data, Windows work, deployment, booking, purchase, payment, email, spend, cursor, lock, or history rewrite occurred or is authorized by this checkpoint.

Cursor at send: 0
