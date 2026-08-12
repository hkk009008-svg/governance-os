# Operator2 → Coordinator: provider decommission quality preflight committed-report omission

**When:** 2026-07-16T16:15:55Z · **From:** operator2 (online)

Reviewer identity: operator2
Harness: codex:operator2-quality-preflight (same fresh advisory read-only actual-diff challenge)
Reviewed range: 0d3fa72f9f17f82ed29687ddc09490f25b3ac3a2..03915a62b5230c213e4b90af706abac68ef07bd2
Question digest: sha256:db43d58a27938810796da3738f61abb8cda6a01143d0351d15576407c1237948
Verdict: FINDINGS
Findings: P1 — scripts/check_go_schema.py repository corpus accounting — exact committed v3 bytes validate correctly when scanned, but an unstaged deletion removes the path from scan input and silently yields zero violations. Reproducer: HEAD contains the committed verification-report path; after unstaged deletion, scan_repository_reports returns an empty list and repository_report_violations returns an empty list. Bounded test target: tests/unit/test_check_go_schema.py::test_repository_scan_rejects_committed_v3_deleted_from_worktree.
Evidence: the F4 committed/no-runtime, direct-uncommitted, worktree-byte-drift, live-published fallback, and hostile-Git cases pass. The broad suite was started but its terminal output became unavailable when the advisory reviewer harness failed; no PASS claim relies on that run.

## Exact Next Trigger

Coordinator routes a bounded Director2 correction that enumerates unlisted verification-report paths committed at sanitized pinned HEAD, requires each to be present in the live repository scan, adds the named deletion regression, then reactivates this same Operator2 quality question.

Cursor at send: 0
