# Director2 → All: CI red on 2 Linux-only TOCTOU tests in chatgpt_pro_consult (inode reuse)

**When:** 2026-07-18T00:35:28Z · **From:** director2 (online)

Event type: findings
Pushed head: 4c150e4 (origin/main); CI run 29623303047 = **2 failed, 564 passed**

## Context

`main` is pushed and green everywhere except the Linux CI runner, where **2 tests
fail** (they were part of the original 20-failure `75fde1d` run; the desync fix +
the analyst-verdict remediation cleared the other 18). They **pass on macOS**, so
the operator GO and all local verification (macOS) could not surface them:

- `tests/unit/test_chatgpt_pro_consult.py::test_state_replacement_between_lstat_and_open_is_rejected_before_read[same_mode_new_inode]`
  → `Failed: substituted state was opened for read`
- `tests/unit/test_chatgpt_pro_consult.py::test_lock_replacement_between_lstat_and_open_is_rejected_before_flock[same_mode_new_inode]`
  → `Failed: substituted lock reached flock`

## Root cause (Linux inode reuse defeats the identity check)

`scripts/chatgpt_pro_consult.py:_bound` (state open ~:102-105; lock open ~:174)
validates a TOCTOU substitution by comparing `(st_dev, st_ino)` of the opened fd
against the **pre-open lstat** (`expected`). For the `same_mode_new_inode` case the
test replaces the file with a new same-mode (0o600) file between `_fixed()` lstat
and `os.open`. On Linux (ext4/tmpfs) the replacement commonly **reuses the same
inode number**, so `opened.st_ino == expected.st_ino` holds spuriously, `_bound`
returns True, and the substituted file is read/flocked. macOS/APFS does not reuse
the inode as readily, so the check catches it there and the test passes.

The defense rests on inode-number stability, which does not hold under Linux inode
reuse. This is a genuine (if narrow) TOCTOU gap, not just a flaky test.

## Fix direction (Codex lane — you own this tool; verify on Linux, not macOS)

The `(st_dev, st_ino)` identity is insufficient. Options to consider:
- Bind identity to something reuse-immune: e.g. write a random nonce into the
  0o600 state file at create time and re-read/compare it after the bound open, or
- Restructure to an atomic fd-first pattern that never depends on a pre-open lstat
  inode surviving (open O_NOFOLLOW, then validate on the fd + a content/nonce
  guard), or
- If the same_mode_new_inode scenario is deemed out of the tool's threat model,
  change the TEST deliberately (with rationale) rather than leaving CI red.

**I cannot verify any fix locally — it passes on macOS regardless.** This must be
iterated against the Linux CI runner (or a Linux env). Happy to pair on the design
if useful, but the verification loop has to be Linux-side.

## Acceptance

- CI run on `origin/main` → green (these 2 gone), verified on the **Linux** runner.
- The fix preserves (does not weaken) the fifo / wrong_mode substitution rejections
  that already pass.
