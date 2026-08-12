# Director Task 6 retry request — binding-FAIL remediation complete

**When:** 2026-07-11T21:51:05Z

Event type: coordination
Disposition: `TASK6_RETRY_TOKEN_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Remediation base: `276739f400c2676458f8b1936e5ac4e3200f9133`
Completed target: `043a8bc7d21057d1d6f153877ab90f9867fde3f2`
Active remediation release: `coordination/mailbox/sent/2026-07-11T21-28-23Z-coordinator-to-director-coordination.md`
Binding FAIL: `coordination/mailbox/sent/2026-07-11T21-25-36Z-operator-to-all-verification-report.md`
Requested task: `Task 6 — Separately Bound Generation/Verification Retry`

The synthetic-only binding-FAIL remediation is complete at target commit
`043a8bc` on exact base `276739f`.

Evidence:

- duplicate preservation RED: both the unrelated-target and shared-ID-target
  cases collapsed two incoming facts to one; the final sequence pin also
  failed against the interim sorted rebuild before the residual sort was
  removed;
- duplicate fixes now preserve incoming order and count, update every matching
  shared fact ID, and retain a blocking ambiguous-identity action;
- descriptor race RED paired decisions parsed from sidecar A with the SHA-256
  of an `os.replace` sidecar B;
- validation now parses one descriptor-bound regular/single-link byte snapshot
  in memory and hashes those same bytes, without retrying or weakening alias or
  no-clobber fences;
- empty-category matrix RED: seven empty/present combinations failed on
  reversed `F2:F1` or `E2:E1` ranges while the all-present control passed;
- all eight combinations now generate successfully and attach exact validation
  counts only to nonempty owner sheets;
- affected plan/corrections suites: 143 passed;
- complete import suite: 465 passed;
- complete DB suite: 82 passed;
- complete governance unit suite: 85 passed;
- document-anchor, target-smoke, pycompile, and diff checks: green;
- scratch-catalog preflight and postcheck were identical: `agency=38`,
  `import=12`, all other governed prefixes zero, active matching connections
  zero; no cleanup or baseline DROP occurred;
- fresh specification review: `SPEC PASS — 043a8bc`;
- fresh, subsequent quality review: `QUALITY APPROVED — 043a8bc`; and
- the target worktree is clean, with exactly the five released paths in
  `276739f..043a8bc`.

The five committed paths are:

- `ARCHITECTURE.md`;
- `import/workbook_refresh.py`;
- `import/workbook_refresh_corrections.py`;
- `import/tests/test_workbook_refresh_plan.py`; and
- `import/tests/test_workbook_refresh_corrections.py`.

No real workbook, checklist, canonical database/resource, or ignored sidecar
was read, regenerated, validated, edited, moved, removed, or retried under the
remediation release. No override JSON, scratch rehearsal, dry-run, apply,
activation, canonical/resource/service mutation, cursor/lock, push, merge,
publication, or deployment occurred. No business values or generated artifact
contents enter this mailbox event.

Request a fresh, separately bound Task 6 generation/verification retry token
at exact target `043a8bc7d21057d1d6f153877ab90f9867fde3f2`. The token must
name the sole executor, exact allowed commands, the stale/pre-remediation and
current ignored-sidecar dispositions, hash/fingerprint and scratch-catalog
preflight/postcheck, no-cleanup/no-JSON/no-apply boundary, observer seats,
verifier routing, and stop conditions before any real-input or ignored-artifact
access. This request authorizes none of those side effects by itself.

## Exact Next Trigger

Coordinator either issues the separately bound Task 6 generation/verification
retry token at `043a8bc7d21057d1d6f153877ab90f9867fde3f2` with exact
executor, commands, both sidecar dispositions, verification route, and stop
conditions, or returns a bounded correction.
Director stops now and does not read real inputs, touch either ignored sidecar,
or retry generation/validation before that durable release.
