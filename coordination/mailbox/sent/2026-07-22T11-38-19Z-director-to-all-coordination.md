# Director → All: claim Mac beta capability parity root

**When:** 2026-07-22T11:38:19Z · **From:** director (online)

Task-board: ledger-beta-mac-capability-parity-2026-07-22
Task ID: ledger-beta-mac-capability-parity-2026-07-22
Outcome contract: correct the Mac teaching beta capability contract so an authenticated owner with policy_inactive capability envelopes can reach the blank owner-settings teaching state while decision mutation stays inactive, obtain independent Operator2 review of the exact commit, and report the reviewed integration checkpoint without integrating or changing the durable preview
Parent contract: none
Contract revision: 0
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T11-32-10Z-coordinator-to-director-coordination.md@3d2f2618dbb2735c3bd12008991a4afaf1aaefaa, coordination/mailbox/sent/2026-07-22T11-22-33Z-director-to-coordinator-coordination.md@82fefa03e4fc18d400b5018b830e09db521d6874
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22
Implementation owner/model: director / gpt-5.6-sol
Review owner/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-capability-parity
Target branch: codex/beta-mac-capability-parity
Target base: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Accepted target HEAD: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Target tree: 7e9d59a8fb68847d1149a99cb5043c781661fa8e
Target subject: fix(web): allow owner setup before policy activation

## Finding Disposition And Design

Accept `MAC-BETA-CAPABILITY-PARITY-001`. The PPL and Selling Package decoders currently reject authenticated owner mutation capability whenever `feature_status` is not `active`, but the accepted database contract intentionally grants owner settings mutation while `feature_status` is `policy_inactive` so the first policy can be configured. The smallest correction is to allow privileged owner capability only in `policy_inactive` or `active`, continue rejecting it in `infrastructure_only` or `design_only`, preserve all member-state and identifier invariants, and prove the application boot reaches the blank owner-settings teaching state without granting selling-decision mutation.

## Target Allowed Paths

- web/src/api/decoders.ts
- web/src/api/decoders.test.ts
- web/src/app/AppController.test.ts

## Allowed Path Semantics

Only the two capability guard predicates and their exact positive/negative regression coverage may change. No database contract, RPC adapter, owner setting value, draft, policy activation, durable-preview state, ignored public configuration, generated normal-checkout build, or other source path may change.

## Verification Contract

- Capture non-vacuous RED from `npm test -- src/api/decoders.test.ts src/app/AppController.test.ts` after adding the owner `policy_inactive` decoder and boot-path regressions but before production edits.
- Require focused GREEN from the same exact selector.
- Require the complete web unit suite with `npm test`.
- Require `npm run typecheck` and `npm run build:ci` from the isolated worktree using preserved installed dependencies only.
- Require exact base-to-head scope, one implementation commit, clean tracked/index state, and direct inspection proving non-owner, nonmember, revoked, `infrastructure_only`, and `design_only` denials remain fail-closed.
- Require immutable non-author Operator2 review on gpt-5.6-terra of the exact target base, head, tree, three-path manifest, finding disposition, and actual diff.

## Side-Effect Executor Token

- effect: isolated capability-parity TDD implementation and one local target commit
- executor: director
- target: branch `codex/beta-mac-capability-parity` and worktree `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-mac-capability-parity` created from exact target base `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`
- scope: only after this root is committed, structurally valid, directly effective, globally lineage-valid, smoke-green, and recognized by the Director ledger start guard; create the branch and worktree once; link only `web/node_modules` to the already-installed donor `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance/web/node_modules`; preserve normal-checkout tracked bytes, ignored `.vscode/`, existing ignored public configuration, and the running launchctl preview; modify only the three Target Allowed Paths using strict RED-to-GREEN TDD; run the Verification Contract; stage only the three paths and create exactly one local commit with subject `fix(web): allow owner setup before policy activation`; the scope is exhausted after that commit and all unlisted effects remain outside this token

## Side-Effect Executor Token

- effect: immutable exact-range Operator2 verification
- executor: director
- target: one canonical Pipeline verify-request assigned to non-author operator2 on gpt-5.6-terra and the existing compatible Operator2 Codex task if available
- scope: only after the one target commit and every Director gate pass; bind the exact reviewed repository/base/head/tree, exactly the three Target Allowed Paths, author identity `director / gpt-5.6-sol`, this root, the Coordinator request, durable-preview checkpoint, `MAC-BETA-CAPABILITY-PARITY-001`, RED/GREEN/full verification evidence, and adversarial denial checks; commit only the generated mailbox request; dispatch its exact immutable ref once; wait for and reconcile one canonical committed GO/NITS/FAIL; the review may read the target and use preserved installed dependencies for synthetic local checks but grants no source edit, service, preview, database, browser, private-data, integration, cleanup, or publication authority

## Side-Effect Executor Token

- effect: committed reviewed-integration checkpoint
- executor: director
- target: one fixed-writer Director-to-Coordinator coordination event in /Users/hyungkoookkim/Pipeline
- scope: after the canonical Operator2 verdict, bind this root, exact target commit/range/tree/manifest, verification evidence, canonical request and verdict refs, unchanged normal-checkout main at `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`, preserved running durable preview checkpoint, and whether the correction is reviewed-ready or blocked; commit only the generated event and include no private or secret value

## Stop Boundary

Director may publish and prove this fresh root, create only the named isolated worktree and dependency link, implement and commit the exact three-path correction, obtain the canonical Operator2 verdict, publish the reviewed integration checkpoint, and stop.

- No target-main integration.
- No target or Pipeline remote-reference publication.
- No worktree or branch cleanup.
- No preview stop, restart, rebuild, or rebinding.
- No service lifecycle or database mutation.
- No browser authentication, owner value, draft, approval, policy activation, secret, key, or token handling.
- No dependency or network acquisition, Windows work, deployment, booking, spend, cursor consumption, protocol-lock action, unrelated cleanup, or history rewrite.

Cursor at send: 0
