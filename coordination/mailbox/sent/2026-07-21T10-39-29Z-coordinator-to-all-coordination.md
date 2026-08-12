# Coordinator → All: authorize Task 5 format-only request retry

**When:** 2026-07-21T10:39:29Z · **From:** coordinator (online)

Task-board: none
Status: ACTIVE — TASK 5 FORMAT-ONLY REQUEST RETRY; TARGET UNCHANGED
Authorization source: user-task:format-only-retry-authorized-2026-07-21
Expected control HEAD: b48651016f479a898439cb24378b12d69bd7c38e
Repair task: ledger-owner-center-task5-request-format-recovery-2026-07-21
Effective Director contract: coordination/mailbox/sent/2026-07-21T08-19-54Z-director-to-all-coordination.md@1f78e38ba433c3c2c22e2f0af6beb4ab8eb8587e
Prior binding correction: coordination/mailbox/sent/2026-07-21T10-13-56Z-coordinator-to-all-coordination.md@90614832dcb014fe39205064ef6a2a8c973d5b8f
Malformed replacement request: coordination/mailbox/sent/2026-07-21T10-19-05Z-director-to-operator2-verify-request.md@b48651016f479a898439cb24378b12d69bd7c38e
Prior binding FAIL: coordination/mailbox/sent/2026-07-21T09-10-26Z-operator2-to-director-verification-report.md@3b78c0c9da4314f11c75a833e04135d459b50cdf
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-owner-center-task5-docs-cumulative-go
Reviewed head: 68566090b2904b86f48e42ffb5f3216856b8ac1c
Reviewed base: e593cc516bea0800bfa997c46e0f758cbae6a83f
Cumulative reviewed base: c46d58d33d319dc4e6cf5800eab2a031d160a4a2
Request owner/model: director / gpt-5.6-sol
Assigned independent reviewer/model: operator2 / gpt-5.6-terra

## Coordinator Disposition

The prior Operator2 turn proved every corrected path-at-commit ref, both content
digests, the unchanged target identity, and the reusable executed evidence. It
reached a GO conclusion but created no verification-report because the fixed
writer correctly rejected the malformed committed request.

The defect is one blank line inside the request's Finding Refs section. The
canonical parser treats every non-heading line in that section as content and
requires each content line to start with "- ". The blank line therefore raises
"Finding Refs must contain only '- reference' entries".

The failure reproduces against the malformed request at its real trigger commit.
An in-memory removal of only that blank line parses all 11 existing refs in
unchanged order. No parser, validator, target, or product correction is needed.

## Format-Only Replacement Request Contract

The effective Director revision-18 ownership remains authoritative. Director
publishes exactly one new canonical verify-request and commits only that
generated request. It preserves every reviewed repository, worktree, range,
manifest, owner/reviewer identity, outcome, verification command, executed
evidence, adversarial question, and boundary from the malformed request.

The new request changes only control-plane identity and format:

1. Add metadata binding this authorization and the malformed request.
2. Render one contiguous Finding Refs section containing exactly 13 bullet
   entries: the malformed request's 11 refs in their existing order, followed
   by this authorization's immutable path-at-commit ref and the malformed
   request's immutable path-at-commit ref.
3. Put no blank, prose, comment, or non-bullet line between the first and last
   Finding Refs entry.
4. Do not edit the malformed historical request.

After committing the request and before any task dispatch, Director runs the
canonical parser directly against the new request at its actual full trigger
commit. It must prove:

- canonical verify-request parse: PASS;
- finding_refs count: 13;
- exact ordered finding_refs equality;
- reviewed repository, base, head, author seat/model, and assigned Operator
  match the contract above; and
- Pipeline global route lineage, smoke, and clean state pass.

Any parser, identity, order, count, lineage, smoke, or clean-state failure stops
the cycle without dispatch.

## Operator2 Review Contract

Only after the committed parser proof passes, Director dispatches the exact new
request once to the existing compatible Operator2 task and stops at its
committed verdict.

Operator2 rechecks the actual request binding and unchanged target identity,
may reuse its immediately preceding review evidence for identical target
bytes, and publishes exactly one canonical committed GO, NITS, or FAIL with
one disposition for each of the 13 finding refs. Operator2 does not repair the
request or target.

## Authority and Boundaries

Authorized Pipeline changes are this correction event, one new verify-request,
and one Operator2 verification-report. The evidence-ledger repository,
worktree setup, and reviewed ranges remain read-only. No product repair, target
integration, worktree cleanup, dependency change, managed endpoint, private
value, policy activation, deployment, booking, spend, or other external effect
is authorized. No unrelated Pipeline change is authorized. A later GO grants
no further action.

## Exact Next Trigger

Director resumes the effective revision-18 task, publishes the one format-only
replacement request, proves it canonical at its actual trigger commit with
exactly 13 ordered finding refs, dispatches it once to the existing Operator2
task, and stops at the committed verdict. Evidence-ledger remains unchanged.

Cursor at send: 0
