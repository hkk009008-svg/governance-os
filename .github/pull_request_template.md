## Summary
<!-- 1-3 sentences. What changed and why, in operator-friendly language. -->

## Why
<!-- Motivation. Link the governing issue, route, ADR, or handoff if applicable. -->

## Test plan
- [ ] `.venv/bin/python scripts/ci_smoke.py` passes locally
- [ ] `.venv/bin/python -m pytest tests/unit/ -q` clean (current governance baseline: **234 passed / 0 failed**)
- [ ] CI (`.github/workflows/ci.yml`) is green on this PR
- [ ] ARCHITECTURE.md updated if a documented governance or protocol subsystem was touched
- [ ] [DECISIONS.md](../DECISIONS.md) appended (new ADR) if this is an architectural decision

## Priority / Route (if applicable)
Name the governing mailbox route, handoff, ADR, or task-board packet.

- [ ] **P0** — Ship-blocking risk (test coverage, CI, cost-tracking)
- [ ] **P1** — Quality risk (observability, orchestrator size, schema validation, frontend resilience)
- [ ] **P2** — Cost / efficiency (LLM cost default, pod billing, cascade visibility)
- [ ] **P3** — Code health (concurrency hygiene, dead code, deduplication)
- [ ] **P4** — Strategic / open (vendor sprawl, multi-user, review fatigue, experiment tracking, console mode)
- [ ] N/A — Routine fix / cleanup / refactor not tied to a P-priority

## Verification output
<!--
Per CLAUDE.md / AGENTS.md "Verification discipline" (Rule 3): if this PR
makes inventory-shaped claims (counts, file presence, LOC, etc.), paste the
producing command + output here. Authority-voice claims without verifying
output get pushed back.
-->

```
$ <command>
<output>
```

## Out of scope
<!-- Anything noticed but deliberately not addressed. -->
