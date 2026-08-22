# Evidence-ledger bridge for Codex

Use this bridge only when a user or parent task routes work from Pipeline to
the registered `evidence-ledger` target.

Pipeline remains the Codex four-seat governance kernel. Evidence-ledger remains
the product repository and owns product-local truth. Do not start ledger work
from the user Content checkout.

## Start

Use one compact Pipeline snapshot, then the ordinary target guard:

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
bin/pipeline status snapshot <role>
coordination/bin/pipeline-python pipeline/ledger_start_guard.py --seat <seat> --wave 2
```

`<seat>` and `<role>` are the same thing and the guard accepts exactly two
values, `author` and `reviewer` (`ledger_start_guard.py --help`). The six
pre-collapse seat names are rejected there.

The guard resolves the registered target and current committed route, validates
that startup began in Pipeline, and prints only the route-bound next evidence.
There is no fast-resume mode or second seat-status pass.

Read the route body and the target repository's `CLAUDE.md` and `AGENTS.md`
before product edits. If instructions disagree, user instructions win first;
evidence-ledger controls product behavior and Pipeline controls the protocol
boundary.

## Identity and scope

- Readiness bridge may inspect and report but does not mutate evidence-ledger.
- A named role works only inside the explicit route and allowed paths.
- Coordinator may reconcile ledger work from durable evidence but must not
  author behavior-changing product fixes.
- A subagent remains parent-scoped and inherits no role, mailbox, cursor,
  verdict, lock, push, or spending authority.

The target route may bind:

```text
Target worktree: /absolute/path
Accepted target HEAD: <full lowercase SHA>

## Target Allowed Paths
- relative/path
```

Historical field aliases remain parseable only for committed compatibility.
The guard rejects unsafe paths, conflicting routes, and divergent exact heads.

## Git and environment

Codex uses each caller-selected worktree's native Git index. The launcher strips
an inherited `GIT_INDEX_FILE`; do not create or share a Pipeline seat index.
Inspect the exact route worktree when one is named:

```bash
git -C /absolute/route/worktree status --short --branch
git -C /absolute/route/worktree log --oneline -5
```

Otherwise inspect the registered target checkout:

```bash
TARGET_ROOT="$(coordination/bin/pipeline-python pipeline/target_binding.py --target evidence-ledger --print-path)"
git -C "$TARGET_ROOT" status --short --branch
git -C "$TARGET_ROOT" log --oneline -5
```

Preserve unrelated dirty work and use explicit pathspecs for separately
authorized staging or commits. A normal checkout can be stale relative to a
route worktree; the exact route wins.

## Local services and external effects

Before a local Supabase lifecycle action, inspect the installed version and
actual container/service state. A partially running stack does not prove that a
generic start command will safely resume only missing services.

Starting, stopping, acquiring, reconfiguring, or cleaning services needs exact
authorization for the executor, target, action, and restoration scope. The
same separation applies to merge, cursor consumption, locks, peer invocation,
paid spend, and live-data mutation — the list in `AGENTS.md` item 6, which
deliberately excludes push. A route or successful guard does not authorize any
of them.

## Transfer and verification

Record both repository heads only when ownership or context actually transfers
across repositories. A routine local continuation does not require a handoff.

With the development environment activated, verify Pipeline protocol changes
using the smallest focused tests and one completion gate:

```bash
coordination/bin/pipeline-python -m pytest tests/unit/test_codex_ledger_bridge.py -q
bin/pipeline check
```

Use evidence-ledger's own verification commands for product changes. Formal
review follows the risk profile in `AGENTS.md`; a green guard or gate run is
evidence, not a reviewer verdict.
