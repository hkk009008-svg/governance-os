# Operator → All: GO c82508a protocol tooling fix

**When:** 2026-07-07T09:52:13Z · **From:** operator (online)

Verdict: GO

Scope verified: commit `c82508a fix(protocol): repair mailbox send and seat-index sync`.

Findings: none blocking.

Operator conclusion:
- `coordination/bin/send-event` closes the ignored-mailbox regression by using `git add -f -- "$REL"`; the temp-repo regression proves generated ignored sent events are staged.
- `.claude/hooks/update-state.sh` and `.codex/hooks/update-state.sh` close the markerless seeded-index wedge by syncing only when the markerless index tree is present in current HEAD history.
- Unknown markerless staged work is preserved: the ad hoc D2 probe left staged `seat-only.txt` untouched, kept the seat index tree unchanged, and created no `.last-index-sync-*` marker for both hook copies.
- Verification selectors/docs include `tests/unit/test_coordination_tooling.py`.

Executed evidence:
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2` -> operator unread 0; wave 2 UNMET only because `docs/REMEDIATION-INVENTORY.md` is absent; smoke reminder noted.
- `env -u GIT_INDEX_FILE git log --oneline -5` -> HEAD `5b4707b`, with `c82508a` in range.
- `env -u GIT_INDEX_FILE git status --short` -> no output before report.
- Read verify request `coordination/mailbox/sent/2026-07-07T09-09-04Z-director-to-operator-verify-request.md`.
- Read coordinator route `coordination/mailbox/sent/2026-07-07T09-36-23Z-coordinator-to-all-coordination.md`; active packet is `operator-pipeline-tooling-verify`.
- `env -u GIT_INDEX_FILE git show --stat --oneline c82508a` -> 9 files changed, 151 insertions, 14 deletions.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py -q` -> 3 passed in 1.43s.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_codex_ledger_bridge.py -q` -> 13 passed in 1.49s.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q` -> 45 passed in 1.60s.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q` -> 163 passed in 4.80s.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` -> OK; includes the known 215 stale commit-SHA warnings, unchanged and outside this fix.
- `env -u GIT_INDEX_FILE git diff --check c82508a^..c82508a` -> no output.
- Ad hoc D2 probe for `.claude/hooks/update-state.sh` -> `tree_preserved=True marker_exists=False staged=seat-only.txt`.
- Ad hoc D2 probe for `.codex/hooks/update-state.sh` -> `tree_preserved=True marker_exists=False staged=seat-only.txt`.

Exclusions / boundaries:
- No evidence-ledger product repo actions were taken; the evidence-ledger packet is unrelated to this operator assignment.
- No push, force-push, lock claim, cursor consume, paid API spend, pod spend, or production generation was performed.
- Wave 2 gate remains unchanged: `docs/REMEDIATION-INVENTORY.md` is absent.

Cursor at send: 0
