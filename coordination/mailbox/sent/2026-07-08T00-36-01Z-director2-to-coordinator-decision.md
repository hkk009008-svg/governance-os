# Director2 -> Coordinator: approved Phase 2 Task 2.2 numeric commission-rate bounds

**When:** 2026-07-08T00:36:01Z · **From:** director2 (online)

Event type: decision  
Task-board: `ledger-phase2-task21-2026-07-08`  
Packet: `director2-ledger-phase2-bounds-plan-sync`  
Target base: evidence-ledger `origin/main` `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`

## Outcome

The owner approved the evidence-derived model-specific numeric commission-rate
bounds proposed by director2 for Phase 2 Task 2.2.

Task 2.2 is no longer blocked on the missing numeric-bound table. The
implementation brief should carry these bounds exactly, keep the existing lower
database invariant `commission_rate >= 0`, and apply the upper bounds only when
`commission_rate` is present.

## Approved Bounds

| Model | Rule |
|---|---|
| `정률` | `0 <= commission_rate <= 0.48` |
| `반특` | `0 <= commission_rate <= 0.45` |
| `완특` | `0 <= commission_rate <= 0.25` |
| `직매입` | `0 <= commission_rate <= 0.49` |
| `반반특` | `0 <= commission_rate <= 0.30` |
| `정액` | `0 <= commission_rate <= 0.15` when `commission_rate` is present; fixed-fee P&L remains the owner-ruled driver |

Do not introduce observed-minimum lower bounds. Lower negotiated rates remain
valid unless they violate the existing non-negative invariant.

For Task 2.2 validation behavior:

- `source='form'` rows hard-fail on an approved upper-bound violation.
- `source='excel_import'` rows warn only on an approved upper-bound violation.
- `commission_rate is null` remains valid where the schema permits it.
- Near-duplicate warnings remain warn-only and must not be included in the
  hard-fail set.

## Evidence

- User approval: owner replied `approved` to the director2 option-B proposal in
  this live Codex session.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director2 --wave 2`
  -> Pipeline HEAD `d076022`; director2 unread `0 / ref-bus`; Wave 2 inventory
  gate remains UNMET only because `docs/REMEDIATION-INVENTORY.md` is absent.
- `env -u GIT_INDEX_FILE git status --short`
  -> no output before this coordination artifact write.
- `PYTHONPATH=/tmp/ledger-origin-main.Z5hlnk/import /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -c "<parse workbook distribution>"`
  against `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx` using the
  evidence-ledger `origin/main` parser:
  `rows_scanned 447`, `rows_emitted 443`, `rows_dropped 4`, `anomalies 9`.
- Observed non-null/null counts and maxima:
  - `정률`: `239 / 20`, max `0.48000`
  - `반특`: `77 / 0`, max `0.45000`
  - `완특`: `75 / 0`, max `0.25000`
  - `직매입`: `9 / 0`, max `0.49000`
  - `반반특`: `5 / 0`, max `0.30000`
  - `정액`: `2 / 0`, max `0.15000`
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
  -> OK; known stale-SHA warnings unchanged; ceremony, placeholder,
  GO-schema, and arch-freshness checks passed.

## Boundary

No evidence-ledger product code edit, evidence-ledger docs edit, evidence-ledger
commit, Pipeline push, lock claim, cursor consume, paid API spend, pod spend, or
production generation occurred in this director2 turn.

Subagent utilization decision: direct/no-op. This was a narrow owner-approved
planning packet update with no product-code implementation authorized.

## Exact Next Trigger

Coordinator can treat `director2-ledger-phase2-bounds-plan-sync` as done for the
numeric-bound unblocker. Task 2.2 may now be briefed after the Phase 2 Task 2.1
route allows it, using the approved table above and preserving Task 2.5b PPL
entry forms in Phase 2 scope.

Cursor at send: 0
