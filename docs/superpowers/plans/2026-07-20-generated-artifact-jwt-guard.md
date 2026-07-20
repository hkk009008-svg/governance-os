# Generated-artifact Semantic JWT Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generated-bundle dotted-identifier heuristic with semantic compact-JWT detection so real embedded JWTs still fail while ordinary minified property chains pass.

**Architecture:** Keep generated-artifact credential detection separate from structural application-source enforcement. Discover three-segment Base64URL candidates in built content, canonically decode the header and payload, and classify only two non-null JSON objects as a JWT; retain every non-JWT bundle prohibition unchanged.

**Tech Stack:** Node.js >=22.12 ESM, Node `Buffer` Base64URL support, fatal UTF-8 `TextDecoder`, Vitest 4.1.10, TypeScript/Vite build pipeline.

## Global Constraints

- Approved design: `docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040`.
- Durable blocker: `coordination/mailbox/sent/2026-07-20T08-28-48Z-director-to-coordinator-coordination.md@cf210120b7b544829ec4ece7e63f87980b4f2e31`.
- Target worktree: `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`.
- Accepted target parent: `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- Preserve exactly the current 17-path unstaged WIP; open no additional target path.
- This correction may newly edit only `web/scripts/check-pwa-dist.mjs` and `web/src/api/owner-settings-api.test.ts`, which are already among the 17 paths.
- Add no dependency, package, lockfile, configuration, generated-file, service, database, Auth, private-value, or backend change.
- Preserve the existing `sb_secret_`, private-key, real-data-path, `.xlsx`, source-map, operations-only RPC, source-structure, and dependency-inventory gates.
- Do not allowlist a filename, bundle hash, byte offset, property name, occurrence count, React version, or current emitted bundle.
- Director remains the sole writer. The only target commit is the existing single authorized combined Task 3 commit after all gates and reviews pass.
- Operator2 / `gpt-5.6-terra` remains the non-author actual-range reviewer and sole verdict authority.
- No merge, push, cursor consumption, lock action, cleanup, reset, rebase, amend, activation, deployment, booking, or spend is authorized.

## File map

- Modify `web/src/api/owner-settings-api.test.ts`: express semantic JWT positives, false-positive regressions, malformed/non-object negatives, and preservation of all non-JWT bundle prohibitions.
- Modify `web/scripts/check-pwa-dist.mjs`: replace only the dotted-string JWT regex with canonical Base64URL plus JSON-object classification; leave all other guard responsibilities intact.

---

### Task 1: Make built-content JWT detection semantic

**Files:**
- Modify: `web/src/api/owner-settings-api.test.ts`
- Modify: `web/scripts/check-pwa-dist.mjs`

**Interfaces:**
- Consumes: `assertBuiltContentSafety(source: string, path?: string): void` from `web/scripts/check-pwa-dist.mjs`.
- Produces: `containsSemanticJwt(source: string): boolean`, used only by `assertBuiltContentSafety` and optionally exported for focused testing.
- Preserves: the existing failure text `dist check failed: forbidden built content in <path>`.

- [ ] **Step 1: Reconfirm the frozen writer boundary**

Run from the target worktree root:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git status --short
```

Expected:

- `HEAD` is exactly `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- The staged-path command prints nothing.
- Status lists exactly the preserved 17 paths and no other path.
- Stop without editing if any invariant differs.

- [ ] **Step 2: Replace the current built-content test with semantic positive and negative cases**

In `web/src/api/owner-settings-api.test.ts`, replace the single test beginning `allows the ReactDOM internal token` with these two tests:

```ts
  it("distinguishes semantic JWTs from ordinary dotted built code", async () => {
    const guard = await loadOwnerSourceGuard();
    const header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9";
    const payload = "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ";
    const signature = "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

    for (const jwt of [`${header}.${payload}.${signature}`, `${header}.${payload}.`]) {
      expect(() => guard.assertBuiltContentSafety(jwt, "assets/index.js")).toThrow("forbidden built content");
    }

    for (const allowed of [
      'function reactDOMInternal(){return "dangerouslySetInnerHTML"}',
      "dependencies.commandRunner.retryConfirmedAbsent",
      "dependencies.commandRunner.retireConfirmedAbsent",
      "abcdefghijkl.mnopqrstuvwx.yzABCDEFGHIJ",
      "abcde.e30.c2ln",
      "bm90LWpzb24.bm90LWpzb24.c2ln",
      "e30.InNjYWxhciI.c2ln",
      "e30.W10.c2ln",
      "_w.e30.c2ln",
    ]) {
      expect(() => guard.assertBuiltContentSafety(allowed, "assets/index.js")).not.toThrow();
    }
  });

  it("retains every non-JWT built-content prohibition", async () => {
    const guard = await loadOwnerSourceGuard();
    for (const forbidden of [
      "sb_secret_abcdefghijklmnop",
      "-----BEGIN PRIVATE KEY-----",
      "data/private.csv",
      "private-workbook.xlsx",
    ]) {
      expect(() => guard.assertBuiltContentSafety(forbidden, "assets/index.js")).toThrow("forbidden built content");
    }
  });
