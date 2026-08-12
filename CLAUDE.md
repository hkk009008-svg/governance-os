@AGENTS.md

# Claude Desktop additions

- Use the Code tab and let Desktop create an isolated worktree for each
  independent writing session.
- Use native attributed session messaging only for transient Claude-to-Claude
  coordination. It is not a channel to Codex.
- Use a side chat for a disposable question that should not steer the main
  session.
- For a Codex-authored branch or pull request, invoke `/cross-app-review` and
  stay read-only unless the user asks you to implement fixes.
- Prefer the visual diff, browser preview, file editor, and integrated terminal.
  Do not add instructions for a separate terminal product.
