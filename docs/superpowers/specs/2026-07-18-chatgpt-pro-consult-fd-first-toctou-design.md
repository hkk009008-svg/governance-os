# ChatGPT Pro Consultation FD-First TOCTOU Repair Design

**Date:** 2026-07-18

**Status:** Approved in chat for documentation on 2026-07-18

**Parent design:** `2026-07-17-compact-chatgpt-pro-browser-consultation-design.md`

## 1. Goal and evidence

Repair the filesystem-dependent identity check in
`scripts/chatgpt_pro_consult.py` without weakening the existing rejection of
symlinks, FIFOs, wrong-mode files, corrupt state, or duplicate reservations.

GitHub Actions run
[`29623303047`](https://github.com/hkk009008-svg/governance-os/actions/runs/29623303047)
on Ubuntu 24.04 failed only these cases at `4c150e4`:

- state replacement between pre-open `lstat` and `open` reached `fdopen`;
- lock replacement in the same window reached `flock`.

Both failures used the `same_mode_new_inode` test case. The complete unit run
reported 2 failed and 564 passed. The six focused replacement cases pass on
Darwin, so macOS execution alone does not prove the repair.

The root cause is the pre-open identity contract in `_bound`: after the test
unlinks the old object, Linux may immediately reuse its `(st_dev, st_ino)` for
the replacement. The comparison can therefore accept a different object.

## 2. Decision and threat boundary

Use an FD-first design. Open the object before treating any pathname metadata
as trusted, validate the opened object with `fstat`, and only then compare the
live FD with the name currently bound in the already-open Git common directory.

An open FD pins its inode. A replacement performed after `open` therefore
cannot reuse that inode while the FD remains live, making the post-open binding
comparison deterministic on Linux and macOS.

A same-mode regular file that is already present when the first `open` occurs
is the current object, not a detectable substitution. The kernel continues to
validate its type, mode, and state schema. Arbitrary concurrent mutation by an
actor with the same account and write access to the Git common directory is
outside this tool's threat model; portable pathname metadata cannot provide an
authentication boundary against that actor. The implementation and tests must
not claim otherwise.

## 3. Architecture

### 3.1 Directory and object opening

`_locked` opens the Git common directory once and retains that directory FD
through the lock, state read, action, and atomic write. Lock and state names are
opened relative to it.

The state opener:

1. calls `os.open` with `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`;
2. treats `FileNotFoundError` as empty state;
3. requires the opened FD to be a regular mode-`0600` file;
4. compares the FD identity with `os.stat(..., dir_fd=common_fd,
   follow_symlinks=False)` after the FD is open;
5. reads and validates JSON from that same FD.

The lock opener first attempts `O_CREAT | O_EXCL` so only a proven-new lock is
`fchmod`ed. If the name already exists, it opens without `O_CREAT`, validates
the existing object's type and exact mode, and never repairs an unsafe object.
Both paths use `O_NOFOLLOW | O_NONBLOCK`.

Open errors caused by an unsafe object remain `state_path_invalid`; unrelated
filesystem failures remain `io_failed`. No rejected input or file content is
added to errors.

### 3.2 Binding and locking

The old `_fixed` pre-open snapshot and `_bound(..., expected, ...)` contract are
removed. The replacement binding helper accepts only a live object FD, the
common-directory FD, and the fixed basename. It validates:

- regular-file type;
- exact mode `0600`;
- equality between the live FD identity and the name's current identity.

The lock binding is checked once immediately after open and again after
`flock(LOCK_EX)` returns, before state is read or an action runs. The second
check closes the replacement window while a process waits for the lock.

State replacement remains atomic. The state schema, request hashing, terminal
transitions, public Python API, CLI, and browser skill do not change.

## 4. Sibling audit and dispositions

| Sibling surface | Disposition | Required behavior |
|---|---|---|
| State symlink | mirror | `O_NOFOLLOW`; reject without reading or mutation. |
| Lock symlink | mirror | `O_NOFOLLOW`; reject without flocking or mutation. |
| State FIFO or wrong mode present before open | mirror | Nonblocking open and `fstat` reject before `fdopen`. |
| Lock FIFO or wrong mode present before open | mirror | Nonblocking open and `fstat` reject before `flock`; do not `fchmod` existing objects. |
| Same-mode state replacement after open | mirror | Live-FD/name mismatch rejects before `fdopen`. |
| Same-mode lock replacement after open | mirror | Live-FD/name mismatch rejects before `flock`. |
| Lock replacement while waiting in `flock` | mirror | Post-flock rebind rejects before state read or action. |
| Same-mode replacement completed before first open | document | Treat the opened object as current; validate type, mode, and state schema. Do not claim prior-object identity. |
| State replacement after read by an uncooperative same-account writer | document | Outside the same-account threat boundary; advisory locking serializes cooperating clients. |
| Two worktrees and concurrent reservations | mirror | Retain shared Git-common-dir state and exactly-one-created behavior. |
| State schema, secret scanning, browser send lifecycle | exempt | No change in this repair. |

## 5. Test design

The tests separate two different questions instead of combining them in a
filesystem-allocation-dependent case.

1. **Opened-object safety:** replace the path before the real `open` with a FIFO
   or wrong-mode regular file. Assert `O_NONBLOCK`, rejection before
   `fdopen`/`flock`, and no mutation of the unsafe object.
2. **Post-open binding:** call the real `open` first, keep the returned FD live,
   then unlink and install a same-mode regular replacement before returning the
   FD to production code. Assert rejection before `fdopen`/`flock`. Keeping the
   old FD live guarantees a distinct inode on every supported filesystem.
3. **Blocked-lock rebind:** replace the lock inside a fake `flock` immediately
   before it returns. Assert no state read, action, or write occurs.
4. Retain the existing symlink, corruption-without-rewrite, terminal-transition,
   same-key concurrency, linked-worktree, CLI, and content-free-error tests.

The RED proof for the new post-open and post-flock cases must fail against the
pre-repair implementation for the intended reason. No test may force a fake
inode value merely to make the old pre-open contract appear portable.

## 6. Independent abuse cases and acceptance criteria

An independent read-only design review identified these enforced targets:

- substitution after state open is rejected before read;
- substitution after lock open is rejected before flock;
- substitution while waiting for flock is rejected before action;
- FIFO and wrong-mode objects remain nonblocking and fail closed;
- only a proven-new lock may be normalized to mode `0600`;
- corrupt or structurally invalid state is not rewritten;
- two processes still produce exactly one new reservation;
- two worktrees still share one state and lock domain;
- terminal `reserved -> sent|failed` behavior remains unchanged;
- the implementation makes no protection claim for a same-account writer that
  controls the directory before the first open.

## 7. Alternatives rejected

### Persisted nonce

A nonce would require state-format migration, crash-safe bootstrap, and token
propagation across every atomic state replacement. A token stored only in the
same replaceable, same-account-writable directory can also be copied by the
actor it purports to stop. It is unnecessary for the approved threat model.

### More metadata

Adding `ctime`, size, birth time, or platform-specific generation fields might
make the current CI case pass, but it remains a probabilistic incarnation test
and is not portable across Linux and macOS. It does not repair the architecture.

## 8. Scope and verification

Allowed production and test paths:

- `scripts/chatgpt_pro_consult.py`;
- `tests/unit/test_chatgpt_pro_consult.py`.

The design, R-BRIEF, and implementation plan may add their own files under
`docs/superpowers/`. The integration test and canonical browser skill change
only if a failing contract test proves they must; otherwise they are excluded.

Verification requires:

```text
pytest tests/unit/test_chatgpt_pro_consult.py -q
pytest tests/integration/test_chatgpt_pro_consult_flow.py tests/unit/test_protocol_prompt_sync.py -q
pytest tests/unit --tb=short -q
scripts/ci_smoke.py
git diff --check
```

Linux proof must come from a Linux container or GitHub Actions. Completion also
requires a committed non-author Operator verification report. Commit, mailbox
publication, push, merge, browser submission, paid spend, and other external
effects remain separately gated; this design authorizes none of them.
