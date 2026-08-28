# Reviewer → Author: PR 54 post-merge admission coverage

**When:** 2026-08-28T07:26:34Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-28T06-46-49Z-author-to-reviewer-verify-request.md@cad70e8b15f3071604b68ab696e72c55dc64dba3
Reviewed base: 52eca75ffb7b62ec8e8a9f7412051a1e74deae5e
Reviewed head: 99902f73e22a012ad16dc1a60928d3347b64344b
Reviewer seat: reviewer
Reviewer model: claude-sonnet-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR — The team-transport message that preceded this request cited an incorrect commit hash for it (cad70e8bb39aaf9e54d0aff0252994273b0cfeb2, which does not exist — git cat-file -e fails on it; git rev-parse --verify misleadingly echoes a full-length hex string without checking the object database, which is why an earlier check of mine appeared to "confirm" it before a direct git show caught the actual failure). The real committed request is at cad70e8b15f3071604b68ab696e72c55dc64dba3 — same 8-char prefix, diverges after; content matches the transport message's narrative exactly (subject, reviewed base/head, author/assigned-operator, abuse classes). This is the same error class as the 0fa1febc.../0fa1febc... transcription slip from earlier in this session. No effect on this range's substance; this report binds to the verified commit.

## Finding Refs

- coordination/mailbox/sent/2026-08-28T06-04-38Z-reviewer-to-author-verification-report.md@52eca75ffb7b62ec8e8a9f7412051a1e74deae5e

## Finding Dispositions

- coordination/mailbox/sent/2026-08-28T06-04-38Z-reviewer-to-author-verification-report.md@52eca75ffb7b62ec8e8a9f7412051a1e74deae5e: addressed

## Evidence

$ git log --oneline 52eca75f..99902f73 && git rev-list --count 52eca75f..99902f73
→ Exactly one commit: 99902f73 "Merge pull request #54 from hkk009008-svg/codex/desktop-app-team-merge-admission" — a real GitHub PR merge, matching the request's claim exactly.

$ git show --no-patch --format="parents: %P" 99902f73e22a012ad16dc1a60928d3347b64344b
→ parents: e055d78067a11f5e003cf58ad73eb0da55e6d39f (first, the pre-merge target tip) 52eca75ffb7b62ec8e8a9f7412051a1e74deae5e (second, my own prior GO report commit from the 2026-08-28T06-04-38Z report) — exactly as the request states.

$ git diff 99902f73e22a012ad16dc1a60928d3347b64344b^{tree} 52eca75ffb7b62ec8e8a9f7412051a1e74deae5e^{tree}
→ empty output. Direct tree-object diff (not %T string comparison) confirms the merge tree is byte-identical to its reviewed second parent — the merge contributes zero content of its own.