```

- [ ] **Step 3: Run the focused test and capture the non-vacuous RED**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts -t "distinguishes semantic JWTs"
```

Expected: FAIL because the unchanged dotted-string regex rejects at least `dependencies.commandRunner.retryConfirmedAbsent`; the realistic populated and empty-signature JWT assertions continue to fail closed. Preserve the exact failing assertion in the Director evidence.

- [ ] **Step 4: Implement canonical semantic JWT classification**

At the top of `web/scripts/check-pwa-dist.mjs`, add the Node built-in import:

```js
import { Buffer } from "node:buffer";
```

Replace only the JWT entry in `forbiddenBuilt` and update `assertBuiltContentSafety` with this implementation:

```js
const compactJwtCandidate = /(?<![A-Za-z0-9_-])([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]*)(?![A-Za-z0-9_-])/g;
const fatalUtf8 = new TextDecoder("utf-8", { fatal: true });

function decodeCanonicalJsonObject(segment) {
  try {
    const bytes = Buffer.from(segment, "base64url");
    if (bytes.toString("base64url") !== segment) return undefined;
    const value = JSON.parse(fatalUtf8.decode(bytes));
    return typeof value === "object" && value !== null && !Array.isArray(value)
      ? value
      : undefined;
  } catch {
    return undefined;
  }
}

export function containsSemanticJwt(source) {
  for (const match of source.matchAll(compactJwtCandidate)) {
    if (decodeCanonicalJsonObject(match[1]) !== undefined &&
        decodeCanonicalJsonObject(match[2]) !== undefined) {
      return true;
    }
  }
  return false;
}

const forbiddenBuilt = [
  /sb_secret_[A-Za-z0-9_-]{16,}/,
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
  /(?:^|["'])data\//,
  /\.xlsx\b/,
];

export function assertBuiltContentSafety(source, path = "built asset") {
  if (containsSemanticJwt(source) || forbiddenBuilt.some((pattern) => pattern.test(source))) {
    fail(`forbidden built content in ${path}`);
  }
}
```

Do not change source scanning, RPC inventories, dependency inventories, generated-file traversal, or any other built-content pattern.

- [ ] **Step 5: Run the focused guard file to GREEN**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts
```

Expected: all 28 tests pass. The property-chain, malformed Base64URL, invalid UTF-8, non-JSON, scalar-JSON, and array-JSON fixtures pass; both semantic JWT fixtures and all four retained built-content fixtures fail closed.

- [ ] **Step 6: Prove the real bundle passes without weakening actual credential detection**

Run from `web`:

```bash
npm run build:ci
```

Expected: typecheck and Vite build pass, `check:dist` prints `dist check passed`, and neither observed `commandRunner` property chain is reported as a credential.

Do not stage or commit yet; the combined Task 3 gate and both final-byte reviews remain mandatory.

---

### Task 2: Reverify and submit the complete Task 3 range

**Files:**
- Verify: all 17 preserved target paths
- Commit: the exact 17-path combined Task 3 range only after every gate and review passes
- Publish: one canonical Pipeline verify-request assigned to Operator2

**Interfaces:**
- Consumes: Task 1 GREEN semantic guard and the preserved Task 3 implementation/review-finding fixes.
- Produces: one local evidence-ledger Task 3 commit and one immutable actual-range verify-request.

- [ ] **Step 1: Run the combined focused suite**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
```

Expected: all 73 tests pass.

- [ ] **Step 2: Run typecheck, the complete suite, and the production build gate**

Run from `web`, one command at a time:

```bash
npm run typecheck
npm run test
npm run build:ci
```

Expected:

