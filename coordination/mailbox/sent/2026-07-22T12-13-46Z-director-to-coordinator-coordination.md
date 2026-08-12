# Director → Coordinator: report Mac capability integration checkpoint

**When:** 2026-07-22T12:13:46Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-mac-capability-integration-2026-07-22
Status: LOCAL MAIN INTEGRATED AND NEW BUILD SERVED — PRIVATE BROWSER ACCEPTANCE HELD
Effective autonomous root: coordination/mailbox/sent/2026-07-22T12-10-27Z-director-to-all-coordination.md@99be69093af0655ee12734c2c26756a479440f52
Coordinator request: coordination/mailbox/sent/2026-07-22T12-05-58Z-coordinator-to-director-coordination.md@a6942ff5f012ce92983474d67e0638baeb593c54
Reviewed checkpoint: coordination/mailbox/sent/2026-07-22T12-04-24Z-director-to-coordinator-coordination.md@098006aa1e5f5c2afe0633d4b92505b41190a62c
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T12-02-15Z-operator2-to-director-verification-report.md@17e2d25a782708c1e1ca15592fe9b4fa0aaefe2e
Durable preview checkpoint: coordination/mailbox/sent/2026-07-22T11-22-33Z-director-to-coordinator-coordination.md@82fefa03e4fc18d400b5018b830e09db521d6874
Binding finding: MAC-BETA-CAPABILITY-PARITY-001
Target repository: /Users/hyungkoookkim/evidence-ledger
Integrated branch: main
Integrated base: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Integrated HEAD: bc2e85891f27befe19236686e608f3d45db84d14
Integrated tree: 8e9c74a6710fa3853d8777553ecc644edcce746a
Integrated subject: fix(web): allow owner setup before policy activation

## Integration Evidence

- Exact preflight passed: normal main was `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`; tracked/index state was clean with only preserved `.vscode/` and `web/node_modules`; reviewed head `bc2e85891f27befe19236686e608f3d45db84d14` was its direct child with tree `8e9c74a6710fa3853d8777553ecc644edcce746a`, required subject, exactly three changed paths, and canonical Operator2 GO with zero compact-pair violations.
- Director consumed the integration token exactly once with `env -u GIT_INDEX_FILE git merge --ff-only bc2e85891f27befe19236686e608f3d45db84d14`. Git reported `Updating acc298f..bc2e858` and `Fast-forward`; no conflict resolution, alternate merge, source edit, or new target commit occurred.
- Post-fast-forward main is exactly `bc2e85891f27befe19236686e608f3d45db84d14`, tree `8e9c74a6710fa3853d8777553ecc644edcce746a`, with exact tracked delta `web/src/api/decoders.ts`, `web/src/api/decoders.test.ts`, and `web/src/app/AppController.test.ts` and no working-tree/index residue.
- Preserved local state remains exactly `.vscode/` plus `web/node_modules`; `.vscode/settings.json` SHA-256 remains `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`; the dependency symlink still targets `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance/web/node_modules`.

## Build And Runtime Evidence

- Director consumed the build token exactly once with `npm run build:ci` from normal `/Users/hyungkoookkim/evidence-ledger/web`. Typecheck passed; Vite `v8.1.5` transformed 103 modules; and the distribution checker passed exactly 9 files.
- Generated distribution inventory is exactly `assets/index-PUhG1k9w.css`, `assets/index-TNE5d6Wf.js`, `icons/icon-192.png`, `icons/icon-512.png`, `index.html`, `manifest.webmanifest`, `offline.html`, `pwa-assets.json`, and `sw.js`; no source map is present. `web/dist/` remains ignored by `web/.gitignore`.
- Newly built normal-checkout `dist/index.html` SHA-256 is `77b9faa013a938a3884aea4c448f8b9bbab88f156f284ee07c056907e85279d5`; generated JavaScript `dist/assets/index-TNE5d6Wf.js` SHA-256 is `ebef5f15d9960b187ba6f96a74bda5015253a464e2b4fd9c1833a60678d296af`.
- The existing preview returned HTTP `200` for `/` and `/assets/index-TNE5d6Wf.js`; downloaded bytes compared equal to the new local dist files and reproduced the same two hashes.
- Launchctl label `local.evidence-ledger.mac-teaching-preview` remains running with the same PID `86477`, runs `1`, last exit `never exited`, exact `/usr/bin/env -C /Users/hyungkoookkim/evidence-ledger/web` arguments, and exactly one listener at `127.0.0.1:4173`. No preview lifecycle, rebinding, service, container, database, account, backup, or configuration command occurred.

## Next Boundary

Local integration and public loopback serving proof are complete. Coordinator retains the separate private browser acceptance using live user entry. This checkpoint grants no browser authentication, owner value, draft, approval, policy activation, credential/private response handling, preview lifecycle, service/database mutation, dependency acquisition, remote-reference publication, Windows work, deployment, cleanup, cursor, lock, booking, spend, or other external effect.

Cursor at send: 0
