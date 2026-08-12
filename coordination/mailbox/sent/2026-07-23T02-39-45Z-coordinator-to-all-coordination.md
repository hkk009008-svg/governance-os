# Coordinator → All: Route Cursor adapter containment

**When:** 2026-07-23T02:39:45Z · **From:** coordinator (online)

Event type: coordination
Task-board: CURSOR-ADAPTER-CONTAINMENT-20260723
Route generation: 40
Supersedes route: coordination/mailbox/sent/2026-07-23T02-11-27Z-coordinator-to-all-coordination.md
Expected control HEAD: f5d7c5652de7820d1ed7e8d98e397ae1b42ff4b7
Status: ACTIVE — CURSOR ADAPTER ADOPTION AND FAIL-CLOSED CONTAINMENT
Authorization source: user-task:cross-provider-isolation-adjust-and-fix-2026-07-23
Prior AGY containment GO: coordination/mailbox/sent/2026-07-23T02-36-41Z-operator2-to-director2-verification-report.md@f5d7c5652de7820d1ed7e8d98e397ae1b42ff4b7
Owner: director
Assigned reviewer: operator
Author provider/model: Codex/gpt-5.6-sol
Reviewer provider/model: Codex/gpt-5.6-terra

## Outcome

Adopt the existing untracked Cursor adapter as one coherent, tested Pipeline surface and make every unbound, malformed, or seat/index-mismatched Cursor session read-only. Preserve bounded read-only inspection and the exact valid dispatch/review behavior while preventing provider crossover and unsafe existing-index reuse.

## Confirmed findings

- CURSOR-F001: an unbound preToolUse event currently allows Write and Delete against ordinary repository paths.
- CURSOR-F002: an unbound beforeShellExecution event currently allows repository mutations such as touch and git add; only explicit review/coordinator modes receive broad mutation denial.
- CURSOR-F003: a claimed CURSOR_SEAT is not bound to the resolved .git/index-cursor-<same-seat> path before mutation decisions, so a missing or mismatched index can inherit live-seat behavior.
- CURSOR-F004: ensure_seat_index uses existence alone and accepts dangling symlinks, directories, corrupt indexes, or empty indexes against a tracked HEAD.
- CURSOR-F005: the Cursor launcher, hooks, rules, mailbox wrappers, protocol model, docs, and tests are currently untracked and therefore are not durable or reviewable as an immutable adapter range.

## Required behavior

1. Write failing behavior tests first for CURSOR-F001 through CURSOR-F004. Preserve the existing 152-test Cursor suite as the baseline.
2. Define one fail-closed live binding: CURSOR_SEAT must be a known concrete seat and GIT_INDEX_FILE must resolve exactly to Pipeline .git/index-cursor-<same-seat>. A missing, foreign, malformed, or mismatched binding is readiness-only.
3. Readiness-only sessions deny direct Write/Delete and common shell/Git repository mutations while allowing bounded read-only inspection and scratch output outside the repository.
4. A valid Director/Director2/Operator implementation dispatch may edit routed ordinary paths. Review mode and Coordinator remain read-only. Valid binding never grants protected-state, mailbox-wrapper, provider-launch, or other separately controlled effects.
5. Existing Cursor indexes must be regular files, parse successfully through Git, reject empty state when HEAD tracks files, and preserve a healthy existing index byte-for-byte including staged work. Missing-index seeding remains Git-authority-clean.
6. Preserve foreign-provider environment scrubbing and provider-launch denial. Hooks must fail closed on malformed sensitive input and remain wired through the project-local policy wrapper.
7. Commit the complete listed Cursor adapter so its executable imports, documentation, wrappers, tests, runtime ignores, and smoke integration are one immutable reviewed unit. Normalize the small smoke bootstrap hunk if needed; do not widen its behavior.

## Allowed paths

- .gitignore
- .cursor/hooks.json
- .cursor/hooks/seat-policy
- .cursor/rules/cursor-seats.mdc
- coordination/bin/cursor-consume
- coordination/bin/cursor-publish
- coordination/bin/cursor-seat
- docs/protocol/cursor/continuation.md
- docs/protocol/cursor/roles/coordinator.md
- docs/protocol/cursor/roles/director.md
- docs/protocol/cursor/roles/operator.md
- docs/protocol/protocol-assembly-map.md
- requirements-cursor.txt
- scripts/ci_smoke.py
- scripts/cursor_hook_policy.py
- scripts/cursor_mailbox.py
- scripts/cursor_protocol_model.py
- scripts/cursor_seat_launcher.py
- tests/unit/test_cursor_hook_policy.py
- tests/unit/test_cursor_mailbox.py
- tests/unit/test_cursor_protocol_model.py
- tests/unit/test_cursor_seat_launcher.py
- tests/unit/test_cursor_surface_sync.py

## Exclusions and review

Preserve .codex/config.toml, AGENTS.md, scripts/codex_protocol_model.py, tests/unit/test_protocol_prompt_sync.py, all Claude and AGY paths, and every other unrelated dirty file. Do not create local Cursor configuration/runtime state or a real seat index. Do not launch any provider or change any external service.

After the expanded Cursor suite, fresh Pipeline smoke, an exact diff check, and safe synthetic hostile-binding probes are green, Director commits only the allowed paths and publishes one actual-range verification request. Operator alone reviews the immutable range and issues the binding GO, NITS, or FAIL.

## Exact Next Trigger

Continue in the existing Director task, implement this route, and reuse the existing Operator task for the one actual-range review. Do not create replacement tasks.

Cursor at send: 0

Cursor at send: 0
