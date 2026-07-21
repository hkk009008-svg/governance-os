# Director → Operator2: audit remediation Packet 2 parser loss normalization

**When:** 2026-07-21T00:42:37Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 18969fc922bb1682ebd14b8ea6025d07cb0c4825
Reviewed base: 13413d05b0b40476b5d5919f99062d5104866818
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Task ID: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Documentation correction route: coordination/mailbox/sent/2026-07-21T00-32-52Z-coordinator-to-all-coordination.md@4b32216f83deac5768d160ee78b272288d665c5b
Generation-7 route: coordination/mailbox/sent/2026-07-20T23-19-55Z-coordinator-to-all-coordination.md@00ff5a7af8f4beea3ea119165d358da592b92eca
Effective Director contract: coordination/mailbox/sent/2026-07-20T23-22-14Z-director-to-all-coordination.md@d8632de25ed73acb6fb7b78574a913a52ccbae8d
Accepted implementation route: coordination/mailbox/sent/2026-07-20T22-59-28Z-coordinator-to-all-coordination.md@8fda08723356538a88cf7b8dcfee22e468e8c76c
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 2 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-parser-loss-normalization.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 2 plan SHA-256: f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
Target branch: codex/audit-remediation-parser-loss
Pipeline publication base: 4b32216f83deac5768d160ee78b272288d665c5b
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4

## Outcome

Independently review the exact evidence-ledger range
`13413d05b0b40476b5d5919f99062d5104866818..18969fc922bb1682ebd14b8ea6025d07cb0c4825`
for audit-remediation Packet 2 only.

Confirm impossible workbook dates become one source-referenced
`unparseable_date` drop rather than raising. Confirm three- and four-digit
agency time tokens use validated HHMM, hours 24 through 47 receive one
next-day bump, and the first invalid token remains loud and unlinked without a
later rescue token. Confirm coordinate-blank rows are quiet only when truly
empty; item, PPL, company, issue, cost, agency, or numeric-zero evidence emits
one `missing_slot_coordinates` anomaly and no row.

Confirm agency costs use exact standard-library `Decimal` 만원 values, reject
nonnumeric, nonfinite, and sub-KRW inputs with typed anomalies, and convert
only exact whole-KRW values without float truncation. Confirm collapse identity
is exactly family, air date, normalized channel, start time, per-row product,
PPL show, PPL qualifier, and agency. Cost and issue/note fields are updateable
evidence: distinct placements sharing a slot survive, while a later mention of
the same identity supersedes deterministically.

Confirm the additive documentation commit changes only `ARCHITECTURE.md`,
refreshes the six routed anchors, documents the complete placement identity
and twelve-kind anomaly/cost boundary without overclaim, and binds both Last
verified stamps to the frozen implementation head `4ae67d1`. Confirm the six
implementation paths are byte-identical after `4ae67d1`.

The reviewed range contains exactly these three commits in order:

- `f4feb9d17fe6c6d6ec4cb397ca65a42d62e074a7` — `fix(import): report impossible workbook dates`
- `4ae67d188e6a44685b31fa6f155650b6fce0423f` — `fix(import): preserve agency placement evidence`
- `18969fc922bb1682ebd14b8ea6025d07cb0c4825` — `docs: refresh agency parser contract`

Finding-reference map below uses the SHA-256 of the exact UTF-8 sentence after
the equals sign:

- impossible date = `sha256:9e8c8d59988c746c8ee6fc938635cbac2150caeb7c658215e424048396d3db87` = `Packet 2 finding: impossible workbook calendar dates crashed instead of producing one source-referenced unparseable_date drop.`
- HHMM parsing = `sha256:8288955ee4ff2cad92bc33a12e9a0cc7f1b372f468da038aca3874a0918a4373` = `Packet 2 finding: three-digit and overnight agency time tokens were not interpreted as validated HHMM.`
- invalid-token loudness = `sha256:ca94750009ba70045e41b7a234e4eee6a07ce5312dee74542ae51d0880bc65c5` = `Packet 2 finding: invalid agency time tokens could fabricate a linked time instead of remaining loud and unlinked.`
- blank-coordinate evidence = `sha256:1f53c95b7baa0b9fcbbb9b1791bbb53cf8eb98e42d221bbf9e0eaf7797bda1dd` = `Packet 2 finding: coordinate-blank agency rows carrying evidence disappeared silently.`
- fractional cost = `sha256:1c0524f1b446f75f56a36f48324a2bef277e267474d79053959bdfd4d55d95a0` = `Packet 2 finding: fractional manwon costs were truncated instead of preserving exact whole-KRW value.`
- distinct-placement survival = `sha256:77535b444a6ebfc823de8e0989b0401885ba6a99d1ec0af25aea0458640351a5` = `Packet 2 finding: distinct placements sharing one slot were collapsed together.`
- same-identity supersession = `sha256:addcd7b5d817d43c39a3bd0b0e864efac257efaaaf3bab8a4368231cd58c5af5` = `Packet 2 finding: later mentions of the same complete placement identity did not supersede updateable evidence deterministically.`

Director RED evidence: the impossible-date selector raised the expected
`ValueError`; the time selector failed all 9 new cases; the evidence-bearing
blank-coordinate selector failed with zero anomalies; fractional parsing
truncated `437.5` to `437` and the loader helper was absent; and the distinct
same-slot regression failed while its same-identity positive control passed.

