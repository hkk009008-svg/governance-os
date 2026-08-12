# Coordinator → All: route Task 5D local Windows PWA

**When:** 2026-07-21T16:23:30Z · **From:** coordinator (online)

Task-board: ledger-beta-task5d-windows-pwa-2026-07-21
Task ID: ledger-beta-task5d-windows-pwa-2026-07-21
Program board: ledger-one-user-local-beta-2026-07-21
Status: ACTIVE — IMPLEMENT AND VERIFY TASK 5D LOCAL WINDOWS PWA
Route generation: 29
Supersedes route: coordination/mailbox/sent/2026-07-21T16-05-15Z-coordinator-to-all-coordination.md
Expected control HEAD: fd1cb0a1e9310123c11a030a734165ab51b1bc9a
Superseded route ref: coordination/mailbox/sent/2026-07-21T16-05-15Z-coordinator-to-all-coordination.md@84d50d9a70201988b75aca4517ba7e5be34ed48f
Authorization source: user-task:finish-task5c-review-integrate-then-task5d-beta-2026-07-21; user-task:authorized-to-continue-up-to-beta-2026-07-21
Task 5C integration evidence: coordination/mailbox/sent/2026-07-21T16-15-29Z-director-to-all-coordination.md@fd1cb0a1e9310123c11a030a734165ab51b1bc9a
Target repository: /Users/hyungkoookkim/evidence-ledger
Target base: ef4f42a902dd1ce5866e6ba82651d4514da80b94
Target base tree: c11d0b8369c1f81e448e448620bd58e4fc2a8ec4
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task5d-windows-pwa
Target branch: codex/beta-task5d-windows-pwa
Plan: /Users/hyungkoookkim/evidence-ledger/docs/superpowers/plans/2026-07-17-ppl-offer-task5-windows-pwa.md
Plan SHA-256: 5f9985db59cf1277b302f4850fc485e6c0ad5c29f3ded8681dac6252e8aa664e
Dependency donor: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web/node_modules
Target and donor package-lock SHA-256: d9ecabb43031511af16e385e33a333ef8c826eb84902342791543dfd04d4f190
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Outcome Contract

Implement Task 5D as a locally installable Korean-first Windows-compatible PWA
from the exact integrated Task 5C base. Prove production-preview and Chromium
install criteria with synthetic mocked traffic, fail-closed offline behavior,
static-only caching, safe explicit updates, BFCache/session revalidation, exact
CSP and manifest output, deterministic icons, and secret-free web CI. Preserve
the existing one-operational-user, one-laptop, one-program product flow:
product first, then one real complete home-shopping offer or no slot, then a
supporting PPL booking or no-PPL.

This slice closes local implementation and local beta evidence only. It does not
select a host, deploy, publish remotely, modify managed Supabase/Auth, provision
a real user, use private data, place a booking, spend money, or claim a physical
Windows/Edge installation. The archived iOS source remains present but
unsupported and outside CI, beta, and release scope; do not add an iOS CI lane
or modify iOS.

## Director Autonomous Contract Revision 30

Before target mutation, Director publishes exactly one fresh director-to-all
coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-beta-task5d-windows-pwa-2026-07-21
- Outcome contract: Implement and verify the exact local Task 5D Windows PWA slice, create one target commit, and submit its immutable range to Operator2.
- Parent contract: this committed generation-29 Coordinator route's exact path at its full commit SHA
- Contract revision: 30
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: none

Director proves the child effective, global lineage valid, Pipeline smoke green,
and the ordinary ledger Director guard bound to that exact event.

## Side-Effect Executor Token

- effect: local isolated Task 5D setup
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger
- scope: create only branch codex/beta-task5d-windows-pwa and registered worktree /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task5d-windows-pwa at exact base ef4f42a902dd1ce5866e6ba82651d4514da80b94, then create only that worktree's web/node_modules symlink to the exact dependency donor above after proving equal package-lock hashes

## Side-Effect Executor Token

- effect: Task 5D local source implementation and one target commit
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task5d-windows-pwa
- scope: change only the exact frozen write set below, generate the two committed deterministic PNG icons, remove only ignored artifacts generated inside this worktree when no longer needed, and create exactly one commit with subject "feat(web): make selling workflow installable"; no integration or remote reference change

## Frozen Write Set

