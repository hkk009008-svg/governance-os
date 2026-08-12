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
env -u GIT_INDEX_FILE .venv/bin/python scripts/chatgpt_pro_consult.py reserve --repo-root .
```

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/chatgpt_pro_consult.py finish --repo-root . --key KEY --hash SHA256 --status sent
```
