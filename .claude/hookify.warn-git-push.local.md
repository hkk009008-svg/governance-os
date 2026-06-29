---
name: warn-git-push
enabled: true
event: bash
action: warn
pattern: git push
---

⚠️ **`git push` — push is user-gated in this project**

Pushing to origin is a shared-state action that needs **explicit user authorization** by default (operator/director protocol; the push gate re-arms after each use).

**Confirm before pushing:** has the user authorized *this* push? If not, pause and ask. If yes, proceed.
