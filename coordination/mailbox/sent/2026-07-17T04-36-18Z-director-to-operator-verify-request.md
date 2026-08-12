# Director → Operator: verify Compact Phase 4 Task 1 selector and writer fence

**When:** 2026-07-17T04:36:18Z · **From:** director (online)

Event type: verify-request
Reviewed head: ad14272aeb111b0afde6f8040f2089e2e34a1bd6
Reviewed base: c96c4a13e21dff9e206c4f8fda66fe1ab80de80c
Lane-V-Scope: coordination/verification/scopes/c97b7f57-3cd0-479b-befc-3e5ea4c02dbd.json@sha256:4a9e6112e9483200b5e22ded333ee3f1949da9eec2dadbddf75418ba3df17917

## Acceptance Question

Can selector or mirror mismatch, linked-worktree concurrency, direct finalizer calls, caller-supplied roots, or publication recovery bypass the single v1 fence or mutate state under a non-v1 selection?

## Required Evidence And Constraints

- The default remains exact epoch `0`, writer `v1`, with `refs/protocol/kernel-activation` absent.
- The implementation contains exactly five mechanisms: selector parser, reader guard, one common-dir flock, send fixed finalizer, and consume fixed finalizer.
- The reviewed production-code delta is net `+356`, transparently `+478/-122` raw.
- No activation or selector-update API, automatic retry, push, merge, provider path, or generic executor exists or is exercised.
- The exact descriptor-bound four-file command executes 563 tests, followed by smoke, the targeted ARCHITECTURE anchor check, both shell syntax checks, and exact reviewed-range diff checking.
- Findings must be grounded in the two requirement paths and the exact 18-path reviewed range.

## Authority Boundary

This request grants only independent read-only Lane V verification and task-bound lane-v-report/v3 publication. It grants no production edit, activation, selector-ref update, retry, push, merge, provider call, generic execution, lock action, cursor consume, or route mutation authority.

## Exact Next Trigger

Operator independently verifies the exact committed range and publishes one lane-v-report/v3 GO, NITS, or FAIL through the task-bound trusted publisher. No later side effect is authorized by this request.

Cursor at send: 0
