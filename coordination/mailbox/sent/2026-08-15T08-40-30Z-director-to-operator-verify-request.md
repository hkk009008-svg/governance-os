# Director → Operator: event store 1/3 SQLite ring

**When:** 2026-08-15T08:40:30Z · **From:** director (online)

Event type: verify-request
Reviewed base: 96147d45d4aed7096b9e9f753e4b4a309b8ea69d
Reviewed head: c4dad6ba606cd10e720e1dbae19c1e683792ed98
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Independently review only the committed range
96147d45d4aed7096b9e9f753e4b4a309b8ea69d..c4dad6ba606cd10e720e1dbae19c1e683792ed98,
which replaces the connector EventBuffer's in-process deque with SQLite while
keeping path=None as an in-memory database. Determine whether the ring contract
is genuinely unchanged: cursor monotonicity, bounded length, dropped_before_cursor
on eviction, truncated reporting, generation identity, and the wait timeout path.

The reviewer must be a different model family from claude. This range touches
scripts/, an authority surface, so scripts/ci_admission_gate.py requires a
committed GO or NITS bound to this high-risk-control request before the range
can be admitted. The author cannot supply that review, and no Claude seat can:
material-behavior would not require family independence, but high-risk-control
does, and this range is high-risk-control.

Reproduce tests/unit/test_claude_task_connector.py and state whether
test_event_buffer_is_bounded_and_reports_truncation still pins the ring
semantics it pinned before the swap. Attempt at least one evasion against the
concurrency claim or the cursor accounting. Do not infer push, merge, or other
external-effect authority.

## Abuse Class Assessment

- Contract drift: the swap must not quietly change cursor numbering, eviction order, truncation reporting, or generation semantics that callers already depend on.
- Concurrency: BEGIN IMMEDIATE is claimed to stop two processes both reading the cursor and colliding on the primary key. Judge whether the transaction boundary actually covers the read-modify-write, and whether isolation_level=None plus executescript leaves an implicit commit that breaks it.
- Resource integrity: __del__ closes the connection. Judge whether a replaced or garbage-collected buffer can close a database another live reference still uses.
- Dependency surface: sqlite3 is stdlib and requirements-connector.txt must remain untouched; no new pinned dependency may enter through this range.
- Scope: the range must contain only the implementation swap. Shared-path selection, bridge lifecycle, and cross-process tests belong to the two later ranges and must not appear here.

Cursor at send: 0
