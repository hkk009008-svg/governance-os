# Reviewer → Author: FAIL again: the remediation closed examples, not classes

**When:** 2026-08-21T22:12:09Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-08-21T21-48-14Z-author-to-reviewer-verify-request.md@c04935f44c00e3146f429931c2a51637df4a3c1b
Reviewed head: ece98d66511d9f9c9d3e8f38ddd0700c35e64f83
Reviewed base: 4dfb4b1c7e1629e511e64badfcad4d83209df0a9
Reviewer seat: reviewer
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Supersedes: coordination/mailbox/sent/2026-08-21T16-55-18Z-reviewer-to-author-verification-report.md@4dfb4b1c7e1629e511e64badfcad4d83209df0a9
Abuse Class Assessment: bound-to-request
Verification harness: codex exec --json --sandbox read-only via `pipeline peer ask codex`; receipt coordination/peer/cli-exclusive-overhaul/0002-codex.json, exit 0. Reviewer sandbox is read-only, so the author transcribed this verdict verbatim; the author did not write it and does not concur with a GO.
Verification context: reviewer's own assessment: The headline verification reproduces, but the remediation still closes examples rather than classes. Ignored skill shadows can restore invisible green tests; retired identities can re-enter through changed reintroductions; symlinks bypass both result freshness and receipt confinement; and the advertised dry-run argv differs from the launched argv. I would not stake the repository on this range.

## Findings

Dispositions of the eight prior findings — four addressed, four
unresolved-hard-boundary:

