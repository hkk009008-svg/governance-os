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

`check` requires an executed, non-skipped test and ignores inherited
`PYTEST_ADDOPTS` and `PYTEST_PLUGINS` overrides. For custom selections/options,
run pytest directly with the primary checkout's `.venv/bin/python`.
This is a fixed full-suite command, not a sandbox for installed Python plugins.
`status` lists every pending request; `status --json` includes their exact ranges.

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

Publication is two separate commits: the request must be the only change
directly after its reviewed head, and the report must be the only change
directly after that request. The composer reads Outcome text from stdin and
prints a body; it does not publish. Pass that body to `mail send`, then commit
only the emitted path with an explicit pathspec. Use the actual running model,
not an admitted label chosen to make validation pass. Revisions after review
need their own exact-range coverage.

Validate a draft before publication with:

```bash
bin/pipeline review validate --help
```

Admission for an explicit range is checked with:

```bash
bin/pipeline check admission --base <full-sha> --head <full-sha>
```

Do not write ordinary team conversation to the mailbox. Published formal
artifacts are append-only: retain requests and reports in
`coordination/mailbox/sent/` and retire verdicts through valid `Supersedes`
reports, not deletion, renaming, or rewriting. This includes mailbox-only
commits and changes later reverted inside the integration range.

`status` and `check` describe mailbox health, not integration admission.
Historical FAILs with previously pruned requests remain visible as advisories;
they are not a blanket veto on unrelated work. Admission applies to the explicit
base/head range. A same-request GO does not retire an unsuperseded FAIL.

Local `check admission --base/--head` selects history, not the validator version:
it executes code in the current checkout. The required PR workflow instead runs
the gate from the trusted base against candidate Git objects, without executing
candidate code. Land prerequisite gate changes before changes that rely on them.
Direct-push CI is not a substitute for that PR admission check.

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
