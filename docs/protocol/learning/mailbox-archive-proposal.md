# O3 mailbox-archive proposal (not executed)

Standalone maintenance proposal required by ADR-067 O3 / learning-plane
plan §5 Stage 6. This file authorizes no archive run. A future change
that executes it is a high-risk-control compact pair of its own, with
contract I6 fail-closed backup.

## Why this is not a learning-plane stage

The mailbox is already the durable episode store. Archiving old events
does not extract, promote, or distribute a lesson. It is repository
maintenance that happens to shrink the tree the collectors walk.
Mixing it into a learning landing was the Stage 6 dissolution: the
curator was struck, and the archive was filed here.

## Proposed shape (when activated)

1. History-preserving `git mv` of aged events from
   `coordination/mailbox/sent/` to
   `coordination/mailbox/archive/<YYYY>/`, mirroring
   `pipeline/archive_handoffs.py` (clean worktree, `git mv` only, restore
   earlier moves on later failure).
2. **I6:** backup failure blocks. Before the first `git mv`, take a
   fail-closed copy of the sent tree (a git archive or a second
   worktree at the pre-move HEAD). If the copy cannot be verified
   (byte count + name list), refuse. If any `git mv` fails, restore
   already-moved paths and refuse. Recovery is explicit: the backup
   tree or the pre-move commit is the rollback, not a best-effort
   leftover.
3. Projections keep reading the archive. `pipeline/check_coordination.py`
   committed-mailbox projection, `pipeline/protocol_mailbox.py`
   candidate/checkpoint loaders, `pipeline/learning_metrics.py`,
   `pipeline/slope_metrics.py`, `pipeline/learning_index.py`, and
   `pipeline/bus_unread.py` must treat
   `coordination/mailbox/archive/<YYYY>/*.md` as the same evidence
   class as `sent/`. An archive that drops events from the projection
   is a history rewrite and is forbidden.
4. The writer continues to publish **only** into `sent/`. Archive is
   read-only. Cursors, kinds, and envelope identity do not change.
5. Refs already published as `coordination/mailbox/sent/<name>@<sha>`
   remain valid: git history still contains those blobs at those
   paths at those commits. Live HEAD paths for archived names become
   the archive path; loaders that resolve `path@commit` against the
   named commit are unaffected. Loaders that resolve a bare filename
   against HEAD must search `sent/` then `archive/`.

## Activation criterion (collector latency, not count)

Do not activate on event count alone. 889 sent events (measured
`git ls-tree -r HEAD --name-only coordination/mailbox/sent/` at the
parent of this proposal) is large, and the
`tests/unit/test_check_coordination.py` file is already the expensive
path, but `pipeline/learning_metrics.py` still returns in ~0.4 s on
that corpus.

Activate when a **named live collector** that operators actually run
— `pipeline/check_coordination.py` live snapshot, or the committed-
mailbox projection it uses — is measured at a pinned commit to exceed
a recorded budget that a seat cites as blocking orientation. Record
that measurement in the activating change (command, commit, seconds).
Until then, keep the corpus in `sent/`.

A count threshold may be *part* of the recorded budget (for example
"projection > N seconds at M events") but is not itself the trigger.

## Explicitly out of scope

- No deletion. No `git rm` of events.
- No rewrite of historical bytes (the reintroduction rule in
  `check_coordination.py` stays: byte-identical restore keeps the
  earliest introduction; mutated canonical review events stay fatal).
- No new mailbox kind.
- No cursor fast-forward as a side effect of archiving.
- No embeddings, no second index, no autonomous curator.

## Risk class when executed

`high-risk-control`: it mutates the evidence corpus layout that review
projections and unread accounting consume. Distinct non-author,
different-model actual-diff review, plus abuse-class assessment
(history rewrite, projection split-brain, cursor desync).
