# Governance OS

Pipeline is the governance kernel for a multi-provider AI coding protocol.
It keeps the minimum durable state needed to coordinate bounded work: mailbox
events, exact-range review, and separately authorized external effects.
Codex and Claude share one policy
(`scripts/codex_protocol_model.py`) and differ only in runtime mechanics.

This repository is not the private product application. `evidence-ledger` is
the bound product target for the current ledger-routed work, while Pipeline
keeps the shared protocol machinery honest and executable.

The standing pair is director plus operator. Director2, operator2, and
coordinator are cold capacity, not standing chats. Ordinary reversible local
work needs no seat, mailbox event, or formal review.

## Quick Start

Use the repo venv and the checkout's ordinary Git index:

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
# First session in this checkout — every worktree needs its own venv:
test -d .venv || (python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt)
env -u GIT_INDEX_FILE .venv/bin/python scripts/status.py snapshot
```

For ledger-routed governed work, additionally use the Pipeline guard:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2
```

## How It Works

ARCHITECTURE.md records verified governance-kernel truth. Executable code
wins when prose drifts. Load-bearing runtime lives under `scripts/`,
`coordination/`, `.agents/`, and the provider adapters (`.claude/`,
`.codex/`).

- Seats publish durable events through `coordination/bin/send-event` into
  `coordination/mailbox/sent/`.
- Formal review is one committed Compact Pair
  (`scripts/compact_pair_loop.py`) for an exact Git range. High-risk-control
  also needs a different model family and an abuse-class assessment.
- Long-horizon wrap, transfer, or interruption publishes a checkpoint
  `findings` event. `scripts/draft_checkpoint.py` drafts to scratch only.
- Lessons route through `learning-candidate` events. Recalled memory and
  skill-use counts are advisory: they grant no authority and do not write
  canonical skills.
- `threeway/` is a dormant signed-bus substrate. The live transport is the
  mailbox (`governance.toml`).

Work mode (`explore` / `validate` / `promote`) is orthogonal to review risk
and grants no authority. See `docs/protocol/work-modes.md`.

## Doc Map

| Need | Read |
|---|---|
| Agent contract (start here in a session) | [AGENTS.md](AGENTS.md) |
| Comprehensive repository and process map | [docs/REPOSITORY-MANUAL.md](docs/REPOSITORY-MANUAL.md) |
| Task-oriented walkthrough of the common paths | [docs/GUIDEBOOK.md](docs/GUIDEBOOK.md) |
| Supported desktop apps: setup, strengths, and communication | [docs/protocol/app-quickstart.md](docs/protocol/app-quickstart.md) |
| Direct Codex/Claude transient task connector | [docs/protocol/claude/task-connector.md](docs/protocol/claude/task-connector.md) |
| Verified code and topology facts | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Operating commands and troubleshooting | [OPERATIONS.md](OPERATIONS.md) |
| User-principal intent for this kernel | [docs/PROGRAM-MANUAL.md](docs/PROGRAM-MANUAL.md) |
| Decision history | [DECISIONS.md](DECISIONS.md) |
| Work modes | [docs/protocol/work-modes.md](docs/protocol/work-modes.md) |
| Learning plane (advisory memory and skills) | [docs/protocol/learning/contract.md](docs/protocol/learning/contract.md) |
| Codex ledger bridge | [docs/protocol/codex/ledger-cli-adoption.md](docs/protocol/codex/ledger-cli-adoption.md) |
| Protocol assembly map | [docs/protocol/protocol-assembly-map.md](docs/protocol/protocol-assembly-map.md) |

## Verification

Use a native Git worktree and that checkout's ordinary Git index. Do not
export a persistent `GIT_INDEX_FILE`.

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/governance_verify_all.py
```

`governance_verify_all.py` is the completion-gate aggregate (the old
`ci_smoke.py` name is a deprecated alias). Smoke stays quiet for the
reviewed historical commit-SHA baseline. Run
`python scripts/check_doc_claims.py --sha-refs`
when you need the full SHA-reference audit report.

## License

Proprietary. All rights reserved. Access to this private repository does not
grant a license.
