# Governance OS

Pipeline is the governance kernel for a multi-seat AI coding protocol. It
coordinates director, operator, director2, operator2, and coordinator work with
mailbox artifacts, capacity packets, smoke gates, and Codex/Claude/Antigravity
adoption docs.

This repository is not the private product application. `evidence-ledger` is
the bound product target for the current ledger-routed work, while Pipeline
keeps the shared protocol machinery honest and executable.

## Quick Start

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py
```

For ledger-routed live seats, start from Pipeline and use the guard:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2
```

## How It Works

ARCHITECTURE.md records verified governance-kernel truth. The load-bearing
runtime is a set of committed Python and shell tools under `scripts/`,
`coordination/`, `threeway/`, `.agents/`, and `.codex/`. Seats exchange durable
mailbox events in `coordination/mailbox/sent/`; capacity packets under
`coordination/capacity/packets/` define active routed work; smoke and protocol
doctor commands prove that the kernel is still internally consistent.

## Doc Map

| Need | Read |
|---|---|
| Verified code and topology facts | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Operating commands and troubleshooting | [OPERATIONS.md](OPERATIONS.md) |
| User-principal intent for this kernel | [docs/PROGRAM-MANUAL.md](docs/PROGRAM-MANUAL.md) |
| Decision history | [DECISIONS.md](DECISIONS.md) |
| Codex ledger bridge | [docs/protocol/codex/ledger-cli-adoption.md](docs/protocol/codex/ledger-cli-adoption.md) |
| Protocol assembly map | [docs/protocol/protocol-assembly-map.md](docs/protocol/protocol-assembly-map.md) |

## Verification

Use `env -u GIT_INDEX_FILE` for ordinary git and Python commands so seat-local
indexes do not leak into shared checks.

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
```

Smoke may warn about baselined stale commit-SHA references. That means SHA
provenance is not clean; it does not mean the warning has been fixed.

## License

MIT - see [LICENSE](LICENSE).
