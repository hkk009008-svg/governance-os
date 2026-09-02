# Operations

## Orient

1. Read the current user request and repository instructions.
2. Inspect the branch, `git status --short`, relevant diff, and recent commits.
3. Call `team_status` once and read addressed messages with `team_wait`.
4. Start the scoped work directly.

Use `team_send` for a bounded question, finding, result, or handoff. Queue
success is not acknowledgement; acknowledgement is not understanding; a reply
must be read to determine whether it is useful.

## Verify

```bash
bin/pipeline --help
bin/pipeline preflight
bin/pipeline status
bin/pipeline check --fast
bin/pipeline check
```

`check --fast` validates the live harness state. `check` also runs the full test
suite. Use focused tests during implementation and one proportionate final pass.
Investigate unexpected failures before changing behavior. A green check proves
only the paths it executed.

## Formal review

For `material-behavior` or `high-risk-control`, commit the candidate and create
an exact-range request:

```bash
bin/pipeline review request --help
bin/pipeline mail send --help
```

The author sends `verify-request` to a non-author Codex or Claude member. The
reviewer reproduces the evidence, inspects the actual diff, and sends one bound
`verification-report`. High-risk review also requires different model families
and a request-level abuse-class assessment.

Validate a draft before publication with:

```bash
bin/pipeline review validate --help
```

Admission for an explicit range is checked with:

```bash
bin/pipeline check admission --base <full-sha> --head <full-sha>
```

Do not write ordinary team conversation to the mailbox. Current formal
artifacts stay in `coordination/mailbox/sent/`; older state is available through
Git history.

## Troubleshoot

- Missing team tool: reopen the repository in the app and run `preflight`.
- AGY not connected: refresh the workspace `pipeline-team` plugin and approve
  the exact `mcp(pipeline-team/*)` permission if desired.
- Queued but unacknowledged: continue independent work or wait at a natural
  boundary; do not infer assent.
- Store security refusal: inspect the Git common directory's `pipeline-team`
  entry and restore owner-only, non-symlinked state.
- Formal artifact refusal: run `review validate` and fix the reported binding,
  range, identity, or evidence error.

Push, merge, release, spend, destructive actions, and live-data mutation are
performed only with exact current user authorization.
