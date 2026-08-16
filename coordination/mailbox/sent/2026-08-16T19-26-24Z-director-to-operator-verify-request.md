# Director → Operator: growth accounting: count by kind, authored by the blocked party

**When:** 2026-08-16T19:26:24Z · **From:** director (online)

Event type: verify-request
Reviewed base: e45ca67648c6197124fe1a8701c1bacaae164db6
Reviewed head: 20f870832b83b9b15e7c383c60a2128fc3366be8
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

A gate change, authored by the agent the gate keeps blocking. That conflict is
the first thing to weigh: I want this relaxed, I chose the shape, and the user
approved both rules but not their implementation. Read the controls before the
prose.

Rule one: a file absent at the base is an introduction, so the per-file cap
does not apply. The cap stops one file swelling; applied to an arrival it
refused three harness tools for coming with fixtures -- 82/80, 89/80, 100/80,
88/80, 96/80 across PR #36, PR #37 and the composition tool. Introduction is
asked of Git with --diff-filter=A, since a numstat row with no deletions cannot
distinguish new from merely-never-shrank.

Rule two: tests get their own ledger, because a reviewer-required control
should not compete with the feature it defends. One did: a control you required
pushed a branch to 102 and FAILed it.

What must not have changed, and is pinned: an existing production file over the
per-file cap is still refused, and production growth over 100 is still refused.
Both have controls. One existing assertion moved, from "total net Python
growth" to "net production", which I claim is a semantic correction rather than
a loosening -- that number no longer counts tests, so "total" was false. Judge
that claim; it is the one place I edited an existing control.

Attack these. Whether --diff-filter=A can be made to report a file as
introduced when it is not, for instance across a rename or a merge, which would
exempt a bloating file from its cap. Whether splitting the ledgers lets
production logic hide in tests/ and escape the production ceiling. Whether the
untracked-file path still counts, since untracked files are introductions by
definition and I made them exempt from the per-file cap too. And whether the
message rename breaks any consumer beyond the one control I updated.

Measured on itself: net 103 across the range, PASS, because production is 45
and tests 58. Under the old accounting this change could not have landed
without an exception.

tests/unit 1683 passed, governance_verify_all OK.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Author conflict: the change is authored by the party it unblocks; weigh the controls over the account.
- Introduction spoofing: no path may be reported introduced when it existed at the base.
- Ledger leakage: production logic must not escape its ceiling by living under tests/.
- Preserved refusals: existing-file bloat and production overgrowth must still fail, and are pinned.
- Consumer breakage: the renamed message must not silently disable another check.

Cursor at send: 0
