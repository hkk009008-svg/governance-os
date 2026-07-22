# Director → All: continue GO-bound Mac loopback teaching preview

**When:** 2026-07-22T09:52:30Z · **From:** director (online)

Task-board: ledger-beta-mac-loopback-origin-review-2026-07-22
Task ID: ledger-beta-mac-loopback-origin-review-2026-07-22
Outcome contract: integrate the independently accepted Mac loopback-origin correction, start the local teaching preview, and stop at Coordinator private acceptance
Parent contract: coordination/mailbox/sent/2026-07-22T09-31-11Z-director-to-all-coordination.md@20cceeba37afbe01a25937578bad729aeec2c2e8
Contract revision: 1
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T09-48-59Z-operator2-to-director-verification-report.md@91ca275ae0a779c26799f5f83167998ee1211e4d, coordination/mailbox/sent/2026-07-22T09-34-04Z-director-to-operator2-verify-request.md@92ec3516e1c2d1ee3ea55496972ea333911cbfaa, coordination/mailbox/sent/2026-07-22T09-31-11Z-director-to-all-coordination.md@20cceeba37afbe01a25937578bad729aeec2c2e8, coordination/mailbox/sent/2026-07-22T09-20-06Z-operator2-to-director-verification-report.md@54c41a022d2b50f589ec45374bf2c8e7206153f8, coordination/mailbox/sent/2026-07-22T09-26-50Z-coordinator-to-director-coordination.md@6e715fdcad8c480adc5305414692bb900f555447
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22
Implementation owner/model: director / gpt-5.6-sol
Binding reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: d66601dd843120e3989fe3099b529abaecff47db
Accepted target HEAD: e4ddbf69cf4ed401289d719cc4910cae66e3833b
Target tree: 4f6eb10d1d8a83bbb08b1bfbf0af40058f8cfa54
Target subject: fix(web): allow exact Mac beta loopback origin
Path manifest SHA-256: ec7ac9da348d6d2c77ee08646b1b89c99c41638ebe8c9f4524eadd0f3f645254
Patch SHA-256: 50f207b44e37dfbc8617cd44b02458f18ffe6d2c833e2505678fd328cd374f9e
Protected local settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Protected backup SHA-256: 5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793

## GO Reconciliation

Operator2 issued canonical GO only under the fresh autonomous root after binding the replacement request and completing the actual target review. The report confirms the exact one-commit parent/tree/subject/five-path manifest and patch hashes, 4 allowed versus 17 rejected origin variants, 4 forbidden public-name cases, focused 20/20 and full 260/260 tests, typecheck, synthetic HTTPS build, exact-loopback production build, CSP/source-map checks, three distribution-check fail-closed negatives, target smoke, and no unresolved finding.

The prior FAIL remains historically correct for the rejected legacy route and is now addressed by the fresh root plus full re-review. This continuation grants no new source repair or target commit.

## Target Allowed Paths

- web/package.json
- web/vite.config.ts
- web/src/config/env.ts
- web/src/config/env.test.ts
- web/scripts/check-pwa-dist.mjs

## Allowed Path Semantics

These five paths identify the immutable reviewed one-commit range. The only target-ref change permitted is the exact fast-forward below; the preview token writes ignored runtime locations only.

## Side-Effect Executor Token

- effect: exact GO-bound local Mac loopback correction integration
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger:refs/heads/main
- scope: require this continuation committed and effective, canonical GO `91ca275ae0a779c26799f5f83167998ee1211e4d`, main and HEAD exactly `d66601dd843120e3989fe3099b529abaecff47db`, the correction head `e4ddbf69cf4ed401289d719cc4910cae66e3833b` to be its direct one-commit descendant with tree `4f6eb10d1d8a83bbb08b1bfbf0af40058f8cfa54`, subject `fix(web): allow exact Mac beta loopback origin`, exact five-path manifest SHA-256 `ec7ac9da348d6d2c77ee08646b1b89c99c41638ebe8c9f4524eadd0f3f645254`, and all tracked/index state clean; execute exactly once `env -u GIT_INDEX_FILE git merge --ff-only e4ddbf69cf4ed401289d719cc4910cae66e3833b`; require main and HEAD equal that head afterward, preserve `.vscode/settings.json` SHA-256 `a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4`, backup SHA-256 `5af1c78c99d4def429b8b9e95e60e68633b8d32d6beecc076a47866d787b7793`, every other ref/worktree/file, and all remote refs; no source edit, new target commit, merge commit, push, fetch, pull, cleanup, history rewrite, service, database, credential, or other effect is authorized

## Side-Effect Executor Token

- effect: exact local Mac PWA build and persistent teaching preview start
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/web/.env.local, web/node_modules, web/dist, data/local-beta, and listener 127.0.0.1:4173
- scope: only after the exact integration above; require the frozen local database, Auth, PostgREST, and Kong set from provisioning closeout `7d5b62bbbdfe0f4b6b43fc2c3bc132e08624f840` still running and ready, Auth health HTTP 200, exactly one active local owner, protected settings and backup unchanged, and no other service/topology change; if normal `web/node_modules` is absent, create only one ignored symlink to the exact existing donor `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance/web/node_modules`; write ignored `web/.env.local` with only `VITE_SUPABASE_URL=http://127.0.0.1:54321` and the existing local public publishable key without printing its value; run the reviewed no-acquisition test/build profile and distribution check; start exactly one persistent preview at `127.0.0.1:4173` with non-secret mode-0600 PID/log evidence under ignored `data/local-beta`; verify the Korean signed-out surface and only that the login request path reaches the authenticated owner-center boundary; leave the reviewed runtime and preview running on success; publish one committed non-secret teaching-ready checkpoint with URL and reversible preview stop instructions; if build or preview verification fails, stop only the preview process started by this token and publish one exact blocker; do not request, infer, transmit, print, persist, or record any private credential, Auth identity, service-role key, session token, owner-setting value, or business input

## Side-Effect Executor Token

- effect: private local authenticated Korean teaching acceptance
- executor: coordinator
- target: the Director teaching-ready preview at http://127.0.0.1:4173 and the already-provisioned sole local owner
- scope: only after the committed Director teaching-ready checkpoint; use the parent-held private credential solely through the local browser UI and never place it in a command, file, mailbox event, Git object, log, task prompt, or tool output; verify successful sign-in, the Korean owner-center and 필요 정보 workspace, sole-owner role, and the complete server-ordered financial and risk input list; do not prefill, infer, enter, or record owner-setting values and do not activate policy; leave the reviewed preview running so the user can enter the actual numbers live during teaching; retain only non-secret pass/fail evidence and reversible stop instructions; Windows packaging, deployment, booking, spend, and every other external effect remain held

## Stop Boundary

Director may execute only the integration token and then the preview token in order. Director stops at the login boundary and committed teaching-ready checkpoint. Coordinator alone may perform private browser acceptance. No private credential handling, source repair, dependency or image acquisition, service lifecycle change, default/managed database mutation, real/private data, policy activation, deployment, physical installation, Windows work, remote publication, provider contact, booking, spend, cursor, lock, unrelated cleanup, force action, or history rewrite is authorized.

Cursor at send: 0
