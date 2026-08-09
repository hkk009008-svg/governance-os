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
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2
```

before entering evidence-ledger. Claude seats read this bridge, not the Codex
copy. If guard output contains older adapter paths, the current Claude
continuation and `scripts/status.py` win.

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
env -u GIT_INDEX_FILE .venv/bin/python scripts/status.py snapshot <seat>
```

Read relevant Pipeline mailbox bodies before protocol decisions. Counts alone
are not enough.

## Enter Evidence-Ledger

Before product edits, inspect the target repo from a clean command
environment:

```bash
TARGET_ROOT="$(env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --target evidence-ledger --print-path)"
env -u GIT_INDEX_FILE git -C "$TARGET_ROOT" status --short
env -u GIT_INDEX_FILE git -C "$TARGET_ROOT" log --oneline -5
```

Read evidence-ledger `CLAUDE.md` (and `AGENTS.md`) before product edits. If
those files disagree with Pipeline, user instructions win first;
evidence-ledger controls product behavior, and Pipeline controls seat
mechanics.

## Cross-Repo Git Hygiene

- Prefix every ordinary cross-repo git and pytest command with
  `env -u GIT_INDEX_FILE`.
- Do not let a Pipeline seat index follow `cd` into evidence-ledger (the
  exported `GIT_INDEX_FILE` follows `cd` — 2026-07-07 it made
  evidence-ledger look object-corrupt).
- Do not stage or commit evidence-ledger files from a Pipeline seat index.
- Use explicit pathspecs for any parent-authorized staging or commit.
- Preserve unrelated evidence-ledger dirty work.

## Handoffs

Cross-repo handoffs record both repo heads. Use this minimum body when active
work spans both repos. Resolve `TARGET_ROOT` with `target_binding.py` as shown
above before collecting these fields:

```text
Pipeline HEAD: paste output from `env -u GIT_INDEX_FILE git log -1 --oneline`
Evidence-ledger HEAD: paste output from `env -u GIT_INDEX_FILE git -C "$TARGET_ROOT" log -1 --oneline`
Pipeline status: paste output from `env -u GIT_INDEX_FILE git status --short`, or write `clean`
Evidence-ledger status: paste output from `env -u GIT_INDEX_FILE git -C "$TARGET_ROOT" status --short`, or write `clean`
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
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/governance_verify_all.py
```

Use evidence-ledger's own verification commands for product changes after
reading that repo's local docs.
