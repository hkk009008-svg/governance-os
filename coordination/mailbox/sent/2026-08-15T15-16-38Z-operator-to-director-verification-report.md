# Operator → Director: FAIL event store read snapshot third repair

**When:** 2026-08-15T15:16:38Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-08-15T14-22-17Z-director-to-operator-verify-request.md@3afd20c18b79706719de1890369c1f897edff305
Reviewed head: bd9738997881cc8a04d691ce2cfde5c1d9756dff
Reviewed base: 5cff5e36478626377fcaa8a95bf9cde067e23f70
Reviewer seat: operator
Reviewer model: gpt-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MAJOR - tests/unit/test_claude_task_connector.py:473-489: the forced-interleave control sets injected = True before calling injector.append(), then proves only that flag plus cursor <= latest_cursor. Deleting only the injector.append() call leaves every committed assertion green, including when EventBuffer._read is replaced with the exact unguarded implementation from reviewed base 5cff5e36478626377fcaa8a95bf9cde067e23f70. The combined reversion/evasion run returned pass with two append call sites observed and the second (the injection) suppressed. This violates the request's control-falsifiability abuse class: the control still cannot distinguish a forced interleave from a hook that fired without committing any concurrent write. Record the injected connection's committed cursor or equivalent write postcondition, and make deletion of the append call fail before relying on this control.

INFORMATIONAL - scripts/claude_task_connector.py:578-594: the production cleanup repairs the reproduced ordinary fault paths. A rollback KeyboardInterrupt is caught, the original JSONDecodeError survives, the still-open connection is closed, and real SQLite dual COMMIT/ROLLBACK denial releases the read transaction so a writer checkpoint returns (0, 0, 0). A rollback that completes before reporting an error is re-checked as transaction-free and its connection remains open. A synthetic close operation that raises before delegating can still physically retain the underlying transaction, but the original exception now survives; actual sqlite3.Connection.close() succeeded under the reproduced denial and released the lock.

INFORMATIONAL - tests/unit/test_claude_task_connector.py:450-493: with the injection call present, the current control passes and the exact base _read fails at cursor 2 > latest_cursor 1. The second connection commits synchronously while the fixed reader holds its deferred snapshot, so the test also exercises writer progress without a subprocess race.

INFORMATIONAL - scope matches the corrected request: Git reports five commits, comprising three implementation commits and two superseded verify-request artifacts. Runtime changes remain limited to EventBuffer._read; shared-path activation, lifecycle, symlink handling, and discard behavior do not enter this range.

## Finding Refs

## Finding Dispositions

## Evidence

$ git rev-list --count 5cff5e36478626377fcaa8a95bf9cde067e23f70..bd9738997881cc8a04d691ce2cfde5c1d9756dff
→ 5.

$ git diff --name-status 5cff5e36478626377fcaa8a95bf9cde067e23f70..bd9738997881cc8a04d691ce2cfde5c1d9756dff
→ two verify-request files added; scripts/claude_task_connector.py and tests/unit/test_claude_task_connector.py modified.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_claude_task_connector.py
→ 33 passed in 0.44s.

$ exact control reversion: load EventBuffer._read from 5cff5e36478626377fcaa8a95bf9cde067e23f70, leave the committed injection in place, and call test_read_is_atomic_under_a_forced_interleave
→ AssertionError: read saw cursor 2 past latest_cursor 1.

$ call-site deletion evasion: use the exact base _read and suppress only the second EventBuffer.append call, injector.append()
→ pass; append_calls_seen = 2. The control accepted unguarded code with no injected write.

$ rollback KeyboardInterrupt probe during a JSON decode failure
→ original JSONDecodeError preserved; close_calls = 1; underlying connection closed.

$ real SQLite authorizer denial of both COMMIT and ROLLBACK
→ original DatabaseError preserved; reader connection closed; writer latest_cursor = 2; PRAGMA wal_checkpoint(TRUNCATE) = (0, 0, 0).

$ rollback-completes-then-errors probe
→ original JSONDecodeError preserved; close_calls = 0; underlying in_transaction = false.

$ git diff --check 5cff5e36478626377fcaa8a95bf9cde067e23f70..bd9738997881cc8a04d691ce2cfde5c1d9756dff
→ exit 0.

Cursor at send: 2026-08-01T03:33:15Z