Create only:

- web/build/pwa-assets.ts
- web/public/manifest.webmanifest
- web/public/offline.html
- web/public/sw.js
- web/public/icons/icon-192.png
- web/public/icons/icon-512.png
- web/scripts/generate-icons.mjs
- web/src/pwa/register.ts
- web/src/pwa/register.test.ts
- web/e2e/pwa.spec.ts

Modify only:

- web/playwright.config.ts
- web/e2e/security.spec.ts
- web/e2e/workflow.spec.ts
- web/index.html
- web/vite.config.ts
- web/scripts/check-pwa-dist.mjs
- web/src/main.tsx
- web/src/app/AppController.ts
- web/src/app/AppController.test.ts
- web/src/app/App.tsx
- .github/workflows/ci.yml
- scripts/ci_local.sh

The existing browser harness files are modifications, not new paths. No
package manifest or lockfile change is authorized. If a correct implementation
or material review correction requires any other tracked path, stop and publish
one immutable scope blocker naming the smallest needed expansion.

## Required Behavior

Follow Task 5D of the bound plan with these current corrections:

- use only the existing dependency closure and installed Chromium; locally run
  no npm install, npm ci, npx playwright install, package download, or browser
  acquisition;
- web/build/pwa-assets.ts emits /pwa-assets.json with exactly schema_version 1,
  cache_name ppl-static-<sha256-prefix>, and a sorted deduplicated same-origin
  asset list containing the built hashed JS/CSS, offline shell, manifest, and
  192/512 icons, with no query, fragment, external origin, REST/Auth/RPC path,
  source map, or business data;
- generate deterministic opaque 192x192 and 512x512 PNG icons using only Node
  standard-library mechanisms, and prove repeated generation byte-identical;
- the service worker validates the generated manifest, pre-caches only that
  allowlist, deletes only older ppl-static-* caches, waits for explicit
  SKIP_WAITING, and never implements background sync, push, periodic sync,
  business IndexedDB, runtime JSON caching, or business-state messages;
- cross-origin, non-GET, /rest/, /auth/, and /rpc/ traffic is not intercepted;
  navigations are network-first with static offline fallback and never runtime
  cached; eligible static misses go to network without being cached;
- registration occurs only in production. A waiting-worker notice cannot
  activate while a command is in flight. Before SKIP_WAITING, synchronously
  clear sensitive drafts and business DTOs; controller change reloads only
  after that gate;
- offline or transport-unavailable transition synchronously clears sensitive
  state and shows only static shell, nonbusiness pending metadata, and
  "인터넷 연결이 필요합니다";
- pageshow and actor/session transitions revalidate auth, capability, and
  recovery before business state can render, so BFCache and stale async work
  cannot resurrect data across logout or actor/case/revision changes;
- the production meta CSP is exact for the selected same-origin and Supabase
  endpoints, with synthetic.supabase.co used by the test build. Record that
  frame-ancestors and other HTTP response headers remain activation evidence
  for a future host and are not proven by meta CSP;
- the Korean manifest uses start_url and scope "/", standalone display, fixed
  colors, and exact any-maskable PNG entries;
- Playwright page.route mocks all Auth/PostgREST traffic. Browser coverage proves
  login/capability/pagination/comparison/recovery/logout/offline/pageshow/actor
  switch, install criteria, service-worker control/update gate, storage/cache
  emptiness, no business fixture or command body persistence, and zero unmocked
  requests;
- only reviewed auth keys may exist in Session Storage and only nonbusiness
  pending metadata may exist in Local Storage. No business state may persist in
  Cache Storage, Local/Session Storage, IndexedDB, or service-worker messages;
- add secret-free Linux web-tests and web-browser GitHub jobs using
  actions/setup-node@v6 and Node 22.12.0, npm ci --ignore-scripts, explicit
  Chromium acquisition only in the CI browser job, and no repository secrets;
- extend local CI commands for the web gates, but preserve the explicit archived
  iOS exclusion. Do not add or claim an iOS lane.

Assess malformed asset manifests, poisoned cache names/paths, traversal or
external URL entries, cache confusion, stale waiting workers, concurrent
commands, controller-change races, offline/logout/actor-switch races, BFCache
restoration, malicious stored values, unexpected response types, and
uncontrolled network requests. Fail closed without weakening Task 5A-5C
identity, capability, recovery, response-ID, or one-user invariants.

