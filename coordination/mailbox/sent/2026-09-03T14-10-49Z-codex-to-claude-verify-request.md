# Codex → Claude: Review AGY 3.8 and harness-friction upgrades

**When:** 2026-09-03T14:10:49Z · **From:** codex (online)

Event type: verify-request
Reviewed base: b48ca82d6b1e9813755dfbc1b0165dbc075d8fca
Reviewed head: 5001eca726f18619370840ab085d71863c5c7cbd
Author model: gpt-5.6-sol
Risk class: high-risk-control

## Outcome

Independently review the exact candidate range. Confirm Gemini 3.8 High is the sole active Gemini author model without losing historical family parsing; linked worktrees reuse only their canonical repository registration while exact tool schemas remain mandatory; admission output is compact by default but complete under --verbose and never hides blockers; and review-request help accurately exposes its required stdin input.

## Abuse Class Assessment

- Retired Gemini aliases or nested harness/provider prefixes must not regain active-author status.
- Existing admitted history must remain admitted after Gemini 3.8 becomes the sole active Gemini author model.
- A linked worktree may inherit only its own Git common-directory primary registration, never an unrelated repository registration.
- Tampered, missing, extra, or permission-unsafe AGY tool-cache files must remain rejected after timestamp freshness is removed.
- Compact admission output must still expose active FAILs and uncovered authority commits; verbose mode must retain every skipped-report path.
- The AGY plugin config, MCP handshake, and request composer must retain exact validation behavior.

Cursor at send: cursorless