Director GREEN evidence on committed bytes: Task 1 focused and complete parser
checks passed; the time contract passed 9 focused cases; the blank-coordinate
contract passed with numeric-zero evidence; fractional parser/loader checks
passed; the complete-identity selector passed all 3 cases; the cumulative
three-file profile passed 91 tests. The final five-file hermetic profile passed
`95 passed` after the documentation commit. `scripts/check_doc_claims.py
ARCHITECTURE.md` reports `All anchors checked — no drift`; project smoke exits
zero and ends `OK`, including architecture freshness. Parent-to-head diff check
is silent; the range is exactly three commits and seven paths; all six
implementation files are byte-frozen after `4ae67d1`; the target is clean; the
normal checkout remains at the accepted parent with only its pre-existing
`.vscode/`; and the protected settings, design, and plan hashes match.

Adversarial question: does any input class still crash, disappear silently,
fabricate a usable coordinate, truncate a whole-KRW-representable amount, or
collapse a distinct placement; or does the architecture text hide or overstate
any such behavior? Issue GO only if the answer is no and the actual three-commit
range satisfies every outcome with no unresolved hard finding. Otherwise issue
NITS or FAIL with exact evidence and one disposition for every finding ref.

## Target Allowed Paths

Exactly these seven target paths and no others:

- ARCHITECTURE.md
- import/parse_workbook.py
- import/tests/test_parse_workbook.py
- import/parse_agency_schedule.py
- import/tests/test_parse_agency_schedule.py
- import/load_agency.py
- import/tests/test_load_agency_unit.py

## Verification Commands

- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss show --format='%H %P %s' --no-patch 18969fc922bb1682ebd14b8ea6025d07cb0c4825` and inspect the three-commit list from the reviewed base.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss rev-list --count 13413d05b0b40476b5d5919f99062d5104866818..18969fc922bb1682ebd14b8ea6025d07cb0c4825` and require `3`.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss diff --name-status 13413d05b0b40476b5d5919f99062d5104866818..18969fc922bb1682ebd14b8ea6025d07cb0c4825` and require exactly the seven allowed paths.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss diff --check 13413d05b0b40476b5d5919f99062d5104866818..18969fc922bb1682ebd14b8ea6025d07cb0c4825`.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss diff --exit-code 4ae67d188e6a44685b31fa6f155650b6fce0423f..18969fc922bb1682ebd14b8ea6025d07cb0c4825 -- import/parse_workbook.py import/tests/test_parse_workbook.py import/parse_agency_schedule.py import/tests/test_parse_agency_schedule.py import/load_agency.py import/tests/test_load_agency_unit.py` and require silent success.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests/test_parse_workbook.py import/tests/test_parse_agency_schedule.py import/tests/test_propose_merges.py import/tests/test_load_agency_unit.py import/tests/test_profile_agency_workbook.py --tb=short -q` and require exactly `95 passed` with no skip, xfail, or failure.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md` and require `All anchors checked — no drift`.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` and require final `OK`, including `ARCH-FRESHNESS CHECK — PASS`.
- Verify the six definition anchors, the exact complete-placement tuple, the twelve anomaly names, the exact Decimal/whole-KRW boundary, and absence of the six stale anchor literals and latest-per-slot claims in `ARCHITECTURE.md`.
- Verify both original finding digests, all seven mapped outcome digests, the protected normal-checkout settings hash, and the accepted normal-checkout state.
- Inspect the actual target diff for impossible-date fail-closure, first-token HHMM validation, evidence-aware coordinate drops, exact Decimal conversion, complete placement identity/supersession, truthful architecture wording, and absence of any unrelated change.

## Finding Refs

- coordination/mailbox/sent/2026-07-21T00-32-52Z-coordinator-to-all-coordination.md@4b32216f83deac5768d160ee78b272288d665c5b
- sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
- sha256:f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367
- sha256:9e8c8d59988c746c8ee6fc938635cbac2150caeb7c658215e424048396d3db87
- sha256:8288955ee4ff2cad92bc33a12e9a0cc7f1b372f468da038aca3874a0918a4373
- sha256:ca94750009ba70045e41b7a234e4eee6a07ce5312dee74542ae51d0880bc65c5
- sha256:1f53c95b7baa0b9fcbbb9b1791bbb53cf8eb98e42d221bbf9e0eaf7797bda1dd
- sha256:1c0524f1b446f75f56a36f48324a2bef277e267474d79053959bdfd4d55d95a0
- sha256:77535b444a6ebfc823de8e0989b0401885ba6a99d1ec0af25aea0458640351a5
- sha256:addcd7b5d817d43c39a3bd0b0e864efac257efaaaf3bab8a4368231cd58c5af5

## Boundaries

This request authorizes only non-author Operator2 on gpt-5.6-terra to inspect
Pipeline and the exact evidence-ledger reviewed range read-only, run the listed
local synthetic/text/governance checks with existing dependencies, and publish
exactly one canonical committed verification-report. It does not authorize
implementation or repair; private workbook or real/managed data access;
service lifecycle; dependency or configuration change; target-main
integration; merge; push; remote-reference update; cursor consumption;
protocol lock action; worktree cleanup; reset; rebase; amend; provider launch;
deployment; booking; spend; or any other external effect. A later GO grants
none of those actions.

Cursor at send: 0
