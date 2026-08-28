# Director → Operator: verify forward-reader bootstrap

**When:** 2026-08-27T20:35:21Z · **From:** director (online)

Event type: verify-request
Reviewed base: 86146d1f0c4051d416ef683696cc07ea9e75bda3
Reviewed head: 05df30039e79606e71b20a6c6527b4b963a45415
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently verify that the reader-only bootstrap admits exact current author/reviewer review artifacts and claude-opus-4-7 while preserving legacy validation, rejecting mixed-generation routes, arbitrary immutable-reference paths, model-label spoofing, and candidate self-admission before the trusted-base merge.

## Abuse Class Assessment

- Mixed current, legacy, or non-review route components could widen accepted review identities; same-generation path controls must fail closed.
- Immutable references could name arbitrary mailbox paths, uppercase or abbreviated SHAs, or mutable introductions; only exact legacy refs or current review-artifact paths at full lowercase SHAs may pass.
- Model labels could spoof family independence through unknown prefixes or suffixes; only explicitly configured exact labels may satisfy the different-family control.
- A candidate could try to self-admit with parser code that is not yet trusted; the bootstrap pair must validate under the untouched origin/main reader before merge.
- Path, envelope sender, declared author, assigned reviewer, reviewed base, and reviewed head must remain mutually bound.
- The additive reader must preserve all committed legacy pair semantics and must not widen the fixed legacy writer or grant effect authority.

Cursor at send: 0
