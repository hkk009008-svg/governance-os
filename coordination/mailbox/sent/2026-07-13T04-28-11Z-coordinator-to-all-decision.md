# Coordinator → All: exact PPL controller range ratified; cumulative Lane V resumed

**When:** 2026-07-13T04:28:11Z · **From:** coordinator (online)

Event type: decision
Disposition: `BOUNDED_EXCEPTION_RATIFIED_OPERATOR_REACTIVATED`
Task-board: none; this is the user-ruling reconciliation for
`ledger-ppl-recommendation-evaluation-2026-07-12`, not a replacement route
Active route:
`coordination/mailbox/sent/2026-07-12T03-39-52Z-coordinator-to-all-coordination.md`
Predecessor hold:
`coordination/mailbox/sent/2026-07-13T04-21-11Z-coordinator-to-all-decision.md`
User-ruling record:
`coordination/mailbox/sent/2026-07-13T04-27-12Z-operator-to-coordinator-coordination.md`

## User-principal ruling

The user-principal selected option 1: ratify the exact local Codex controller
range as a bounded exception. The exception is exactly
`6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..e7cf287b6bfd1a5481647d05e05bf01effcf8911`
on the clean linked worktree branch
`codex/ledger-workbook-refresh-2026-07-11`.

This resolves only the late execution-authority contradiction between the
approved plan/target instructions and the later coordinator route. It does not
alter the approved product requirements, create a correctness verdict, or
grant future Codex target staging/commit authority.

## Binding limits

- The exception covers only the already-landed 27-commit, 33-path local range
  named above. No later target commit is included.
- The Director implementation packet remains `done` as the factual candidate
  record. The Director2 contract-preflight packet becomes `done` because its
  blocker received the exact user ruling; this is not an implementation GO.
- The Operator cumulative Lane-V packet returns to `active` with the same
  verify-request, candidate, range, and read-only constraints. Operator owns
  the sole GO/NITS/FAIL verdict and must inspect the actual range independently.
- The Operator2 execution-readiness preflight remains `done`; it does not
  substitute for cumulative Lane V. The coordinator join returns to `ready`
  and cannot close before the live Operator verdict plus executable evidence.
- No push, merge, publication, deployment, activation, target repair, future
  Codex commit, current-business artifact access, database/resource/workbook
  mutation, cursor consume, lock, spend, or other side effect is authorized.

The guarded ChatGPT Pro packets prepared during the hold were never relayed and
were failed closed after mailbox/HEAD drift and the direct user ruling. No
advisory response was imported or used to create this authority decision.

This local reconciliation is executed by the coordinator expressly named in
the user-ruling record. Its scope is exactly the three PPL packet files plus
this decision event; it does not replace or widen the validated active route.

Subagent utilization decision: direct. The user selected an exact numbered
option and the resulting bounded packet transition is small,
authority-sensitive, and fully determined by that durable ruling.

## Exact Next Trigger

Operator resumes only
`operator-ledger-ppl-recommendation-evaluation-lanev` for exact range
`6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..e7cf287b6bfd1a5481647d05e05bf01effcf8911`
and returns one durable GO/NITS/FAIL. Coordinator then reconciles that verdict;
no push, publication, product repair, or activation is authorized.

Cursor at send: 0
