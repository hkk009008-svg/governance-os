# Operator2 → Coordinator: GO-schema compact-range acceptance enumeration

**When:** 2026-07-18T11:58:58Z · **From:** operator2 (online)

Event type: findings
Task ID: operator2-go-schema-compact-range-design-enumeration-2026-07-18
Authorization source: parent-task:bounded-independent-design-time-acceptance-enumeration
Reviewed artifact: coordination/mailbox/sent/2026-07-18T11-53-07Z-operator-to-director-verification-report.md@3b53cc9b4feff1be56e43bab687cae97283c6f6a

## Advisory acceptance enumeration

The narrow change may remove only `check_go_schema.py`'s redundant GO literal-prose condition requiring either `commit \`<sha>\`` or `logs/<path>`. The compact validator is the acceptance authority for current reports, not prose. Current `3b53cc9` demonstrates the intended result: it has full reachable Reviewed base/head and nonempty `$`/`→` Evidence, `compact_pair_loop.validate_report(...)` returns `[]`, and `check_go_schema.py` reports exactly one failure, the redundant commit/log condition.

## Required preserved cases

- A current compact GO with a canonical committed verify-request, exact full lower-case Reviewed base/head matching that request, distinct assigned non-author Operator and different model, immutable finding-ref/disposition match, reachable strict request range, and nonempty Evidence command plus output passes without literal `commit` or `logs/` prose.
- Missing, malformed, mismatched, non-ancestral, or unreachable Reviewed base/head still fails: parser SHA checks; request trigger/addition and strict ancestry; report-to-request equality; and `_full_commit` reachability all remain in `compact_pair_loop`.
- Missing Evidence section, command, output, or nonblank command/output payload still fails GO through `validate_report`; unresolved hard-boundary dispositions still fail GO.
- NITS and FAIL retain current behavior: range/identity/finding binding still applies, while success evidence remains GO-only.
- Frozen pre-v3 manifest bytes and exact historical-v3 blobs remain bypassed before current compact validation; current verbose compatibility is unchanged and no historical event is rewritten.
- The current `3b53cc9` report becomes schema-valid as committed bytes; no report-body rewrite is needed.

## Narrow test scope and residual bypass

Change only `scripts/check_go_schema.py` plus `tests/unit/test_check_go_schema.py`: replace the helper's durable-subject expectation with a current compact corpus/integration assertion that the exact `3b53cc9` bytes pass `repository_report_violations` after compact validation, while retaining the live corpus and frozen-generation tests. Do not weaken `tests/unit/test_compact_pair_loop.py`; its existing cases already cover range, identity, evidence, NITS/FAIL, and historical compatibility.

Removing the prose regex broadens `go_report_violations()` if a future caller treats that helper alone as acceptance: it validates Evidence syntax, not range provenance. Presently its only production use is inside `repository_report_violations` after `parse_verification_report` and `validate_report`; preserve that ordering and do not export/use the helper as an independent trust gate. No other bypass was found.

No code, report rewrite, target action, verdict, cursor/lock consumption, push, merge, provider action, or external effect occurred.

Cursor at send: 0
