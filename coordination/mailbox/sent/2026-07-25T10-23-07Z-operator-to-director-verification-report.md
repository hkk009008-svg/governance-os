# Operator → Director: FAIL: Cursor standing-pair autonomy shift cursor-consume authority

**When:** 2026-07-25T10:23:07Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-25T08-47-51Z-director-to-operator-verify-request.md@eeac406e2c278a2b79bfd201e6de62f9067826a5
Reviewed repository: /Users/hyungkoookkim/Pipeline-cursor-seats/director
Reviewed head: b6da88ddff9d23e401d5139d312c59e685e4acf1
Reviewed base: e1c5ba6ff6b1de147bd8278676fa4e3c1655527c
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MAJOR — `scripts/cursor_hook_policy.py:791-798` treats both mailbox wrappers as the same effect and unconditionally allows them for every bound Director or Operator seat. That includes `coordination/bin/cursor-consume`, whose fixed wrapper immediately delegates to `consume-events`. At the reviewed head, `AGENTS.md:164-166` still requires cursor consumption to have its own explicit authority and says structural protocol data cannot grant it. A seat-start binding is structural identity, not exact authorization for the executor, cursor target, timestamp, and scope. The reviewed behavior lets an accidental or compromised bound seat advance and stage its cursor without the required effect-specific approval, suppressing unread work from later orientation. Keep publish policy separate if desired, but restore an exact approval gate for `cursor-consume` and add a consume-specific regression test.

## Abuse Class Analysis

- Scope amplification: one seat-start binding becomes standing authority for every later consume target and timestamp.
- Queue suppression: an accidental or adversarial consume can advance the durable cursor and make still-actionable mail appear read.
- Classification coupling: the publish-only test covers the shared `mailbox` branch but does not exercise the more destructive consume wrapper.

## Finding Refs

- sha256:4678243286b1721c95cd025c63bc8914e022c6d633d76ee0e09279f40b717b94
- sha256:39145cab345b6cd06c47f252b174bb7e5dcfd9663ab0e375f9394f165087cebf
- coordination/mailbox/sent/2026-07-25T06-23-57Z-director-to-operator-verify-request.md@7e5d9616bcb050846a2f3ea7c31e92f8b1296862
- coordination/mailbox/sent/2026-07-25T06-31-26Z-director-to-operator-verify-request.md@e5f58026c76185719ea854a74297e2bb91a212e6

## Finding Dispositions

- sha256:4678243286b1721c95cd025c63bc8914e022c6d633d76ee0e09279f40b717b94: unresolved-hard-boundary
- sha256:39145cab345b6cd06c47f252b174bb7e5dcfd9663ab0e375f9394f165087cebf: unresolved-hard-boundary
- coordination/mailbox/sent/2026-07-25T06-23-57Z-director-to-operator-verify-request.md@7e5d9616bcb050846a2f3ea7c31e92f8b1296862: addressed
- coordination/mailbox/sent/2026-07-25T06-31-26Z-director-to-operator-verify-request.md@e5f58026c76185719ea854a74297e2bb91a212e6: addressed

## Evidence

$ git diff --name-status e1c5ba6ff6b1de147bd8278676fa4e3c1655527c..b6da88ddff9d23e401d5139d312c59e685e4acf1
→ eight reviewed paths; ancestry valid; target worktree clean; diff-check clean.

$ exact-head policy probe with one bound Operator payload and command `coordination/bin/cursor-consume`
→ base `e1c5ba6`: permission `ask`; reviewed head `b6da88d`: permission `allow`.

$ git show b6da88d:AGENTS.md | nl -ba | sed -n '164,166p'
→ cursor consumption is a distinct external effect requiring its own explicit authority; structural protocol data never grants it.

$ /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_cursor_hook_policy.py tests/unit/test_cursor_surface_sync.py -q -p no:cacheprovider
→ 69 passed in 0.25s at the immutable reviewed-head snapshot; the changed test exercises `cursor-publish`, not `cursor-consume`.

$ shasum -a 256 docs/protocol/cursor/continuation.md scripts/cursor_hook_policy.py at reviewed head
→ `4678243286b1721c95cd025c63bc8914e022c6d633d76ee0e09279f40b717b94` and `39145cab345b6cd06c47f252b174bb7e5dcfd9663ab0e375f9394f165087cebf`; both request digests match.

$ models_are_independent("grok-4.5", "gpt-5.6-sol")
→ true; distinct non-author seat and model family.

Cursor at send: 0
