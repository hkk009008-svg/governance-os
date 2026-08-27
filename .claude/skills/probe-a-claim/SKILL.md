---
name: probe-a-claim
description: Formation-time discipline for load-bearing claims — derive the premises from the claim's shape, cite each with the command that measured it, attack only the claim sentence with a native reduced-context desktop subagent, and record the blank cells. Use BEFORE writing "verified", "enforced", "complete", "never", "measured", or citing a reference as provenance; prove-a-control is for the mechanism, this is for the belief.
disable-model-invocation: true
---

# Probe a Claim

The canonical body of this skill is `.agents/skills/probe-a-claim/SKILL.md`
(repo-relative). Read that file now and follow it exactly as if its content
were written here.

Claude-native deltas when executing it: prefix git with `env -u GIT_INDEX_FILE`,
run Python and pytest as `coordination/bin/pipeline-python` after a preceding
`unset GIT_INDEX_FILE` line (not behind an `env -u` prefix, which Claude's Bash
tool refuses once the command takes options). `bin/pipeline probe` prints a
prompt and launches nothing; give only that prompt to Claude's native
`amnesiac-prober` agent, and label the same-family instruction-isolated read as
weaker than independent review.
