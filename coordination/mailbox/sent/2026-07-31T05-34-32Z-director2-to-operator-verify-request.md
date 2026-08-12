# Director2 → Operator: learning-plane stages 1 and 2

**When:** 2026-07-31T05:34:32Z · **From:** director2 (online)

Event type: verify-request
Reviewed base: 1b7c89bcc43aeff2fa769b84f7e74486cd857d4d
Reviewed head: 4a7d04b4553e8d2915b663b1138dfbb0f59222e3
Author seat: director2
Author model: claude-fable-5
Assigned operator: operator
Risk class: material-behavior

## Outcome

Stages 1 and 2 of the learning-plane plan (ADR-067, docs/protocol/learning/contract.md at the merged Stage 0).
Stage 1: scripts/learning_index.py builds an FTS5 episodic index from the COMMITTED tree at the build commit (never the worktree) over mailbox events, docs/HANDOFF-*, docs/superpowers/plans, and logs jsonl ledgers; every row carries source path, scope, per-source-rule timestamp, and git blob SHA; meta records the build commit; availability follows the bus_unread None-vs-empty taxonomy; the ingest boundary refuses user-scope paths; coordination/learning/ is gitignored.
Stage 2: kinds.txt gains learning-candidate AND retires memory-candidate in the same commit (O1 ruling; zero committed instances at the ADR baseline); protocol_mailbox gains parse_learning_candidate_statement and parse_learning_disposition_statement plus committed_learning_candidate_ids (dedup from committed events at a pinned commit); Candidate ID is the sha256 of the normalized payload, recomputed at parse; send-event gains a wrapper-side pair-seat gate for the new kind labeled bypassable until Stage 2b; the coordination/README v5 note is rewritten; every refusal is advisory until Stage 2b and tests and docstrings say so.
Verify against the actual diff: that the index reads only the committed tree and refuses the named user-scope shapes; that None-vs-empty is honest in both directions; that the same commit both adds and retires the registry kinds with the doc sweep complete (grep memory-candidate across the head tree); that the candidate-ID recomputation cannot be satisfied by a wrong embedded ID; that the I1 import test actually parses kernel imports rather than pattern-matching text; and that no parser or gate in this range claims publication-time enforcement.
Allowed range paths: .gitignore; coordination/README.md; coordination/bin/send-event; coordination/mailbox/kinds.txt; scripts/learning_index.py; scripts/protocol_mailbox.py; tests/unit/test_learning_candidate.py; tests/unit/test_learning_index.py.
No implementation repair, merge, push, cursor consumption, or unrelated external effect is authorized. Author checks are evidence, not a verdict.

## Finding Refs

Cursor at send: 0
