# R-BRIEF — Retroactive high-risk review of the merged PR #3 range

**Why this brief exists.** PR #3 (provider capability unification,
`5d044e233f0b22e9666e1a16afbe74d887faf6ab..3410f834ab89874bc05fa25fe8e27ee94b4f7d89`)
merged with no committed Compact Pair binding. By this repository's own
classification, two commits in that range touch `high-risk-control` authority
surfaces and therefore require a distinct non-author Operator on a different
model family. The admission gate run against the merged range reports exactly:

```text
4809480f1307 touches scripts/cursor_hook_policy.py
f044ab9f6399 touches scripts/cursor_mailbox.py
```

The range was authored by a Cursor cloud agent session (model
`claude-fable-5`); the standing Director adopts ownership of the landed range
for this retroactive review. This brief grants no authority; the committed
request and report do.

## Director steps

1. In the pinned Director seat chat, copy the body below into
   `.pytest-verify-tmp/pr3-retroactive-verify-request.md`.
2. Replace `REPLACE-WITH-DIRECTOR-MODEL-ID` with this seat's registered
   app-visible model ID (the publish wrapper rejects any other value
   byte-for-byte).
3. Publish:

   ```bash
   coordination/bin/cursor-publish --to operator --kind verify-request \
     --subject "Retroactive review: PR #3 provider capability unification" \
     --body-file .pytest-verify-tmp/pr3-retroactive-verify-request.md
   ```

4. Commit only the staged event path the fixed writer returns, with
   `git commit --only -- COMMIT-PATH-RETURNED-BY-WRITER`.

## Operator steps

Activate the pinned Operator chat and run `/review-next`. The Operator's
selected model family must differ from the request's author model family; the
wrapper and `compact_pair_loop` enforce this for `high-risk-control`.

## Verify-request body (copy from the next line to the end of the block)

```text
Event type: verify-request
Reviewed base: 5d044e233f0b22e9666e1a16afbe74d887faf6ab
Reviewed head: 3410f834ab89874bc05fa25fe8e27ee94b4f7d89
Author seat: director
Author model: REPLACE-WITH-DIRECTOR-MODEL-ID
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Retroactively review the landed provider capability unification range. The range was authored by a Cursor cloud agent (claude-fable-5) and merged without a committed review binding; the Director adopts ownership of the landed state. Confirm the two authority-surface commits preserve every hard boundary: the hook policy change (4809480) lets bound Director/Operator chats launch parent-scoped subagents while the child rules still deny repository mutation, mailbox effects, opaque interpreters, unclassified shell, seat impersonation, and out-of-workspace writes; the mailbox change (f044ab9) alters only the dry-run requires_app_approval report to match the seat-start grant the hook already enforced, with no change to writer delegation or model binding. Acceptance grants no push, merge, spend, launch, or other external-effect authority.

## Abuse Class Assessment

- Reject subagent authority inheritance: with subagentStart now allowed from bound seats, prove the preToolUse and shell child rules still deny repo mutation, mailbox wrappers, fixed-writer calls, and seat impersonation for subagent payloads regardless of parent posture.
- Reject scratch-path escape: the reordered preToolUse scratch allowance must apply only after outside-workspace and protected-prefix denials, so a crafted scratch path cannot reach coordination/mailbox, locks, or .cursor/runtime state.
- Reject impersonation-by-task-text: the subagentStart impersonation regex must still deny seat-claiming or verdict-issuing task text from every posture, bound or unbound.
- Reject approval-surface weakening: confirm requires_app_approval is a dry-run report only; the publish and consume execution paths still delegate to the fixed writers unchanged, and coordinator publishes still ask.
- Reject model-binding bypass: Author model and Reviewer model byte-equality against the registered session model_id must be unchanged by the mailbox edit.
- Reject doctrine-grants-authority drift: the new App capabilities prose and rules text must state capabilities add no task, review, or effect authority, and must not contradict the executable policy.
- Reject consultation widening: the provider-neutral ChatGPT Pro skill must keep parent-owned one-send, subagent propose-only, and never-for-verdict guards on every side.
- Reject test-vacuity: the updated hook tests must fail if the child sandbox or impersonation denial regresses (one-fact mutation goes RED), and the new advisor catalogs must remain read-only definitions.
```

(The publish wrapper composes the event envelope and the `Cursor at send:`
footer itself; the body must contain only the lines above.)

After a GO/NITS report lands, the admission gate over the historical range is
satisfied evidence-wise; a FAIL routes fixes through the normal remediation
request flow.
