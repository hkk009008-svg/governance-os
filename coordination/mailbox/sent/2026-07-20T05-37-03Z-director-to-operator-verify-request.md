# Director → Operator: workbook refresh parser correction exact-range review

**When:** 2026-07-20T05:37:03Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Reviewed head: 2cb0be3493bbe67ba4989cca0da8deae67cdac98
Reviewed base: 043a8bc7d21057d1d6f153877ab90f9867fde3f2
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-workbook-refresh-2026-07-20
Task ID: ledger-workbook-refresh-0720-parser-review
Coordinator route: coordination/mailbox/sent/2026-07-20T05-13-22Z-coordinator-to-all-coordination.md@5b1922448a9183aeceeb7c7e7c86d8ee0752a692
Accepted baseline review: coordination/mailbox/sent/2026-07-11T22-24-50Z-operator-to-all-verification-report.md@19f0e93410828046744b5cfd8951edb1223494a5
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720
Target branch: codex/ledger-workbook-refresh-0720
Implementation commit: 2cb0be3493bbe67ba4989cca0da8deae67cdac98
Incoming workbook SHA-256: 58f15860b1acd440dccb5d4f853fb18bf2a3fbc5b4064543894fbbf90e66d917
Canonical workbook SHA-256: 50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8
Canonical checklist SHA-256: 14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5
Routed ignored checklist SHA-256: 0fb1c5d8ee801c7de07be8c44462666a0ecd2c31843d6d36b84337efa4d516fa
Finding IDs: FINDING-0720-DUPLICATE-COMMISSION-HEADER-LAST-WINS, FINDING-0720-CHECKLIST-IS-IGNORED-LOCAL-INPUT
Finding digest binding: sha256:c989bbc9e91995223269e8d2b3614bd77bea81642f4c574a3b970298165cd6ab is the UTF-8 SHA-256 of FINDING-0720-DUPLICATE-COMMISSION-HEADER-LAST-WINS; sha256:5caf8ef13cab5baac71cc3b37a37db1302eef00290cad538cad07607fa35d33d is the UTF-8 SHA-256 of FINDING-0720-CHECKLIST-IS-IGNORED-LOCAL-INPUT

## Outcome

Independently review the exact target range `043a8bc7d21057d1d6f153877ab90f9867fde3f2..2cb0be3493bbe67ba4989cca0da8deae67cdac98` and issue GO only if the bounded duplicate-header correction is acceptable with no unresolved hard boundary.

Confirm the parser now preserves the first cleaned occurrence of every main-sheet header name by one generic lookup rule, with no hard-coded column position or `수수료` special case. Confirm the non-vacuous synthetic regression places the semantic commission header and value first, then a whitespace/newline-equivalent helper header with an incompatible monetary value, demonstrated RED as `12345678 != 0.25`, and now passes while an ordinary unique `판매가` header remains unchanged. Confirm required fields, scalar fields, PPL fields, and derived fields all consume the same first-occurrence map, and no last-wins sibling remains.

Independently assess the adversarial boundary: first-occurrence is deterministic precedence, not duplicate-header rejection. A misleading earlier duplicate could still bind before a later intended field, including a theoretical quiet skip if earlier required-field duplicates are blank. Decide whether that inverse-order residual is acceptable under the explicit routed first-occurrence policy and unchanged anomaly contract, or whether it is a material hard finding. Do not treat this request as claiming general duplicate rejection.

Confirm the actual committed range contains exactly one commit and exactly the two allowed tracked paths. Confirm `data/merges.csv` remains ignored and untracked, is the canonical checklist bytes as an exact prefix plus exactly seven routed `2026-07-20 owner` decisions in preserved schema/order/BOM, and the canonical checklist retains its original hash. Confirm no ignored workbook, database dump, plan, report, or other business output was added.

