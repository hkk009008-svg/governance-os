# Remediation Inventory

This is the compatibility input for the optional hardening-wave checker. It is
not desktop-team status, a routine task list, or an authority source. It
intentionally starts with no data rows; use `team_status` for current member
and message state.

Add a row only when the accepted task deliberately schedules a confirmed defect
into a named remediation wave. Do not add synthetic `verified` rows just to
satisfy a gate. `verified` requires executed evidence and the temporary
independent reviewer's GO for the exact committed range when the risk class
requires review.

The column names `lane-owner` and `verifier` are frozen for compatibility with
the checker. They mean the current implementation owner and exact-range
reviewer, respectively; they do not create standing seats or roles.

| id | subsystem | file:line | severity | priority | fail-mode | repro | xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |
|----|-----------|-----------|----------|----------|-----------|-------|-----------|------------|-------------|------|--------|----------|-------|
