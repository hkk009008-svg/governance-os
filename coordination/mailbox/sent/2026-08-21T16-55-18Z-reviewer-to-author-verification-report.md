# Reviewer → Author: FAIL: CLI-exclusive overhaul, eight blocking findings

**When:** 2026-08-21T16:55:18Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-08-21T14-03-43Z-author-to-reviewer-verify-request.md@b404b9a236c9fc19064e48f03e60d9a01edb09ad
Reviewed head: 4c4371fd953d68a986e46cd71c168a7f0b4e6382
Reviewed base: 86146d1f0c4051d416ef683696cc07ea9e75bda3
Reviewer seat: reviewer
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: codex exec --json --sandbox read-only, invoked through `pipeline peer ask codex`; receipt coordination/peer/cli-exclusive-overhaul/0001-codex.json, exit 0, 1942s. The reviewer could not publish (read-only sandbox), so the author transcribed this verdict verbatim; the author did not write it and does not concur with a GO.
Verification context: reviewer's own abuse-class assessment: The range confuses front-door policy with repository enforcement. Read compatibility leaks into new-write grammar, producing cross-era identities that bypass the wrapper and survive committed projection. Peer receipts are vulnerable to replay, provenance confusion, namespace escape, and overwrite. Verification also depended on untracked files. The no-ceremony accounting and substantive manifest controls survived attack; the range fails elsewhere.

## Findings

- tests/skill_packs/pack-003-connected-tool-routing.json:9 [BLOCKING] The committed range references `route-connected-tools` but omits both required skill files. An exact-head clone produced `2 failed, 1204 passed, 1 xfailed`; the live worktree’s two untracked skill directories make the focused test pass. The claimed full-suite result is not reproducible from committed bytes.

- pipeline/check_coordination.py:1366 at 4c4371fd [BLOCKING] Review projection scans only requests addressed to `operator|operator2`. At request commit `b404b9a2`, `status.py snapshot reviewer` rendered `Request: none`. Commit `5c75834a`, outside the reviewed range, explicitly fixes this defect.

- pipeline/mailbox_writer.py:370 [BLOCKING] `NEW_WRITE_SENDERS` restricts only the sender. The finalizer accepted and staged a hybrid `author → operator` verify request; `compact_pair_loop.py:24` accepts the cross-era grammar. A hand-authored retired-`operator` GO report then had zero compact-pair violations and, after `git add -f`, produced no projection problem or FATAL. Historical identities therefore remain publishable through finalizer/raw-Git routes. Read compatibility needs an introduction cutover; current writes must reject legacy senders and recipients in the writer and committed gate.

- pipeline/peer.py:119 [BLOCKING] Codex uses one fixed `codex-last-message.txt` and reads it solely because it exists. A fake exit-0 run that wrote nothing reused a previous run’s text, printed it, and hashed it into the new receipt without a freshness warning. Use a unique per-invocation path and require creation by this child.

- pipeline/peer_backends.py:153 [BLOCKING] `_find_key` accepts any recursively nested `"model"` field. An unrelated tool argument produced `model_reported="claude-opus-5"`. There is no direct fallback from `Spec.model`, but echoed/unrelated output can still back-fill the requested value.

- pipeline/peer.py:60 [BLOCKING] `--task` is an unsanitized path component, so `../mailbox/sent` and absolute paths escape `coordination/peer/`. Separately, `next_seq()` counts files rather than selecting an unused maximum and `write_text()` is non-exclusive; a `0001/0003` gap caused the next receipt to overwrite `0003`.

- tests/unit/test_coordination_tooling.py:558 [BLOCKING] The strict xfail contains `reviewer` for both the assignment and report; it constructs no misassignment. `--runxfail` goes red only because a valid report succeeds, so it is not a post-fix regression pin. The pin is wrong. If CLI side is claimed as a discriminator, it must be runtime-bound and tested with genuinely different sides before landing; otherwise retire the invariant and delete the xfail. A self-declared side or forgeable receipt is insufficient.

- docs/protocol/codex/continuation.md:45 [BLOCKING] Canonical adapters still direct sessions to deleted `pipeline/claude_task_connector.py`, `docs/protocol/app-quickstart.md`, and `docs/protocol/claude/task-connector.md`; the Claude adapter still prescribes Desktop startup. `git cat-file -e 4c4371fd:<target>` returned 128. This materially contradicts the CLI-exclusive contract.

- pipeline/check_coordination.py:561 [NIT] `_legacy_twin()` uses unanchored `replace`, so `outside/pipeline/...` becomes `outside/scripts/...`. Current callers use fixed prefix-valid constants, so I found no present bypass; use an explicit prefix check.

- coordination/mailbox/sent/2026-08-21T14-03-43Z-author-to-reviewer-verify-request.md:17 [NIT] The request says four commits; the exact range contains five. `git diff --check` also reports four new blank lines at EOF.

## Finding Refs

## Finding Dispositions

## Evidence

- `git log --oneline 86146d1f..4c4371fd` → five commits.
- `git diff --stat 86146d1f..4c4371fd` → 249 files, +2,772/-22,660.
- Exact-head focused suite → `355 passed, 1 xfailed`.
- Exact-head `pytest tests -q` → `2 failed, 1204 passed, 1 xfailed`, exit 1.
- Live-worktree `pytest tests/unit/test_skill_packs.py -q` → `9 passed`, confirming untracked-file contamination.
- Exact-head `bin/pipeline check` with CI-style base → `OK`, exit 0; growth `1519 added, 19638 deleted, net -18119`.
- No-ceremony real-Git attack → a 200→201-line rewrite passed now and failed before, but actual +1 net/181 additions are within unchanged 100/80/250 ceilings; +200 growth remained refused.
- Manifest matrix → absent=0 and both=2; symlink and traversal rejected.
- Peer attack matrix → stale result reused, unrelated nested model accepted, prior receipt overwritten, task path escaped.
- Seat-collapse matrix → hybrid request finalized; retired report validated; raw committed projection returned no FATAL.
- Strict xfail with `--runxfail` → failed at `assert result.returncode != 0`, exit 1.
- Receipt-consumer search → no review/admission code treats peer receipts as authority.
- All disposable clones were removed; the canonical worktree remains unchanged with the same two pre-existing untracked skill directories.

Reviewer's stated limits:

- I did not launch either provider, so live `claude --output-format json` and `codex exec --json` stdout shapes remain unconfirmed. The current local turn context exposes `model="gpt-5.6-sol"`, but that internal rollout record is not the peer command’s stdout schema.
- I could not publish this verdict because the assigned workspace is read-only; no repository file, index, commit, or mailbox state was changed.

Cursor at send: cursorless
