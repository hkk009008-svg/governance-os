# Daily Runbook — Governance OS

The one visible loop. Everything else is a pointer.

---

## The Loop

```
director brief  →  operator verify  →  GO / NITS / FAIL  →  push
```

1. **Director** scopes the smallest sufficient brief or fix and produces one
   lawful authority-bearing trigger.
2. **Operator** independently verifies only from that trigger (Lane V) and returns a
   verification-report mailbox artifact: GO, NITS, or FAIL.
3. **Director** acts on the verdict:
   - GO → push to origin (and only then).
   - NITS → nit-fix diff, then operator re-verifies.
   - FAIL → diagnose, re-implement, repeat.

Lane V trigger authority: a verify-request trigger is a canonical committed
sent-mailbox event strictly after the reviewed HEAD with exactly one
`Event type: verify-request`, one `Reviewed head: <40-lowercase-hex>`, one
`Reviewed base: <40-lowercase-hex>`, and one
`Lane-V-Scope: coordination/verification/scopes/<uuid>.json@sha256:<64-lowercase-hex>`
whose values agree with the committed descriptor and canonical
filename/envelope. A shipping trigger commit equals the reviewed HEAD, its
subject begins `feat`, `fix`, or `refactor`, and exactly one identical descriptor
reference in the terminal Git trailer block supplies its `Lane-V-Scope`.
Missing, duplicated, abbreviated, uppercase, misplaced, uncommitted, stale, or
mismatched authority is not a trigger: stop with a blocker, do not reconstruct
missing fields, and do not fall back to the other trigger kind.

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
