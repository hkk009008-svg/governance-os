# Task 3 Artifact-Scanner Resource Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace unsafe whole-bundle TypeScript tokenization with a forward-only closed constant recognizer that preserves every Task 1 security finding and lets the real bundle pass under Node's ordinary heap.

**Architecture:** Keep the contiguous semantic-JWT classifier, but stream additional values from a finite constant grammar that is independent of whole-program JavaScript lexical state. Use an explicit frame stack, input-derived work/value bounds, and a conservative exact-identifier pass for source safety; retain the TypeScript scanner only for bounded literal decoding and pre-existing structural checks, with deterministic non-progress failure.

**Tech Stack:** Node.js ESM, TypeScript 7 unstable scanner for isolated literal decoding and existing structural checks, Vitest 4, Vite 8, npm.

## Global Constraints

- Binding design: `docs/superpowers/specs/2026-07-20-task3-artifact-scanner-resource-correction-design.md@60fa6fbe425ed0cd8d9e5dc377b94a2a0f6ce281`.
- Binding blocker: `coordination/mailbox/sent/2026-07-20T10-36-43Z-director-to-coordinator-coordination.md@7543b34f10e80490f302d1085e16cd6c5019b0f7`.
- Target worktree: `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`.
- Accepted and current target HEAD: `8376ed1fdca13001d2c5f1f1dd5bc452b596d04e`.
- Modify only `web/scripts/check-pwa-dist.mjs` and `web/src/api/owner-settings-api.test.ts` in this correction.
- Preserve exactly 17 routed WIP paths, an empty index, the nine protected WIP hashes, and both closed-file hashes.
- Preserve exactly 28 tests in `owner-settings-api.test.ts`; extend existing cases only.
- Add no path, package, lockfile, dependency, framework, configuration, build flag, generated fixture, heap override, allowlist, or occurrence-count assumption.
- `e30.e30.c2ln`, populated signatures, and empty signatures remain credential-like.
- A resource/progress violation fails closed; it never becomes a whole-artifact safe result.
- Tasks 2 through 4 remain untouched until this correction passes focused 28/28 and real `build:ci` with `NODE_OPTIONS` unset.
- Do not stage or create an interim target commit. The accepted Task 3 route still permits only one combined target commit after all Tasks 1 through 4, every gate, and both fresh final-byte reviews pass.
- No merge, push, target-main update, cursor consumption, protocol lock action, cleanup, reset, rebase, amend, service lifecycle, managed database/Auth action, private-data access, activation, booking, spend, deployment, or production effect.

---

### Task 1: Pin deterministic regex-before-candidate failures

**Files:**
- Modify: `web/src/api/owner-settings-api.test.ts:221-243`
- Modify: `web/src/api/owner-settings-api.test.ts:307-345`
- Modify: `web/src/api/owner-settings-api.test.ts:347-352`
- Modify: `web/src/api/owner-settings-api.test.ts:420-452`
- Test: `web/src/api/owner-settings-api.test.ts`

**Interfaces:**
- Consumes: current `OwnerSourceGuard.assertProductionSourceSafety(source, allowRpc?, path?)` and `OwnerSourceGuard.assertBuiltContentSafety(source, path?)`.
- Produces: four deterministic regressions that the current bytes accept without hanging, while preserving the file's 28-test count.

- [ ] **Step 1: Extend the existing dynamic-code test with a regex-prefixed computed sink**

In `rejects dynamic code execution and construction inside the factory`, keep the existing `statements` loop and append this assertion after `expect(accepted).toEqual([])`:

```ts
    expect(() => guard.assertProductionSourceSafety(
      'const marker = /[`]/; globalThis["Fun" + "ction"]("return hidden")()',
      true,
      "owner-settings-api.ts",
    )).toThrow("dynamic code sink");
```

This calls the source-wide policy directly. Do not route this fixture through
`assertOwnerRpcInventory`: the blocked scanner currently rejects that form for
the unrelated structural error `owner adapter function structure is invalid`,
which would make the security regression vacuous.

- [ ] **Step 2: Extend the existing ordinary-source test with the same lexical prefix**

In the rejection array inside
`keeps raw operations, persistence, network, and owner imports out of ordinary sources`,
append this exact string:

```ts
      'const marker = /[`]/; globalThis["Fun" + "ction"]("return client")()',
