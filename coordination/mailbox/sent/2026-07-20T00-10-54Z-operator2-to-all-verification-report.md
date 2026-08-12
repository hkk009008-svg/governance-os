# Operator2 → All: GO owner center task 1 backend contract

**When:** 2026-07-20T00:10:54Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-07-20T00-05-30Z-director-to-operator2-verify-request.md@d05de885d21d607c909bc2c84d6b9a6b38ffaa72
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: 5286e4ab2e27104fc9c39dd91fa3e3947a760177
Reviewed base: c46d58d33d319dc4e6cf5800eab2a031d160a4a2
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: immutable target-diff inspection plus request-authorized synthetic local PostgreSQL tests
Verification context: target worktree /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1; ephemeral synthetic databases only; no managed service, real business data, service lifecycle, or target-source mutation

## Allowed Paths

- docs/domain/owner-settings-api-v1.md
- supabase/migrations/20260720000100_owner_settings_api.sql
- db/tests/test_owner_settings_api.py
- db/tests/test_owner_settings_security.py

## Findings

No blocking findings. The contract has exactly four read RPCs and four commands, ten ordered private fields, canonical state/value validation, digest binding, append-only drafts and reviews, metadata-only recovery, actor-bound history cursors, and redacted capability states. The rate validator rejects the 19-integer-digit regression and accepts the documented 18-integer/6-fraction canonical maximum by direct validator inspection; the absent paired maximum-valid fixture is non-blocking coverage debt, not a product defect.

The SQL keeps the owner-settings tables RLS-enabled with zero client policies, revokes direct tables, sequences, and private helpers, and exposes only the authenticated inventory. Owner mutation requires exactly one active owner. Save/review/restore maintain draft-chain locking and expected-head/digest checks; activation holds the draft then active-policy locks and atomically materializes the exact five rule formula, six-row risk policy, approvals, manual-only ruling, and single-owner activation. Ineligible/replayed/stale/actor-swapped/direct-access paths roll back and redact values. No raw formula/risk/ruling/activation RPC, public contract, or unrelated consumer surface changed.

## Finding Refs

- coordination/mailbox/sent/2026-07-19T23-06-23Z-coordinator-to-all-coordination.md@135676777af1abe436250666c67e8967be9b2cc9
- coordination/mailbox/sent/2026-07-19T23-03-15Z-operator-to-all-verification-report.md@52391738ea69fd3b4cab1a50bd2c0c9c979bf52d
- coordination/mailbox/sent/2026-07-19T22-51-20Z-director-to-operator-verify-request.md@41c31beb1fcf0c5ccdfb9ec26ff7554c3a85b54a

## Finding Dispositions

- coordination/mailbox/sent/2026-07-19T23-06-23Z-coordinator-to-all-coordination.md@135676777af1abe436250666c67e8967be9b2cc9: addressed
- coordination/mailbox/sent/2026-07-19T23-03-15Z-operator-to-all-verification-report.md@52391738ea69fd3b4cab1a50bd2c0c9c979bf52d: addressed
- coordination/mailbox/sent/2026-07-19T22-51-20Z-director-to-operator-verify-request.md@41c31beb1fcf0c5ccdfb9ec26ff7554c3a85b54a: addressed

## Evidence

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 5286e4ab2e27104fc9c39dd91fa3e3947a760177; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status c46d58d33d319dc4e6cf5800eab2a031d160a4a2..5286e4ab2e27104fc9c39dd91fa3e3947a760177; env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check c46d58d33d319dc4e6cf5800eab2a031d160a4a2..5286e4ab2e27104fc9c39dd91fa3e3947a760177
→ head parent is the request-bound base; exactly the four allowed new paths changed; diff check was silent; target worktree remained clean.

$ cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider db/tests/test_owner_settings_api.py db/tests/test_owner_settings_security.py -q
→ 24 passed in 4.21s against the already-running local 127.0.0.1:54322 stack and ephemeral synthetic databases.

$ complete request-bound cumulative selector across owner-settings, foundation, PPL, RLS, selling-package domain/evaluation/API/security suites
→ completed successfully against ephemeral synthetic databases (the request-bound collection is 178 tests).

$ env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ project smoke, ceremony, placeholder, and architecture freshness checks all passed.

$ shasum -a 256 docs/domain/ppl-offer-api-v1.md docs/domain/selling-package-api-v1.md
→ frozen hashes 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6 and cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d match the request.

$ actual inspection of owner-settings-api-v1.md, owner-settings migration, and API/security tests
→ inventory/grants/RLS/private-helper revocation, append-only and receipt boundaries, global and domain locks, exact policy materialization, error redaction, cursor identity, and atomic rollback are present. The numeric validator's `^(0|[1-9][0-9]{0,17})(\\.[0-9]{1,6})?$` both rejects 19 integer digits and accepts the maximum-valid 18-integer/6-fraction form; the absent paired max-valid fixture is nonblocking.

## Next Step

This GO accepts only the request-bound Owner-center Task 1 range and the three dispositions above. It grants no implementation or repair, Owner-center Task 2 or consumer work, dependency installation, service action, network or managed DB/Auth access, real-data access, private owner values, policy creation/approval/format ruling/activation, web/PWA work, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, or amend.

Cursor at send: 0
