# Control-Plane Compact Phase 3 Convergence Plan

**Status:** Conditional; three tasks maximum.

**Goal:** Keep only live Pipeline control-plane behavior and add at most one missing trigger behavior inside the existing reducer boundary.

**Canonical constraints:** `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

**Entry:** Phase 1-2 is proven on current `main`. Provider decommission is terminal. Evidence-ledger work is excluded.

## Task 1: Inventory Live Callers

- [ ] Refresh Git and mailbox truth.
- [ ] Run `rg -n 'reduce_protocol_state|adapt_v1_history|load_kernel_mirror' scripts tests`.
- [ ] For each helper touched by this plan, choose only `keep` for a live caller or `delete` for no live caller.
- [ ] If no concrete behavior gap remains, stop as a no-op.

## Task 2: Make One Narrow Change

Run only for a failure demonstrated by a focused test.

- [ ] Route one writer for the exact files.
- [ ] Add or amend one failing test.
- [ ] Implement the minimum behavior or delete the dead helper.
- [ ] Run the affected unit file plus:

  `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_reducer.py tests/unit/test_capability_v1_adapter.py tests/unit/test_target_binding.py -q`

GPT-Pro is not implemented by this plan. A future provider tool requires separate user authorization and a new plan.

## Task 3: One Independent Verdict

For a behavior-changing diff, request one cold non-author-model Operator review. The Operator alone issues GO/NITS/FAIL.

## Tripwire

Do not add a second event store, provider schema, receipt bridge, actor framework, or advisory subsystem. If the production delta approaches 500 lines or needs a recovery plan, stop and re-scope.
