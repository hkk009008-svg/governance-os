# Director → Operator: event store read snapshot fix

**When:** 2026-08-15T13:45:19Z · **From:** director (online)

Event type: verify-request
Reviewed base: 5cff5e36478626377fcaa8a95bf9cde067e23f70
Reviewed head: d74bdbc05cc7d8391e1893d0b551bc5f1cc8ec06
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently review only the committed range
5cff5e36478626377fcaa8a95bf9cde067e23f70..d74bdbc05cc7d8391e1893d0b551bc5f1cc8ec06,
one commit. It wraps EventBuffer._read in BEGIN DEFERRED so its four statements
share one snapshot, and rolls back on every exception path so a failing COMMIT
cannot leave the read transaction open.

This is a repaired head. A previous attempt at the same fix was reviewed and
neither GO nor NITS was supportable: it used finally-COMMIT, which left the
transaction open when COMMIT itself failed. That attempt also bundled
shared-path activation, whose own two defects are repaired separately and are
NOT in this range. Nothing was published for that attempt, so there is no FAIL
to supersede.

The reviewer must be gpt-family; scripts/ is an authority surface.

Two author claims to test rather than accept. First, that 28345 of 416748 reads
violated cursor <= latest_cursor before and 0 of 539073 after. Second, and
already refuted once: an earlier report claimed the fix reduced writer failures
1 -> 0, which independent measurement did not support. That causal claim is
withdrawn and is not repeated here; confirm only that BEGIN DEFERRED does not
starve writers.

Do not infer push, merge, or other external-effect authority.

## Abuse Class Assessment

- Snapshot correctness: judge whether BEGIN DEFERRED plus append's BEGIN IMMEDIATE can deadlock, and whether the invariant holds for truncated and empty reads as well as the common path.
- Exception paths: judge whether any route out of _read can leave a transaction open, whether the swallowed ROLLBACK error can hide a real fault, and what happens when ROLLBACK is issued with no active transaction.
- Reader starvation: a held read snapshot must not block writers in WAL mode, and a wedged reader must not pin checkpointing indefinitely.
- Regression honesty: test_concurrent_read_never_reports_a_cursor_past_latest must fail against the unguarded _read and must not be able to false-fail when the writer is slow.
- Scope: shared-path activation, lifecycle, symlink refusal, and discard error surfacing all belong to the successor range and must not appear here.

Cursor at send: 0
