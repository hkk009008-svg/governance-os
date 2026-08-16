# Director → All: user-accepted exception: PR 32 merges over two red gates

**When:** 2026-08-16T18:22:44Z · **From:** director (online)

Recorded because a merge is about to happen over two gates that would otherwise
refuse it, and the history should show a decision rather than an omission.

What the user decided. Merge PR #32 to main now, accepting the growth-gate
failure as an explicit exception. Offered alternatives were reverting the PR #34
merge to restore the sequential arithmetic, or raising the caps as its own
reviewed governance change. The user chose the exception.

What is red at merge time, measured at 2b0697bb.

check_no_ceremony from e858b4e: FAIL, 211 added, 11 deleted, net 200 against a
limit of 100, with scripts/claude_task_connector.py at 107 and
tests/unit/test_claude_task_connector.py at 93 against a per-file cap of 80.

ci_admission_gate from e858b4e: BLOCKED. Authority-surface commits lack a
committed GO/NITS high-risk-control report covering them.

Why the growth number is not bloat. PR #34 merged into PR #32's branch, which
is where it was based, so PR #32 now carries both features. The 200 lines are
two independently reviewed changes measured once each; the ACL half already
carries a GO at aa562cfc. Sequential merges to main would have measured 100,
then 100, then 99. Stacking re-parented the same lines under one base. This is
re-accumulation, not growth.

What is genuinely unreviewed, stated plainly. The FAIL at e02cddbc -- that the
range does not deliver the cross-process read its own docstring claimed -- was
remediated at 776777c6 by correcting the claim and pointing at the reviewed
successor. That remediation has NOT been reviewed. No verdict supersedes
e02cddbc. Anyone reading main should treat the cross-process claim as corrected
but the correction as unverified by a second party.

Precedent this extends. Two earlier ranges on this repository merged with no
committed review binding: PR #21/#22 at tips 3be45f1 and 597d8ab, and PR #24/#25
at 7c46021 and 127d56f. That finding is still open. This merge is a third
instance, differing in that it is deliberate, bounded, and recorded here rather
than discovered later.

What remains true and verified at this head: tests/unit 1672 passed,
governance_verify_all OK, and the 39 connector controls from both features pass
together, including the ACL refusal, the deny-only positive, the sentinel
ordering control, and the real-subprocess cross-process read.

Lessons: none-considered.

Cursor at send: 0
