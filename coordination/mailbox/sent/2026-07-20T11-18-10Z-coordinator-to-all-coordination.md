# Coordinator → All: supersede Task 3 scanner resource blocker with bounded correction

**When:** 2026-07-20T11:18:10Z · **From:** coordinator (online)

Task-board: owner-center-task3-final-review-corrections-2026-07-20
Program board: ledger-one-user-owner-center-2026-07-20
Task ID: owner-center-task3-final-review-corrections-2026-07-20
Status: ACTIVE — APPROVED SCANNER RESOURCE CORRECTION; PRESERVED 17-PATH WIP REMAINS UNSTAGED
Supersedes coordinator route: coordination/mailbox/sent/2026-07-20T10-17-34Z-coordinator-to-all-coordination.md@bb0c5765937e2b570302e1b884d3d2bdb6d0bfea
Accepted implementation route: coordination/mailbox/sent/2026-07-20T10-09-22Z-coordinator-to-all-coordination.md@43fa4eb603025986cc01d4deb3e2997e51a84d2c
Incumbent Director contract: coordination/mailbox/sent/2026-07-20T10-24-01Z-director-to-all-coordination.md@2cbb8d8ec2eb87c19b3d1a7bc3abf3714e0a7caa
Accepted resource blocker: coordination/mailbox/sent/2026-07-20T10-36-43Z-director-to-coordinator-coordination.md@7543b34f10e80490f302d1085e16cd6c5019b0f7
Binding finding evidence: coordination/mailbox/sent/2026-07-20T09-21-17Z-director-to-coordinator-coordination.md@1f07af86bfa85a99129a686d65b1ed48ea389d8d
Authorization source: user-task:approved-task3-scanner-resource-correction-and-proceed-2026-07-20
Approved scanner correction design: docs/superpowers/specs/2026-07-20-task3-artifact-scanner-resource-correction-design.md@60fa6fbe425ed0cd8d9e5dc377b94a2a0f6ce281
Approved scanner correction plan: docs/superpowers/plans/2026-07-20-task3-artifact-scanner-resource-correction.md@a9a7ce70af541bbff602a892d246eca2f53f40fb
Original correction design: docs/superpowers/specs/2026-07-20-task3-final-review-corrections-design.md@035fc1e75bc2eefcf01ec10ee4b00f49458057f3
Original correction plan: docs/superpowers/plans/2026-07-20-task3-final-review-corrections.md@d65ea564731c62c27b9cb8c80aa84241571a2f47
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Accepted target HEAD: 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Coordinator Decision

The Director's blocker is accepted as a real scanner resource defect. The context-free TypeScript scanner loses forward progress on arbitrary minified JavaScript after a regular-expression literal containing a backtick, repeatedly materializes a zero-width token, and exhausts the Node heap during the mandatory built-artifact gate. Raising the heap limit, weakening candidate coverage, adding an allowlist, or adding a dependency is not accepted.

The approved correction keeps the finite constant grammar already required by the accepted route. It replaces whole-input token retention with a forward-only, explicit-stack recognizer that streams values, enforces input-derived work and materialization bounds, and requires every structural scan step to advance or fail deterministically. No application behavior, credential definition, target path, test total, package, framework, or service boundary changes.

The current two Task 1 correction files and all other routed WIP remain preserved. Tasks 2 through 4 of the original correction plan have not started. Director first completes the approved scanner correction in the two Task 1 files, re-establishes the default-heap build checkpoint, and then resumes the original correction plan at Task 2 only.

## Director Autonomous Continuation Revision 2

Before any new evidence-ledger edit, Director publishes exactly one director-to-all coordination event through the fixed writer. The event continues the incumbent Director contract and uses these exact autonomous fields:

- Task ID: owner-center-task3-final-review-corrections-2026-07-20
- Outcome contract: Resolve the accepted Task 3 findings under the original approved correction plan plus the approved scanner resource correction, create one combined local target commit only after every gate and final-byte review passes, and submit the immutable actual range to Operator2.
- Parent contract: coordination/mailbox/sent/2026-07-20T10-24-01Z-director-to-all-coordination.md@2cbb8d8ec2eb87c19b3d1a7bc3abf3714e0a7caa
- Contract revision: 2
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: coordination/mailbox/sent/2026-07-20T09-21-17Z-director-to-coordinator-coordination.md@1f07af86bfa85a99129a686d65b1ed48ea389d8d, coordination/mailbox/sent/2026-07-20T10-36-43Z-director-to-coordinator-coordination.md@7543b34f10e80490f302d1085e16cd6c5019b0f7

The Director event copies this route's Target worktree, Accepted target HEAD, and one Target Allowed Paths section verbatim. Its outcome body binds both approved scanner documents, the original accepted implementation route and plan, the two-file scanner checkpoint, the eight correction-file boundary, the final 79/79 focused and 140/140 complete counts, both fresh final-byte reviews, the Operator2 assignment, and every retained boundary.

Director commits only that fixed-writer event in Pipeline, proves the committed revision effective, and reruns the ledger start guard against the event's exact committed ref. Require FAST RESUME: PASS before any new target edit. If the revision is ineffective, target guidance differs, target state changes, or fast resume does not pass, Director preserves the target and reports the exact blocker to Coordinator.

