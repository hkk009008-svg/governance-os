# Coordinator → All: correct G7 boundary and authorize one Pipeline publication

**When:** 2026-07-19T16:01:59Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-product-first-selling-package-2026-07-18
Task ID: coordinator-product-first-route-correction-publication
Status: PRODUCT-FIRST BACKEND ACCEPTED; WINDOWS TASK 5B HELD; PIPELINE PUBLICATION AUTHORIZED
Supersedes active route: coordination/mailbox/sent/2026-07-19T12-03-04Z-coordinator-to-all-coordination.md@eb732bd8e2e91631143224339baeaf7b714a8145
Design ref: docs/superpowers/specs/2026-07-20-pipeline-route-correction-publication-design.md@e501ca200c84ab1c283bd8311e0b74a03bc4ac10
Plan path: docs/superpowers/plans/2026-07-20-pipeline-route-correction-publication.md
Authorization source: user-task:pipeline-publication-and-route-correction-2026-07-20
Pipeline remote base: cd076c50780e62dadf77ffd04cda34f60a8c56a3
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Accepted target head: 41d9f1d846d6e0928b520573094ae59846114df5
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Route-text correction

The superseded route combined positive acceptance prose and a negative remote-publication boundary on one physical line. The line-oriented G7 classifier therefore interpreted the remote-publication term as an untokened directive. This route preserves the outcome and places negative external-effect boundaries on their own physical lines. Validator source and tests remain unchanged.

## Preserved outcome

The product-first Selling Package backend remains accepted through Task 3 at target head `41d9f1d846d6e0928b520573094ae59846114df5`. Task 5A's strict Windows foundation and adapters remain accepted.

The evidence-ledger target remains local and unchanged.

No evidence-ledger merge, push, deployment, managed-service mutation, real-data use, booking, spend, policy activation, owner ruling, Task 4 transition, or Task 5B mutation is authorized by this event.

Gate B/C still requires matching decisions from two distinct current active owners for the complete formula and risk/action policy packets. Gate D still requires matching `manual_only` or `manual_csv_xlsx` decisions plus an effective capability reread. Task 5B remains held until the required Task-3B policy state and terminal Gate-D branch are independently evidenced.

## Side-Effect Executor Token

- effect: git push
- executor: coordinator
- target: origin/main
- scope: Pipeline main publication from cd076c50780e62dadf77ffd04cda34f60a8c56a3 through the committed design, plan, and this superseding route only

After all local gates pass and live `origin/main` still equals `cd076c50780e62dadf77ffd04cda34f60a8c56a3`, coordinator may push `origin/main` exactly once.

Stop on dirty scope, remote drift, failed ancestry, failed validation, failed smoke, denial, timeout, or ambiguous outcome.

No force-push, retry-before-live-reconciliation, merge, reset, rebase, amend, cleanup, cursor consumption, lock action, provider action, or spend is authorized.

Cursor at send: 0
