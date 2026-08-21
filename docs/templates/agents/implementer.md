# Implementer prompt template — agent-agnostic

> Relocated verbatim from `AGENTS.md` as part of the operative/provenance
> split (see `docs/protocol/migration-map-claudemd-split.md`). Loaded **at dispatch**,
> not at session start. Two-tree strategy: this is the `agents` copy.
> During the add-first window the root file still holds this content; it will be
> stubbed once this destination is confirmed.

---

## Git hygiene

- Use the selected task worktree's native Git index. Do not inherit or create a
  per-seat `GIT_INDEX_FILE`. Prefix every git invocation with
  `env -u GIT_INDEX_FILE ` — a dispatched agent cannot un-inherit the variable
  by intent, and an inherited value follows `cd` into unrelated repositories,
  where it presents as index corruption rather than as a wrong index.
- Never run state-changing git (add/commit/checkout/stash/restore/read-tree)
  without explicit instruction. Read-only git such as show, log, diff, grep,
  rev-parse, and ls-tree is allowed when relevant.
- For Lane V trigger authority, rely on the committed compact-pair verify-request
  (`pipeline/compact_pair_loop.py`) — there is
  no scope descriptor and no shipping trailer to emit; never invent trigger authority.

## Prompt template (for Lane B implementers)

The fresh instance has no memory of your session. Give it only the context
needed to act cold:

```
You are implementing Task <ID> from `<plan path>` (Slice <S>, sub-slice <ID>).
Working dir: `<absolute>`. Branch: `<branch>`. Latest commit: `<sha>`.

## Task Description (verbatim from plan §X.Y)

<paste exact plan text — code blocks, tables, prose intact>

## Critical Context

- <what shipped before that this builds on>
- <what's coming after that depends on this>
- <any plan-vs-source divergences already discovered>

## Where Exactly

- File path: <absolute path>
- Insertion point: <line ~N> after <existing landmark>
- Surrounding pattern to match: <existing convention>

## Project conventions you MUST follow

Per `AGENTS.md` (or `CLAUDE.md` if you're Claude Code):
1. Run impact analysis before editing existing symbols (grep callers + Read call sites)
2. Run scope check after edits — confirm only expected files changed
3. <task-specific gotcha>
4. **Brief-pattern reference adherence.** When the brief says "mirror pattern X at file:line" or "use the existing _foo_-style endpoint," verify the FULL shape of X — signature, route path, scope parameters, error handling, lock guards — not just the called function. Brief-pattern references are implicit specs; silent deviations cascade; brief-pattern references are runtime claims when they cite canonical sites: verify the named symbol exists at the cited SHA and verify the cited SHA exhibits the named sub-pattern. If the named helper doesn't exist or the wording is ambiguous, report the divergence in your status BEFORE implementing. (Broader codifier-side discipline: see Rule #12 — brief-level grep-the-writes — in `docs/PROTOCOL-RULES-LOG.md`.)
5. **Scoping check on new endpoints.** When adding/touching an HTTP endpoint operating on a tenant- or project-scoped resource, verify the route takes the scoping ID explicitly. Do NOT scan to find a matching resource by leaf ID alone — IDs can collide across tenants/projects depending on the ID-generation scheme. Inspect at least one similar existing endpoint in the same file to confirm the route shape and scoping. (Broader codifier-side discipline: see Rule #13 — symmetric-endpoint audit — in `docs/PROTOCOL-RULES-LOG.md`.)
6. **Pattern-doc uniformity pass.** When a brief cites a migration or pattern doc and says cumulative production sites cross 20 with per-site detail drift, include the requested pattern-doc uniformity pass or report why the doc class is exempt before editing.

## Verification

1. `<command>` — expected: <result>
2. `<command>` — expected: <result>

## Before You Begin

If you have questions about:
- <ambiguity 1>
- <ambiguity 2>

**Ask before implementing.**

## Your Job

1-7. <numbered steps>

## Report Format

- Status: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT
- Impact findings (callers, risk) or grep-fallback equivalent
- Files changed (paths only)
- Verification command output
- Pin selectors run — the exact pytest node-ids / `xfail-pin` column values you executed (so an independent reviewer can re-run them with `--runxfail` + a one-fact mutation non-vacuity check)
- Commit SHA — capture from `git log` AFTER post-commit hook activity settles, not from `git commit` stdout. If the project has a post-commit hook that amends another file (e.g., a state snapshot), the SHA from stdout may be stale by one.
- Self-review findings

## Reviewer Result Handling

- Use findings-first ordering by severity for review output and verification reports.
- When relaying reviewer or verifier output, preserve verdict, findings, and next steps.
- separate uncertainty, inference, and follow-up so readers can tell evidence from hypothesis.
- do not auto-fix after a review; route or request the next implementation action instead.
- failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.
```

A **bad** implementer prompt is "implement task A1" — the fresh instance
burns context discovering things you already know, and the report comes
back vague.

For spec and code-quality reviewer prompts, see
`docs/templates/agents/reviewer.md` (both prompt bodies live there) —
the structure transfers directly to non-Claude tools.

## Hardening notes — provenance for the implementer-template additions

Items 4-5 in "Project conventions you MUST follow" and the Commit SHA
capture guidance in "Report Format" are hardened in from cycle-5 +
cycle-6 failure modes. Carry them forward in future dispatches; if you
trim the template, do NOT trim these:

- **Item 4 (brief-pattern adherence)** — observed failure mode: a brief
  said "mirror the `_mutate_shot` pattern" but `_mutate_shot` didn't
  exist; the actual pattern used `mutate_project` with a pid-scoped
  route. Implementer correctly used `mutate_project` but missed the
  pid-scoping. Operator-seat's post-commit verification caught the
  divergence as a CRITICAL finding. Fix required a follow-up commit
  + route migration in callers.
- **Item 5 (scoping check)** — same root cause as item 4, codified as
  a standing convention so the next implementer catches the failure
  mode at design time, not via post-commit verification. Cost
  comparison: design-time check is ~1 grep; post-commit verification
  catch cost ~200k+ tokens + the fix commit's developer-time. Front-load
  is cheap.
- **Pattern-doc uniformity pass** — when a canonical migration/pattern doc
  accumulates enough sites to drift, the implementer must not only apply
  the current site change; it must also carry the documented uniformity
  pass if the brief says cumulative production sites cross 20 and per-site
  detail drift is present.
- **Commit SHA capture** — observed failure mode: implementer-reported
  SHAs sometimes 1 commit stale because a post-commit hook amends a
  state-snapshot file, changing HEAD after `git commit` returns. Capturing
  from `git log` after the hook settles is the reliable source.