```

Keep the existing loop and its `toThrow()` assertion unchanged.

- [ ] **Step 3: Pin deterministic failure for a desynchronized structural scan**

In `rejects template and unprovable dynamic owner adapter imports`, append:

```ts
    expect(() => guard.assertOwnerImportSafety(
      'const marker = /[`]/; import("./local")',
      false,
      "src/app/Bypass.ts",
    )).toThrow("source scanner made no progress");
```

The current blocked bytes accept this source because the regex backtick hides
the later import from the context-free scanner. The corrected structural scan
must reject it deterministically as unterminated/non-progressing input.

- [ ] **Step 4: Extend the existing semantic-JWT test with a regex-prefixed joined token**

After `signature` is defined in
`distinguishes semantic JWTs from ordinary dotted built code`, add:

```ts
    const regexPrefixedJoinedJwt =
      'const marker = /[`]/; const token = ["' +
      [header, payload, signature].join('", "') +
      '"].join(".");';
```

Append `regexPrefixedJoinedJwt` to the existing `builtSource` rejection array.
The final positive array remains:

```ts
    for (const builtSource of [
      `${header}.${payload}.${signature}`,
      `${header}.${payload}.`,
      `const token = "${header}" + "." + "${payload}" + "." + "${signature}";`,
      `const token = ["${header}", "${payload}", "${signature}"].join(".");`,
      `const token = ["${header}", "${payload}", ""].join(".");`,
      `const token = \`${header}\${"."}${payload}\${"."}${signature}\`;`,
      regexPrefixedJoinedJwt,
      "e30.e30.c2ln",
    ]) {
      expect(() => guard.assertBuiltContentSafety(builtSource, "assets/index.js"))
        .toThrow("forbidden built content");
    }
```

- [ ] **Step 5: Add safe stress and malformed-input assertions to the same JWT test**

After the existing allowed-fixture loop, add:

```ts
    const safeMinified = Array.from(
      { length: 512 },
      (_, index) => `const r${index}=/[\`]/;const value${index}="safe_${index}";`,
    ).join("");
    expect(() => guard.assertBuiltContentSafety(safeMinified, "assets/safe.js"))
      .not.toThrow();

    for (const malformed of [
      'const value = "unterminated',
      'const value = `safe${"tail"',
      'const value = ["safe", "tail"].join("',
    ]) {
      expect(() => guard.assertBuiltContentSafety(malformed, "assets/malformed.js"))
        .not.toThrow();
    }
```

These assertions do not add a Vitest case. They prove bounded completion and
malformed-candidate handling inside the existing semantic-JWT contract.

- [ ] **Step 6: Run the named RED selector**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts -t "rejects dynamic code execution|keeps raw operations|rejects template and unprovable dynamic owner adapter imports|distinguishes semantic JWTs"
```

Expected: RED with the four selected cases failing and 24 cases skipped.
The failures must show that the regex-prefixed computed `Function` fixtures do
not throw, the regex-prefixed import does not throw, and
`regexPrefixedJoinedJwt` does not throw. A timeout, abort, heap failure, or
unrelated owner-structure error is not acceptable RED evidence.

- [ ] **Step 7: Preserve the no-commit checkpoint**

Run from the target worktree:

```bash
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git status --porcelain=v1 -uall
```

Expected: diff check passes, the index output is empty, and status contains the
same 17 routed paths only.

---

### Task 2: Replace whole-input constant tokenization with a bounded recognizer

**Files:**
- Modify: `web/scripts/check-pwa-dist.mjs:14-211`
- Test: `web/src/api/owner-settings-api.test.ts`

**Interfaces:**
- Consumes: `createScanner`, `LanguageVariant`, `SyntaxKind`, `fail`, `containsContiguousSemanticJwt`, `dynamicCodeNames`, and `rawTransportNames`.
- Produces: internal `closedConstantValues(source: string): Iterable<string>`, `exactIdentifierValues(source: string): Iterable<string>`, deterministic `scanSource(source, path?)`, and unchanged public `assertProductionSourceSafety`, `assertNoRawHtml`, `containsSemanticJwt`, and `assertBuiltContentSafety` signatures.

- [ ] **Step 1: Make every retained TypeScript structural scan fail on non-progress**

Replace `scanSource` with this progress-checked version. It remains for the
existing owner RPC/import/raw-HTML structural checks, but it is no longer used
to enumerate constant roots across a whole artifact.

