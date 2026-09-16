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
inherited `PYTEST_ADDOPTS` and `PYTEST_PLUGINS`. Use focused pytest runs while
iterating and one proportionate final pass. Investigate unexpected failures
before changing behavior; a green check proves only the paths it executed.
`preflight` exits nonzero until every checked binding and handshake passes;
app bundle and native discovery checks run on macOS by default and anywhere
with `--desktop`.

## Formal review

For `material-behavior` or `high-risk-control`, commit the candidate, then:

```bash
bin/pipeline review request --help
bin/pipeline review validate --help
bin/pipeline mail send --help
bin/pipeline check admission --base <full-sha> --head <full-sha>
```

The author composes a `verify-request` (Outcome text on stdin), publishes it
with `mail send`, and commits only the emitted path directly after the
reviewed head. The non-author reviewer reproduces the evidence, inspects the
diff, and publishes one bound `verification-report` directly after the
request. Use the actual running model. Revisions after review need their own
exact-range pair. Land a reviewed chain as a merge commit or fast-forward,
never a squash: only a byte-clean landing inherits coverage.

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
