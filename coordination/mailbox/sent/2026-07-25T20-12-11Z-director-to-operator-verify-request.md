# Director → Operator: close the ignore gap and prune git-ignored trees from active-surface sweeps (material-behavior)

**When:** 2026-07-25T20:12:11Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed base: e1b2e4d81fe644ef951b9d6ab139543f4b95d9c0
Reviewed head: f3b2368a394654f33a4ef82890f86116f6006b93
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: material-behavior

## Allowed Paths

- .gitignore
- tests/unit/test_protocol_prompt_sync.py

## Outcome

Three commits, already on origin/main, submitted together because they are not
separable: the first is a functional input to the second.

6f56929 adds `.claude/worktrees/` to the committed `.gitignore` beside the
existing `.worktrees/` entry. The rule previously lived only in machine-local
`.git/info/exclude`, which is never cloned, so every fresh clone and CI checkout
re-acquired the gap.

86d9b33 is `git cherry-pick -x` of ca969c2 from branch
claude/unruffled-goldstine-ac9cc9, whose superseded request is
coordination/mailbox/sent/2026-07-25T19-28-55Z-director-to-operator-verify-request.md
at commit 576cfa78. That request bound e1b2e4d..ca969c2 at material-behavior
after the user reviewed and overrode the author's high-risk-control
classification; this request keeps that user-directed class. The cherry-pick
applied with no conflict: ca969c2's parent is e1b2e4d, and the file at that base
is byte-identical to main's, so the reviewed content of that commit is unchanged
from what the superseded request described. Its Outcome, coverage measurement and
abuse-class analysis remain accurate and are not restated here.

f3b2368 changes only the comment above UNSWEEPABLE_FALLBACK. That comment
justified the floor by asserting `.claude/worktrees/` is "only in machine-local
`.git/info/exclude`, never in the committed `.gitignore`" — a statement 6f56929
falsified in the same range. The constant is untouched; only its stated reason
changes.

The ordering matters for review: 6f56929 closes the first carried finding of the
superseded request, and in doing so it degrades the test design that finding was
compensating for. That is raised as a new author finding rather than fixed,
because fixing it means adding a probe or an assertion and would widen this range
past the two Allowed Paths.

The first digest under Finding Refs is the superseded request's first carried
finding, closed by 6f56929 inside this range. The second digest is that request's
second carried finding, still open and unchanged in substance. The third digest
is new and author-raised; it is sha256 over this exact one-line text:
`After 6f56929 added .claude/worktrees/ to the committed .gitignore, no test exercises UNSWEEPABLE_FALLBACK: neutering it to an empty frozenset leaves both active-surface sweeps and test_active_surface_sweeps_skip_git_ignored_trees passing, so the floor the superseded request called load-bearing is now unguarded.`

## Verification Run By The Author

Module: 15 passed, 1 failed. The failure is
test_project_codex_config_does_not_claim_runtime_permissions, pre-existing
uncommitted `.codex/config.toml` dirt in the main checkout, outside this range.
Attribution was measured, not asserted: `git show 86d9b33 -- <the module>` does
not touch that test, and `git show HEAD:.codex/config.toml` carries no
`approval_policy` key, so the failure comes entirely from the working-tree dirt.

scripts/ci_smoke.py: exit 0, OK across project-smoke, ceremony, placeholder,
go-schema, mechanism-ledger and arch-freshness. Re-run after f3b2368: exit 0.

Non-vacuousness of the pruned sweep was measured. A file carrying
`superpowers:negcontrol-probe` was planted at
`.claude/skills/zz-negcontrol-probe-719ca7a0.md`, a non-ignored active
instruction root; `git check-ignore` confirmed it was not ignored.
test_active_instruction_surfaces_have_no_superpowers_invocation then failed,
naming that exact path and needle, and passed again once the probe was removed.
The probe is gone and `git status` is clean apart from the `.codex` dirt. This
establishes the prune skips ignored trees without over-broadening into skipping
live surface.

The new finding was measured the same way. UNSWEEPABLE_FALLBACK was replaced with
an empty frozenset and the three sweep tests were re-run: 3 passed. The module
was restored from a pre-mutation copy, `grep MUTATED` returns nothing, and
`git diff` against the commit is empty.

The digest convention was confirmed by reproducing the superseded request's first
digest from its own one-line text: sha256 over the exact text with no trailing
newline yields 66760e4a…, matching. The new digest was produced the same way.

## Abuse Class Assessment

- Guard blinded by its own ignore rule: 6f56929 makes git authoritative for a path both sweeps prune, so a tracked protocol surface added under `.claude/worktrees/` would be skipped by the git lookup and by the floor alike; this is the superseded request's second carried finding, unchanged in substance and still open, and `git ls-files .claude/worktrees` is empty today.
- Silent removal of a defence: with the floor no longer exercised by any test, a later change may delete UNSWEEPABLE_FALLBACK with a fully green suite and restore the fresh-clone failure mode that 6f56929 now fixes by a different mechanism, so two independent defences remain in the tree but only one of them is guarded.
- Comment drift as false assurance: without f3b2368 the module would tell a future reader that the committed `.gitignore` does not carry this rule, which is precisely the premise a reviewer would rely on to justify keeping the floor, so the stale comment would have made the unguarded floor look load-bearing.
- Range widened past the user's words: the user named 6f56929..f3b2368, and this request binds e1b2e4d..f3b2368 instead, adding 6f56929 itself, because that commit changes what `git ls-files --others --ignored` reports and is therefore a functional input to the pruned sweep rather than unrelated hygiene; reviewing the two apart would let the interaction escape review entirely.

## Finding Refs

- sha256:66760e4a6f3780e719d85d4bd1db7557fefa06b4cbd05059d1dad938b2ee63d4
- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4
- sha256:adc0081d3b30536722e4d664860ca791aa34f0ba902378aa65c3942ba43928df

Cursor at send: 0
