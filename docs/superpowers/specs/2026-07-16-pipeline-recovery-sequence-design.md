# Pipeline Recovery Sequence Design

**Status:** Replaced by this compact Pipeline-only sequence on 2026-07-17.

**Canonical constraints:** `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`

## Objective

Reach a simple, effective Pipeline governance state without replaying provider recovery or carrying evidence-ledger repository work.

## Durable Starting Point

Provider tools are terminally decommissioned. The binding evidence is:

- `coordination/mailbox/sent/2026-07-16T17-07-43Z-operator-to-all-verification-report.md`
- `docs/HANDOFF-coordinator-2026-07-16-provider-tools-decommission-closeout.md`

Future provider work requires separate user authorization. This sequence grants none.

## Eight-Plan Sequence

| Order | Plan | Effective disposition |
|---:|---|---|
| 1 | Recovery owner/WIP disposition | No-op unless current non-provider Pipeline bytes have unclear ownership. |
| 2 | Opus quality correction/recovery | Retired. |
| 3 | Target-aware evidence-ledger bridge | Removed; no target work. |
| 4 | PPL publication-race correction | Removed; no target work. |
| 5 | Compact kernel Phase 1-2 | Prove current state; fix one demonstrated gap at most. |
| 6 | Compact control-plane Phase 3 | Live callers, one narrow behavior change at most, one verdict. |
| 7 | Compact kernel Phase 4 | One selector/fence, one rehearsal/review, separately authorized activation. |
| 8 | Retirement/publication reconciliation | No-op unless later compact work creates descriptive drift. |

Plans 2-4 have no executable dependency and never block Plans 5-8.

## Execution Law

- No trigger means no route, receipt, observer, standby, or closeout artifact.
- One change has one writer and focused tests.
- R-INDEPENDENCE uses one non-author-model Operator; only that Operator issues GO/NITS/FAIL.
- Coordinator state is added only for multiple writers, transferred unfinished ownership, overlapping mutable scope, or a real join.
- Push, merge, activation, provider use, cleanup, and other effects require separate authority.
- A slice approaching 500 production lines or needing its own recovery plan stops for re-scope.

## Completion

The sequence is complete when the last executed compact plan has GO and runtime truth matches descriptive truth. If every conditional plan is a no-op, create no synthetic work.
