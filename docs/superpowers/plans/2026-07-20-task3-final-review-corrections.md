# Owner-center Task 3 Final-review Corrections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The governed Director is the sole production writer; read-only reviewers do not share implementation ownership.

**Goal:** Resolve the seven preserved Important final-byte findings and two directly related Minor gaps without opening a new target path, dependency, framework, or product feature.

**Architecture:** Reuse the existing closed constant-string evaluator for generated and source guards, replace partial journal locking with one actor-scoped transaction, make command attempts clone-safe and terminally classified, and split controller DTO clearing from same-actor retained-command preservation. Logout remains fenced until Supabase storage-backed absence is proven.

**Tech Stack:** TypeScript 7.0.2, Node.js >=22.12 ESM, TypeScript scanner from the existing toolchain, React 19.2.7, Supabase JS/Auth 2.110.7, Web Locks, Session Storage, Vitest 4.1.10, Vite 8.1.5.

## Global Constraints

- Approved correction design: `docs/superpowers/specs/2026-07-20-task3-final-review-corrections-design.md@035fc1e75bc2eefcf01ec10ee4b00f49458057f3`.
- Binding blocker report: `coordination/mailbox/sent/2026-07-20T09-21-17Z-director-to-coordinator-coordination.md@1f07af86bfa85a99129a686d65b1ed48ea389d8d`.
- Prior semantic guard design remains binding where not superseded: `docs/superpowers/specs/2026-07-20-generated-artifact-jwt-guard-design.md@bd0fb985a5a39f042f47ae90422553ac98413040`.
- Target worktree: `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`.
- Accepted target HEAD: `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- Preserve exactly the existing 17-path unstaged Task 3 WIP and an empty index until every final gate and both final-byte reviews pass.
- Newly edit only the eight correction files named in the file map below. The other nine routed Task 3 files remain preserved bytes.
- `web/src/config/env.test.ts` is read-only verification input. `web/src/test/synthetic-wire.ts` remains closed and unchanged.
- Add no package, dependency, lockfile, configuration, service, backend, database, managed Auth, generated artifact, or new source file.
- Preserve object/object compact serialization as credential-like even without a JOSE `alg` member. Preserve empty-signature rejection.
- Preserve every `sb_secret_`, private-key, real-data-path, `.xlsx`, source-map, operations-only, exact RPC-inventory, raw-HTML, import-edge, and dependency-inventory gate.
- Use test-first RED -> minimal GREEN for one correction unit at a time. Do not batch implementation before its named RED.
- Governance overrides the ordinary per-task commit cadence: make no intermediate target commit. Director creates exactly one combined Task 3 target commit only after final reviews and all gates pass.
- Director / `gpt-5.6-sol` is the sole writer. Operator2 / `gpt-5.6-terra` is the assigned non-author actual-range reviewer and sole GO/NITS/FAIL authority.
- User selected a later local merge, not push. This plan authorizes neither; a separate exact post-GO route must bind source SHA, destination branch, executor, and clean-state checks.
- No cursor consumption, protocol lock action, cleanup, reset, rebase, amend, activation, deployment, booking, spend, real/private-data use, Pipeline push, or evidence-ledger push is authorized.

## File map

- Modify `web/scripts/check-pwa-dist.mjs`: closed constant reconstruction, semantic artifact classification, source-wide dynamic-code and direct-transport fences.
- Modify `web/src/api/owner-settings-api.test.ts`: artifact reconstruction, computed sink, direct RPC, and raw transport regressions without changing this file's 28-test count.
- Modify `web/src/features/recovery/pending-journal.ts`: actor-scoped `withExclusive` transaction and no unlocked mutation surface.
- Modify `web/src/features/recovery/pending-journal.test.ts`: transaction use, full-lock serialization, and unsupported-Web-Locks regression; final count 6.
- Modify `web/src/features/recovery/command-runner.ts`: transaction-bound lifecycle, fresh transport clones, terminal retry disposition, and exact revalidation.
- Modify `web/src/features/recovery/command-runner.test.ts`: mutation, terminal rejection, and cross-tab race regressions; final count 11.
- Modify `web/src/app/AppController.ts`: same-actor retained-memory reachability, stale-recovery prevention, logout proof, and callback fence.
- Modify `web/src/app/AppController.test.ts`: stateful same-actor recovery, definitive retry, and logout race regressions; final count 19.

The focused six-file gate starts at 73 tests and ends at exactly 79:

```text
owner-settings-api.test.ts  28 -> 28
env.test.ts                 11 -> 11
session.test.ts              4 -> 4
pending-journal.test.ts      5 -> 6
command-runner.test.ts       8 -> 11
AppController.test.ts       17 -> 19
TOTAL                       73 -> 79
```

The complete suite starts at 134 and ends at exactly 140.

---

### Task 0: Rebind the preserved target and executable baseline

**Files:**
- Verify only: all 17 existing Task 3 paths.

**Interfaces:**
- Consumes: approved design `035fc1e75bc2eefcf01ec10ee4b00f49458057f3`.
- Produces: immutable pre-edit state and executable 73/73 plus 134/134 baselines.

- [ ] **Step 1: Verify target identity, empty index, and exact 17-path WIP**

Run from the target worktree:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git status --short
```

Expected:

- HEAD is exactly `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- The cached-name command prints nothing.
- Status contains exactly the 17 paths in the superseding route and no 18th path.
- Stop without editing on any mismatch.

- [ ] **Step 2: Re-run the focused and complete baselines**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts src/config/env.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
npm run test
```

Expected:

- focused: 6 files, 73/73 tests;
- complete: 11 files, 134/134 tests.

The first sandbox failure at `node_modules/.vite-temp` is `environment-policy`, not a product RED. If it recurs, rerun the identical command once through the supported profile; do not change code, cache paths, dependencies, or configuration.

---

### Task 1: Close reconstructed artifact and source-transport bypasses

**Files:**
- Modify: `web/src/api/owner-settings-api.test.ts`
- Modify: `web/scripts/check-pwa-dist.mjs`

**Interfaces:**
- Consumes: existing `scanSource`, `constantStringExpression`, `containsSemanticJwt`, `assertOwnerRpcInventory`, and `assertBuiltContentSafety`.
- Produces: `assertProductionSourceSafety(source: string, allowRpc: boolean, path?: string): void`.
- Preserves: `containsSemanticJwt(source: string): boolean`, `assertBuiltContentSafety(source: string, path?: string): void`, and every existing guard failure responsibility.

