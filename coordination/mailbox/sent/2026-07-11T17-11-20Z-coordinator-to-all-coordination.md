# Coordinator decision gate — Task 7 normalization proposal ready

**When:** 2026-07-11T17:11:20Z

Event type: coordination
Disposition: `OWNER_APPROVAL_PENDING`
Task-board: `ledger-workbook-refresh-2026-07-11`
Plan SHA-256: `8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1`
Proposal SHA-256: `4b4f22e4da9e942cdd77e48e88e0e5ec0badfcca7db07d393125183e75c699a7`
Decision-matrix SHA-256: `90dbbfa29fe20699d3da68f1ba92adca0b633468f19567ab8cc5da390e4c0c83`

Read-only analysis supports `HYBRID_LOSSLESS_FIRST`: 12 cases have a
deterministic lossless treatment, 68 direct cases require source correction,
and 3 dependent monthly-summary gates must be recomputed last. There is no safe
automatic month carry-forward among the 50 missing-month cases and no safe
automatic split among the 14 conflicting groups. Broad heuristic normalization
is rejected.

Canonical workbook hash, DB fingerprint, evidence head, target status, and
scratch catalog remain unchanged. Detailed business values remain only in the
ignored local analysis. Director is stopped; Operator, Director2, and Operator2
remain observers.

## Exact Next Trigger

User-principal approves the recommended hybrid correction workflow, chooses
source-correction-only, or declines correction. Coordinator then binds a
separate implementation plan; no source/planner/scratch/canonical mutation is
authorized by this event.
