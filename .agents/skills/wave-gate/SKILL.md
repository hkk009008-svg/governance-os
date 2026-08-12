---
name: "wave-gate"
description: "Run the program-hardening wave gate and reconcile the remediation inventory \u2014 check whether a wave's defect rows are all closed + verified before declaring GATE MET. Use when gating a remediation wave or reconciling inventory status after absence."
---

# Wave Gate

Gates a remediation wave against `docs/REMEDIATION-INVENTORY.md`, the source of
truth for the hardening campaign.

Codex has no skill-level equivalent of Claude's `disable-model-invocation`;
use this as procedural guidance in the active session, not as a delegation
trigger for a separate model run.

## Run the gate
```
python scripts/wave_gate_check.py <wave>
```
The script reports whether every defect row assigned to `<wave>` is in a
closed + verified state. A non-zero exit = the wave is NOT met; read which rows
are still open.

## Reconcile before trusting the verdict
The gate reads the inventory; the inventory drifts. Before declaring a wave MET:
1. `git log --oneline -20` — confirm each row's cited fix
   SHA is actually on `origin/main` (git is the tiebreaker, not the doc).
2. For each row, confirm an operator **verification-report** GO exists (two
   independent seats confirming = convergence; a Rule #23 co-sign counts as
   one). A row marked done in the doc without a GO is NOT closed.
3. Confirm any strict-xfail pins for the wave's deferred rows are still
   `xfailed` (not silently XPASSing — a flipped pin means a row closed and the
   pin must be removed). See the `create-regression-pin` skill.

## Declaring GATE MET
- The wave closes on its PLANNED row count — do not let a wave grow
  indefinitely (no-infinite-wave discipline). New defects found mid-wave file
  into the NEXT wave unless explicitly escalated.
- Record the GATE-MET reconciliation commit. The coordinator owns inventory
  writes while live; in-lane seats do not author inventory status changes
  during an open wave.
- Surface the milestone: `git rev-list --count origin/main..HEAD` to confirm
  nothing MET is left unpushed.
- A gate closure is a checkpoint boundary: the owning seat publishes one
  checkpoint `findings` event (`scripts/draft_checkpoint.py`) whose
  `Lessons:` line carries candidate refs or `none-considered`.

## Notes
- `scripts/wave_gate_check.py` is the committed instrument (R-MEASURE); cite its
  output next to any GATE-MET claim.
- The coordinator is on-demand (spawned at multi-pair-wrap boundaries), never an
  in-lane fixer.
## Rule maintenance
Observed failure: GATE MET declared from inventory prose without GO
evidence, or a wave that grows past its planned row count.
Mode/risk: wave closeout. Cost: one `wave_gate_check.py` run plus SHA/GO
reconciliation. Owner: coordinator for inventory writes; the owning seat
for the checkpoint. Re-evaluate: if a MET wave still has open rows on
`origin/main`.
