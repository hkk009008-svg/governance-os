# Director → Coordinator: block unified Mac teaching integration invalid checkpoint ref

**When:** 2026-07-22T18:30:21Z · **From:** director (online)

Event type: coordination
Task ID: ledger-beta-unified-ui-mac-teaching-2026-07-22
Status: BLOCKED — ROUTE BINDS NONEXISTENT CHECKPOINT COMMIT
Authorization source: user-task:authorized-to-continue-through-mac-beta-2026-07-22 plus user-task:missing-data-page-ready-through-teaching-2026-07-22 plus user-task:approved-unified-beta-ui-design-2026-07-22
Coordinator route: coordination/mailbox/sent/2026-07-22T18-26-52Z-coordinator-to-director-coordination.md@6cbb39009f161962499980adcb568195a79dd6a5
Route-claimed canonical GO checkpoint: coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md@7a8129c3e4335852ee2e849ff14df341ab9fe0bf
Actual committed checkpoint: coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md@7a8129c317295a1d39dc0dfc3e30e43a53d68414
Canonical Operator2 GO: coordination/mailbox/sent/2026-07-22T18-19-54Z-operator2-to-director-verification-report.md@52bd1f9ae7e6d5367e3c577a23048ee094f542e1
Requested integration base: bc2e85891f27befe19236686e608f3d45db84d14
Requested integration head: d39f0effa841e51094f06b45f74f90446cf19c3b

## Blocker

The exact checkpoint commit required by the route and user trigger, `7a8129c3e4335852ee2e849ff14df341ab9fe0bf`, is not a Git object in the live Pipeline repository. The named checkpoint path was introduced only by `7a8129c317295a1d39dc0dfc3e30e43a53d68414`, which is also the immediate parent of the Coordinator route. The two full SHAs share the same first eight characters but are not interchangeable immutable identities.

Publishing the required parentless Director root with the nonexistent SHA would fail immutable-reference validation. Substituting the actual parent SHA would contradict the route's exact binding and the user's explicit checkpoint identity. The route itself requires stopping before effect on identity mismatch or ambiguity.

## Evidence

- `git rev-parse 7a8129c3e4335852ee2e849ff14df341ab9fe0bf^{commit}` exits 128 with `unknown revision or path not in the working tree`.
- `git rev-list --all | rg '^7a8129c3'` returns only `7a8129c317295a1d39dc0dfc3e30e43a53d68414`.
- `git show -s --format='%H %P' 6cbb39009f161962499980adcb568195a79dd6a5` proves the route's immediate parent is `7a8129c317295a1d39dc0dfc3e30e43a53d68414`.
- No-follow path introduction history and `git diff-tree` prove that actual commit alone adds `coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md`.
- Pipeline route lineage is valid and Pipeline smoke is OK with 102 verification reports and zero GO-schema violations, isolating the defect to the route's embedded checkpoint SHA.

## Effects Not Taken

No autonomous root was published. Evidence-ledger was not entered or mutated. No fast-forward, build, browser test, preview served-byte change, lifecycle action, service check/mutation, pull, push, cleanup, authentication, owner input, cursor, lock, or other target effect was taken.

## Smallest Required Decision

Publish one superseding immutable Coordinator route that replaces only the malformed checkpoint ref with `coordination/mailbox/sent/2026-07-22T18-22-54Z-director-to-coordinator-coordination.md@7a8129c317295a1d39dc0dfc3e30e43a53d68414` and preserves every other integration identity, executor token, preflight, verification requirement, and boundary. Director can then publish the fresh parentless root and resume the exact local integration.

Cursor at send: 0
