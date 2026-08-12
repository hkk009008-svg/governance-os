# Coordinator → All: supersede two-owner gates and open one-user foundation

**When:** 2026-07-19T17:40:34Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation
Status: ONE-USER OWNER CONTRACT APPROVED; FOUNDATION TASK 1 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T16-01-59Z-coordinator-to-all-coordination.md@bf217ebb0a9cdd2a87198057ce31fdd13f99ca74
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 41d9f1d846d6e0928b520573094ae59846114df5
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Superseding owner contract

The prior route's requirement for matching decisions from two distinct owners is superseded for this private deployment. The product has one operational user, one owner account, one persistent authenticated owner session, one laptop, and one installed Windows PWA. The product has no user switcher and no second-owner matching workflow.

Legacy two-owner policy and format history remains immutable under `two_owner_v1`. New owner-center activation will use an additive `single_owner_v1` quorum that requires exactly one current active owner and one digest-bound approval from that owner. The frozen ordinary PPL and selling-package adapter inventories remain unchanged.

## Owner decisions and runtime truth

Gate B's public formula semantics are approved exactly as recorded in the design: incremental campaign contribution in KRW; `target_lines`; approved `linear_rate` mappings for `정률`, `반특`, `완특`, `직매입`, and `반반특` only when a valid owner rate exists; `정액` and null or unsettled terms fail closed to `NEEDS_INFO`; net-of-return/cancellation inputs; `owner_manual_without_ppl`; incremental costs deducted once; campaign-level action with no target break-even for mixed rates; target-slot timing with `booked_at` budget commitment; and six-decimal, final-only, half-up, post-round whole-KRW semantics.

Gate C's public policy semantics are approved exactly as recorded in the design: all five private limits are enabled; `Asia/Seoul`; booked-at calendar month; intent-only manual BUY and pilot TEST; evidence-first display; server-owned eligibility facts; TEST before NEGOTIATE only when the experimental choice is enabled; non-financial strategy text cannot change the calculated action; and the ordered actions are NEEDS_INFO, hard SKIP, BUY, TEST, NEGOTIATE, fallback SKIP.

Gate D's owner choice is `manual_only`.

The owner has not supplied the five commission rates or the five private risk amounts. Those values must remain unset, private, and uninferred until the owner center collects them. Gate B and Gate C are therefore decision-complete but not runtime-active. Gate D remains runtime `owner_ruling_required` until the single-owner record exists and a capability reread reports `manual_only`. Task 4 is not yet recorded `SKIPPED-NOT-APPLICABLE`.

## Open slice — Foundation Task 1 only

Director owns Task 1, `Version the policy quorum without changing the frozen v1 operations`, from the foundation plan. Start only from immutable target parent `41d9f1d846d6e0928b520573094ae59846114df5` with a clean target worktree.

Allowed target paths are exactly:

- `supabase/migrations/20260717000500_decision_policy.sql`
- `supabase/migrations/20260717000600_offer_evaluation.sql`
- `db/tests/test_ppl_decision_policy.py`

Work test-first. Add immutable quorum metadata and private shared predicates so `two_owner_v1` continues to require two matching current approvals while `single_owner_v1` requires exactly one current active owner and one matching approval. Replace every downstream hard-coded approval count with the shared predicate except the preserved v1 operations-only wrappers, which remain explicitly two-owner. Capability format resolution must use the matching versioned quorum.

The actual commit must contain no real formula, rate, amount, risk body, approval, format ruling, activation, owner-center API, web change, or managed-state effect. Commit only the bounded Task-1 paths, run the plan's focused and security verification, and submit the exact parent-to-head range to non-author Operator2 on a different model. Operator2 alone returns GO, NITS, or FAIL for that range.

Foundation Tasks 2 through 4 remain held until Task 1 receives committed GO. The owner-center plan remains held until the complete foundation range receives cumulative GO. Director may narrow, transfer, or reroute through a durable accepted handoff, but an author cannot verify authored work.

## Exact next trigger

Director reads this complete route, runs the Pipeline ledger start guard for `director`, confirms the exact target parent and three-path clean scope, then executes Foundation Task 1 and sends its immutable actual-range verify-request to Operator2.

## External-effect boundaries

No private owner value collection is authorized by this route.

No real policy creation is authorized by this route.

No format ruling or policy activation is authorized by this route.

No managed database or Auth mutation is authorized by this route.

No service lifecycle or dependency-network action is authorized by this route.

No real-data access, provider contact, booking, deployment, or spend is authorized by this route.

No evidence-ledger merge is authorized by this route.

No evidence-ledger push is authorized by this route.

No Pipeline push is authorized by this route.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized by this route.

Cursor at send: 0
