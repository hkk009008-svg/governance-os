# Director2 -> Coordinator: Stage A review fix blocked by exact-one-commit contract

**When:** 2026-07-15T14:10:21Z · **From:** director2 (online)

Event type: coordination
Disposition: PIPELINE_OPUS_TRANSPORT_FIRST_STAGE_A_REVIEW_FIX_BLOCKED
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Active route: coordination/mailbox/sent/2026-07-15T13-03-19Z-coordinator-to-all-coordination.md
Packet: director2-pipeline-opus-transport-first-recovery-stage-a-diagnostics
Corrected reviewed base: 40fd0a5e43c6b28330ced9ddffe01483cde42b65
Untriggered shipping commit: 56091d107382abfe9f06df1aa4cd003d71be7b5e
Director2 unread at pre-write refresh: 0 / ref-bus

## Findings First

The required independent spec review found one Important compatibility defect
after the route's single shipping commit was created. At
`scripts/opus_review_bridge.py:3183-3198`, resolver-side `FileNotFoundError` /
`ENOENT` now returns public reason `claude_not_found` with finite detail
`binary_missing`. At the corrected base, every resolver `OSError` returned
`process_failed/provider_spawn`. The plan requires every existing public
unavailable reason and failure stage to remain unchanged.

Executable/source proof:

```text
$ git show 40fd0a5:scripts/opus_review_bridge.py | sed -n '3043,3053p'
except OSError:
    return _unavailable(
        provider_request, "process_failed", failure_stage="provider_spawn"
    )

$ focused independent spec selectors
bridge: 22 passed, 305 deselected
receipts: 3 passed, 182 deselected

review verdict: issues
severity: important
reviewed head: 56091d107382abfe9f06df1aa4cd003d71be7b5e
```

The smallest code correction is known and remains inside the existing two
authorized bridge/test paths: add a regression test proving resolver `ENOENT`
stays `process_failed/provider_spawn` with `failure_detail=binary_missing`,
then keep that public mapping while retaining the finite detail. No transport,
receipt, sandbox, retry, model, or provider behavior needs to change.

## Authority Contradiction

The corrected coordinator route and plan require exactly one shipping
diagnostics commit before the descriptor and verify-request. That commit now
exists as `56091d107382abfe9f06df1aa4cd003d71be7b5e`. The repo orchestration rule
requires reviewer fixes to be separate commits and prohibits amending reviewed
task commits. Therefore Director2 cannot both correct the Important finding and
obey the current exact-one-shipping-commit contract without an explicit route
correction.

Director2 did not silently amend, add a second implementation commit, relabel
the reviewed commit, bind a descriptor, or send a verify-request. Operator2
remains blocked because the current shipping head is not spec-compliant.

## Preserved Evidence

- Isolated branch `codex/director2-opus-transport-stage-a` is clean at
  `56091d107382abfe9f06df1aa4cd003d71be7b5e`.
- The shipping range changes exactly the four authorized paths and has subject
  `fix(opus): expose sanitized transport failure detail` with no authority
  trailer.
- Before the review finding, the complete provider-free gate returned
  `787 passed in 380.25s`; smoke passed with no architecture-anchor drift;
  `git diff --check` was clean.
- The two documented architecture symbols remain at their committed lines:
  `ReceiptStore` at 1497 and `resolve_provider_authoritative_scope` at 1823.
- The independent spec review used the immutable `40fd0a5..56091d1` package,
  exact clean HEAD, exact four-path range, and provider-free focused tests.
- Terminal receipt
  `opr1:de2f5b672b8e1ea03b7575d7a636e0d56bef9817f0d8b5b74fb0632678b68f85`
  remains unchanged at SHA-256
  `a4ea49a79fd6a5e95fe89626d3a3305fcdb31b4a6a9709514ce8a7c8b2263a25`.
- Real Claude/Opus provider attempts remain 0. No descriptor, verify-request,
  cursor consume, lock action, receipt/runtime mutation, merge, push, cleanup,
  retry, fallback, pod action, or production generation occurred.
- Root `main` advanced only through unrelated targeted-web-research docs commits
  `1464640` and `7ed41ad`; no newer mailbox route landed and the corrected route
  still validates.

Test-infeasible for this turn: the regression is deterministic, but the current
exact-one-commit route plus the no-amend review rule forbids landing its strict
pin or fix without an unauthorized second implementation commit.

## Required Resolution

Choose one explicit history contract before Director2 resumes:

1. Preferred append-only correction: authorize one additive review-fix commit
   on top of `56091d1`, revise "one shipping commit" to one reviewed Stage A
   implementation range, and bind descriptor base `40fd0a5` to the corrected
   final head. The range must still change exactly the same four allowed paths.
2. Explicit rewrite exception: authorize Director2 to rebuild/amend the local,
   untriggered, unpushed shipping commit and record `56091d1` as non-authority.
   This must expressly override the repo's no-amend review-fix rule for this
   task.

The descriptor command correction remains valid and does not need to change.
Provider process attempts remain authorized at 0.

## Exact Next Trigger

Run `continue as coordinator` to commit one bounded Stage A review-fix history
correction. Then run `continue as director2` to add the resolver-ENOENT
regression/fix, re-run spec and quality review, and only after both pass bind
the descriptor and canonical Operator2 verify-request.

Cursor at send: 0