- [ ] **Step 1: Extend existing tests without adding a new Vitest case**

In the existing test `rejects dynamic code execution and construction inside the factory`, append these exact statements:

```ts
'globalThis["Fun" + "ction"]("return hidden")()',
'globalThis[["Fun", "ction"].join("")]("return hidden")()',
```

In `keeps raw operations, persistence, network, and owner imports out of ordinary sources`, add this exact synthetic rejection loop:

```ts
    for (const source of [
      'client.rpc("get_owner_settings_status")',
      'client["r" + "pc"]("get_owner_settings_status")',
      'fetch("/rest/v1/rpc/get_owner_settings_status")',
      "new XMLHttpRequest()",
      'navigator.sendBeacon("/rest/v1/rpc/get_owner_settings_status", body)',
      'globalThis["Fun" + "ction"]("return client")()',
    ]) {
      expect(() => guard.assertProductionSourceSafety(source, false, "src/app/Bypass.ts")).toThrow();
    }
```

Extend the local `OwnerSourceGuard` test interface with:

```ts
assertProductionSourceSafety(source: string, allowRpc?: boolean, path?: string): void;
```

Extend the same test's production-tree loop so only the three exact adapter paths pass `allowRpc=true`:

```ts
    const rpcAdapters = new Set([
      join(root, "api/ppl-api.ts"),
      join(root, "api/selling-package-api.ts"),
      join(root, "api/owner-settings-api.ts"),
    ]);
    for (const file of productionFiles) {
      expect(() => guard.assertProductionSourceSafety(
        readFileSync(file, "utf8"),
        rpcAdapters.has(file),
        file,
      )).not.toThrow();
    }
```

In `distinguishes semantic JWTs from ordinary dotted built code`, add these exact reconstructed positives and preserve `e30.e30.c2ln` as forbidden:

```ts
    for (const builtSource of [
      `${header}.${payload}.${signature}`,
      `${header}.${payload}.`,
      `const token = "${header}" + "." + "${payload}" + "." + "${signature}";`,
      `const token = ["${header}", "${payload}", "${signature}"].join(".");`,
      `const token = ["${header}", "${payload}", ""].join(".");`,
      `const token = \`${header}\${"."}${payload}\${"."}${signature}\`;`,
      "e30.e30.c2ln",
    ]) {
      expect(() => guard.assertBuiltContentSafety(builtSource, "assets/index.js"))
        .toThrow("forbidden built content");
    }
```

Keep every existing allowed fixture and every non-JWT prohibition assertion.

- [ ] **Step 2: Run the three named tests and preserve non-vacuous RED**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts -t "rejects dynamic code execution|keeps raw operations|distinguishes semantic JWTs"
```

Expected: RED because at least the split `Function`, direct ordinary RPC/raw transport, and joined JWT forms are accepted by the current guard. The existing contiguous JWT assertions remain fail-closed.

- [ ] **Step 3: Add closed constant-root enumeration and reuse the semantic classifier**

Add this helper beside the existing constant-string evaluator:

```js
function constantStringRoots(tokens) {
  const roots = [];
  for (let index = 0; index < tokens.length; index += 1) {
    if (tokenIs(tokens[index - 1], SyntaxKind.PlusToken)) continue;
    const expression = constantStringExpression(tokens, index);
    if (!expression || tokenIs(tokens[expression.cursor], SyntaxKind.PlusToken)) continue;
    roots.push(expression.value);
  }
  return roots;
}
```

Extract the current regex loop without changing its object/object semantics:

```js
function containsContiguousSemanticJwt(source) {
  for (const match of source.matchAll(compactJwtCandidate)) {
    if (decodeCanonicalJsonObject(match[1]) !== undefined &&
        decodeCanonicalJsonObject(match[2]) !== undefined) {
      return true;
    }
  }
  return false;
}

export function containsSemanticJwt(source) {
  if (containsContiguousSemanticJwt(source)) return true;
  return constantStringRoots(scanSource(source))
    .some((value) => containsContiguousSemanticJwt(value));
}
```

Do not add identifier resolution, alias tracking, arbitrary call evaluation, control-flow analysis, or a new parser.

- [ ] **Step 4: Add one source-wide safety helper**

Keep the existing `dynamicCodeNames` declaration, add `rawTransportNames`, and
add the helper below. Do not create a second `dynamicCodeNames` declaration:

```js
const rawTransportNames = new Set(["fetch", "XMLHttpRequest", "sendBeacon"]);

function exactConstantNames(tokens) {
  const names = [];
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];
    if (tokenIs(token, SyntaxKind.Identifier) ||
        tokenIs(token, SyntaxKind.StringLiteral) ||
        tokenIs(token, SyntaxKind.NoSubstitutionTemplateLiteral)) {
      names.push(token.value);
    }
    if (tokenIs(tokens[index - 1], SyntaxKind.PlusToken)) continue;
    const expression = constantStringExpression(tokens, index);
    if (expression && !tokenIs(tokens[expression.cursor], SyntaxKind.PlusToken)) {
      names.push(expression.value);
    }
  }
  return names;
}

export function assertProductionSourceSafety(
  source,
  allowRpc = false,
  path = "guard-fixture.ts",
) {
  const names = exactConstantNames(scanSource(source));
  if (names.some((name) => dynamicCodeNames.has(name))) {
    fail(`dynamic code sink is forbidden in ${path}`);
  }
  if (names.some((name) => rawTransportNames.has(name))) {
    fail(`raw transport is forbidden in ${path}`);
  }
  if (!allowRpc && names.includes("rpc")) {
    fail(`direct RPC is forbidden in ordinary source ${path}`);
  }
}
```

Make `assertNoOwnerDynamicCode` delegate to `assertProductionSourceSafety(source, true, path)`. Invoke `assertProductionSourceSafety` at the start of `assertOwnerRpcInventory` so computed dynamic names fail even in the bound owner adapter.

In `runDistCheck`, compute the exact allowed adapter set:

```js
const rpcAdapterPaths = new Set([
  normalize(join(root, "src/api/ppl-api.ts")),
  normalize(join(root, "src/api/selling-package-api.ts")),
  normalize(join(root, "src/api/owner-settings-api.ts")),
]);
```

For every production source, call:

```js
assertProductionSourceSafety(
  source,
  rpcAdapterPaths.has(normalize(file)),
  file,
);
```

The three adapters remain governed by their existing literal inventory checks. Raw transport and dynamic code are forbidden even when `allowRpc` is true.

