# Daily Runbook — Governance OS

The one visible loop. Everything else is a pointer.

---

## The Loop

```
director brief  →  operator verify  →  GO / NITS / FAIL  →  push
```

1. **Director** scopes the smallest sufficient brief or fix and commits it.
2. **Operator** independently verifies the named commit (Lane V) and returns a
   verification-report mailbox artifact: GO, NITS, or FAIL.
3. **Director** acts on the verdict:
   - GO → push to origin (and only then).
   - NITS → nit-fix diff, then operator re-verifies.
   - FAIL → diagnose, re-implement, repeat.

---

## Four state facts (one line each)

- **Baton passes are mailbox artifacts, not chat** (Rule #19).
- **First commit to land wins** — always run `git log --oneline -3` + check
  mailbox before writing a commit or gate decision (R-HOT-TREE).
- **No push before GO** (R-VERIFY-THEN-PUSH).
- **docs / status / handoff-only commits skip Lane V** (phase detection).

---

## Less-common paths → see these files (trigger → reference)

| Trigger | See |
|---|---|
| Uncertainty about any Rule #7–#23 | `docs/protocol/agents/director-operator.md` |
| Cross-cutting change needs a co-sign (Tier A/B?) | `docs/protocol/agents/four-seat-extension.md` + `docs/protocol/codex/continuation.md` |
| Acquiring / releasing a cross-cutting lock | `docs/protocol/agents/four-seat-extension.md` |
| Wave gate, wave sequence, or inventory audit | `.agents/skills/seat-coordinator/SKILL.md` + `docs/protocol/codex/continuation.md` |
| Emergency / escalation / rollback | `docs/protocol/agents/failure-modes.md` |
| Git sharp edges (phantom index, pathspec, env flags) | `docs/protocol/agents/core.md` |
| Measurement behind a GO/NO-GO verdict | `docs/protocol/agents/core.md` (R-MEASURE) |
| Coordinator seat spawn criteria | `.agents/skills/seat-coordinator/SKILL.md` |
