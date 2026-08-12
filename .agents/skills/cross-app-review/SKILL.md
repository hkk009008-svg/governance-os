---
name: cross-app-review
description: Review an exact branch, commit, pull request, or working-tree diff produced in the other desktop app. Use for a focused Claude-to-Codex or Codex-to-Claude handoff without taking implementation ownership.
---

# Cross-app review

1. Establish the exact target: pull request, branch and base, commit range, or
   working-tree diff. Do not review a vague moving target.
2. Stay read-only unless the user explicitly asks you to implement fixes.
3. Inspect the actual diff and enough surrounding code to evaluate behavior,
   regressions, security, and missing tests.
4. Run the smallest relevant checks when useful. State clearly what did and did
   not run.
5. Report prioritized, actionable findings. Give each finding a severity,
   file/line, technical reason, and concise fix direction.
6. Do not invent findings to justify the handoff. If none remain, say so and
   name any residual risk or untested area.
7. Return the review in the current app. Publish GitHub comments only when the
   user asks for that external write.
