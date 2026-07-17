# Compact Kernel Phase 4 Activation Plan

**Status:** Inactive; separate user authorization is required to activate.

**Goal:** Move Pipeline through one small, fail-closed cutover while preserving one writer.

**Canonical constraints:** `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

**Scope:** Pipeline only. Evidence-ledger, provider, target-bridge, and PPL gates are excluded.

## Task 1: Small Cutover Boundary

- [x] Put current live readers and writers behind one activation selector and one shared writer fence.
- [x] Keep the default at epoch `0` / writer `v1`.
- [x] Add focused denial and single-writer tests.

## Task 2: Rehearse and Review

- [x] Run one disposable local cutover rehearsal.
- [x] Prove failed or partial activation leaves the normal state authoritative.
- [x] Obtain one cold non-author-model Operator verdict over the exact diff and rehearsal evidence.

## Task 3: Separately Authorized Activation

Only the executor named by the user may perform the effect.

- [ ] Recheck GO, current HEAD, selector state, and writer fence.
- [ ] Perform one activation attempt; fail closed on ambiguity.
- [ ] Verify the normal runtime state and stop.

## Tripwire

Do not create archive-ref forests, new cursor authorities, fixed observation rituals, self-hash workarounds, retries, or a recovery campaign. Push and cleanup are separate actions.
