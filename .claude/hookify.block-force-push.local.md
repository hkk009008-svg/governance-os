---
name: block-force-push
enabled: true
event: bash
action: block
pattern: git push.*(--force|\s-f\b)
---

🛑 **Blocked: force-push**

CLAUDE.md: **never force-push** (especially to main). In this shared-tree, two-seat workflow a force-push can overwrite the other seat's commits and rewrite published history — hard to undo and high blast radius.

**If you truly need this** (rare, and only with explicit user approval):
1. confirm the remote state with the user,
2. prefer `--force-with-lease` over `--force`,
3. temporarily set `enabled: false` in `.claude/hookify.block-force-push.local.md`, push, then re-enable.
