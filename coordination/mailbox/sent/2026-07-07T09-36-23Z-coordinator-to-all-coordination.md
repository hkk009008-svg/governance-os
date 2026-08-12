# Coordinator → All: ledger alignment task-board

**When:** 2026-07-07T09:36:23Z · **From:** coordinator (online)

Task-board: ledger-t14-align-2026-07-07

Coordinator basis from fresh commands:
- Pipeline HEAD: acc7755 coordination: request operator verify protocol tooling fix.
- Pipeline publication boundary: main is 2 ahead of origin/main; origin/main is d4093ac. Publication is not part of this route.
- Evidence-ledger HEAD: 1f1b7c2 feat(import): add cross-source reconciliation readout instrument.
- Evidence-ledger publication boundary: local main is 4 ahead of origin/main; origin/main is b614df2. The t14-agency-load work is fast-forwarded locally and not published to origin/main from this route.
- Pipeline mailbox state before route: no prior coordinator broadcast; all four live-seat heartbeats stale; latest active request is director-to-operator verify-request for c82508a.
- Evidence-ledger durable boundary: latest t14 agency-load handoff records local-green branch readiness, non-interactive T16 GO, and optional owner-guided simulator acceptance still pending if the owner wants literal visual acceptance.

Start prompts:
- coordinator: continue task as coordinator on ledger
- director: continue task as director on ledger
- director2: continue task as director2 on ledger
- operator: continue task as operator on ledger
- operator2: continue task as operator2 on ledger

Seat assignments:
- coordinator owns packet coord-ledger-t14-align-route. Maintain this board, reconcile incoming reports, and do not edit evidence-ledger product files.
- director owns packet director-ledger-publication-decision. Refresh both repos, wait for operator and operator2 verification reports, frame the owner decision between accepting non-interactive T16 evidence and requiring visual simulator acceptance, then stop before publication unless the user gives an explicit later instruction.
- director2 owns packet director2-ledger-next-brief. Prepare the narrow next-task brief from current ledger evidence: PPL cost-month semantics/readout, T16 visual boundary if required, and post-publication queue. Do not make product-code changes in the planning pass.
- operator owns packet operator-pipeline-tooling-verify. Continue the existing verify-request at coordination/mailbox/sent/2026-07-07T09-09-04Z-director-to-operator-verify-request.md and issue GO, NITS, or FAIL on c82508a before any Pipeline publication decision.
- operator2 owns packet operator2-ledger-main-verify. Independently verify evidence-ledger range b614df2..1f1b7c2 from a clean env -u GIT_INDEX_FILE shell, include R-DATA checks, and issue GO, NITS, or FAIL before any ledger publication decision.

Side effects boundary:
- No push, force-push, lock claim, paid API spend, pod spend, or production generation is authorized by this route.
- Coordinator mail must not be consumed.
- All cross-repo git, pytest, and local verification commands must use env -u GIT_INDEX_FILE.

Join condition: coordinator may close this cycle only after packet coord-ledger-t14-align-route is committed, operator reports GO/NITS/FAIL for c82508a, operator2 reports GO/NITS/FAIL for b614df2..1f1b7c2, director records the owner-facing publication or visual-acceptance decision boundary, and director2 records the next-task brief or a no-op reason.

Cursor at send: 0
