# Coordinator → All: route Task 4 cleanup then evidence-ledger publication

**When:** 2026-07-21T07:49:27Z · **From:** coordinator (online)

Task-board: ledger-owner-center-task4-cleanup-publish-2026-07-21
Task ID: ledger-owner-center-task4-cleanup-publish-2026-07-21
Program board: ledger-one-user-owner-center-2026-07-20
Status: ACTIVE — EXACT TASK 4 CLEANUP THEN EVIDENCE-LEDGER MAIN PUBLICATION
Route generation: 16
Supersedes route: coordination/mailbox/sent/2026-07-21T07-10-20Z-coordinator-to-all-coordination.md
Expected control HEAD: bdef4c4502e7b2e13693ba768c38c22bbd7d0b8e
Superseded route ref: coordination/mailbox/sent/2026-07-21T07-10-20Z-coordinator-to-all-coordination.md@c1a65650f630f1b526fc8b628c5ddc3b84923fdb
Authorization source: user-task:choice-4-cleanup-push-task5-in-order-2026-07-21
Accepted Task 4 GO: coordination/mailbox/sent/2026-07-21T06-59-57Z-operator2-to-director-verification-report.md@4ed12306c9912a467cd39a614ddba040f0ab27c4
Accepted Task 4 integration evidence: coordination/mailbox/sent/2026-07-21T07-20-07Z-director-to-all-coordination.md@bdef4c4502e7b2e13693ba768c38c22bbd7d0b8e
Executor/model: director / existing compatible Codex task
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47
Accepted target HEAD: e593cc516bea0800bfa997c46e0f758cbae6a83f
Remote target: origin/main
Cleanup worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui
Cleanup branch: codex/owner-center-task4-korean-ui
Cleanup symlink: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui/web/node_modules
Dependency donor: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web/node_modules
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4

## Outcome Contract

Execute the two user-authorized effects in order. First remove only the
integrated Task 4 dependency symlink, owned worktree, and merged local feature
branch. Then publish the already-integrated evidence-ledger `main` from live
remote base `cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47` to exact local head
`e593cc516bea0800bfa997c46e0f758cbae6a83f` with one ordinary non-force
fast-forward remote update.

This packet preserves the dependency donor and every unrelated worktree,
branch, ref, file, and protected setting. Task 5 begins only through a later
committed route after both effects are durably reconciled.

## Director Autonomous Contract Revision 17

Before either effect, Director publishes exactly one fresh director-to-all
coordination event through the fixed writer and commits only that event. It
uses:

- Task ID: ledger-owner-center-task4-cleanup-publish-2026-07-21
- Outcome contract: Remove only the exact integrated Task 4 symlink/worktree/branch, then perform and verify one exact non-force evidence-ledger main publication.
- Parent contract: this committed generation-16 Coordinator route's exact path at its full commit SHA
- Contract revision: 17
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: the immutable refs of this route, the accepted Task 4 GO, and the accepted Task 4 integration evidence

Director proves the contract effective and global route lineage valid, then
runs the ordinary ledger Director start guard against that exact committed
event. The contract grants no effect beyond the two ordered tokens below.

## Side-Effect Executor Token

- effect: exact local feature worktree and branch cleanup
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui:refs/heads/codex/owner-center-task4-korean-ui
- scope: after-main=e593cc516bea0800bfa997c46e0f758cbae6a83f, unlink-one-symlink=/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui/web/node_modules, remove-one-worktree=/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task4-korean-ui, delete-one-local-branch=codex/owner-center-task4-korean-ui, preserve-donor=/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web/node_modules, preserve-all-other-worktrees-and-branches, no-prune, no-force

## Side-Effect Executor Token

- effect: git push
- executor: director
- target: origin/main
- scope: after-cleanup, remote-base=cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47, local-head=e593cc516bea0800bfa997c46e0f758cbae6a83f, refspec=e593cc516bea0800bfa997c46e0f758cbae6a83f:refs/heads/main, exactly-once, no-force

## Exact Preflight

Director stops without either effect unless one fresh observation proves:

- Pipeline contains this exact committed route and its effective revision-17
  Director child; route validation, global lineage, ledger start guard, and
  Pipeline smoke pass;
- the accepted integration evidence binds local `main` at
  `e593cc516bea0800bfa997c46e0f758cbae6a83f`, the canonical GO, the exact
  one-commit Task 4 range, and the protected settings hash;
