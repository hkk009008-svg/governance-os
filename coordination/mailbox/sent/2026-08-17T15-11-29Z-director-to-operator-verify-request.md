# Director → Operator: range A transitional growth ceiling

**When:** 2026-08-17T15:11:29Z · **From:** director (online)

Event type: verify-request
Reviewed base: 86146d1f0c4051d416ef683696cc07ea9e75bda3
Reviewed head: 7b13b4b17b3dbfd9163fc179d556288b9aec5e0d
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Range A of the three-range bootstrap you ruled. It raises the aggregate Python
ceiling from 100 to 181 and contains no exception logic at all.

WHY A CEILING IS BEING RAISED, since that is the thing to be suspicious of.
The reviewed exception mechanism that makes the aggregate a trigger rather than
a wall cannot be built under that ceiling and may not except itself. Measured,
the complete corrected mechanism is net 181; the ceiling is 100; so
check_no_ceremony exits 1 on its own growth and forbids the change that would
make exceeding it reviewable. An absolute aggregate ceiling is self-entrenching.

181 IS THE MEASURED SIZE OF RANGE B, not a round figure and not a design
threshold. You ruled that a number chosen for convenience becomes a steady
state nobody restores, so the control pins both edges: 181 passes, 182 fails,
no headroom. It was resized from 166 when range B moved its tests into their
own file -- the per-file net cap is unwaivable and refused the range at net 96
against 80, and an arriving file is exempt from that cap, so the split is the
exemption working rather than a way around it. That resize is exactly the
remeasure-if-B-moves rule you required, and it happened.

TWO EXISTING ASSERTIONS were rewritten to derive their numbers from the
constant instead of hardcoding 100. They test the mechanism rather than the
value, which is why range C does not need to touch them.

WHAT TO ATTACK. Whether the envelope control genuinely forbids headroom or only
appears to, since it asserts on _python_growth_violations rather than on a real
range. Whether raising a hard ceiling at all is the wrong answer to a
self-entrenchment finding, and some fourth option exists that neither of us
saw. Whether the two rewritten assertions lost anything by deriving from the
constant -- I believe they now test more, but I am their author. And whether
this range can be merged and then abandoned, which is the failure mode the
whole three-range shape exists to prevent.

NOT CLAIMED. That 181 is a good permanent value; it is a transitional envelope
and range C restores 100. That this range is useful alone; it is not, and it
must not merge unless B and C merge with it.

VERIFICATION at this head: tests/unit 1706 passed, check_no_ceremony exit 0,
governance_verify_all exit 0.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Abandoned broadening: a raised ceiling that merges without its restoration becomes the new normal, which is why A, B and C are all committed and reviewable before any merge.
- Silent absorption: an envelope with headroom would admit later work nobody sized it for, so the pin is exact at both edges.
- Cap laundering: the per-file net, per-file additions, rename and untracked rules are untouched here and remain unconditional.
- Value anchoring: a transitional number must not be argued into a permanent one on the strength of having been used once.

Cursor at send: 0
