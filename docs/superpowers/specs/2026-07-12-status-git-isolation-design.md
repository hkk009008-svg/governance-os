# Status Git Isolation Design

## Goal

Make `scripts/status.py` report Git state for the repository passed to
`collect_git()` regardless of the process working directory or an ambient
seat-specific `GIT_INDEX_FILE`.

## Scope

This slice changes only `scripts/status.py` and its focused unit tests. It does
not introduce a repository-wide subprocess abstraction, migrate other scripts,
write `STATUS.md`, or change any mailbox, route, cursor, lock, commit, or push
state.

## Design

Change `_run_git` to require `repo_root`, execute Git with that directory as
`cwd`, and pass a copy of the process environment with `GIT_INDEX_FILE`
removed. `collect_git(repo_root)` passes its existing argument to every Git
query. Command results, timeout behavior, unavailable sentinels, and the
rendered dashboard schema remain unchanged.

The regression test creates a clean temporary Git repository, installs a
divergent alternate index in the test process environment, changes the process
working directory away from the repository, and asserts that `collect_git`
still reports the temporary repository's commit and a clean shared-index
worktree.

## Alternatives Considered

1. Extract a repository-wide Git runner now. Rejected for this slice because
   callers have materially different read, index, and mutation semantics.
2. Remove `GIT_INDEX_FILE` only at the CLI entry point. Rejected because direct
   callers of `collect_git()` would remain unsafe.
3. Make the existing status runner explicit and isolated. Selected as the
   smallest change that fixes both demonstrated root causes.

## Verification

- Observe the new regression test fail against the current implementation.
- Run the complete `tests/unit/test_status.py` file after the implementation.
- Run the project smoke and full pytest suite once as completion evidence.
