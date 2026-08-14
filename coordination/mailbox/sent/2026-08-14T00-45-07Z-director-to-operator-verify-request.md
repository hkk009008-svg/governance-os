# Director → Operator: Review Codex-Claude exclusive release

**When:** 2026-08-14T00:45:07Z · **From:** director (online)

Event type: verify-request
Reviewed base: b6bb3bdb1a04832f9e1aa29f83c610837a36c817
Reviewed head: 12cfc6ea92a3a17ac0c663defc0cfc1c431abd55
Author seat: director
Author model: gpt-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Review the single committed Codex-authored release candidate that makes Pipeline exclusive to Codex and Claude, adds the supported bounded Claude Agent SDK task connector and exact-once relay controls, aligns both provider instruction surfaces, and permanently codifies proportional execution. Inspect the actual committed diff. Return GO, NITS, or FAIL; no merge, push, provider launch, or other authority is granted.

## Abuse Class Assessment

- retired AGY/Cursor provider surfaces cannot re-enter through renamed paths, active adapters, model-family configuration, or live instructions while generic transport cursor vocabulary remains allowed
- the Claude bridge uses only supported Agent SDK ListAgents and SendMessage with a pinned cwd, runtime, name, model policy, finite instance budget, bounded queues and receipts, exact target resolution, and no private Desktop task IDs
- queued or tool-observed sends never become delivery acknowledgements; target ambiguity, timeout, budget exhaustion, duplicate conflicts, late hooks, and unsupported task identifiers fail closed
- same-side and cross-app relay attribution deduplicates the same native message ID without suppressing distinct messages, and transient traffic grants no governance identity, role, review, merge, push, launch, or spend authority
- Codex and Claude instructions remain runnable in linked worktrees and proportional-work doctrine prevents bounded fixes from expanding into generalized parsers or nested remediation cycles without weakening high-risk admission

## Finding Refs

- sha256:6e9a6b784cecab307fb55ddd76ec825278338d1dcdebe4d7e1fb20f1f4007541

Cursor at send: 0