- [ ] **Step 5: Run guard GREEN and real build**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts
npm run build:ci
```

Expected:

- owner guard file: 28/28 tests;
- build and distribution check pass;
- real command-runner property chains remain allowed;
- contiguous, concatenated, templated, joined, populated-signature, empty-signature, and `e30.e30.c2ln` credential-like forms fail closed.

- [ ] **Step 6: Record a no-commit checkpoint**

Run from the target worktree:

```bash
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git diff --cached --name-only
```

Expected: diff check passes and the index remains empty. Do not commit.

---

### Task 2: Replace partial pending-journal locks with one actor transaction

**Files:**
- Modify: `web/src/features/recovery/pending-journal.test.ts`
- Modify: `web/src/features/recovery/pending-journal.ts`

**Interfaces:**
- Produces:

```ts
export interface PendingJournalTransaction {
  read(): PendingMetadata | null;
  begin(value: PendingMetadata): void;
  removeMatching(requestId: string): void;
}

export interface PendingJournal {
  read(actorId: string): PendingMetadata | null;
  withExclusive<T>(
    actorId: string,
    callback: (transaction: PendingJournalTransaction) => T | Promise<T>,
  ): Promise<T>;
}
```

- Removes from the public interface: unlocked `begin`, `clearApplied`, `retireConfirmedAbsent`, and partial `beginExclusive`.

- [ ] **Step 1: Convert existing journal tests to the transaction API**

Add this test helper:

```ts
async function begin(
  journal: ReturnType<typeof createPendingJournal>,
  actorId: string,
  pending: PendingMetadata,
) {
  await journal.withExclusive(actorId, (transaction) => transaction.begin(pending));
}
```

Make the existing persistence, recreation, and rejection tests async. Replace direct mutation calls as follows:

```ts
await begin(journal, UUID.toUpperCase(), pending);

await expect(journal.withExclusive(UUID, (transaction) =>
  transaction.begin({
    namespace: "owner_settings",
    operation: "create_selling_case",
    request_id: UUID,
    created_at: UTC,
  } as never),
)).rejects.toBeInstanceOf(InvalidPendingJournalError);

await expect(journal.withExclusive(UUID, (transaction) =>
  transaction.removeMatching(ACTOR_B),
)).rejects.toBeInstanceOf(InvalidPendingJournalError);
```

Because mutation now deliberately fails closed without Web Locks, pass a real
test lock manager to every journal instance used for mutation. Reuse one shared
manager when a test recreates the journal over the same storage:

```ts
const locks = sameOriginLocks();
const first = createPendingJournal(storage, locks);
const reopened = createPendingJournal(storage, locks);
```

Read-only malformed-storage assertions may continue constructing a journal
without entering a transaction.

Replace the current concurrent-begin test with this full-callback serialization test:

```ts
  it("holds one actor lock through the complete transaction callback", async () => {
    const { storage } = memoryStorage();
    const locks = sameOriginLocks();
    const first = createPendingJournal(storage, locks);
    const second = createPendingJournal(storage, locks);
    const entered = deferred<void>();
    const release = deferred<void>();
    const firstPending = { namespace: "selling_workflow", operation: "create_selling_case", request_id: UUID, created_at: UTC } as const;
    const secondPending = { namespace: "selling_workflow", operation: "revise_selling_case", request_id: ACTOR_B, created_at: UTC } as const;

    const firstTransaction = first.withExclusive(UUID, async (transaction) => {
      transaction.begin(firstPending);
      entered.resolve();
      await release.promise;
      transaction.removeMatching(UUID);
    });
    await entered.promise;

    let secondEntered = false;
    const secondTransaction = second.withExclusive(UUID, (transaction) => {
      secondEntered = true;
      expect(transaction.read()).toBeNull();
      transaction.begin(secondPending);
    });
    await Promise.resolve();
    expect(secondEntered).toBe(false);

    release.resolve();
    await Promise.all([firstTransaction, secondTransaction]);
    expect(second.read(UUID)).toEqual(secondPending);
  });
```

Add this local helper above the tests:

```ts
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((next) => { resolve = next; });
  return { promise, resolve };
}
```

Replace the existing `sameOriginLocks` double with a generic implementation of
the new `PendingLockManager` contract, and import that type:

```ts
function sameOriginLocks(): PendingLockManager {
  let tail = Promise.resolve();
  return {
    async request<T>(
      _name: string,
      _options: { mode: "exclusive" },
      callback: () => T | Promise<T>,
    ): Promise<T> {
      const predecessor = tail;
      let release!: () => void;
      tail = new Promise<void>((resolve) => { release = resolve; });
      await predecessor;
      try {
        return await callback();
      } finally {
        release();
      }
    },
  };
}
```

- [ ] **Step 2: Add the sixth journal test for unsupported Web Locks**

```ts
  it("rejects before persistence when Web Locks are unavailable", async () => {
    const { values, storage } = memoryStorage();
    const journal = createPendingJournal(storage, null);
    const pending = { namespace: "selling_workflow", operation: "create_selling_case", request_id: UUID, created_at: UTC } as const;

    await expect(journal.withExclusive(UUID, (transaction) =>
      transaction.begin(pending),
    )).rejects.toBeInstanceOf(InvalidPendingJournalError);
    expect(storage.setItem).not.toHaveBeenCalled();
    expect(values.size).toBe(0);
  });
```

- [ ] **Step 3: Run journal RED**

Run from `web`:

```bash
npm test -- src/features/recovery/pending-journal.test.ts
```

Expected: RED because `withExclusive` and its transaction object do not exist and the current factory does not accept the explicit `null` unsupported-lock sentinel.

- [ ] **Step 4: Implement the transaction interface**

Use these exact interfaces:

```ts
export interface PendingJournalTransaction {
  read(): PendingMetadata | null;
  begin(value: PendingMetadata): void;
  removeMatching(requestId: string): void;
}

export interface PendingJournal {
  read(actorId: string): PendingMetadata | null;
  withExclusive<T>(
    actorId: string,
    callback: (transaction: PendingJournalTransaction) => T | Promise<T>,
  ): Promise<T>;
}