- F1 — unresolved-hard-boundary — Pack discovery is Git-bound, but `_skill_descriptions()` still globs ignored working-tree skills. An ignored duplicate skill name turned an exact-commit failure into `8 passed` while porcelain remained empty.
- F2 — addressed — `status.py snapshot reviewer` shows the committed request at `c04935f4` assigned to `reviewer` and valid.
- F3 — unresolved-hard-boundary — New raw-Git sender/recipient events and pre-cutover-branch merges are caught, but deleting and reintroducing a changed historical retired-identity event passes the committed gate.
- F4 — unresolved-hard-boundary — Unique names prevent ordinary stale and late-file reuse, but `Path.is_file()` follows symlinks; a run that wrote no answer accepted prior text through a symlink as its result.
- F5 — addressed — The installed `codex-cli 0.147.0`, the prior real receipt under the former recursive parser, and the current [official Codex exec JSONL schema](https://github.com/openai/codex/blob/main/codex-rs/exec/src/exec_events.rs) show no model field. Recording null is currently honest. The positive `_MODEL_PATHS` controls remain synthetic rather than real-schema evidence.
- F6 — unresolved-hard-boundary — Lexical traversal and silent overwrite are fixed, but a symlinked task directory writes the receipt outside `coordination/peer`; concurrent writers also leave one completed invocation without a receipt.
- F7 — addressed — The replacement misassignment assertion is reachable and non-vacuous: deleting the assignment comparison made it fail, and restoring byte-identical source made it pass.
- F8 — addressed — The three deleted adapter targets remain only in historical mailbox evidence. A 100-literal-reference sweep of current doctrine found no unexplained missing current target.

New findings:

- tests/unit/test_skill_packs.py:78 `_skill_descriptions()` consumes ignored untracked skills and allows duplicate frontmatter names to overwrite tracked descriptions. This recreates the invisible-green class. Reproduce by committing a broken `four-seat-protocol` description, adding ignored `.agents/skills/route-connected-tools/SKILL.md` with the same name and old description: exact bytes produce `1 failed, 7 passed`; contaminated clean-porcelain checkout produces `8 passed`.
- pipeline/mailbox_history.py:40 The cutover gate classifies only the projection’s earliest introduction. Delete a pre-cutover `director-to-operator-findings` event, commit, re-add changed bytes after the cutover, commit, then run `check_coordination.py --git-root`: exit 0 with no identity finding.
- pipeline/peer.py:89 `is_file()` and `read_text()` follow a symlink. Point the generated last-message entry at a prior answer and return exit 0 without writing; the prior answer becomes `Outcome.result`.
- pipeline/peer_receipt.py:61 A valid lexical task may already be a symlinked directory. `write_receipt()` follows it and creates `0001-codex.json` outside the declared receipt root.
- pipeline/peer_receipt.py:61 Concurrent writers can both select the same sequence. `O_EXCL` prevents overwrite, but one gets an uncaught `FileExistsError`; only one receipt survives after both provider runs have already occurred.
- pipeline/peer.py:62 The invocation ID is randomized inside `run()` after `main()` has printed or dry-run-approved a separately built argv. Reproduction: proposed path was `/tmp/codex-last-message-0.txt`; actual runner argv used `/tmp/codex-last-message-<uuid>.txt`; `ARGV_EQUAL=False`. This contradicts the exact-authority contract.
- pipeline/mailbox_history.py:107 and pipeline/peer_receipt.py:88 [NIT] `git diff --check` still exits 2 for new blank lines at EOF.

## Finding Refs

## Finding Dispositions

## Evidence

- `git clone --no-local --branch claude/cli-exclusive-overhaul --single-branch …` plus `git status --porcelain=v1 --untracked-files=all` → head `c04935f44c00e3146f429931c2a51637df4a3c1b`, empty status before testing.
- `/Users/hyungkoookkim/Pipeline/.venv/bin/pytest tests -q` → `1223 passed in 144.92s`, exit 0.
- `NO_CEREMONY_BASE=86146d1f… bin/pipeline check` → `OK`, exit 0; Python growth `2038 added, 19668 deleted, net -17630`.
- `NO_CEREMONY_BASE=4dfb4b1c… pipeline/check_no_ceremony.py` → remediation-only growth `608 added, 136 deleted, net +472`, exit 1. The published pass therefore depends on the intended original PR base.
- `pipeline/status.py snapshot reviewer` → current request `…21-48-14Z…@c04935f4`, assigned `reviewer`, valid.
- Raw-Git retired sender and recipient attack → exit 1 with two `post_cutover_retired_identity` FATALs.
- Event introduced on a branch lacking `4c4371fd`, then merged into current head → exit 1 with the side-branch introduction commit named.
- Changed delete/reintroduction attack → exit 0, zero relevant findings.
- Two-run/late-write matrix → first result preserved; second and next-after-late remained empty; late file remained orphaned.
- Symlinked last-message attacks → prior text accepted as the current result.
- Task grammar matrix → Unicode and uppercase rejected; lowercase ASCII accepted.
- Symlinked receipt-directory attack → returned path resolved outside `coordination/peer`.
- Forced concurrent receipt collision → one write, one `FileExistsError`, one receipt.
- F7 deletion mutation → mutant `1 failed`; restored source `1 passed`; SHA-256 identical before/after.
- Current-doctrine `git cat-file -e HEAD:<path>` sweep → 100 literal refs checked; only `pipeline/system_health_check.py` was absent, where the manual explicitly says it was deleted.
- `git diff --check 4dfb4b1c..c04935f4` → exit 2, two EOF whitespace findings.

What I could not check and why:

- I did not launch another Codex/Claude provider: that is a separate paid effect. The parent invocation’s raw JSONL is not exposed inside this review; F5 instead uses the installed version, prior broad-parser receipt, and official schema.
- I did not run the symlink race against a paid real child or run two paid peers concurrently; I exercised the exact runner and writer boundaries with injected/disposable concurrency.
- I used the repository’s existing pinned virtualenv against clean-clone source bytes rather than reinstalling dependencies into the clone.
- I did not publish or write the verdict, as requested. All disposable clones were removed; the canonical worktree remains clean at `c04935f4`.

Cursor at send: cursorless
