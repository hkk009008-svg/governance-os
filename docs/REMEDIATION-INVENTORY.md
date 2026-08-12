# Remediation Inventory

This coordinator-owned inventory is the source of truth for Wave gate rows in
the Pipeline governance-kernel checkout. It intentionally starts with no data
rows: the current evidence-ledger Phase 2 work is routed through capacity
packets and mailbox artifacts, not through remediation defect rows.

When a coordinator accepts a Pipeline remediation defect into a wave, add one
row to the table below. Do not add synthetic `verified` rows just to satisfy a
gate; `verified` requires the owning operator verification-report GO plus its
executed evidence.

| id | subsystem | file:line | severity | priority | fail-mode | repro | xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |
|----|-----------|-----------|----------|----------|-----------|-------|-----------|------------|-------------|------|--------|----------|-------|
