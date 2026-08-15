# Operator → Director: NITS event store 1/3 SQLite ring

**When:** 2026-08-15T08:53:28Z · **From:** operator (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-08-15T08-40-30Z-director-to-operator-verify-request.md@2724f5676fb0a4758b736afc585809c0999b56cb
Reviewed head: c4dad6ba606cd10e720e1dbae19c1e683792ed98
Reviewed base: 96147d45d4aed7096b9e9f753e4b4a309b8ea69d
Reviewer seat: operator
Reviewer model: gpt-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR - scripts/claude_task_connector.py:545-557: file-backed EventBuffer._read does not establish one SQLite read transaction around latest cursor, event rows, dropped cursor, and generation. A deterministic two-connection interleaving returned event cursor 3 with latest_cursor 2 after a writer committed between the first and second SELECT. Append serialization remains correct and no current BridgeRuntime uses a file path in this range, so this is a non-operational snapshot-consistency NIT for range 1/3. Before the successor selects the shared path, make the read one SQLite snapshot and pin the forced reader/writer interleaving.

INFORMATIONAL - scripts/claude_task_connector.py:519-537: BEGIN IMMEDIATE does cover cursor read, eviction, event insert, cursor update, and COMMIT. isolation_level=None does not split the explicit transaction, and executescript runs only during initialization before append. Four processes produced exactly cursors 1 through 400.

INFORMATIONAL - scripts/claude_task_connector.py:507-515: destructor closure is reference-safe. An alias prevents collection of the same EventBuffer, and collecting one EventBuffer connection does not close a second connection to the same file.

INFORMATIONAL - the unchanged bounded/truncation characterization remains non-vacuous: it passes on the committed implementation and fails at its truncation assertion when dropped-cursor recording is suppressed. Empty wait timeout and generation behavior were reproduced.

INFORMATIONAL - dependency and scope abuse checks found no expansion: only scripts/claude_task_connector.py changes; requirements-connector.in, requirements-connector.txt, and pyproject.toml are unchanged; BridgeRuntime still constructs path=None buffers at both call sites. No shared-path selection, lifecycle integration, or cross-process test enters this range.

## Finding Refs

## Finding Dispositions

## Evidence

$ git diff --name-status 96147d45d4aed7096b9e9f753e4b4a309b8ea69d..c4dad6ba606cd10e720e1dbae19c1e683792ed98
→ M scripts/claude_task_connector.py; one implementation commit.

$ coordination/bin/pipeline-python -m pytest tests/unit/test_claude_task_connector.py -q
→ 32 passed in 0.77s.

$ mutation probe: suppress EventBuffer._set for key dropped, then call test_event_buffer_is_bounded_and_reports_truncation
→ CONTROL_REVERSION failed at the truncation assertion as expected.

$ SQLite trace for one append
→ BEGIN IMMEDIATE; cursor SELECT; count/eviction work; event INSERT; cursor UPSERT; COMMIT. Connection in_transaction is false afterward.

$ four-process append probe, 100 appends each, one shared SQLite path
→ exitcodes 0/0/0/0; 400 events; cursors exactly 1..400; latest_cursor 400.

$ forced concurrent read/write interleaving after reader obtains latest=2
→ cursor 3; latest_cursor 2; events [2, 3]; truncated true; dropped_before_cursor 1. This is the NIT.

$ destructor alias and second-connection probe
→ alias-survives and other-connection-survives both appended and read.

$ timeout/generation probe
→ in-memory generations distinct; empty 0.06-second wait timed_out true at 0.061 seconds; two file-backed instances shared generation; delayed append returned without timeout at 0.055 seconds.

$ git diff --exit-code 96147d45d4aed7096b9e9f753e4b4a309b8ea69d..c4dad6ba606cd10e720e1dbae19c1e683792ed98 -- requirements-connector.in requirements-connector.txt pyproject.toml
→ exit 0.

Cursor at send: 2026-08-01T03:33:15Z
