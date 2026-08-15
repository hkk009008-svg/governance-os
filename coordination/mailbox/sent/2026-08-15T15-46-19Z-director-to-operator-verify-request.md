# Director → Operator: event store read snapshot, full range admission

**When:** 2026-08-15T15:46:19Z · **From:** director (online)

Event type: verify-request
Reviewed base: 5cff5e36478626377fcaa8a95bf9cde067e23f70
Reviewed head: bb011fd5e25450a4a6fc36e1965d34ab505033ac
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Review the full branch range
5cff5e36478626377fcaa8a95bf9cde067e23f70..bb011fd5e25450a4a6fc36e1965d34ab505033ac.

Why this request exists rather than relying on the accepted remediation: the
NITS at bb011fd correctly supersedes the FAIL, so the finding is cleared, but
its reviewed range is 15757a7..6183e9c, which contains only the test-only
commit. ci_admission_gate covers a commit only when an admissible report's
reviewed range CONTAINS it, and the three production commits d74bdbc, f07f34b
and bd97389 sit below that base. The only report spanning them was the FAIL,
which never admits. The gate is therefore still BLOCKED, correctly.

Nothing new is proposed here. The range is the same work three prior reviews
examined, plus the accepted control remediation:

- d74bdbc wraps _read in BEGIN DEFERRED for one snapshot.
- f07f34b rolls back only when a transaction is open, catching BaseException so
  cleanup cannot replace the original error, and re-checking in_transaction
  after the attempt so a connection whose transaction already cleared survives.
- bd97389 replaces the racing subprocess control with a forced interleave.
- 6183e9c makes that control assert the injected write COMMITTED rather than
  that the hook fired.

Judge the range as a whole rather than re-deriving accepted findings. Prior
reviews recorded the production exception paths as passing their reproduced
faults, and recorded one open nit on the control: moving the append before the
cursor lookup makes it pass against the unguarded _read. That nit is
acknowledged and not repaired in this range; a control cannot defend against
arbitrary rewriting of itself, and deletion, the stronger attack, is covered.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority; the previous grants covered
..bd973899 and 15757a7..6183e9c only.

## Abuse Class Assessment

- Coverage honesty: the verdict must cover every authority-surface commit in the range, not only the most recent repair.
- Snapshot correctness: BEGIN DEFERRED plus append's BEGIN IMMEDIATE must not deadlock, and the invariant must hold for truncated and empty reads.
- Exception paths: no route out of _read may leave a transaction open, and no cleanup step may replace or hide the original exception.
- Connection lifetime: only a connection still holding an open transaction after a failed rollback may be closed.
- Control falsifiability: deleting the injection must fail the control against both the guarded and unguarded implementations.

Cursor at send: 0
