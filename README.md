# Governance OS

Pipeline is the governance kernel for a two-CLI AI coding protocol. It keeps
the minimum durable state needed to coordinate bounded work: mailbox events,
exact-range review, and separately authorized external effects.

It is **CLI-exclusive**. The only two participants are the `claude` CLI and
the `codex` CLI. Both read the same contract (`AGENTS.md`), both drive the
same command (`bin/pipeline`), and each reaches the other by running it once
as a child process. There is no desktop app, no MCP server, no persistent
agent peer, and no browser in any supported path.

This repository is not the private product application. evidence-ledger is the bound product target for ledger-routed work, while Pipeline keeps the
shared protocol machinery honest and executable.

## Quick Start

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
# First session in this checkout — every worktree needs its own venv:
test -d .venv || (python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt)

bin/pipeline --help      # every verb
bin/pipeline status      # where are we
bin/pipeline preflight   # can both peers run at all
```

Put `bin/` on `PATH` and it is just `pipeline <verb>`. The shim clears
`GIT_INDEX_FILE` and finds the primary checkout's interpreter itself, so a
governed command is one line with no prefix ceremony.

## How It Works

ARCHITECTURE.md records verified governance-kernel truth, and executable
code wins when prose drifts. Load-bearing runtime lives under `pipeline/`,
`coordination/`, `.agents/`, and the two CLI adapters (`.claude/`, `.codex/`).

- Roles publish durable events through `coordination/bin/send-event` into
  `coordination/mailbox/sent/`.
- Formal review is one committed Compact Pair (`pipeline review validate`) for
  an exact Git range. High-risk-control also needs a different model family and
  an abuse-class assessment.
- The two CLIs reach each other with `pipeline peer ask <side>`, which runs
  that CLI once and commits a receipt of what actually ran. The child's exit
  code is the delivery acknowledgement.
- AGY is available to both sides as an advisory subagent
  (`pipeline peer ask agy --role ...`). It is never a seat, reviewer, or
  verdict source.
- Long-horizon wrap, transfer, or interruption publishes a checkpoint
  `findings` event (`pipeline checkpoint` drafts to scratch only).
- Lessons route through `learning-candidate` events. Recalled memory and
  skill-use counts are advisory.

Work mode (`explore` / `validate` / `promote`) is orthogonal to review risk
and grants no authority. See `docs/protocol/work-modes.md`.

## Doc Map

| Need | Read |
|---|---|
| Agent contract (start here in a session) | [AGENTS.md](AGENTS.md) |
| How the two CLIs work as one unit | [docs/protocol/peer.md](docs/protocol/peer.md) |
| Comprehensive repository and process map | [docs/REPOSITORY-MANUAL.md](docs/REPOSITORY-MANUAL.md) |
| Task-oriented walkthrough of the common paths | [docs/GUIDEBOOK.md](docs/GUIDEBOOK.md) |
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
bin/pipeline check
coordination/bin/pipeline-python -m pytest tests -q
```

`pipeline check` is the completion-gate aggregate. CI measures the Python
growth budget across the whole pull-request range; reproduce that with
`NO_CEREMONY_BASE=$(git merge-base main HEAD) bin/pipeline check ceremony`.

## License

Proprietary. All rights reserved. Access to this private repository does not
grant a license.
