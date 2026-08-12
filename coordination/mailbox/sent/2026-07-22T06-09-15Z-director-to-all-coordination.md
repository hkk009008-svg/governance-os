# Director → All: own Mac-first local beta activation

**When:** 2026-07-22T06:09:15Z · **From:** director (online)

Task-board: ledger-beta-mac-activation-2026-07-22
Task ID: ledger-beta-mac-activation-2026-07-22
Outcome contract: integrate the reviewed Task 6 head and prepare the exact local Mac beta runtime through a private-provisioning checkpoint and final loopback teaching URL
Parent contract: coordination/mailbox/sent/2026-07-22T06-03-28Z-coordinator-to-all-coordination.md@da36b21029303939ddbd7d8ec1eace0ffcd8e7b2
Contract revision: 35
Previous owners: none
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-22T06-03-28Z-coordinator-to-all-coordination.md@da36b21029303939ddbd7d8ec1eace0ffcd8e7b2, coordination/mailbox/sent/2026-07-22T02-19-59Z-operator2-to-director-verification-report.md@1f2cdb9040e18bc3ffdd0a617d00e61691139f51, coordination/mailbox/sent/2026-07-22T05-14-28Z-operator2-to-director-verification-report.md@ef52b7c66d73052f840285069d44b987013c3a8f, coordination/mailbox/sent/2026-07-22T05-16-26Z-director-to-coordinator-coordination.md@ec759c9205052bba9769e72c2124861e6c388d6a
Authorization source: user-task:mac-first-beta-activation-approved-2026-07-22
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Target base: 171617635a7043ad5814edcc250cda3bc3474f75
Accepted target HEAD: 171617635a7043ad5814edcc250cda3bc3474f75
Reviewed integration head: 87a10b787a2f01f4353cad6a5e8ed338c381d333
Protected local settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Private provisioning executor: coordinator

## Target Allowed Paths

- data/local-beta
- web/.env.local
- web/dist

## Allowed Path Semantics

These are the complete ignored runtime write locations. No tracked source edit or new target commit is authorized. The exact reviewed fast-forward is the only target history change. Preserve the untracked `.vscode/` directory and its protected settings hash exactly.

## Side-Effect Executor Token

- effect: exact local Task 6 fast-forward integration
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger:refs/heads/main
- scope: require current main and HEAD exactly 171617635a7043ad5814edcc250cda3bc3474f75 with only preserved `.vscode/`; require that base is an ancestor of 87a10b787a2f01f4353cad6a5e8ed338c381d333 and the accepted Task 6 GO binds that head; execute one `git merge --ff-only 87a10b787a2f01f4353cad6a5e8ed338c381d333`; require main and HEAD equal the reviewed head, index and tracked diff empty, `.vscode/settings.json` hash unchanged, exact 24-path range, and diff check clean; no fetch, pull, conflict resolution, history rewrite, remote-reference change, feature-worktree cleanup, or unrelated staging

## Side-Effect Executor Token

- effect: exact installed Docker Desktop launch and identity discovery
- executor: director
- target: /Applications/Docker.app bundle com.docker.docker version 4.82.0 build 233772
- scope: if the daemon is still unavailable, open the existing application once without installation, update, sign-in, configuration change, image acquisition, container command, or retry; wait at most 180 seconds for the local daemon; then perform read-only inventory only and publish revision 36 before any container/database action; if the daemon is already available, do not relaunch or later quit it

## Boundaries

This continuation grants no effect beyond the committed parent route. All later runtime phases remain held until their exact route checkpoint. No tracked source change, target commit, remote-reference publication, dependency or image acquisition, managed service, real/private business data, policy activation, deployment, Windows packaging, provider contact, booking, spend, cursor consumption, shared coordination fence mutation, feature-worktree cleanup, or unrelated cleanup is authorized.

Cursor at send: 0
