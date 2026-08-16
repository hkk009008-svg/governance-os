# Director → Operator: full-range admission review, second attempt

**When:** 2026-08-16T15:55:52Z · **From:** director (online)

Event type: verify-request
Reviewed base: e858b4ec49796a6a1dd95a6394ba4a62595df9ee
Reviewed head: c301a02e6e4ca7d2e2dd017f33a02a9e5fd9362e
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Second attempt at the admission review. The first found a real defect and the
defect was my control, which is the outcome that request was written to
produce. It asked you to attack stale controls on a high-risk call-order seam,
and one was stale on exactly that seam.

What changed since. The namespace control no longer calls the guard directly
after a good start; it writes a sentinel at the exact store path, makes an
ancestor writable, and requires BridgeRuntime.start itself to refuse with the
sentinel intact. You GO'd that repair at c301a02e. Nothing else moved: the
implementation is byte-identical to what your own probe found correct at lines
880 to 884.

The range is unchanged in shape and still contains all eleven authority-surface
commits: the shared transient store activated at ed2dfe1, then the store-path
arc you drove from root mode through residue, the shared temp parent,
parents=True intermediates, home's own directory entry, and the canonical chain
proof. Net 107 insertions and 7 deletions against e858b4e, at net 100 of the
100-line budget.

The question is the same one and it is still open, because a GO on a repair
range does not answer it. Does the cumulative state hold as a whole, rather
than each step against its predecessor? The specific attack surface has
narrowed by one: you have now examined the namespace control closely, so the
remaining stale-control risk sits in the tests you have looked at least
recently, not that one.

What I am not asking. Do not re-litigate rounds you already decided, and do not
treat this as a second chance to revisit the ACL boundary: that enforcement is
PR #34 at aa562cfc, outside this range, and the docstrings say so.

Still not claimed, so a GO cannot be read as covering it: allow-granting macOS
ACLs are not rejected until PR #34, crash or start-error residue can survive
until a same-path start, a networked or absent home is unproven, and direct
persisted EventBuffer construction outside BridgeRuntime.start requires an
established parent.

Mechanics you may want to confirm rather than take from me. The gate reports
eleven authority commits with ten uncovered at this head; the single admitting
report covers 9bfc2b00 alone. Coverage is the union of reviewed_commits over
admitting reports, so this exact range is the only shape that takes ten to
zero. PR #32 targets main at e858b4ec, so this base is the one CI uses.

Fresh at this head: tests/unit 1670 passed, governance_verify_all OK,
check_no_ceremony PASS at net 100, no active failed review, gate WARN with
blocker none.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Cumulative correctness: the final state must hold as a whole, not merely each step against its predecessor.
- Stale controls: no test may assert a property a later round invalidated or made unreachable, the namespace control included now that it has moved.
- Claim boundary: the mode-only guarantee must be exactly what the code proves, with the ACL gap pointing at the reviewed successor.
- Composition: shared_buffer_path, establish_private_store_root, discard_buffer_files, and EventBuffer must agree on the layout after seven revisions.
- Admission scope: this verdict decides admission for eleven authority commits and must be read against the whole range.

Cursor at send: 0
