# Coordinator owner decision — analyze Task 7 quarantines

**When:** 2026-07-11T17:00:39Z

Event type: coordination
Disposition: `OWNER_DECISION_ANALYZE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Plan SHA-256: `8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1`

The user-principal selected option 1: analyze and propose exact normalization
rules for approval. This authorizes read-only analysis of the existing ignored
plan, both workbook inputs, checklist, and canonical database. It does not
authorize source edits, planner changes, scratch cloning/apply, quarantine
suppression, or canonical mutation.

Produce one local ignored proposal that, for each reason class, records:

- observed structural cause and whether it is stable across old/new workbook;
- authoritative source and safe derivation candidates;
- exact deterministic rule, or `manual-only` when no lossless rule exists;
- affected fact count and non-business-value identifiers/hashes;
- rejection/stop conditions and non-vacuous tests required before adoption;
- effect on preservation, monthly reconciliation, and directional reporting.

The exact corrected reason split is 50 missing placement payment months, 14
conflicting grouped payment months, 10 parser anomalies, 6 unheaded cells, and
3 monthly-summary mismatches. Keep detailed business values local-only; mailbox
reporting is counts, reason classes, and hashes only.

## Exact Next Trigger

Director returns the hash-bound normalization proposal and a ranked owner
decision matrix. Coordinator presents it to the user-principal; no production
or data mutation begins without the user's second explicit approval.
