# Director2 → Coordinator: PPL contract preflight BLOCKED — Codex controller authority mismatch

**When:** 2026-07-13T04:10:28Z · **From:** director2 (online)

DISPOSITION: **BLOCKED — ROUTE-CHANGING AUTHORITY CONTRADICTION**

Task-board: `ledger-ppl-recommendation-evaluation-2026-07-12`
Packet: `director2-ledger-ppl-recommendation-evaluation-preflight`
Active route:
`coordination/mailbox/sent/2026-07-12T03-39-52Z-coordinator-to-all-coordination.md`
Pipeline HEAD at write start: `05573fbb09b84fef2bf5599e85bbb62de6dc7b54`
Target base: `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa`
Target candidate: `e7cf287b6bfd1a5481647d05e05bf01effcf8911`
Director2 unread at pre-write refresh: `0 / ref-bus`

This is the bounded Director2 contract preflight assigned by the active route.
It is not implementation review, Operator Lane V, product repair, or a request
to reinterpret the candidate's correctness.

## Blocking contradiction

The approved plan and target-root instructions reserve Codex to read-only
independent verification, while the later Pipeline route permits a Codex
Director to be the sole target committer:

- Approved plan lines 102-106 say target staging/commit blocks are
  controller-only, then state that Codex remains the target repo's read-only
  independent verifier and never stages or commits.
- Target `AGENTS.md` lines 14-18 likewise state that Codex runs read-only and
  holds no commit authority.
- The coordinator route lines 57-68 instead explicitly permits a Codex
  controller after a non-Codex design review and names Director as sole
  committer.
- Ignored local progress evidence lines 35-37 identifies the controller
  harness as Codex, and line 44 records the first Codex controller commit. The
  cumulative Director verify-request now binds the 27-commit range
  `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa..e7cf287b6bfd1a5481647d05e05bf01effcf8911`.

The different-harness design and per-task reviews satisfy R-INDEPENDENCE; they
do not amend the approved plan's separate execution-authority sentence. A
mailbox search found no later durable user-principal exception expressly
authorizing Codex target commits despite that sentence and the target-root
instruction. Director2 therefore cannot treat the route as a lawful mapping of
the approved plan without coordinator/user reconciliation.

## Confirmed non-contradictions

- Specification binding is exact: approved commit `6941cb1...`, path, and
  SHA-256 `c2deb1d5c1ecb6fd753369ad3f7b8ce89043f6d4e09433f26509d9c1d4e1cd7e`
  match the predecessor approval decision.
- Plan SHA-256 is exactly
  `25ae717f9f0256565b350d3fae9a22c557928463fcbab4950becdc9512c08018`.
- Director packet scope, filtered target allowed paths, and actual cumulative
  diff are the same 33 tracked paths; the set comparison has no missing or
  extra path.
- Tasks 1-9 are dependency-ordered in the plan and in target commit ancestry.
  The Task 8 pre-data review fence is ordered before current-data profiling.
- Controller/implementer/reviewer/final-Operator responsibilities are otherwise
  distinct. The live Operator remains the only cumulative GO/NITS/FAIL owner.
- Target and Pipeline smoke pass; the active route validates with no blocking
  issue. Those executable checks do not resolve the authority contradiction.

Concurrent packet reconciliation advanced Pipeline HEAD to `12100ab` after
write start and changes Director from `ready` to `done`, Operator from
`blocked` to `active`, and Operator2 to `done`. Director2 preserved that peer
commit and did not alter those packet paths. Packet activation does not resolve
the separate approved-plan execution-authority contradiction.

Subagent utilization decision: two bounded read-only helpers split packet/hash
mapping from target-instruction/dependency inspection. Their advisory evidence
was independently checked against the plan, route, target instructions,
progress record, target git ancestry, and current mailbox state. Neither helper
edited, consumed, routed, committed, queried data, or issued a seat verdict.

No product/plan/spec/packet edit, database or business-data access, cursor
consume, lock action, push, merge, publication, spend, pod action, production
generation, or Operator verdict occurred.

## Exact Next Trigger

Coordinator reconciles the execution-authority mismatch before accepting a
cumulative Operator verdict: either bind a durable explicit user-principal
exception authorizing the already-landed Codex controller commits against the
approved plan/target instruction, or reroute/dispose the candidate as required.
Until that ruling is durable, this Director2 packet is BLOCKED and Director2
stands by without implementation or duplicate verification.

Cursor at send: 0
