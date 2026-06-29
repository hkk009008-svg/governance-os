---
name: block-git-add-all
enabled: true
event: bash
action: block
pattern: git add\s+(-A|--all|\.)(\s|$)
---

🛑 **Blocked: bulk `git add` (`-A` / `.` / `--all`)**

This project requires **surgical, named-file staging** (operator handoff + CLAUDE.md git-safety). Bulk-adding risks:
- committing untracked artifacts like `logs/` (which must stay untracked),
- polluting a reviewer's clean `BASE_SHA..HEAD_SHA` range,
- in the shared two-seat tree, accidentally staging the other seat's in-flight work.

**Do instead:** stage by name — `git add path/to/file1 path/to/file2`.
If you genuinely need everything, list the files explicitly, or disable this rule (`enabled: false` in `.claude/hookify.block-git-add-all.local.md`).