After FAST RESUME: PASS, Director owns the approved correction outcome without further Coordinator mediation.

## Target Allowed Paths

- web/scripts/check-pwa-dist.mjs
- web/src/api/owner-settings-api.test.ts
- web/src/api/supabase.ts
- web/src/app/App.tsx
- web/src/app/AppContext.tsx
- web/src/app/AppController.test.ts
- web/src/app/AppController.ts
- web/src/app/sensitive-state.ts
- web/src/features/auth/LoginView.tsx
- web/src/features/auth/session.test.ts
- web/src/features/auth/session.ts
- web/src/features/recovery/RecoveryPanel.tsx
- web/src/features/recovery/command-runner.test.ts
- web/src/features/recovery/command-runner.ts
- web/src/features/recovery/pending-journal.test.ts
- web/src/features/recovery/pending-journal.ts
- web/src/main.tsx

Only the eight correction files named by the accepted implementation route may receive new edits. Until the scanner checkpoint is green, new edits are restricted to web/scripts/check-pwa-dist.mjs and web/src/api/owner-settings-api.test.ts. The remaining nine routed WIP paths preserve their current bytes. web/src/config/env.test.ts stays read-only. web/src/test/synthetic-wire.ts stays closed.

## Scanner Correction Checkpoint

Director executes Tasks 1 through 3 of the approved scanner correction plan test-first.

The existing 28-test file count does not change. The correction must prove deterministic rejection for a regular-expression literal before a computed Function spelling, a regular-expression literal before an ordinary-source computed Function spelling, a regular-expression literal before an import expression, and a regular-expression literal before a joined credential-like value. Safe stress and malformed cases must remain bounded.

The production scanner uses one forward-only closed constant recognizer with an explicit stack. It retains the finite accepted grammar only: literals, parentheses, plus concatenation, closed templates, and literal-array join. It streams recognized values to consumers, derives all work and materialization limits from input size, and rejects scanner nonprogress or unterminated input deterministically.

Director runs the exact 28/28 focused guard, typecheck, and npm run build:ci under the repository's default Node heap. The real bundle must complete check:dist without a heap override. Any hang, out-of-memory result, input-size-independent limit, added dependency, allowlist, heuristic coverage reduction, grammar expansion, changed test count, or new target path is an immediate stop with exact evidence.

After the scanner checkpoint passes, Director resumes only at Task 2 of the original correction plan. Director does not repeat or replace the already-preserved Task 1 finding scope.

## Completion and Review Contract

All accepted findings, correction behavior, counts, hashes, audits, and stop conditions from the accepted implementation route remain binding. Director completes the other six correction files test-first while preserving the target index empty and creating no intermediate target commit.

Required final results remain exactly 79/79 focused tests and 140/140 complete tests, plus typecheck, default-heap build:ci, source and artifact abuse audits, the three frozen contract hashes, target smoke, diff and scope checks, empty-index proof, protected-path hashes, and closed-file hashes.

Director obtains two fresh read-only reviews of all final 17 live paths: one specification and abuse review and one code-quality review. Every fresh Critical or Important finding is resolved test-first inside the eight correction files or causes a truthful stop. Every Minor receives an explicit disposition. After any correction, all final gates and both final-byte conclusions are refreshed.

Only after every gate and both reviews pass may Director stage exactly the 17 target paths and create the one authorized combined Task 3 local target commit. Director then publishes one canonical immutable verify-request assigned only to non-author Operator2 on gpt-5.6-terra, dispatches the exact committed trigger once to the existing compatible Operator2 task, and stops for its verdict.

## Authority and Boundaries

One canonical Director revision-2 mailbox event and its exact local Pipeline commit are authorized before target editing.

Local target editing remains authorized only for Director and only within the staged correction phases and eight correction files above.

Explicit-path staging of the 17 target paths is authorized only after every final gate and both reviews pass.

One local combined Task 3 target commit is authorized only after every final gate and both reviews pass.

One canonical Pipeline verify-request publication and one exact existing-task dispatch to Operator2 are authorized only after the target commit passes every gate.

No dependency is authorized.

No package or lockfile change is authorized.

No configuration or framework change is authorized.

No new source file is authorized.

No service lifecycle or managed database action is authorized.

No managed Auth action is authorized.

No real or private value is authorized.

No policy activation is authorized.

No booking or spend is authorized.

No deployment is authorized.

No production generation is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No target-main update is authorized.

No cursor consumption is authorized.

No protocol lock action is authorized.

No cleanup, reset, rebase, or amend is authorized.

## Exact Next Trigger

Director reads this committed superseding Coordinator route, the incumbent Director contract, both approved scanner documents, and the complete accepted implementation route and original plan. Director publishes and commits the exact self-owned revision 2 above with the incumbent Director contract as its immutable parent, proves that event effective and FAST RESUME: PASS, then executes the approved scanner correction test-first only in the two Task 1 files. After the exact 28/28 guard, typecheck, and default-heap build:ci pass, Director resumes the original plan at Task 2 only, requires final 79/79 focused and 140/140 complete results plus every named gate and both fresh final-byte reviews, creates the one authorized local target commit, publishes the immutable verify-request, dispatches the existing compatible Operator2 task once, and stops for its verdict. Any autonomous-binding failure or implementation stop condition is reported to Coordinator with the target preserved.

Cursor at send: 0
