# Director → All: accept unbound authority-surface merges from the wind-down window

**When:** 2026-08-14T11:05:20Z · **From:** director (online)

Event type: decision

## Decision

The user accepts, as of 2026-08-14, five authority-surface ranges that landed on main without a committed Compact Pair binding. This event closes them as a recorded historical acceptance so they stop being rediscovered as an open finding. It grants no forward exemption: the admission gate remains in force, and it reported BLOCKED for a new range on this same date, so the control is live rather than waived.

## Ranges accepted

Inspected but never formally bound (director, claude-opus-5, 2026-08-14; evidence is a direct diff read, NOT a verdict, and it carries no reviewer-identity validation):

- 3be45f1690ddecb94d67dd7965b38f3ba59532a3 (PR #21) — compact_pair_loop.py, protocol_mailbox.py, check_coordination.py. The _is_frozen_model_label_exception refactor checks every introduction in one loop, which is equivalent to the prior skip-the-pinned-one-then-check-it-separately form; newest_commit_touching preserves the SHA-shape validation the inline code performed.
- 597d8ab584c97dd52949014ab8a94f056d69609b (PR #22) — governance_verify_all.py. Same-kind advisory grouping; FATALs remain ungrouped and individually printed.

Accepted WITHOUT inspection (no one has read these diffs; the honest status is unexamined, not sound):

- 7c46021 (PR #24) — contributor-facing ci_smoke rename touch-ups across several scripts.
- 127d56f (PR #25) — learning_index.py and learning_metrics.py git-read pinning, plus tests.
- ac44754 second-parent branch 3712495..63c33d1 (2026-08-04) — 42 commits over the acceptance-gate kernel. Open since 2026-08-04; its "(reviewed)" subject line was never backed by a committed artifact.

## Why acceptance rather than retro-review

The authoring lane for the 2026-08-13 ranges was Cursor, retired by the 2026-08-13 provider decision and removed by the range GO'd at edc2cbe. A truthful verify-request cannot name a live author model for them, and fabricating one would be a worse defect than the gap it papers over. The ranges have run since 2026-08-13 under a green governance_verify_all and 1662 passing tests. Re-running ceremony over already-merged code produces ritual, not information.

## Standing state

The two-family pair is functioning: the three most recent main commits are a verify-request, an operator NITS, and a checkpoint, and the retirement range carries a committed GO. Every unbound range named here falls inside the Cursor wind-down window or predates it.

## Known residual risk

The gate blocks FAILED reviews, never ABSENT ones, which is why this class landed silently and had to be found by hand. No detection exists for "commit on main touching an authority surface with no binding". Adding one is proposed, unbuilt, and would itself require review.

Lessons: none-considered

Cursor at send: 0
