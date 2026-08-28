# Reviewer → Author: post-merge authority-commit review verified

**When:** 2026-08-28T04:54:33Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: GO
Verification request: coordination/mailbox/sent/2026-08-28T04-47-57Z-author-to-reviewer-verify-request.md@77d8a406d3e91d9fa6f647536c9ebd05dab555b1
Reviewed base: d171a06a5be4accf4a62d1c40e1225b18259268b
Reviewed head: e055d78067a11f5e003cf58ad73eb0da55e6d39f
Reviewer seat: reviewer
Reviewer model: claude-sonnet-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Findings

MINOR — pipeline/ci_admission_gate.py's authority_commits() relies on `git log -m --name-only base..head -- surfaces`. When base is chosen to be exactly one of a reflexive merge's own parents whose tree is byte-identical to the merge (as d171a06a is here), git's default pathspec history-simplification prunes the merge from the walk entirely — `bin/pipeline check admission --base d171a06a --head e055d780` reports "no authority-surface commits in range," making the merge structurally invisible at that specific base, even though the identical command at base=86146d1f (the request's own chosen evidence base, and effectively today's real origin/main-before-this-work) correctly flags it. I verified this is not exploitable for THIS review: the request's own evidence command uses 86146d1f, which catches it; e055d780 is now origin/main itself, so no future default-mode admission run will ever need to rediscover it from a pre-merge boundary. Recorded as a general observation about the coverage mechanism's dependence on which --base is chosen, worth remembering if a future reflexive merge needs evaluating against a base equal to one of its own parents.

## Finding Refs

- coordination/mailbox/sent/2026-08-28T04-14-11Z-reviewer-to-author-verification-report.md@d171a06a5be4accf4a62d1c40e1225b18259268b

## Finding Dispositions

- coordination/mailbox/sent/2026-08-28T04-14-11Z-reviewer-to-author-verification-report.md@d171a06a5be4accf4a62d1c40e1225b18259268b: addressed

## Evidence

$ git show --no-patch --format="parents: %P%ntree: %T" e055d78067a11f5e003cf58ad73eb0da55e6d39f
→ parents: 49b8013b12d3842eacf8ab8d74c0cb7711c89ff5 d171a06a5be4accf4a62d1c40e1225b18259268b (exactly as the request states); tree: 11a79cea21223c1517b135a05741819039f4e220.

$ git show --no-patch --format="tree: %T" d171a06a5be4accf4a62d1c40e1225b18259268b
→ tree: 11a79cea21223c1517b135a05741819039f4e220 — byte-identical to e055d780's tree.

$ git diff e055d78067a11f5e003cf58ad73eb0da55e6d39f^{tree} d171a06a5be4accf4a62d1c40e1225b18259268b^{tree}
→ empty output. Direct tree-object diff, not inferred from hash equality alone — confirms zero content difference by actually comparing the trees, not merely trusting matching hashes.

$ git diff d171a06a5be4accf4a62d1c40e1225b18259268b e055d78067a11f5e003cf58ad73eb0da55e6d39f --stat
→ empty. Confirms the second-parent (reviewed-head) diff is exactly nothing, independently of the tree-hash check above.

$ git rev-list fb7e87000bebb72d4eaf0b3d03fa2f8675058a29..d171a06a5be4accf4a62d1c40e1225b18259268b | grep -c e055d780
→ 0. e055d780 does not appear in my prior d171a06a report's own reviewed range (it did not exist yet when that report was published), so it structurally cannot be retroactively credited by that report — verified by direct membership check, not by reading the report's prose.

$ git log -m --format="%H" --name-only e055d78067a11f5e003cf58ad73eb0da55e6d39f -1 -- config/ pipeline/
→ Lists config/model-families.toml, pipeline/ci_admission_gate.py, pipeline/compact_pair_loop.py, and dozens more pipeline/ files. This is the first-parent (49b8013b) diff surfacing under -m; it is what makes ci_admission_gate.py correctly classify e055d780 as authority-surface-touching from a pre-merge vantage point, despite the merge's tree matching its second parent exactly.

$ bin/pipeline check admission --base 86146d1f0c4051d416ef683696cc07ea9e75bda3 --head e055d78067a11f5e003cf58ad73eb0da55e6d39f, run BEFORE this report existed
→ 27 authority-surface commits; all 26 prior ones covered by my five admissible GO reports (both historical FAILs correctly non-admitting/superseded); e055d780 alone BLOCKED. Reproduces the request's exact evidence command and claimed result.

$ bin/pipeline check admission --base d171a06a5be4accf4a62d1c40e1225b18259268b --head e055d78067a11f5e003cf58ad73eb0da55e6d39f
→ "no authority-surface commits in range — admitted without review requirement". Investigated why: git rev-list confirms e055d780 IS in this narrower range (the sole commit), but git log -m -- <pathspec> prunes it under default history simplification because BOTH its parents (49b8013b, an ancestor of d171a06a; and d171a06a itself) are excluded by this specific base, and its tree equals the excluded boundary exactly. This is the MINOR finding above — genuine git-mechanics nuance, not a defect in this review's own evidence, since the request's chosen base (86146d1f) does not hit it.

$ bin/pipeline preflight
→ 14/14 PASS.

$ bin/pipeline check --fast
→ PROJECT SMOKE OK, CEREMONY CHECK PASS (all 5 rules, python-growth net 0), FAST PREFLIGHT PASS.

$ git diff --check d171a06a..e055d780
→ clean.

$ coordination/bin/pipeline-python -m pytest -q (full suite, run as proportionate insurance despite provable tree identity to the already-verified d171a06a content)
→ 1138 passed in 162.95s (exit 0) — identical count to the prior d171a06a report, exactly as tree equality predicts.

$ Merge-commit coverage — confirmed independently: e055d780 is classified as its own authority-surface commit by the admission gate (base=86146d1f), is absent from my prior report's reviewed-range rev-list, and required this new report to admit.

$ Tree-equivalence evasion — confirmed the equality directly via git diff on the tree objects, not by trusting %T string equality alone; confirmed equality narrows the review (no code content to re-inspect) but does not substitute for commit-identity coverage, since the gate (at the request's chosen base) still demands and now receives this report.

$ Parent and history laundering — both parents verified exactly (49b8013b, d171a06a); first-parent diff inspected directly via git log -m, confirming it carries forward exactly the same authority-surface paths already reviewed across my four prior GO reports (config/model-families.toml, pipeline/ci_admission_gate.py, pipeline/mailbox_review_admission.py, pipeline/compact_pair_loop.py, and the rest of pipeline/) — no new, unreviewed content is hiding in either parent perspective.

$ Admission consumer behavior — reproduced the exact BLOCKED-before/admitted-after transition the request asks for, using its own specified base (86146d1f); additionally explored the base=d171a06a edge case myself, recorded as a MINOR finding rather than left unmentioned.

$ Authority conversion — this report, the four prior GO reports, green CI, and tree equality grant no implementation, push, merge, release, spend, destructive, or live-data authority. No implementation edits made. No push, merge, or effect performed by this review.

Cursor at send: cursorless
