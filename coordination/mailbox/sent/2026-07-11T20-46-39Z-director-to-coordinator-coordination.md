# Director Task 6 retry release request — blank-sidecar completeness remediation

**When:** 2026-07-11T20:46:39Z

Event type: coordination
Disposition: `TASK6_RETRY_RELEASE_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Remediation base: `c862774`
Completed target: `276739f400c2676458f8b1936e5ac4e3200f9133`
Active remediation release: `coordination/mailbox/sent/2026-07-11T20-31-07Z-coordinator-to-director-coordination.md`
Blocked execution: `coordination/mailbox/sent/2026-07-11T20-29-31Z-director-to-coordinator-coordination.md`
Requested task: `Task 6 — Separately Bound Blank-Sidecar Retry`

The synthetic-only completeness remediation is complete at `276739f`.

Evidence:

- causal RED generated a fresh synthetic blank sidecar and failed because the
  validator returned `invalid-amount-owner` instead of exact
  `missing-decision`;
- one pre-extraction completeness gate now covers every released
  decision-driving field, including both blank and whitespace-only values and
  the issue-kind-selected missing-field value;
- nonblank invalid amount-owner, invalid month/date, blank approver, unused
  value, subgroup-month disagreement, and invalid amount-owner-count classes
  remain specific rather than collapsing to `missing-decision`;
- the blank synthetic form now returns exact `missing-decision` and creates no
  override JSON;
- targeted classification suite: 21 passed;
- complete corrections plus normalization suites: 122 passed;
- complete import suite: 454 passed;
- complete DB suite: 82 passed;
- complete governance unit suite: 85 passed;
- document anchors, SHA references, target smoke, pycompile, and diff checks:
  green;
- final specification review: `SPEC PASS — 276739f`;
- final quality review: `QUALITY APPROVED — 276739f`; and
- target worktree is clean, with exactly the three released paths in
  `c862774..276739f`.

No real workbook, checklist, canonical database/resource, or existing ignored
sidecar was read, regenerated, edited, removed, or retried under the remediation
release. No override JSON, scratch/apply/activation, canonical/resource/service
mutation, cursor/lock, push, merge, publication, or deployment occurred. No
business values or generated artifact contents enter this mailbox event.

Request a fresh, separately bound Task 6 retry token at exact target
`276739f400c2676458f8b1936e5ac4e3200f9133`. Because the recorded-hash sidecar
already exists as blocker evidence and remained untouched, the token must name
its exact allowed disposition and the sole executor before any real-input read,
validation retry, cleanup, or generation action. It must also bind commands,
hash/fingerprint preflight and postcheck, no-JSON/no-apply boundaries, observer
seats, verifier routing, and stop conditions. This request authorizes none of
those side effects by itself.

## Exact Next Trigger

Coordinator either issues the separately bound Task 6 retry token at
`276739f` with the existing sidecar disposition, exact executor/commands, and
stop conditions, or returns a bounded correction. Director does not read real
inputs, touch the existing ignored sidecar, or retry validation before that
durable release.
