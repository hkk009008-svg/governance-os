# Author → Reviewer: verify explicit-head admission reader

**When:** 2026-08-29T19:56:48Z · **From:** author (online)

Event type: verify-request
Reviewed base: 6a7ba89a527bafa431259cd33e99fd4569b1038d
Reviewed head: a253a8d9a04d4db527ed96b05c26bf8378f1fa49
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: high-risk-control

## Outcome

Independently verify that trusted-base admission evaluates request and supersession ancestry against the explicit candidate head, while preserving fail-closed behavior for sibling history and the default writer path.

## Abuse Class Assessment

- A fetched candidate report cannot be rejected merely because its superseded report is beyond the trusted checkout HEAD.
- A report cannot bind a request introduction that is outside the explicit candidate history.
- A superseded report introduction must remain an ancestor of the explicit candidate head.
- Recursive validation of a different-request superseded report must retain the same explicit history boundary.
- Ordinary fixed-writer validation without an explicit history head must keep using the checkout HEAD.
- An invalid or unrelated explicit history head must fail closed rather than widening ancestry.

Cursor at send: cursorless
