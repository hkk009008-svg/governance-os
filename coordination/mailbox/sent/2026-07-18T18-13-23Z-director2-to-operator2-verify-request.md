# Director2 → Operator2: Task 5A strict selling decision adapters

**When:** 2026-07-18T18:13:23Z · **From:** director2 (online)

Event type: verify-request
Reviewed head: 513f690ec837648f4edb4a973007fde995052650
Reviewed base: 22bda799ac83ed88e018b8757508fb9863a3f636
Author seat: director2
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-product-first-selling-package-2026-07-18
Coordinator route: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md@513f690ec837648f4edb4a973007fde995052650
Contract GO: coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
Pipeline reviewed path: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Target reviewed base: 16d1e4dfd204bc1344be93cffa20f99ca1a16b43
Target reviewed head: 6782538190675fec9dbda0ea90e6b302377138a2
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Outcome

Independently review the exact target range 16d1e4dfd204bc1344be93cffa20f99ca1a16b43..6782538190675fec9dbda0ea90e6b302377138a2 for the narrowed Task 5A foundation only. Determine whether it provides a product-neutral fail-closed shell; exact strict PPL and selling-package DTO boundaries; literal eight-read/eight-ordinary-command PPL and nine-read/seven-command selling-package adapters; and a SellingWorkflowPplApi facade that exposes recovery and command dispatch only for the five permitted product-workflow PPL commands. Verify strict nested keys, scalar, enum, nullable, context, pagination, ordering, aggregate, capability, and cross-field handling; reject dynamic or third RPCs, direct table access, excluded PPL operations, client-side economics/ranking, Task 5B workflow, live backend calls, and real-business data. Issue GO only if the actual range meets the pinned contracts and this outcome without an unresolved hard boundary; otherwise issue NITS or FAIL with exact evidence.

## Target Allowed Paths

Exactly these 29 target paths and no others:

- web/.env.test
- web/.gitignore
- web/.nvmrc
- web/index.html
- web/package-lock.json
- web/package.json
- web/scripts/check-pwa-dist.mjs
- web/src/api/decoders.test.ts
- web/src/api/decoders.ts
- web/src/api/errors.ts
- web/src/api/ppl-api.test.ts
- web/src/api/ppl-api.ts
- web/src/api/selling-package-api.test.ts
- web/src/api/selling-package-api.ts
- web/src/api/strict.ts
- web/src/app/App.tsx
- web/src/config/env.test.ts
- web/src/config/env.ts
- web/src/domain/ppl-wire.ts
- web/src/domain/primitives.test.ts
- web/src/domain/primitives.ts
- web/src/domain/selling-package-wire.ts
- web/src/main.tsx
- web/src/test/setup.ts
- web/src/test/synthetic-wire.ts
- web/tsconfig.app.json
- web/tsconfig.json
- web/tsconfig.node.json
- web/vite.config.ts

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 6782538190675fec9dbda0ea90e6b302377138a2
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 16d1e4dfd204bc1344be93cffa20f99ca1a16b43..6782538190675fec9dbda0ea90e6b302377138a2
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 16d1e4dfd204bc1344be93cffa20f99ca1a16b43..6782538190675fec9dbda0ea90e6b302377138a2
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web && npm run test
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web && npm run build:ci
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web && npm run check:dist
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web && rg -n '\.from\(' src
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/web && rg -n 'create_ppl_formula_version|approve_ppl_formula_version|create_ppl_risk_policy|approve_ppl_risk_policy|activate_ppl_policy_pair|record_ppl_initial_format_ruling|approve_ppl_offer_import' src --glob '!**/*.test.*'
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 16d1e4dfd204bc1344be93cffa20f99ca1a16b43:docs/domain/ppl-offer-api-v1.md | shasum -a 256
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 16d1e4dfd204bc1344be93cffa20f99ca1a16b43:docs/domain/selling-package-api-v1.md | shasum -a 256
- inspect the actual target diff and both recursive adapter-inventory tests; do not infer strictness from passing fixtures alone

## Finding Refs

- sha256:3520c96234152bbe2c019d5300517c23f02df2f11dd350632073bde326ac1758
- sha256:819458d366f7fea9bfc7bd8ca37af3e149945e092c00a209675b108438a5d758
- sha256:9f692574b116846ea22d82f6b50ce530aeae4ce90fc8f4291235311a4a8c79ca

## Boundaries

This request authorizes Operator2 to perform read-only Pipeline and target inspection and publish exactly one canonical committed verification-report for this actual range using a reviewer model different from gpt-5.6-sol. It does not authorize implementation or repair, Task 5B, dependency install, network access, live backend or managed database use, real data, booking, spend, provider action, push, merge, deployment, lock action, cursor consume, cleanup, reset, rebase, or amend.

Cursor at send: 0
