# Operations

## Orient

1. Read the user request and repository instructions.
2. `bin/pipeline orient --member <label>` prints Git, bindings, transport
   with every member's focus, your resume cursor and handoff, review state,
   and the newest artifacts in one digest. `status` shows the same without a
   member view; `--verbose` adds historical unresolved FAILs; `--json` is
   machine-readable.
3. Call `team_status` once and read addressed messages with `team_wait` from
   its `resume_cursor`. Set your `focus` now and your `handoff` before you
   stop; both are observational.
4. Start the scoped work directly.

## Verify

```bash
bin/pipeline check --fast
bin/pipeline check
bin/pipeline preflight
```

`check --fast` validates bindings, review policy, and mailbox health; `check`
also runs the full suite and requires at least one executed test, ignoring
inherited `PYTEST_ADDOPTS` and `PYTEST_PLUGINS`. A green check proves only
the paths it executed.
`preflight` exits nonzero until every checked binding and handshake passes;
app bundle and native discovery checks run on macOS by default and anywhere
with `--desktop`.

## Formal review

For `material-behavior` or `high-risk-control`, commit the candidate, then:

```bash
bin/pipeline review publish --help
bin/pipeline review accept --help
bin/pipeline review land-check --help
bin/pipeline check admission --base <full-sha> --head <full-sha>
```

At the reviewed head the author runs `review publish`: it composes the
`verify-request` (Outcome from `--outcome-file` or stdin), validates it,
publishes it through the fixed writer, and commits only that artifact
directly after the head, refusing at any other HEAD. The non-author reviewer
checks out the request commit, reproduces the evidence, inspects the diff,
and runs `review accept` with the verdict, findings, and evidence; it
publishes and commits the bound `verification-report` directly after the
request. Use the actual running model. Revisions after review need their own
pair. `review land-check` confirms the chain admits and can land byte-clean;
land it as a fast-forward or merge commit, never a squash. `review request`,
`review validate`, and `mail send` remain the underlying steps.

`status` and `check` describe mailbox health. `check admission` evaluates an
explicit range with the code in the current checkout; the PR workflow runs the
gate from the trusted base without executing candidate code, so land
prerequisite gate changes before changes that rely on them. A historical FAIL
whose request is gone is an advisory, not a veto.

## Troubleshoot

- Missing team tool: reopen the repository in the app and run `preflight`.
- AGY not connected: refresh the workspace `pipeline-team` plugin and approve
  the exact `mcp(pipeline-team/*)` permission.
- Queued but unacknowledged: continue independent work; do not infer assent.
- Store refusal: restore owner-only, non-symlinked state under the Git common
  directory's `pipeline-team` entry.
- Artifact refusal: run `review validate` and fix the reported binding, range,
  identity, or evidence error.
