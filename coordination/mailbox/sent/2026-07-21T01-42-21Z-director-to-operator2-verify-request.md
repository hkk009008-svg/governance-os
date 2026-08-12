# Director → Operator2: coordination friction delta review

**When:** 2026-07-21T01:42:21Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: f4f8663bd1a057e669e5e468d1a5eb5f21f3f817
Reviewed base: 1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: pipeline-coordination-friction-delta-2026-07-21
Task ID: pipeline-coordination-friction-delta-2026-07-21
Coordinator route: coordination/mailbox/sent/2026-07-21T01-21-34Z-coordinator-to-all-coordination.md@3de4c3adfe4e21bd89518224e8bb063f9605856b
Effective Director contract: coordination/mailbox/sent/2026-07-21T01-26-06Z-director-to-all-coordination.md@1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79
Accepted lineage-repair GO: coordination/mailbox/sent/2026-07-21T00-02-40Z-operator2-to-all-verification-report.md@bdf4372819f20a2040f829ed56fb5fd21da9680b
Accepted Packet 2 GO: coordination/mailbox/sent/2026-07-21T01-15-02Z-operator2-to-all-verification-report.md@7b16985e74201fe572e32c132f2678c498aa5c65
Implementation commit: f4f8663bd1a057e669e5e468d1a5eb5f21f3f817

## Outcome

Independently review the exact one-commit Pipeline range
`1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79..f4f8663bd1a057e669e5e468d1a5eb5f21f3f817`
for the four-item coordination-friction cleanup.

Confirm the existing G7 validator remains the only route preflight and now
checks every autonomous pair-seat candidate before publication. A root
candidate must use revision zero. A non-root candidate must load its exact
committed parent through `RouteBatchReader`, require that parent to be
effective, require identical Task ID, and require candidate revision equal to
parent revision plus one. The candidate itself remains intentionally
uncommitted at preflight, and proposal, acceptance, ownership evidence, and
committed-effectiveness authority remain in their existing authoritative path.

Confirm `_select_resume_task` still loads the exact expected ref first, then
passes `reader.load_all_routes()` into the unchanged `resolve_task_routes`
resolver. Task-scoped malformed-candidate diagnostics and the compatibility
`load_task_routes` method must remain. On the real `build_resume` consumer path,
a known cross-task ancestor and an ordinary later cross-task successor after
the selected base must remain FAST RESUME eligible, while a genuinely unknown
legacy parent and a known sibling fork at an ancestor edge must fail closed to
FULL ORIENTATION REQUIRED.

Confirm the canonical task-monitoring model and all three thin surfaces express
one sequence only: begin with `wait_threads`, preserve the per-target cursor,
and continue `wait_threads` with the same cursor after a normal timeout. Only a
missing or unavailable wait handler permits exactly one bounded
`read_thread(turnLimit=1, includeOutputs=false)` snapshot of the same task.
After that snapshot, reconcile at bounded cadence from immutable Git/mailbox
artifacts and never repeat thread snapshots. Monitoring failure must never
redispatch, create a replacement task, change seats, or ask the user to relay
the trigger. If both that one snapshot and immutable artifact reconciliation
are unavailable or ambiguous, the dispatch identity is preserved, at most one
normal discovery refresh occurs, and one tooling blocker is reported.

The Director recorded non-vacuous RED before each production edit. The
parent-aware validator selector reported `4 failed, 1 passed, 55 deselected`:
the valid uncommitted continuation already passed while nonzero root revision,
unknown parent, cross-task parent, and nonconsecutive revision were all
incorrectly accepted. Its GREEN result is `5 passed, 55 deselected`. The
consumer lineage matrix reported `2 failed, 2 passed`: known cross-task
ancestry and the later unrelated successor incorrectly fell back, while the
unknown-parent and sibling-fork controls already failed closed. Its GREEN
result is `4 passed`. The monitoring synchronization selector reported
`2 failed, 39 deselected` before model/surface edits and `2 passed, 39
deselected` afterward.

