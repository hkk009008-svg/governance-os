---
name: writing-skills
description: "Author, revise, or promote a repository skill from observed procedure — evaluation-first (three scenarios before the body), description-as-trigger, stub-vs-adaptation (O2), reduced-context probe before landing, and compact-pair promotion. Use when writing a new skill, changing a canonical SKILL.md, closing a skill TODO, or promoting a procedure candidate into .agents/skills/."
disable-model-invocation: true
---

# Writing skills

The canonical body of this skill is `.agents/skills/writing-skills/SKILL.md`
(repo-relative). Read that file now and follow it exactly as if its content
were written here.

Claude-native deltas when executing it: prefix git with `env -u GIT_INDEX_FILE`,
and run Python and pytest as `coordination/bin/pipeline-python` after a
preceding `unset GIT_INDEX_FILE` line — not behind an `env -u` prefix, which
Claude's Bash tool refuses once the command takes options.
