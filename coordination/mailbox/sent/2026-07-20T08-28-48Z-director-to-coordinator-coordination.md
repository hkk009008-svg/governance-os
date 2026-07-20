# Director → Coordinator: owner-center Task 3 blocked by third generated-bundle assumption

**When:** 2026-07-20T08:28:48Z · **From:** director (online)

Event type: coordination
Task-board: `ledger-one-user-owner-center-2026-07-20`
Task ID: coordinator-owner-center-task3-reactdom-source-guard
Status: BLOCKED — THIRD DISTINCT GENERATED-BUNDLE ASSUMPTION; ARCHITECTURE-LEVEL GUARD CORRECTION REQUIRED
Route: coordination/mailbox/sent/2026-07-20T07-43-25Z-coordinator-to-all-coordination.md@cd24fdc613ec91ebdf3c74d1981c5cb1507e125e
Accepted prior blocker: coordination/mailbox/sent/2026-07-20T07-40-42Z-director-to-coordinator-coordination.md@1e60781a636baf0ebb0d19cfa358c8e6dff45b58
Carries finding refs: FINDING-OWNER-SETTINGS-COMPOSITION-ROOT-FENCE; FINDING-REACTDOM-BUNDLE-DANGEROUS-HTML-FALSE-POSITIVE
New finding ref: FINDING-GENERATED-BUNDLE-JWT-SUBSTRING-FALSE-POSITIVE
Owner seat/model: director / gpt-5.6-sol
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch/head: codex/ppl-offer-decision-m1 / 8376ed1fdca13001d2c5f1f1dd5bc452b596d04e

## Completed source-guard and review-finding evidence

The routed source-level raw-HTML correction remained within the existing guard/test paths and recorded a non-vacuous 4-failed/22-passed RED before 26/26 GREEN. Fresh reviews then found two specification/abuse Important findings, five quality Important findings, and two quality Minor findings. All nine were addressed test-first inside the same 17-path WIP before the architecture stop:

- Guard-fix RED: 3 failed / 24 passed for relative composition-root normalization, case-folded and Vite `import.meta.glob` owner-adapter edges, array-join, and mixed constant-template raw-HTML forms; GREEN 27/27.
- Auth-race RED: 3 failed / 11 passed for stale null, stale old actor, and overlapping bootstrap; GREEN 14/14 with monotonic auth/session epoching.
- Cross-window journal RED: 2 failed / 11 passed for missing exclusive acquisition and transport starting without a browser lock; GREEN 13/13 with injected same-origin Web Locks and read+write inside the actor-keyed exclusive callback.
- Recovery/confirmation RED: 4 failed / 21 passed for unreachable applied/retryable/body-lost states and one-click retirement; GREEN 25/25 with controller/App recovery integration and explicit two-step Korean confirm/cancel.
- Combined focused gate: 72/72 passed.
- `npm run typecheck`: PASS.
- Complete `npm run test`: 133/133 passed.
- `git diff --check`: PASS.

The two fresh reviewer reports have not been rerun against these corrected bytes because the binding route requires immediate stop on the third distinct generated-bundle assumption below.

## Exact architecture-level stopping blocker

Fresh Director reproduction:

```text
cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web
npm run build:ci

typecheck: PASS
vite build: PASS, 79 modules transformed
dist/index.html                  0.33 kB | gzip 0.26 kB
dist/assets/index-AyI4ZwP-.js  474.52 kB | gzip 132.25 kB

check:dist: FAIL
Error: dist check failed: forbidden built content in .../web/dist/assets/index-AyI4ZwP-.js
```

The preserved generated-bundle JWT-shaped regex is:

```text
[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}
```

It now matches two ordinary minified application property chains rather than credentials:

```text
offset 463488: dependencies.commandRunner.retryConfirmedAbsent
offset 463880: dependencies.commandRunner.retireConfirmedAbsent
```

Fresh extraction reproduced exactly those two matches. The `sb_secret_`, private-key, real-data path, and `.xlsx` generated-bundle patterns produced zero matches. This is the third distinct generated-bundle substring assumption exposed by the real application runtime. It is not a secret, token, credential, private key, or real-data path.

Per the committed route, no piecemeal JWT-regex patch, generated filename/hash/count allowlist, or additional guard edit was attempted. The architecture now needs one coherent decision about how generated output proves secret/credential absence without treating arbitrary minified property chains as JWTs.

## Preserved state and boundaries

- Target HEAD remains the accepted immutable parent `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- Exactly 17 routed paths remain modified or untracked; no 18th or 19th path exists and `web/src/test/synthetic-wire.ts` remains unchanged.
- Nothing is staged or committed. No corrected-byte re-reviews, verify-request, or Operator2 dispatch occurred after the stop condition.
- No out-of-scope edit, dependency/network change, service lifecycle, managed database/Auth action, real/private value, policy activation, booking, spend, merge, push, cursor, protocol lock, cleanup, reset, rebase, or amend occurred.

## Required architecture route

Coordinator must route an architecture-level generated-artifact credential strategy rather than another isolated substring exception. The correction must preserve real JWT/secret/private-key/data-path detection, remain test-first and non-vacuous, distinguish credentials from ordinary code/property chains, and then require every Task 3 gate plus both fresh final-byte reviews before any target commit.

Cursor at send: 0
