# Director → All: Lane A TDD RED blocked by prohibited local service start

**When:** 2026-07-18T16:38:11Z · **From:** director (online)

Event type: coordination
Task-board: ledger-product-first-selling-package-2026-07-18
Task ID: director-selling-package-domain-task1
Parent route: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md@513f6902b7236ad7bce9030a6aca27da316a1064
Reviewed contract GO: coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target start: 16d1e4dfd204bc1344be93cffa20f99ca1a16b43
Owner: director
Status: BLOCKED before implementation

## Finding

The routed Task-1 synthetic tests collect successfully: 11 tests across db/tests/test_selling_package_domain.py and db/tests/test_selling_package_security.py. The required executable RED is not valid because every fixture fails before migrations or RPC calls: PostgreSQL at 127.0.0.1:54322 returns Connection refused. A listener check finds no process on 54322, and Docker reports no daemon socket. OPERATIONS.md documents the local Supabase stack as the required dependency and `supabase start` as the remedy.

The parent route explicitly withholds service start/stop authority. Therefore the Director cannot lawfully start Docker Desktop or the local Supabase stack, and the test-first boundary forbids beginning production SQL without observing a product-specific RED.

## Preserved target WIP

Only these routed synthetic RED-test paths were added and remain uncommitted:

- db/tests/test_selling_package_domain.py
- db/tests/test_selling_package_security.py

The pre-existing untracked web/ peer work remains untouched. No migration, grant pin, implementation commit, verify-request, push, merge, deploy, managed database access, policy activation, real-data action, cursor consume, or lock action occurred.

## Resume condition

Resume when the local stack is already listening on 127.0.0.1:54322, or when the user separately authorizes the exact service effects needed to start Docker Desktop and run local `supabase start` for this target. Then rerun the two-test executable RED before any production implementation.

Cursor at send: 0
