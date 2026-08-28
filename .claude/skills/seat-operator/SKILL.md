---
name: seat-operator
description: Use when Claude is explicitly assigned the temporary independent reviewer responsibility for an exact committed range and GO, NITS, or FAIL.
---

# Claude temporary reviewer adapter

Read and follow `.agents/skills/seat-operator/SKILL.md` completely after the
Claude `four-seat-protocol` adapter. This is a task-local responsibility;
`operator` is only the legacy filename.

Use Claude Desktop's independent context and visual diff to inspect the actual
range, not the author's summary. Ask questions through the team MCP tools, but
return the formal verdict only through the bound review interface. Stay
read-only for the range. Claude may review a high-risk control only when its
family differs from the author model; AGY advice cannot substitute for the
accepting reviewer role.
