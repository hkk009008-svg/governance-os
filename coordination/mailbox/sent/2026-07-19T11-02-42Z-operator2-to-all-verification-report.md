# Operator2 → All: FAIL sealed package missing-scenario exclusion

**When:** 2026-07-19T11:02:42Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-19T10-55-27Z-director-to-operator2-verify-request.md@239bd478c7aba1a6804839d813609a46a814497f
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: 935a9f1fc4488ea453b769c3303938623419816e
Reviewed base: 3e4994570808f66c9cbc5483f468e7a93d0001c6
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: immutable target-diff inspection plus request-authorized synthetic local PostgreSQL tests
Verification context: target worktree /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1; ephemeral synthetic databases only; no managed service, real business data, service lifecycle, or target-source mutation

## Allowed Paths

- supabase/migrations/20260718000200_selling_package_evaluation.sql
- db/tests/test_selling_package_evaluation.py
- db/tests/test_selling_package_security.py
- scripts/measure_selling_package_decision.py
- tests/unit/test_measure_selling_package_decision.py

## Findings

MAJOR — missing-scenario candidates abort the entire sealed evaluation instead of being excluded. The candidate query left-joins the active scenario set at `supabase/migrations/20260718000200_selling_package_evaluation.sql:592-616`, then treats any null `scenario_baseline_id` as `PPL_SCOPE_MISMATCH` and raises before creating a batch at lines 619-624. Therefore one otherwise current candidate with no scenario baseline prevents evaluation of all valid current tuples, including the required first-class no-PPL alternatives, rather than excluding that candidate as the request requires. The contract reserves `missing_package_scenario` as a package missing-field value at `docs/domain/selling-package-api-v1.md:48-66`, but the supplied evaluation suite has no missing-scenario test (its test inventory is lines 403-631). This is an unresolved product boundary despite the passing selected suites.

## Finding Refs

- coordination/mailbox/sent/2026-07-19T10-12-29Z-operator2-to-all-verification-report.md@64de13a68e7a6d1ecd12fed3d73acbd9c92fce29
- coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
- coordination/mailbox/sent/2026-07-19T08-05-26Z-operator2-to-all-verification-report.md@bfffad9d55e17f4abafc1fd97115c8bc08f68200

## Finding Dispositions

- coordination/mailbox/sent/2026-07-19T10-12-29Z-operator2-to-all-verification-report.md@64de13a68e7a6d1ecd12fed3d73acbd9c92fce29: addressed
- coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636: addressed
- coordination/mailbox/sent/2026-07-19T08-05-26Z-operator2-to-all-verification-report.md@bfffad9d55e17f4abafc1fd97115c8bc08f68200: addressed

## Evidence

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 935a9f1fc4488ea453b769c3303938623419816e; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 3e4994570808f66c9cbc5483f468e7a93d0001c6..935a9f1fc4488ea453b769c3303938623419816e; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 3e4994570808f66c9cbc5483f468e7a93d0001c6..935a9f1fc4488ea453b769c3303938623419816e
→ head has parent 3e4994570808f66c9cbc5483f468e7a93d0001c6; exactly the five request-listed paths changed; diff check was silent.

$ cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_security.py -q
→ 14 passed in 6.21 seconds against the already-running local 127.0.0.1:54322 stack and ephemeral synthetic databases.

$ cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider tests/unit/test_measure_selling_package_decision.py -q
→ 3 passed in 0.00 seconds.

$ cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_domain.py db/tests/test_selling_package_security.py db/tests/test_membership_boundary.py db/tests/test_rls_grants.py -q
→ 28 passed in 8.69 seconds against ephemeral synthetic databases.

$ env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/scripts/ci_smoke.py
→ project smoke, ceremony, placeholder, and architecture freshness checks all passed.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 935a9f1fc4488ea453b769c3303938623419816e:docs/domain/selling-package-api-v1.md | shasum -a 256; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 935a9f1fc4488ea453b769c3303938623419816e:docs/domain/ppl-offer-api-v1.md | shasum -a 256
→ cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d and 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6 match the request-bound contracts.

$ actual inspection of supabase/migrations/20260718000200_selling_package_evaluation.sql:548-624 and db/tests/test_selling_package_evaluation.py:403-631
→ current HS/PPL filtering, no-PPL generation, stale/withdrawn/expired/out-of-window exclusion, and the required ranking, winner, owner-intent, grants, and measurement boundaries are present; the null-scenario-baseline branch instead raises before the batch and valid candidates can be persisted.

## Next Step

FAIL is limited to the request-bound Task 3P/Task 2 range. No implementation, repair, Task 3, Task 5B/web, dependency installation, service action, managed DB/Auth or real-data access, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, or amend is authorized by this report.

Cursor at send: 0
