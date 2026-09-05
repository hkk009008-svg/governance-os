# Pipeline

Pipeline is a small local engineering harness for the Codex, Claude, and AGY
(Antigravity) desktop apps. They share a repository-scoped message transport,
work in normal Git worktrees, and use formal review only when the risk requires
it.

Pipeline does not launch model providers from the shell or turn one desktop app
into another app's child process. Shell commands are for Git, tests, preflight,
and deterministic repository tooling.

## Start

In a fresh primary checkout, install Python 3.11 or newer and the pinned test
dependencies once (linked worktrees reuse this environment):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.txt
```

Open this repository in any of the three apps. Their checked-in bindings use
the member labels `codex`, `claude`, and `agy`. In the app, call `team_status`,
read addressed messages with `team_wait`, and use `team_send` when another
member can help. A queued or acknowledged message is not permission, agreement,
or a formal verdict.

Check local readiness and repository health with:

```bash
bin/pipeline preflight
bin/pipeline status
bin/pipeline check --fast
bin/pipeline check
```

## Work

All three apps may reason, direct, implement, test, and challenge. Use their
strengths as routing hints, not job restrictions:

- Codex: sustained implementation, integration, tests, and parallel workspace work.
- Claude: large-context reasoning, architecture, independent review, and visual judgement.
- AGY: fast mapping and debugging, browser or artifact work, and premise/evasion challenges.

Prefer the smallest sufficient change. Run focused tests while editing, inspect
the exact diff, then run one proportionate final pass.

Most work needs no formal artifact. Material behavior changes need one
non-author Codex or Claude review of the exact committed range. Authority and
security controls additionally need a different model family and abuse-class
analysis. AGY may author, test, and challenge those changes, but does not issue
the formal GO/NITS/FAIL verdict.

Push, merge, release, paid spend, destructive actions, and live-data mutation
remain separate effects requiring exact current user authority.

## Main surfaces

- `AGENTS.md` — active operating contract.
- `ARCHITECTURE.md` — implemented components and trust boundaries.
- `OPERATIONS.md` — commands and troubleshooting.
- `docs/protocol/agents/risk-classes.md` — proportional review boundary.
- `pipeline/team*.py` — local app communication.
- `pipeline/compact_pair_loop.py` — exact-range formal review.
- `pipeline/ci_admission_gate.py` — authority-surface admission.

Executable code and current Git state outrank prose.