```js
const scanSource = (source, path = "guard-fixture.ts") => {
  const scanner = createScanner(true, LanguageVariant.Standard, source);
  const tokens = [];
  const templateBraceDepths = [];
  let braceDepth = 0;
  let previousEnd = -1;

  const appendScannerToken = (kind) => {
    const end = scanner.getTokenEnd();
    if (end <= previousEnd || scanner.isUnterminated()) {
      fail(`source scanner made no progress in ${path}`);
    }
    previousEnd = end;
    tokens.push({
      kind,
      text: scanner.getTokenText(),
      value: scanner.getTokenValue(),
    });
  };

  for (let kind = scanner.scan(); kind !== SyntaxKind.EndOfFile; kind = scanner.scan()) {
    appendScannerToken(kind);
    if (kind === SyntaxKind.TemplateHead) {
      templateBraceDepths.push(braceDepth);
    } else if (kind === SyntaxKind.OpenBraceToken) {
      braceDepth += 1;
    } else if (kind === SyntaxKind.CloseBraceToken) {
      const templateDepth = templateBraceDepths.at(-1);
      if (templateDepth !== undefined && braceDepth === templateDepth) {
        const templateKind = scanner.reScanTemplateToken(false);
        appendScannerToken(templateKind);
        if (templateKind === SyntaxKind.TemplateTail) templateBraceDepths.pop();
      } else {
        braceDepth = Math.max(0, braceDepth - 1);
      }
    }
  }
  return tokens;
};
```

- [ ] **Step 2: Delete the whole-input token constant evaluator**

Delete these functions after the new recognizer from Step 3 is present:

```text
constantStringAtom
constantStringExpression
constantTemplate
constantArrayJoin
constantStringRoots
exactConstantNames
```

Keep `isConstantStringToken`; `assertOwnerImportSafety` still uses it for
bounded import/glob structure. Keep `isDynamicCodeToken`; the exact owner RPC
inventory retains its local belt-and-suspenders rejection.

- [ ] **Step 3: Add the forward-only recognizer and exact-identifier pass**

Insert the following implementation after `isConstantStringToken`. The frame
stack is explicit, all parse results have strictly advancing end offsets, and
the work/materialization limits are derived from the inspected input length.

