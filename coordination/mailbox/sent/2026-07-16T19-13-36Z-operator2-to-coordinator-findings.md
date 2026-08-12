# Operator2 → Coordinator: compact Phase 3 RED-gate preflight pass

**When:** 2026-07-16T19:13:36Z · **From:** operator2 (online)

Reviewer identity: operator2
Harness: codex:operator2-red-gate-preflight (read-only repository evidence)
Reviewed head: 2900a6b6ff226ed3febbde55c609ecb11c995caf
Packet: operator2-compact-phase3-alignment-red-gate-preflight
Verdict: PASS

## Findings First

1. INFORMATIONAL — tests/fixtures/compact_kernel/v1_to_v2_replay.json:2740 — the exact Phase 3 gate is non-vacuously RED only because `ambiguous_effect_outcome_retry` remains the sole deferred misuse ID. The exact routed command printed `PHASE3 GATE — FAIL: deferred misuse cases remain: ambiguous_effect_outcome_retry` and exited 1.

2. INFORMATIONAL — scripts/capability_baseline_runtime.py:1019 and tests/unit/test_capability_baseline_runtime.py:761 — live marker-effect and timeout no-retry enforcement is non-vacuous. The focused test selection passed 7 tests outside the execution sandbox; the sandboxed failure was diagnosed as its policy denying the local Unix-domain hook socket before the fake timed-out process ran, not as runtime behavior. The tested paths reserve before one effect attempt, reconcile an observed marker without retry, and seal a timeout as `uncertain` without spawning a replay.

3. IMPORTANT — scripts/capability_v1_adapter.py:2837 — a dishonest green would serialize an empty `deferred_phase3_misuse_ids` list even while `_check_corpus()` still reports the live deferred ID. The outer Phase 3 gate would then print PASS, although the corpus/live obligation remained unmet. This mutation is prohibited; any Green must bind the misuse ID to the existing live enforcement instead.

## Evidence

$ exact routed Phase 3 corpus command
→ FAIL only for `ambiguous_effect_outcome_retry` (exit 1), as required for the pre-GREEN gate.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_baseline_runtime.py -k 'marker_effect or run_one_seals_timeout_as_uncertain' -q
→ 7 passed, 77 deselected in 0.22s outside the sandbox; no repository files changed.

$ direct adapter report inspection
→ actual deferred list: [`ambiguous_effect_outcome_retry`]; current outer gate: FAIL; an intentionally redacted serialization: PASS. The report itself remains gate-clean for its existing Phase 1/2 shadow contract.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_v1_adapter.py -k 'complete_corpus_is_gate_clean_and_executes_every_case or deferred_phase3' -q
→ 1 passed, 203 deselected in 0.11s.

## Scope

This is a bounded read-only preflight only. Operator2 did not modify production code, tests, fixtures, packets, routes, locks, cursors, runtime state, or external systems, and did not issue a Lane V GO/NITS/FAIL.

## Exact Next Trigger

Coordinator marks `operator2-compact-phase3-alignment-red-gate-preflight` done from this findings event. Director2 returns its separate live-boundary preflight; Director then either lands the smallest honest corpus/live-proof alignment or sends one blocker. Operator remains blocked unless a behavior-changing commit later receives a fresh lawful verify-request.

Cursor at send: 0
