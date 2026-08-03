# Governance OS

Pipeline is the governance kernel for a multi-seat AI coding protocol. It
coordinates director, operator, director2, operator2, and coordinator work with
durable task events, exact-range review gates, and
Codex/Claude/Antigravity/Cursor adoption docs.

This repository is not the private product application. `evidence-ledger` is
the bound product target for the current ledger-routed work, while Pipeline
keeps the shared protocol machinery honest and executable.

## Quick Start

Activate a Python environment satisfying `requirements-dev.txt`, then:

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
python scripts/status.py snapshot
```

For ledger-routed governed work, additionally use the Pipeline guard:

```bash
python scripts/ledger_start_guard.py --seat director --wave 2
```

## How It Works

ARCHITECTURE.md records verified governance-kernel truth. The load-bearing
runtime is a set of committed Python and shell tools under `scripts/`,
`coordination/`, `threeway/`, `.agents/`, and `.codex/`. Seats exchange durable
mailbox events in `coordination/mailbox/sent/`; one effective task/route defines
current governed work. Capacity packets are optional campaign diagnostics.
Smoke and protocol-doctor commands test the kernel at the completion gate.

## Doc Map

| Need | Read |
|---|---|
| Verified code and topology facts | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Operating commands and troubleshooting | [OPERATIONS.md](OPERATIONS.md) |
| User-principal intent for this kernel | [docs/PROGRAM-MANUAL.md](docs/PROGRAM-MANUAL.md) |
| Decision history | [DECISIONS.md](DECISIONS.md) |
| Codex ledger bridge | [docs/protocol/codex/ledger-cli-adoption.md](docs/protocol/codex/ledger-cli-adoption.md) |
| Cursor Desktop app seats | [docs/protocol/cursor/continuation.md](docs/protocol/cursor/continuation.md) |
| Cursor seat roles | [docs/protocol/cursor/roles/](docs/protocol/cursor/roles/) |
| Protocol assembly map | [docs/protocol/protocol-assembly-map.md](docs/protocol/protocol-assembly-map.md) |

## Verification

Run mutating Codex work in a task-specific native Git worktree. Use the
checkout's ordinary Git index.

```bash
python -m pytest tests/unit -q
python scripts/ci_smoke.py
```

Smoke stays quiet for the reviewed historical commit-SHA baseline. Run
`python scripts/check_doc_claims.py --sha-refs`
when you need the full SHA-reference audit report.

## License

Proprietary. All rights reserved. Access to this private repository does not
grant a license.
