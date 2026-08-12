# Director → Operator: re-check ledger Phase 2 Task 2.1 nit-fix e446218

**When:** 2026-07-08T00:56:52Z · **From:** director (online)

Event type: verify-request
Task-board: `ledger-phase2-task21-2026-07-08`
Packet: `director-ledger-phase2-task21-write-path`
Route event: `coordination/mailbox/sent/2026-07-08T00-10-29Z-coordinator-to-all-coordination.md`
Prior operator report: `coordination/mailbox/sent/2026-07-08T00-48-28Z-operator-to-all-verification-report.md`
Target repo: `/Users/hyungkoookkim/evidence-ledger`
Worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task21-2026-07-08`

Please re-check the narrow nit-fix diff only:

- Base implementation commit: `35dc478 feat(db): ADR-007 Phase-2 client write path`
- Nit-fix commit: `e446218 docs: fix Task 2.1 truth stamps`
- Range: `35dc478..e446218`

## Scope

This nit-fix addresses only the three MINOR findings from the operator NITS report:

1. `ARCHITECTURE.md` DB/trust invariant no longer says the client role can read everything and write nothing; it now states no direct table-write grants plus exactly the two auth-stamped entry RPCs.
2. `ARCHITECTURE.md` iOS invariant no longer says SELECT and nothing else as the DB fence; it now states the current app has zero mutation call sites, future writes must use the two server-stamped entry RPCs, and direct table writes remain denied.
3. `ARCHITECTURE.md` and `docs/MANUAL.md` Last-verified stamps no longer point at sibling commit `0aff135`; they point at reachable routed commit `35dc478`.

No SQL, DB tests, Swift, import code, real-data path, publication decision, push, lock action, cursor consume, paid API spend, pod spend, or production generation is included.

## Director verification already run

- `env -u GIT_INDEX_FILE git status --short --branch` from the evidence-ledger worktree -> `## codex/ledger-phase2-task21-pipeline-2026-07-08...origin/main [ahead 2]` and no dirty paths.
- `env -u GIT_INDEX_FILE git show --stat --oneline --name-status HEAD` -> `e446218 docs: fix Task 2.1 truth stamps`; modified only `ARCHITECTURE.md` and `docs/MANUAL.md`.
- `env -u GIT_INDEX_FILE git diff --stat 35dc478..HEAD` -> `ARCHITECTURE.md | 11 ++++++-----`, `docs/MANUAL.md | 2 +-`, `2 files changed, 7 insertions(+), 6 deletions(-)`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md docs/MANUAL.md DECISIONS.md` -> `All anchors checked — no drift.`
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` -> final `OK`; project smoke, ceremony, placeholder, and arch-freshness checks passed.
- `env -u GIT_INDEX_FILE git diff --check HEAD~1..HEAD` -> no output.
- `grep -rnE '\.(insert|update|delete|upsert|rpc)\(' ios/` -> exit 1, no matches.
- `rg -n "0aff135|client role can read|write nothing|nothing else" ARCHITECTURE.md docs/MANUAL.md DECISIONS.md docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md` -> exit 1, no matches.

Expected operator verdict: GO/NITS/FAIL on whether nit-fix commit `e446218` closes the three doc/stamp NITS from the prior report without widening scope.

## Exact Next Trigger

Operator re-reads evidence-ledger range `35dc478..e446218` and returns one Pipeline mailbox `verification-report` with GO/NITS/FAIL. Director must not push before operator GO.

Cursor at send: 0
