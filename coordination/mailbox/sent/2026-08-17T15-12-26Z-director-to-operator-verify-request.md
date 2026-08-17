# Director → Operator: range C restore the aggregate trigger

**When:** 2026-08-17T15:12:26Z · **From:** director (online)

Event type: verify-request
Reviewed base: 9406c8ad86b0c3efcd7ec4e03ae580e946889d65
Reviewed head: d54a26f55f380f03fa371b2246f3ed5e9ee8045e
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Range C, and the point of the whole sequence. The transitional envelope is
removed and 100 returns as the design trigger. Net -24: a restoration range
should remove more than it adds.

WHY 100 AND NOT SOMETHING ELSE. You ruled it and I agree with the reasoning.
The evidence showed that treating 100 as an absolute wall is defective; it did
not show that 100 is the wrong number. Every figure I could propose would be
anchored on what I happened to build today, which is the wrong way to choose a
policy constant. Section 4.6 keeps 100 as the trigger and adds reviewed
proportionality above it, and after this range that is what exists.

The envelope control is deleted with the envelope, since it pinned a
transitional value and outlives nothing. The two assertions that once
hardcoded 100 were rewritten in range A to derive it from the constant, so they
need no change here and continue testing the mechanism rather than the value.

WHAT TO ATTACK, and this is the range where I most want a hostile reading.
Whether the end state is genuinely identical in behaviour to main plus the
mechanism -- that is, whether A's broadening leaves any residue after C beyond
the mechanism itself. Whether deleting the envelope control removes a property
worth keeping at 100. Whether the mechanism still refuses everything it refused
before, now that the trigger it sits above has moved back down. And whether
this range could be silently skipped: it is the last of three, so if anything
makes it easy to merge A and B and stop, say so, because that is precisely the
abandoned steady state the shape exists to prevent.

NOT CLAIMED. That the sequence is safe to merge out of order. That A or B may
merge without C committed and reviewed, which was your explicit condition.

VERIFICATION at this head: tests/unit 1707 passed; check_no_ceremony exit 0;
governance_verify_all exit 0; end state MAX_PYTHON_NET_GROWTH = 100.

COMPOSITION, measured rather than asserted: A is an ancestor of B, B is an
ancestor of C, and C's committed constant is 100.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Skipped restoration: the transitional ceiling must not survive the sequence, and this range is the only thing that removes it.
- Residue: the end state must differ from the start state only by the mechanism, never by a loosened rule left behind.
- Lost control: deleting the envelope control must not remove a property that still applies at the restored trigger.
- Ordering: merging out of order would leave either an unusable mechanism or an unrestored ceiling.

Cursor at send: 0
