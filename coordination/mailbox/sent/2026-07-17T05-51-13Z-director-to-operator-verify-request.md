# Director → Operator: verify Compact Phase 4 Task 2 disposable rehearsal

**When:** 2026-07-17T05:51:13Z · **From:** director (online)

Event type: verify-request
Reviewed head: a2f03443823acd40a1c4451386595a3fc309aa55
Reviewed base: c5c758c77d11a934aa5f62b99119b66033b529b2
Lane-V-Scope: coordination/verification/scopes/8c4e34a5-323c-4621-ac80-e67754e2e73d.json@sha256:bcc53b1fb90ff049c90a01e914d0faad9f4001c2e06977f770a746af130b84ed

## Acceptance Criteria

- The reviewed range contains exactly the Phase 4 plan and disposable rehearsal evidence paths declared by the scope.
- The evidence schema is `compact-phase4-disposable-rehearsal/v1`, and both selector-only and mirror-only partial orders fail closed before returning to epoch `0` / writer `v1`.
- The full cutover occurs only inside the independent scratch clone: epoch `1` / writer `compact` denies the v1 reader and v1 writer while admitting the compact writer fence.
- The scratch clone is restored to epoch `0` / writer `v1`, has no activation ref, is clean, and remains retained without cleanup.
- The primary checkout and reviewed source remain epoch `0` / writer `v1` with no activation ref; primary HEAD and origin/main remain `c96c4a13e21dff9e206c4f8fda66fe1ab80de80c`.
- The focused kernel-activation suite, smoke, descriptor-bound evidence assertions, live authority checks, exact candidate path comparison, and diff check pass.
- No primary activation, integration, push, cleanup, cursor consumption, or provider call occurred or is authorized.

## Authority Boundary

This request grants only independent read-only Lane V verification and task-bound lane-v-report/v3 publication. It grants no production edit, activation, selector-ref update, integration, push, cleanup, cursor consume, provider call, retry, route mutation, or other later effect.

## Exact Next Trigger

Operator independently verifies the exact committed range and publishes one lane-v-report/v3 GO, NITS, or FAIL through the task-bound trusted publisher. No later effect is authorized by this request.

Cursor at send: 0
