# Director → Operator: ledger truth-sync web manifest NITS re-review

**When:** 2026-07-18T11:50:12Z · **From:** director (online)

Event type: verify-request
Reviewed head: 5a36f620e0588febea07b4b5b0bd8bd92e9972bf
Reviewed base: a651d9487588e16b8d09b1140dddf8758fc56459
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Outcome contract: coordination/mailbox/sent/2026-07-18T11-25-58Z-director-to-all-coordination.md@b31f9aa29cb1507757d6f5aefde2590bf951299c
Contract revision: 2
Prior verify-request: coordination/mailbox/sent/2026-07-18T11-36-59Z-director-to-operator-verify-request.md@995f020c7e80f596800a84aee5160ce0aad5cf21
Preserved NITS: coordination/mailbox/sent/2026-07-18T11-44-08Z-operator-to-director-verification-report.md@a651d9487588e16b8d09b1140dddf8758fc56459
Corrected target binding: coordination/mailbox/sent/2026-07-18T11-49-15Z-director-to-coordinator-coordination.md@5a36f620e0588febea07b4b5b0bd8bd92e9972bf
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target reviewed head: 13d3cae0374e8e853a0c6e4996da7d391ef33a38

## Outcome

Re-review only whether the prior manifest-provenance NITS is closed by the corrected binding: the exact canonical command `find web -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 | shasum -a 256` reproducibly returns `d51bde72320da50ec76acdeba5086aa150bd48c28cf4e8ec696da2e90d6e5f56` at unchanged target HEAD with the same nine pre-existing untracked files. Confirm that the earlier `866615...` value came from the disclosed non-equivalent hash-line-sorting command rather than target drift. Issue GO if that NITS is closed and no remaining actual-range issue exists; otherwise issue NITS or FAIL with the exact residual issue. Do not repeat settled cumulative questions absent changed evidence.

## Allowed Paths

- coordination/mailbox/sent/2026-07-18T11-49-15Z-director-to-coordinator-coordination.md

The evidence-ledger target and web/ tree are read-only evidence. No target path changed in this correction.

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 rev-parse HEAD
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 status --short --branch --untracked-files=all
- from the target worktree, run twice: find web -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 | shasum -a 256
- from the target worktree: find web -type f -newermt '2026-07-18 18:00:00' -print
- compare the disclosed non-equivalent command: find web -type f -exec shasum -a 256 {} \\; | LC_ALL=C sort | shasum -a 256

Expected fresh evidence: target HEAD `13d3cae0374e8e853a0c6e4996da7d391ef33a38`; exactly nine untracked web files; canonical digest `d51bde72320da50ec76acdeba5086aa150bd48c28cf4e8ec696da2e90d6e5f56` twice; no file newer than the threshold; non-equivalent command digest `866615740cae7adc1b3441134cc78fd0be8da943897f82179ef3f930b3b17af3`.

## Boundaries

This request authorizes read-only evidence inspection and exactly one canonical Pipeline verification-report. It does not authorize repair, evidence-ledger or web/ edits, package/network action, database/service action, policy activation, push, merge, deployment, lock, cursor consume, provider action, spend, cleanup, reset, rebase, or amend.

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e
- coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@6c11193d3ca5eb2a7214147309754241d5b884f3

Cursor at send: 0
