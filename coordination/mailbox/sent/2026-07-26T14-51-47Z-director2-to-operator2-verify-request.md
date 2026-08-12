# Director2 → Operator2: make the pathspec-magic negative control hold in every checkout, not only the main one

**When:** 2026-07-26T14:51:47Z · **From:** director2 (online)

Event type: verify-request
Reviewed base: f3b91aa5f90d2c91e5922d61fe99e030db79b37e
Reviewed head: a372db1f4e2ef4a55e973b6bed9f0ea43bf41bbe
Author seat: director2
Author model: claude-opus-5
Assigned operator: operator2
Risk class: material-behavior

## Outcome

Repairs the negative control at the head of
test_pathspec_magic_candidate_is_refused_before_git_is_asked, added by 8cb84eb in
the same lineage as the 2026-07-25 parser rounds on this module. One commit, one
file, tests only. No production module is touched, and the guard under test is
unchanged.

The reported defect. The control asserted
`_git_exit_code("check-ignore", "-q", "--", ":(top).claude/worktrees") == 0`
under a comment reading "Measured, not assumed". It measured, but against a
precondition it did not create, so it held only in the main checkout. From every
linked worktree the file reported 1 failed, 34 passed, and agents routinely work
in one: `.claude/worktrees/*`, `.worktrees/*`, `Pipeline-cursor-seats/*`. The
suite therefore read red there for a reason unrelated to whatever was being
changed.

The mechanism, measured rather than inferred. The cause is not that
`.claude/worktrees` is absent from a linked worktree. The committed rule at
.gitignore:108 is `.claude/worktrees/`, and a trailing slash makes a rule
directory-only; `git check-ignore` applies a directory-only rule only where it
can see a directory, and given a query carrying no trailing slash of its own it
consults the working tree. Isolated against a throwaway `.gitignore` under
.claude/agents on git 2.50.1: a `dir-only/` rule answers 1 for an absent path
and 0 for a present one, while an `any-kind` rule answers 0 either way. So the
old line read a property of one checkout as a property of the repository, and a
`False` it produced from a worktree was not the guard's work — the exact vacuity
the control exists to prevent.

The fix. The control now runs inside the `_ignored_probe` the rest of the test
already opens, which supplies that directory in any tree, and it measures the
exact string the second half forges rather than a neighbouring one. Both
confirmations are pinned separately, because `_git_confirms_prunable` requires
`check-ignore` 0 and `--error-unmatch` exactly 1, and a `False` from either half
is indistinguishable from the refusal under test; the old control pinned only
`check-ignore` while its comment claimed both. The literal path is pinned absent
as well, since that is what makes the 0 an answer about a path other than the
one named, which is the hazard the guard closes.

Alternatives rejected, both of which were on the table. Choosing a path that is
ignored and present in every worktree makes the control depend on machine state
rather than on the repository, so it rots the same way for a new reason. Gating
the assertion on the precondition, loudly or not, leaves the measurement absent
in exactly the trees where agents work, which is where the red was reported.

Evidence, all with `env -u GIT_INDEX_FILE`. 35 passed from the main checkout and
35 passed from a linked worktree; the same file at f3b91aa reports 1 failed, 34
passed from that worktree. Non-vacuousness was measured in both trees by
replacing the magic refusal in `_git_confirms_prunable` with a dead branch, each
mutation restored from a pre-mutation copy with the file left byte-identical by
sha256: the test fails in both, reporting `_git_confirms_prunable(...)` is True
rather than erroring on the precondition, which is the reason it must fail for.
Before this change that mutant was undetectable from a worktree because the test
died one line earlier. Full suite 1163 passed from the linked worktree;
scripts/ci_smoke.py exit 0. The probe leaves no residue in either tree, and
`.claude/worktrees` in the main checkout is intact, since `_ignored_probe`
rmdirs the parent only when it created it.

Residues carried rather than claimed closed. The control still depends on git
being runnable and on the committed `.claude/worktrees/` rule continuing to
exist; if that rule were deleted the two pinned exit codes fail loudly rather
than passing vacuously, which is the direction this module prefers. The
pre-existing 91-column `monkeypatch.setattr` line is untouched.

The user directed that acceptance route through a non-author Operator on a
different model family. The risk class is declared material-behavior, which is
honest to the change and does not by itself require model independence, so the
different-family reviewer is a user instruction layered on top of the profile
rather than a claim about the class: the reviewing model must not be a Claude
model, and the report should record which model it was.

This request and its range live only on branch claude/gracious-grothendieck-98eb49
and are invisible from main, which is deliberate — both operator seats hold
in-flight requests from peer sessions (operator: 2026-07-26T08-02-33Z,
operator2: 2026-07-25T21-32-17Z), and publishing this into main's mailbox could
mask one of them in seat resolution. Nothing here consumes a cursor, and no push
or merge is requested or authorized.

## Finding Refs

- sha256:a0b99ff030ea7efd7cf09557dd59d3a74066739292233d7f0ddb81fb44a3722a
- sha256:b77400b5d0a5872bf5894ac9e10bdfb330072a712fd0d6c73511325b0e77f370

Cursor at send: 0