```js
const NO_CHILD = Symbol("no-child");
const CLOSED_PRODUCTION_COUNT = 4;
const CLOSED_TRANSITIONS_PER_STATE = 32;
const CLOSED_MATERIALIZED_PER_CODE_UNIT = 32;
const identifierStart = /[A-Za-z_$]/;
const identifierPart = /[A-Za-z0-9_$]/;

class ClosedConstantRecognizer {
  constructor(source) {
    this.source = source;
    this.memo = new Map();
    this.work = 0;
    this.maxWork = CLOSED_PRODUCTION_COUNT * CLOSED_TRANSITIONS_PER_STATE *
      (source.length + 1);
    this.materialized = 0;
    this.maxMaterialized = CLOSED_MATERIALIZED_PER_CODE_UNIT *
      (source.length + 1);
  }

  spend(amount = 1) {
    this.work += amount;
    if (this.work > this.maxWork) {
      fail("closed constant recognition exceeded its input-derived work bound");
    }
  }

  trivia(start) {
    let cursor = start;
    while (cursor < this.source.length) {
      this.spend();
      const character = this.source[cursor];
      if (/\s/u.test(character)) {
        cursor += 1;
        continue;
      }
      if (this.source.startsWith("//", cursor)) {
        const newline = this.source.indexOf("\n", cursor + 2);
        const end = newline < 0 ? this.source.length : newline + 1;
        this.spend(end - cursor);
        cursor = end;
        continue;
      }
      if (this.source.startsWith("/*", cursor)) {
        const close = this.source.indexOf("*/", cursor + 2);
        if (close < 0) return this.source.length;
        this.spend(close + 2 - cursor);
        cursor = close + 2;
        continue;
      }
      break;
    }
    return cursor;
  }

  append(left, right) {
    if (left.length + right.length > this.source.length) {
      fail("closed constant reconstruction exceeds inspected input length");
    }
    return left + right;
  }

  join(values, separator) {
    const length = values.reduce((total, value) => total + value.length, 0) +
      Math.max(0, values.length - 1) * separator.length;
    if (length > this.source.length) {
      fail("closed constant reconstruction exceeds inspected input length");
    }
    return values.join(separator);
  }

  decodeLiteral(start, end, expectedKinds) {
    const literal = this.source.slice(start, end);
    const scanner = createScanner(true, LanguageVariant.Standard, literal);
    const kind = scanner.scan();
    const value = scanner.getTokenValue();
    if (!expectedKinds.has(kind) || scanner.isUnterminated() ||
        scanner.getTokenEnd() !== literal.length ||
        scanner.scan() !== SyntaxKind.EndOfFile) {
      return undefined;
    }
    return value;
  }

  decodeTemplateChunk(start, end) {
    const literal = `\`${this.source.slice(start, end)}\``;
    const scanner = createScanner(true, LanguageVariant.Standard, literal);
    const kind = scanner.scan();
    const value = scanner.getTokenValue();
    if (kind !== SyntaxKind.NoSubstitutionTemplateLiteral ||
        scanner.isUnterminated() || scanner.getTokenEnd() !== literal.length ||
        scanner.scan() !== SyntaxKind.EndOfFile) {
      return undefined;
    }
    return value;
  }

  quoted(start) {
    const quote = this.source[start];
    let cursor = start + 1;
    while (cursor < this.source.length) {
      this.spend();
      const character = this.source[cursor];
      if (character === "\\") {
        cursor += 2;
        continue;
      }
      if (character === quote) {
        const end = cursor + 1;
        const value = this.decodeLiteral(
          start,
          end,
          new Set([SyntaxKind.StringLiteral]),
        );
        return value === undefined ? null : { value, end };
      }
      if (character === "\n" || character === "\r") return null;
      cursor += 1;
    }
    return null;
  }

  frame(kind, start) {
    const common = { kind, start, key: `${kind}:${start}`, child: NO_CHILD };
    if (kind === "expression") {
      return { ...common, state: "first", cursor: start, value: "" };
    }
    if (kind === "atom") {
      return { ...common, state: "start", cursor: start };
    }
    if (kind === "template") {
      return {
        ...common,
        state: "chunk",
        cursor: start + 1,
        chunkStart: start + 1,
        value: "",
      };
    }
    return {
      ...common,
      state: "element-or-end",
      cursor: start + 1,
      values: [],
    };
  }

  remember(key, result) {
    if (this.memo.has(key)) return;
    if (result !== null) {
      this.materialized += result.value.length;
      if (this.materialized > this.maxMaterialized) {
        fail("closed constant recognition exceeded its input-derived value bound");
      }
    }
    this.memo.set(key, result);
  }

  parse(kind, start) {
    const rootKey = `${kind}:${start}`;
    if (this.memo.has(rootKey)) return this.memo.get(rootKey);

    const stack = [this.frame(kind, start)];
    let delivery = NO_CHILD;

    const request = (childKind, childStart) => {
      const key = `${childKind}:${childStart}`;
      if (this.memo.has(key)) {
        delivery = this.memo.get(key);
      } else {
        stack.push(this.frame(childKind, childStart));
      }
    };

    while (stack.length > 0) {
      this.spend();
      const current = stack.at(-1);
      if (delivery !== NO_CHILD) {
        current.child = delivery;
        delivery = NO_CHILD;
      }

      const finish = (result) => {
        stack.pop();
        this.remember(current.key, result);
        delivery = result;
      };
      const takeChild = () => {
        const child = current.child;
        current.child = NO_CHILD;
        return child;
      };

      if (current.kind === "expression") {
        if (current.state === "first") {
          current.state = "after-first";
          request("atom", this.trivia(current.cursor));
          continue;
        }
        if (current.state === "after-first") {
          const child = takeChild();
          if (child === null) {
            finish(null);
            continue;
          }
          current.value = child.value;
          current.cursor = child.end;
          current.state = "operator";
          continue;
        }
        if (current.state === "operator") {
          const operator = this.trivia(current.cursor);
          if (this.source[operator] !== "+") {
            finish({ value: current.value, end: current.cursor });
            continue;
          }
          current.state = "after-next";
          request("atom", this.trivia(operator + 1));
          continue;
        }
        const child = takeChild();
        if (child === null) {
          finish(null);
          continue;
        }
        current.value = this.append(current.value, child.value);
        current.cursor = child.end;
        current.state = "operator";
        continue;
      }

      if (current.kind === "atom") {
        if (current.state === "start") {
          current.cursor = this.trivia(current.cursor);
          const character = this.source[current.cursor];
          if (character === "\"" || character === "'") {
            finish(this.quoted(current.cursor));
            continue;
          }
          if (character === "`") {
            current.state = "forward-child";
            request("template", current.cursor);
            continue;
          }
          if (character === "[") {
            current.state = "forward-child";
            request("array", current.cursor);
            continue;
          }
          if (character === "(") {
            current.state = "parenthesized";
            request("expression", current.cursor + 1);
            continue;
          }
          finish(null);
          continue;
        }
        const child = takeChild();
        if (child === null) {
          finish(null);
          continue;
        }
        if (current.state === "forward-child") {
          finish(child);
          continue;
        }
        const close = this.trivia(child.end);
        if (this.source[close] !== ")") {
          finish(null);
          continue;
        }
        finish({ value: child.value, end: close + 1 });
        continue;
      }

      if (current.kind === "template") {
        if (current.state === "after-expression") {
          const child = takeChild();
          if (child === null) {
            finish(null);
            continue;
          }
          const close = this.trivia(child.end);
          if (this.source[close] !== "}") {
            finish(null);
            continue;
          }
          current.value = this.append(current.value, child.value);
          current.cursor = close + 1;
          current.chunkStart = close + 1;
          current.state = "chunk";
          continue;
        }

        let resolved = false;
        while (current.cursor < this.source.length) {
          this.spend();
          const character = this.source[current.cursor];
          if (character === "\\") {
            current.cursor += 2;
            continue;
          }
          if (character === "`") {
            const chunk = this.decodeTemplateChunk(
              current.chunkStart,
              current.cursor,
            );
            if (chunk === undefined) {
              finish(null);
            } else {
              finish({
                value: this.append(current.value, chunk),
                end: current.cursor + 1,
              });
            }
            resolved = true;
            break;
          }
          if (character === "$" && this.source[current.cursor + 1] === "{") {
            const chunk = this.decodeTemplateChunk(
              current.chunkStart,
              current.cursor,
            );
            if (chunk === undefined) {
              finish(null);
            } else {
              current.value = this.append(current.value, chunk);
              current.state = "after-expression";
              request("expression", current.cursor + 2);
            }
            resolved = true;
            break;
          }
          current.cursor += 1;
        }
        if (!resolved && current.cursor >= this.source.length) finish(null);
        continue;
      }

      if (current.state === "element-or-end") {
        current.cursor = this.trivia(current.cursor);
        if (this.source[current.cursor] === "]") {
          current.cursor += 1;
          current.state = "join";
          continue;
        }
        current.state = "after-element";
        request("expression", current.cursor);
        continue;
      }
      if (current.state === "after-element") {
        const child = takeChild();
        if (child === null) {
          finish(null);
          continue;
        }
        current.values.push(child.value);
        const delimiter = this.trivia(child.end);
        if (this.source[delimiter] === ",") {
          current.cursor = delimiter + 1;
          current.state = "element-or-end";
          continue;
        }
        if (this.source[delimiter] === "]") {
          current.cursor = delimiter + 1;
          current.state = "join";
          continue;
        }
        finish(null);
        continue;
      }
      if (current.state === "join") {
        let cursor = this.trivia(current.cursor);
        if (this.source[cursor] !== ".") {
          finish(null);
          continue;
        }
        cursor = this.trivia(cursor + 1);
        if (!this.source.startsWith("join", cursor) ||
            identifierPart.test(this.source[cursor + 4] ?? "")) {
          finish(null);
          continue;
        }
        cursor = this.trivia(cursor + 4);
        if (this.source[cursor] !== "(") {
          finish(null);
          continue;
        }
        current.state = "after-separator";
        request("expression", cursor + 1);
        continue;
      }
      const separator = takeChild();
      if (separator === null) {
        finish(null);
        continue;
      }
      const close = this.trivia(separator.end);
      if (this.source[close] !== ")") {
        finish(null);
        continue;
      }
      finish({
        value: this.join(current.values, separator.value),
        end: close + 1,
      });
    }

    return delivery === NO_CHILD ? null : delivery;
  }

  *values() {
    for (let index = 0; index < this.source.length; index += 1) {
      this.spend();
      if (!"\"'`([".includes(this.source[index])) continue;
      const expression = this.parse("expression", index);
      if (expression === null) continue;
      const after = this.trivia(expression.end);
      if (this.source[after] === "+") continue;
      yield expression.value;
    }
  }
}

