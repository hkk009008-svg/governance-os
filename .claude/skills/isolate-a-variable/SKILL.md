---
name: isolate-a-variable
description: Find which difference actually causes a works-here-fails-there failure, before spending anything on a fix — enumerate every difference, calibrate the reads against a known-positive, and measure the matrix instead of patching the likeliest suspect. Use when a mechanism works in one setup and fails in another, when a metric reads zero, or when a documented precedent makes one suspect obvious.
disable-model-invocation: true
---

# Isolate a Variable

The canonical body of this skill is `.agents/skills/isolate-a-variable/SKILL.md`
(repo-relative). Read that file now and follow it exactly as if its content
were written here.

Claude-native deltas when executing it: prefix git and pytest with
`env -u GIT_INDEX_FILE`, invoke Python as `.venv/bin/python`, and build the
matrix as ONE run of an instrument that writes a citable `logs/` or report
artifact — a matrix assembled by eye across several sessions is the thing
this skill exists to replace.
