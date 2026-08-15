# Director → Operator: event store read snapshot fix, second repair

**When:** 2026-08-15T13:59:35Z · **From:** director (online)

Event type: verify-request
Reviewed base: 5cff5e36478626377fcaa8a95bf9cde067e23f70
Reviewed head: f07f34bd31171edf076cc8cf138a874f0826966f
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently review only the committed range
5cff5e36478626377fcaa8a95bf9cde067e23f70..f07f34bd31171edf076cc8cf138a874f0826966f, two commits, which wrap
EventBuffer._read in one snapshot and close the transaction on every exit path.

This is the SECOND repaired head for this range. The first repair was declined:
_read suppressed every rollback failure without checking in_transaction, so with
COMMIT and ROLLBACK both denied it left the transaction open and wedged the next
read; and the regression control discarded the writer's exit status, so it
passed against the unguarded _read when a fake writer exited 17. Both are
reproduced and fixed here. Nothing was published for either declined attempt, so
there is no FAIL to supersede.

The reviewer must be gpt-family; scripts/ is an authority surface.

Publication note: the previous review reported it lacked event-publication
authority for this range. That is a user-granted external effect and this
request cannot confer it. If it is still absent, report the verdict without
publishing and say so, rather than treating the absence as a finding.

Attack the same two places again rather than trusting the repair. For the
rollback path, judge whether closing the connection is the right response or
merely a different failure, whether in_transaction can be stale, and whether any
route still leaves a transaction open. For the control, judge whether asserting
exit status and observed > 1 is sufficient, or whether a writer that starts,
writes one event and dies still leaves it trivially green.

Do not infer push, merge, or other external-effect authority.

## Abuse Class Assessment

- Exception paths: every route out of _read must leave no open transaction, including a failing COMMIT, a failing ROLLBACK, a validation error, and a JSON decode error.
- Error masking: the original exception must survive the cleanup path; judge whether closing the connection can hide the cause or convert a recoverable fault into an unrecoverable one.
- Snapshot correctness: BEGIN DEFERRED plus append's BEGIN IMMEDIATE must not deadlock, and the invariant must hold for truncated and empty reads.
- Control honesty: the regression must fail against the unguarded _read under a real writer, and must not pass when no concurrent write occurred.
- Scope: shared-path activation, lifecycle, symlink refusal, and discard error surfacing belong to the successor range and must not appear here.

Cursor at send: 0
