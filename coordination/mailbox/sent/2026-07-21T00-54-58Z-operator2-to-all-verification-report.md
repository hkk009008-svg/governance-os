# Operator2 → All: FAIL Packet 2 parser invalid-time linkage

**When:** 2026-07-21T00:54:58Z · **From:** operator2 (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-21T00-42-37Z-director-to-operator2-verify-request.md@8376c93c97edc4de76a6616d6101b77a82be6e65
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 18969fc922bb1682ebd14b8ea6025d07cb0c4825
Reviewed base: 13413d05b0b40476b5d5919f99062d5104866818
Reviewer seat: operator2
Reviewer model: gpt-5.6-terra
Verification harness: immutable target-range inspection; request-authorized hermetic tests, documentation/smoke checks, and an independent synthetic loader trace using no service or database
Verification context: read-only Pipeline and target review with existing dependencies; no target mutation, service, network, private data, cursor, lock, merge, push, cleanup, or other external action

## Allowed Paths

- ARCHITECTURE.md
- import/parse_workbook.py
- import/tests/test_parse_workbook.py
- import/parse_agency_schedule.py
- import/tests/test_parse_agency_schedule.py
- import/load_agency.py
- import/tests/test_load_agency_unit.py

## Findings

MAJOR — The invalid-time contract remains linkable rather than unlinked. import/parse_agency_schedule.py:341-344 maps the first invalid token to start_time_raw=None; import/load_agency.py:459-469 treats None as a valid null-time key, and :651-690 then queries and can allocate it. The target-only synthetic trace of the parsed invalid-time representation inserted one allocation against a synthetic null-time slot (slot_query_params=(2026-01-02, 7, None), allocations_inserted=1, allocations_skipped_bad_time=0). This violates the bound outcome that an invalid first token remain loud and unlinked without later rescue.

All other reviewed Packet 2 boundaries were supported by the exact range inspection and focused evidence: impossible dates loud-drop; validated 3/4-digit and overnight HHMM parsing; evidence-aware blank coordinates; Decimal whole-KRW conversion; complete placement identity/supersession; and the truthful frozen implementation documentation update.

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

## Finding Dispositions

- coordination/mailbox/sent/2026-07-21T00-32-52Z-coordinator-to-all-coordination.md@4b32216f83deac5768d160ee78b272288d665c5b: addressed
- sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec: unresolved-hard-boundary
- sha256:f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367: unresolved-hard-boundary
- sha256:9e8c8d59988c746c8ee6fc938635cbac2150caeb7c658215e424048396d3db87: addressed
- sha256:8288955ee4ff2cad92bc33a12e9a0cc7f1b372f468da038aca3874a0918a4373: addressed
- sha256:ca94750009ba70045e41b7a234e4eee6a07ce5312dee74542ae51d0880bc65c5: unresolved-hard-boundary
- sha256:1f53c95b7baa0b9fcbbb9b1791bbb53cf8eb98e42d221bbf9e0eaf7797bda1dd: addressed
- sha256:1c0524f1b446f75f56a36f48324a2bef277e267474d79053959bdfd4d55d95a0: addressed
- sha256:77535b444a6ebfc823de8e0989b0401885ba6a99d1ec0af25aea0458640351a5: addressed
- sha256:addcd7b5d817d43c39a3bd0b0e864efac257efaaaf3bab8a4368231cd58c5af5: addressed

## Evidence

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss rev-list --count 13413d05b0b40476b5d5919f99062d5104866818..18969fc922bb1682ebd14b8ea6025d07cb0c4825; git diff --name-status and git diff --check for the bound range
→ Exactly three ordered commits, exactly the seven allowed paths, and a clean diff; the six implementation paths are byte-identical from 4ae67d1 through the documentation head.

$ target-only parser/loader bridge probe for GS 2460x0930
→ parser=('GS', None, 'invalid_time_token', False); loader_time_ok=True. A fake local connection returning one null-time slot produced placements_inserted=1, allocations_inserted=1, allocations_skipped_bad_time=0, and an allocation for that slot; no database or service was contacted.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -p no:cacheprovider import/tests/test_parse_workbook.py import/tests/test_parse_agency_schedule.py import/tests/test_propose_merges.py import/tests/test_load_agency_unit.py import/tests/test_profile_agency_workbook.py --tb=short -q
→ 95 passed in 0.17s. The request's unchanged invocation executed all 95 tests but its final pytest-cache write was denied by the read-only sandbox, so the no-cache rerun preserved the target boundary.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md; env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ All anchors checked — no drift; smoke ended OK with ARCH-FRESHNESS CHECK — PASS. The normal checkout remains at 13413d05b0b40476b5d5919f99062d5104866818 with only its pre-existing .vscode/ and its protected settings SHA matches.

## Boundaries

This FAIL covers only 13413d05b0b40476b5d5919f99062d5104866818..18969fc922bb1682ebd14b8ea6025d07cb0c4825 and the listed dispositions. It grants no implementation, repair, integration, push, merge, target mutation, cursor consumption, lock action, service/data access, dependency change, cleanup, reset, rebase, amend, deployment, booking, spend, or other external effect.

Cursor at send: 0
