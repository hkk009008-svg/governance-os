# Coordinator → All: route Owner-center Task 4 Korean UI

**When:** 2026-07-21T06:09:48Z · **From:** coordinator (online)

Task-board: ledger-owner-center-task4-korean-ui-2026-07-21
Task ID: ledger-owner-center-task4-korean-ui-2026-07-21
Program board: ledger-one-user-owner-center-2026-07-20
Status: ACTIVE — OWNER-CENTER TASK 4 KOREAN STATUS-PLUS-STEP UI
Route generation: 14
Supersedes route: coordination/mailbox/sent/2026-07-21T05-25-09Z-coordinator-to-all-coordination.md
Expected control HEAD: 1cbb6860d2329baddb8de20d7c6b86f7c2ffbe44
Superseded route ref: coordination/mailbox/sent/2026-07-21T05-25-09Z-coordinator-to-all-coordination.md@2c0bc19ad7c04eb04d8b3749d271f64d2f5a9384
Authorization source: user-task:proceed-with-ledger-task-2026-07-21
Accepted audit-remediation completion: coordination/mailbox/sent/2026-07-21T05-36-34Z-director-to-all-coordination.md@1cbb6860d2329baddb8de20d7c6b86f7c2ffbe44
Accepted Owner-center Task 3 GO: coordination/mailbox/sent/2026-07-20T13-07-20Z-operator2-to-all-verification-report.md@4a630a9e87061c7f44f324a54b25c714f4a690a7
Accepted Owner-center Task 3 integration commit: 1ad4eb2b5550af7c3941aacf08240559a9051193
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Approved design SHA-256: d4f037c728fc7d1d87d1992c20a3979f6c223cf5d7dc7f12ab73738a761ec208
Implementation plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Implementation plan SHA-256: 8fad121fdc3888155fae06867d5524d4c347bbf29d8ba83e3cd39991195e6f8f
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui
Target branch: codex/owner-center-task4-korean-ui
Target base: 9879888ee9a3eea29624b168941fc5f0fd1f7628
Accepted target HEAD: 9879888ee9a3eea29624b168941fc5f0fd1f7628
Dependency donor: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web/node_modules
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Outcome Contract

Execute only Owner-center Task 4 from the approved plan: build the Korean
`필요 정보` status-plus-step owner center on the current integrated target head.
The page collects the one operational user's missing private configuration,
keeps unknown values explicit, performs every command through the existing
actor-scoped command runner, and displays server-authoritative status, draft,
review, activation, history, and copy-to-draft restore behavior.

This packet creates one local target commit and submits its immutable actual
range for independent Operator2 review. It does not execute Task 5, activate a
real policy, contact a service or database, use private values, install a
dependency, integrate target main, publish a remote reference, deploy, install
the PWA, book, or spend.

## Current-Head Plan Reconciliation

The approved plan's fixed Task 1-3 worktree is intentionally preserved at
`edd148f30b7ba001a8dfb754ebb6856f119ed3a2`; it is stale for new work. Task 4
uses the fresh isolated worktree above at `9879888ee9a3eea29624b168941fc5f0fd1f7628`.
The current target's `web/` tree is byte-identical to the accepted Task 3 head,
while audit remediation changed only non-web surfaces.

The plan says the page consumes `OwnerSettingsApi`, the command runner, and the
controller, but current `App.tsx` can access only controller capability methods.
The packet therefore permits the smallest missing composition seam in
`AppController.ts` plus focused tests: read methods delegate to the existing
owner API, and mutations delegate only through the existing actor-scoped
`commandRunner.execute`. No new context, store, persistence layer, transport,
or operation is permitted.

The plan's activation-dialog prose names separate formula/risk/format digests,
but the accepted `owner-settings-api-v1` deliberately exposes only the current
review digest, active formula/risk/activation IDs, and format status. The dialog
must show those authoritative fields and no private values. Do not widen the
reviewed API, DTO, database contract, or adapter merely to manufacture fields
that do not exist.

## Director Autonomous Contract Revision 15

