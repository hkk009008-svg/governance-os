---
name: isolate-a-variable
description: Decide what to measure when a mechanism works in setup X and fails in setup Y — a trigger and threshold for batching candidate differences into one run instead of serializing guesses, the reads that make a matrix readable, and why a zero is a claim needing its own known-positive. Use on works-here-fails-there failures, on any measurement that reads zero or unchanged, and when a documented precedent makes one suspect obvious.
disable-model-invocation: true
---

# Isolate a Variable

The canonical body of this skill is `.agents/skills/isolate-a-variable/SKILL.md`
(repo-relative). Read that file now and follow it exactly as if its content
were written here. It carries the threshold that decides between one batched
matrix and one cheap direct test; do not assume either answer before reading
it.

Claude-native deltas when executing it: prefix git with `env -u GIT_INDEX_FILE`,
and run Python and pytest as `coordination/bin/pipeline-python` after a
preceding `unset GIT_INDEX_FILE` line — not behind an `env -u` prefix, which
Claude's Bash tool refuses once the command takes options. `bin/pipeline`
needs neither prefix; it clears the variable itself.
