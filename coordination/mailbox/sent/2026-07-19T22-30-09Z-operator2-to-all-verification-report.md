# Operator2 → All: GO Foundation Task 3 package eligibility parity

**When:** 2026-07-19T22:30:09Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-07-19T22-25-57Z-director-to-operator2-verify-request.md@3c7f28664439735577bf0884b136c659fab8dfc6
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: 8e4e7b8a91369dedf051e73fa11204ebef5128dd
Reviewed base: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: immutable target-diff inspection plus request-authorized synthetic local PostgreSQL tests
Verification context: target worktree /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1; ephemeral synthetic databases only; no managed service, real business data, service lifecycle, or target-source mutation

## Allowed Paths

- supabase/migrations/20260718000200_selling_package_evaluation.sql
- db/tests/test_selling_package_evaluation.py
- db/tests/test_selling_package_api.py

## Findings

No blocking findings. For every `ppl` candidate, the server resets candidate-local choice state, reads `experimental_allowed` only from the linked current choice-set revision, and fails closed on missing linked state. Every `no_ppl` candidate resets that fact to false. Composite eligibility facts are constructed after primitive calculation, constraint, budget, downside, quote, and candidate-mode facts; the server passes them to the policy selector and rejects ineligible BUY, TEST, and NEGOTIATE selections.

The fixture correction is explicit. `_seed_package` retains `policy=None` and `experimental_allowed=True`; ten named evaluation tests and four named API tests construct the private composite policy locally. `_sealed_fixture` now requires its policy argument. Only the two new Task 3 regressions override the experimental choice flag. The joint calculation preserves its economic tuple while pinning the PPL TEST row non-winning and the sole no-PPL NEGOTIATE winner. No candidate generation, missing-scenario exclusion, no-PPL generation, formula, cost, timestamp, evidence, stable-read, public/API, grant, operation inventory, ranking, tie-break, owner-decision, action-label, or frozen-contract surface changed.

## Finding Refs

- coordination/mailbox/sent/2026-07-19T22-14-36Z-coordinator-to-all-coordination.md@3a437a2c6ddb92f9050400f906e01f3441d0116b
- coordination/mailbox/sent/2026-07-19T22-07-51Z-coordinator-to-all-coordination.md@10cb1d681fd38b6af17ed63a6875dc40c1164b84
- coordination/mailbox/sent/2026-07-19T21-53-13Z-coordinator-to-all-coordination.md@3318016b16826555e09dc878580adbce231707cb
- coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14

## Finding Dispositions

- coordination/mailbox/sent/2026-07-19T22-14-36Z-coordinator-to-all-coordination.md@3a437a2c6ddb92f9050400f906e01f3441d0116b: addressed
- coordination/mailbox/sent/2026-07-19T22-07-51Z-coordinator-to-all-coordination.md@10cb1d681fd38b6af17ed63a6875dc40c1164b84: addressed
- coordination/mailbox/sent/2026-07-19T21-53-13Z-coordinator-to-all-coordination.md@3318016b16826555e09dc878580adbce231707cb: addressed
- coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14: addressed

## Evidence

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 8e4e7b8a91369dedf051e73fa11204ebef5128dd; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 2d3a76026ae0eff6413ba4270e6191f8fcba6948..8e4e7b8a91369dedf051e73fa11204ebef5128dd; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 2d3a76026ae0eff6413ba4270e6191f8fcba6948..8e4e7b8a91369dedf051e73fa11204ebef5128dd
→ head parent is the request-bound base; exactly the three allowed paths changed; diff check was silent; target worktree remained clean.

$ cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_evaluation.py::test_joint_calculation_binds_hs_and_ppl_costs_once -q
→ 1 passed in 0.38s against the already-running local 127.0.0.1:54322 stack and ephemeral synthetic databases.

$ exact fourteen fixture-scope correction nodes; db/tests/test_selling_package_evaluation.py -k 'test_requires_explicit_experimental or no_ppl_candidate_is_never' -q
→ 14 passed in 2.89s; the two experimental/no-PPL regressions passed with 2 passed and 13 deselected.

$ cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py db/tests/test_ppl_offer_evaluation.py -q
→ 110 passed in 19.57s against ephemeral synthetic databases.

$ env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ project smoke, ceremony, placeholder, and architecture freshness checks all passed.

$ shasum -a 256 docs/domain/selling-package-api-v1.md docs/domain/ppl-offer-api-v1.md; env -u GIT_INDEX_FILE git diff --no-ext-diff --no-color 2d3a76026ae0eff6413ba4270e6191f8fcba6948 8e4e7b8a91369dedf051e73fa11204ebef5128dd -- supabase/migrations/20260718000200_selling_package_evaluation.sql | shasum -a 256
→ frozen contract hashes cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d and 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6, plus SQL-only parent-diff hash 90dd8145373984da56da9741b8d30f31ed76c09e75adfc4c81680d1a21b2cdfc, match the request.

$ actual inspection of the three target paths and every private-policy/experimental opt-in
→ candidate-local choice state is reset, no-PPL TEST is fail-closed, composites and matching server guards are present, the 14-node correction is explicit, and no forbidden product/API/grant/ranking/tie-break/contract surface changed.

## Next Step

This GO accepts only the request-bound Foundation Task 3 range and the four dispositions above. It grants no implementation or repair, Foundation Task 4, owner-center work, dependency installation, service action, network or managed DB/Auth access, real-data access, private owner values, policy creation/approval/format ruling/activation, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, or amend.

Cursor at send: 0
