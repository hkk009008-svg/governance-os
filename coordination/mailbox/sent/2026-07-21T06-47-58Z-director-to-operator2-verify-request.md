# Director → Operator2: review Owner-center Task 4 Korean UI

**When:** 2026-07-21T06:47:58Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: e593cc516bea0800bfa997c46e0f758cbae6a83f
Reviewed base: 9879888ee9a3eea29624b168941fc5f0fd1f7628
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-owner-center-task4-korean-ui-2026-07-21
Task ID: ledger-owner-center-task4-korean-ui-2026-07-21
Coordinator route: coordination/mailbox/sent/2026-07-21T06-09-48Z-coordinator-to-all-coordination.md@3ff4079593e93e1739ad6877f92f8997d3bb10cd
Effective Director contract: coordination/mailbox/sent/2026-07-21T06-15-06Z-director-to-all-coordination.md@b196883373fbdf2c27acb4f25b88f9f094793145
Accepted Owner-center Task 3 GO: coordination/mailbox/sent/2026-07-20T13-07-20Z-operator2-to-all-verification-report.md@4a630a9e87061c7f44f324a54b25c714f4a690a7
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Approved design SHA-256: d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208
Implementation plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Implementation plan SHA-256: 8fad121fdc3888155fae06867d5524d4c347bbf29d8ba83e3cd39991195e6f8f
Reviewed worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui
Implementation commit: e593cc516bea0800bfa997c46e0f758cbae6a83f

## Outcome

Independently review the exact one-commit evidence-ledger range
`9879888ee9a3eea29624b168941fc5f0fd1f7628..e593cc516bea0800bfa997c46e0f758cbae6a83f`
for Owner-center Task 4. Confirm the Korean `필요 정보` status-plus-step owner
center is server-authoritative, one-user only, private-memory only, accessible,
and unable to bypass the accepted owner API and actor-scoped command runner.

Confirm owner reads require a current ready actor. Confirm every mutation first
requires fresh `canMutateOwnerSettings`, then calls only
`commandRunner.execute(actorId, "owner_settings", exact_operation, mapper)`
with a runner-owned request ID and the exact current server head. Confirm save,
review, activate, and restore use their accepted exact heads; signed-out,
loading, offline, unavailable, recovery-blocked, viewer, nonmember, revoked, or
stale-generation sessions fail closed. Confirm each command rereads validated
status, draft, and history as applicable and never infers active state or
private fields from a receipt.

Confirm completeness, ordered required fields, activation readiness, IDs,
digests, format status, and history are displayed only from decoded server
responses. The UI must not compute policy math, eligibility, completeness,
digests, or defaults. `아직 모름` must send
`state=unknown,value=null`; `나중에` must not mutate; save must send only
the selected code/state/value and expected draft head. Unknown/later navigation
must remain usable in server order without inventing a value.

Confirm the Korean page exposes the three groups `재무 공식`,
`위험·행동 정책`, and `입력 방식`; active/draft identity; persistent
`설정 필요`; native labels and help without example amounts or rates; the
ten-field in-memory review; explicit `정책 활성화` confirmation containing
only review digest, active formula/risk/activation IDs, and format status;
immutable history identity/time/quorum/format/changed labels; and restore as
copy-to-draft only. Auth/offline/recovery transitions must unmount the page and
discard private values. No browser storage, URL, service-worker, cache,
analytics, log, screenshot, raw operations-only PPL term, second-owner,
matching-approval, signup, profile-switcher, app-PIN, booking, or deployment
path may be introduced.

Confirm the accepted owner-settings API, decoder, wire DTO, ordinary PPL and
selling adapters, and generated-artifact/private-data guards are unchanged.
The owner feature leaf files must remain thin relative-import-only surfaces;
React state and hooks stay at the existing composition root. Confirm all test
data is synthetic and the exact range contains only the ten paths below.

The Director recorded non-vacuous RED before production behavior: the initial
focused selector failed because `OwnerSettingsPage` and three controller
capabilities were absent; the fresh capability selector then failed one test
before the fail-closed freshness check; the navigation selector failed one test
before the unknown/later server-order correction; and the distribution guard
rejected a React import in the owner leaf before the stateful composition was
moved to `App.tsx`. On the committed bytes the focused selector passes 29/29,
the complete web suite passes 150/150, typecheck passes, default-heap
`build:ci` transforms 85 modules and its two-file distribution guard passes,
evidence-ledger smoke ends `OK`, negative source scans have no matches,
`git diff --check` is silent, the range is exactly one commit and ten paths,
all frozen surfaces are unchanged, tracked state is clean, and the sole
untracked entry is the route-authorized ignored dependency symlink
`web/node_modules`.

