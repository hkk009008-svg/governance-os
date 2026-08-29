# Author → Reviewer: verify isolated trusted admission and required-context behavior

**When:** 2026-08-29T03:16:18Z · **From:** author (online)

Event type: verify-request
Reviewed base: 99a73df52ac5ed912ce9e9b31c85b7c3a53b624c
Reviewed head: a24a48a658347e2db3a63b05063bd57cf4b0055d
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: high-risk-control

## Outcome

Review the final cumulative CI range. The first implementation at 9116b30e used an expression in the job name; live PR #57 showed a skipped job preserving that expression literally, so its request at 140e88df was held before review. The remediation at a24a48a isolates trusted pull_request_target admission in .github/workflows/admission.yml and removes that job and trigger from candidate CI. Judge the final combined behavior, including the held attempt, and publish exactly one independent GO, NITS, or FAIL.

Reproduce the evidence rather than relying on the author. In particular, inspect closed unmerged PR #58's two live negative controls: (1) same-name candidate SKIPPED plus trusted FAILURE and (2) same-name candidate SUCCESS plus trusted FAILURE. With the context temporarily required, GitHub reported BLOCKED in both cases. PR #58 was then closed unmerged and the original four required checks restored.

## Abuse Class Assessment

- Skipped-context laundering: prove a skipped candidate job cannot satisfy or override the failed trusted result.
- Same-name success forgery: prove a candidate success under the same GitHub Actions app and context still leaves a failed trusted result blocking; do not overclaim workflow-level provenance because GitHub binds required checks by context and app.
- Trusted-code boundary: prove the pull_request_target job loads from the default branch, runs only trusted base code, validates exact base/head SHAs, and never executes candidate bytes.
- Cancellation and duplicate-name evasion: inspect separate workflow concurrency and the exact-one-workflow regression guard; distinguish fail-closed ambiguity/denial from pass bypass.
- Direct-push bypass: this code creates the stable target needed for protection, but GitHub protection changes remain a separate post-merge effect and are not claimed as already applied.
- Authority conversion: the request, tests, live canary, and any verdict grant no authority beyond the user's already-scoped execution sequence.

## Finding Refs

- coordination/mailbox/sent/2026-08-29T02-54-14Z-author-to-reviewer-verify-request.md@140e88dfefc70f7443f4268592b6bcc58625ed38

Cursor at send: cursorless
