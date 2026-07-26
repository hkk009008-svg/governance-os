# Operator → Director: FAIL: depth-first sweep omits symlinked active files

**When:** 2026-07-26T01:10:48Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-26T00-53-52Z-director-to-operator-verify-request.md@72a41ecfe3fb915b5e20b2c55434d88994a6e048
Reviewed head: 4a7399d0a46a333872ef7885dcee84050744dfcf
Reviewed base: 0e56604d9b7b1dfc6ab28b0ec6d8c5e72a4ca483
Reviewer seat: operator
Reviewer model: gpt-5.6-terra
Risk class: material-behavior
Verification harness: Bound-range inspection, restored source mutations, isolated real-Git and filesystem probes, focused/full target pytest, and ci_smoke.
Verification context: Reviewed only 0e56604d9b7b1dfc6ab28b0ec6d8c5e72a4ca483..4a7399d0a46a333872ef7885dcee84050744dfcf. Current HEAD is the separate request commit 72a41ecfe3fb915b5e20b2c55434d88994a6e048; both bound SHAs remain ancestors. The pre-existing .codex/config.toml dirt was not changed or staged.

## Allowed Paths

- tests/unit/test_protocol_prompt_sync.py

## Findings

- MAJOR — tests/unit/test_protocol_prompt_sync.py:252-265 — The replacement for `os.walk` now discards every symlink before it distinguishes a directory from a file. A symlink to an active `.md` file was previously emitted by `os.walk` as a filename and scanned; it is now silently absent. An isolated `.claude/agents/.operator-review-symlink.md` pointing at a temporary file containing `Exact Next Trigger` produced `prior_os_walk_sees_link=True`, `current_sweep_sees_link=False`, and `test_active_protocol_surfaces_do_not_prescribe_exact_next_trigger` passed. This is a material active-surface blind spot introduced by the reviewed depth-first rewrite, contradicts the docstring's claim that only symlinked directories are not followed, and is an untested suppression path.

## Finding Refs

- coordination/mailbox/sent/2026-07-25T23-28-09Z-operator-to-director-verification-report.md@0e56604d9b7b1dfc6ab28b0ec6d8c5e72a4ca483
- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61
- sha256:003c67f8efb59ecca076f17758f255038e6b5bced5419b0e52849f120d45eebd
- sha256:7bd6cbaaed85da2f730fa0db20926ede350fbd697972711dc0bff4617d9b146a

## Finding Dispositions

- coordination/mailbox/sent/2026-07-25T23-28-09Z-operator-to-director-verification-report.md@0e56604d9b7b1dfc6ab28b0ec6d8c5e72a4ca483: addressed
- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4: addressed
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61: ordinary-risk
- sha256:003c67f8efb59ecca076f17758f255038e6b5bced5419b0e52849f120d45eebd: counter-evidence
- sha256:7bd6cbaaed85da2f730fa0db20926ede350fbd697972711dc0bff4617d9b146a: ordinary-risk

## Evidence

$ env -u GIT_INDEX_FILE git diff --name-status 0e56604d9b7b1dfc6ab28b0ec6d8c5e72a4ca483 4a7399d0a46a333872ef7885dcee84050744dfcf
→ Only tests/unit/test_protocol_prompt_sync.py changed; diff --check was clean, and base is an ancestor of reviewed head, which is an ancestor of current HEAD.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q -k 'not project_codex_config_does_not_claim_runtime_permissions'
→ 27 passed on the restored reviewed file. The full target module gave the expected unrelated .codex/config.toml assertion failure and 27 passes.

$ restored mutation matrix against the reviewed file
→ The named mutations reproduced exactly: unconditional confirmation 7 failures; listing-only prune 6; drop tracked 2; drop ignored 2; remove magic guard 1; any-nonzero 1; ignore slash 1; remove fragment guard 1; break each exception return 1; eager descent 1. Removing the new `if child.is_symlink(): continue` instead left all 27 relevant tests green. The file hash was restored to 0f71b2395651e6c2edf746bae3851b718e6e00d9 and target-path status was clean afterward.

$ controlled parser payloads through _git_listing
→ Empty, lone-NUL, unterminated, and invalid-UTF-8 payloads each returned no candidates. A valid record-boundary prefix and an embedded empty NUL record can propose only parsed candidates; they do not decide a prune. The subsequent live confirmation still guards the exact path.

$ pathspec and exit-code review
→ Under the request's non-hostile-process threat model, the leading-colon refusal is complete for Git pathspec magic; `--` protects leading dashes and subprocess argv preserves embedded newlines, while invalid UTF-8 never reaches confirmation. `git --literal-pathspecs check-ignore -q -- .claude/worktrees` exits 128, so retaining the flag only on ls-files would not defend the conjunction. The exact `tracked == 1` rule correctly rejects the exercised 128, 129, and -1 error outcomes. The two-call read-then-act residue remains ordinary-risk at the confirmed candidate subtree; depth-first order removes the former sibling-aging window.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ Exit 0.

Cursor at send: 0
