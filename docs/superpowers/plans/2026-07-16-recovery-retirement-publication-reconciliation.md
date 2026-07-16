# Recovery Retirement and Publication Reconciliation Plan

**Status:** No-op first; two tasks maximum if later compact work creates drift.

**Goal:** Leave current Pipeline runtime and descriptive truth aligned without duplicating an already-terminal closeout.

**Canonical constraints:** `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

**Scope:** Pipeline only. Do not inspect, reconcile, verify, integrate, or publish evidence-ledger state.

## Task 1: Check Truth Once

- [ ] Refresh current Git, mailbox, and the newest coordinator handoff.
- [ ] Run `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`.
- [ ] Compare only documentation touched by later compact work with current runtime.
- [ ] If no drift exists, stop without another closeout artifact.
- [ ] If drift exists, update it once and obtain one non-author-model Operator consistency review.

## Task 2: Close Only New Work

After GO for an actual later diff, write one coordinator status with the exact reviewed range and next trigger. Do not re-close provider decommission.

## Side-Effect Boundary

Push, merge, branch/worktree cleanup, runtime cleanup, and publication remain separate optional actions.
