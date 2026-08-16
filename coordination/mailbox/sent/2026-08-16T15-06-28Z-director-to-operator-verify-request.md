# Director → Operator: full-range review for PR 32 admission

**When:** 2026-08-16T15:06:28Z · **From:** director (online)

Event type: verify-request
Reviewed base: e858b4ec49796a6a1dd95a6394ba4a62595df9ee
Reviewed head: 9e73f9b8bac9d38a35a788f0256f1dafb705f7f2
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

This is the admission review, and it asks a question none of the previous ones
did. Every round so far reviewed one range against its predecessor. None
reviewed e858b4e..HEAD, which is why the gate reports eleven authority-surface
commits with ten still uncovered: superseded reports do not admit, FAIL does not
admit, and the only admitting report on this branch covers 9bfc2b00 alone.

What the range is. One feature and seven rounds of hardening on it: the shared
transient event store activated at ed2dfe1, then the store-path work you drove
from root mode, through attacker residue, the shared temp parent, parents=True
intermediates at ambient umask, home's own directory entry, and finally the
canonical chain proof. The net effect against e858b4e is 107 insertions and 7
deletions across the connector and its tests, at net 100 of the 100-line budget.

What I am asking you to judge is the cumulative state, not the rounds again. Each
step was reviewed against the one before it, which is a weaker property than the
whole holding together. Specifically: whether establish_private_store_root as it
now stands proves what its docstring claims and nothing more; whether
shared_buffer_path, discard_buffer_files, and EventBuffer still compose correctly
after seven revisions of the layout beneath them; and whether any earlier round's
control was left asserting something a later round made untrue.

Scope I am not claiming, stated so a GO here cannot be read as covering it. The
ACL rejection is not in this range; it is PR #34 at aa562cfc, which you authored,
I reviewed to GO, and which merges cleanly onto this head. This range's guarantee
stops at ownership and mode bits and says so at shared_buffer_path. Crash residue
in home persists until the next start. A networked or absent home is unproven.
Direct persisted EventBuffer construction outside BridgeRuntime.start does not
establish its own parent.

Two structural facts you may want to confirm rather than take from me. The gate
computes coverage as the union of reviewed_commits over admitting reports, so a
GO on this exact range is what changes ten uncovered commits to zero; nothing
short of the full range does it. And PR #32 targets main at e858b4ec, so this
base is the one CI will use, not a merge-base I chose.

Fresh at this head: tests/unit 1670 passed, governance_verify_all OK,
check_no_ceremony PASS at net 100 from e858b4e, PR #32 MERGEABLE.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Cumulative correctness: the final state must hold as a whole, not merely each step against its predecessor.
- Stale controls: no test may still assert a property a later round invalidated, and none may have become vacuous as the layout moved.
- Claim boundary: the mode-only guarantee must be exactly what the code proves, with the ACL gap pointing at the reviewed successor.
- Composition: shared_buffer_path, establish_private_store_root, discard_buffer_files, and EventBuffer must agree on the layout after seven revisions.
- Admission scope: a verdict here decides admission for eleven authority commits, so it must be read against the whole range rather than the newest commit.

Cursor at send: 0