Before target mutation, Director publishes exactly one fresh director-to-all
coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-owner-center-task4-korean-ui-2026-07-21
- Outcome contract: Implement and verify the Korean status-plus-step owner center at the exact routed target parent, create one local Task 4 commit, and submit its immutable range to Operator2.
- Parent contract: this committed generation-14 Coordinator route's exact path at its full commit SHA
- Contract revision: 15
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: the immutable ref of this route, the accepted Task 3 GO, and the approved design and plan SHA-256 refs

Director proves the contract effective and global route lineage valid, then
runs the ordinary ledger Director start guard against that exact committed
event before touching the target.

## Side-Effect Executor Token

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui
- scope: branch=codex/owner-center-task4-korean-ui, parent=9879888ee9a3eea29624b168941fc5f0fd1f7628, dependency-setup=ignored-web-node_modules-symlink-from-existing-donor, no-install, no-network

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

Every other target path is frozen. Test fixtures are synthetic and contain no
real business amount, rate, credential, owner value, workbook value, command
body, or response copied from a live system.

## Exact Preflight

Director stops without target mutation unless one fresh observation proves:

- Pipeline contains this exact committed route and its effective revision-15
  Director child; route validation, global lineage, ledger start guard, and
  Pipeline smoke pass;
- evidence-ledger normal `main` and HEAD equal the accepted target head, with
  `.vscode/` as their only status entry and the protected settings hash intact;
- `1ad4eb2b5550af7c3941aacf08240559a9051193` is an ancestor of the target head;
- the target `web/` tree is byte-identical to accepted Task 3 head
  `edd148f30b7ba001a8dfb754ebb6856f119ed3a2`;
- the authorized target worktree path and branch do not exist;
- the design and plan bytes match their stated SHA-256 values;
- the dependency donor exists, is ignored, and its source worktree is clean;
  and
- no dependency installation, service, database, network, or private-data
  access is needed.

Director creates only the exact branch/worktree in the token. It may create one
ignored `web/node_modules` symlink to the donor and must prove the new worktree
otherwise clean at the exact parent. Before edits, run the complete current web
suite, typecheck, and `build:ci`; any baseline failure stops the packet.

## Test-First Implementation Contract

Director follows RED-GREEN-REFACTOR for each behavior. Production code is not
written until the corresponding focused test fails for the expected missing
behavior. Record the focused RED command and expected failure evidence, then
make the smallest implementation that turns it green.

### 1. Minimal controller composition seam

Extend the existing controller tests first. Reads are available only for a
current ready actor and delegate to the accepted owner API. Owner mutations are
available only when `canMutateOwnerSettings` is true and execute through
`commandRunner.execute(actorId, "owner_settings", exact_operation, ...)`.
Every command uses a fresh runner-owned request ID and the exact server head
specified by `owner-settings-api-v1`. Direct UI-to-RPC calls, new operation
names, nested command transactions, or mutation while signed out, loading,
offline, unavailable, recovery-blocked, viewer, nonmember, or revoked are
forbidden.

After each command, reread validated server status/draft/history as applicable.
Do not infer a private field or active state from the metadata-only command
receipt.

### 2. Korean server-authoritative page

`ConfiguredApp` renders the owner center for the ready one-owner session. The
page renders loading, expected-error, redacted-unavailable, offline, and
recovery-blocked states without cached private data. It groups the status as
`재무 공식`, `위험·행동 정책`, and `입력 방식`; shows active versus draft
identity; maintains a persistent `설정 필요` badge/banner when incomplete;
and chooses the next required field only from the server's ordered items.

The UI never computes completeness, action eligibility, formula math, policy
digests, or defaults. It trusts only the decoded `activation_ready`, field
states, and IDs from the server.

### 3. Step, unknown, and help behavior

The current field has a native Korean label, help text explaining where to find
the information, and an input appropriate to rate or whole-KRW values. Help
contains no example amount or rate and inputs are never prefilled with an
invented value. `아직 모름` sends `state=unknown,value=null`; `나중에`
performs no mutation; `저장하고 다음` sends only the selected code/state/value
and expected draft head, then replaces local display state from a validated
server reread.

### 4. Review, activation, history, and restore

