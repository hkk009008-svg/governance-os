# Pipeline

Pipeline is a small local engineering harness for the Codex, Claude, and AGY
(Antigravity) desktop apps. They share one repository-scoped message
transport, work in normal Git worktrees, and use formal review only when the
risk class requires it. Shell commands are for Git, tests, preflight, and
deterministic repository tooling, never for launching a model.

## Start

In a fresh primary checkout, install Python 3.11 or newer and the pinned test
dependencies once (linked worktrees reuse this environment):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.txt
```

Open the repository in any of the three apps; their checked-in bindings use
the member labels `codex`, `claude`, and `agy`. Then:

```bash
bin/pipeline orient --member <label>
bin/pipeline check --fast
```

## Surfaces

- `AGENTS.md`: the operating contract for every member.
- `ARCHITECTURE.md`: components and trust boundaries.
- `OPERATIONS.md`: commands, the formal review procedure, troubleshooting.
- `DECISIONS.md`: the decisions that still shape the harness.
- `docs/protocol/agents/risk-classes.md`: when formal review is required.
- `docs/plans/`: analyses and improvement plans.
- `pipeline/`: the executable harness; `tests/`: its regression suite.

Executable code and current Git state outrank prose.