- normal evidence-ledger `main` and `HEAD` equal the accepted head, their only
  status entry is `.vscode/`, and the protected settings hash matches;
- the cleanup worktree is on `codex/owner-center-task4-korean-ui` at the same
  accepted head with no tracked change and exactly one untracked entry: a
  symlink whose `readlink` target is the stated donor;
- the cleanup branch is fully merged into local `main` and has no commit not
  reachable from `main`;
- the donor worktree, branch, and dependency directory exist and are clean;
- the complete web suite, typecheck, default-heap build/distribution guard,
  normal-checkout smoke, and exact range checks still pass before destructive
  cleanup;
- the exact ordered worktree and local-branch inventories are captured; the
  expected counts are 15 worktrees and 24 local branches;
- `origin` resolves to `https://github.com/hkk009008-svg/evidence-ledger.git`;
- a live read-only remote observation reports `origin/main` exactly
  `cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47`;
- that remote base is an ancestor of the accepted local head with divergence
  `0 remote-only / 43 local-only`; and
- no service, database, private-data, managed-Auth, real policy, deployment,
  booking, or spend access is needed.

No fetch, pull, checkout replacement, autostash, reset, rebase, amend,
cherry-pick, conflict resolution, force deletion, broad pruning, unrelated
staging, or alternate dependency setup is permitted.

## Exact Cleanup Execution And Verification

Director refreshes local state immediately before cleanup. It verifies the
cleanup path is a symlink with the exact donor target, unlinks only that
symlink, and proves the donor still exists unchanged. From the normal
repository root it then runs non-force `git worktree remove` on only the exact
cleanup worktree, followed by non-force `git branch -d` on only the exact
cleanup branch. It does not run `git worktree prune` because unrelated stale
registrations are outside this packet.

Director proves the exact worktree path and local branch are absent, the donor
is intact, local `main` remains the accepted head, the protected hash is
unchanged, and the before/after inventories differ only by the exact cleanup
targets. Expected post-cleanup counts are 14 worktrees and 23 local branches.

## Exact Publication Execution And Verification

After cleanup succeeds, Director refreshes local `main`, status, ancestry,
remote URL, protected hash, and live remote state. If the live remote head is
still `cdd71c0665c46c753efe1a97cc8cf1cd5fbb9e47`, Director may push
origin/main exactly once using the explicit refspec
`e593cc516bea0800bfa997c46e0f758cbae6a83f:refs/heads/main`.

Director performs no retry. A fresh post-effect `git ls-remote` must report
`origin/main` exactly `e593cc516bea0800bfa997c46e0f758cbae6a83f`;
local `main`, `origin/main`, and the live remote ref must align with divergence
`0/0`. Local status and the protected settings hash must remain unchanged.

## Completion Evidence

After both effects and every postcheck pass, Director publishes exactly one
ordinary director-to-all coordination event through the fixed writer with
subject `report Task 4 cleanup and evidence-ledger publication`. It contains
the exact route ref, pre/post cleanup inventories, removed targets, preserved
donor and unrelated state, pre/post live remote refs, explicit refspec, local
and remote alignment, protected hash, verification results, and frozen
boundaries. The event contains no `Task-board` field. Director commits only
that event and returns its immutable ref to Coordinator.

If cleanup or publication cannot complete exactly, Director stops, preserves
all recoverable state, publishes one truthful blocker, performs no fallback,
and returns the exact local and remote state.

## Frozen Boundaries

Other branch/worktree cleanup authority: none.
Broad worktree pruning authority: none.
Additional remote-reference publication authority: none.
Pipeline remote publication authority: none.
Product-edit and new-product-commit authority: none.
Task 5 implementation authority in this route: none.
Dependency installation and replacement authority: none.
Service, database, managed-Auth, and private-data authority: none.
Real policy review or activation authority: none.
Windows installation and deployment authority: none.
Booking and spend authority: none.
Cursor and protocol-lock authority: none.
Reset, rebase, amend, squash, revert, force deletion, conflict resolution,
additional branch deletion, additional worktree removal, and unrelated cleanup
authority: none.

## Exact Next Trigger

Director reads this committed generation-16 route, publishes and proves its
revision-17 autonomous contract, runs the exact preflight, consumes the cleanup
token and then the publication token, publishes the one completion-evidence
event, and stops. Coordinator then independently reconciles local cleanup plus
the live remote ref before routing Task 5.

Cursor at send: 0
