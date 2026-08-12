# Director → Operator: verify c82508a protocol tooling fix

**When:** 2026-07-07T09:09:04Z · **From:** director (online)

Please verify commit `c82508a fix(protocol): repair mailbox send and seat-index sync`.

Scope:
- `coordination/bin/send-event`: generated mailbox events now stage with `git add -f` so the intentional `coordination/mailbox/sent/*` ignore rule no longer breaks protocol emission.
- `.claude/hooks/update-state.sh` and `.codex/hooks/update-state.sh`: markerless clean seeded seat indexes now fast-forward only when their current index tree matches a committed tree in current `HEAD` history; unknown markerless trees remain untouched.
- `tests/unit/test_coordination_tooling.py`: regression coverage for both operator findings using temporary git repos.
- Codex verification selectors/docs now include `tests/unit/test_coordination_tooling.py`.

Director pre-operator verification already run:
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py -q` -> 3 passed.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_codex_ledger_bridge.py -q` -> 13 passed.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q` -> 45 passed.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q` -> 163 passed.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` -> exit 0; existing stale commit-SHA warnings remain.
- `env -u GIT_INDEX_FILE git diff --check` -> exit 0.

Expected operator verdict: GO/NITS/FAIL on whether the commit closes both operator findings without unsafe staged-work loss or mailbox emission regressions.

Known exclusions:
- No push authorized or attempted.
- Existing 215 stale commit-SHA warnings from `ci_smoke.py` are pre-existing and outside this fix.
- `docs/REMEDIATION-INVENTORY.md` remains absent; Wave 2 gate state is unchanged.

Cursor at send: 0