function closedConstantValues(source) {
  return new ClosedConstantRecognizer(source).values();
}

function* exactIdentifierValues(source) {
  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (!identifierStart.test(character) ||
        identifierPart.test(source[index - 1] ?? "")) {
      continue;
    }
    let cursor = index + 1;
    while (cursor < source.length && identifierPart.test(source[cursor])) {
      cursor += 1;
    }
    yield source.slice(index, cursor);
    index = cursor - 1;
  }
}
```

Do not export the recognizer. The behavioral tests exercise its existing
public consumers. Do not add a child process, timeout, worker, parser package,
or bundle-specific fast path.

- [ ] **Step 4: Point source safety, raw-HTML safety, and semantic JWTs at the new streams**

Replace `assertProductionSourceSafety`, `assertNoRawHtml`, and
`containsSemanticJwt` with these bodies:

```js
function rejectSourceName(name, allowRpc, path) {
  if (dynamicCodeNames.has(name)) {
    fail(`dynamic code sink is forbidden in ${path}`);
  }
  if (rawTransportNames.has(name)) {
    fail(`raw transport is forbidden in ${path}`);
  }
  if (!allowRpc && name === "rpc") {
    fail(`direct RPC is forbidden in ordinary source ${path}`);
  }
}

export function assertProductionSourceSafety(
  source,
  allowRpc = false,
  path = "guard-fixture.ts",
) {
  for (const name of exactIdentifierValues(source)) {
    rejectSourceName(name, allowRpc, path);
  }
  for (const name of closedConstantValues(source)) {
    rejectSourceName(name, allowRpc, path);
  }
}

