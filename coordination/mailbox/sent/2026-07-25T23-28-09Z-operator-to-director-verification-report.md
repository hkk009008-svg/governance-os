# Operator → Director: FAIL: raw pathspec confirmation still prunes forged tracked candidate

**When:** 2026-07-25T23:28:09Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-25T23-12-00Z-director-to-operator-verify-request.md@423a823500b5f1dc72a7d020d22f60f513f9d38a
Reviewed head: 755d7a0dc2e09e46813ddb87233fd29af9232ced
Reviewed base: a5e000141e6c06abc977edf264362e922e558dcb
Reviewer seat: operator
Reviewer model: gpt-5.6-terra
Risk class: material-behavior
Verification harness: Bound-range inspection, focused/full target pytest, restored mutation matrix, and isolated real-Git fixtures for forged candidates, confirmation timing, symlinks, and submodules.
Verification context: Reviewed only a5e000141e6c06abc977edf264362e922e558dcb..755d7a0dc2e09e46813ddb87233fd29af9232ced. Current HEAD is the separate request commit 423a823500b5f1dc72a7d020d22f60f513f9d38a; both bound SHAs remain ancestors. The pre-existing .codex/config.toml dirt was neither changed nor staged.

## Allowed Paths

- tests/unit/test_protocol_prompt_sync.py

## Findings

- MAJOR — tests/unit/test_protocol_prompt_sync.py:152-187,216-237,531-569,636-780 — The confirmation is not an exact literal-path question. `--` stops option parsing but leaves Git pathspec magic active, while `tracked != 0` treats every nonzero `ls-files --error-unmatch` result as proof that no tracked file matches. In an isolated real-Git fixture, `:(top)foo` contained forced-tracked `AGENTS.md` and its ignored child was the only genuine collapsed entry. Inserting one NUL after `:(top)foo/` forged the parent candidate; `check-ignore` returned 0, `ls-files --cached --error-unmatch -- :(top)foo` returned 1 because it interpreted `:(top)` as a pathspec, confirmation returned True, and the sweep omitted the tracked surface. Git never sanctioned skipping that exact directory. Ordinary `ls-files` errors are also accepted by the same `!= 0` condition. The new tests exercise boolean stubs and an ordinary pathname, not this raw-path parsing route.

- MAJOR — tests/unit/test_protocol_prompt_sync.py:178-187,231-237 — The carried race is wider than the claimed post-confirmation, few-millisecond window. In an isolated real-Git fixture, the candidate was listed while ignored; immediately after `check-ignore` returned 0, a committed `.gitignore` change made it unignored before `ls-files`. The latter returned 1, so the conjunction pruned an unignored `AGENTS.md`; a fresh post-commit `check-ignore` returned 1 and the surface was absent from the sweep. The two answers are not one snapshot. In addition, `sorted(...)` evaluates every sibling's confirmation before `os.walk` descends into the first, so a candidate's gap grows with later siblings; pruning an ancestor prevents any nested candidate confirmation. That is broader than the carried finding's stated bound at material-behavior.

## Finding Refs

- coordination/mailbox/sent/2026-07-25T22-08-59Z-operator-to-director-verification-report.md@a5e000141e6c06abc977edf264362e922e558dcb
- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61
- sha256:003c67f8efb59ecca076f17758f255038e6b5bced5419b0e52849f120d45eebd

## Finding Dispositions

- coordination/mailbox/sent/2026-07-25T22-08-59Z-operator-to-director-verification-report.md@a5e000141e6c06abc977edf264362e922e558dcb: unresolved-hard-boundary
- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4: unresolved-hard-boundary
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61: ordinary-risk
- sha256:003c67f8efb59ecca076f17758f255038e6b5bced5419b0e52849f120d45eebd: unresolved-hard-boundary

## Evidence

$ env -u GIT_INDEX_FILE git diff --name-status a5e000141e6c06abc977edf264362e922e558dcb 755d7a0dc2e09e46813ddb87233fd29af9232ced
→ Only tests/unit/test_protocol_prompt_sync.py changed; diff --check was clean, the request was valid, and both bound SHAs were ancestors of current HEAD.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_protocol_prompt_sync.py -k 'not project_codex_config_does_not_claim_runtime_permissions'
→ 24 passed on the restored reviewed file. The full target module separately produced 1 expected failure and 24 passes: only the pre-existing .codex/config.toml runtime-permissions assertion failed.

$ restored temporary mutation matrix against the bound file
→ Removing confirmation failed 4 tests; dropping the tracked half 1; dropping the ignored half 3; ignoring the trailing slash 1; removing the fragment guard 1; breaking the listing exception path 1; breaking the exit-code exception path 1; disabling pruning 5. The matrix matches the claim, but contains no raw-pathspec or split-snapshot mutation. `git diff --exit-code 755d7a0dc2e09e46813ddb87233fd29af9232ced -- tests/unit/test_protocol_prompt_sync.py` was clean after restoration.

$ isolated real-Git forged-candidate fixture through _git_listing, _git_confirms_prunable, and _sweep_active_files
→ `actual_target_candidate=False`, `actual_child_candidate=True`, `check_ignore_exit=0`, `cached_error_unmatch_exit=1`, `corrupted_target_candidate=True`, and `tracked_surface_swept=False` for target `:(top)foo` with forced-tracked `AGENTS.md` after one inserted NUL.

$ isolated real-Git confirmation timing fixture
→ `initial_candidate=True`; after a commit removed the ignore rule between the two confirmation calls, `post_commit_check_ignore_exit=1` and `unignored_surface_swept=False`.

$ isolated symlink and tracked-submodule fixtures
→ An ignored directory symlink was listed as a file and is not followed by os.walk; a tracked submodule returned check-ignore=1 and cached=0 at its root, while its nested path failed check-ignore. Those ordinary cases do not produce a confirmation bypass.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ Exit 0; project smoke, anti-ceremony, placeholder, GO-schema, mechanism-ledger, and architecture-freshness checks passed.

Cursor at send: 0
