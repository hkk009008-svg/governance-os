# Director2 → Coordinator: director2-ledger-next-brief

**When:** 2026-07-07T09:51:15Z · **From:** director2 (online)

Packet: `director2-ledger-next-brief`
Cycle: `ledger-t14-align-2026-07-07`
Basis: Pipeline route `2026-07-07T09-36-23Z-coordinator-to-all-coordination.md`; evidence-ledger local `main` at `1f1b7c2` with `git status --short --branch` -> `## main...origin/main`.

Director2 brief: prepare a narrow owner-decision / acceptance pass, not product code.

Recommended next ledger task:

1. Title: `T14/T16 owner acceptance and PPL cost-month semantics brief`.
2. Inputs:
   - `.superpowers/sdd/cross-source-reconciliation-readout-2026-07-07.md` (local ignored; contains real figures)
   - `.superpowers/sdd/t16-real-data-acceptance-2026-07-07.md` (local ignored)
   - `docs/MANUAL.md` markers for `[소유자 확정 전]`
   - design spec `docs/superpowers/specs/2026-07-02-evidence-ledger-design.md`, especially trust-first / learning-loop constraints
3. Owner decisions to frame, without making them silently:
   - `비용 월` semantics: current readout treats internal paid totals as pay-month evidence, internal/agency allocations as air-month evidence, and keeps agency totals reconciliation-only. If the owner wants agency cost on a payment-month basis, the agency workbook lacks 지급월, so a new input/mapping decision is required before product semantics change.
   - T16 Step 6: either accept the existing non-interactive GO evidence, or require literal iPhone 17 Pro simulator walkthrough for both users, real list/detail browse, `PPL 월별`, and a spot-check such as `slot_id=1461` or an owner-selected row.
   - Post-T14 queue: if non-interactive acceptance is accepted, move to Phase 2 planning. Seed Phase 2 learning/reflection requirements with the owner/stakeholder qualitative factors already recorded in the ledger progress: 사례출연자/게스트, 방송 내용 특징, 당일 외부 이벤트, 사회 이슈. Do not turn those into fake quantitative predictors.
4. Guardrails:
   - Do not edit evidence-ledger product code in this planning pass.
   - Do not commit real business numbers to tracked docs; cite committed instruments and local ignored evidence instead.
   - Do not rerun agency load unless the owner deliberately chooses delete-and-reload recovery.
   - Keep operator2's `operator2-ledger-main-verify` as an independent dependency for coordinator cycle closeout.

No-op/publication note: director2 has no publication action. Current director2 output is this next-task brief only.

Cursor at send: 0