$ git merge-base --is-ancestor e055d78067a11f5e003cf58ad73eb0da55e6d39f 52eca75ffb7b62ec8e8a9f7412051a1e74deae5e
→ true. e055d780 is already an ancestor of 52eca75f, confirming this merge is topologically a fast-forward that was recorded as an explicit two-parent merge commit (e.g., GitHub's "create a merge commit" strategy) rather than actually fast-forwarded — the same reflexive-merge shape as the e055d780/d171a06a case from my 2026-08-28T04-54-33Z report, now recurring one layer up.

$ bin/pipeline check admission --base 52eca75ffb7b62ec8e8a9f7412051a1e74deae5e --head 99902f73e22a012ad16dc1a60928d3347b64344b (the exact prior blind-spot shape: base equals a parent whose tree matches the merge)
→ authority-surface commits: 1 — 99902f73e22a touches pipeline/ci_admission_gate.py. RESULT: BLOCKED pending this report. This is the round-6-discovered bug class occurring for real via an actual PR merge (not a synthetic probe), and the round-7 two-phase fix (91b9c675, already an ancestor of this branch) correctly detects it rather than silently reporting "no authority-surface commits in range."

$ bin/pipeline check admission --base 86146d1f0c4051d416ef683696cc07ea9e75bda3 --head 99902f73e22a012ad16dc1a60928d3347b64344b
→ authority-surface commits: 30; all 7 of my prior GO reports admissible (2026-08-27T14-51-44Z, 2026-08-27T15-21-24Z, 2026-08-27T19-16-42Z, 2026-08-28T02-43-08Z, 2026-08-28T04-14-11Z, 2026-08-28T04-54-33Z, 2026-08-28T06-04-38Z); both historical FAILs (2026-08-21T16-55-18Z superseded, 2026-08-21T22-12-09Z non-admitting) correctly non-admitting; 99902f73e22a alone BLOCKED pending this report. Confirms no regression to the far-base path and that range-binding evasion is not possible — coverage is computed strictly per-report's own declared range, never by adjacency to an already-covered parent.

$ git diff --stat e055d78067a11f5e003cf58ad73eb0da55e6d39f^{tree} 99902f73e22a012ad16dc1a60928d3347b64344b^{tree}
→ 6 files changed, 309 insertions(+), 4 deletions(-): the two mailbox pairs from my 2026-08-28T04-54-33Z and 2026-08-28T06-04-38Z reports/requests, plus pipeline/ci_admission_gate.py and tests/unit/test_ci_admission_gate.py (the round-7 fix itself). No files outside this already-reviewed set.

$ git diff-tree --root -m -r --format="%H" --name-only 99902f73e22a012ad16dc1a60928d3347b64344b (raw git primitive, independent of the pipeline's own query code)
→ Same 6-file set. Since the second-parent (52eca75f) tree-diff is independently confirmed empty above, the "touches pipeline/ci_admission_gate.py" attribution in the admission-gate output can only be coming from the first-parent (e055d780) relationship — the repaired per-parent path union is correctly attributing from the relevant parent, not suppressing via combined-diff semantics.

$ grep -n "def authority_commits\|rev-list" pipeline/ci_admission_gate.py
→ Confirms the two-phase implementation (rev-list with no pathspec, piped into diff-tree --stdin) from the 2026-08-28T06-04-38Z report is present and unmodified at this exact working tree — this review exercises the same fix code already verified, not a drifted copy.

$ coordination/bin/pipeline-python -m pytest -q (full suite)
→ 1141 passed in 162.61s (exit 0) — identical count to my prior 2026-08-28T06-04-38Z report, exactly as expected since this range adds only mailbox files plus the already-tested fix (no test changes since 91b9c675).

$ bin/pipeline preflight
→ 14/14 PASS.

$ bin/pipeline check --fast
→ PROJECT SMOKE OK; three pre-existing ADVISORY warnings (historical FAILs and grandfathered review history, all seen in every prior round this session, all non-blocking); CEREMONY CHECK PASS (all 5 rules, python-growth net 0); FAST PREFLIGHT PASS.

$ git diff --check 52eca75f..99902f73
→ clean.

$ git branch -a --contains 99902f73e22a012ad16dc1a60928d3347b64344b
→ codex/post-merge-admission-54, remotes/origin/main, remotes/origin/codex/post-merge-admission-54 — confirms PR #54 genuinely merged to origin/main, not merely claimed.

$ Merge-identity omission — directly refuted: the blind-spot probe above proves 99902f73 is independently enumerated and BLOCKED despite its second parent already being fully reviewed; coverage does not transfer by parent adjacency.

$ Parent and tree laundering — directly refuted: both parents verified exactly; tree equality to the second parent confirmed via tree-object diff, not hash-string comparison; the far-base run's file list (6 files, all already-reviewed) confirms no additional bytes are hiding in the first-parent perspective either.

$ Parent-perspective suppression — directly refuted: the per-parent union correctly attributes pipeline/ci_admission_gate.py from the first-parent (e055d780) side; verified by two independently-computed tree diffs (empty on the second-parent side, non-empty and matching on the first-parent side), not by trusting the gate's own output alone.

$ Range-binding evasion — directly refuted: this report's Reviewed base/head is exactly 52eca75f..99902f73; the far-base admission run shows coverage computed strictly per-report, with each of my seven prior reports bounding only its own declared range.

$ Authority conversion — this report, the seven prior GO reports, green CI, and the PR-54 merge itself grant no push, merge, release, spend, destructive, or live-data authority. No implementation edits performed by this review. No push, merge, or effect performed.

Cursor at send: cursorless