export interface PendingLockManager {
  request<T>(
    name: string,
    options: { mode: "exclusive" },
    callback: () => T | Promise<T>,
  ): Promise<T>;
}
```

Make `browserLockManager()` return `PendingLockManager | null`, and make the factory's second parameter `PendingLockManager | null = browserLockManager()`.

Inside `createPendingJournal`, keep the existing strict decoder and read function. Add:

```ts
  function transaction(actorId: string): PendingJournalTransaction {
    const key = actorKey(actorId);
    return {
      read: () => read(actorId),
      begin(value) {
        if (read(actorId) !== null) fail();
        const metadata = decodeMetadata(value);
        storage.setItem(key, JSON.stringify({
          namespace: metadata.namespace,
          operation: metadata.operation,
          request_id: metadata.request_id,
          created_at: metadata.created_at,
        }));
      },
      removeMatching(requestId) {
        let canonicalRequest: string;
        try { canonicalRequest = canonicalUuid(requestId); } catch { return fail(); }
        const pending = read(actorId);
        if (pending === null || pending.request_id !== canonicalRequest) fail();
        storage.removeItem(key);
      },
    };
  }

  return {
    read,
    async withExclusive<T>(actorId, callback) {
      if (locks === null) fail();
      return locks.request(
        actorLockName(actorId),
        { mode: "exclusive" },
        () => callback(transaction(actorId)),
      );
    },
  };
```

Remove the old public mutation methods. Do not add a timeout, fallback lock, Local-Storage spin lock, BroadcastChannel protocol, or retry loop.

- [ ] **Step 5: Run journal GREEN and the interim focused gate**

Run from `web`:

```bash
npm test -- src/features/recovery/pending-journal.test.ts
npm test -- src/api/owner-settings-api.test.ts src/config/env.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
```

Expected:

- journal: 6/6;
- interim focused gate: RED only in runner/controller compilation because their old journal calls are now intentionally removed. Preserve this as an interface-migration RED; do not weaken the transaction API to make old callers compile.

- [ ] **Step 6: Record a no-commit checkpoint**

Run `git diff --check` and prove the target index is still empty. Do not commit.

---

### Task 3: Bind the command runner to the transaction and immutable retry bytes

**Files:**
- Modify: `web/src/features/recovery/command-runner.test.ts`
- Modify: `web/src/features/recovery/command-runner.ts`

**Interfaces:**
- Consumes: `PendingJournal.withExclusive` and `PendingJournalTransaction`.
- Produces:

```ts
export type RetryOutcome =
  | { readonly kind: "applied" }
  | { readonly kind: "rejected" };
```

- `retryConfirmedAbsent(actorId: string): Promise<RetryOutcome>`.
- `retireConfirmedAbsent(actorId: string, confirmation: string): Promise<void>`.

- [ ] **Step 1: Update existing retry/retirement assertions for the new terminal API**

In the existing retry test, require:

```ts
await expect(runner.retryConfirmedAbsent(UUID)).resolves.toEqual({ kind: "applied" });
expect(selling.command.mock.calls[1]![1]).not.toBe(selling.command.mock.calls[0]![1]);
expect(selling.command.mock.calls[1]![1]).toEqual(selling.command.mock.calls[0]![1]);
```

Rename the test so it describes retained canonical bytes rather than exact
object identity. Remove its old `.toBe(...)` identity assertion.

Make retirement assertions asynchronous:

```ts
await expect(second.runner.retireConfirmedAbsent(UUID, "잘못된 확인")).rejects.toThrow();
await expect(second.runner.retireConfirmedAbsent(UUID, "보류 명령 폐기")).resolves.toBeUndefined();
```

- [ ] **Step 2: Add three focused runner regressions**

Add the mutation regression:

```ts
  it("retries a fresh clone when the first transport mutates its argument", async () => {
    const selling = {
      command: vi.fn()
        .mockImplementationOnce((_operation, command) => {
          command.body.title = "transport mutation";
          return Promise.reject(new TypeError("network"));
        })
        .mockResolvedValueOnce(commandEnvelope(packageCommandData.create_selling_case)),
      commandResult: vi.fn().mockResolvedValue(readEnvelope({ state: "confirmed_absent", response: null })),
    };
    const { runner } = harness({ selling });

    await expect(runner.execute(UUID, "selling_workflow", "create_selling_case",
      (requestId) => ({ ...packageCommand("create_selling_case"), request_id: requestId }),
    )).rejects.toBeInstanceOf(AmbiguousCommandError);
    await expect(runner.recover(UUID)).resolves.toMatchObject({ kind: "retryable" });
    await expect(runner.retryConfirmedAbsent(UUID)).resolves.toEqual({ kind: "applied" });

    expect(selling.command.mock.calls[0]![1]).not.toBe(selling.command.mock.calls[1]![1]);
    expect(selling.command.mock.calls[1]![1].body.title).toBe("합성 판매");
  });
```

Add the definitive-retry regression:

```ts
  it("returns a terminal rejection and clears the journal after a definitive retry error", async () => {
    const expected = new PplExpectedError("PPL_STALE_HEAD", null);
    const selling = {
      command: vi.fn()
        .mockRejectedValueOnce(new TypeError("network"))
        .mockRejectedValueOnce(expected),
      commandResult: vi.fn().mockResolvedValue(readEnvelope({ state: "confirmed_absent", response: null })),
    };
    const { runner, values } = harness({ selling });

    await expect(runner.execute(UUID, "selling_workflow", "create_selling_case",
      (requestId) => ({ ...packageCommand("create_selling_case"), request_id: requestId }),
    )).rejects.toBeInstanceOf(AmbiguousCommandError);
    await expect(runner.recover(UUID)).resolves.toMatchObject({ kind: "retryable" });
    await expect(runner.retryConfirmedAbsent(UUID)).resolves.toEqual({ kind: "rejected" });
    expect(values.size).toBe(0);
    expect(runner.pending(UUID)).toBeNull();
  });
```

Import `PendingLockManager`. Update the existing `immediateLocks` helper and
the gated lock double in `awaits exclusive same-origin pending acquisition
before transport` to implement its generic `request<T>` method. Where that
test asserts calls, record them with a separate `vi.fn` rather than weakening
the production interface.

```ts
function immediateLocks(): PendingLockManager {
  return {
    async request<T>(
      _name: string,
      _options: { mode: "exclusive" },
      callback: () => T | Promise<T>,
    ): Promise<T> {
      return callback();
    },
  };
}
```

For the gated test, call a separate `const request = vi.fn()` from inside the
same generic method and move the existing call-count assertion to `request`.

Add these declarations above the runner tests:

```ts
const ACTOR_B = "22222222-2222-4222-8222-222222222222";

