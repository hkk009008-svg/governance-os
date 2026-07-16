# Recovery Owner/WIP Disposition Plan

**Status:** Standby; no-op by default.

**Goal:** Prevent current non-provider Pipeline work from being overwritten when ownership is genuinely unclear.

**Canonical constraints:** `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

**Scope:** Pipeline only. Provider-tool work and all evidence-ledger repository work are excluded.

## Trigger

Run this plan only when current non-provider Pipeline bytes have no clear owner or must transfer to another owner. A clean tree, an already-owned worktree, or historical branch state is not a trigger.

## Execution

- [ ] Refresh current `main`, newest mailbox bodies, worktree state, and `git status`.
- [ ] Identify only the exact ambiguous paths and their current owner.
- [ ] If ownership is already clear, stop without a route, inventory, or handoff.
- [ ] If ownership is unclear, name one owner and preserve the exact bytes once.
- [ ] Write one handoff only if ownership actually transfers; include the exact paths, base, preserved location, and next trigger.

## Acceptance

- No provider branch, receipt, consultation, target checkout, or evidence-ledger artifact is opened or changed.
- No aggregate packet matrix or recovery inventory is created.
- Commit, route, branch creation, push, merge, and cleanup remain separately authorized actions.

## Exact Stop

Stop when ownership is clear and the bytes are safe. Do not manufacture downstream work.
