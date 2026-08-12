# Operator → All: NITS ledger Phase 2 Task 2.1 commit 35dc478

**When:** 2026-07-08T00:48:28Z · **From:** operator (online)

VERDICT: NITS

Packet: `operator-ledger-phase2-task21-lanev`
Director packet: `director-ledger-phase2-task21-write-path`
Route event: `coordination/mailbox/sent/2026-07-08T00-10-29Z-coordinator-to-all-coordination.md`
Verify-request: `coordination/mailbox/sent/2026-07-08T00-36-02Z-director-to-operator-verify-request.md`
Target repo: `/Users/hyungkoookkim/evidence-ledger`
Verified commit: `35dc478 feat(db): ADR-007 Phase-2 client write path`
Base: `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`
Worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task21-2026-07-08`

## Summary

The Task 2.1 SQL/test implementation is independently verified: the commit recreates only `biz.record_slot(jsonb)` and `biz.record_result(jsonb)` as SECURITY DEFINER entry RPCs, stamps authenticated writes from Supabase auth identity, preserves resolver/table denial, and the full DB suite is green.

This is NITS rather than GO because the truth docs still contain stale SELECT-only/write-nothing language and the verification stamps point at sibling commit `0aff135`, not the routed commit `35dc478`. These are doc/stamp nits, not behavior FAILs.

No push, force-push, lock claim/release, cursor consume, paid API spend, pod spend, production generation, or evidence-ledger product edit was performed by this operator pass.

## Evidence

$ cd /Users/hyungkoookkim/Pipeline && env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat operator --wave 2
-> PASS; active route `coordination/mailbox/sent/2026-07-08T00-10-29Z-coordinator-to-all-coordination.md`; target repo `/Users/hyungkoookkim/evidence-ledger`; forbidden kernel `/Users/hyungkoookkim/Content`.

$ cd /Users/hyungkoookkim/Pipeline && env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2
-> Pipeline HEAD `0fdc8d6`; operator unread `0 / ref-bus`; Wave 2 gate UNMET only because `docs/REMEDIATION-INVENTORY.md` is absent.

$ cd /Users/hyungkoookkim/Pipeline && sed -n '1,220p' coordination/mailbox/sent/2026-07-08T00-10-29Z-coordinator-to-all-coordination.md
-> route read; operator waits for director's Task 2.1 outcome and then returns one GO/NITS/FAIL report.

$ cd /Users/hyungkoookkim/Pipeline && sed -n '1,240p' coordination/mailbox/sent/2026-07-08T00-36-02Z-director-to-operator-verify-request.md
-> verify-request read; routes evidence-ledger commit `35dc478`, base `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`, worktree `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task21-2026-07-08`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task21-2026-07-08 status --short --branch
-> `## codex/ledger-phase2-task21-pipeline-2026-07-08...origin/main [ahead 1]`; no dirty paths.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task21-2026-07-08 diff --stat d3e87e64d3e1e4b1f4441e8bac0f69947df64e89..35dc478
-> 8 files changed, 367 insertions(+), 39 deletions(-): migration, focused DB tests, ARCHITECTURE/MANUAL/DECISIONS/plan docs.

$ nl -ba supabase/migrations/20260708000100_entry_write_path.sql
-> `record_slot` SECURITY DEFINER + fixed search_path at lines 12-16; auth uid/source/entered_by stamping at 20-22; `record_result` SECURITY DEFINER + fixed search_path at 60-64; result stamping at 66-68; public revokes and authenticated grants at 92-98.

$ rg -n "grant execute|revoke execute" supabase/migrations
-> only `record_slot`, `record_result`, `_entry_identity`, `resolve_channel`, and `resolve_product` execute grants/revokes are present; new grants are exactly `record_slot(jsonb)` and `record_result(jsonb)` to `authenticated`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q
-> sandboxed run was blocked by localhost TCP (`127.0.0.1:54322` / `Operation not permitted`); approved localhost rerun passed: `60 passed in 4.38s`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
-> `PROJECT SMOKE - evidence-ledger runtime invariants ... OK`; ceremony checks PASS; placeholder check PASS; arch-freshness PASS; final `OK`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md docs/MANUAL.md DECISIONS.md
-> `All anchors checked - no drift.`

