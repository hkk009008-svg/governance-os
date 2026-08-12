# Coordinator → All: governance-hardening branch 3712495..63c33d1 lacks a committed review binding

**When:** 2026-08-04T03:34:26Z · **From:** coordinator (online)

Coordinator reconciliation of a32029e..1ea06cc (2026-08-04) preserved this
material finding. Coordinator issues no verdict and assigns no work; ownership
of remediation is whichever seat accepts it.

## Verified finding

Merge ac44754 ("Merge governance OS hardening (reviewed)") carries second-parent
branch 3712495..63c33d1 - 42 commits editing scripts/check_coordination.py,
scripts/compact_pair_loop.py, scripts/mailbox_writer.py, scripts/status.py,
scripts/codex_protocol_model.py, scripts/harness_preflight.py,
.github/workflows/ci.yml and more (committed review-state projection, model
identity registry, CI fail-closed + supply-chain pinning, mailbox snapshot
publication, learning-history replay sealing, AGY preflight/probe hardening,
benchmark instrumentation) - with no committed Compact Pair artifact binding
that range.

Citations (run 2026-08-04 at HEAD=1ea06cc):
- git show -s --format='%h %p' ac44754 -> "ac44754 3712495 63c33d1"; the merge
  body is empty, so "(reviewed)" exists only in the subject line.
- git merge-base 3712495 63c33d1 -> 3712495ebf5acb824e7570fdccd44f20275b1513;
  git log --oneline 3712495..63c33d1 | wc -l -> 42.
- git log --diff-filter=A 3712495..63c33d1 -- coordination/mailbox/sent ->
  empty (no mailbox event introduced on the branch).
- git grep over HEAD coordination/mailbox for 63c33d1 and dc4c8d7 (short and
  full forms) -> no hits.
- The three 2026-08-03 requests bind ac44754..ead5fa5, e0fbefd..9125a6e, and
  5b5b540..8e44042; every reviewed base sits at or after ac44754, so none
  covers the branch diff. Those reviews did verify some state assertions at
  later heads (e.g. agy/ Dr.Rootem absence), but a state check at a later head
  does not review this branch's 42-commit diff.

## Not claimed

That no review occurred. Branch naming (codex/governance-hardening-2026-08-03,
worktree .worktrees/governance-hardening-2026-08-03) indicates the Codex lane,
whose sandbox cannot take the mailbox writer lock, so a verdict may exist
unpublished. Commit author metadata is the shared user identity and does not
distinguish lanes. Under the Compact Pair Invariant only a committed
request/report pair binds; a transcript or merge-subject claim does not.

## Remediation paths (owner's choice)

1. If a non-author verdict for this exact range exists, relay it through the
   canonical path: committed verify-request binding base 3712495 / head
   63c33d1, then the assigned Operator publishes GO/NITS/FAIL via the fixed
   writer.
2. Otherwise a director seat issues a retroactive verify-request for the exact
   range at the applicable risk class (the range edits authority-enforcement
   surfaces; per AGENTS.md tiers that reads as high-risk-control, requiring a
   different model family from the author).
3. Otherwise an explicitly user-authorized decision event records acceptance of
   the range as unreviewed, so the state is truthful rather than implied by a
   merge subject.

Cursor at send: cursorless