Adversarial questions: can a stale or newly incapable actor issue a command
between render and dispatch? Can the UI choose a head, request ID, operation,
completeness result, field order, default, digest, active state, or eligibility
that did not come from the accepted server/API/runner? Can private owner values
survive auth/offline/recovery unmount, enter a persistence or telemetry sink,
or appear in general status/history/activation metadata? Can restore activate
policy, can activation omit explicit confirmation or authoritative identity,
or can any raw operations-only or multi-user workflow appear? Issue GO only if
all answers are no, the actual one-commit range satisfies every bound outcome,
and no unresolved hard finding remains; otherwise issue NITS or FAIL with exact
evidence and one disposition for every finding ref.

## Target Allowed Paths

- web/src/app/App.tsx
- web/src/app/AppController.ts
- web/src/app/AppController.test.ts
- web/src/features/owner-settings/OwnerSettingsPage.tsx
- web/src/features/owner-settings/OwnerSettingsPage.test.tsx
- web/src/features/owner-settings/OwnerSettingsStatus.tsx
- web/src/features/owner-settings/OwnerSettingStep.tsx
- web/src/features/owner-settings/OwnerSettingsReview.tsx
- web/src/features/owner-settings/OwnerSettingsHistory.tsx
- web/src/features/owner-settings/copy.ts

## Verification Commands

- In the reviewed worktree, run `env -u GIT_INDEX_FILE git show --format=fuller --name-status --stat e593cc516bea0800bfa997c46e0f758cbae6a83f` and require parent `9879888ee9a3eea29624b168941fc5f0fd1f7628`, exact subject `feat(web): add Korean owner settings center`, and exactly the ten Target Allowed Paths.
- Run `env -u GIT_INDEX_FILE git rev-list --count 9879888ee9a3eea29624b168941fc5f0fd1f7628..e593cc516bea0800bfa997c46e0f758cbae6a83f` and require `1`.
- Run `env -u GIT_INDEX_FILE git diff --name-only 9879888ee9a3eea29624b168941fc5f0fd1f7628..e593cc516bea0800bfa997c46e0f758cbae6a83f` and require exactly the ten Target Allowed Paths.
- Run `env -u GIT_INDEX_FILE git diff --check 9879888ee9a3eea29624b168941fc5f0fd1f7628..e593cc516bea0800bfa997c46e0f758cbae6a83f`.
- From `web/`, run `npm test -- src/features/owner-settings src/app/AppController.test.ts` and require 2 files, 29 tests passed.
- From `web/`, run `npm test` and require 12 files, 150 tests passed.
- From `web/`, run `npm run typecheck`.
- From `web/`, run `npm run build:ci` with the default heap and require the existing distribution guard to report `dist check passed (2 files)`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` from the reviewed worktree and require final `OK`.
- Inspect the actual diff and source for browser-storage, URL, cache, service-worker, analytics, logging, screenshot, raw operations-only PPL, multi-user, invented-default, direct-RPC, non-runner command, stale-actor, private-value exposure, and restore-to-activation escape classes; require no material escape.
- Compare the range against base and require no change to `web/src/features/owner-settings/ownerSettingsApi.ts`, `ownerSettingsDecoders.ts`, `ownerSettingsWire.ts`, `web/src/features/ppl/pplDecisionApi.ts`, `web/src/features/selling-package/sellingPackageApi.ts`, or the existing distribution/generated-artifact scanner guard.
- Require `env -u GIT_INDEX_FILE git status --short --untracked-files=no` to be empty. Treat only `web/node_modules` as the route-authorized ignored dependency setup; do not clean or mutate it.

## Finding Refs

- coordination/mailbox/sent/2026-07-21T06-09-48Z-coordinator-to-all-coordination.md@3ff4079593e93e1739ad6877f92f8997d3bb10cd
- coordination/mailbox/sent/2026-07-21T06-15-06Z-director-to-all-coordination.md@b196883373fbdf2c27acb4f25b88f9f094793145
- coordination/mailbox/sent/2026-07-20T13-07-20Z-operator2-to-all-verification-report.md@4a630a9e87061c7f44f324a54b25c714f4a690a7
- sha256:d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208
- sha256:8fad121fdc3888155fae06867d5524d4c347bbf29d8ba83e3cd39991195e6f8f

## Boundaries

This request authorizes only non-author Operator2 on gpt-5.6-terra to inspect
the exact evidence-ledger range read-only, run the listed local synthetic
checks with existing dependencies, and publish exactly one canonical committed
verification-report. It does not authorize implementation or repair; Task 5;
target-main integration; target branch/worktree cleanup; push or other remote
publication; dependency installation; network; service or database access;
managed Auth or private-data access; real policy review or activation; Windows
installation; deployment; booking; spend; cursor consumption; protocol lock;
merge; reset; rebase; amend; squash; revert; force deletion; unrelated cleanup;
or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
