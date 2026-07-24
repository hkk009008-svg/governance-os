---
name: review-next
description: Resolves and reviews the next committed Pipeline verify-request addressed to the bound Cursor Operator app seat. Use when the user invokes /review-next in a pinned Operator worktree chat.
disable-model-invocation: true
---

# Review next

1. Read `docs/protocol/cursor/roles/operator.md`,
   `.agents/skills/seat-operator/SKILL.md`, and
   `.agents/skills/seat-operator/verification-report-format.md`.
2. Run `python3 scripts/cursor_mailbox.py next-review` from the current
   app-seat worktree. Do not ask the user for a prompt, event path, or SHA.
3. If no request is pending, report that fact and stop. Never consume a cursor
   merely to search.
4. Read the returned committed event and validate its exact base/head, author
   seat/model, assigned Operator, outcome, allowed paths, and finding refs.
   Refuse same-model or self-authored review.
5. Materialize the reviewed head with
   `python3 scripts/cursor_review_snapshot.py --repository <reviewed-repository>
   --head <reviewed-head> --output
   .pytest-verify-tmp/cursor-reviews/<reviewed-head>`. Use the current worktree
   as the repository when the request omits that field.
6. Inspect the base/head Git diff and run focused tests from that immutable
   scratch snapshot. Production edits, staging, and general index mutation are
   forbidden. Run repository-level gates (`scripts/ci_smoke.py`,
   `scripts/cursor_land_gate.py`) in this seat worktree, never inside the
   snapshot: the archive has no `.git` and only the head-commit mailbox
   corpus, so history-bound validators such as GO-SCHEMA report spurious
   violations there.
7. Draft one canonical GO/NITS/FAIL body under `.pytest-verify-tmp/`, disposition
   every finding ref, and show the verdict plus evidence.
8. Publish only after an explicit in-app approval through
   `coordination/bin/cursor-publish --to <director-seat> --kind verification-report
   --subject <subject> --body-file <scratch-file>`. Commit only the staged event
   path returned by the fixed writer, using `git commit --only -- <event-path>`.

The committed report is binding. Test output alone is not a verdict.