function sameOriginLocks(): PendingLockManager {
  let tail = Promise.resolve();
  return {
    async request<T>(
      _name: string,
      _options: { mode: "exclusive" },
      callback: () => T | Promise<T>,
    ): Promise<T> {
      const predecessor = tail;
      let release!: () => void;
      tail = new Promise<void>((resolve) => { release = resolve; });
      await predecessor;
      try {
        return await callback();
      } finally {
        release();
      }
    },
  };
}
```

Then add this cross-tab regression:

```ts
  it("serializes retry, retirement, and replacement begin across tabs", async () => {
    const values = new Map<string, string>();
    const storage = {
      getItem: vi.fn((key: string) => values.get(key) ?? null),
      setItem: vi.fn((key: string, value: string) => values.set(key, value)),
      removeItem: vi.fn((key: string) => values.delete(key)),
    };
    const locks = sameOriginLocks();
    const retryGate = deferred<unknown>();
    const selling = {
      command: vi.fn()
        .mockRejectedValueOnce(new TypeError("network"))
        .mockImplementationOnce(() => retryGate.promise)
        .mockResolvedValueOnce(commandEnvelope(packageCommandData.create_selling_case)),
      commandResult: vi.fn().mockResolvedValue(readEnvelope({ state: "confirmed_absent", response: null })),
    };
    const first = harness({ journal: createPendingJournal(storage, locks), selling }).runner;
    const second = harness({ journal: createPendingJournal(storage, locks), selling }).runner;
    const replacement = harness({
      journal: createPendingJournal(storage, locks),
      selling,
      randomUuid: () => ACTOR_B,
    }).runner;

    await expect(first.execute(UUID, "selling_workflow", "create_selling_case",
      (requestId) => ({ ...packageCommand("create_selling_case"), request_id: requestId }),
    )).rejects.toBeInstanceOf(AmbiguousCommandError);
    await expect(first.recover(UUID)).resolves.toMatchObject({ kind: "retryable" });
    await expect(second.recover(UUID)).resolves.toMatchObject({ kind: "body_lost" });

    const retry = first.retryConfirmedAbsent(UUID);
    await vi.waitFor(() => expect(selling.command).toHaveBeenCalledTimes(2));
    const observe = second.recover(UUID);
    const retire = second.retireConfirmedAbsent(UUID, "보류 명령 폐기");
    const next = replacement.execute(UUID, "selling_workflow", "create_selling_case",
      (requestId) => ({ ...packageCommand("create_selling_case"), request_id: requestId }),
    );
    await Promise.resolve();
    expect(selling.command).toHaveBeenCalledTimes(2);

    retryGate.resolve(commandEnvelope(packageCommandData.create_selling_case));
    await expect(retry).resolves.toEqual({ kind: "applied" });
    await expect(observe).resolves.toEqual({ kind: "clear" });
    await expect(retire).rejects.toThrow();
    await expect(next).resolves.toBeDefined();
    expect(selling.command).toHaveBeenCalledTimes(3);
  });
```

- [ ] **Step 3: Run runner RED**

Run from `web`:

```bash
npm test -- src/features/recovery/command-runner.test.ts
```

Expected: RED because the current runner uses removed journal methods, passes the retained object directly to transport, rethrows definitive retry errors, returns raw retry responses, and retires outside the actor lock.

- [ ] **Step 4: Implement terminal attempt classification and fresh clones**

Import `PendingJournalTransaction` and add:

```ts
export type RetryOutcome =
  | { readonly kind: "applied" }
  | { readonly kind: "rejected" };

type AttemptOutcome =
  | { readonly kind: "applied"; readonly response: unknown }
  | { readonly kind: "rejected"; readonly error: PplExpectedError };
```

Inside `createCommandRunner`, immediately after `send`, add the attempt
classifier so it can call the local `withTimeout` and `send` functions:

```ts
  async function attempt(
    pending: PendingMetadata,
    canonicalCommand: unknown,
  ): Promise<AttemptOutcome> {
    try {
      return {
        kind: "applied",
        response: await withTimeout(send(pending, cloneCommand(canonicalCommand))),
      };
    } catch (error: unknown) {
      if (error instanceof PplExpectedError) return { kind: "rejected", error };
      throw new AmbiguousCommandError();
    }
  }

  function samePending(left: PendingMetadata | null, right: PendingMetadata): boolean {
    return left !== null &&
      left.namespace === right.namespace &&
      left.operation === right.operation &&
      left.request_id === right.request_id &&
      left.created_at === right.created_at;
  }

  function forget(actorId: string) {
    retained.delete(actorKey(actorId));
    recoveryByActor.delete(actorKey(actorId));
  }

  function clearTerminal(
    transaction: PendingJournalTransaction,
    actorId: string,
    pending: PendingMetadata,
  ) {
    try {
      transaction.removeMatching(pending.request_id);
    } catch {
      throw new AmbiguousCommandError();
    }
    forget(actorId);
  }
