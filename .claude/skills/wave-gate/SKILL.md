---
name: wave-gate
description: Run the program-hardening wave gate and reconcile the remediation inventory — check whether a wave's defect rows are all closed + verified before declaring GATE MET. Use when gating a remediation wave or reconciling inventory status after absence.
disable-model-invocation: true
---

# Wave Gate

Protocol SEMANTICS are canonical in `.agents/skills/wave-gate/SKILL.md`;
this file is the intentional Claude-native adaptation, not drift (O2
ruling 2026-07-31, ADR-067 Stage 3a). Where the two disagree on protocol
semantics, the `.agents` side wins and this file is corrected in the same
change.

Gates a remediation wave against `docs/REMEDIATION-INVENTORY.md`, the source of
truth for the hardening campaign.

**Read this first: the inventory currently holds zero data rows.** Every wave
therefore reports `UNMET ... wave has no inventory rows`. Until a real defect
row is accepted into a wave, there is nothing here to gate.

## Run the gate
```
unset GIT_INDEX_FILE
coordination/bin/pipeline-python pipeline/wave_gate_check.py <wave>
```
`<wave>` is an integer. The script reports whether every defect row assigned to
that wave is in a closed + verified state. A non-zero exit = the wave is NOT
met; read which rows are still open.

## Reconcile before trusting the verdict
The gate reads the inventory; the inventory drifts. Before declaring a wave MET:
1. `env -u GIT_INDEX_FILE git log --oneline -20` — confirm each row's cited fix
   SHA is actually on `origin/main` (git is the tiebreaker, not the doc).
2. For each row, confirm a **verification-report** GO from the assigned
   `reviewer` exists (a historical row may cite an `operator`/`operator2` GO;
   those events still parse and still count). A row marked done in the doc
   without a GO is NOT closed.
3. Confirm any strict-xfail pins for the wave's deferred rows are still
   `xfailed` (not silently XPASSing — a flipped pin means a row closed and the
   pin must be removed). See the `create-regression-pin` skill.

## Declaring GATE MET
- The wave closes on its PLANNED row count — do not let a wave grow
  indefinitely (no-infinite-wave discipline). New defects found mid-wave file
  into the NEXT wave unless explicitly escalated.
- Record the GATE-MET reconciliation commit. The inventory still describes
  itself as coordinator-owned; that position is retired, so the `author` that
  owns the wave writes the row and the `reviewer` confirms it.
- Surface the milestone: `env -u GIT_INDEX_FILE git rev-list --count
  origin/main..HEAD` to confirm nothing MET is left unmerged upstream.
- A gate closure is a checkpoint boundary: the owning role publishes one
  checkpoint `findings` event (draft it with `bin/pipeline checkpoint`) whose
  `Lessons:` line carries candidate refs or `none-considered`.

## Notes
- `pipeline/wave_gate_check.py` is the committed instrument (R-MEASURE); cite its
  output next to any GATE-MET claim.
- The gate is evidence, never authority. It cannot see whether a GO was
  independent, only whether the inventory says one exists.
