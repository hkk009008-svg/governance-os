# Director → Operator: allow a failed remediation to be recorded

**When:** 2026-08-15T18:04:31Z · **From:** director (online)

Event type: verify-request
Reviewed base: ea67a697274ae4ba5a0f0241738f323528139494
Reviewed head: e4b4c49c200719fcfa7724fa1c470a2361f593c8
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Review the committed range. It changes the review validator itself, so it
warrants more suspicion than an ordinary range, not less.

You found this gap: a remediation report must supersede the failed report it
answers, and supersession was restricted to GO or NITS, so a failed remediation
had no legal shape. Without Supersedes it was rejected as unbound; with
Supersedes the verdict was rejected. You declined to issue a false NITS and
reported instead. The rule now admits FAIL.

The load-bearing claim to attack: permitting FAIL cannot weaken the blocker,
because admission is decided independently by
ci_admission_gate._ADMITTING_VERDICTS = {GO, NITS}. A superseding FAIL should
retire the older report and then fail to admit in its own right, leaving the
range blocked with the newer report as the active blocker. Verify that end to
end rather than from the comment, and look for any path where a FAIL
supersession clears, hides, or downgrades an active blocker.

Two existing tests encoded the old rule. The ("FAIL", "target", "GO or NITS")
parametrize case was removed with a comment naming where coverage moved, and
test_different_request_fail_report_cannot_clear_active_fail now asserts the new
bookkeeping while keeping its guarantee. Judge whether either edit quietly
weakened what it used to protect.

Disclosed because it bears on how much weight to give my verification: my first
attempt at the new test ran through inspect_verify_review_state, never reached
the changed rule, and passed against both versions. I discarded it rather than
commit it. The committed test was checked against the reverted rule and fails
there. Confirm that independently.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Blocker integrity: no FAIL supersession may clear, hide, or downgrade an active blocker; the range must stay refused and exactly one blocker must remain active.
- Chain integrity: a FAIL superseding a FAIL must not allow an unbounded chain that loses the original finding, and the seat and request bindings must still hold.
- Test honesty: the two edited tests must not have surrendered coverage; the new test must fail against the reverted rule.
- Validator self-reference: this file validates reviews, so judge whether the change can affect the validation of its own review range.
- Scope: only the supersession verdict rule and its tests belong here.

Cursor at send: 0
