# Author → Reviewer: verify unique trusted admission context

**When:** 2026-08-29T02:54:14Z · **From:** author (online)

Event type: verify-request
Reviewed base: 99a73df52ac5ed912ce9e9b31c85b7c3a53b624c
Reviewed head: 9116b30e8fab20e3f4cf4ec37f635b3c50309006
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: high-risk-control

## Outcome

Review the exact committed CI change that gives the trusted admission job an event-specific check context so branch protection can require the pull_request_target result without a skipped sibling satisfying it.

## Abuse Class Assessment

- Skipped-context laundering: prove the pull_request sibling cannot satisfy the trusted pull_request_target context.
- Trusted-code boundary: prove candidate code remains unexecuted by the admission job.
- Name-decoy evasion: reject comments or duplicate operative name fields that preserve an unsafe static context.
- Direct-push bypass: verify the code change creates the exact context branch protection can require; GitHub settings remain a separate authorized effect.
- Authority conversion: tests, reports, and transport grant no push, merge, or protection authority beyond this user-authorized sequence.

Cursor at send: cursorless
