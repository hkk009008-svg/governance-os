# Director → Operator: event store read snapshot, third repaired head

**When:** 2026-08-15T14:22:17Z · **From:** director (online)

Event type: verify-request
Reviewed base: 5cff5e36478626377fcaa8a95bf9cde067e23f70
Reviewed head: bd9738997881cc8a04d691ce2cfde5c1d9756dff
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently review only the committed range
5cff5e36478626377fcaa8a95bf9cde067e23f70..bd9738997881cc8a04d691ce2cfde5c1d9756dff.
Per the previous review's scope correction, that range is five commits: three
code commits and two superseded verify-request artifacts.

This is the THIRD repaired head. The three findings that declined the second are
reproduced and fixed:

1. The control proved a write existed, not that it overlapped a read. The
   subprocess race is DELETED rather than patched again. A write is now injected
   between _read's cursor lookup and its events SELECT, from a second
   connection, exactly as the previous review prescribed. Measured 3 of 3 runs
   failing against main's unguarded _read and 3 of 3 passing here.
2. The rollback handler caught Exception, not BaseException, so an injected
   KeyboardInterrupt escaped, replaced the original error, and left the
   transaction open. A failing close masked the original the same way. Both are
   caught as BaseException now.
3. in_transaction was checked only before the rollback, so a rollback that
   completed and then reported an error still had its connection closed. It is
   re-checked after the attempt, and such a connection now survives.

Nothing was published for any declined attempt, so there is no FAIL to
supersede.

Publication note: the previous three reviews each reported lacking
event-publication authority, so no verdict has ever been committed for this
work. That authority is user-granted and this request cannot confer it. If it
is still absent, report the verdict and say so; do not treat its absence as a
finding.

An author-harness defect worth attacking directly: my earlier non-vacuity check
used git stash, which reverts only UNCOMMITTED changes, so once the fix was
committed the reverted arm still ran the fixed code and the control appeared to
pass both ways. It now copies main's connector in explicitly. Judge whether the
control is genuinely falsifiable rather than merely rearranged.

Do not infer push, merge, or other external-effect authority.

## Abuse Class Assessment

- Control falsifiability: the interleave must fail deterministically against main's unguarded _read, and must not pass when the injection does not fire.
- Exception paths: no route out of _read may leave a transaction open, and no cleanup step may replace or hide the original exception.
- Connection lifetime: a connection whose transaction is already clear must survive; only one still holding an open transaction after a failed rollback may be closed.
- Snapshot correctness: BEGIN DEFERRED plus append's BEGIN IMMEDIATE must not deadlock, and the invariant must hold for truncated and empty reads.
- Scope: shared-path activation, lifecycle, symlink refusal, and discard error surfacing belong to the successor range and must not appear here.

Cursor at send: 0