```

- [ ] **Step 5: Move every command lifecycle into `withExclusive`**

Implement `execute` with this shape:

```ts
return dependencies.journal.withExclusive(actorId, async (transaction) => {
  if (transaction.read() !== null) throw new InvalidPendingJournalError();
  transaction.begin(pending);
  retained.set(actorKey(actorId), { pending, command });

  const outcome = await attempt(pending, command);
  clearTerminal(transaction, actorId, pending);
  if (outcome.kind === "rejected") throw outcome.error;
  return outcome.response;
});
```

Implement `recover` with this exact transaction flow:

```ts
async recover(actorId: string): Promise<RecoveryState> {
  try {
    return await dependencies.journal.withExclusive(actorId, async (transaction) => {
      const pending = transaction.read();
      if (pending === null) {
        forget(actorId);
        return { kind: "clear" };
      }

      const key = actorKey(actorId);
      recoveryByActor.set(key, { kind: "checking", pending });
      let response: unknown;
      try {
        response = await recoverCall(pending);
      } catch {
        const unresolved = { kind: "unresolved", pending } as const;
        recoveryByActor.set(key, unresolved);
        return unresolved;
      }

      const decoded = recoveryData(response);
      if (decoded === null) {
        const unresolved = { kind: "unresolved", pending } as const;
        recoveryByActor.set(key, unresolved);
        return unresolved;
      }
      if (decoded.state === "applied") {
        try {
          clearTerminal(transaction, actorId, pending);
          return { kind: "applied", pending };
        } catch {
          const unresolved = { kind: "unresolved", pending } as const;
          recoveryByActor.set(key, unresolved);
          return unresolved;
        }
      }

      const memory = retained.get(key);
      const next = memory !== undefined && samePending(memory.pending, pending)
        ? { kind: "retryable", pending } as const
        : { kind: "body_lost", pending } as const;
      recoveryByActor.set(key, next);
      return next;
    });
  } catch {
    return { kind: "invalid_journal" };
  }
}
```

Implement retry exactly as:

```ts
async retryConfirmedAbsent(actorId: string): Promise<RetryOutcome> {
  return dependencies.journal.withExclusive(actorId, async (transaction) => {
    const key = actorKey(actorId);
    const recovery = recoveryByActor.get(key);
    const memory = retained.get(key);
    if (recovery?.kind !== "retryable" ||
        memory === undefined ||
        !samePending(transaction.read(), memory.pending) ||
        !samePending(memory.pending, recovery.pending)) {
      throw new Error("재시도할 명령 본문이 없습니다.");
    }

    const outcome = await attempt(memory.pending, memory.command);
    clearTerminal(transaction, actorId, memory.pending);
    return { kind: outcome.kind === "rejected" ? "rejected" : "applied" };
  });
}
```

Implement retirement exactly as an async transaction:

```ts
async retireConfirmedAbsent(actorId: string, confirmation: string): Promise<void> {
  await dependencies.journal.withExclusive(actorId, (transaction) => {
    const key = actorKey(actorId);
    const recovery = recoveryByActor.get(key);
    if (recovery?.kind !== "body_lost" ||
        confirmation !== "보류 명령 폐기" ||
        !samePending(transaction.read(), recovery.pending)) {
      throw new Error("명시적 폐기 확인이 필요합니다.");
    }
    transaction.removeMatching(recovery.pending.request_id);
    forget(actorId);
  });
}
```

Do not hold a second or nested Web Lock. Do not persist the retained command or response.

- [ ] **Step 6: Run runner GREEN and interim focused count**

Run from `web`:

```bash
npm test -- src/features/recovery/command-runner.test.ts
npm test -- src/api/owner-settings-api.test.ts src/config/env.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts
```

Expected:

- runner: 11/11;
- five-file interim: 60/60;
- no command body appears in Local Storage.

- [ ] **Step 7: Record a no-commit checkpoint**

Run `git diff --check` and prove the target index remains empty. Do not commit.

---

### Task 4: Make same-actor recovery reachable and logout storage-proof

**Files:**
- Modify: `web/src/app/AppController.test.ts`
- Modify: `web/src/app/AppController.ts`

**Interfaces:**
- Consumes: `RetryOutcome`, async retirement, and existing `AuthPort.getSession`.
- Preserves: the current `AppSnapshot` wire and Korean recovery controls.
- Adds no auth-storage adapter or new UI component.

- [ ] **Step 1: Replace the mock-only retry reachability setup with a stateful same-actor transition**

Replace the body of `retries a retained confirmed-absent command from persisted recovery before unblocking` with:

```ts
    const pending = { namespace: "selling_workflow", operation: "create_selling_case", request_id: OWNER, created_at: "2026-01-02T03:04:05Z" } as const;
    let retained = false;
    const commandRunner = {
      clearMemory: vi.fn(() => { retained = false; }),
      pending: vi.fn().mockReturnValueOnce(null).mockReturnValueOnce(pending).mockReturnValue(null),
      recover: vi.fn(async () => retained
        ? { kind: "retryable", pending } as const
        : { kind: "body_lost", pending } as const),
      retryConfirmedAbsent: vi.fn().mockResolvedValue({ kind: "applied" }),
      retireConfirmedAbsent: vi.fn(),
    };
    const { controller, emit } = harness({ commandRunner });
    render(createElement(AppControllerProvider, { controller, children: createElement(ConfiguredApp) }));
    await act(async () => controller.start());
    retained = true;
    const clearCallsBeforeSameActor = commandRunner.clearMemory.mock.calls.length;

    emit("TOKEN_REFRESHED", session(OWNER));
    await vi.waitFor(() => expect(controller.getSnapshot()).toMatchObject({
      phase: "recovery",
      recovery: { kind: "retryable" },
    }));
    expect(commandRunner.clearMemory).toHaveBeenCalledTimes(clearCallsBeforeSameActor);

    await userEvent.click(screen.getByRole("button", { name: "같은 요청으로 재시도" }));
    expect(commandRunner.retryConfirmedAbsent).toHaveBeenCalledExactlyOnceWith(OWNER);
    await vi.waitFor(() => expect(controller.getSnapshot().phase).toBe("ready"));
```

- [ ] **Step 2: Add two controller tests**

Add one test that covers both terminal and ambiguous retry outcomes:

```ts
  it("revalidates terminal retry rejection but keeps an ambiguous retry unresolved", async () => {
    const pending = { namespace: "selling_workflow", operation: "create_selling_case", request_id: OWNER, created_at: "2026-01-02T03:04:05Z" } as const;
    const terminalRunner = {
      clearMemory: vi.fn(), pending: vi.fn().mockReturnValueOnce(pending).mockReturnValue(null),
      recover: vi.fn().mockResolvedValue({ kind: "retryable", pending }),
      retryConfirmedAbsent: vi.fn().mockResolvedValue({ kind: "rejected" }), retireConfirmedAbsent: vi.fn(),
    };
    const terminal = harness({ commandRunner: terminalRunner }).controller;
    await terminal.start();
    await terminal.retryRecovery();
    await vi.waitFor(() => expect(terminal.getSnapshot()).toMatchObject({
      phase: "ready",
      recovery: null,
      pending: null,
    }));

    const ambiguousRunner = {
      clearMemory: vi.fn(), pending: vi.fn().mockReturnValue(pending),
      recover: vi.fn().mockResolvedValue({ kind: "retryable", pending }),
      retryConfirmedAbsent: vi.fn().mockRejectedValue(new AmbiguousCommandError()), retireConfirmedAbsent: vi.fn(),
    };
    const ambiguous = harness({ commandRunner: ambiguousRunner }).controller;
    await ambiguous.start();
    await ambiguous.retryRecovery();
    expect(ambiguous.getSnapshot()).toMatchObject({
      phase: "recovery",
      recovery: { kind: "unresolved", pending },
      pending,
    });
  });