export function assertNoRawHtml(source, path = "guard-fixture.ts") {
  const tokens = scanSource(source, path);
  if (tokens.some((token) =>
    tokenIs(token, SyntaxKind.Identifier, rawHtmlProperty))) {
    fail(`${rawHtmlProperty} is forbidden in production source ${path}`);
  }
  for (const value of closedConstantValues(source)) {
    if (value === rawHtmlProperty) {
      fail(`${rawHtmlProperty} is forbidden in production source ${path}`);
    }
  }
}

export function containsSemanticJwt(source) {
  if (containsContiguousSemanticJwt(source)) return true;
  for (const value of closedConstantValues(source)) {
    if (containsContiguousSemanticJwt(value)) return true;
  }
  return false;
}
```

Keep `assertNoOwnerDynamicCode` delegating to
`assertProductionSourceSafety(source, true, path)`. Keep
`assertOwnerRpcInventory` invoking the same source-safety helper before its
structural scan. Pass the real `path` argument into structural `scanSource`
calls where available so any non-progress error identifies its inspected file.

- [ ] **Step 5: Run the named selector to verify GREEN**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts -t "rejects dynamic code execution|keeps raw operations|rejects template and unprovable dynamic owner adapter imports|distinguishes semantic JWTs"
```

Expected: the four selected tests pass and 24 tests are skipped. The computed
source and artifact fixtures must fail for the intended dynamic-code or
forbidden-built-content messages; only the structural import fixture fails for
the stable scanner-progress message.

- [ ] **Step 6: Run the complete owner guard file**

Run from `web`:

```bash
npm test -- src/api/owner-settings-api.test.ts
```

Expected: exactly 28/28 pass. The exact count is binding; do not update it.

- [ ] **Step 7: Run the real build under the ordinary heap**

Run from `web`:

```bash
env -u NODE_OPTIONS npm run build:ci
```

Expected: typecheck passes, Vite reports 79 transformed modules, the generated
JavaScript artifact completes semantic checking, and `dist check passed (2 files)`
appears. No `--max-old-space-size`, environment heap setting, filename/hash
allowlist, or retry is permitted. A synthetic-only GREEN is insufficient.

- [ ] **Step 8: Preserve the no-commit checkpoint**

Run from the target worktree:

```bash
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git status --porcelain=v1 -uall
```

Expected: diff check passes, the index is empty, and exactly the same 17 routed
paths remain. No Task 2, 3, or 4 file has a new modification time from this
resource correction.

---

### Task 3: Re-establish the Task 1 checkpoint and resume the accepted plan

**Files:**
- Verify: `web/scripts/check-pwa-dist.mjs`
- Verify: `web/src/api/owner-settings-api.test.ts`
- Read-only selector input: `web/src/config/env.test.ts`
- Read-only selector input: `web/src/features/auth/session.test.ts`
- Read-only selector input: `web/src/features/recovery/pending-journal.test.ts`
- Read-only selector input: `web/src/features/recovery/command-runner.test.ts`
- Read-only selector input: `web/src/app/AppController.test.ts`

