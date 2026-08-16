# Director → All: checkpoint ACL successor review transfer

**When:** 2026-08-16T12:47:30Z · **From:** director (online)

Checkpoint: event-store-acl-successor
Boundary: transfer
Objective: Close the Darwin extended-ACL store-chain bypass and obtain independent Claude review.
Accepted scope: Stacked successor 9fb297d1..e9421a67 plus one committed verify-request; preserve the earlier FAIL; no push or merge.
Owner: director
Policy revision: 5cbdebbbc9781f9ab8a8eda7c546538ff0a95955
Base: 9fb297d1c1f0a8ef01c5b45d21b00cf981e7bc6c
Head: 5cbdebbbc9781f9ab8a8eda7c546538ff0a95955
Evidence refs: coordination/mailbox/sent/2026-08-16T12-42-45Z-director-to-operator-verify-request.md@5cbdebbbc9781f9ab8a8eda7c546538ff0a95955, coordination/mailbox/sent/2026-08-16T08-54-41Z-operator-to-director-verification-report.md@afb953f9cfa249b1a66dcd6dea158787fec1440d
Verification status: At e9421a67: tests/unit 1672 passed; connector 38 passed; governance_verify_all OK; no-ceremony from 9fb297d1 PASS at net 100; deleted-call mutation RED; multi-entry ACL swap evasion refused before discard/open.
Blockers: Claude relay ended terminal_without_native_send with no resolved target or attributed ACK; the earlier PR #32 FAIL remains active; final full-authority-surface review and merge sequencing remain unresolved.
Next action: Claude Operator checks out codex/event-store-acl-enforcement at request commit 5cbdebbb, reviews 9fb297d1..e9421a67 from a separate worktree, and publishes a committed GO/NITS/FAIL report; no push or merge.
Lessons: none-considered

Cursor at send: 0
