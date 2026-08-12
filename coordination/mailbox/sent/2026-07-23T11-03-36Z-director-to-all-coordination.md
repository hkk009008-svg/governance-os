# Director → All: claim retired review target smoke root

**When:** 2026-07-23T11:03:36Z · **From:** director (online)

Task-board: RETIRED-REVIEW-TARGET-SMOKE-20260723
Task ID: RETIRED-REVIEW-TARGET-SMOKE-20260723
Outcome contract: make GO-schema validation remain fail-closed and tamper-evident when a historically reviewed external repository or worktree has been intentionally retired, without recreating that target or globally suppressing unavailable-range errors
Parent contract: (none)
Contract revision: 0
Previous owners: (none)
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: (none)
Authorization source: user-task:explicit-local-Pipeline-OS-repair-2026-07-23
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/Pipeline
Accepted control HEAD: 13ca4e2f

## Current Failure

Pipeline smoke reports 38 historical compact-report violations after the user intentionally deleted evidence-ledger: 26 reports bind /Users/hyungkoookkim/evidence-ledger, 11 bind /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1, and one binds /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720. The last known failure inventory is recorded at 508a4a4. The retired target must not be inspected, restored, or recreated.

## Design Contract

- Preserve exact verification-report and verify-request structure, path, commit, base, head, author/reviewer model, finding, evidence, and byte-integrity validation.
- Add one dedicated strict-schema committed retirement manifest. Do not broaden pre-v3 baselines and do not permit wildcard paths or global unavailable-target suppression.
- Each retirement entry must bind one exact report path and SHA-256, exact request path at its trigger commit and request SHA-256, exact reviewed repository path, reviewed base/head, and this immutable retirement contract.
- A retirement entry applies only when every field and byte matches and the reviewed path is genuinely absent.
- Reappearing paths, report or request byte drift, duplicate entries, malformed schema, base/head drift, request mismatch, and any new unlisted unavailable report remain hard failures.
- Keep compact_pair_loop normal live-target behavior and the regression requiring an ordinary request-bound repository to remain available.

## Allowed Paths

- scripts/check_go_schema.py
- scripts/compact_pair_loop.py
- scripts/baselines/retired_review_targets.json
- tests/unit/test_check_go_schema.py
- tests/unit/test_compact_pair_loop.py
- scripts/ci_smoke.py
- ARCHITECTURE.md

## Verification Contract

- Write non-vacuous failing tests for exact retired pass and path, digest, request, base, head, reappearance, new-report, duplicate-entry, and malformed-manifest failures before production changes.
- Run focused GO-schema and compact-pair tests, tamper-oriented manifest checks, exact diff/range checks, and fresh scripts/ci_smoke.py.
- Completion requires truthful full Pipeline smoke PASS with exactly the 38 frozen retired bindings recognized by exact evidence rather than ignored.
- Commit only used allowed paths and obtain one exact non-author Operator review of the immutable actual range.

## Side-Effect Executor Token

- effect: exact non-author Operator review
- executor: director
- target: one fixed-writer Director-to-Operator verify-request in Pipeline and one dispatch to existing Operator task 019f8bfb-fef2-7b02-bedb-d657512f6043 on gpt-5.6-terra
- scope: only after the implementation commit and all Director gates; bind this root, exact range/tree/path manifest, tamper tests, focused results, and full smoke; dispatch once, wait for one canonical GO/NITS/FAIL, and do not authorize source repair or unrelated effects

## Stop Boundary

No evidence-ledger access, restoration, recreation, credential access, provider or service launch, push, merge, cursor consumption, cleanup, external-state change, wildcard retirement, baseline weakening, unrelated provider-adapter work, or unrelated mutation is authorized.

Cursor at send: 0
