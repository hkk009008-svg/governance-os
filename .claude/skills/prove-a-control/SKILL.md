---
name: prove-a-control
description: Prove a guard, gate, or negative control actually holds before claiming it does — the two control kinds (reversion and evasion), the five ways a green control means nothing, and the evidence rules for citing it. Use when writing or reviewing any test whose value is that it would fail, any pre-dispatch or pre-spend gate, or any assertion described as "measured".
disable-model-invocation: true
---

# Prove a Control

The canonical body of this skill is `.agents/skills/prove-a-control/SKILL.md`
(repo-relative). Read that file now and follow it exactly as if its content
were written here.

Claude-native deltas when executing it: prefix git with `env -u GIT_INDEX_FILE`,
run Python and pytest as `coordination/bin/pipeline-python` after a preceding
`unset GIT_INDEX_FILE` line (not behind an `env -u` prefix, which Claude's Bash
tool refuses once the command takes options), and for any mutation-control run
add `PYTHONDONTWRITEBYTECODE=1` plus a `__pycache__` sweep, restoring mutated
files from a byte backup — never `git checkout --` over uncommitted work.
