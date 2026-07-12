# Status Git Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `scripts/status.py` Git reporting independent of ambient CWD and seat-specific index state.

**Architecture:** Keep the existing status collector boundary. Make its private Git runner accept an explicit repository root and construct a shared-index subprocess environment for every query.

**Tech Stack:** Python 3 standard library, Git CLI, pytest.

## Global Constraints

- Modify only `scripts/status.py`, `tests/unit/test_status.py`, and these design/plan artifacts.
- Do not create a generic repository-wide subprocess helper in this slice.
- Preserve result keys, unavailable sentinels, timeouts, and rendering behavior.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest commands.
- Do not commit, push, merge, consume mail, or mutate protocol state without separate authorization.

---

### Task 1: Pin and Fix Status Git Isolation

**Files:**
- Modify: `tests/unit/test_status.py`
- Modify: `scripts/status.py`

**Interfaces:**
- Consumes: `collect_git(repo_root: Path) -> dict`
- Changes privately: `_run_git(repo_root: Path, args: list[str], timeout: int = 5) -> str`
- Preserves: all `collect_git` result keys and values.

- [x] **Step 1: Add the failing regression tests**

Create a temporary Git repository with one committed file. One test changes CWD
outside that repository and asserts `collect_git(repo)` returns its commit. A
second test installs an ambient empty index and asserts the shared-index
worktree remains clean.

- [x] **Step 2: Run the focused test and confirm RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_status.py::test_collect_git_runs_in_requested_repo tests/unit/test_status.py::test_collect_git_ignores_ambient_index -q
```

Expected: FAIL because `_run_git` currently uses ambient CWD and environment.

- [x] **Step 3: Implement the minimal runner change**

Import `os`; update `_run_git` to accept `repo_root`, copy `os.environ`, remove
`GIT_INDEX_FILE`, and pass both `cwd=repo_root` and the sanitized environment to
`subprocess.run`. Pass `repo_root` from every call in `collect_git`.

- [x] **Step 4: Verify GREEN and regressions**

Run the focused test, all status tests, project smoke, and the full pytest suite.
Inspect `git diff --check` and the exact path-scoped diff before completion.
