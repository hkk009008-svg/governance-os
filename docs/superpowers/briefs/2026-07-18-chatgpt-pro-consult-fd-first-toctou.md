# R-BRIEF: CONSULT-TOCTOU-001 — remove filesystem-dependent pre-open identity

> **Status (2026-07-18): OPTIONAL — not required for CI-green.** The user-principal
> scoped CI to macOS (`10163ef`; Linux is not used and not planned), which retires
> the Linux inode-reuse failure this brief targets. Retained for a future Linux
> deployment only.

PRIORITY: MAJOR

LANE: A (ChatGPT Pro consultation safety kernel)

CROSS-CUTTING: no

LOCK: N/A; the allowed production and test paths are lane-owned and no active
inventory or protocol lock names them.

## The defect

At `565b878`, `scripts/chatgpt_pro_consult.py:91-105` takes a pre-open `lstat`
snapshot and treats `(st_dev, st_ino)` as an object-incarnation identity. The
Ubuntu 24.04 unit job in GitHub Actions run `29623303047` reused the unlinked
inode for a same-mode replacement, allowing substituted state to reach
`fdopen` and a substituted lock to reach `flock`. The run reported 2 failed and
564 passed. The same six focused tests pass on Darwin, so macOS is not acceptance
evidence for this defect.

Allowed implementation paths:

- `scripts/chatgpt_pro_consult.py`;
- `tests/unit/test_chatgpt_pro_consult.py`.

Excluded unless a failing contract proves otherwise:

- `.agents/skills/chatgpt-pro-consultation/SKILL.md`;
- `tests/integration/test_chatgpt_pro_consult_flow.py`;
- request/state schema, CLI, secret scanning, and browser lifecycle behavior.

## Rule 12 — grep the writes

Target: the shared reservation state and its atomic filesystem replacement.

```text
$ rg -n "^def _write|os\.replace|state\[key\]" scripts/chatgpt_pro_consult.py
135:def _write(common: Path, state: dict[str, dict[str, str]]) -> None:
150:        os.replace(temporary, common / STATE_NAME)
204:        state[key] = {"hash": request_hash, "status": "reserved"}
219:        state[key] = {"hash": request_hash, "status": status}
```

The runtime write path is `reserve|finish -> apply -> _write -> os.replace`.
Both mutators execute inside `_locked`; the declaration of `STATE_NAME` is not
write evidence.

## Rule 13 — sibling audit and dispositions

Shared fence: fixed 0600 state and lock objects in the Git common directory.

- State and lock symlinks: **mirror** with `O_NOFOLLOW` and no mutation.
- State and lock FIFOs or wrong modes present before open: **mirror** with
  `O_NONBLOCK`, live-FD type/mode validation, and rejection before use.
- Same-mode state and lock replacement after open: **mirror** with a live-FD to
  current-name binding check.
- Lock replacement while waiting in `flock`: **mirror** with a post-flock
  binding check before state read or action.
- Same-mode replacement completed before the first open: **document** as the
  current object; validate type, mode, and state schema without claiming a
  prior-object identity.
- Uncooperative same-account directory mutation after state read: **document**
  outside the threat boundary; advisory locking serializes cooperating clients.
- Two-process and linked-worktree serialization: **mirror** existing coverage.
- Secret scanning, state schema, CLI, and browser lifecycle: **exempt** because
  this repair does not change them.

## Full-shape pattern reference

Canonical site: `565b878:scripts/chatgpt_pro_consult.py:135-169`, `_write`.
Its full shape creates a temporary in the Git common directory, forces mode
0600, completes a checked write loop, fsyncs the file, atomically replaces the
fixed state name, fsyncs the directory, maps filesystem errors to `io_failed`,
and cleans up open descriptors and temporary files. At the same SHA,
`_locked:170-194` holds `flock(LOCK_EX)` while invoking the state action.

The repair preserves that write and return contract while pinning the common
directory FD, opening state/lock FD-first relative to it, and rechecking lock
binding after `flock`.

## The fix

Expected delta: approximately 80-140 production/test lines across the two
allowed files.

1. Replace pre-open `_fixed` snapshots with FD-first open helpers.
2. Validate regular type and exact mode 0600 from `fstat`.
3. Compare a live FD with the fixed name only after open.
4. Create the lock with `O_CREAT|O_EXCL`; only that proven-new FD may be
   `fchmod`ed. Existing unsafe objects remain unchanged.
5. Rebind the live lock after `flock` and before state access.
6. Split pre-open FIFO/wrong-mode tests from deterministic post-open same-mode
   replacement tests; add RED coverage for FD-first ordering and post-flock
   replacement.

Implementation is direct because the change is small, tightly coupled, and
authority-sensitive. The earlier independent read-only design review supplies
the required adversarial enumeration; the director owns implementation and a
non-author operator owns the verdict.

## Verification

```text
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_chatgpt_pro_consult.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/integration/test_chatgpt_pro_consult_flow.py tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit --tb=short -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Linux execution of the full unit suite is required before the director requests
verification. Final closure requires a committed non-author Operator report.
Commit, mailbox publication, Docker/network use, push, merge, browser
submission, and paid spend remain separately gated.
