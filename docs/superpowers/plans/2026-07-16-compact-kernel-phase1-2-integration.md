# Compact Kernel Phase 1-2 Integration Plan

**Status:** Conditional; no-op first.

**Goal:** Confirm that current Pipeline `main` already provides the reducer/adapter seam needed by the next live caller, while epoch `0` and writer `v1` remain authoritative.

**Canonical constraints:** `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

**Scope:** Pipeline only. Provider replay and evidence-ledger gates are excluded.

## Task 1: Prove Current State

- [ ] Refresh current Git and mailbox truth.
- [ ] Run:

  `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_reducer.py tests/unit/test_capability_v1_adapter.py tests/unit/test_capability_reducer_replay.py tests/unit/test_compact_state_mapping.py -q`

- [ ] Inspect the live caller that needs this seam.
- [ ] If the tests pass and the caller need is already met, close this plan as a no-op.

## Task 2: Correct One Proven Gap

Run only when Task 1 produces one concrete failing test or missing live seam.

- [ ] Route one writer for that exact failure.
- [ ] Add the smallest failing test, then the smallest implementation that passes it.
- [ ] Keep epoch `0`, writer `v1`, and all effect authority unchanged.
- [ ] Re-run the focused command from Task 1.

## Task 3: Verify Only a Changed Diff

If Task 2 changes behavior, obtain one cold review from a non-author-model Operator over the exact committed diff. No behavior change means no verify-request.

## Tripwire

Do not replay frozen branches, descriptors, receipts, handoff digests, or cherry-pick choreography. One unresolved gap that cannot stay narrow stops this plan for re-scope.