**Interfaces:**
- Consumes: corrected Task 1 guard and the still-unstarted Tasks 2 through 4 in `docs/superpowers/plans/2026-07-20-task3-final-review-corrections.md@d65ea564731c62c27b9cb8c80aa84241571a2f47`.
- Produces: immutable evidence that Task 1 is again eligible to hand off to original-plan Task 2 without a target commit.

- [ ] **Step 1: Run the exact pre-Task-2 focused selector**

Run from `web`:

```bash
npm test -- \
  src/api/owner-settings-api.test.ts \
  src/config/env.test.ts \
  src/features/auth/session.test.ts \
  src/features/recovery/pending-journal.test.ts \
  src/features/recovery/command-runner.test.ts \
  src/app/AppController.test.ts
```

Expected before Tasks 2 through 4 begin: exactly 73/73 pass across six files.
The final 79/79 count remains reserved for the completed original correction
plan.

- [ ] **Step 2: Recheck immutable protected state**

Run from the target worktree:

```bash
shasum -a 256 \
  web/src/api/supabase.ts \
  web/src/app/App.tsx \
  web/src/app/AppContext.tsx \
  web/src/app/sensitive-state.ts \
  web/src/features/auth/LoginView.tsx \
  web/src/features/auth/session.test.ts \
  web/src/features/auth/session.ts \
  web/src/features/recovery/RecoveryPanel.tsx \
  web/src/main.tsx \
  web/src/config/env.test.ts \
  web/src/test/synthetic-wire.ts
```

Require these exact results:

```text
fb43c7c0a459450b14b371776ce68d1158db4c2550e2db497ca513f4c5ce343d  web/src/api/supabase.ts
a31f7cb16dd83c59298ea6601187900eaadb602a4ac437bc3583c3e619e36bb5  web/src/app/App.tsx
1c2906c26ffca496f52351428e80b55ce7a77ec48d3a700a6207c66a00c38fda  web/src/app/AppContext.tsx
590334ca5b7b85237434da72647543e1243f6bfe2faf6dc1058074cf0c6620fc  web/src/app/sensitive-state.ts
649ff35b5f70ae2332f0707aa6952bb7333990ec5f85528d8eb63db6aae3b79a  web/src/features/auth/LoginView.tsx
3d110615fc3068d3f0744047213df0d151b911a0c1bf6c8f0ba20982307398cd  web/src/features/auth/session.test.ts
ec2201383444008c653c81f9b2a19d901ca1bc199e2e084ef74d876cd7d7d3a2  web/src/features/auth/session.ts
1d3de73b702b466cd8dd5f01cd56a0d065c9c96b026054e9f924a85738eaed25  web/src/features/recovery/RecoveryPanel.tsx
2a22dc6fc1a98b5460fc2220a8cd5a4bae6eba14ee319969586203a9f370f9bb  web/src/main.tsx
2b269354e610bfe26a23f6ee8fcd1f01736aca52420faf95601482fecab39ed2  web/src/config/env.test.ts
6ff0fa5fe5a6dd0f18c94647e0cfe32f460353ee6afe502be5c5af2456c27b4d  web/src/test/synthetic-wire.ts
```

Expected: all nine protected WIP hashes and both closed-file hashes remain
exact. Any mismatch stops without staging.

- [ ] **Step 3: Resume only at original-plan Task 2**

Continue at `### Task 2: Replace partial pending-journal locks with one actor transaction`
in the accepted Task 3 plan. Do not repeat original-plan Task 1 and do not
reinterpret its algorithm text as authority to restore whole-bundle
`scanSource` or `constantStringRoots`.

The remaining binding completion sequence is unchanged:

```text
original Task 2 RED/GREEN
original Task 3 RED/GREEN
original Task 4 RED/GREEN
exact final focused selector: 79/79
exact complete suite: 140/140
typecheck and default-heap build:ci
source/artifact audits and three frozen contract hashes
target smoke, diff/scope, protected/closed hashes, empty pre-commit index
two fresh final-byte reviews of all 17 live paths
one combined local target commit
one canonical immutable Operator2 verify-request
```

No target commit, verify-request, Operator2 dispatch, merge, or push occurs at
this checkpoint.