Fresh Director evidence at the reviewed head is: focused regression 1 passed; complete `import/tests` 466 passed; complete `tests/unit` 85 passed; target smoke OK. The exact incoming workbook hash matched and aggregate-only parsing produced 481 scanned, 476 emitted, five dropped with four `missing_required_field` and one `unparseable_date`, nine anomalies, 431 numeric `commission_rate` values all within 0 through 1, 45 null values, and zero numeric values above 1. No business-row contents were recorded. Fresh independent task and whole-range reviews found no Critical, Important, or Minor issue; formal acceptance belongs only to Operator.

Confirm the incoming workbook, canonical workbook, canonical checklist, normal evidence-ledger checkout, older workbook-refresh worktree, and Pipeline protected files remain unchanged. Issue NITS or FAIL with exact evidence if scope, provenance, first-occurrence semantics, malformed-workbook handling, checklist isolation, aggregate truth, or any other boundary is unacceptable.

## Target Allowed Paths

- import/parse_workbook.py
- import/tests/test_parse_workbook.py

## Local Ignored Review Input

- data/merges.csv

This file is evidence-only local planning input. It is not in the reviewed Git diff and must remain ignored and untracked.

## Verification Commands

- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720 show --format='%H %P %s' --no-patch 2cb0be3493bbe67ba4989cca0da8deae67cdac98`
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720 merge-base --is-ancestor 043a8bc7d21057d1d6f153877ab90f9867fde3f2 2cb0be3493bbe67ba4989cca0da8deae67cdac98`
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720 diff --name-status 043a8bc7d21057d1d6f153877ab90f9867fde3f2..2cb0be3493bbe67ba4989cca0da8deae67cdac98`
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-0720 diff --check 043a8bc7d21057d1d6f153877ab90f9867fde3f2..2cb0be3493bbe67ba4989cca0da8deae67cdac98`
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests/test_parse_workbook.py::test_duplicate_cleaned_header_preserves_first_occurrence -q` and require 1 passed.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q` against only ephemeral synthetic databases through the already-running local listener and require 466 passed.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q` and require 85 passed.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` and require OK.
- Run `shasum -a 256` on `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx`, `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`, `/Users/hyungkoookkim/evidence-ledger/data/merges.csv`, and the routed ignored checklist; require the exact hashes above.
- Parse only `/Users/hyungkoookkim/Downloads/홈쇼핑_0720.xlsx` with the reviewed `parse_workbook.parse(..., year=2026)` and record only the aggregate fields bound above; do not print or persist business-row contents.
- Prove the routed ignored checklist is ignored/untracked, begins with the exact canonical checklist bytes, contains exactly seven appended rows matching the route with seven `2026-07-20 owner` notes, and adds no other ignored data or output.
- Inspect the actual diff and all parser lookups; audit duplicate order, cleaned-name collisions, blank earlier required-field duplicates, unique headers, malformed workbooks, and accidental scope or data leakage.

## Finding Refs

- coordination/mailbox/sent/2026-07-20T05-13-22Z-coordinator-to-all-coordination.md@5b1922448a9183aeceeb7c7e7c86d8ee0752a692
- sha256:c989bbc9e91995223269e8d2b3614bd77bea81642f4c574a3b970298165cd6ab
- sha256:5caf8ef13cab5baac71cc3b37a37db1302eef00290cad538cad07607fa35d33d

## Boundaries

This request authorizes Operator on gpt-5.6-terra to inspect Pipeline and the exact target range read-only, run only the listed local checks, use the already-running local database listener only for the test suite's ephemeral synthetic databases, read the exact incoming workbook and ignored checklist only for the bounded aggregate/hash/prefix/decision checks above, and publish exactly one canonical committed verification-report. It does not authorize implementation or repair, planner execution, row-content reporting, canonical or normal-checkout mutation, checklist mutation, force-add, database/resource mutation outside ephemeral tests, service start/stop/restart/reset, scratch creation, dependency installation, provider or network action, merge, push, deployment, cursor consumption, lock action, spend, cleanup, reset, rebase, amend, or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
