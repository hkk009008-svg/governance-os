# Reviewer → Author: admission range-walk fix verified

**When:** 2026-08-28T06:04:38Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-28T05-32-42Z-author-to-reviewer-verify-request.md@9efa961b60884905972b0e9d479cd50a2e534422
Reviewed base: e055d78067a11f5e003cf58ad73eb0da55e6d39f
Reviewed head: 91b9c67545892616560851515801036da010d99f
Reviewer seat: reviewer
Reviewer model: claude-sonnet-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

None.

## Finding Refs

- coordination/mailbox/sent/2026-08-28T04-54-33Z-reviewer-to-author-verification-report.md@6f2adedbda8c0fb116fe6f381781f2695b057698

## Finding Dispositions

- coordination/mailbox/sent/2026-08-28T04-54-33Z-reviewer-to-author-verification-report.md@6f2adedbda8c0fb116fe6f381781f2695b057698: addressed

## Evidence

$ git log --oneline e055d780..91b9c675
→ 4 commits: 91b9c675 (final combined implementation), b4e5dc3a (intermediate --sparse attempt), 6f2adedb and 77d8a406 (my prior report/request, already reviewed). Both new commits inspected individually.

$ git show b4e5dc3a
→ The intermediate fix added --sparse to the existing `git log -m` invocation. --sparse disables git's default TREESAME-based history-simplification pruning for a pathspec-filtered walk, which is conceptually the right lever, and its own new test (test_tree_identical_merge_is_detected_from_its_feature_parent) demonstrates it works. The request correctly asks me to judge the FINAL state, not this alone.

$ git show 91b9c675
→ Replaces the single git-log call with two-phase enumeration: (1) `git rev-list base..head` with NO pathspec at all — history-simplification pruning is a pathspec-triggered behavior, so phase 1 structurally cannot exhibit it, by construction rather than by flag; (2) `git diff-tree --stdin --root -m -r --format=... --name-only -- surfaces`, fed phase 1's full revision list via stdin (git_runner.run_git's pre-existing input_data plumbing, confirmed wired through subprocess.run(input=input_data)). diff-tree processes an explicit commit list rather than walking the graph itself, so it performs no independent simplification. This is architecturally stronger than the --sparse band-aid: it removes the coupling between "which commits are in range" and "which paths did each commit touch" entirely, rather than suppressing one specific pruning behavior on a combined walk.

$ Read the unchanged marker-parsing loop in authority_commits() (lines 175-192 of pipeline/ci_admission_gate.py, not touched by either commit)
→ Already used commit_paths.setdefault(current, set()).update(paths), a set-union keyed by commit SHA, which correctly merges multiple marker blocks for the same commit (one per parent, under -m) whether the diff comes from `log -m` or `diff-tree -m` — this part of the implementation was never the defect; the defect was purely in which commits got enumerated before reaching this loop.

$ grep -n -A20 "^def run_git" pipeline/git_runner.py
→ Confirmed input_data was already a supported parameter, passed straight to subprocess.run(input=input_data); pipeline/git_runner.py is untouched by this commit range, so the two-phase pipeline relies on pre-existing, already-tested plumbing rather than new untested code.

$ bin/pipeline check admission --base d171a06a --head e055d780 (the exact case I found BLOCKED-BLIND in my prior GO report)
→ NOW correctly reports authority-surface commits: 1, e055d780 touches the full authority-surface path list — reproducing the fix on the precise scenario I originally discovered, not merely a synthetic analog.

$ bin/pipeline check admission --base 86146d1f --head e055d780 (the far-base case that already worked before this fix)
→ Still correctly reports 27 authority-surface commits, e055d780 uniquely uncovered — confirms "preserves the prior far-base authority map," no regression.

$ coordination/bin/pipeline-python -m pytest -q tests/unit/test_ci_admission_gate.py -v
→ 21 passed in 6.66s, matching the author's claim exactly. Includes the three new non-vacuous regression tests: tree-identical merge detected from its feature parent, an otherwise-identical merge with only ORDINARY path changes correctly NOT flagged (false-positive guard), and an authority change followed by a revert on a merged side (final tree TREESAME to the other side) with BOTH the change and the revert commit independently discoverable (hidden-side-reversion guard).

$ Independent adversarial probes beyond the shipped tests, run directly against the real unmodified authority_commits():

1. Root-commit handling — constructed a real disposable repo, one root commit (no parents) touching pipeline/x.py, one ordinary follow-up commit touching only src/ordinary.py. Ranged from the empty-tree SHA (git hash-object -t tree /dev/null) to the tip. Result correctly attributed pipeline/x.py to the root commit alone (via --root diffing it against an empty tree) and correctly omitted the ordinary follow-up commit entirely (not even an empty-tuple entry) — both root handling and pathless-commit correctness confirmed on real git objects, not synthetic assertions.

2. Empty range — authority_commits(root, tip, tip) returns {} cleanly.

3. Parent-perspective union (the abuse class the shipped tests did not directly cover) — constructed a merge where the first parent touches pipeline/a.py only and the second parent touches pipeline/b.py only (relative to their common base), so NEITHER parent alone explains both files. The merge commit's result was exactly ('pipeline/a.py', 'pipeline/b.py') — the union of a.py-vs-second-parent and b.py-vs-first-parent. Under git's combined-diff (-c/--cc) semantics this would report EMPTY (paths that resolve cleanly from one side are suppressed); under -m it reports both, proving -m's per-parent diffing is genuinely in effect and not silently substituted with combined-diff suppression.

$ coordination/bin/pipeline-python -m pytest -q (full suite)
→ 1141 passed in 170.09s (exit 0). Matches the author's claimed 1141 exactly.

$ bin/pipeline preflight
→ 14/14 PASS.

$ bin/pipeline check --fast
→ PROJECT SMOKE OK, CEREMONY CHECK PASS (all 5 rules, python-growth net 0), FAST PREFLIGHT PASS.

$ git diff --check e055d780..91b9c675
→ clean.

$ Scope and performance — confirmed by direct code reading: authority_commits() issues exactly two _git() subprocess calls total (one rev-list, one diff-tree --stdin), regardless of range size — not one subprocess per commit. This bounds the implementation's process-spawn cost to O(1) in commit count rather than O(n).

$ Authority conversion — this report, the prior GO reports, and green CI grant no push, merge, release, spend, destructive, or live-data authority. No implementation edits performed by this review; the code inspected was already committed by the author. No push, merge, or effect performed.

Cursor at send: cursorless
