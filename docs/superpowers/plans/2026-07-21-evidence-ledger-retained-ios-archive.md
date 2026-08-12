# Evidence-Ledger Retained iOS Archive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retain the complete iOS source tree as unsupported archive code while removing every current support, setup, verification, CI, beta, and release claim.

**Architecture:** Change repository-facing truth and the local verification harness only. Keep every tracked path under `ios/` byte-for-byte unchanged, reduce `scripts/ci_local.sh` to the active database/import lanes, and preserve executable GitHub Actions topology while correcting comments.

**Tech Stack:** Markdown, Bash, GitHub Actions YAML comments, existing evidence-ledger Python governance checks.

## Global Constraints

- Bind all target work to parent `1ad4eb2b5550af7c3941aacf08240559a9051193` in `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ios-null`.
- Execute this plan directly in the existing Director task with `superpowers:executing-plans`; do not use a child implementer.
- Modify exactly `README.md`, `ARCHITECTURE.md`, `OPERATIONS.md`, `scripts/ci_local.sh`, and `.github/workflows/ci.yml`.
- Keep every tracked path under `ios/` unchanged. Do not delete, repair, regenerate, build, or test the retained client.
- Do not create, boot, shut down, or delete a simulator. Do not run Xcode, XcodeGen, Swift, or XCTest commands.
- Do not change executable CI job topology; `.github/workflows/ci.yml` changes are comments only.
- Do not change packages, lockfiles, schemas, import behavior, Python code, web code, generated projects, services, or private data.
- Use only repository text and synthetic/local verification. Do not access a private workbook, managed database, or real business values.
- Produce one target commit containing exactly the five allowed paths, then submit its exact actual range to non-author Operator2.
- Target-main integration and every remote-reference change remain separately held.

---

### Task 1: Establish the archive boundary and its non-vacuous RED evidence

**Files:**

- Inspect: `README.md`
- Inspect: `ARCHITECTURE.md`
- Inspect: `OPERATIONS.md`
- Inspect: `scripts/ci_local.sh`
- Inspect: `.github/workflows/ci.yml`

**Interfaces:**

- Consumes: target parent `1ad4eb2b5550af7c3941aacf08240559a9051193` and the approved archive design at `docs/superpowers/specs/2026-07-21-evidence-ledger-retained-ios-archive-design.md@487ca2175b44eb8e436b597bc2e5f2cd7d799ae1`.
- Produces: captured evidence that the unmodified tree still presents iOS as supported and locally verified.

- [ ] **Step 1: Prove the routed worktree is still the clean accepted parent**

Run:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE git diff --exit-code -- ios/
```

Expected: branch `codex/audit-remediation-ios-null`, HEAD exactly `1ad4eb2b5550af7c3941aacf08240559a9051193`, no tracked status entries, and no `ios/` diff.

- [ ] **Step 2: Capture the stale current claims as RED evidence**

Run:

```bash
rg -n "existing read-only iOS client|remains supported|db \+ import \+ ios tests|xcodegen generate" README.md
rg -n "iOS runs locally|no paid macOS runner|SIM_DEVICE|iOS client \(`ios/EvidenceLedger/`\)" ARCHITECTURE.md
rg -n "xcodebuild|xcodegen|SIM_DEVICE|iOS Simulator|iOS lane stays local" OPERATIONS.md
rg -n "xcodebuild|SIM_DEVICE|ios project not generated" scripts/ci_local.sh
rg -n "no paid macOS runner|iOS tests stay local|macos-latest|xcodebuild" .github/workflows/ci.yml
```

Expected: every command prints one or more matches. These matches are the non-vacuous RED condition; the repository still advertises an abandoned surface as current or revivable.

---

### Task 2: Correct the active product and quickstart boundary

**Files:**

- Modify: `README.md`

**Interfaces:**

- Consumes: the user decision that the Windows PWA is the active client and `ios/` is retained unsupported archive source.
- Produces: one current product statement, one archive notice, and a quickstart containing no iOS tooling or command.

- [ ] **Step 1: Replace the opening product description and status**

Use this exact product-boundary text near the top of `README.md`, preserving the existing design/manual links below it:

```markdown
Private system for two Korean home-shopping executives: a trustworthy P&L
system of record and a Windows PWA for the bounded PPL-offer workflow. Every
figure is computed deterministically from the database; every AI answer carries
verifiable, hash-chained evidence; every recommendation is preceded by a
recorded prediction that gets graded against reality.

