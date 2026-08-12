# Director → Operator: pin the seat shim interpreters

**When:** 2026-07-26T22:39:27Z · **From:** director (online)

Event type: verify-request
Reviewed base: 36fb178c2c3a9ff1fa946d9a766bdacc247de5ce
Reviewed head: 7cd388474203f615bb6328ddcfc68c499a95e909
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

All three `coordination/bin/*-seat` shims ran `exec /usr/bin/env python3`, so a
seat executed under whichever python3 the caller's PATH offered: the repo venv
normally, macOS system 3.9.6 in a stripped environment. The AGY and Codex
launchers import `tomllib`, stdlib only since 3.11, so that case died on a
ModuleNotFoundError traceback instead of the launcher's own error contract.

Each shim now prefers `$ROOT/.venv/bin/python`, falls back to PATH, and refuses
below 3.11 naming the interpreter and version.

The design changed once during implementation and that is the part most worth
attacking. A hard pin to `$ROOT/.venv/bin/python` was written first and
rejected: `.github/workflows/ci.yml` provisions Python via actions/setup-python
and never creates `.venv`, so the pin would have broken
`test_dry_run_uses_cwd_without_creating_index_or_starting_codex`, which runs
`codex-seat` and asserts exit 0 — green locally, red in CI. Verify that reading
of the workflow, and whether the fallback reintroduces the ambient-resolution
defect it was meant to remove. If it does, the fix is wrong.

Verify specifically:
(1) The version floor is right and enforced. 3.11 is claimed because of
`tomllib`. Check nothing else in these three launchers needs newer, and that the
guard cannot be passed by an interpreter that then fails at import anyway.
(2) The fallback is sound. Preferring the venv and falling back to PATH still
selects from ambient state when no venv exists — argue whether the version gate
makes that acceptable or merely narrows the hole.
(3) `cursor-seat` is included though it was latent, not broken: its launcher
imports no 3.11-only module. Judge whether raising its floor to the repo's is
right or whether it now refuses interpreters it would have run on fine.
(4) The new tests are non-vacuous. The refusal test uses a fake python3 that
exits 99 if ever handed the launcher script, so a bypassed guard is
distinguishable from a guarded refusal. Confirm that actually discriminates, and
that the hermetic test's comment-stripping does not let a real regression hide
in a comment.
(5) Nothing regressed for the ordinary paths: every seat still dry-runs on both
AGY and Codex, and cursor-seat's subcommands still run.

Disclosed, out of range: `tests/unit/test_harness_preflight.py::test_agy_with_every_review_grant_is_ready`
fails wherever the AGY binary is absent, including CI. It predates this range,
is documented in the verify-addendum at ac54cfd, and is being fixed on
`claude/preflight-host-independence`. It is not a regression from this commit.

## Abuse Class Assessment

- bound-to-request

Cursor at send: 0
