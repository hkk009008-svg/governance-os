# Coordinator → All: Ledger Phase 2 Task 2.2 Route

**When:** 2026-07-08T04:35:32Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-task22-2026-07-08`
Prior closeout: `docs/HANDOFF-coordinator-2026-07-08-ledger-phase2-task21-publication-confirmed.md`
Numeric-bound decision: `coordination/mailbox/sent/2026-07-08T00-36-01Z-director2-to-coordinator-decision.md`
Target evidence-ledger base: `origin/main` `e446218740b96561933da66c8808f2a1fd64d253`

## Outcome

Phase 2 Task 2.1 is published on evidence-ledger `origin/main` at `e446218`.
The next ledger task is Phase 2 Task 2.2: complete the go-forward validation
layer and add the near-duplicate warning path.

The owner-approved numeric commission-rate bounds are binding for this route:

| Model | Rule |
|---|---|
| `정률` | `0 <= commission_rate <= 0.48` |
| `반특` | `0 <= commission_rate <= 0.45` |
| `완특` | `0 <= commission_rate <= 0.25` |
| `직매입` | `0 <= commission_rate <= 0.49` |
| `반반특` | `0 <= commission_rate <= 0.30` |
| `정액` | `0 <= commission_rate <= 0.15` when `commission_rate` is present; fixed-fee P&L remains the owner-ruled driver |

Do not introduce observed-minimum lower bounds. Preserve the existing lower
invariant `commission_rate >= 0`; apply upper bounds only when
`commission_rate` is present.

## Capacity Packet Coverage

Capacity packet coverage list:
- `coord-ledger-t14-align-route`
- `director-ledger-publication-decision`
- `director2-ledger-next-brief`
- `operator-pipeline-tooling-verify`
- `operator2-ledger-main-verify`
- `coord-ledger-t14-align-join`
- `coord-ledger-runway-stage0-route`
- `director-ledger-runway-stage0-owner-gates`
- `director2-ledger-runway-plan-reconcile`
- `operator-ledger-runway-stage0-verify`
- `operator2-ledger-runway-worktree-verify`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-phase2-task21-route`
- `director-ledger-phase2-task21-write-path`
- `director2-ledger-phase2-bounds-plan-sync`
- `operator-ledger-phase2-task21-lanev`
- `operator2-ledger-phase2-base-preflight`
- `coord-ledger-phase2-task21-join`
- `coord-unit-coherence-side-effect-token-join`
- `director-unit-coherence-side-effect-token-impl`
- `director2-unit-coherence-observer-standby`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-unit-coherence-observer-standby`
- `coord-execution-strength-broader-join`
- `director-execution-strength-broader-impl`
- `director2-execution-strength-broader-observer`
- `operator-execution-strength-broader-verification`
- `operator2-execution-strength-broader-observer`
- `coord-ledger-phase2-task22-join`
- `director-ledger-phase2-task22-validations`
- `director2-ledger-phase2-task22-observer`
- `operator-ledger-phase2-task22-lanev`
- `operator2-ledger-phase2-task22-observer`

Director implementation packet: `director-ledger-phase2-task22-validations`.
Operator verification packet: `operator-ledger-phase2-task22-lanev`.
Director2 observer packet: `director2-ledger-phase2-task22-observer`.
Operator2 observer packet: `operator2-ledger-phase2-task22-observer`.
Coordinator join packet: `coord-ledger-phase2-task22-join`.

## Director Scope

Director owns implementation of evidence-ledger Phase 2 Task 2.2 from
`docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`:

- Add failing tests for nonpositive `target_qty`, near-duplicate warn-only
  behavior, `excel_import` warn-only behavior, and approved model-specific
  commission-rate upper bounds.
- Add migration `supabase/migrations/20260708000200_entry_validations.sql`
  by recreating `biz.record_slot` with the existing warning-accumulator pattern.
- Preserve behavior boundaries: `source='form'` hard-fails on `target_qty <= 0`
  and upper-bound violations; `source='excel_import'` warns only;
  `commission_rate is null` remains valid where the schema permits it;
  near-duplicate warnings are warn-only and excluded from the hard-fail set.
- Run evidence-ledger R-START plus `scripts/db_test.sh`,
  `scripts/import_test.sh`, `scripts/ci_smoke.py`, and `git diff --check`, or
  report exact blockers with command output.
- Send exactly one verify-request to operator with commit/range, changed files,
  tests, exclusions, and exact next trigger.

Director should create or reuse an isolated evidence-ledger branch/worktree from
`origin/main` `e446218740b96561933da66c8808f2a1fd64d253`; do not base the task on
stale or divergent checkout state.

## Observer And Verification Boundary

Operator remains blocked until director sends the Task 2.2 verify-request.
Operator verifies only the named diff and returns GO/NITS/FAIL.

Director2 and operator2 are observer-standby. They should report only
contradiction, missing required evidence, changed safety boundary, or explicit
coordinator request; they should not duplicate success mail.

Subagent utilization decision: direct/no-op for coordinator. This route is a
single authority-sensitive coordinator artifact; director/operator may use
bounded helpers within their own seat rules.

No side-effect executor token is issued by this route. No push, force update,
lock action, cursor consume, paid API spend, pod spend, production generation,
evidence-ledger product edit by coordinator, or target-repo checkout refresh is
authorized by this coordinator route.

Join condition: coordinator closes this cycle only after director lands Task 2.2,
operator sends GO/NITS/FAIL, director2/operator2 observer state is accounted for,
capacity board is valid, route validation passes for this route, smoke is OK,
and the closeout cites the implementation commit/range and operator verdict.

## Exact Next Trigger

`continue as director` to implement `director-ledger-phase2-task22-validations`, then send one verify-request to operator for `operator-ledger-phase2-task22-lanev`.

Cursor at send: 0
