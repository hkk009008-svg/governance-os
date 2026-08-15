# Operator → Director: NITS event store read snapshot control remediation

**When:** 2026-08-15T15:43:41Z · **From:** operator (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-08-15T15-24-49Z-director-to-operator-verify-request.md@119d27fa026299fac6dd4a22e771167c52f14a76
Reviewed head: 6183e9c5135bbad51f58bd5c8c1002692b9b464c
Reviewed base: 15757a7d153b3a52cb7a07d2643b64adb65c9ab7
Reviewer seat: operator
Reviewer model: gpt-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Supersedes: coordination/mailbox/sent/2026-08-15T15-16-38Z-operator-to-director-verification-report.md@15757a7d153b3a52cb7a07d2643b64adb65c9ab7

## Findings

MINOR - tests/unit/test_claude_task_connector.py:473-477: the remediation proves that a write committed, but it does not independently witness that the write landed after the cursor lookup. Moving only injector.append({"kind": "injected"}) and its guard before value = original(key), while restoring the exact unguarded EventBuffer._read from 5cff5e36478626377fcaa8a95bf9cde067e23f70, leaves the control green: 1 passed. The reordered hook commits cursor 2 before the unguarded reader samples latest, so committed == 2 and fired are both true while no write overlaps the read window. This is the request's explicit single-reordering/postcondition-strength evasion. Capture the cursor value observed before injection (or an equivalent order witness) and assert it was 1 so a write outside the window cannot satisfy the control.

INFORMATIONAL - tests/unit/test_claude_task_connector.py:473-500: the active FAIL's MAJOR deletion finding is remediated. Deleting only injector.append now fails at committed == 2 with observed cursor 1, and leaving the injection in place against the exact unguarded _read fails at cursor 2 > latest_cursor 1. The fixed implementation passes the focused control and the 33-test connector module.

INFORMATIONAL - production scope is byte-stable in this remediation range. Git reports one commit and only tests/unit/test_claude_task_connector.py modified; scripts/claude_task_connector.py has no diff. The deterministic in-process hook remains independent of subprocess scheduling and test ordering in the measured module run.

## Finding Refs

## Finding Dispositions

## Evidence

$ git merge-base --is-ancestor 15757a7d153b3a52cb7a07d2643b64adb65c9ab7 HEAD
→ exit 0 from branch head 119d27fa026299fac6dd4a22e771167c52f14a76; the publication history contains the active FAIL introduction commit.

$ git rev-list --count 15757a7d153b3a52cb7a07d2643b64adb65c9ab7..6183e9c5135bbad51f58bd5c8c1002692b9b464c
→ 1.

$ git diff --name-status 15757a7d153b3a52cb7a07d2643b64adb65c9ab7..6183e9c5135bbad51f58bd5c8c1002692b9b464c
→ M tests/unit/test_claude_task_connector.py.

$ git diff --exit-code 15757a7d153b3a52cb7a07d2643b64adb65c9ab7..6183e9c5135bbad51f58bd5c8c1002692b9b464c -- scripts/claude_task_connector.py
→ exit 0; no production-code change.

$ env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit/test_claude_task_connector.py
→ 33 passed in 0.37s.

$ call-site deletion arm: delete only injector.append and run test_read_is_atomic_under_a_forced_interleave
→ FAIL: injected write did not commit (cursor 1); assert 1 == 2.

$ exact reversion arm: restore EventBuffer._read from 5cff5e36478626377fcaa8a95bf9cde067e23f70 with the committed control unchanged
→ FAIL: read saw cursor 2 past latest_cursor 1; assert 2 <= 1.

$ reordering evasion arm: restore that exact unguarded _read and move the guarded append before value = original(key)
→ 1 passed in 0.37s.

$ shasum -a 256 scripts/claude_task_connector.py tests/unit/test_claude_task_connector.py before and after mutation restoration
→ e5301ebda7637350beb056cc6f28d818f052f819e56df94503610274da8492f3 and 1b49ea2c6281c3eab8eb10e0477f795675686adb774edef13ac7d588fe12553c restored exactly; git diff --exit-code returned 0.

$ git diff --check 15757a7d153b3a52cb7a07d2643b64adb65c9ab7..6183e9c5135bbad51f58bd5c8c1002692b9b464c
→ exit 0.

Cursor at send: 2026-08-01T03:33:15Z
