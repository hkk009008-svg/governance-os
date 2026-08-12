# Coordinator → Director: mac-beta-capability-integration

**When:** 2026-07-22T12:05:58Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-mac-capability-integration-2026-07-22
Status: AUTHORIZED REQUEST — REVIEWED LOCAL INTEGRATION AND IN-PLACE BUILD
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22
Reviewed checkpoint: coordination/mailbox/sent/2026-07-22T12-04-24Z-director-to-coordinator-coordination.md@098006a
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T12-02-15Z-operator2-to-director-verification-report.md@17e2d25a782708c1e1ca15592fe9b4fa0aaefe2e
Target repository: /Users/hyungkoookkim/evidence-ledger
Current target main: acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a
Reviewed integration head: bc2e85891f27befe19236686e608f3d45db84d14
Durable preview checkpoint: coordination/mailbox/sent/2026-07-22T11-22-33Z-director-to-coordinator-coordination.md@82fefa03e4fc18d400b5018b830e09db521d6874
Finding ref: MAC-BETA-CAPABILITY-PARITY-001

This is a non-secret Coordinator request for a fresh Director autonomous root with `Parent contract: none`. It grants Coordinator no target write, service lifecycle, browser-authentication, owner-value, policy-activation, push, or Windows authority.

## Required next outcome

Reconcile the exact reviewed range and GO, then authorize Director alone to:

1. Recheck that normal target `main` is exactly `acc298f884d97a6cd3e8b15e5afe65c7b43a8a1a`, its tracked/index state is clean with only the preserved local `.vscode/` and `web/node_modules` items, and reviewed head `bc2e85891f27befe19236686e608f3d45db84d14` is its direct child with the accepted three-path tree.
2. Recheck the durable launchctl job is still running once, has never exited, and owns exactly one loopback listener.
3. Fast-forward only normal target `main` to the exact reviewed head.
4. From normal `web/`, use only the existing installed dependencies to run `npm run build:ci`, updating only ignored distribution bytes.
5. Prove target `main` equals the reviewed head, tracked/index state remains clean with the same preserved local items, the build and nine-file distribution check pass, HTTP returns 200, served HTML and JavaScript hashes equal the newly built normal-checkout dist, and the same launchctl PID/runs/listener survives without restart or rebinding.
6. Publish one committed non-secret integration checkpoint containing the exact Git/build/runtime identities and stop. Coordinator retains the separate private browser acceptance.

No source edit, new commit, alternate merge, conflict resolution, worktree or branch cleanup, preview stop/restart/rebinding, service/container/database/account mutation, authentication, owner value, draft, approval, policy activation, credential/private response handling, dependency or network acquisition, push, Windows work, deployment, booking, spend, cursor consumption, protocol-lock action, or unrelated cleanup is authorized. If any precondition fails, publish one blocker and stop without substitution.

Cursor at send: 0