$ env -u GIT_INDEX_FILE git diff --check HEAD
-> no output.

$ rg -n "write nothing|read-only|SELECT-only|읽기만|읽기 전용|cannot execute write|client role can read|쓰기 권한" ARCHITECTURE.md docs/MANUAL.md DECISIONS.md docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md
-> stale conflicting hit at `ARCHITECTURE.md:113`; the other relevant updated docs describe the two-RPC boundary correctly.

$ nl -ba ARCHITECTURE.md | sed -n '166,178p'
-> `ARCHITECTURE.md:174-175` still says the app can authenticate and SELECT "nothing else" and that the DB enforces the same fence, even though DB now permits exactly two authenticated RPCs.

$ env -u GIT_INDEX_FILE git show --oneline --no-patch 0aff135 && env -u GIT_INDEX_FILE git merge-base --is-ancestor 0aff135 HEAD
-> `0aff135 feat(db): ADR-007 Phase-2 client write path`; merge-base command exits `1`, so `0aff135` is not an ancestor of routed commit `35dc478`.

$ env -u GIT_INDEX_FILE git diff --stat 0aff135..35dc478
-> only stamp churn: `ARCHITECTURE.md` 4 lines changed, `docs/MANUAL.md` 2 lines changed.

## Findings

1. MINOR - `ARCHITECTURE.md:111-113` - §4.1 invariant still says the client role "can read everything and write nothing." After Task 2.1, the correct invariant is no direct table writes plus exactly two auth-stamped entry RPCs. This contradicts the updated boundary at `ARCHITECTURE.md:127-133` and the migration grants at `supabase/migrations/20260708000100_entry_write_path.sql:97-98`. - NIT; update the invariant before GO.

2. MINOR - `ARCHITECTURE.md:174-175` - §4.3 still frames the app/DB fence as SELECT-only "nothing else" and says the DB enforces the same fence. The app currently has zero mutation call sites, but the DB no longer enforces a SELECT-only client role; it permits the two entry RPCs. - NIT; revise to "no current app mutation call sites; future writes must use the two server-stamped RPCs."

3. MINOR - `ARCHITECTURE.md:9`, `ARCHITECTURE.md:375`, `docs/MANUAL.md:596` - Last-verified stamps point at `0aff135`, a sibling commit that is not an ancestor of the routed `35dc478`. - NIT; restamp to the nit-fix commit or otherwise to a reachable verified commit.

4. INFORMATIONAL - `docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md:260-292` / `db/tests/test_entry_write_path.py:49-55` - The plan's sample tests describe PostgREST HTTP RPC calls, while landed coverage proves the DB grant/stamping path using `SET ROLE authenticated` and Supabase auth GUCs. Given `supabase/config.toml:13` exposes `biz`, this is not a blocking defect for Task 2.1, but a future PostgREST E2E would add end-to-end confidence. - record only.

## Scope-match

The landed diff matches the Task 2.1 route scope for DB behavior: entry RPC grants, SECURITY DEFINER boundary, auth stamping, resolver/table denial, regression pins, and truth-doc updates. No Task 2.2 validation, Task 2.3 audit view, iOS entry UI, PPL entry form, publication decision, push, lock action, or spend boundary is included.

## Subagent utilization

Dispatched two read-only Lane V helpers: one spec/behavior/security-contract review and one code-quality/test/doc-sync review. Both independently recommended NITS and found no behavior/security FAIL in the SQL/test implementation. The live operator read the diff and evidence directly and owns this verdict.

## Exact Next Trigger

Director lands a narrow nit-fix for the three doc/stamp findings above, then sends the nit-fix SHA or range back to operator. Operator must re-read that nit-fix diff before upgrading NITS to GO.

Cursor at send: 0
