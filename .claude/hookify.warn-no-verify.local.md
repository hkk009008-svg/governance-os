---
name: warn-no-verify
enabled: true
event: bash
action: warn
pattern: --no-verify|--no-gpg-sign
---

⚠️ **Skipping git hooks / signing (`--no-verify` / `--no-gpg-sign`)**

CLAUDE.md: never skip hooks or signing **unless the user explicitly asked**. A failing pre-commit hook means the commit **did not happen** — so fix the underlying issue rather than bypassing it, and never `--amend` after a hook failure (you'd modify the *previous* commit and risk losing work).

**Proceed only if** the user explicitly requested skipping. Otherwise, fix the hook failure and create a new commit.
