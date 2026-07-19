# Director → Operator2: Foundation Task 3 product-first eligibility parity

**When:** 2026-07-19T22:25:57Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: 8e4e7b8a91369dedf051e73fa11204ebef5128dd
Reviewed base: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: director-one-user-owner-policy-foundation-task3-review
Coordinator route: coordination/mailbox/sent/2026-07-19T22-14-36Z-coordinator-to-all-coordination.md@3a437a2c6ddb92f9050400f906e01f3441d0116b
Fixture-scope correction route: coordination/mailbox/sent/2026-07-19T22-07-51Z-coordinator-to-all-coordination.md@10cb1d681fd38b6af17ed63a6875dc40c1164b84
Initial Task 3 route: coordination/mailbox/sent/2026-07-19T21-53-13Z-coordinator-to-all-coordination.md@3318016b16826555e09dc878580adbce231707cb
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 2 GO: coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Implementation commit: 8e4e7b8a91369dedf051e73fa11204ebef5128dd
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6
Production SQL parent-diff SHA-256: 90dd8145373984da56da9741b8d30f31ed76c09e75adfc4c81680d1a21b2cdfc

## Outcome

Independently review the exact target range 2d3a76026ae0eff6413ba4270e6191f8fcba6948..8e4e7b8a91369dedf051e73fa11204ebef5128dd for Foundation Task 3 only. Confirm product-first package evaluation sources `experimental_allowed` only from the linked current `biz.ppl_choice_set_revisions` row for a `ppl` candidate and forces it false for every `no_ppl` candidate, resetting candidate-local state and failing closed when linked PPL choice state is absent. Confirm the server builds the Task 2 composite eligibility facts only after primitive calculation, constraint, budget, downside, quote, and candidate-mode facts exist, preserves the primitive vocabulary, passes the composites to `decision._ppl_select_action`, and rejects BUY, TEST, or NEGOTIATE unless its matching eligibility fact is true.

Confirm the paired regression holds synthetic facts constant except the linked choice-set revision's experimental flag: false does not select TEST, true selects TEST ahead of otherwise eligible NEGOTIATE, and the same private policy proves no-PPL cannot select TEST. Audit candidate-mode/source spoofing, null or missing linked state, stale loop-state leakage, policy-selected ineligible actions, and no-PPL TEST escape. Confirm candidate generation, missing-scenario exclusion, no-PPL generation, formulas, costs, timestamps, evidence, stable reads, public APIs, grants, operation inventory, owner-decision behavior, action labels, ranking, tie-break fields, and precedence are unchanged except for the existing ranking consumption of corrected server action values.

Confirm synthetic policy isolation is explicit only: `_seed_package` retains `policy=None` and `experimental_allowed=True`; exactly ten named evaluation compatibility tests and four named API tests construct and pass the existing Task 2 private composite policy; `_sealed_fixture` requires policy with no default; only the two new Task 3 regressions override `experimental_allowed`; and no GATE table, generic engine table, frozen fixture, adversarial table, hidden default, marker, or environment switch changed. Confirm the joint-calculation test reads one rows list, preserves its exact economic tuple, pins the PPL row to non-winning TEST, and pins the sole winner to no-PPL NEGOTIATE without changing ranking or tie-break implementation.

The fresh pre-commit read-only review of the exact three-path bytes found no Critical, Important, or Minor issue. Independently inspect the committed actual range and issue GO only if every behavior and boundary is satisfied with no unresolved hard finding; otherwise issue NITS or FAIL with exact evidence.

## Target Allowed Paths

Exactly these three target paths and no others:

- supabase/migrations/20260718000200_selling_package_evaluation.sql
- db/tests/test_selling_package_evaluation.py
- db/tests/test_selling_package_api.py

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 8e4e7b8a91369dedf051e73fa11204ebef5128dd
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 2d3a76026ae0eff6413ba4270e6191f8fcba6948..8e4e7b8a91369dedf051e73fa11204ebef5128dd
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 2d3a76026ae0eff6413ba4270e6191f8fcba6948..8e4e7b8a91369dedf051e73fa11204ebef5128dd
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_evaluation.py::test_joint_calculation_binds_hs_and_ppl_costs_once -q and require 1 passed
- run the exact fourteen compatibility nodes listed in the fixture-scope correction route and require 14 passed
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_evaluation.py -k 'test_requires_explicit_experimental or no_ppl_candidate_is_never' -q and require 2 passed
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py db/tests/test_ppl_offer_evaluation.py -q and require the complete cumulative profile to pass; Director observed 110 passed
- env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/scripts/ci_smoke.py
- shasum -a 256 /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/docs/domain/selling-package-api-v1.md /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/docs/domain/ppl-offer-api-v1.md
- inspect the actual range and recompute the SQL-only parent diff hash for exact product-first composite definitions, linked choice-set sourcing, per-candidate reset, matching action guards, explicit-only test policy selection, corrected winner expectation, frozen contracts, and absence of Task 4, private values, policy activation, owner-center/web, real or managed data, booking, spend, deployment, or another external effect

## Finding Refs

- coordination/mailbox/sent/2026-07-19T22-14-36Z-coordinator-to-all-coordination.md@3a437a2c6ddb92f9050400f906e01f3441d0116b
- coordination/mailbox/sent/2026-07-19T22-07-51Z-coordinator-to-all-coordination.md@10cb1d681fd38b6af17ed63a6875dc40c1164b84
- coordination/mailbox/sent/2026-07-19T21-53-13Z-coordinator-to-all-coordination.md@3318016b16826555e09dc878580adbce231707cb
- coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14

## Boundaries

This request authorizes Operator2 on gpt-5.6-terra to inspect Pipeline and the exact target range read-only, run only the listed checks against ephemeral synthetic databases through the already-running local Supabase listener at 127.0.0.1:54322, and publish exactly one canonical committed verification-report. It does not authorize implementation or repair, Foundation Task 4, owner-center work, dependency installation, service start/stop/restart/reset, network or managed database/Auth access, real business data, private owner values, policy creation/approval/format ruling/activation, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, amend, or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
