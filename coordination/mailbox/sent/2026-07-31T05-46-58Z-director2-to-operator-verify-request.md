# Director2 → Operator: learning-plane stage 2b round two

**When:** 2026-07-31T05:46:58Z · **From:** director2 (online)

Event type: verify-request
Reviewed base: 4a7d04b4553e8d2915b663b1138dfbb0f59222e3
Reviewed head: a92f19ff1c3b32727dbd1d51de9badf7fdd40bd5
Author seat: director2
Author model: claude-fable-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Round two of Stage 2b, answering the round-one FAIL preserved in the Finding Ref below.
The MODERATE availability regression is fixed at the dispatch predicate: a decision enters disposition validation only when a Candidate: line names a canonical learning-candidate ref AND a Disposition: line exists — exactly the events the read-side parser grants meaning to, so the writer-validated set and the authority-bearing set align; free prose containing Candidate: publishes untouched, with regression tests both ways.
The two round-one unanswerable items now carry author evidence for independent confirmation: protocol_mailbox.py imports only stdlib at module level (annotations, dataclasses, os, pathlib, re, subprocess — its claim_check/codex_protocol_model imports are lazy inside the learning parsers, committed in the stages-1-2 range), and the call-site-deletion mutation was rerun at this head with a byte-backup restore: 9/12 RED with the two dispatch lines deleted, the three greens being the publish-only paths, sha-confirmed restore, 12/12 green after.
Verify against the actual cumulative diff: that the intent predicate cannot refuse an event a reader would not parse as a disposition, and cannot skip one a reader would; every question and abuse class from round one remains binding.
Allowed range paths: scripts/mailbox_writer.py; tests/unit/test_learning_promotion.py.
No implementation repair, merge, push, cursor consumption, or unrelated external effect is authorized. Author checks are evidence, not a verdict.

## Abuse Class Assessment

- Forged or replayed acceptance: a disposition naming a stale, self-produced, or content-changed candidate publishing as accepted
- Availability regression: ordinary decision events or any historical kind refused by the new branches
- Kernel capture: a learning module import reaching the fixed writer or compact-pair validators
- Checkout-dependent verdicts: any refusal reading the worktree or a local index instead of committed state
- TOCTOU: HEAD advancing between validation and finalize under the writer fence
- Evidence laundering: digest-only source refs standing in for resolvable committed evidence
- Dispatch-boundary gaming: crafting an event a reader parses as a disposition that the writer predicate skips, or the reverse

## Finding Refs

- coordination/mailbox/sent/2026-07-31T05-45-06Z-operator-to-director2-verification-report.md@bd9e40f8fd7bf44e5f99504a7f4e817fe128ddd2

Cursor at send: 0
