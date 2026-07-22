# Director → Coordinator: report Mac production dist corrected

**When:** 2026-07-22T19:20:06Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-mac-production-dist-2026-07-22
Status: COMPLETE — PRODUCTION DIST CORRECTED; COORDINATOR BROWSER ACCEPTANCE HELD
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22 plus user-task:approved-proceed-2026-07-22
Effective Director root: coordination/mailbox/sent/2026-07-22T19-13-32Z-director-to-all-coordination.md@faff02f101c22b290dbaaa78fa0c26419592bc06
Coordinator route: coordination/mailbox/sent/2026-07-22T19-08-07Z-coordinator-to-director-coordination.md@338b4cd44aef943a6421a90db58391f554feadba
Invalid prior checkpoint: coordination/mailbox/sent/2026-07-22T19-00-33Z-director-to-coordinator-coordination.md@aa3f48a7860e1ab7ab39aca6a55f264968cf8fa6
Prior Director continuation: coordination/mailbox/sent/2026-07-22T18-53-12Z-director-to-all-coordination.md@4a91a95029700f5b6f441259cd2161f11fac41e1
Canonical source GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Binding finding: MAC-BETA-PRODUCTION-MODE-001
Finding disposition: CORRECTED — ignored distribution regenerated in production mode; reviewed source unchanged
Target repository: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target HEAD: d39f0effa841e51094f06b45f74f90446cf19c3b
Target tree: 65d9b036a6847fef401d41135bdc6d7d5160a99a

## Authorized Build Result

- Exact token command npm run build was executed once from /Users/hyungkoookkim/evidence-ledger/web.
- Typecheck passed.
- Vite production build passed with 106 modules transformed.
- Production-mode distribution check passed with exactly 9 files.
- No alternate build, retry, dependency acquisition, source edit, target commit, preview lifecycle, or service lifecycle action occurred.
- Target project smoke passed with final OK.
- Pipeline global route lineage remains valid and Pipeline smoke remains OK.

## Production Distribution Evidence

Pre-build index SHA-256: 88c691dbc8e30c5927ed320d294ed78f30ecb31ef09fc5033b6aa17393507f8d
Pre-build JavaScript: /assets/index-C8L9l4iL.js
Pre-build JavaScript SHA-256: ad9a5ba2d66b301ee2562c93577849158acb2d4c89bc45d2633264624b22d909
Pre-build distribution inventory SHA-256: c9f279e9fdeb7574a2e6923ec115358b005df6d31e89dc8a7c85fabef2b6c8a6
Post-build index SHA-256: dc27b39634e4df54a922ea33dd2e326f2b7213773cccb76794a7c358d5a65311
Post-build JavaScript: /assets/index-C9iIOTKO.js
Post-build JavaScript SHA-256: 24acf949c398b9b052334cb2c02405ca86604ea23c6a94932ed5aae58e51292d
Post-build distribution inventory SHA-256: ca359086c70c2ea75ebebe43bd29c6da554f95aa735f7572af3ccc4ea9d5e316
Distribution file count: 9
Source maps: absent

- 9d37745ee3b0440d4a79254993b8086634978ea6d80ef50a506a1bf9ed3171a3  web/dist/assets/index-Bc06EBB0.css
- 24acf949c398b9b052334cb2c02405ca86604ea23c6a94932ed5aae58e51292d  web/dist/assets/index-C9iIOTKO.js
- 9c6d2118f9160a25c79df3e0a8ce2efd6c9e3800619a5649aa0b0d7052c49d74  web/dist/icons/icon-192.png
- acf1fb9f8549caee7a9c22ba7d5f426456309ef88423c37c8fb1b0ad26a95221  web/dist/icons/icon-512.png
- dc27b39634e4df54a922ea33dd2e326f2b7213773cccb76794a7c358d5a65311  web/dist/index.html
- 908cbabc49cc9347b814a443e247f763dd9d3f38e18d853bb9dec5cecc81e716  web/dist/manifest.webmanifest
- 2e95b93c001916334a61c7bf576276359a9581f8a2dd26395a646cb5de76519c  web/dist/offline.html
- c52d413461b404885af01f9835e2bd7dbfb30441e697ef72a6a748e5277f6696  web/dist/pwa-assets.json
- a6f1418cea9cc8aa7f3c914d68db760ca35c1894791e644341d851be06b08510  web/dist/sw.js

The generated JavaScript no longer contains the synthetic Supabase origin and does contain the accepted exact loopback runtime origin. No publishable key or configuration value is included in this event.

## Served-Byte And Process Proof

- Supported host-loopback checks returned HTTP 200.
- Served index SHA-256 equals the post-build local index SHA-256.
- Served JavaScript SHA-256 equals the post-build local JavaScript SHA-256.
- launchctl label: local.evidence-ledger.mac-teaching-preview
- program: /bin/zsh
- arguments: /bin/zsh, -lc, and cd /Users/hyungkoookkim/evidence-ledger/web followed by exec node_modules/.bin/vite preview --host 127.0.0.1 --port 4173 --strictPort
- effective working directory: /Users/hyungkoookkim/evidence-ledger/web
- state: running
- runs: 1
- PID: 7749
- last exit: never exited
- listener: sole Node listener at 127.0.0.1:4173
- port 4174: unbound
- teaching URL: http://127.0.0.1:4173/
- reversible stop instruction: launchctl remove local.evidence-ledger.mac-teaching-preview

## Preserved State

- Target HEAD/tree and all tracked/index bytes remain unchanged.
- Target status remains only the preserved untracked .vscode/settings.json and web/node_modules.
- Ignored web/.env.local remains mode 0600, byte-identical at SHA-256 48ee0e47fb1c21be8059d51713b4c64c39ca54a364619c0161164fce7f43b0bf, and passes the exact two-key loopback public-config shape without exposing values.
- Protected .vscode/settings.json remains SHA-256 a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4.
- The ignored installed dependency link remains unchanged.
- Frozen DB, Auth, PostgREST, and Kong identities and readiness remain unchanged; gateway-routed Auth and PostgREST checks returned HTTP 200.
- No credential, identity, key, token, owner value, private response, or environment value was requested, printed, persisted, or recorded.

## Stop Boundary

The corrected durable teaching preview remains running for Coordinator-owned private browser acceptance. No browser authentication, source/test edit, target commit, dependency acquisition, preview or service lifecycle action, draft, review, approval, activation, push, remote publication, cleanup, Windows work, deployment, real/private data, booking, purchase, payment, email, spend, cursor, lock, or history rewrite occurred or is authorized by this checkpoint.

Cursor at send: 0
