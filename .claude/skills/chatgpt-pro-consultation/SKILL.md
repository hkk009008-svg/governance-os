---
name: chatgpt-pro-consultation
description: Use for one optional parent-owned ChatGPT Pro consultation through the signed-in Claude in-app Browser when the user explicitly asks or a material reasoning trigger applies.
---

# ChatGPT Pro consultation

The canonical body of this skill is
`.agents/skills/chatgpt-pro-consultation/SKILL.md` (repo-relative). Read that
file now and follow it exactly as if its content were written here.

Claude-native deltas when executing it: drive the page with the in-app
Browser tools (`mcp__Claude_Browser__*`) as the canonical body's Claude
mapping says, and run the reserve/finish commands from the repository root
as:

```bash
unset GIT_INDEX_FILE
coordination/bin/pipeline-python scripts/chatgpt_pro_consult.py reserve --repo-root .
```

```bash
unset GIT_INDEX_FILE
coordination/bin/pipeline-python scripts/chatgpt_pro_consult.py finish --repo-root . --key KEY --hash SHA256 --status sent
```

Both take options, so they `unset GIT_INDEX_FILE` rather than prefix
`env -u GIT_INDEX_FILE`: Claude's Bash tool refuses `env` once a dash-prefixed
token follows the variable list, which would leave these unrunnable from the
session that is supposed to run them.
