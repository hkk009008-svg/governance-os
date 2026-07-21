# FoulPlay Cursor Adoption Bridge

This bridge is for **Cursor** sessions building
`/Users/hyungkoookkim/FoulPlay` while Pipeline remains the governance kernel.

Pipeline remains the four-seat governance OS. FoulPlay remains the product
repo and owns product-local truth (Godot project, sims, scenes, game tests).

Use this bridge when the user routes Cursor work to FoulPlay. Do not treat it
as a replacement for the Codex/Claude evidence-ledger bridges; those keep
serving ledger-routed seats.

Canonical path: `docs/protocol/cursor/foulplay-adoption.md`.

Do not start product work from `/Users/hyungkoookkim/Content`.

## Authority Boundary

- Readiness / orientation: may inspect Pipeline and FoulPlay and report. It
  must not mutate mailbox, cursors, locks, or push.
- Named live seat: may work on FoulPlay only inside an explicit route that
  names foulplay keywords or the FoulPlay path.
- Coordinator: may reconcile from durable evidence but must not author
  behavior-changing FoulPlay fixes.
- Cursor without an explicit seat name stays readiness-bridge / local-builder
  unless the user names a seat or protocol decision.

## Select The FoulPlay Target

evidence-ledger stays the ADR-013 registry default. Cursor sessions must
select FoulPlay explicitly:

```bash
cd /Users/hyungkoookkim/Pipeline
export GOVERNANCE_TARGET=foulplay
env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py \
  --seat <seat> --wave 2 --target foulplay
```

Or one-shot without exporting:

```bash
env -u GIT_INDEX_FILE GOVERNANCE_TARGET=foulplay \
  .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2 --target foulplay
```

## Start From Pipeline, Then Enter FoulPlay

Orientation (no seat):

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE GOVERNANCE_TARGET=foulplay \
  .venv/bin/python scripts/target_binding.py --check
```

Before product edits, inspect FoulPlay:

```bash
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/FoulPlay status --short --branch
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/FoulPlay log --oneline -5
```

Read FoulPlay `AGENTS.md` and the active design/plan under
`docs/superpowers/` before editing game code. If Pipeline and FoulPlay
disagree: user instructions win first; FoulPlay owns product behavior;
Pipeline owns seat/mailbox mechanics.

## Cross-Repo Git Hygiene

- Prefix ordinary cross-repo git commands with `env -u GIT_INDEX_FILE`.
- Do not let a Pipeline seat index follow `cd` into FoulPlay.
- Do not stage or commit FoulPlay files from a Pipeline seat index.
- Use explicit pathspecs; preserve unrelated dirty work in either tree.
- Record both heads in any cross-repo handoff.

## Adopted OS Workflow (Cursor-local)

Cursor adopts these Pipeline OS habits without copying the full protocol tree
into FoulPlay:

1. Durable shared state beats chat memory (git, mailbox, plans, tests).
2. Smallest sufficient verification; tests prove only what they execute.
3. Push, merge, lock, mailbox publish, and paid spend are separately
   user-authorized.
4. Behavior-changing acceptance still needs distinct non-author review when a
   live seat / compact-pair path is in force; ordinary local game iteration
   without a named seat does not invent mailbox GO.
5. Before editing a symbol, find definition, writers, callers, and siblings.

## Product Pointers

| Need | Source |
|---|---|
| Game vision / combat design | `FoulPlay/docs/superpowers/specs/2026-07-21-foul-play-design.md` |
| Roadmap | `FoulPlay/docs/superpowers/plans/ROADMAP.md` |
| Controls / builds | `FoulPlay/README.md` |
| Engine project | `FoulPlay/project.godot` |
