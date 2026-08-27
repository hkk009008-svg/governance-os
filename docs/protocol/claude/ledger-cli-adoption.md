# Evidence-ledger bridge for Claude desktop

Use this adapter only when the current task routes work from Pipeline to the
registered `evidence-ledger` target. Pipeline owns the shared engineering and
review boundary; evidence-ledger owns product truth. Do not work on the user
Content checkout by mistake.

## Enter the target

In the Pipeline task, inspect current state and resolve the target:

```bash
bin/pipeline status
bin/pipeline target --target evidence-ledger --print-path
```

If the task is bound to an existing committed Pipeline route, validate it
before entering the target:

```bash
coordination/bin/pipeline-python pipeline/ledger_start_guard.py --seat <author|reviewer> --wave 2
```

The `--seat` spelling is retained for route-schema compatibility; it denotes a
temporary formal responsibility, not a standing Claude identity. Ordinary
direct target work creates neither a role nor a route.

Open the printed target as its own Claude desktop task when the app will not
permit cross-repository commands from the Pipeline worktree. Read the selected
route body when one exists, then read evidence-ledger's `CLAUDE.md` and
`AGENTS.md`. User instructions win first, evidence-ledger controls product
behavior, and Pipeline controls the cross-repository review boundary.

## Work and scope

Claude remains member `claude` of the desktop team. A readiness helper may
inspect only. Implementation stays inside the accepted target and allowed
paths. At a formal boundary, `author` owns the candidate and `reviewer` is a
non-author Codex or Claude member for that exact range. AGY may co-direct,
implement in isolation, and challenge evidence, but is not the sole formal
accepting verdict.

Use each task worktree's native Git index. Preserve unrelated dirty work and
stage explicit pathspecs. If a committed route names another worktree, open or
inspect that exact path; the registered checkout may be stale. Subagents are
parent-scoped and inherit no task, review, push, merge, release, spend, lock,
or live-data authority.

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
