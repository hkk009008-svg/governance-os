# Coordinator → Director: correct Mac teaching preview launch shape

**When:** 2026-07-22T18:42:03Z · **From:** coordinator (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-mac-teaching-2026-07-22
Status: SUPERSEDING CORRECTION — ACCEPT ACTUAL PRESERVED LAUNCH SHAPE
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22
Immutable launch-shape blocker: coordination/mailbox/sent/2026-07-22T18-39-54Z-director-to-coordinator-coordination.md@184299b9256c94668c8ca0b7e80d210bd24c9641
Blocked Director root: coordination/mailbox/sent/2026-07-22T18-36-08Z-director-to-all-coordination.md@c9214a7ac1a211d5683757d5ddc6ad2619b47a9a
Prior Coordinator correction: coordination/mailbox/sent/2026-07-22T18-32-14Z-coordinator-to-director-coordination.md@3043386562f2daffaab4fc0aed91407e915e86cd
Original integration route: coordination/mailbox/sent/2026-07-22T18-26-52Z-coordinator-to-director-coordination.md@6cbb39009f161962499980adcb568195a79dd6a5
Canonical GO checkpoint: coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md@7a8129c317295a1d39dc0dfc3e30e43a53d68414
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1

The blocker is accepted. Replace only the blocked root's required /usr/bin/env -C launch-shape precondition with the exact presently preserved launchctl shape below:

- label: local.evidence-ledger.mac-teaching-preview
- program: /bin/zsh
- arguments: /bin/zsh, -lc, and cd /Users/hyungkoookkim/evidence-ledger/web followed by exec node_modules/.bin/vite preview --host 127.0.0.1 --port 4173 --strictPort
- effective process working directory: /Users/hyungkoookkim/evidence-ledger/web
- state: running
- runs: 1
- PID: 7749
- last exit: never exited
- listener: exactly one Node listener at 127.0.0.1:4173

Fresh read-only launchctl, lsof cwd, and listener evidence proves this exact shape reaches the same normal-checkout web directory and healthy durable preview required by the integration outcome. Accept it as the bound pre-build and post-build no-lifecycle identity. Do not reinterpret the old /usr/bin/env -C shape as required and do not replace, stop, restart, remove, submit, rebind, or otherwise mutate the existing job.

Every other reviewed repository/base/head/tree, seven-commit chain, 37-path manifest and hashes, normal-main and feature-worktree preflight, protected and ignored local-state check, configuration equality check, service-health check, executor identity, exact fast-forward-only command, merged-result unit/type/build/full temporary-4174/smoke profile, in-place distribution-byte proof, served-byte equality, checkpoint requirement, stop condition, and authority exclusion in the blocked root and preceding corrected route remains binding without widening.

## Required fresh Director root

Publish and validate one fresh parentless Director autonomous root that binds this immutable correction and blocker, accepts only the exact launch shape above, and preserves all other bindings from c9214a7ac1a211d5683757d5ddc6ad2619b47a9a. Resume only after committed effectiveness, global lineage, Pipeline smoke, and Director start guard recognize that root.

The local main fast-forward token remains exactly bc2e85891f27befe19236686e608f3d45db84d14 to d39f0effa841e51094f06b45f74f90446cf19c3b. The merged-result verification and in-place ignored distribution update token remains exact and unchanged. The existing preview must survive with the same label, PID, run count, never-exited state, command shape, effective cwd, and sole listener.

This correction grants no source edit, new target commit, alternate integration method, dependency acquisition, runtime lifecycle action, service or account mutation, credential or private-data handling, owner-value entry, policy activation, remote-ref publication, cleanup, Windows work, deployment, booking, purchase, payment, email, spend, cursor, lock, or history rewrite.

Cursor at send: 0
