---
name: warn-pytest-without-venv
enabled: true
event: bash
action: warn
conditions:
  - field: command
    operator: regex_match
    pattern: (^pytest\b|python3?\s+-m\s+pytest)
  - field: command
    operator: not_contains
    pattern: .venv
---

⚠️ **pytest without the project venv (CLAUDE.md failure-mode #6)**

System `python3` lacks the project's test deps; the project venv has them. Use the explicit path:

`.venv/bin/python -m pytest tests/unit/ -q`

(Already inside an activated `.venv`? The explicit path is still the project convention and avoids ambiguity.)
