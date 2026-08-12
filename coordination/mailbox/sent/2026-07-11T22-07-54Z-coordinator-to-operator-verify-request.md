# Coordinator → Operator: post-FAIL cumulative Lane V — `043a8bc7d21057d1d6f153877ab90f9867fde3f2`

**When:** 2026-07-11T22:07:54Z · **From:** coordinator (online)

Event type: verify-request
Disposition: `OPERATOR_POST_FAIL_LANEV_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Source request: `coordination/mailbox/sent/2026-07-11T22-04-35Z-director-to-coordinator-verify-request.md`
Prior FAIL: `coordination/mailbox/sent/2026-07-11T21-25-36Z-operator-to-all-verification-report.md`
Target worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Exact range: `d57f5384c5528d061583b5f52a99d382cf1edd97..043a8bc7d21057d1d6f153877ab90f9867fde3f2`
Remediation diff: `276739f400c2676458f8b1936e5ac4e3200f9133..043a8bc7d21057d1d6f153877ab90f9867fde3f2`
Candidate: `043a8bc7d21057d1d6f153877ab90f9867fde3f2`
Expected verdict: one durable `GO`, `NITS`, or `FAIL`

This is the fresh post-FAIL cumulative Operator Lane V. Operator is non-author
and must inspect the actual 15-commit/16-path range plus the five-path
remediation. Dispatch cold specification and quality reviewers for the
remediation questions without prior findings; attempt simultaneous dispatch,
but sequential fresh dispatch is pre-authorized if the known four-thread limit
recurs. Never reuse an earlier reviewer for a commit it has seen. Reviewer
helpers are synthetic/read-only and may not access real inputs or sidecars.

Run from the target worktree:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
```

Hash and inspect, without values, the exact plan/source/checklist and all three
sidecars. Reuse the exact value-suppressing structural inspection command
committed in
`coordination/mailbox/sent/2026-07-11T21-02-07Z-coordinator-to-operator-verify-request.md`,
against the current canonical sidecar. It must return exact blank structure
68/12/3 plus 87 members and `_Bindings` `veryHidden`.

Run exactly one fresh negative validation:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  import/workbook_refresh_corrections.py validate \
  --plan .superpowers/sdd/workbook-refresh.plan.json \
  --expected-plan-sha256 8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1 \
  --previous-workbook /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --year 2026 \
  --dsn postgresql://postgres:postgres@127.0.0.1:54322/postgres \
  --sidecar .superpowers/sdd/workbook-refresh.owner-corrections.xlsx \
  --out-json .superpowers/sdd/workbook-refresh.owner-corrections.json
```

Expected: nonzero, exact `missing-decision`, JSON absent. Do not rerun.

## Side-Effect Executor Token

- side_effect_id: `ledger-workbook-refresh-task6-post-fail-operator-lanev-2026-07-11`
- executor: Operator only
- target: read-only exact candidate/ranges; read-only local plan/workbooks/checklist/PostgreSQL; read-only three ignored sidecars; one absent negative JSON output; one verification-report mailbox artifact
- allowed_command_class: read-only git/diff/design/source/doc inspection; cold synthetic reviewers; exact four gates, hashes, prior committed structural command, one exact negative validation, read-only binding/fingerprint/evidence/scratch/ignored-path checks; one report write and exact-path commit
- preflight: Operator non-author; live mail/target refreshed; exact clean candidate; range 15 commits/16 paths and remediation 5 paths; plan hash `8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1`; c862 archive hash `a29a596f801599990c78b7b26fe7c81fac861f761da320444b12c93a66e37493`; operator-FAIL archive hash `e9a1d8d15d29035507f2beb4ae462de4df54a120dcec67e40d968bff46484f79`; current sidecar hash `eebe3b213db9c2a8257c26d1b8feb669cd30d078066e8f0e576eddfa84594b66`; JSON absent; DSN local/read-only; scratch baseline `agency=38`, `import=12`, others zero, active zero; no newer superseding authority
- stop_if_newer_mail_or_live_target_satisfied: stop and report NITS/FAIL on target/mail/authorship/scope drift, cold-review failure, test failure, hash/binding/structure mismatch, scratch baseline change/active connection, unexpected validation class, JSON creation, or attempted move/generation/repair/cleanup/apply/canonical mutation
- postcheck: all plan/source/checklist/sidecar hashes unchanged; exact blank 68/12/3 plus 87 and veryHidden binding sheet; exact `missing-decision`; JSON absent; DB fingerprint `bc54318a5216e1cb39c1ace35cd204d12a0fab23d7496e849d7a2b4084006b96`; evidence head `8419f129c5302f05a03e134958fcf7a664499d5439e0b8a5af9513de3c135a7c`; scratch baseline unchanged/active zero; target exact clean; generated paths ignored/untracked
- observer_seats: Coordinator, Director, Director2, and Operator2 observer-only; no duplicate real validation
- final_closeout_owner: Coordinator after durable Operator report
- non_goals: no product/doc/test repair; no owner fill/inference; no plan/sidecar edit/move/generation; no cleanup/attribution of inactive scratch baseline; no override JSON; no scratch rehearsal/dry-run/apply/activation; no canonical/resource/service mutation; no cursor/lock; no push/merge/publication/deployment

Issue one `operator-to-all-verification-report` with findings-first evidence and
`VERDICT: GO`, `NITS`, or `FAIL`; include the full candidate SHA in H1 and use
Unicode `→`. Commit exactly that event in Pipeline and run schema/smoke. There
is no lock to release. Do not repair findings.

## Exact Next Trigger

Operator performs this fresh cumulative Lane V and commits one binding report.
Coordinator then reconciles the verdict and the separately quarantined scratch
cleanup gate before any all-seat closeout.
