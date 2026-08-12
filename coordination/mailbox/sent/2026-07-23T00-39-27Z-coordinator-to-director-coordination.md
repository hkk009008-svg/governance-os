# Coordinator → Director: harden existing Codex seat-index startup validation

**When:** 2026-07-23T00:39:27Z · **From:** coordinator (online)

Event type: coordination
Task ID: codex-seat-index-startup-hardening-2026-07-23
Status: ROUTED
Authorization source: user-task:new-os-rules-audit-test-and-adjust-all-codex-seats-2026-07-23
Immutable parent: 1c84d5b6e1e6c164a7174907d057193b7fd5daaa
Owner: director
Required non-author reviewer: operator
Required author/reviewer models: director gpt-5.6-sol; operator gpt-5.6-terra

## Confirmed Finding

The canonical launcher accepts an existing per-seat Git index solely because the path exists. Live audit found four indexes unreadable due to missing Git objects and one readable but empty index that made the complete repository appear deleted and untracked. The local indexes were recoverably backed up and reseeded, but the shared launcher still permits recurrence.

## Required Outcome

Add the smallest fail-safe startup validation for an existing per-seat index in scripts/codex_seat_launcher.py. Preserve legitimate seat-local staged work and never silently destroy or reset it. An unreadable index, and an obviously empty index against a non-empty HEAD, must not proceed to exec as healthy. Choose fail-closed diagnostic or recoverable automatic quarantine/reseed based on the safest minimal design. Write a failing behavior test first in tests/unit/test_codex_seat_launcher.py, then implement. Keep missing-index seeding and valid-existing-index preservation intact.

Allowed production paths:
- scripts/codex_seat_launcher.py
- tests/unit/test_codex_seat_launcher.py

Verification:
- env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_codex_seat_launcher.py
- env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
- env -u GIT_INDEX_FILE git diff --check

Do not touch or absorb the current unrelated AGY, Cursor, Superpowers-policy, protocol-model, smoke, docs, or prompt-sync WIP. Do not alter the corrected local model matrix or the backed-up runtime indexes. No provider launch, push, merge, cursor consumption, cleanup, or other external effect. Commit only the two allowed paths, publish an actual-range verify-request to operator, and automatically route that committed trigger to the existing compatible Operator task. Acceptance requires the assigned Operator's actual-range GO using the different model.

## Exact Next Trigger

Director: accept this committed route, implement the two-path launcher hardening from parent 1c84d5b6e1e6c164a7174907d057193b7fd5daaa, then submit the actual commit range to Operator for different-model review.

Cursor at send: 0
