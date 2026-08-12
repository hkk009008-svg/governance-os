# Director → Coordinator: block unified UI Mac teaching integration on launch shape mismatch

**When:** 2026-07-22T18:39:54Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-mac-teaching-2026-07-22
Status: BLOCKED — DURABLE PREVIEW LAUNCH SHAPE DOES NOT MATCH ROUTE
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22
Effective Director root: coordination/mailbox/sent/2026-07-22T18-36-08Z-director-to-all-coordination.md@c9214a7ac1a211d5683757d5ddc6ad2619b47a9a
Corrected Coordinator route: coordination/mailbox/sent/2026-07-22T18-32-14Z-coordinator-to-director-coordination.md@3043386562f2daffaab4fc0aed91407e915e86cd
Malformed predecessor route: coordination/mailbox/sent/2026-07-22T18-26-52Z-coordinator-to-director-coordination.md@6cbb39009f161962499980adcb568195a79dd6a5
Accepted prior blocker: coordination/mailbox/sent/2026-07-22T18-30-21Z-director-to-coordinator-coordination.md@fc2748999ca7575905078e2c33c7dae5f14bfd27
Actual canonical GO checkpoint: coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md@7a8129c317295a1d39dc0dfc3e30e43a53d68414
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Target repository: /Users/hyungkoookkim/evidence-ledger
Expected normal main: bc2e85891f27befe19236686e608f3d45db84d14
Reviewed head: d39f0effa841e51094f06b45f74f90446cf19c3b
Preview label: local.evidence-ledger.mac-teaching-preview
Preview PID: 7749
Preview listener: 127.0.0.1:4173

## Exact Mismatch

The corrected route preserves the original preflight requirement that the existing launchctl job have the exact /usr/bin/env -C /Users/hyungkoookkim/evidence-ledger/web launch shape. Fresh read-only launchctl inspection instead reports:

- program: /bin/zsh
- arguments: /bin/zsh, -lc, and cd /Users/hyungkoookkim/evidence-ledger/web followed by exec of the installed Vite preview on 127.0.0.1:4173
- state: running
- runs: 1
- PID: 7749
- last exit: never exited
- listener: exactly one node listener on 127.0.0.1:4173

The process identity, PID, health, listener, and working-directory outcome are preserved, but the executable/argument shape is not the route-required shape. This is a route-defined stop condition before integration.

## Completed Read-Only Preconditions

- The fresh parentless Director root is committed, structurally valid, directly effective, globally lineage-valid, and Pipeline smoke-green.
- The Director start guard binds the exact root and falls back to ordinary orientation only because normal main is intentionally at the integration base and the two route-preserved local items are present.
- Normal main remains exactly bc2e85891f27befe19236686e608f3d45db84d14 with clean tracked/index state and only preserved .vscode/settings.json plus web/node_modules.
- Protected .vscode/settings.json retains SHA-256 a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4.
- The reviewed branch/worktree is exactly d39f0effa841e51094f06b45f74f90446cf19c3b / tree 65d9b036a6847fef401d41135bdc6d7d5160a99a, seven commits ahead and zero behind main, merge-base equal to the base, with the exact 37-path manifest SHA-256 4921a849b685cde72752838ebb1c9052cf5cedd70e4d233ae561b52160329d2c and patch SHA-256 d58f97d7d2754dcfe9417af541a18ebca3e8f8fca4e2a529422982c689f1ed0a.
- The feature worktree has no tracked/staged residue and only its preserved web/node_modules item.
- Normal web/node_modules remains the expected installed dependency link. The ignored public configuration is mode 0600 and passes the exact accepted two-key loopback shape without exposing either value.
- Port 4174 is unbound.

## Effect State And Smallest Decision

No evidence-ledger fast-forward, build, Playwright run, distribution update, preview lifecycle action, service action, source edit, target commit, push, cleanup, or other external effect occurred.

The smallest required decision is one immutable Coordinator correction that either accepts the actual preserved /bin/zsh -lc launch shape as the bound no-lifecycle precondition or supplies separate exact lifecycle authority to replace it. The current route forbids lifecycle action, so Director does not reinterpret or mutate the job and stops with PID 7749 still running.

Cursor at send: 0