```

Import `AmbiguousCommandError` from the command runner for this regression.

Add one loop-based logout failure test so the test count increases by one, not by the number of cases:

```ts
  it("keeps logout fenced when local session absence is not proven", async () => {
    const cases = [
      { signOut: { error: new Error("server") }, proof: { data: { session: session() }, error: null } },
      { signOut: { error: null }, proof: { data: { session: null }, error: new Error("storage") } },
    ];
    for (const currentCase of cases) {
      const current = harness();
      current.auth.getSession
        .mockResolvedValueOnce({ data: { session: session() }, error: null })
        .mockResolvedValueOnce(currentCase.proof);
      current.auth.signOut.mockResolvedValueOnce(currentCase.signOut);
      await current.controller.start();
      await current.controller.logout();

      expect(current.controller.getSnapshot()).toMatchObject({
        phase: "unavailable",
        actorId: null,
        canMutateDecision: false,
        canMutateOwnerSettings: false,
        message: "로그아웃 상태를 확인할 수 없습니다",
      });
      current.emit("TOKEN_REFRESHED", session(OTHER));
      await Promise.resolve();
      expect(current.controller.getSnapshot()).toMatchObject({
        phase: "unavailable",
        actorId: null,
      });
      await current.controller.login("owner@example.test", "synthetic-password");
      await vi.waitFor(() => expect(current.controller.getSnapshot()).toMatchObject({
        phase: "ready",
        actorId: OWNER,
      }));
    }
  });
```

Modify the existing broad transition test so its first `getSession` returns the owner and its logout proof read returns a null session:

```ts
auth.getSession
  .mockResolvedValueOnce({ data: { session: session() }, error: null })
  .mockResolvedValueOnce({ data: { session: session() }, error: null })
  .mockResolvedValueOnce({ data: { session: null }, error: null });
```

The first two values cover the initial and post-refresh starts; the third is
the logout proof. The test must still expect normal signed-out state only after
successful local sign-out plus that null-session proof.

- [ ] **Step 3: Run controller RED**

Run from `web`:

```bash
npm test -- src/app/AppController.test.ts
```

Expected: RED because same-actor application currently clears retained memory, terminal retry rejection has no discriminated behavior, logout publishes signed-out before proof, and late callbacks are not fenced.

- [ ] **Step 4: Split transition clearing by identity boundary**

Update the runner type import and change `CommandMemoryPort` to consume
`RetryOutcome` and async retirement:

```ts
import type { RecoveryState, RetryOutcome } from "../features/recovery/command-runner";

retryConfirmedAbsent(actorId: string): Promise<RetryOutcome>;
retireConfirmedAbsent(actorId: string, confirmation: string): Promise<void>;
```

Add:

```ts
private logoutFence = false;

private beginTransition(clearCommandMemory: boolean) {
  this.generation += 1;
  this.dependencies.sensitiveState.clearAll();
  if (clearCommandMemory) this.dependencies.commandRunner.clearMemory();
}

private publishSignedOut(message: string | null = null) {
  this.beginTransition(true);
  this.publish({ ...SIGNED_OUT, message });
}

