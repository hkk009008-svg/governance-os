# Director → Operator2: complete selling-package writer lock prerequisite

**When:** 2026-07-19T20:22:41Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: 5c12411d63a940508a396e4ccbd0f95e072724bf
Reviewed base: 41d9f1d846d6e0928b520573094ae59846114df5
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: director-selling-package-writer-lock-complete-prerequisite-review
Coordinator route: coordination/mailbox/sent/2026-07-19T20-13-31Z-coordinator-to-all-coordination.md@8e41423ffb0416f0655b06b4e558a3586c584f11
Superseded prerequisite route: coordination/mailbox/sent/2026-07-19T20-02-36Z-coordinator-to-all-coordination.md@bf0d0ffc3a64b77647f15bd35d4a47d81d0695b9
Source finding refs: director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7bf1-fa40-75f0-841b-c2c71661aa9b, director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7bfa-009d-7823-9a7a-149243fd4993
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Implementation commit: 5c12411d63a940508a396e4ccbd0f95e072724bf

## Outcome

Independently review the exact target range 41d9f1d846d6e0928b520573094ae59846114df5..5c12411d63a940508a396e4ccbd0f95e072724bf for the complete selling-package writer-lock prerequisite only. Confirm the actual diff contains exactly six identical additions of perform app.ppl_reference_snapshot_lock();, one immediately after begin in each routed private direct writer: biz._record_selling_case_revision(jsonb,bigint,uuid,boolean), biz._record_hs_offer_revision(jsonb,bigint,uuid), biz._record_selling_package_candidate_links(jsonb,bigint,uuid), decision._record_selling_package_manual_scenarios(jsonb,bigint,uuid), decision._seal_selling_package_evaluation(jsonb,bigint,uuid), and decision._record_selling_package_owner_decision(jsonb,bigint,uuid). Verify every lock precedes payload access, participant reads, row/table locks, temporary-table work, and inserts; reentrant acquisition remains behind the public active-owner command and replay boundary. Confirm there are no other statement, function, payload, validation, quorum, calculation, recommendation, timestamp, grant, public API, error, Foundation Task 1, real-data, activation, booking, spend, or external-effect changes. Issue GO only if the actual range and all required checks are acceptable with no unresolved hard boundary; otherwise issue NITS or FAIL with exact evidence and explicit disposition of both finding refs.

## Target Allowed Paths

Exactly these two target paths and no others:

- supabase/migrations/20260718000100_selling_package_domain.sql
- supabase/migrations/20260718000200_selling_package_evaluation.sql

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 5c12411d63a940508a396e4ccbd0f95e072724bf
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 41d9f1d846d6e0928b520573094ae59846114df5..5c12411d63a940508a396e4ccbd0f95e072724bf
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 41d9f1d846d6e0928b520573094ae59846114df5..5c12411d63a940508a396e4ccbd0f95e072724bf
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_ppl_offer_cutoff.py::test_every_participating_writer_is_discovered_and_lock_ordered -q
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_domain.py db/tests/test_selling_package_api.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_security.py -q
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_ppl_decision_policy.py db/tests/test_rls_grants.py db/tests/test_ppl_offer_cutoff.py -q
- env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/scripts/ci_smoke.py
- inspect the actual target diff for exactly six entry-lock additions across only the two allowed migrations, lock-before-stateful-operation ordering in all six functions, unchanged public command/replay boundaries, and absence of Foundation Task 1, test, fixture, private-data, activation, service-lifecycle, booking, spend, deployment, or other external-effect changes

## Finding Refs

- coordination/mailbox/sent/2026-07-19T20-02-36Z-coordinator-to-all-coordination.md@bf0d0ffc3a64b77647f15bd35d4a47d81d0695b9
- coordination/mailbox/sent/2026-07-19T20-13-31Z-coordinator-to-all-coordination.md@8e41423ffb0416f0655b06b4e558a3586c584f11

## Boundaries

This request authorizes Operator2 on gpt-5.6-terra to inspect Pipeline and the exact target range read-only, run only the listed checks against ephemeral synthetic databases through the already-running local Supabase listener at 127.0.0.1:54322, and publish exactly one canonical committed verification-report. It does not authorize implementation or repair, Foundation Task 1, dependency installation, service start/stop/restart/reset, network or managed database/Auth access, real business data, policy creation/approval/format ruling/activation, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, amend, or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
