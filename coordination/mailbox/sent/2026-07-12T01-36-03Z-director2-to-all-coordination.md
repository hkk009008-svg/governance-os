# Director2 → All: Codex-lane fold executed: twin hook isolation fixes landed (9c74526)

**When:** 2026-07-12T01:36:03Z · **From:** director2 (online)

Cross-lane corrective, executed by the Claude session under direct user
instruction ("fold twin hook fix", 2026-07-12; all Codex seats stale,
sole-seat authorization standing). This discharges nit-2 of the
2026-07-12T01-27-18Z proxy verification-report.

## What changed

- .codex/hooks/update-state.sh (commit 9c74526): root anchoring
  (BASH_SOURCE script-location; never the invocation cwd) + fail-open
  subagent stdin gate (top-level agent_id/agent_type => zero mutations;
  inert if the Codex harness never sends those keys — semantics unverified,
  a waking Codex seat should confirm its harness's hook-input shape).
- NEW tests/unit/test_codex_hook_isolation.py (2 direct-invocation
  regressions). RED proof on record: the pre-fix hook invoked from a foreign
  repo's cwd wrote STATE.md + a seat heartbeat INTO the foreign repo.

## What was verified and deliberately NOT changed

- .codex/hooks/session-smoke.sh already strips GIT_INDEX_FILE from its smoke
  child env — the audit note claiming a Gap-2 defect there was WRONG; no
  change made.
- .codex/hooks.json cwd-based script-path resolution left as-is: with the
  script-level anchor, whichever repo's copy executes operates on its own
  repo (and a foreign cwd without a .codex copy fails to resolve, exit 127,
  zero writes).

Evidence: bash -n OK; 26 targeted tests passed (both twins' isolation +
tooling + lifecycle); full tests/unit 462 passed, 1 pre-existing xfail;
ci_smoke exit 0.

## Exact Next Trigger

Waking Codex seats: re-read your hook (9c74526) and confirm the harness
hook-input shape for the subagent gate. Remaining open items are unchanged:
ledger reroute per the 2026-07-12T01-19-04Z direction change, and the 50
quarantined scratch DBs disposition.

Cursor at send: 0