Review remains unavailable until the server reports `activation_ready` or the
accepted draft state permits the review step. The Korean review shows the ten
field labels and current private values only inside the in-memory owner screen.
Activation requires an explicit `정책 활성화` confirmation showing the review
digest, active formula/risk/activation IDs, and format status; general status
and history copy do not expose private values.

History shows immutable activation identity/time, approval quorum, format, and
changed field names. Restore only executes copy-to-draft, reloads the new draft,
and routes to review; it never changes active policy directly.

### 5. Accessibility and one-user negatives

Focused tests cover native labels, semantic headings/status, keyboard order,
focus placement after save/error/navigation, disabled mutations, and fixed
Korean copy. They assert no second-owner, matching-approval, signup, profile
switcher, app-PIN, booking, deployment, or raw operations-only language. Page
unmount on auth/offline/recovery transitions must discard its in-memory private
state; browser storage, URL, service-worker, cache, analytics, log, and
screenshot persistence are forbidden.

## Commit And Verification

Director creates exactly one local target commit with subject:

`feat(web): add Korean owner settings center`

The committed range must be exactly one commit after the accepted target head
and may contain only the ten allowed paths. Stage explicit pathspecs only.

On committed bytes, run:

- focused owner-center plus controller tests;
- the complete web test suite;
- `npm run typecheck`;
- `npm run build:ci` with default heap and the existing distribution guard;
- source searches proving private persistence and raw operations-only PPL names
  did not enter the owner feature or app;
- evidence-ledger `scripts/ci_smoke.py`;
- exact-range `git diff --check`, one-commit/path manifest, and clean-worktree
  checks; and
- normal-checkout head/status plus protected-settings hash checks.

No acceptance command may contact Postgres, Supabase, another service, a
network endpoint, private workbook, or real data.

## Independent Review Contract

After every committed-byte gate passes, Director publishes exactly one
immutable verify-request assigned to non-author Operator2 and dispatches the
existing compatible Operator2 Codex task exactly once. The request binds the
target repository, worktree, exact base/head/one-commit range, ten-path
manifest, author and reviewer identities, design/plan refs and hashes, RED/GREEN
evidence, verification commands/results, and distinct immutable finding refs
for:

- actor/capability gating and command-runner-only mutations;
- server-authoritative completeness and post-command rereads;
- unknown/no-default behavior and private-memory boundaries;
- Korean status/step/review/activation/history/restore behavior;
- review-digest plus active-ID/format confirmation;
- accessibility and one-user language negatives;
- unchanged owner API/DTO/adapter and ordinary PPL/selling adapter inventories;
- unchanged artifact-scanner/private-data fences; and
- exact scope, synthetic-only evidence, and clean state.

Operator2 independently inspects and runs the focused tests, full web suite,
typecheck, build/distribution guard, persistence/operation negative searches,
and target smoke against the actual committed range. Operator2 alone issues
GO, NITS, or FAIL. Director stops at that verdict; it does not integrate or
clean the target branch/worktree.

## Frozen Boundaries

Task 5 documentation and cumulative-review work authority: none.
Target-main integration authority: none.
Target branch/worktree cleanup authority: none.
Remote-reference publication authority: none.
Dependency installation authority: none.
Network authority: none.
Service and database authority: none.
Managed Auth and private-data authority: none.
Real policy review or activation authority: none.
Windows installation and deployment authority: none.
Booking and spend authority: none.
Cursor and protocol-lock authority: none.
Reset, rebase, amend, squash, revert, force deletion, and unrelated cleanup authority: none.

## Exact Next Trigger

Director reads this committed generation-14 route, publishes and proves its
revision-15 autonomous contract, runs the exact preflight, creates only the
authorized worktree, and executes Task 4 test-first under the reconciliations
above. Director creates one target commit, proves its exact immutable range,
publishes the single verify-request, dispatches Operator2 once, and stops at
the independent verdict. Any lineage, baseline, RED-evidence, scope, test,
build, privacy, Korean-copy, accessibility, manifest, synthetic-data, or clean-
state failure returns to Coordinator with both repositories preserved.

Cursor at send: 0
