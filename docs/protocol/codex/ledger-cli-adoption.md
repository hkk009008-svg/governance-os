# Ledger CLI Adoption Bridge

This bridge is for Codex CLI sessions working on
`/Users/hyungkoookkim/evidence-ledger` while Pipeline remains the governance
kernel.

Pipeline remains the Codex four-seat governance kernel. Evidence-ledger remains
the product repo and owns product-local truth.

Use this bridge only when the user or parent prompt routes work to
`/Users/hyungkoookkim/evidence-ledger`.

Canonical path: `docs/protocol/codex/ledger-cli-adoption.md`.

## Authority Boundary

- Readiness bridge: may inspect and report. It must not mutate evidence-ledger.
- Named live seat: may work on evidence-ledger only inside the explicit route.
- Coordinator: Coordinator may reconcile ledger work from durable evidence but must not author behavior-changing product fixes.
- Subagent: receives only the parent prompt, allowed paths, acceptance evidence,
  forbidden side effects, and git hygiene. It does not inherit mailbox, cursor,
  GO, route, lock, push, or spend authority.

## Start From Pipeline

Readiness bridge:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
```

Named live seat:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Coordinator:

```bash
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Read relevant Pipeline mailbox bodies before protocol decisions. Counts alone
are not enough.

## Enter Evidence-Ledger

Before product edits, inspect the target repo from a clean command environment:

```bash
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger log --oneline -5
```

Read evidence-ledger CLAUDE.md and AGENTS.md before product edits. If those
files disagree with Pipeline, user instructions win first; evidence-ledger
controls product behavior, and Pipeline controls Codex seat mechanics.

## Cross-Repo Git Hygiene

- Prefix every ordinary cross-repo git and pytest command with `env -u GIT_INDEX_FILE`.
- Do not let a Pipeline seat index follow `cd` into evidence-ledger.
- Do not stage or commit evidence-ledger files from a Pipeline seat index.
- Use explicit pathspecs for any parent-authorized staging or commit.
- Preserve unrelated evidence-ledger dirty work.

## Handoffs

Cross-repo handoffs record both repo heads.

Use this minimum body when active work spans both repos:

```text
Pipeline HEAD: paste output from `env -u GIT_INDEX_FILE git log -1 --oneline`
Evidence-ledger HEAD: paste output from `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger log -1 --oneline`
Pipeline status: paste output from `env -u GIT_INDEX_FILE git status --short`, or write `clean`
Evidence-ledger status: paste output from `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short`, or write `clean`
Seat: write one of `director`, `director2`, `operator`, `operator2`, or `coordinator`
Authority used: write one of `readiness report`, `live-seat route`, `operator verification`, or `coordinator reconciliation`
Evidence run: paste commands and results
Side effects not taken: push, lock, cursor consume, mailbox event, spend
Exact next trigger: paste the next prompt or seat event
```

Replace every field value with concrete command output or one of the listed
values before committing a real handoff. Do not commit this example body as-is.

## Verification

Use current Pipeline protocol checks:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Use evidence-ledger's own verification commands for product changes after
reading that repo's local docs.
