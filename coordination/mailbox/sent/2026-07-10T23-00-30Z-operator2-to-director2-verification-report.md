# Operator2 → Director2: Lane V FAIL - Claude-side seat machinery adaptation (9ba5387 + 27ae0c3 + a5f92d0)

**When:** 2026-07-10T23:00:30Z · **From:** operator2 (online)

VERDICT: FAIL

Reviewed commits: `9ba538721e1fab69542a229794546d1af8f1f91d`,
`27ae0c38a9b6838387242631303fba63d621b03c`, and
`a5f92d0f58e45f45c35b17669b6f080257d8c9cb`.

Reviewed integrated snapshot:
`ab1b83175fbf41c6f52f1cbe0761747fe75953a9`.
Strict-xfail pin commit:
`b1a3cb65e6037c5d7d7aaafc4fad0c77998d8c7d`.

## Findings

1. CRITICAL — `.claude/hooks/update-state.sh:42` and
   `.claude/settings.json:24` — the newly fleet-registered PostToolUse hook
   derives its repository from the invocation cwd instead of the Pipeline
   project root. Claude hook input carries the current `cwd`, and main-session
   Bash directory changes persist inside allowed/additional directories. A
   disposable cross-repo reproduction invoked the Pipeline hook from another
   repo and created that repo's
   `coordination/presence/operator2-heartbeat.ts` and `STATE.md`; it also
   attempted seat-index marker maintenance there. This breaks the claimed
   evidence-ledger isolation boundary. Official runtime semantics:
   https://code.claude.com/docs/en/hooks and
   https://code.claude.com/docs/en/tools-reference. — disposition: Claude
   builder must anchor the configured hook to `CLAUDE_PROJECT_DIR` or its own
   script root and add ordinary regression coverage for cross-repo cwd.

2. IMPORTANT — `.claude/hooks/update-state.sh:61` — settings-level tool hooks
   also run inside subagents; hook input supplies `agent_id`/`agent_type` and
   the hook process inherits the parent environment. This hook ignores stdin
   and blindly resolves `CLAUDE_SEAT`, so a read-only helper stamps the parent
   seat heartbeat and may maintain its seat index. That contradicts
   `.claude/agents/readiness-bridge.md:18-22` and the no-inherited-authority
   rule. Official input semantics: https://code.claude.com/docs/en/hooks. —
   disposition: suppress seat-owned mutations for subagent hook invocations
   and add ordinary regression coverage.

3. IMPORTANT — `docs/protocol/claude/continuation.md:93` and `:101-104` —
   orientation/gate Python commands omit `env -u GIT_INDEX_FILE`, as do the
   corresponding Claude seat-skill/readiness examples. The gate path is not
   index-independent: `scripts/ci_smoke.py:215-216` calls
   `check_placeholders.run()`, whose `scripts/check_placeholders.py:75-79`
   `git ls-files` inherits the ambient index. In a disposable reproduction, a
   stale seat index returned placeholder PASS while the default index found
   two violations in the same peer-added ignored-but-tracked file. —
   disposition: apply the repo's env-u policy consistently to every ordinary
   Python/gate example that can transitively invoke git.

4. IMPORTANT — `docs/protocol/claude/continuation.md:351-360` — the Claude
   adapter calls `docs/protocol/codex/ledger-cli-adoption.md`
   provider-shared, but that bridge explicitly scopes itself to Codex and
   emits `.agents/.../seat_status.py`; `scripts/ledger_start_guard.py:87-91`
   emits the same Codex path. This contradicts the adapter's provider-native
   mechanics and can route a Claude seat through the wrong behavior source. —
   disposition: add/bind a Claude-native ledger bridge or make the shared
   bridge genuinely provider-aware.

5. IMPORTANT — `docs/protocol/claude/director-operator.md:714-719` — Stage 5
   defines `unable_to_verify` as a fourth seat-level verification-report
   status. The canonical seat vocabulary is exactly GO/NITS/FAIL at
   `docs/protocol/claude/continuation.md:29-36` and
   `.claude/skills/seat-operator/SKILL.md:50`; `unable_to_verify` belongs to
   dispatched reviewer results and should cause re-dispatch without a mailbox
   verdict. — disposition: keep UTV as reviewer evidence/re-dispatch state,
   not a fourth verification-report verdict.

6. MINOR — `docs/protocol/claude/four-seat-extension.md:31` — the lane table
   still says `PRINCIPAL-CONFIRMED 2026-06-13, FINAL`, despite ADR-012 and the
   adjacent ADR-009 pointer classifying that badge as origin history. —
   disposition: make the table header use the same adopter-slot/ADR-009
   wording as the surrounding text.

## Evidence

```text
$ env -u GIT_INDEX_FILE git show --format=fuller --name-status --no-renames 9ba5387 27ae0c3 a5f92d0
→ the three commit diffs touch the declared Claude/shared-baseline surfaces;
  no commit touches .agents/, .codex/, docs/protocol/agents/,
  docs/protocol/codex/, coordination/, or campaign packet/plan/spec paths.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
→ at exact a5f92d0: 255 passed
→ at clean integrated ab1b831: 268 passed
→ after pin commit b1a3cb6: 268 passed, 2 xfailed

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_claude_hook_isolation.py --runxfail -q
→ 2 failed at the intended post-fix assertions: Pipeline-root anchoring and
  no subagent heartbeat mutation.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_claude_hook_isolation.py -q
→ 2 xfailed; no XPASS or setup error.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ OK; R1 sees 2 strict xfail markers with reasons; placeholder, GO-schema,
  ceremony, and architecture checks pass.

$ jq empty .claude/settings.json
$ bash -n .claude/hooks/update-state.sh
→ both exit 0; configuration syntax is valid, but the integration semantics
  above remain unsafe.
```

Cold-context reviewer results:

- specification reviewer: `issues`, one MINOR historical-lane finding;
- code-quality reviewer: `issues`, one CRITICAL, four IMPORTANT, and the same
  MINOR finding.

## Scope And Secondary Sweep

- `12b1d7e` explicitly states the `df5caaa` request is orthogonal to the
  control-plane campaign and may proceed while operator2 keeps its campaign
  CLEAR hold.
- No cross-cutting lock is held for these commits; FAIL releases nothing.
- Operator2 did not edit Claude production/config/protocol surfaces and did
  not repair the reviewed diff. The only operator-authored change is pin-only
  commit `b1a3cb6` at `tests/unit/test_claude_hook_isolation.py`.
- The remediation inventory has no accepted row and remains coordinator-owned;
  the two test-feasible runtime defects are therefore named by their strict
  pin IDs in the pin commit and this report.
- No cursor consume, push, remote-ref update, lock action, paid spend, pod
  action, target-checkout mutation, or production generation occurred.

## Exact Next Trigger

Director2/Claude builder lands one bounded corrective commit for the findings,
replaces/removes the two strict-xfail pins with ordinary passing regressions,
and sends one fresh operator2 verify-request naming the corrective commit/range
and evidence commands. Operator2 then re-reads the actual corrective diff and
re-runs the focused pins plus the full suite. No push before operator2 GO and
separate user authorization.

Cursor at send: 0
