# Codex Markdown Behavior Compaction Design

**Date:** 2026-07-17
**Status:** Approved; Codex Markdown lane implemented, Claude contract alignment pending

## Goal

Make Codex behavior guidance simple, compact, flexible, and effective without
weakening authority or side-effect safeguards. Claude owns concurrent
implementation and any non-Markdown contract/test changes.

## Scope

Edit only these Codex behavior surfaces:

- `AGENTS.md`
- `docs/protocol/codex/continuation.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-operator/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`

Do not edit Python, TOML, tests, Claude or three-way surfaces, shared protocol
doctrine, mailbox state, historical evidence, templates, artifact formats, or
target-specific adapters such as `docs/protocol/codex/ledger-cli-adoption.md`.

## Structure

Use one rule: **one owner, one pointer, one local consequence**.

- `AGENTS.md` is the thin always-loaded router: risk tier, default
  readiness-bridge mode, authority precedence, and links.
- `continuation.md` is the Codex runtime adapter: modes, startup commands,
  Git hygiene, Codex-native tool mapping, and canonical pointers.
- `four-seat-protocol/SKILL.md` is the triggered orientation checklist: choose
  mode, inspect durable state, respect mailbox/cursor boundaries, then load the
  concrete seat skill.
- Each seat skill contains only that seat's triggers, responsibilities,
  permitted outputs, and prohibitions.

Copied lifecycle, emergency, disagreement, capacity, reviewer-result,
side-effect-token, and pair-contract explanations are replaced by canonical
pointers plus only the consequence needed at the current surface.

## Safeguards retained

- User instructions remain highest authority.
- Durable Git and relevant mailbox bodies beat chat summaries and counts.
- A subagent never inherits seat, cursor, mailbox, GO, lock, push, or spend
  authority.
- Only a non-author operator issues GO/NITS/FAIL from repository evidence.
- A coordinator routes and reconciles but does not author behavior-changing
  production fixes.
- Push, merge, paid spend, and other external effects remain separately gated.
- Ordinary Git and pytest commands retain `env -u GIT_INDEX_FILE`.
- Live-seat work retains same-seat handoff, mailbox, capacity, and hot-tree
  checks when their trigger actually fires.

## Ceremony removed

- No mandatory subagent-utilization report or recorded no-op decision.
- No status, handoff, route, receipt, or verification artifact unless it
  changes ownership, carries authority, preserves a real transfer, reports a
  verdict, or records an actual blocker.
- No duplicate review of the same unchanged commit for the same question.
- No live-seat startup, mailbox, worktree, TDD, or completion ceremony for
  conversational and read-only tasks unless their own trigger fires.
- No new framework, generator, schema, hook, or documentation layer.

Use a bounded subagent only when it adds independent signal or genuinely
parallel capacity; otherwise work directly without explaining the non-use.

## Compatibility boundary

Existing prompt-sync tests deliberately pin duplicated wording across these
surfaces. This Markdown pass follows the approved semantic compaction even if
those literal duplication assertions become stale. Claude owns any aligned
test or executable-model update; Codex will not broaden into those files.

Before every write and final comparison, refresh `HEAD` and the working tree so
concurrent Claude changes are preserved. If a scoped file changes concurrently,
reconcile its current content instead of overwriting it.

## Acceptance

- Only the six scoped Markdown files change, apart from this design note.
- Each scoped file has one clear responsibility and remains usable when loaded
  directly.
- The retained safeguards above remain explicit or have an unambiguous
  canonical pointer and local consequence.
- Repeated doctrine is removed rather than paraphrased into new duplicates.
- Markdown links, placeholders, and whitespace validate.
- Focused prompt-sync failures, if any, are classified as obsolete duplication
  pins versus genuine lost safeguards and reported for Claude ownership.
