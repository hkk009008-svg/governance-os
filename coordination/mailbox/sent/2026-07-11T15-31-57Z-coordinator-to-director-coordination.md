# Coordinator Task 7 release — real-data read-only plan

**When:** 2026-07-11T15:31:57Z

Event type: coordination
Disposition: `TASK7_READ_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Packet: `director-ledger-workbook-refresh-implementation`
Target worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Reviewed target HEAD: `d57f538`

Tasks 0–6 are complete with fresh per-task specification and quality approval.
Release Task 7 Steps 1–4 only: confirm the existing local service health, rerun
the full synthetic suites, and generate the read-only real-data plan from the
canonical workbook/checklist/database and `/Users/hyungkoookkim/Downloads/260710.xlsx`.
Persist outputs only under ignored `.superpowers/sdd/` paths. Prove canonical
DB fingerprint, evidence head, workbook hash, and target status are unchanged.
Any blocking disposition stops before scratch cloning or apply.

## Side-Effect Executor Token

- side_effect_id: `ledger-workbook-refresh-task7-real-plan-2026-07-11`
- executor: Director only
- target: read-only canonical PostgreSQL `postgresql://postgres:postgres@127.0.0.1:54322/postgres`, canonical workbook `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`, checklist `/Users/hyungkoookkim/evidence-ledger/data/merges.csv`, incoming workbook `/Users/hyungkoookkim/Downloads/260710.xlsx`, and ignored outputs `workbook-refresh.plan.json` plus `workbook-refresh.plan.md` in the routed worktree `.superpowers/sdd/`
- allowed_command_class: exact Task 7 Steps 1–4 commands from the approved plan using `/Users/hyungkoookkim/evidence-ledger/.venv/bin/python` and `PG_BIN=/opt/homebrew/opt/libpq/bin`; read/hash/query/report generation only
- preflight: target HEAD/status exactly `d57f538` and clean; local Docker/Supabase already healthy or read-only health checks pass; all three input files are regular files; capture canonical DB fingerprint, evidence-chain head, canonical workbook hash, and git status before planning
- stop_if_newer_mail_or_live_target_satisfied: stop on newer workbook-refresh authority, target drift, non-local DSN, missing/aliased input, any blocking disposition, parser baseline failure, summary mismatch, or any attempted database/resource mutation
- postcheck: planner exits with zero blocking dispositions; plan JSON/report exist only in ignored `.superpowers/sdd/`; before/after DB fingerprint, evidence head, canonical workbook hash, and git status are identical; record the plan SHA-256 and disposition counts without business values
- observer_seats: Operator, Director2, and Operator2 remain observer-only; no repeated read/generation
- final_closeout_owner: Coordinator after Director reports the exact plan hash and zero-blocker/read-only evidence
- non_goals: no scratch database create/drop, dump/restore, dry-run/apply, canonical database/resource mutation, normal-checkout edit, cursor consume, lock action, push, merge, publication, deployment, paid service, service stop, or container/volume deletion

## Exact Next Trigger

Director executes Task 7 Steps 1–4 under this token and returns the exact plan
SHA-256, disposition-only zero-blocker summary, and unchanged canonical
fingerprints. Coordinator then issues the separately bound real-data scratch
clone/dry-run/apply/cleanup token.
