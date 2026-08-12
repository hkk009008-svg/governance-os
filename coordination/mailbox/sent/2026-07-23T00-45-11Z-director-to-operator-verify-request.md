# Director → Operator: review Codex seat-index startup hardening

**When:** 2026-07-23T00:45:11Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: ee3e27d61e95becdd1ace4ed396d216c253567e3
Reviewed base: d66e56297d0b35714f784370f8ba3ed66f2acb25
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: codex-seat-index-startup-hardening-2026-07-23
Task ID: codex-seat-index-startup-hardening-2026-07-23
Coordinator route: coordination/mailbox/sent/2026-07-23T00-39-27Z-coordinator-to-director-coordination.md@d66e56297d0b35714f784370f8ba3ed66f2acb25
Immutable parent: 1c84d5b6e1e6c164a7174907d057193b7fd5daaa
Implementation commit: ee3e27d61e95becdd1ace4ed396d216c253567e3
Reviewed tree: f776b2d335f6ef79f418a36194cc21824bb9706b
Path count: 2
Path manifest SHA-256: 96d92914380852d8c9ac7062e9f8a767d7f4571350e2220911b2a3269af50a37
Patch SHA-256: 348e80ae8a9ab63a97d558d75cc9e7a76ceb4e34fd12f5f6ca8e9e68d7424fb1

## Outcome

Independently review the immutable one-commit actual range `d66e56297d0b35714f784370f8ba3ed66f2acb25..ee3e27d61e95becdd1ace4ed396d216c253567e3`. Require the Codex seat launcher to fail closed before exec when an existing per-seat index cannot be parsed or cannot support a read-only Git status because referenced Git objects are unavailable, and when an existing index has no tracked entries while non-empty HEAD does. Require every existing index byte to remain untouched, including legitimate seat-local staged work. Missing-index seeding from HEAD and dry-run behavior must remain unchanged.

## Abuse-Class Dispositions

- path-exists-only bypass: CLOSED by parsing existing index entries and running read-only status validation before exec.
- missing-object or foreign-index state: CLOSED by nonzero Git validation becoming a LaunchError with the underlying diagnostic.
- empty-index mass-deletion view: CLOSED by comparing zero index entries with tracked HEAD entries and refusing launch.
- staged-work destruction: CLOSED by fail-closed diagnostics only; no quarantine, read-tree, reset, unlink, rename, or write is performed for an existing index.
- ambient-index confusion: CLOSED by constructing the validation environment without ambient GIT_INDEX_FILE and then binding only the exact seat index.
- optional index refresh: CLOSED by `git --no-optional-locks status`; validation does not acquire the optional refresh lock.
- missing-index regression: CLOSED by retaining the existing one-time `read-tree --index-output=<seat-index> HEAD` seed path.

## Target Allowed Paths

- scripts/codex_seat_launcher.py
- tests/unit/test_codex_seat_launcher.py

## Director Verification Evidence

- Strict RED: the unreadable-index and empty-index selectors failed 2/2 before production edits because no LaunchError was raised.
- Focused GREEN: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_codex_seat_launcher.py` passed 18/18.
- A read-only two-repository foreign-index probe made `git --no-optional-locks status` return 128 with a missing-object diagnostic while `ls-files --stage` alone returned zero, confirming the status probe covers the reported unreadable-object class.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` ended OK.
- `env -u GIT_INDEX_FILE git diff --check` and exact-range `git diff --check d66e56297d0b35714f784370f8ba3ed66f2acb25..ee3e27d61e95becdd1ace4ed396d216c253567e3` were silent.
- The actual range contains exactly one commit and the two allowed paths. Unrelated AGY, Cursor, Superpowers-policy, protocol-model, smoke, docs, prompt-sync, model-matrix, runtime-index, and shared-tree WIP remained unmodified and unstaged by this commit.

## Operator Verification

- Parse this request at its actual trigger commit and require exact Pipeline repository/base/head/tree, one-commit range, two-path manifest and hashes, Director/gpt-5.6-sol author identity, Operator/gpt-5.6-terra assignment, and ordered finding refs.
- Inspect both changed files and the full actual diff. Confirm validation happens before exec, every existing index remains byte-preserved, missing-index seeding remains one-time, dry-run still has no index or provider effect, and the launcher emits a fail-closed diagnostic without automatic reset or quarantine.
- Run `env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_codex_seat_launcher.py`.
- Run `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`.
- Run `env -u GIT_INDEX_FILE git diff --check d66e56297d0b35714f784370f8ba3ed66f2acb25..ee3e27d61e95becdd1ace4ed396d216c253567e3`.
- Adversarially exercise a syntactically readable index whose cached entries reference unavailable objects, an obviously empty index against non-empty HEAD, and a valid index with staged changes. Issue GO only if every required boundary is preserved without an unresolved hard finding; otherwise issue NITS or FAIL with immutable evidence.

Adversarial question: can a corrupt, foreign, missing-object, or obviously empty existing seat index reach Codex exec as healthy; can validation rewrite or replace staged seat-local state; can ambient GIT_INDEX_FILE redirect validation; or can the new checks break missing-index seeding or dry-run isolation? GO requires every answer to be no.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T00-39-27Z-coordinator-to-director-coordination.md@d66e56297d0b35714f784370f8ba3ed66f2acb25

## Boundaries

This request authorizes only the assigned non-author Operator on gpt-5.6-terra to inspect the immutable Pipeline range, run the listed local synthetic checks and bounded temporary-index probes, and publish exactly one canonical committed GO, NITS, or FAIL. It authorizes no implementation or repair, provider launch, runtime-index mutation, model-matrix change, unrelated WIP mutation, dependency acquisition, push, merge, cursor consumption, cleanup, history rewrite, or other external effect. A later GO grants none of those actions.

Cursor at send: 0