private publishLogoutUnavailable() {
  this.beginTransition(true);
  this.publish({
    ...SIGNED_OUT,
    phase: "unavailable",
    message: "로그아웃 상태를 확인할 수 없습니다",
  });
}
```

In `applySession`, compute `actorId` first, then call:

```ts
this.beginTransition(this.snapshot.actorId !== actorId);
```

This clears old-actor or initial memory but preserves same-actor memory. Keep sensitive DTO clearing unconditional. Use `beginTransition(false)` in same-actor recovery revalidation. Use `beginTransition(true)` for page show, offline/transport loss, authentication failure, logout, and disposal.

- [ ] **Step 5: Consume terminal retry and verify remaining metadata on ambiguity**

On a terminal retry outcome, always revalidate. On catch, inspect `commandRunner.pending(actorId)`:

```ts
try {
  await this.dependencies.commandRunner.retryConfirmedAbsent(current.actorId);
} catch {
  if (actionEpoch !== this.authEpoch) return;
  let stillPending: PendingMetadata | { readonly invalid: true } | null;
  try {
    stillPending = this.dependencies.commandRunner.pending(current.actorId);
  } catch {
    stillPending = { invalid: true };
  }
  if (stillPending !== null &&
      !("invalid" in stillPending) &&
      stillPending.request_id === current.recovery.pending.request_id) {
    this.publish({ ...current, recovery: { kind: "unresolved", pending: current.recovery.pending } });
    return;
  }
}
if (actionEpoch === this.authEpoch) await this.revalidateAfterRecovery(current.actorId);
```

Await `retireConfirmedAbsent` before revalidation.

- [ ] **Step 6: Add the logout fence and storage-backed proof**

In the auth callback:

```ts
if (this.logoutFence) {
  if (event === "SIGNED_OUT") {
    this.authEpoch += 1;
    this.logoutFence = false;
    this.publishSignedOut();
  }
  return;
}
```

Outside the fence, retain the existing auth-epoch behavior for normal `SIGNED_OUT`, null session, refresh, and actor changes.

Implement logout:

```ts
async logout(): Promise<void> {
  const logoutEpoch = ++this.authEpoch;
  this.logoutFence = true;
  this.beginTransition(true);
  this.publish({ ...SIGNED_OUT, phase: "loading", message: "로그아웃 상태를 확인하고 있습니다" });

  try {
    const result = await this.dependencies.auth.signOut({ scope: "local" });
    if (!this.logoutFence || logoutEpoch !== this.authEpoch) return;
    const proof = await this.dependencies.auth.getSession();
    if (!this.logoutFence || logoutEpoch !== this.authEpoch) return;
    if (result.error === null && proof.error === null && proof.data.session === null) {
      this.logoutFence = false;
      this.publishSignedOut();
      return;
    }
  } catch {
    if (!this.logoutFence || logoutEpoch !== this.authEpoch) return;
  }
  this.publishLogoutUnavailable();
}
```

After `bootstrapSession` receives `result` and passes its auth-epoch check, add:

```ts
if (this.logoutFence) {
  if (result.error === null && result.data.session === null) {
    this.logoutFence = false;
    this.publishSignedOut();
  } else {
    this.publishLogoutUnavailable();
  }
  return;
}
```

The `getSession()` throw path must honor the same fence before it can publish:

```ts
} catch {
  if (authEpoch !== this.authEpoch) return;
  if (this.logoutFence) this.publishLogoutUnavailable();
  else this.publishSignedOut("세션을 확인할 수 없습니다");
  return;
}
```

Thus a thrown proof read cannot expose the ordinary signed-out state.

In `login`, remember whether the controller was fenced. Do not lower the fence
while the password request is pending:

```ts
const wasLogoutFenced = this.logoutFence;
```

On thrown or invalid login while `wasLogoutFenced` is true, call
`publishLogoutUnavailable`; otherwise retain the existing fixed Korean login
failure. Immediately before applying a returned valid session, lower the
fence:

```ts
this.logoutFence = false;
await this.applySession(result.data.session, authEpoch);
```

No other in-page path lowers it. Replace `dispose` with:

```ts
dispose(): void {
  this.authEpoch += 1;
  this.beginTransition(true);
  this.subscription?.unsubscribe();
  this.subscription = null;
  this.listeners.clear();
}
```

Do not add `pagehide`, HMR, root-unmount, or new listener behavior.

- [ ] **Step 7: Run controller and exact focused GREEN**

Run from `web`:

```bash
npm test -- src/app/AppController.test.ts
npm test -- src/api/owner-settings-api.test.ts src/config/env.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
```

Expected:

- controller: 19/19;
- focused: 6 files, 79/79;
- the same-actor test reaches `retryable` without a mock that returns it unconditionally;
- definitive rejection returns to ready/revalidated state;
- failed or indeterminate logout remains unavailable and ignores late sessions.

- [ ] **Step 8: Record a no-commit checkpoint**

Run `git diff --check` and prove the index remains empty. Do not commit.

---

### Task 5: Reverify, review, commit, and request Operator2 verdict

**Files:**
- Verify: all 17 existing Task 3 paths.
- Commit: exactly the same 17 paths after all gates and reviews pass.
- Publish: one canonical Pipeline verify-request assigned to Operator2.

**Interfaces:**
- Consumes: Task 1 through Task 4 GREEN bytes and all immutable finding refs.
- Produces: one local combined Task 3 target commit and one immutable Operator2 verify-request.

- [ ] **Step 1: Run the exact focused, type, full, and build gates**

Run from `web`, one command at a time:

```bash
npm test -- src/api/owner-settings-api.test.ts src/config/env.test.ts src/features/auth/session.test.ts src/features/recovery/pending-journal.test.ts src/features/recovery/command-runner.test.ts src/app/AppController.test.ts
npm run typecheck
npm run test
npm run build:ci
```

Expected:

- focused: 6 files, 79/79;
- typecheck: PASS;
- complete: 11 files, 140/140;
- Vite build and `check:dist`: PASS.

Any count mismatch is a hard stop. Do not rewrite the route count after execution.

- [ ] **Step 2: Run source, persistence, transport, and generated-artifact audits**

Run from the target worktree:

```bash
rg -n "localStorage|sessionStorage|indexedDB|CacheStorage|caches\\.|JSON\\.stringify\\(" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
rg -n "\\.rpc\\(|\\[.*rpc.*\\]|fetch\\(|XMLHttpRequest|sendBeacon|\\.from\\(" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
rg -n "eval\\(|Function\\(|Fun.*ction|dangerouslySetInnerHTML" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
rg -n "create_ppl_formula_version|approve_ppl_formula_version|create_ppl_risk_policy|approve_ppl_risk_policy|activate_ppl_policy_pair|record_ppl_initial_format_ruling|approve_ppl_offer_import" web/src
rg -n "console\\.|logger\\.|signup|sign up|user switcher|사용자 전환|회원가입" web/src --glob '*.ts' --glob '*.tsx' --glob '!*.test.*'
```

Expected:

- Local Storage only in `pending-journal.ts`; Session Storage only in the auth adapter/Supabase wiring; no IndexedDB or Cache Storage.
- Production RPC calls only in the three exact API adapters; no raw direct transport or `.from(` call.
- No dynamic-code or raw-HTML production sink.
- No operations-only name, logging, signup, or user-switcher production surface.

Run the compiled guard through `npm run build:ci`; source grep is inventory evidence, not a substitute for the executable structural checks.

- [ ] **Step 3: Recompute immutable contracts and repository gates**

Run from the target worktree:

```bash
shasum -a 256 docs/domain/ppl-offer-api-v1.md docs/domain/selling-package-api-v1.md docs/domain/owner-settings-api-v1.md
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git status --short
```

Expected hashes:

```text
1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6
cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40
```

Also require target smoke PASS, diff syntax PASS, empty index, exactly 17 WIP paths, unchanged `web/src/config/env.test.ts`, and unchanged `web/src/test/synthetic-wire.ts`.

- [ ] **Step 4: Obtain two fresh final-byte reviews**

Director obtains:

1. specification/abuse review of all 17 live paths, explicitly covering all seven Important findings, the two accepted Minor corrections, the rejected `alg` requirement, the deferred lifecycle-listener Minor, constant reconstruction limits, source-wide RPC/raw-transport abuse, full-lock inter-tab races, same-actor recovery, terminal retry, logout storage proof, and late callbacks;
2. code-quality review of the same SHA set and live unstaged bytes, covering types, lock nesting, timeout behavior, storage failure, async retirement, actor epochs, test non-vacuity, and exact path/count contracts.

Every Critical or Important finding is resolved test-first within the eight correction files or causes another truthful stop. Do not expand to `main.tsx`, a ninth correction file, or an 18th path without a new design and route. Preserve every finding and disposition.

After any correction, repeat Steps 1 through 3 on the new final bytes and obtain fresh final-byte conclusions.

- [ ] **Step 5: Stage the exact 17 paths and create the one target commit**

Only after both reviews and every gate pass:

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

Expected: cached inventory is exactly those 17 paths, cached diff check passes, and one new commit is created on `codex/ppl-offer-decision-m1`.

- [ ] **Step 6: Publish the canonical immutable verify-request**

Director returns to `/Users/hyungkoookkim/Pipeline` and uses the fixed writer once. The verify-request must bind:

- this plan commit and design `035fc1e75bc2eefcf01ec10ee4b00f49458057f3`;
- the superseding correction route;
- target repository, worktree, branch, immutable base, and new head;
- all 17 actual paths and the eight correction-file boundary;
- Director and Operator2 seat/model identities;
- each preserved Important and Minor finding with disposition;
- focused 79/79, complete 140/140, typecheck, build, artifact/source audits, three hashes, smoke, scope, and closed-file evidence;
- both final-byte reviews; and
- every excluded side effect.

Director reuses the existing compatible Operator2 task, sends the exact committed trigger once, monitors without duplicate dispatch, and stops for GO/NITS/FAIL.

No merge or push follows from this plan. After committed Operator2 GO, Coordinator must publish a separate exact local-merge route before any integration action.
