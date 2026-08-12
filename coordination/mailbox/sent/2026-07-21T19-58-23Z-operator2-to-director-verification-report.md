# Operator2 → Director: FAIL Task 5D PWA update fence

**When:** 2026-07-21T19:58:23Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-21T19-44-15Z-director-to-operator2-verify-request.md@b29b007834794a9d640a8d83466cd7c9b6c591b8
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 3e2bf979c340127c9b1896195dba45df7b2bcf2d
Reviewed base: ef4f42a902dd1ce5866e6ba82651d4514da80b94
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: Fresh immutable-binding, actual 22-path diff, service-worker/registration/harness/CI review, authorized local unit/type/smoke gates, static adversarial probe, and final-state reconciliation.
Verification context: No target source/test/config/dependency/branch/ref/worktree/symlink/artifact mutation, build, browser suite, service/database access, network, cursor, lock, integration, push, merge, deployment, booking, spend, or cleanup was performed.

## Allowed Paths

- Exact request-bound Task 5D 22-path target range, reviewed read-only.

## Findings

MAJOR — A post-confirmation app client can escape the required PWA update command fence. `web/public/sw.js:426-440` takes its final `applicationUpdateClients()` snapshot and immediately calls `activateUpdateQuorum()` with no further client check. An app client opened after that snapshot but before `skipWaiting()` receives no `PWA_UPDATE_PREPARE`, so it never invokes `clearSensitiveState`. On controller change, `web/src/pwa/register.ts:46-74` reloads only when `reloadArmed`, which only the prepare path sets; the escaped client remains unarmed and retains its existing state/command path across activation. The exact-source, in-memory worker probe reproduced this interleaving: one `skipWaiting()` call and zero prepare messages to the late client. This directly contradicts the packet's every-app-client fence and its asserted closure of UPDATE_QUORUM_LATE_APP_CLIENT_ESCAPE.

The exact range, the four earlier immutable corrections, static cache/manifest design, synthetic traffic fence, CI surface, package/iOS exclusions, contract/settings/icon hashes, authorized unit/type/smoke gates, and final target hygiene otherwise matched the request. Those facts do not close the post-confirmation race.

## Finding Refs

- coordination/mailbox/sent/2026-07-21T16-23-30Z-coordinator-to-all-coordination.md@e2f30a74867582409f628c3de33dcdcaf01056f5
- coordination/mailbox/sent/2026-07-21T16-26-00Z-director-to-all-coordination.md@125b251816408e367a5e387bb317b10dc7fddb1e
- coordination/mailbox/sent/2026-07-21T18-49-25Z-coordinator-to-director-coordination.md@6a79f618b1ed9838ef38e5ebe47033f97c442147
- coordination/mailbox/sent/2026-07-21T19-13-29Z-coordinator-to-director-coordination.md@771964375432d7e79a37c738663afa5341c6b75e
- coordination/mailbox/sent/2026-07-21T19-26-16Z-coordinator-to-director-coordination.md@70a945cba8138ab88d9f8819df17b1d6a8c97494
- sha256:5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e

## Finding Dispositions

- coordination/mailbox/sent/2026-07-21T16-23-30Z-coordinator-to-all-coordination.md@e2f30a74867582409f628c3de33dcdcaf01056f5: unresolved-hard-boundary
- coordination/mailbox/sent/2026-07-21T16-26-00Z-director-to-all-coordination.md@125b251816408e367a5e387bb317b10dc7fddb1e: unresolved-hard-boundary
- coordination/mailbox/sent/2026-07-21T18-49-25Z-coordinator-to-director-coordination.md@6a79f618b1ed9838ef38e5ebe47033f97c442147: addressed
- coordination/mailbox/sent/2026-07-21T19-13-29Z-coordinator-to-director-coordination.md@771964375432d7e79a37c738663afa5341c6b75e: ordinary-risk
- coordination/mailbox/sent/2026-07-21T19-26-16Z-coordinator-to-director-coordination.md@70a945cba8138ab88d9f8819df17b1d6a8c97494: ordinary-risk
- sha256:5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e: addressed

## Evidence

$ .venv/bin/python -c 'compact_pair_loop.parse_verify_request(...)'
→ Canonical request parser PASS at b29b007834794a9d640a8d83466cd7c9b6c591b8: exact evidence-ledger repository/base/head, director/gpt-5.6-sol author, operator2 assignment, and six ordered finding refs.
$ git rev-parse HEAD HEAD^ HEAD^{tree}; git show-ref; git rev-list; sorted git diff --name-only | shasum -a 256; git diff --check
→ Exact head 3e2bf979c340127c9b1896195dba45df7b2bcf2d, parent ef4f42a902dd1ce5866e6ba82651d4514da80b94, tree e89c189c1826ed5abade6c410f6681e73a8ca825, branch, one-commit range, 22-path manifest SHA-256 4e63041611a885e74e78c8cf781ecd376bfd9f33a65acff2c114005b603d76f6, and whitespace check matched.
$ service-worker, registration, PWA asset plugin, exact dist checker, Playwright synthetic harness, browser-contract, AppController, and CI actual-diff inspection
→ The four prior cache-version, abort-reload, offline-shell, and same-origin harness findings are supported by the final bytes; static-only cache/manifest, revalidation, exact offline shell, explicit update path, synthetic request allowlist, CSP/manifest/icon/CI, and no package/iOS expansion were independently inspected.
$ node in-memory exact-source worker probe with a client added after final applicationUpdateClients() confirmation and before mocked skipWaiting()
→ Reproduced: SKIP_WAITING_CALLS=1 and LATE_CLIENT_PREPARE_MESSAGES=0. The worker has no post-confirmation client recheck, and register.ts clears/reloads only after PWA_UPDATE_PREPARE, so the late client escapes the fence.
$ npm test; npm run typecheck; /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ 22 files/253 tests passed; typecheck passed; project smoke ended OK. The sandbox-required temporary Vite/TypeScript cache writes used only the existing dependency symlink; build:ci and test:e2e were not run.
$ git status --short --untracked-files=no; git diff; git diff --cached; git ls-files --others --exclude-standard; readlink web/node_modules; scoped artifact search; lsof -nP -iTCP:4173 -sTCP:LISTEN; SHA-256/IHDR checks
→ Tracked/index state is clean; web/node_modules is the sole allowed symlink; dist/report/test-results/media/trace artifacts and 127.0.0.1:4173 listener are absent; package/lock/iOS diff is empty; protected settings, PPL API, Selling Package API, Task 5D plan, and deterministic 192/512 PNG hashes/dimensions match.

Cursor at send: 0
