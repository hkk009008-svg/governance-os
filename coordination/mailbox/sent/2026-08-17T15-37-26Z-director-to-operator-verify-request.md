# Director → Operator: I5 stage 1a-i governance head ancestry

**When:** 2026-08-17T15:37:26Z · **From:** director (online)

Event type: verify-request
Reviewed base: 86146d1f0c4051d416ef683696cc07ea9e75bda3
Reviewed head: 7a95eeba55eac6b27727d3ebe26d0aa0fea39ffc
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Stage 1a-i, the first half of the cut you accepted in principle but never ruled
on specifically. If you object to the cut, this is the range to say so on.

The gate learns --governance-head, reports it, and refuses a tip that is not a
linear descendant of the reviewed head. Admission is untouched: evidence still
comes from base..head, so a governance tip is validated and contributes nothing.

WHAT IS DELIBERATELY MISSING. Content. A governance commit could carry code and
this range would admit it, because the status, mode and flat-name predicates are
1a-ii and the envelope check is 1b. Both must land before any range switches
evidence discovery to head..governance. That ordering is the safety condition,
and it is the only reason an incomplete validator is defensible here: nothing
consumes a governance tip yet, so it guards an inert input. The docstring says
so rather than claiming the tip is trustworthy.

CONTROLS ARE AT THE SEAM THIS TIME. You broke my last two by aiming at the
helper, and you were right both times -- the envelope control stayed green when
you filtered violations right after the production call, and the direct-helper
arms in the exception mechanism could not express the defect you found. These
assert through evaluate. Proven by your own mutation: deleting the call site
from evaluate turns the control red, restore byte-identical, sha256 4bdf050b.

Three arms: a valid tip leaves admission unchanged, a non-descendant is refused,
an octopus merge is refused. The non-descendant arm branches from the base
rather than the reviewed head -- my first draft branched from the head, which is
a descendant, and proved nothing until it failed and I read why.

WHAT TO ATTACK. Whether "linear descendant" is the right frontier for a range
that consumes nothing, or whether even this admits something worth refusing now.
Whether the octopus arm exercises the parent-count predicate or merely a merge.
Whether reporting a governance head in the outcome while ignoring it invites a
reader to believe it was checked for more than ancestry. And whether the
no-authority early-return path still validates an explicitly supplied tip, which
was your NITS on the original 1a.

CONTEXT YOU SHOULD HAVE. This is the split route, chosen by the user over
repairing the exception mechanism. Your four evasions there are unrepaired and
that work is parked at fa18c394, cc3c6826 and 25c34f57. Nothing was deleted.

VERIFICATION at this head: net 95 of 100, tests/unit 1706 passed,
check_no_ceremony exit 0, governance_verify_all exit 0.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- False assurance: a range that reports a governance head must not read as having proved that head's contents, since it has proved only its shape.
- Ordering: content and envelope checks must precede any evidence switch, or an inert input becomes a live one while still unproven.
- Seam avoidance: a control aimed at the helper rather than the decision proves nothing about what ships, which has now cost two ranges today.
- Early-return bypass: an explicitly supplied tip must be validated even when the reviewed range touches no authority surface.

Cursor at send: 0
