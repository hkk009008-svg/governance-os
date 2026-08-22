# Proportional independence (R-INDEPENDENCE)

Autonomous Seat Outcome Contract: pipeline/codex_protocol_model.py

This rule applies when work composes parseable/executable input, enforces an
authority or security boundary, gates a side effect, or validates a schema whose
acceptance grants trust.

The owner explicitly assesses plausible abuse classes, edge cases, and coverage
targets before implementing. It preserves all material independent findings as
immutable refs through ownership changes and review. The owner chooses methods
and the actual-diff reviewer chooses proportional review depth.

Early independent review is encouraged when it adds signal, especially for a
novel or high-consequence surface. It is advisory: there is no universal
preflight CLEAR. A FINDING is not BLOCKED unless it identifies an
unresolved hard-boundary violation.

Behavior-changing acceptance requires a non-author reviewer from a distinct
identity to review the actual commit or range. High-risk control additionally
requires a reviewer from a distinct seat and different system-visible model
family, plus explicit abuse-class assessment. That
reviewer cannot verify authored work and issues GO/NITS/FAIL through the fixed mailbox writer.

The two live identities are `author` and `reviewer` (`pipeline/protocol_mailbox.py`
`ROLES`); the six pre-collapse seat names remain readable in committed history
and are not positions anyone occupies. "Distinct seat" above means an identity
that is not the author's.
Review depth is proportional; actual-range binding, finding
preservation, and non-authorship remain strict once review is triggered.

R-VERIFY-TIER still prevents redundant same-question passes. A later reviewer
must disposition every carried finding ref; changing owners or reviewers cannot
erase material evidence.

External effects remain separately user-authorized for the exact
effect/executor/target/scope. A structural seat-authored token never grants
execution authority.

## Evidence

- owner abuse assessment and coverage selected for the task;
- immutable material finding refs, including explicit empty state;
- committed verify-request bound to the actual base/head and identities;
- non-author reviewer report with explicit dispositions and, for
  `high-risk-control`, a different model family plus abuse-class assessment.

Canonical Compact Pair Invariant: pipeline/codex_protocol_model.py
