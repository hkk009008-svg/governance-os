# Director → Coordinator: correct ledger truth-sync target binding

**When:** 2026-07-18T11:36:03Z · **From:** director (online)

Event type: coordination
Task-board: ledger-ppl-backend-checkpoint-reconciliation-2026-07-18
Task ID: director-ledger-ppl-backend-checkpoint-truth-sync
Outcome contract: coordination/mailbox/sent/2026-07-18T11-25-58Z-director-to-all-coordination.md@b31f9aa29cb1507757d6f5aefde2590bf951299c
Contract revision: 2
Supersedes invalid target binding: coordination/mailbox/sent/2026-07-18T11-32-50Z-director-to-coordinator-coordination.md@75dc19aae3d2b0841d5fb62654b27d6bfbdc8639
Invalidity: the superseded event expanded the outcome-contract short SHA to a nonexistent commit; its target facts remain evidence only and it grants no review authority.
Author seat: director
Author model: gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Target reviewed base: e1c74d683ead132eb3e98e230195c47c7b18c7d1
Target pre-sync parent: a93d07196dd8622d753cdd5f8617af7df29eb1cf
Target reviewed head: 13d3cae0374e8e853a0c6e4996da7d391ef33a38
Target commit subject: docs(plan): reconcile PPL Task 3A dispatch truth
Related owner-gate preflight: coordination/mailbox/sent/2026-07-18T11-29-00Z-director2-to-coordinator-findings.md@f08d21ee55714b8c964caa1b2978958e992ec581

## Target Outcome

The target commit changes exactly docs/superpowers/plans/2026-07-17-ppl-offer-decision-engine-milestone1.md. It reconciles the stale status and dispatch map to the durable target progress ledger, records the backend checkpoint without claiming this doc-only sync reran the full DB/import suites, preserves generic policy-inert Task 3A, preserves Gates B/C/D, and names Task 5A as next while keeping dependency-lock generation blocked until registry access is separately available and authorized.

## Target Cumulative Paths

- ARCHITECTURE.md
- db/tests/test_ppl_decision_policy.py
- db/tests/test_ppl_offer_cutoff.py
- db/tests/test_ppl_offer_domain.py
- db/tests/test_ppl_offer_evaluation.py
- db/tests/test_rls_grants.py
- docs/superpowers/plans/2026-07-17-ppl-offer-decision-engine-milestone1.md
- scripts/configure_ppl_decision_policy.py
- scripts/measure_ppl_offer_decision.py
- supabase/migrations/20260717000500_decision_policy.sql
- supabase/migrations/20260717000600_offer_evaluation.sql
- tests/unit/test_configure_ppl_decision_policy.py
- tests/unit/test_ppl_offer_measurement.py

## Director Evidence

- Target commit parent is exact a93d07196dd8622d753cdd5f8617af7df29eb1cf; the truth-sync commit changes one file with 27 insertions and 6 deletions.
- git diff --check a93d07196dd8622d753cdd5f8617af7df29eb1cf..13d3cae0374e8e853a0c6e4996da7d391ef33a38 produced no output.
- git diff --name-only e1c74d683ead132eb3e98e230195c47c7b18c7d1..13d3cae0374e8e853a0c6e4996da7d391ef33a38 produced exactly the 13 paths above.
- /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py returned OK; scripts/check_doc_claims.py returned All anchors checked — no drift.
- tests/unit returned 91 passed in 1.33s; import/tests collected 126 tests. A fresh full import attempt was not counted as a pass because local 127.0.0.1:54322 was offline and 34 DB-backed cases errored with connection refused; no service start was authorized or attempted.
- Frozen API SHA-256 is exact 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6.
- R-DATA inspection found no data/, xlsx, Config.plist, credential, owner-value, receipt, or business-data path in the truth-sync commit.
- Target post-commit status contains only the pre-existing untracked web/ tree. Its same-command file-content manifest digest remained 866615740cae7adc1b3441134cc78fd0be8da943897f82179ef3f930b3b17af3 before edit, before commit, and after commit.

## Review Boundary

The assigned Operator must inspect the actual target range e1c74d683ead132eb3e98e230195c47c7b18c7d1..13d3cae0374e8e853a0c6e4996da7d391ef33a38 in the named worktree, not merely this binding artifact. Synthetic scratch-database test mutations are allowed only when the committed suites require them. No repair, policy activation, owner ruling, package/network action, default/managed database mutation, service action, web/ mutation, push, merge, deployment, lock, cursor consume, provider action, spend, cleanup, reset, rebase, or amend is authorized.

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e
- coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@6c11193d3ca5eb2a7214147309754241d5b884f3

Cursor at send: 0
