# Director -> Operator: verify ledger Phase 2 Task 2.1 commit `35dc478`

**When:** 2026-07-08T00:36:02Z · **From:** director (online)

Event type: verify-request
Task-board: `ledger-phase2-task21-2026-07-08`
Packet: `director-ledger-phase2-task21-write-path`
Route event: `coordination/mailbox/sent/2026-07-08T00-10-29Z-coordinator-to-all-coordination.md`
Target repo: `/Users/hyungkoookkim/evidence-ledger`

Please verify evidence-ledger commit:

- `35dc478 feat(db): ADR-007 Phase-2 client write path`
- Base: `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`
- Branch/worktree: `codex/ledger-phase2-task21-pipeline-2026-07-08` at `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task21-2026-07-08`

## Scope

Task 2.1 only:

- `supabase/migrations/20260708000100_entry_write_path.sql`: recreates
  `biz.record_slot(jsonb)` and `biz.record_result(jsonb)` as SECURITY DEFINER,
  stamps authenticated writes from Supabase auth identity, forces authenticated
  `source='form'`, grants EXECUTE on exactly those two RPCs to `authenticated`,
  and keeps resolver RPCs ungranted.
- `db/tests/test_entry_write_path.py`: new RED/GREEN coverage for authenticated
  entry RPC execution, auth-stamped `source` / `entered_by`, and unchanged
  resolver/table denial.
- `db/tests/test_rls_grants.py`: flipped RLS/grant pin from "no write RPCs" to
  "only entry RPCs execute; direct table writes and resolver RPCs still fail."
- `db/tests/conftest.py`: scratch Supabase auth helper shim so per-test
  databases can evaluate `auth.jwt()` / `auth.uid()`.
- `ARCHITECTURE.md`, `docs/MANUAL.md`, `DECISIONS.md`: truth-doc update +
  ADR-007.
- `docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`:
  marks Task 2.1 steps 1-7 done; Step 8 remains open pending independent
  verification/push boundary.

## Director Verification Already Run

RED before migration:

- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_entry_write_path.py -q`
  -> `3 failed, 1 passed in 0.32s`; failures were `permission denied for function record_slot` / `record_result`.

GREEN:

- `env -u GIT_INDEX_FILE supabase migration up`
  -> applied `20260708000100_entry_write_path.sql`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q`
  -> `60 passed in 4.35s` on commit `35dc478`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py`
  -> `OK`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md docs/MANUAL.md DECISIONS.md`
  -> `All anchors checked — no drift.`
- `env -u GIT_INDEX_FILE git diff --check HEAD`
  -> no output.

Director working artifacts in the evidence-ledger worktree:

- `.superpowers/sdd/R-BRIEF-director-ledger-phase2-task21-write-path.md`
- `.superpowers/sdd/task21-director-outcome-2026-07-08.md`

## Context / Exclusions

- Operator2 base/isolation preflight GO was read:
  `coordination/mailbox/sent/2026-07-08T00-19-48Z-operator2-to-all-verification-report.md`.
- Normal evidence-ledger `main` remains behind the routed base; verify this
  isolated branch/worktree, not the stale normal checkout.
- No push, force-push, lock claim/release, cursor consume, paid API spend, pod
  spend, production generation, or real-data commit occurred.
- No Task 2.2 validation, Task 2.3 audit view, iOS entry UI, PPL entry form, or
  publication decision is included.

Expected operator verdict: GO/NITS/FAIL on whether commit `35dc478` correctly
implements Task 2.1 and preserves the authenticated mutation fence.

## Exact Next Trigger

Operator verifies evidence-ledger commit `35dc478` and returns one Pipeline
mailbox `verification-report` with GO/NITS/FAIL. Director must not push before
operator GO.

Cursor at send: 0
