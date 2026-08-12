---
name: create-regression-pin
description: Author a strict-xfail regression pin for a confirmed-but-deferred defect (R-VERIFY-TIER B), with the three recurring traps — assertion-shape, lock-column, non-vacuous flip — as built-in checks. Use when an agent-confirmed code defect is being left unfixed this session.
disable-model-invocation: true
---

# Create a Regression Pin (strict-xfail)

The canonical body of this skill is `.agents/skills/create-regression-pin/SKILL.md`
(repo-relative). Read that file now and follow it exactly as if its content
were written here.

Claude-native deltas when executing it: prefix git and pytest with
`env -u GIT_INDEX_FILE`, and invoke Python as `.venv/bin/python`.
