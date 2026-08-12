# Director → Operator: re-verify Compact Phase 4 Task 2 disposable rehearsal

**When:** 2026-07-17T07:26:57Z · **From:** director (online)

Event type: verify-request
Reviewed head: a2f03443823acd40a1c4451386595a3fc309aa55
Reviewed base: c5c758c77d11a934aa5f62b99119b66033b529b2
Lane-V-Scope: coordination/verification/scopes/f153c4c7-88f2-4b14-b8ce-9858b3e248bd.json@sha256:a3bbbc456b6e0403fa4a9034fe723d879fea2f972867fdf4b68fec3a24ab2a28

## Findings Requiring This Corrected Trigger

- The superseded scope incorrectly required the review worktree's current HEAD to equal the reviewed head, even though a canonical descriptor and verify-request necessarily land later.
- The failed publication attempt entered through the candidate sender, whose bootstrap requires `scripts/kernel_activation.py` from trusted primary commit `c96c4a13e21dff9e206c4f8fda66fe1ab80de80c`; that blob does not exist there.

## Acceptance Criteria

- Independently verify only the unchanged exact range from `c5c758c77d11a934aa5f62b99119b66033b529b2` through `a2f03443823acd40a1c4451386595a3fc309aa55` and the exact two reviewed paths declared by the fresh descriptor.
- Treat later descriptor and verify-request commits as structural authority, not as reviewed content. The reviewed head must be an ancestor of the current trigger HEAD; current worktree HEAD must not be required to equal the reviewed head.
- The direct reviewed-identity command must print `a2f03443823acd40a1c4451386595a3fc309aa55:5eba3f9cda7a9de97fc68cef18179828c9804a9a`; the committed reviewed mirror must show exact epoch `0` / writer `v1`; and no later diff may touch `governance.toml` or `scripts/kernel_activation.py`.
- The reviewed rehearsal evidence must retain schema `compact-phase4-disposable-rehearsal/v1`, both partial-order fail-closed outcomes, the scratch-only full cutover, restoration to epoch `0` / writer `v1`, clean retained scratch, unchanged primary/source state, and zero prohibited actions.
- Primary HEAD and origin/main must both remain `c96c4a13e21dff9e206c4f8fda66fe1ab80de80c`; scratch HEAD must remain `c5c758c77d11a934aa5f62b99119b66033b529b2`; activation-ref listings and scratch status must remain empty.
- The focused kernel-activation suite, smoke, reviewed evidence display, reviewed commit/tree identity, ancestry check, reviewed selection display, later selection-path diff, activation-ref checks, exact candidate path display, exact primary/scratch identity checks, scratch cleanliness, and reviewed-range diff check must pass with the expected outputs above.
- Expected verdict is GO only if the actual reviewed diff and all descriptor-bound cases pass; otherwise publish NITS or FAIL with findings-first evidence.

## Required Publication Bootstrap

- Build the lane-v-report/v3 body from independent evidence, then invoke the literal absolute primary executable `/Users/hyungkoookkim/Pipeline/coordination/bin/send-event` while the current directory remains `/Users/hyungkoookkim/Pipeline/.worktrees/compact-phase4-task1`.
- The invocation class is `env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/coordination/bin/send-event operator all verification-report <subject>` with the report body on standard input. This is the proven Task 1 bootstrap: it targets the candidate worktree while extracting and running the trusted primary `c96c4a13e21dff9e206c4f8fda66fe1ab80de80c` verification gate blob.
- Do not invoke `coordination/bin/send-event`, `./coordination/bin/send-event`, or `/Users/hyungkoookkim/Pipeline/.worktrees/compact-phase4-task1/coordination/bin/send-event`; those are candidate-sender paths and are forbidden for this publication.

## Authority Boundary And Exclusions

This request grants only independent read-only Lane V verification and one task-bound lane-v-report/v3 publication through the required absolute-primary bootstrap. It grants no production edit, activation, selector-ref update, integration, push, cleanup, cursor consume, provider call, retry, effect execution, packet or route mutation, primary-checkout edit, scratch edit, or historical descriptor/request rewrite. The superseded descriptor and request remain historical and confer no fallback authority.

## Exact Next Trigger

Operator independently verifies the exact unchanged reviewed range and publishes one lane-v-report/v3 GO, NITS, or FAIL through the required absolute-primary sender bootstrap. No later effect is authorized by this request.

Cursor at send: 0
