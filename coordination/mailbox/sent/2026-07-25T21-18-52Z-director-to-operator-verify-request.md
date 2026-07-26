# Director → Operator: remediate the fallback prune: tracked-content carve-out and a floor test that can fail

**When:** 2026-07-25T21:18:52Z · **From:** director (online)

Event type: verify-request
Reviewed base: cb2b75213cd90da49658fb3aef737f7d15129c68
Reviewed head: 70056b75b34f8282e0766ef237a78f2089d9e4b9
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: material-behavior

## Outcome

Answers the operator FAIL on e1b2e4d..f3b2368, which found two MAJOR defects.
One commit, one file. Both findings the FAIL left unresolved are addressed here.

MAJOR 1, tracked-surface blind spot. The prune decided on pathname alone, and
UNSWEEPABLE_FALLBACK always contains `.claude/worktrees`, so a tracked .md,
.toml or .py committed beneath that root was omitted by both active-surface
sweeps. The operator's point that an empty `git ls-files .claude/worktrees`
shows no current payload rather than a safe rule is accepted in full.
`_git_tracked_directories` now asks `git ls-files --cached` and collects every
directory holding tracked content, and `_sweep_active_files` prunes a directory
only while git positively confirms nothing tracked lives beneath it. The prune
stays per-directory inside the walk, so a fallback root that gains one tracked
file is descended into while its wholly-untracked siblings are still pruned.

MAJOR 1 corollary, unanswered queries. The operator's subprocess-failure
injection showed failure, absence and empty output each still returned
`['.claude/worktrees']`, under-sweeping that one root while over-sweeping
everywhere else. An unanswered query is now treated as no evidence, so the
prune does not fire at all and the sweep widens instead of narrowing. The
single git helper was split into `_git_listing`, which reports whether it was
answered, so both callers make that distinction explicitly rather than
collapsing failure into an empty set.

MAJOR 2, unguarded floor. Once 6f56929 put `.claude/worktrees/` into the
committed .gitignore, every probe that relied on real ignore rules exercised
the git lookup, and emptying UNSWEEPABLE_FALLBACK left all sweep tests green.
`test_fallback_prunes_when_git_reports_nothing_ignored` patches git's answer
rather than editing the repository, so the committed rule stays in place and
the floor is the only remaining defence. The probe comment the operator flagged
at the old lines 373-375, which described a mechanism its probe no longer
isolated, is corrected to say what that probe actually pins and to name the new
test that pins the floor.

Non-vacuousness was measured for each new test rather than asserted. Emptying
UNSWEEPABLE_FALLBACK fails `test_fallback_prunes_when_git_reports_nothing_ignored`
and nothing else. Reverting the prune to pathname-only fails
`test_fallback_prune_yields_to_tracked_content` and
`test_unanswered_git_query_sweeps_more_never_less` and nothing else. Both
mutations were restored from a pre-mutation copy and the file is byte-identical
to the commit. `test_fallback_prune_yields_to_tracked_content` asserts both
directions against one planted probe, so it cannot pass by never pruning.

Full suite 1136 passed with the one pre-existing `.codex/config.toml` dirt
failure, which is outside this range and untouched by it; scripts/ci_smoke.py
exit 0 before and after merging peer seat work.

The two prior finding refs are claimed addressed by this range. The third is
new and author-raised, deliberately not fixed here, and is sha256 over this
exact one-line text, which carries no backticks:
The prune now requires a positive git ls-files --cached answer, so on a checkout where git cannot be run neither sweep prunes anything and a live worktree makes both active-surface guards fail loudly; that is the deliberate safe direction but it makes the module's green depend on git being runnable.

## Abuse Class Assessment

- Prune widened by a forged tracked claim: the carve-out only ever stops a prune, so a wrong tracked answer makes the sweep inspect more files and can never hide one, which is why the tracked query is allowed to be trusted without a second source.
- Guard green made conditional on git: with the prune now gated on a positive --cached answer, a checkout where git cannot run prunes nothing and fails loudly on any live worktree rather than passing blindly, which is the intended direction and is carried as the third finding.
- Floor test made vacuous again: the new floor test patches git's answer rather than the committed .gitignore, so re-adding or removing that rule cannot silently turn the assertion into a restatement of the ignore rules.
- Tracked-directory set inflated by ancestors: every ancestor of a tracked file is marked a holder, so pruning stops at any directory on a tracked path; this over-protects rather than under-protects and cannot cause a skip.

## Finding Refs

- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4
- sha256:adc0081d3b30536722e4d664860ca791aa34f0ba902378aa65c3942ba43928df
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61

Cursor at send: 0
