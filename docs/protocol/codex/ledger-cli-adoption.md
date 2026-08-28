# Evidence-ledger bridge for Codex desktop

Use this adapter only when the current task routes work from Pipeline to the
registered `evidence-ledger` target. Pipeline owns the shared engineering and
review boundary; evidence-ledger owns product truth. Do not work on the user
Content checkout by mistake.

## Enter the target

Start with current state and resolve the registered checkout:

```bash
bin/pipeline status
bin/pipeline target --target evidence-ledger --print-path
```

If the task is bound to an existing committed Pipeline route, validate that
route before entering the target:

```bash
coordination/bin/pipeline-python pipeline/ledger_start_guard.py --seat <author|reviewer> --wave 2
```

The `--seat` spelling is a compatibility field for the route schema; it means
the temporary formal responsibility, not a standing app identity. Ordinary
direct target work does not invent a role or route. Read the selected route
body when one exists, then read evidence-ledger's `AGENTS.md` and `CLAUDE.md`.
User instructions win first, evidence-ledger controls product behavior, and
Pipeline controls the cross-repository review boundary.

## Work and scope

Codex remains member `codex` of the desktop team. A readiness helper may
inspect only. Any implementation stays inside the accepted target and allowed
paths. At a formal boundary, `author` owns the candidate and `reviewer` is a
non-author Codex or Claude member for that exact range. AGY may co-direct,
implement in isolation, and challenge evidence, but is not the sole formal
accepting verdict.

Use each worktree's native Git index. Preserve unrelated dirty work and stage
explicit pathspecs. When a route names a worktree, inspect that exact worktree;
the registered checkout may be stale:

```bash
git -C /absolute/route/worktree status --short --branch
git -C /absolute/route/worktree log --oneline -5
```

Otherwise run the same commands in the path printed by `bin/pipeline target`.
Subagents remain parent-scoped and inherit no task, review, push, merge,
release, spend, lock, or live-data authority.

## Effects, transfer, and verification

Starting or stopping local services, push, merge, release, lock acquisition,
paid spend, destructive operations, and live-data mutation each require exact
current authority for the executor, target, effect, and scope. A route, team
message, role label, or green guard does not supply it.

Record both repository heads only when ownership or context really transfers
across repositories. Routine continuation needs no handoff. Verify Pipeline
changes with focused tests and one proportionate completion gate; verify
evidence-ledger changes with that repository's own commands. Formal review
follows the current risk profile in `AGENTS.md` and always inspects the actual
committed range.