**Archived source:** `ios/EvidenceLedger/` is retained as unsupported historical
reference code. It is not built, tested, supported, shipped, or included in
beta/release acceptance, and current database compatibility is not asserted.
```

Replace the Korean status sentence with:

```markdown
Status: DB 스키마·가져오기 파이프라인은 현재 검증 대상이며, 활성 사용자 화면과 베타 대상은 Windows PWA입니다. `ios/EvidenceLedger/`는 지원하지 않는 보관용 참고 코드입니다.
```

In the next-slice paragraph, remove the sentence claiming the existing iOS client remains supported. Keep the Windows PWA design and fail-closed product-policy links unchanged.

- [ ] **Step 2: Replace the quickstart with active lanes only**

Use this exact block:

```markdown
## Quickstart (local dev)

    brew install supabase/tap/supabase && brew install --cask docker
    supabase start                         # local stack
    scripts/seed_users.sh <pw1> <pw2>      # the two accounts
    scripts/ci_local.sh                    # db + import verification only
```

Do not leave any Xcode, XcodeGen, simulator, Swift, XCTest, or iOS setup command in `README.md`.

- [ ] **Step 3: Verify the README contract**

Run:

```bash
rg -n "Archived source:|활성 사용자 화면과 베타 대상은 Windows PWA|db \+ import verification only" README.md
rg -n "remains supported|db \+ import \+ ios tests|xcodegen|xcodebuild|Simulator" README.md
```

Expected: the first command prints exactly the new archive/product/quickstart claims; the second exits 1 with no matches.

---

### Task 3: Remove the archived client from recurring local and CI verification

**Files:**

- Modify: `scripts/ci_local.sh`
- Modify: `.github/workflows/ci.yml` (comments only)

**Interfaces:**

- Consumes: the archive boundary from Task 2.
- Produces: a two-lane local harness and unchanged executable GitHub Actions topology.

- [ ] **Step 1: Replace `scripts/ci_local.sh` with the complete active harness**

The entire file must be exactly:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
scripts/db_test.sh
scripts/import_test.sh
```

- [ ] **Step 2: Correct the workflow scope comments**

In the opening `Scope intentionally NOT included` list, replace the iOS/macOS budget/future-lane comment with:

```yaml
#   - Archived iOS client: retained source is unsupported and outside current
#     CI, beta, and release scope.
```

Delete the complete commented `ios-tests` stub at the bottom of the workflow, from `# ios-tests: OMITTED` through the commented `xcodebuild` destination line. Do not change any non-comment YAML line.

- [ ] **Step 3: Prove local iOS execution is absent**

Run:

```bash
rg -n "xcode|Xcode|ios|iOS|SIM_DEVICE|Simulator|Swift|XCTest" scripts/ci_local.sh
```

Expected: exit 1 with no matches.

- [ ] **Step 4: Prove executable workflow topology is unchanged**

Run:

```bash
diff \
  <(env -u GIT_INDEX_FILE git show 1ad4eb2b5550af7c3941aacf08240559a9051193:.github/workflows/ci.yml | sed -E '/^[[:space:]]*(#|$)/d') \
  <(sed -E '/^[[:space:]]*(#|$)/d' .github/workflows/ci.yml)
rg -n "Archived iOS client: retained source is unsupported" .github/workflows/ci.yml
rg -n "no paid macOS runner|iOS tests stay local|macos-latest|xcodebuild|ios-tests:" .github/workflows/ci.yml
```

Expected: `diff` is silent; the archive comment appears once; the final `rg` exits 1 with no matches.

---

### Task 4: Reclassify architecture and operations as archive-only

**Files:**

- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`

**Interfaces:**

- Consumes: the active product and verification boundaries from Tasks 2 and 3.
- Produces: factual source inventory without current iOS compatibility or operational instructions.

- [ ] **Step 1: Add the architecture archive warning**

Rename the existing §4.3 iOS client heading to:

```markdown
### §4.3 Archived iOS reference (`ios/EvidenceLedger/`, unsupported)
```

Insert this exact block immediately under the heading:

```markdown
> **Archive boundary (2026-07-21):** This source tree is retained for historical
> reference only. It is not built, tested, supported, shipped, or included in
> beta/release acceptance. Current database decode, build, and runtime
> compatibility are not asserted; for example, `commission_model` may be NULL
> in the database while the archived `SlotPnl` model expects a non-optional
> `String`.
```

- [ ] **Step 2: Make every architecture-level iOS claim historical or archived**

Apply these exact classifications throughout `ARCHITECTURE.md`:

- In §1, topology, module map, subsystem heading, configuration, and dependency tables, use `archived`, `unsupported`, or `historical` wherever the retained iOS tree is named.
- Preserve source/file inventory and historical behavior descriptions; do not present them as current compatibility guarantees.
- Replace the current `Test state: 7 XCTest functions` paragraph with:

```markdown
Historical evidence: seven XCTest functions passed in the 2026-07-18 T14
session. That result is retained as dated history only; iOS is no longer a
current local/CI lane or an acceptance signal, and it is not rerun by this
repository.
```

- Replace every `no paid macOS runner`, `iOS runs locally`, `use SIM_DEVICE`, or future-runner statement with the archive boundary; do not leave a revival instruction.
- Set both architecture `Last verified` stamps to `2026-07-21 @ 1ad4eb2`, the immutable parent against which this documentation-only packet is checked.
- Keep current DB/import/web architecture claims unchanged.

- [ ] **Step 3: Reduce operations to one archive notice**

In `OPERATIONS.md`, add this exact subsection after the current prerequisites introduction:

```markdown
### Retained iOS source (unsupported archive)

`ios/EvidenceLedger/` remains in the repository as historical reference code.
It has no supported setup, configuration, execution, troubleshooting, test,
CI, beta, release, or compatibility workflow. Do not use this runbook to build
or operate it.
```

Remove all other active iOS operational material, including:

- Xcode/XcodeGen prerequisites and install commands;
- installation step 6 and `Config.plist` setup;
- iOS configuration-reference and `SIM_DEVICE` entries;
- iOS/XCTest rows in the current verification table;
- `ci_local.sh` simulator expectations;
- CI runner-budget/future-job language;
- simulator, Xcode build, Config.plist, and iOS-query troubleshooting rows; and
- any instruction to generate, open, configure, run, restart for, or support the archived app.

General Supabase/database operational facts may remain, but rewrite an iOS-specific consumer explanation in platform-neutral terms when the database fact is still current.

- [ ] **Step 4: Verify architecture and operations wording**

Run:

```bash
rg -n "Archive boundary \(2026-07-21\)|Historical evidence: seven XCTest|commission_model.*NULL" ARCHITECTURE.md
rg -n "Retained iOS source \(unsupported archive\)|no supported setup" OPERATIONS.md
rg -n "no paid macOS runner|iOS runs locally|use SIM_DEVICE|iOS lane stays local|remains supported" ARCHITECTURE.md OPERATIONS.md
rg -n "xcodebuild|xcodegen|SIM_DEVICE|iOS Simulator|Config\.plist" OPERATIONS.md
```

Expected: the first two commands print the required archive statements. The last two commands exit 1 with no matches.

---

### Task 5: Repair document anchors and run the complete archive gate

**Files:**

- Verify and, only within scope, modify: `README.md`
- Verify and, only within scope, modify: `ARCHITECTURE.md`
- Verify and, only within scope, modify: `OPERATIONS.md`
- Verify: `scripts/ci_local.sh`
- Verify: `.github/workflows/ci.yml`

**Interfaces:**

- Consumes: the five final working-tree files from Tasks 2-4.
- Produces: one clean five-path target commit eligible for Operator2 review.

- [ ] **Step 1: Repair and validate documentation anchors**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py --fix
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py OPERATIONS.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_arch_freshness.py --base 1ad4eb2b5550af7c3941aacf08240559a9051193
```

Expected: both validation commands exit 0 and architecture freshness reports no violation. If `--fix` changes a sixth path, stop and report the exact path instead of staging it.