- typecheck passes;
- all 134 tests pass; and
- compilation, Vite bundling, and `check:dist` all pass.

- [ ] **Step 3: Re-run persistence, transport, and private-surface audits**

Run from the target worktree root:

```bash
rg -n "localStorage|sessionStorage|indexedDB|caches\.|JSON\.stringify\(" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
rg -n "\.rpc\(|\.from\(" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
rg -n "create_ppl_formula_version|approve_ppl_formula_version|create_ppl_risk_policy|approve_ppl_risk_policy|activate_ppl_policy_pair|record_ppl_initial_format_ruling|approve_ppl_offer_import" web/src
rg -n "console\.|logger\.|signup|sign up|user switcher|사용자 전환|회원가입" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
```

Expected:

- Local Storage appears only in `pending-journal.ts` and Session Storage only in the auth adapter.
- No IndexedDB or Cache Storage use exists.
- Production RPC calls remain inside the three literal adapters, with no `.from(` transport.
- Operations-only names, logging, signup, and user-switcher language produce no prohibited production match.

- [ ] **Step 4: Recompute immutable contracts and repository gates**

Run from the target worktree root:

```bash
shasum -a 256 docs/domain/ppl-offer-api-v1.md docs/domain/selling-package-api-v1.md docs/domain/owner-settings-api-v1.md
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git status --short
```

Expected hashes, in order:

```text
1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6
cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40
```

Also require smoke PASS, clean diff syntax, nothing staged, exactly the 17 preserved paths, and no change to `web/src/test/synthetic-wire.ts`.

- [ ] **Step 5: Obtain both fresh final-byte reviews**

Director sends the exact live 17-path bytes to two read-only reviewers:

1. specification/abuse review covering semantic JWT false positives and false negatives, source/bundle responsibility, import and RPC fences, auth epoching, Web Locks atomicity, metadata-only persistence, recovery reachability, and Korean two-step retirement;
2. code-quality review covering the same actual bytes, browser support/fail-closed behavior, lifecycle races, cleanup, type safety, and test adequacy.

Expected: both reviews identify the immutable base, all 17 actual paths, and their findings. Resolve every Critical or Important finding test-first within the allowed paths, then repeat Steps 1 through 4 on the final bytes. Preserve every finding and disposition in the verify-request.

- [ ] **Step 6: Stage the exact combined range and create the single authorized target commit**

Run from the target worktree root only after all gates and reviews pass:

```bash
env -u GIT_INDEX_FILE git add -- \
  web/scripts/check-pwa-dist.mjs \
  web/src/api/owner-settings-api.test.ts \
  web/src/api/supabase.ts \
  web/src/app/App.tsx \
  web/src/app/AppContext.tsx \
  web/src/app/AppController.test.ts \
  web/src/app/AppController.ts \
  web/src/app/sensitive-state.ts \
  web/src/features/auth/LoginView.tsx \
  web/src/features/auth/session.test.ts \
  web/src/features/auth/session.ts \
  web/src/features/recovery/RecoveryPanel.tsx \
  web/src/features/recovery/command-runner.test.ts \
  web/src/features/recovery/command-runner.ts \
  web/src/features/recovery/pending-journal.test.ts \
  web/src/features/recovery/pending-journal.ts \
  web/src/main.tsx
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(web): add owner session recovery foundations"
```

Expected: the staged inventory is exactly the 17 listed paths, the cached diff check passes, and exactly one new target commit is created on `codex/ppl-offer-decision-m1`.

- [ ] **Step 7: Publish and dispatch the immutable Operator2 review trigger**

Director returns to `/Users/hyungkoookkim/Pipeline`, refreshes Pipeline and target state, and uses the fixed writer:

```text
coordination/bin/send-event director operator2 verify-request "Owner-center Task 3 semantic JWT guard actual-range review"
```

The body must bind the approved design and implementation plan commits, superseding coordinator route, target repository/worktree/branch, immutable base and new head, exact 17 paths, Director and Operator2 models, every RED/GREEN and full-gate result, build output, three hashes, both final-byte reviews, all finding refs and dispositions, and every authority exclusion.

Director then reuses the existing compatible Operator2 Codex task, sends the committed exact trigger once, waits without duplicate dispatch, and stops for Operator2 GO/NITS/FAIL.

Expected: one committed canonical verify-request and one exact Operator2 dispatch. No merge or push follows from this plan.
