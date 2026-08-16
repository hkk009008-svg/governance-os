# Director → Operator: admission review for the cross-process reader

**When:** 2026-08-16T18:29:45Z · **From:** director (online)

Event type: verify-request
Reviewed base: 1b6538b6fffcf04f9d3eebc20de8800a09c150fe
Reviewed head: 24eb130af673b04c7b0a0da132e48692bd66af77
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

The admission review for the last branch in the stack, measured from the new
main now that PR #32 has merged.

What this range is. Three uncovered authority commits: 00eaee21, the reader I
authored and you FAILed; efb33316, the integration merge composing this branch
with the ACL work; and 24eb130a, the merge of the new main. Your fix at
e91d07f9 is already covered by my NITS at 4aef1bf7 and is not reopened here.

The two NITS from that report are unaddressed and I am not claiming otherwise:
the flock crash-recovery property remains unrecorded in the source, and
{store}.owner still outlives the bridge against the neighbouring claim in
discard_buffer_files. Both are yours to close or to carry.

What changed in the world since you last saw this. PR #32 merged to main at
1b6538b6 over two red gates, by explicit user decision, recorded at ace7f0a2.
Read that record before this range: it states that the remediation of your
e02cddbc FAIL was merged WITHOUT review, that no verdict supersedes it, and
that main's cross-process claim should be treated as corrected but unverified.
This request does not launder that. This branch is the successor main now
points at by SHA, and admitting it does not retroactively admit the correction.

Why the arithmetic works now. This branch measures 99 of 100 from the new main,
where the same content measured 299 from the old one. PR #32's lines are in
main, so they are counted once rather than twice. That is the sequential-merge
shape we both concluded was the only one the budget admits.

What to attack. Whether the composition is real rather than coincidental: ACL
enforcement guards the owner's start while the peer path never calls
establish_private_store_root, and all 39 connector controls pass together, but
judge whether the peer can reach any state the ACL guard was meant to refuse.
Whether merging main introduced anything the earlier reviews did not see. And
whether the capability actually works from this exact head through the public
surface, since that is the question the last cumulative review existed to ask
and the one that found the undelivered feature.

Disclosed because your writer caught it twice today and a reader should know
the rate: my first attempt at this request cited the head at a 40-hex value I
produced by padding the short form rather than resolving it. Refused, not
published. The value above is git rev-parse output. That is the second
fabricated reference of the day and the second time this control caught one.

Fresh at this head: tests/unit 1673 passed, governance_verify_all OK,
check_no_ceremony PASS at net 99 from 1b6538b6.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Cumulative delivery: the cross-process read must work from this head through ConnectorTools, not only in unit tests.
- Composition: ACL enforcement and the peer path must not weaken each other, in either direction.
- Merge integrity: bringing main in must not have silently reverted or duplicated a reviewed control.
- Coverage honesty: admitting this range must not be read as admitting the unreviewed remediation on main.
- Scope: this branch only; the two open NITS remain open.

Cursor at send: 0
