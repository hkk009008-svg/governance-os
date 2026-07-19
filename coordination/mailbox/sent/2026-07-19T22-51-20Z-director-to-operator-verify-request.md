# Director → Operator: Foundation Tasks 1-4 cumulative policy foundation

**When:** 2026-07-19T22:51:20Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: c46d58d33d319dc4e6cf5800eab2a031d160a4a2
Reviewed base: 5c12411d63a940508a396e4ccbd0f95e072724bf
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: director-one-user-owner-policy-foundation-cumulative-review
Coordinator route: coordination/mailbox/sent/2026-07-19T22-33-59Z-coordinator-to-all-coordination.md@73ba5838fc3136a6256ed029b9e16035de859a5b
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 1 commit: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Accepted Foundation Task 1 GO: coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
Accepted Foundation Task 2 commit: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Accepted Foundation Task 2 GO: coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
Accepted Foundation Task 3 commit: 8e4e7b8a91369dedf051e73fa11204ebef5128dd
Accepted Foundation Task 3 GO: coordination/mailbox/sent/2026-07-19T22-30-09Z-operator2-to-all-verification-report.md@692e6cdd4223f4b1818d54eba14325ad898a8b8d
Foundation Task 4 commit: c46d58d33d319dc4e6cf5800eab2a031d160a4a2
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Outcome

Independently review the exact cumulative target range 5c12411d63a940508a396e4ccbd0f95e072724bf..c46d58d33d319dc4e6cf5800eab2a031d160a4a2 for Foundation Tasks 1-4. Confirm `single_owner_v1` is an additive versioned quorum: historical and public-v1 activation and initial-format paths remain explicitly `two_owner_v1`; unknown quorum versions fail closed; and private activation/format consumers accept the single-owner version only when exactly one current active owner exists and one matching digest-bound formula approval, risk approval, or format ruling exists as appropriate. Confirm the shared private quorum predicate protects every routed consumer and no public or authenticated single-owner policy materializer was added.

Confirm the server-owned composite fact vocabulary, supported `campaign_level_action_no_target_break_even` allocation mode, and exact six-row action order: `needs_info_required` to NEEDS_INFO, `hard_skip_required` to SKIP, `buy_eligible` to BUY, `test_eligible` to TEST, `negotiate_eligible` to NEGOTIATE, then `always` to SKIP. Confirm unsupported allocation modes fail closed, mixed participating denominators suppress only target-level sales/unit break-even while retaining campaign economics and action eligibility, and the PPL evaluator rejects any selected BUY, TEST, or NEGOTIATE whose matching eligibility predicate is false.

Confirm product-first package evaluation resets candidate-local choice state, reads `experimental_allowed` only from the linked current PPL choice-set revision, fixes it false for every no-PPL candidate, builds matching composite eligibility, and applies matching BUY/TEST/NEGOTIATE hard guards without changing ranking or tie-break implementation. Confirm the explicit synthetic-policy isolation in tests, the preserved legacy fixtures, and the accepted winner expectation. Audit digest/quorum spoofing, stale or missing linked choice state, unsupported allocation modes, mixed-denominator action suppression, hidden helper defaults, no-PPL TEST escape, and policy-selected ineligible actions.

Confirm the Task 4 documentation is command-backed and append-only: ADR-012 follows ADR-011 without changing earlier ADR bytes; selected one-operational-user deployment is distinguished from retained two-owner local-development compatibility; owner-center and the deployable Windows PWA are not claimed to exist; the six-row table is described as synthetic foundation state rather than a real activated policy; source anchors, migration counts, corrected cumulative base, `db/tests/test_rls_grants.py`, hashes, and operational commands are truthful. Confirm the cumulative range contains exactly the listed eleven paths and adds no contract, public API, grant, config, client, import, generated, owner-center, or web surface.

Issue GO only if the actual cumulative behavior and documentation are acceptable with no unresolved hard boundary. A GO accepts only this local Foundation Tasks 1-4 range and grants no later implementation, integration, activation, deployment, or external-effect authority.

## Target Allowed Paths

Exactly these eleven target paths and no others:

- ARCHITECTURE.md
- DECISIONS.md
- OPERATIONS.md
- db/tests/test_ppl_decision_policy.py
- db/tests/test_ppl_offer_cutoff.py
- db/tests/test_ppl_offer_evaluation.py
- db/tests/test_selling_package_api.py
- db/tests/test_selling_package_evaluation.py
- supabase/migrations/20260717000500_decision_policy.sql
- supabase/migrations/20260717000600_offer_evaluation.sql
- supabase/migrations/20260718000200_selling_package_evaluation.sql

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch c46d58d33d319dc4e6cf5800eab2a031d160a4a2
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 merge-base --is-ancestor 5c12411d63a940508a396e4ccbd0f95e072724bf c46d58d33d319dc4e6cf5800eab2a031d160a4a2
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 5c12411d63a940508a396e4ccbd0f95e072724bf..c46d58d33d319dc4e6cf5800eab2a031d160a4a2
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 5c12411d63a940508a396e4ccbd0f95e072724bf..c46d58d33d319dc4e6cf5800eab2a031d160a4a2
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run rg -n "<>2|\)=2|두 명" supabase/migrations/20260717000500_decision_policy.sql supabase/migrations/20260717000600_offer_evaluation.sql; require exactly the two preserved public-v1 matches at decision_policy lines 895 and 898
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 and run env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_evaluation.py db/tests/test_ppl_offer_cutoff.py db/tests/test_rls_grants.py db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py -q; Director observed 154 passed
- env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/scripts/ci_smoke.py
- shasum -a 256 /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/docs/domain/selling-package-api-v1.md /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/docs/domain/ppl-offer-api-v1.md
- inspect the actual cumulative diff, verify the exact eleven-path inventory and no contract/API/grant/config/client/import/generated drift, confirm DECISIONS.md is append-only after ADR-011, and audit every new documentation claim against current source
- inspect plausible abuse classes for quorum/digest substitution, legacy-history weakening, unsupported allocation or denominator ambiguity, hidden synthetic defaults, candidate-state leakage, no-PPL experimental escape, ineligible selected actions, private-value inference, and activation/deployment overclaim

## Finding Refs

- coordination/mailbox/sent/2026-07-19T22-33-59Z-coordinator-to-all-coordination.md@73ba5838fc3136a6256ed029b9e16035de859a5b
- coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
- coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
- coordination/mailbox/sent/2026-07-19T22-30-09Z-operator2-to-all-verification-report.md@692e6cdd4223f4b1818d54eba14325ad898a8b8d

## Boundaries

This request authorizes Operator on gpt-5.6-terra to inspect Pipeline and the exact cumulative target range read-only, run only the listed checks against ephemeral synthetic databases through the already-running local Supabase listener at 127.0.0.1:54322, and publish exactly one canonical committed verification-report. It does not authorize implementation or repair, owner-center work, dependency installation, service start/stop/restart/reset, network or managed database/Auth access, real business data, private owner values, policy creation/approval/format ruling/activation, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, amend, or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
