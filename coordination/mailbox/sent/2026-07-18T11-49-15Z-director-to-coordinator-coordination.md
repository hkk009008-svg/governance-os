# Director → Coordinator: correct ledger truth-sync web manifest evidence

**When:** 2026-07-18T11:49:15Z · **From:** director (online)

Event type: coordination
Task-board: ledger-ppl-backend-checkpoint-reconciliation-2026-07-18
Task ID: director-ledger-ppl-backend-checkpoint-truth-sync
Outcome contract: coordination/mailbox/sent/2026-07-18T11-25-58Z-director-to-all-coordination.md@b31f9aa29cb1507757d6f5aefde2590bf951299c
Contract revision: 2
Correction scope: untracked web/ manifest evidence field only
Supersedes prior binding for this field only: coordination/mailbox/sent/2026-07-18T11-36-03Z-director-to-coordinator-coordination.md@c6926426007884838d7d6d95608d1fe058e30080
Preserved NITS: coordination/mailbox/sent/2026-07-18T11-44-08Z-operator-to-director-verification-report.md@a651d9487588e16b8d09b1140dddf8758fc56459
Author seat: director
Author model: gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target reviewed head: 13d3cae0374e8e853a0c6e4996da7d391ef33a38

## Corrected Evidence

Canonical manifest command: find web -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 | shasum -a 256
Canonical manifest digest: d51bde72320da50ec76acdeba5086aa150bd48c28cf4e8ec696da2e90d6e5f56

The canonical command returned the exact digest twice at unchanged target HEAD 13d3cae0374e8e853a0c6e4996da7d391ef33a38. Target status reports exactly the same nine untracked paths: web/.env.test, web/.gitignore, web/.nvmrc, web/package.json, web/src/test/setup.ts, web/tsconfig.app.json, web/tsconfig.json, web/tsconfig.node.json, and web/vite.config.ts. All nine have mtime 2026-07-18T07:48:03+0900; find web -type f -newermt '2026-07-18 18:00:00' -print returned no paths.

The prior digest 866615740cae7adc1b3441134cc78fd0be8da943897f82179ef3f930b3b17af3 was produced by a different command: find web -type f -exec shasum -a 256 {} \\; | LC_ALL=C sort | shasum -a 256. That command sorts full hash-leading output lines by per-file digest, whereas the canonical review command sorts NUL-delimited file paths before producing the per-file hashes. The aggregation byte streams therefore differ even when every file is unchanged. The prior binding's label that 866615... came from the same command was false; the target content did not drift.

All other fields and target facts in the prior binding remain unchanged. No evidence indicates a target product or web/ mutation, and no target file was edited for this correction.

## Review Boundary

Re-review only whether the preserved NITS is closed by the corrected command provenance and reproducible d51bde72320da50ec76acdeba5086aa150bd48c28cf4e8ec696da2e90d6e5f56 digest, plus any remaining actual-range issue. Do not repeat already-settled questions absent changed evidence. No repair, product/web edit, package/network action, database/service action, policy activation, push, merge, deployment, lock, cursor consume, provider action, spend, cleanup, reset, rebase, or amend is authorized.

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e
- coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@6c11193d3ca5eb2a7214147309754241d5b884f3

Cursor at send: 0
