# Ledger CLI Adoption Bridge — Claude Code

This bridge is for Claude Code sessions working on the registered
`evidence-ledger` target while Pipeline remains the governance
kernel. It is the Claude-native analog of
`docs/protocol/codex/ledger-cli-adoption.md` (which scopes itself to Codex
sessions and emits `.agents/...` paths — do not follow that copy from a
Claude seat).

Pipeline remains the four-seat governance kernel. Evidence-ledger remains the
product repo and owns product-local truth.

Use this bridge only when the user or parent prompt routes work to that target.

Canonical path: `docs/protocol/claude/ledger-cli-adoption.md`.

Do not start ledger work from the user Content checkout.
Ledger-routed Claude seats start from the current Pipeline checkout, then run

```bash
unset GIT_INDEX_FILE
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
coordination/bin/pipeline-python scripts/ledger_start_guard.py --seat <seat> --wave 2
```

before entering evidence-ledger. Claude seats read this bridge, not the Codex
copy. If guard output contains older adapter paths, the current Claude
continuation and `scripts/status.py` win.

Every `coordination/bin/pipeline-python` block opens with its own
`unset GIT_INDEX_FILE` line instead of prefixing the command with
`env -u GIT_INDEX_FILE`. The isolation is identical, but Claude's Bash tool
refuses `env` as soon as a dash-prefixed token follows the variable list — it
cannot verify what `env` wraps — so the prefixed form stops working the moment
a command grows an option, and this bridge's entire audience is Claude
sessions. The rule is uniform rather than conditional on whether a given
command currently takes options, because that condition changes without anyone
noticing. Ordinary Git keeps the `env -u GIT_INDEX_FILE` prefix, which is
verified to run.

## Authority Boundary

- Orientation mode: may inspect and report. It must not mutate evidence-ledger.
- Named live seat: may work on evidence-ledger only inside the explicit route.
- Coordinator: may reconcile ledger work from durable evidence but must not
  author behavior-changing product fixes.
- Subagent: receives only the parent prompt, allowed paths, acceptance
  evidence, forbidden side effects, and git hygiene. It does not inherit
  mailbox, cursor, GO, route, lock, push, or spend authority.

## Start From Pipeline

Orientation or named role:

```bash
unset GIT_INDEX_FILE
coordination/bin/pipeline-python scripts/status.py snapshot <seat>
```

Read relevant Pipeline mailbox bodies before protocol decisions. Counts alone
are not enough.

## Enter Evidence-Ledger

Inspecting the target repo before product edits takes two phases, in two
different working directories. Do not try to fuse them into one block.

Phase 1, in the Pipeline checkout — resolve and validate the target path:

```bash
unset GIT_INDEX_FILE
coordination/bin/pipeline-python scripts/target_binding.py --target evidence-ledger --print-path
```

Phase 2, in a separate Claude task rooted at the path Phase 1 printed — read
the target's state with plain commands:

```bash
unset GIT_INDEX_FILE
git status --short
git log --oneline -5
```

The phases are split because both fusions fail. `TARGET_ROOT="$(…)"` cannot run
from a Claude session isolated in a linked worktree, and neither can `git -C`
against another repository; both are refused by the Bash tool. That refusal is
correct rather than an obstacle — cross-repo work does not belong in a task
worktree — so the second phase gets its own task rooted in the target, where
the commands need no `-C` and no captured variable.

Read evidence-ledger `CLAUDE.md` (and `AGENTS.md`) before product edits. If
those files disagree with Pipeline, user instructions win first;
evidence-ledger controls product behavior, and Pipeline controls seat
mechanics.

## Cross-Repo Git Hygiene

- Prefix every ordinary cross-repo Git command with `env -u GIT_INDEX_FILE`.
  In Pipeline, run pytest only after `unset GIT_INDEX_FILE` and through
  `coordination/bin/pipeline-python -m pytest`; in the target-rooted task,
  follow that repository's own test command.
- Do not let a Pipeline seat index follow `cd` into evidence-ledger (the
  exported `GIT_INDEX_FILE` follows `cd` — 2026-07-07 it made
  evidence-ledger look object-corrupt).
- Do not stage or commit evidence-ledger files from a Pipeline seat index.
- Use explicit pathspecs for any parent-authorized staging or commit.
- Preserve unrelated evidence-ledger dirty work.

## Handoffs

Cross-repo handoffs record both repo heads. Collect each side's two lines in
the task rooted at that side — the Pipeline fields in the Pipeline checkout,
the evidence-ledger fields in the Phase 2 task rooted at the target — then
paste the outputs you already have into one body. Neither side needs
`TARGET_ROOT` or `git -C`, because each task is already standing in its own
repository:

```text
Pipeline HEAD: paste output from `env -u GIT_INDEX_FILE git log -1 --oneline`, run in Pipeline
Evidence-ledger HEAD: paste output from `git log -1 --oneline`, run in the target-rooted task
Pipeline status: paste output from `env -u GIT_INDEX_FILE git status --short`, run in Pipeline, or write `clean`
Evidence-ledger status: paste output from `git status --short`, run in the target-rooted task, or write `clean`
Seat: write one of `director`, `director2`, `operator`, `operator2`, or `coordinator`
Authority used: write one of `orientation report`, `live-seat route`, `operator verification`, or `coordinator reconciliation`
Evidence run: paste commands and results
Side effects not taken: push, lock, cursor consume, mailbox event, spend
Exact next trigger: paste the next prompt or seat event
```

Replace every field value with concrete command output or one of the listed
values before committing a real handoff. Do not commit this example body
as-is.

## Verification

Use current Pipeline protocol checks:

```bash
unset GIT_INDEX_FILE
coordination/bin/pipeline-python -m pytest tests -q
coordination/bin/pipeline-python scripts/governance_verify_all.py
```

Use evidence-ledger's own verification commands for product changes after
reading that repo's local docs.
