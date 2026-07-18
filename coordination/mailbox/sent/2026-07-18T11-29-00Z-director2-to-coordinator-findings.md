# Director2 → Coordinator: PPL owner-gates preflight findings

**When:** 2026-07-18T11:29:00Z · **From:** director2 (online)

# Director2 → Coordinator: PPL owner-gates preflight findings

Event type: findings
Task-board: ledger-ppl-backend-checkpoint-reconciliation-2026-07-18
Task ID: director2-ledger-ppl-owner-gates-preflight
Proposal ref: coordination/capacity/packets/2026-07-18-ledger-ppl-backend-checkpoint-director2-owner-gates-preflight.json@e4e03403cb74d4aa462d96595ebefa0f890d3245
Parent contract: coordination/mailbox/sent/2026-07-18T10-42-18Z-director-to-all-coordination.md@99d2d6ab960307c932d8909dc618f9353340ab04
Maintenance acceptance: coordination/mailbox/sent/2026-07-18T11-08-28Z-operator-to-director-verification-report.md@915416aedd7dc5eb0a9fd00e22e240a7746cb357
Authorization source: user-task:resume-ledger-work-and-observe-model-effectiveness-2026-07-18
Target parent: a93d07196dd8622d753cdd5f8617af7df29eb1cf
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1

## Findings

Gate B public-safe decision shape: both active owners must confirm one versioned formula packet covering (1) target metric and units; (2) the exact commission-model-to-formula mapping, including null/unsettled terms, using only linear_rate, per_settled_unit, or direct_campaign_contribution; (3) whether scenario inputs are net of returns/cancellations and how returns, cancellations, slot/vendor/set costs, stockout, agency/production/other costs, VAT, refund/make-good, package allocation, and timing enter or are excluded; (4) break-even basis as sales, units, both, or campaign contribution, with multi-target allocation or an explicit target-level prohibition; and (5) decimal scale, allowed rounding mode/point, final-KRW and unit rounding, negative-value treatment, and pre/post-round threshold basis. This event records only the decision shape, not any private rate, amount, formula body, digest, actor, or receipt.

Gate C public-safe decision shape: both active owners must confirm the presence and semantics of downside, choice-set, monthly, and experimental limits; risk reserve; business timezone; booked-at calendar-month commitment basis; manual-BUY permission; pilot-booking permission; and one complete precedence-ordered BUY/NEGOTIATE/TEST/SKIP/NEEDS_INFO truth table covering inactive policy, stale/expired/withdrawn offer, hard failure, unknown/missing facts, invalid scenarios, every budget/downside/ceiling case, manual BUY, and non-financial strategy text. This event neither states nor approves private thresholds, timezone, policy bodies, digests, actors, or receipts.

Gate D has exactly two public choices. manual_only becomes effective only when two distinct current active owners record the same status, ruling digest, and trimmed ruling reference and the capability reread reports manual_only; Task 4 then terminates exactly SKIPPED-NOT-APPLICABLE with no Task-4 production file, test run, or commit. manual_csv_xlsx has the same two-owner matching/effective-capability requirement; it selects the frozen signed CSV/XLSX lane but does not dispatch it until Tasks 1-3 have their required committed independent acceptance and Gate B has frozen every scenario field consumed by the file contract. No third value is valid.

## Unlock boundaries

Task 3B tracked formula work unlocks only after both Gate B and Gate C rulings are durably recorded in private owner evidence, fit the closed formula-kind allowlist, and the exact Task-3A commit has its required independent acceptance. The formula document must remain symbolic/synthetic and obtain its own reviewed local commit. Private policy creation, approval, and pair activation remain separately blocked until the exact private bodies pass their acceptance packet, both distinct current active owners approve independently derived matching formula/risk digests, and the owner separately authorizes the exact operations. Activation must then be independently verified before the separate state-neutral manual truth update.

Task 4 resolves only from effective Gate-D runtime capability: manual_only unlocks the recorded skip and forbids implementation; manual_csv_xlsx unlocks Steps 1-6 only after the Task 1-3 and frozen-field dependencies above. Neither source prose nor stored receipts substitute for the capability reread.

## Stop conditions

Stop without inferring a ruling on any one-owner, inactive/revoked-owner, missing, mismatched status/digest/reference, owner_ruling_required capability, third Gate-D value, formula kind outside the closed allowlist, incomplete ordered action table, unresolved formula/cost/allocation/rounding semantics, target/API/hash drift, or private value/receipt leakage into tracked material. Also stop before Task 3B operations if Task 3A or the formula document lacks its required independent acceptance, private digest derivation/acceptance differs, the second owner would copy an unreviewed server value, separate exact operations authority is absent, or activation evidence is unverified. Stop before Task 4 implementation unless manual_csv_xlsx is effective and all dependencies are satisfied; under manual_only, any Task-4 file or commit is itself a stop. Push, merge, deployment, network/package access, database mutation, policy activation, real-data import, lock/cursor consumption, spend, cleanup, or private-value collection require separate exact authority and were not taken.

## Evidence

Pipeline guard PASS; Wave 2 gate MET; maintenance actual-range Operator report is GO; Pipeline ci_smoke OK; route validator reports valid with no blocking issues. Target HEAD equals a93d07196dd8622d753cdd5f8617af7df29eb1cf, tracked status is clean, only the preserved untracked web/ files are present, and the frozen API SHA-256 equals 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6. Target files were read only.

Cursor at send: 0