- [ ] **Step 2: Run target smoke**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
```

Expected: final line `OK`.

- [ ] **Step 3: Prove exact scope, source retention, and CI comment-only behavior**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git diff --name-only
env -u GIT_INDEX_FILE git diff --exit-code -- ios/
test -d ios/EvidenceLedger
diff \
  <(env -u GIT_INDEX_FILE git show 1ad4eb2b5550af7c3941aacf08240559a9051193:.github/workflows/ci.yml | sed -E '/^[[:space:]]*(#|$)/d') \
  <(sed -E '/^[[:space:]]*(#|$)/d' .github/workflows/ci.yml)
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: diff check is silent; changed paths are exactly the five allowed paths; the `ios/` diff and uncommented-workflow diff are silent; the retained directory exists; no unrelated or staged path appears.

- [ ] **Step 4: Re-run the GREEN claim checks**

Run:

```bash
rg -n "Archived source:|unsupported archive|Archive boundary \(2026-07-21\)|Historical evidence: seven XCTest" README.md ARCHITECTURE.md OPERATIONS.md .github/workflows/ci.yml
rg -n "remains supported|no paid macOS runner|iOS tests stay local|iOS runs locally|use SIM_DEVICE|iOS lane stays local" README.md ARCHITECTURE.md OPERATIONS.md scripts/ci_local.sh .github/workflows/ci.yml
rg -n "SIM_DEVICE|xcodebuild|xcodegen|macos-latest" README.md OPERATIONS.md scripts/ci_local.sh .github/workflows/ci.yml
```

Expected: archive markers are present in their intended files; both stale/current/revival searches return no matches. Historical Xcode/XcodeGen names may remain only in the explicitly archived architecture inventory.

- [ ] **Step 5: Create the one scoped target commit**

Run:

```bash
env -u GIT_INDEX_FILE git add -- \
  README.md ARCHITECTURE.md OPERATIONS.md scripts/ci_local.sh .github/workflows/ci.yml
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "docs: archive retained iOS client"
```

Expected: exactly one commit containing exactly the five allowed paths.

- [ ] **Step 6: Verify the immutable target range after commit**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check 1ad4eb2b5550af7c3941aacf08240559a9051193..HEAD
env -u GIT_INDEX_FILE git diff --name-only 1ad4eb2b5550af7c3941aacf08240559a9051193..HEAD
env -u GIT_INDEX_FILE git diff --exit-code 1ad4eb2b5550af7c3941aacf08240559a9051193..HEAD -- ios/
test -d ios/EvidenceLedger
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: the committed range contains the same exact five paths; `ios/` is unchanged and present; the worktree is clean.

---

### Task 6: Publish immutable review evidence and stop

**Files:**

- Target repository: verify only; no new target change.
- Pipeline: one fixed-writer Director verify-request event and its exact commit.

**Interfaces:**

- Consumes: exact target range `1ad4eb2b5550af7c3941aacf08240559a9051193..HEAD` and all Task 5 evidence.
- Produces: one committed canonical verify-request assigned to non-author Operator2.

- [ ] **Step 1: Publish the canonical verify-request**

The request must bind:

- reviewed repository `/Users/hyungkoookkim/evidence-ledger`;
- exact base `1ad4eb2b5550af7c3941aacf08240559a9051193` and full reviewed head;
- author `director / gpt-5.6-sol`;
- reviewer `operator2 / gpt-5.6-terra`;
- the exact five-path manifest;
- the approved design at `487ca2175b44eb8e436b597bc2e5f2cd7d799ae1` and this plan's committed ref;
- separate immutable finding references for active-product wording, unsupported-archive wording, local-harness removal, CI comment-only scope, historical architecture labeling, operations removal, zero tracked `ios/` diff, and source retention;
- fresh document, architecture, smoke, scope, and clean-state outputs; and
- explicit exclusions for Swift/XCTest, simulator, generated project, deletion, integration, and remote publication.

- [ ] **Step 2: Commit and dispatch the exact request once**

Commit only the generated verify-request event in Pipeline, validate its exact committed identity, dispatch that single ref to the existing compatible Operator2 task, and stop for GO, NITS, or FAIL.

Do not integrate the target commit, update a remote reference, clean the target worktree, or start the next remediation packet before Coordinator reconciles the independent verdict and the separately held integration boundary.
