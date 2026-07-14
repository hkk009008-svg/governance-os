# Existing-session bridge repair

**Goal:** Make ChatGPT and Opus automatic only through the user's existing signed-in session, with a hard block instead of a fallback.

## Constraints

- Do not launch either provider while implementing or testing.
- Do not edit coordinator routes, packets, mailboxes, cursors, locks, or reviewed heads.
- Do not retry, substitute a provider, enter credentials, or use an API fallback.
- Local support is not live readiness. The coordinator must later clear the hold and run live acceptance.

## ChatGPT

- Default policy is `auto`.
- Automatic transport is the current runtime's in-app Browser (`iab`) only.
- If that transport is unavailable, signed out, challenged, or ambiguous, record failure and block.
- Do not fall back from `auto` to Chrome, manual relay, or an API.
- Keep the existing one-send/idempotency lifecycle and guarded response import.

Tests first:

- The default resolves to `auto`.
- The documented automatic order is `iab`, then block.
- Auto-failure instructions contain no manual-resume or Chrome fallback.

## Opus

- Keep the existing Claude CLI and receipt flow.
- Require transport profile `anthropic-claude-existing-session-v1`.
- Before process creation, reject API credentials, custom provider endpoints, OAuth-token overrides, and proxy overrides.
- Forward only the small environment needed to reuse the locally signed-in CLI session.
- Do not retry or switch transport when validation fails.

Tests first:

- A clean existing-session environment is accepted.
- Each forbidden override blocks before runner/process use.
- A missing or wrong transport profile blocks before runner/process use.

## Completion

- Run focused unit tests and repository smoke checks with no real provider.
- Commit the ChatGPT fix from `e2579f7` and the Opus fix from immutable parent `97c270f` on separate branches.
- Report both heads as locally verified, with live readiness still blocked on coordinator-owned acceptance.