## Test-First And Baseline

After exact setup and before source edits, run the current baseline from the
Task 5D worktree using the symlinked dependency closure:

- npm --prefix web test
- npm --prefix web run typecheck
- npm --prefix web run build:ci
- npm --prefix web run test:e2e
- /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py

Record exact counts and remove only generated worktree artifacts. Add the
focused PWA/security tests first and demonstrate failure for missing behavior,
then implement the smallest complete design. Do not treat a string search,
file-presence assertion, build, or route validator as a substitute for
behavioral execution.

## Required Precommit Gate

From the exact final bytes, run and record:

- focused PWA registration, AppController, asset-manifest, service-worker,
  offline, update, storage, and browser security tests;
- npm --prefix web test;
- npm --prefix web run typecheck;
- npm --prefix web run build:ci followed by the exact dist checker and
  pwa-assets.json schema/allowlist inspection;
- npm --prefix web run test:e2e with production preview and installed Chromium;
- deterministic icon regeneration and IHDR/digest proof;
- /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py;
- exact CSP/manifest/service-worker/cache/storage/network security probes;
- contextual direct-table, RPC, secret, provider/scraping, tracked-real-data,
  source-map, service-worker-scope, and forbidden-endpoint scans;
- exact changed-path manifest, git diff --check, package/lockfile no-diff proof,
  zero iOS diff from the Task-5 base, and protected normal-checkout preservation.

All browser traffic is synthetic. Leave no preview listener, browser report,
test-results, screenshots, trace/video, or generated dist in the final
worktree. web/node_modules is the sole allowed ordinary untracked entry.

Before the target commit, perform two fresh final-byte reviews over the complete
actual diff: one against the functional/spec contract and one against security,
race, persistence, cache, service-worker, and CI abuse cases. Preserve every
material finding with an immutable finding ref. Correct and rerun the
proportional gate; if a material fix needs a frozen path expansion, stop rather
than commit known-bad bytes.

## Commit And Independent Review

Refresh target base/branch/worktree and Pipeline control state immediately before
staging. Stage the frozen manifest explicitly and create exactly one target
commit with the required subject. Prove parent, tree, one-commit range, manifest,
index/tracked cleanliness, sole allowed dependency symlink, absent artifacts and
listeners, and unchanged normal checkout/origin-main.

Director then publishes one canonical committed verify-request through the fixed
writer assigning only Operator2. It binds reviewed repository/worktree, exact
base/head/tree, author identity, exact path manifest and digest, both final-byte
review records/findings, every executed command and result, synthetic/no-network
proof, and all preserved boundaries. It requests one GO/NITS/FAIL over the
actual immutable range.

Use automatic task routing to reuse one compatible Operator2 task or create the
single missing task, send the exact committed request, wait with its cursor, and
reconcile only the canonical committed report. Director may correct material
findings within this route only while the correction remains inside the frozen
write set and yields one squashed Task 5D commit; otherwise publish a blocker.
A correction requires fresh affected tests, complete final-byte reviews, a
replacement committed verify-request, and the same non-author Operator2.

## Stop Boundary

Local Task 5D integration authority: none.
Remote publication authority: none.
Task 5D post-integration aggregate acceptance authority: none.
Task 6 or later-task authority: none.
Other target source, branch, ref, worktree, symlink, commit, or cleanup authority: none.
Dependency and browser acquisition authority: none outside the stated CI workflow text.
Service, database, managed Auth, and private-data authority: none.
Deployment, host selection, physical Windows/Edge installation, booking, and spend authority: none.
iOS modification, build, simulator, CI, beta, and release authority: none.
Cursor and protocol-lock authority: none.
History rewrite, force, broad prune, and unrelated cleanup authority: none.

## Exact Next Trigger

Director reads this committed generation-29 route, publishes and proves the
revision-30 child, creates the exact isolated setup, establishes the executable
baseline, implements Task 5D test-first in the frozen write set, closes both
final-byte reviews, creates the one target commit, publishes the canonical
Operator2 verify-request, automatically dispatches it, waits for the committed
verdict, and stops. Coordinator then routes local integration only after GO and
runs a separately routed fresh aggregate local beta acceptance.

Cursor at send: 0
