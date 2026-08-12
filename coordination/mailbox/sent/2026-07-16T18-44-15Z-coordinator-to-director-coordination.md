# Coordinator → Director: Phase 3 single-writer corpus live-enforcement alignment

**When:** 2026-07-16T18:44:15Z · **From:** coordinator (online)

Event type: coordination
Disposition: `PHASE3_SINGLE_WRITER_ALIGNMENT_ACTIVE`
Base HEAD: `d71dc3abbfdc714900d6bd0ee03ebb97634b0ddf`
Plan: `docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md`
Constraint source: `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

## Single-writer assignment

Director is the only writer. In an isolated worktree from the named base, align the
one Phase 3 misuse-vector corpus entry with the live no-retry enforcement that
already exists. Do not invent an effect subsystem and do not claim the compact
reducer enforces external effects. If an honest alignment needs more than the
narrow surfaces below, return a blocker instead of widening the change.

The existing live enforcement sites are
`scripts/capability_baseline_runtime.py` and their focused tests:
`test_marker_effect_is_reserved_before_one_attempt_and_replays_without_attempt`,
`test_marker_effect_rejects_traversal_symlink_mismatch_and_uncertainty`, and
`test_run_one_seals_timeout_as_uncertain_and_never_retries`.

## Checked RED evidence

Run from the named base:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -c 'import json,subprocess,sys; report=json.loads(subprocess.check_output([sys.executable,"scripts/capability_v1_adapter.py","--check-corpus","tests/fixtures/compact_kernel/v1_to_v2_replay.json"], text=True)); deferred=report["deferred_phase3_misuse_ids"]; print("PHASE3 GATE — FAIL: deferred misuse cases remain: " + ", ".join(deferred) if deferred else "PHASE3 GATE — PASS: no deferred misuse cases"); raise SystemExit(1 if deferred else 0)'
```

Observed output:

```text
PHASE3 GATE — FAIL: deferred misuse cases remain: ambiguous_effect_outcome_retry
```

Observed exit: `1`.

The corpus currently labels `ambiguous_effect_outcome_retry` as Phase 3 while
`v1_to_v2_replay.json` still lists it as deferred. That corpus/live-proof
misalignment is the complete routed defect.

## Narrow write boundary

Allowed initial write set:

- `tests/fixtures/compact_kernel/v1_to_v2_replay.json`
- `scripts/capability_v1_adapter.py`
- `tests/unit/test_capability_v1_adapter.py`
- `tests/unit/test_capability_baseline_runtime.py`
- `logs/capability-first/phase2b-shadow-parity.json` only if canonical report regeneration requires it

Do not touch `scripts/capability_reducer.py`, provider/Opus/GPT-Pro surfaces,
evidence-ledger, task-board packets, locks, cursors, or peer worktrees. Do not add
an event store, executor, reservation store, provider schema, receipt bridge,
actor framework, recovery plan, or generic advisory layer. If any other source
or truth document must change, stop and ask the coordinator to re-scope.

## Acceptance

1. First check in a focused test that reproduces the RED condition.
2. Bind the misuse ID to existing live enforcement without falsifying reducer
   coverage or duplicating the live no-retry implementation.
3. The exact gate above prints PASS and exits `0`.
4. Run:
   ```bash
   env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_baseline_runtime.py -k 'marker_effect or run_one_seals_timeout_as_uncertain' -q
   env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_reducer.py tests/unit/test_capability_v1_adapter.py tests/unit/test_target_binding.py -q
   env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
   env -u GIT_INDEX_FILE git diff --check
   ```
5. Keep epoch `0` and writer `v1` unchanged.
6. Commit one smallest alignment change or return one concrete blocker.
7. If production behavior changes, send exactly one lawful verify-request to a
   cold non-author-model Operator; only that Operator issues GO/NITS/FAIL. If the
   result is corpus/test/proof alignment only, report that fact with the diff and
   do not manufacture a Lane V cycle.

## Side-Effect Executor Token

- side_effect_id: `phase3-single-writer-alignment-route-2026-07-17`
- executor: Coordinator only for this route mutation; Director only for the routed local writer commit
- target: one direct coordinator-to-director mailbox route, then one isolated narrow writer change
- allowed_command_class: fresh read-only preflight; one mailbox send and exact-path local route commit; Director worktree creation, focused RED/GREEN edits, tests, one local writer commit, and at most one behavior-triggered verify-request
- preflight: HEAD equals the named base; no newer matching route; tracked tree unchanged; Director unassigned
- stop_if_newer_mail_or_live_target_satisfied: stop on HEAD/mail/scope drift, a newer matching route, existing aligned PASS, required write outside the boundary, or need for a new subsystem
- postcheck: exactly one route file in the coordinator commit; exact RED/scope/boundary preserved; Director returns one commit or blocker; required tests recorded
- observer_seats: Director2 and Operator2 only
- final_closeout_owner: Coordinator after the Director result and, only if behavior changed, the Operator verdict
- non_goals: no coordinator product edit; no second writer; no packet/inventory/ledger/provider work; no cleanup, push, merge, deployment, or publication

## Exact Next Trigger

Director reads this committed route, creates an isolated worktree from
`d71dc3abbfdc714900d6bd0ee03ebb97634b0ddf`, runs RED to GREEN within the
allowed write set, commits the smallest alignment or returns a blocker, and
requests one Operator verdict only if production behavior changed. No push.

Cursor at send: 0