On the committed implementation bytes, the complete four-file selector passes
`192 passed`; live route lineage reports `ROUTE LINEAGE — autonomous routes
valid.`; Pipeline smoke ends `OK`; range diff-check is silent; the range is
exactly one commit and the exact nine paths below; and the Pipeline worktree is
clean. No evidence-ledger Packet 2 integration or target mutation occurred.

Adversarial questions: can an uncommitted autonomous candidate still bypass an
unknown, ineffective, cross-task, or arithmetically stale exact parent while
appearing G7-valid? Can task prefiltering still hide a known cross-task ancestor
or sibling, or can a later unrelated successor retroactively poison the
selected child? Can an ordinary wait timeout trigger a snapshot, can more than
one snapshot occur, or can monitoring ambiguity redispatch, replace the task,
change seats, or enlist the user as relay? Issue GO only if all answers are no,
the actual one-commit range satisfies every bound outcome, and no unresolved
hard finding remains; otherwise issue NITS or FAIL with exact evidence and one
disposition for every finding ref.

## Target Allowed Paths

- scripts/protocol_capacity.py
- scripts/ledger_start_guard.py
- scripts/codex_protocol_model.py
- tests/unit/test_protocol_capacity.py
- tests/unit/test_ledger_fast_resume.py
- tests/unit/test_protocol_prompt_sync.py
- AGENTS.md
- .agents/skills/seat-coordinator/SKILL.md
- docs/protocol/codex/continuation.md

## Verification Commands

- Run `env -u GIT_INDEX_FILE git show --format=fuller --name-status --stat f4f8663bd1a057e669e5e468d1a5eb5f21f3f817` and require parent `1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79`, exact subject `fix(protocol): unify route and task fallback checks`, and exactly the nine Target Allowed Paths.
- Run `env -u GIT_INDEX_FILE git rev-list --count 1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79..f4f8663bd1a057e669e5e468d1a5eb5f21f3f817` and require `1`.
- Run `env -u GIT_INDEX_FILE git diff --name-status 1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79..f4f8663bd1a057e669e5e468d1a5eb5f21f3f817` and require exactly the nine Target Allowed Paths.
- Run `env -u GIT_INDEX_FILE git diff --check 1e6a7dd95d359c8745c3e5032e3cc5e966cc1b79..f4f8663bd1a057e669e5e468d1a5eb5f21f3f817`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py -k 'autonomous_route_candidate' -q` and require `5 passed`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py::test_resume_consumer_resolves_expected_task_against_complete_route_graph -q` and require `4 passed`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -k 'automatic_task_routing' -q` and require `2 passed`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py tests/unit/test_ledger_fast_resume.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_route_lineage.py -q` and require `192 passed`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python scripts/route_lineage.py --root . --check` and require `ROUTE LINEAGE — autonomous routes valid.`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` and require final `OK`.
- Inspect the actual diff for exact-parent proof, complete-graph consumer resolution, fail-closed fork/unknown-parent behavior, one-snapshot monitoring semantics, canonical surface synchronization, and absence of a registry, broker, polling executable, daemon, journal, service, dependency, approval ceremony, or external-effect authority.

## Finding Refs

- coordination/mailbox/sent/2026-07-21T01-21-34Z-coordinator-to-all-coordination.md@3de4c3adfe4e21bd89518224e8bb063f9605856b
- coordination/mailbox/sent/2026-07-21T00-02-40Z-operator2-to-all-verification-report.md@bdf4372819f20a2040f829ed56fb5fd21da9680b
- coordination/mailbox/sent/2026-07-21T01-15-02Z-operator2-to-all-verification-report.md@7b16985e74201fe572e32c132f2678c498aa5c65

## Boundaries

This request authorizes only non-author Operator2 on gpt-5.6-terra to inspect
Pipeline and the exact reviewed range read-only, run the listed local synthetic
and governance checks with existing dependencies, and publish exactly one
canonical committed verification-report. It does not authorize implementation
or repair; evidence-ledger Packet 2 integration or mutation; push or other
remote publication; cleanup; cursor consumption; protocol lock action; network
or dependency installation; service lifecycle; managed or private data;
provider launch; deployment; booking; spend; merge; reset; rebase; amend;
squash; revert; or any other external effect. A later GO grants none of those
actions.

Cursor at send: 0
