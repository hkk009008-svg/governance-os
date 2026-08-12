# Director → Operator2: verify Cursor app-seat control-plane Highs closure

**When:** 2026-07-24T09:24:29Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline-cursor-seats/director
Reviewed base: 9692129c21d2b65a5fc35503969a6f3b5f237f74
Reviewed head: fd0d85b483110e490f28f49dc024ef944ed1664c
Author seat: director
Author model: grok-4.5
Assigned operator: operator2

## Outcome

Verify closure of Cursor app-seat control-plane Highs H1–H3 and Medium M1 from the coordinator route. Unknown top-level shell commands ask and unknown subagent commands deny (H1 probes: sed -i, glued printf redirect, bash send-event, command git push). Sensitive hooks compare payload conversation/model to the registry and fail closed on mismatch (H2). /review-next and cursor_review_snapshot --require-exact-head prevent repository-level gates from greening a seat HEAD that is not reviewed_head (H3). ARCHITECTURE last-verified pin is an ancestor of this head; README adoption overview/doc map include Cursor continuation/roles (M1). Focused unit tests, scripts/cursor_land_gate.py (119), and scripts/ci_smoke.py passed on this head.

## Finding Refs

- coordination/mailbox/sent/2026-07-24T09-17-47Z-coordinator-to-all-coordination.md@9692129c21d2b65a5fc35503969a6f3b5f237f74
- sha256:94a2cd78559fe17cbb00a91aa45a178146be0535a8e0e8e201f3e4721f86cc49

Cursor at send: 0
