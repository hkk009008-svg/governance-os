# Task 1 Report: Enforce Terminal Exact Next Trigger

## Status

DONE

## Summary

Implemented Task 1 from `.superpowers/sdd/task-1-brief.md`.

- Added terminal `Exact Next Trigger` enforcement to `scripts/check_coordination.py`.
- Added the specified TDD regression tests in `tests/unit/test_check_coordination.py`.
- Updated the executable Codex protocol model and protocol/skill docs with the new invariant.
- Created implementation commit `fc1ebd4be5d70c3fe52aae12d4adff6cf8e78897`.

The report file was written after the implementation commit so the commit matches the plan's scoped file list.

## TDD Evidence

### RED

Command:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py -q
```

Observed output:

```text
F..                                                                      [100%]
FAILED tests/unit/test_check_coordination.py::test_future_live_seat_event_without_terminal_trigger_is_fatal
E       assert []
1 failed, 2 passed in 0.30s
```

Meaning: the future live-seat event without a terminal trigger did not produce `missing_end_trigger`, as expected before implementation.

### GREEN

Command:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py -q
```

Observed output:

```text
...                                                                      [100%]
3 passed in 0.29s
```

## Implementation Notes

- `END_TRIGGER_ADOPTION_TS` is `2026-07-07T17-58-38Z`.
- `_has_terminal_next_trigger(text)` accepts the last `Exact Next Trigger` heading only when it is terminal, has non-cursor content below it, and is not followed by another Markdown heading.
- `_check_end_triggers(coord_root, names, trigger_since=END_TRIGGER_ADOPTION_TS)` emits `CoordIssue(kind="missing_end_trigger", severity="FATAL")` for post-adoption mailbox events missing the terminal section.
- `run(...)` calls `_check_end_triggers(...)` immediately after `_check_events(...)`.
- The coordinator skill did not already have a `Pair Operating Contract` heading, so I added a compact matching block there containing the baton-handoff rule and the new terminal-trigger rule.

## Verification

Focused/protocol verification command:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py tests/unit/test_codex_ledger_bridge.py -q
```

Observed output:

```text
................                                                         [100%]
16 passed in 0.37s
```

Smoke command:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Observed summary:

```text
PROJECT SMOKE - governance-OS runtime invariants ... OK
WARNING: 215 stale commit-SHA ref(s) in docs (run .venv/bin/python scripts/check_doc_claims.py --sha-refs):
CEREMONY CHECK - forbid appearance-of-verification-without-substance (ADR-027 / ADR-028)
RESULT: no ceremony detected - every relied-on green is backed by execution.
PLACEHOLDER CHECK - PASS (no unallowlisted tokens).
GO-SCHEMA CHECK - PASS (3 GO report(s) validated; zero violations).
ARCH-FRESHNESS CHECK - ARCHITECTURE.md not in changeset; gate inert (exit 0).
OK
```

The stale-SHA warnings were present before this task and remain unchanged in kind.

## Commit

```text
fc1ebd4be5d70c3fe52aae12d4adff6cf8e78897 feat(protocol): enforce seat end triggers
```

Committed stat:

```text
8 files changed, 168 insertions(+), 1 deletion(-)
create mode 100644 tests/unit/test_check_coordination.py
```

## Changed Files

Committed implementation files:

- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-operator/SKILL.md`
- `docs/protocol/codex/continuation.md`
- `scripts/check_coordination.py`
- `scripts/codex_protocol_model.py`
- `tests/unit/test_check_coordination.py`

Uncommitted report file:

- `.superpowers/sdd/task-1-report.md`

## Concerns

- Existing `ci_smoke.py` stale-SHA warnings remain: 215 stale commit-SHA refs in docs.
- The brief listed `.agents/skills/seat-coordinator/SKILL.md` under Pair Operating Contract updates, but that file did not contain an existing Pair Operating Contract block; I added a minimal one to carry the requested invariant.

## Fix Review Follow-up: Trigger Cutoff Timestamp Normalization

Addressed final-review findings against commit `fc1ebd4`:

- Added boundary coverage for `2026-07-07T17-59-00Z` with colon-form adoption cutoff `2026-07-07T17:58:38Z`; missing terminal trigger is now FATAL.
- Added just-before-adoption coverage for `2026-07-07T17-58-37Z`; missing terminal trigger remains exempt.
- Normalized `_check_end_triggers(...)` timestamp comparison through colon-form ISO strings and documented `missing_end_trigger` in the `CoordIssue.kind` inline comment.

RED command:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py::test_same_hour_event_after_colon_form_trigger_adoption_is_fatal tests/unit/test_check_coordination.py::test_event_just_before_colon_form_trigger_adoption_is_exempt -q
```

Observed output:

```text
F.                                                                       [100%]
FAILED tests/unit/test_check_coordination.py::test_same_hour_event_after_colon_form_trigger_adoption_is_fatal
E       assert []
1 failed, 1 passed in 0.03s
```

GREEN evidence:

```text
$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py::test_same_hour_event_after_colon_form_trigger_adoption_is_fatal tests/unit/test_check_coordination.py::test_event_just_before_colon_form_trigger_adoption_is_exempt -q
..                                                                       [100%]
2 passed in 0.02s

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py -q
.....                                                                    [100%]
5 passed in 0.30s

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py tests/unit/test_codex_ledger_bridge.py -q
..................                                                       [100%]
18 passed in 0.29s

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
PROJECT SMOKE — governance-OS runtime invariants ... OK
WARNING: 215 stale commit-SHA ref(s) in docs (run .venv/bin/python scripts/check_doc_claims.py --sha-refs)
RESULT: no ceremony detected — every relied-on green is backed by execution.
PLACEHOLDER CHECK — PASS (no unallowlisted tokens).
GO-SCHEMA CHECK — PASS (3 GO report(s) validated; zero violations).
ARCH-FRESHNESS CHECK — ARCHITECTURE.md not in changeset; gate inert (exit 0).
OK
```

## Exact Next Trigger

wait for the next live-seat/coordinator mailbox event, or ask me to close the current Stage 0 coordinator board now that trigger enforcement is in place.
