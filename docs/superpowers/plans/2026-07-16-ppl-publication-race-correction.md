# Evidence-Ledger PPL Publication-Race Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the three binding evidence-ledger CLI publication races with strict synthetic regressions, one or more additive target commits, a reconciled design-time advisory review, a monotonic sequence of reconciled actual-diff advisory reviews, and one fresh cumulative Pipeline Operator verdict.

**Architecture:** The target controller replaces check-then-mutate publication with held destination/staging descriptors and a private mode-`0700`, same-filesystem staging directory outside the repository. Each supported platform has one real final publisher function that repeats all parent/fence/source/destination checks and then directly invokes its fd-relative no-clobber C syscall in the same process, with no Python callback after the final check. Failure never unlinks a pathname. Pipeline’s independently verified target-aware bridge supplies sealed advisory review only; every real question requires its own active route, explicit user consent, complete executor token, CAS identity, and committed reconciliation.

**Tech Stack:** Python 3.11+ standard library, `ctypes` bindings to Darwin `renameatx_np` and Linux `renameat2`, pytest, Git plumbing, evidence-ledger’s synthetic recommendation tests, and the Pipeline target-aware advisory bridge.

## Global Constraints

- Binding umbrella design: `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` at `426744766711d4d6057a4698f5bb19d454ad621d`.
- Binding hold: `coordination/mailbox/sent/2026-07-13T11-38-14Z-coordinator-to-all-coordination.md`.
- Binding Operator FAILs: `coordination/mailbox/sent/2026-07-13T04-43-31Z-operator-to-all-verification-report.md` and `coordination/mailbox/sent/2026-07-13T08-03-23Z-operator-to-all-verification-report.md`.
- Fixed target cumulative base: `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa`. Fixed additive implementation base and held target HEAD: `8eaed44f803d871f09135c5d89395d38cf9e939e`.
- Initial review family: `e7c41a3d-8069-44e2-a0c7-cc1745947951`; design scope task ID: `86f5ca73-50c6-4528-8a7a-84a0c288d0d3`; first actual-diff scope task ID: `fe441a57-2c0c-4838-8622-8f10bfc0b05e`.
- Allowed target writes are exactly `recommendation/cli.py`, `recommendation/tests/test_cli.py`, and `ARCHITECTURE.md` only when the behavior change makes its current publication claims stale.
- The corrected target range is additive. Do not amend, rebase, reset, replace, rebuild, or rewrite `8eaed44f803d871f09135c5d89395d38cf9e939e` or an ancestor.
- Pipeline controls cross-repository routing. One non-Codex target controller owns product edits/commits. Codex is read-only in the target and owns independent verification. Opus is advisory only and is never a controller, seat, committer, verifier of record, verdict owner, or side-effect executor.
- The target-aware bridge must have a committed independent Pipeline GO whose exact report path and report commit are carried by its handoff. That original GO is necessary but not sufficient after candidate-policy integration changes the generic bridge/receipt dependency: Task 1 must also consume `docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md`, the candidate coordinator join's terminal `done_evidence`, and a fresh bounded Operator compatibility GO that binds the exact candidate integrated SHA and proves the target-aware bridge suite unchanged. Generic Opus restoration is not an entry gate.
- `design-time/1` must be reconciled before the first target test edit or product edit. The first implementation review is `actual-diff/2`. If a review issue requires code changes, land a new additive target commit and use `actual-diff/3`, then `/4`, monotonically. Never retry a question identity. A changed base, allowlist, policy, authority boundary, or design assumption requires a new family and a new `design-time/1`.
- Before each real advisory attempt, authority is committed in the acyclic order `scope-preparation route binding canonical path+digest → scope → fresh attempt route binding preparation route+scope → distinct explicit consent for exact scope/attempt route → complete Side-Effect Executor Token`. The umbrella approval, this plan, a previous question’s consent, standing approval, or the token alone does not authorize an attempt.
- Every question after sequence 1 requires the immediately prior receipt to be `reconciled`. Each attempt route and reconciliation route is fresh and committed; the route path, commit, blob OID, byte digest, Wave, active-route status, family, question, scope, receipt, and finite evidence grammar must validate.
- Every unavailable, uncertain, malformed, stale, or mismatched result is terminal for that identity. There is no retry, reset, fallback provider/transport, response import, credential entry, browser/API workaround, or prompt substitution.
- Provider context is the sealed content-addressed closure defined by the bridge plan: committed target Python blobs, selected committed Pipeline requirements, copied/hash-verified runtime, and content-free metadata. No live repository/Git/data/resource/workbook/database/DSN/business-value access is permitted.
- Existing-output behavior is fail-closed no-clobber. `snapshot` and `evaluate` require all output pathnames absent before any database/input read. Callers choose fresh names; the correction never deletes or replaces an existing artifact.
- After a temporary inode exists, any publication failure closes descriptors but never unlinks, removes, renames for cleanup, or truncates any pathname. The uncertain mode-`0600` entry remains in the private outside-repository staging directory for separately authorized cleanup.
- Before every shell block, use `set -euo pipefail`, define explicit Pipeline/target roots, and `cd` to the intended repository. Use `git -C` for every Git operation and prefix ordinary Git/pytest with `env -u GIT_INDEX_FILE`.
- Commit, provider attempt, route, mailbox, target edit, target commit, merge, push, publication, activation, and cleanup remain separate authorities. This plan authorizes none merely by existing.

## Publication Threat Model

The design protects against accidental or adversarial in-process substitutions at every Python seam before the real platform publisher, destination-parent relocation across the ignored/tracked fence before that publisher, source substitution before that publisher, destination clobber, different-user access blocked by the private mode-`0700` staging directory, cross-filesystem publication, and pathname cleanup of an uncertain inode.

It does **not** claim safety against a malicious concurrent process running as the same effective user that changes the staging pathname in the few instructions between the final `stat` and the pathname-based kernel rename call. Root/kernel compromise and a hostile filesystem are also excluded. If same-user concurrent hostility is an acceptance requirement, this plan blocks before implementation and needs a stronger isolation boundary, such as a separately authorized helper under a distinct UID or a proven kernel primitive that publishes from an already-held source handle. No test or handoff may imply this limitation is closed.

## File Structure

| File | Responsibility |
|---|---|
| `recommendation/cli.py` | Held destination/staging descriptors, private same-filesystem staging, direct fd-relative platform publisher, fsync, no-clobber, and no-pathname-cleanup failure behavior. |
| `recommendation/tests/test_cli.py` | Last-boundary relocation/substitution/failure pins, no-clobber, platform, durability, pre-I/O, and threat-model coverage. |
| `ARCHITECTURE.md` | Accurate publication guarantee and explicit same-user-concurrency limitation. |
| `coordination/verification/target-scopes/86f5ca73-50c6-4528-8a7a-84a0c288d0d3.json` | Committed `design-time/1` scope, followed by its fresh route/consent/token chain. |
| `coordination/verification/target-scopes/fe441a57-2c0c-4838-8622-8f10bfc0b05e.json` | First committed `actual-diff/2` scope; later issue-driven scopes use fresh generated task IDs. |
| `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md` | Exact target range, all reconciled receipts, Operator report path+commit, tests, limitations, and publication exclusions. |

---

### Task 1: Pass the target-aware gate and reconcile `design-time/1`

**Files:**
- Read: `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md`
- Read: `docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md`
- Read: the exact post-candidate target-bridge compatibility report and terminal candidate join named by that handoff
- Create under separate authority: design attempt route, user-consent event, complete executor-token event, committed scope, terminal receipt, and reconciliation route/state.

- [ ] **Step 1: Verify exact bridge GO and held target state**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
TARGET_WORKTREE=/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/ledger_start_guard.py --seat coordinator --wave 2
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" status --short
test "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" rev-parse HEAD)" = 8eaed44f803d871f09135c5d89395d38cf9e939e
test -z "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" status --porcelain=v1 --untracked-files=all)"
test "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" rev-parse --absolute-git-dir)" = /Users/hyungkoookkim/evidence-ledger/.git/worktrees/evidence-ledger-workbook-refresh-2026-07-11
test "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" rev-parse --path-format=absolute --git-common-dir)" = /Users/hyungkoookkim/evidence-ledger/.git
```

Read the bridge handoff’s exact report path and report commit. Resolve that path at that commit, validate the Operator GO schema and reviewed bridge range, and confirm the report commit changed only the captured report path. Then resolve the fixed candidate integration handoff, its uniquely bound candidate GO, post-candidate target-bridge compatibility GO, exact integrated Pipeline SHA, and terminal candidate join `done_evidence`. Require all referenced commits and the integrated SHA to be ancestors of current primary `main`; require the compatibility report to have executed the complete target-bridge suite at that exact SHA with provider attempts and receipt mutations both `0`; and prove no target-bridge source/test path changed after that compatibility report. NITS/FAIL, a nonterminal join, stale ancestry, or later dependency edit blocks before any PPL route, receipt reservation, provider action, or target edit. Never substitute the current Pipeline `HEAD` for a bound artifact.

- [ ] **Step 2: Bind and commit the immutable design scope before attempt authority**

First render the exact canonical scope bytes in a private Pipeline runtime buffer without writing the protocol path. Compute their digest. The coordinator then commits and capacity-validates a scope-preparation route that binds family/question/task, the future canonical scope path, that byte digest, scope-writer authority only, and provider attempts `0`. Only after that route is active may the scope be created with `apply_patch` and committed. The scope binds family invariants, correction/cumulative bases, held head, exact target identity, all tracked `recommendation/**/*.py` blobs at the held head, static selected Pipeline requirement blobs, runtime-manifest digest, prompt authority, and finite sealed verification commands. It contains no route, consent, or token reference, so no self-reference is possible.

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
DESIGN_SCOPE_PATH=coordination/verification/target-scopes/86f5ca73-50c6-4528-8a7a-84a0c288d0d3.json
DESIGN_PREP_GUARD_OUTPUT="$(env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/ledger_start_guard.py --seat coordinator --wave 2)"
DESIGN_PREP_ROUTE_PATH="$(printf '%s\n' "$DESIGN_PREP_GUARD_OUTPUT" | sed -n 's/^Active route: //p')"
test -n "$DESIGN_PREP_ROUTE_PATH"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/protocol_capacity_board.py --wave 2 --validate-route "$DESIGN_PREP_ROUTE_PATH"
DESIGN_PREP_ROUTE_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" log -1 --format=%H -- "$DESIGN_PREP_ROUTE_PATH")"
EXPECTED_DESIGN_SCOPE_DIGEST="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" show "$DESIGN_PREP_ROUTE_COMMIT:$DESIGN_PREP_ROUTE_PATH" | sed -n 's/^Target scope sha256: //p')"
test -n "$EXPECTED_DESIGN_SCOPE_DIGEST"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- "$DESIGN_SCOPE_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "docs(opus): bind PPL design advisory scope" -- "$DESIGN_SCOPE_PATH"
DESIGN_SCOPE_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff-tree --no-commit-id --name-only -r "$DESIGN_SCOPE_COMMIT")" = "$DESIGN_SCOPE_PATH"
DESIGN_SCOPE_BLOB="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse "$DESIGN_SCOPE_COMMIT:$DESIGN_SCOPE_PATH")"
DESIGN_SCOPE_DIGEST="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" cat-file blob "$DESIGN_SCOPE_BLOB" | "$PIPELINE_ROOT/.venv/bin/python" -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())')"
test "$DESIGN_SCOPE_DIGEST" = "$EXPECTED_DESIGN_SCOPE_DIGEST"
DESIGN_SCOPE_REFERENCE="$DESIGN_SCOPE_PATH@commit:$DESIGN_SCOPE_COMMIT@blob:$DESIGN_SCOPE_BLOB@sha256:$DESIGN_SCOPE_DIGEST"
```

Run the bridge’s static provider-free scope validator. It must prove repository/ancestry/source/runtime/requirement closure, target clean state, no prior CAS conflict, and no live-root exposure without creating receipt state.

- [ ] **Step 3: Commit the acyclic route, consent, and token chain**

The coordinator commits a fresh Wave-2 attempt route for family `e7c41a3d-8069-44e2-a0c7-cc1745947951`, question `design-time/1`, task `86f5ca73-50c6-4528-8a7a-84a0c288d0d3`, exact preparation-route reference, exact `DESIGN_SCOPE_REFERENCE`, and one predeclared UUID side-effect ID. Only after scope and attempt route are committed, stop and ask the user to authorize exactly this one real advisory attempt. After that explicit reply, record a later non-route `decision` event bound to exact scope+attempt route and the authenticated reply correlation; the record is evidence, never a substitute for live consent. Then create a still-later non-route `decision` artifact carrying the Side-Effect Executor Token bound to exact scope+attempt route+consent, containing all ten required fields, one route-named executor, and in `allowed_command_class` the one exact argv literal with the three already committed references plus `--side-effect-id` and that route-predeclared UUID. The command never names the token itself. Capture path, commit, blob OID, and byte digest for all artifacts and require strict ancestry `preparation route commit < scope commit < attempt route commit < consent commit < token commit`.

The capacity validator and active-route selector must pass after the token commit and immediately before review. The exact bound consent/token artifacts are the only allowed post-route mailbox successors; any other newer mail after the route, any mail after the token, unauthenticated consent correlation, changed target head, satisfied target, missing token field, different executor, non-exact command, backward reference, or descendant/self-reference blocks with zero attempt.

- [ ] **Step 4: Validate authority and execute the one consented `design-time/1` attempt**

Run provider-free validation with the exact scope, attempt-route, and consent references plus the route-predeclared side-effect ID. It must resolve and validate the preparation route through the attempt route, resolve exactly one later committed token, prove active attempt route, strict acyclic ancestry, complete authorization, sealed closure including all four route/consent/token authority blobs, target clean state, and no prior CAS record. Only the token-named executor may then run that exact validated review command. Immediately before reservation the bridge refreshes route/mail/consent/token/target state. Capture canonical review JSON and receipt ID from that invocation. `unavailable`, uncertain delivery, stale state, or malformed output stops the PPL correction with no retry and no target edit.

- [ ] **Step 5: Reconcile every finding through a fresh committed route**

The controller and Operator disposition every issue as `adopted|modified|rejected|unresolved` with the bridge’s finite structured evidence references. The coordinator commits a fresh reconciliation route naming Wave 2, current active route, exact family/question/receipt/scope/closure, and canonical disposition mapping. Capture its path+commit+blob+digest from Git and call only:

```text
opus_target_review_bridge.py reconcile --pipeline-root /Users/hyungkoookkim/Pipeline --receipt-id EXACT_DESIGN_RECEIPT --route-reference EXACT_COMMITTED_RECONCILIATION_ROUTE_REFERENCE
```

Task 2 cannot start until the design receipt state is `reconciled`, its outcome is `pass|issues` rather than `unavailable`, and no unresolved finding blocks the stated threat model, touched paths, syscall contract, tests, or authority boundary. A finding that changes the family’s allowlist, base, policy, authority boundary, or design assumptions closes this family and requires a newly consented family beginning at `design-time/1`.

- [ ] **Step 6: Commit a distinct target-implementation route**

The advisory preparation, attempt, and reconciliation routes grant no target edit or commit authority. After `design-time/1` is reconciled, the coordinator commits and capacity-validates one separate cross-repository implementation route. It names one non-Codex target controller and the independent Codex Operator verifier; binds repository `hkk009008-svg/evidence-ledger`, target common directory `/Users/hyungkoookkim/evidence-ledger/.git`, worktree, cumulative base, exact additive head `8eaed44f803d871f09135c5d89395d38cf9e939e`, exact three-path write allowlist, additive-only commit topology, reconciled design receipt/route, tests, stop conditions, and provider attempts `0`; and grants no merge, push, publication, cleanup, provider, or retry authority. The route's commit/path/blob/digest becomes the edit-authority root for every target commit and later Operator report.

Immediately before the first Task-2 edit, the named controller runs the ledger start guard for its routed role, validates this implementation route through the capacity board, re-resolves the exact route bytes and target/common-directory identity, requires the clean held target head, and proves no newer conflicting route or owner. Any mismatch returns to the coordinator. An advisory route or consent/token artifact can never substitute for this implementation route.

### Task 2: Add strict RED pins at the real final publication boundary

**Files:**
- Modify: `recommendation/tests/test_cli.py`

- [ ] **Step 1: Assert the fixed target base before any edit**

```bash
set -euo pipefail
TARGET_WORKTREE=/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
cd "$TARGET_WORKTREE"
test "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" rev-parse HEAD)" = 8eaed44f803d871f09135c5d89395d38cf9e939e
test -z "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" status --porcelain=v1 --untracked-files=all)"
```

- [ ] **Step 2: Pin destination-parent relocation immediately before the real platform publisher**

Add `test_last_boundary_parent_relocation_calls_real_platform_publisher_and_refuses`. Capture the actual `_darwin_publish_owned_noreplace` or `_linux_publish_owned_noreplace`, replace only the publisher selector with a wrapper that moves the prepared ignored parent under a tracked root, leaves a symlink at the old pathname, then calls the real platform function. The real function must repeat its checks and reject before its C syscall. Assert no destination at either location, no payload bytes under the repository, and one owned mode-`0600` payload inode still in private staging.

- [ ] **Step 3: Pin source substitution immediately before the real platform publisher**

Add `test_last_boundary_source_substitution_calls_real_platform_publisher_and_refuses`. The wrapper renames the owned staging name aside, hard-links a foreign inode at the original name, then calls the real platform function. Assert source-identity rejection, absent destination, unchanged foreign bytes, and survival of both foreign and owned entries. This proves in-process seam defense; it does not claim hostile same-UID concurrency after the final check.

- [ ] **Step 4: Pin syscall failure and no-pathname cleanup**

Add `test_last_boundary_failure_never_unlinks`. Inject an errno result at the direct C symbol, spy on `os.unlink`, `os.remove`, and pathname cleanup helpers, and assert none is called after temporary creation. The target is absent; every staging entry survives; descriptors close; the error is fail-closed.

- [ ] **Step 5: Pin pre-I/O, platform, filesystem, and durability behavior**

Add tests proving:

- any existing output is rejected before `psycopg.connect` or input `read_bytes`;
- staging is outside `REPO_ROOT`, owned by effective UID, mode `0700`, held by descriptor, and on every destination’s device;
- cross-device or unsupported-platform/syscall state fails before database/input reads;
- Darwin directly uses fd-relative `renameatx_np` with `RENAME_EXCL|RENAME_NOFOLLOW_ANY|RENAME_RESOLVE_BENEATH`;
- Linux directly uses fd-relative `renameat2(RENAME_NOREPLACE)` on supported architectures;
- success preserves bytes, mode `0600`, source/final inode equality, file fsync, and both source/destination directory fsync;
- no test asserts safety against a malicious concurrent same-UID process.

- [ ] **Step 6: Run focused RED**

```bash
set -euo pipefail
TARGET_WORKTREE=/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
cd "$TARGET_WORKTREE"
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest recommendation/tests/test_cli.py -k 'last_boundary or existing_output or same_filesystem or rename_noreplace' -q
```

Expected: tests fail because the descriptor-held staging/final publisher/no-cleanup behavior does not exist. Preserve the exact command, exit status, and failing synthetic test names in the Pipeline-side controller handoff/report; do not create or retain a target-worktree scratch artifact.

### Task 3: Implement the descriptor-held direct platform publisher

**Files:**
- Modify: `recommendation/cli.py`
- Modify: `recommendation/tests/test_cli.py`
- Modify if claims become stale: `ARCHITECTURE.md`

**Interfaces:**
- Produces: `_PreparedOutput`, `_PublicationStaging`, `_OwnedTemporary`, `_prepare_output()`, `_prepare_publication_staging()`, `_write_owned_temporary()`, `_platform_publisher()`, `_darwin_publish_owned_noreplace()`, `_linux_publish_owned_noreplace()`, `_publish_owned_noreplace()`, and `_publish_bytes()`.

- [ ] **Step 1: Hold destination and staging identities for the whole operation**

`_PreparedOutput` stores canonical target/parent paths, basename, role, open parent fd, device/inode, repository-relative fence identity, and close state. `_PublicationStaging` stores outside-repository path, open directory fd, device/inode, owner/mode, and close state. `_OwnedTemporary` stores basename, open file fd, device/inode, owner/mode, and close state. None owns a pathname cleanup callback, weakref finalizer, `TemporaryDirectory`, or context-manager deletion behavior.

`_prepare_output()` requires an absent basename, opens the real parent with directory/no-follow/close-on-exec flags, records identity, and validates the existing ignored/tracked fence. `_prepare_publication_staging()` creates one unpredictable private mode-`0700` directory outside `REPO_ROOT`, opens it without following symlinks, and requires the same device as every prepared destination before database/input reads.

- [ ] **Step 2: Write and seal an owned temporary inode**

Create an unpredictable basename relative to the staging fd using exclusive/no-follow flags and mode `0600`. Write exact bytes through the held fd, flush, `fsync`, and record `fstat` identity. Require regular file, effective UID ownership, mode `0600`, link count 1, and staging-path `stat(..., dir_fd=...)` identity equality. Do not expose a cleanup callback.

- [ ] **Step 3: Make each real platform function the final check-and-syscall boundary**

`_platform_publisher()` selects a supported real function before any final check. `_publish_owned_noreplace()` calls the selected function once. Each real platform function must contain, in its own function body:

1. pre-resolved C symbol and encoded source/destination basenames;
2. `fstat` checks for the held staging, parent, and source descriptors;
3. `stat(..., dir_fd=staging_fd, follow_symlinks=False)` equality with the held source inode, regular-file/UID/mode/link-count checks;
4. canonical destination-parent pathname identity equality with the held parent fd and a repeated ignored/tracked fence check;
5. `stat(..., dir_fd=parent_fd, follow_symlinks=False)` proving destination absence;
6. a direct `ctypes` C call using `staging.directory_fd`, source basename, `prepared.parent_fd`, and destination basename.

There is no Python helper, callback, platform-dispatch lookup, logging hook, or test hook between the final check and direct C call. Darwin calls `renameatx_np` with the three fixed safety flags. Linux calls `renameat2` with `RENAME_NOREPLACE`; unsupported symbol/architecture/flag combinations fail closed before product I/O. Both calls are same-process and fd-relative for both directories.

- [ ] **Step 4: Preserve no-clobber, durability, and no-cleanup failure semantics**

On success, confirm final inode identity through the held parent fd, fsync the destination directory and staging directory, and close all descriptors. Do not automatically remove the staging directory pathname; separately authorized cleanup handles even an empty directory. On any failure after temporary creation, close descriptors and propagate a sanitized error; do not unlink, remove, rename, truncate, or retry any pathname. Existing destinations remain untouched due to the kernel no-clobber flag.

- [ ] **Step 5: Integrate both CLI commands and make claims truthful**

Prepare all outputs and same-filesystem staging before `psycopg.connect` or reading inputs. `snapshot` and `evaluate` publish through the new primitive only. Update `ARCHITECTURE.md` if needed to state the exact guarantees and the excluded hostile same-UID race; never use unqualified “race-free” wording.

- [ ] **Step 6: Run focused GREEN**

```bash
set -euo pipefail
TARGET_WORKTREE=/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
cd "$TARGET_WORKTREE"
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest recommendation/tests/test_cli.py -k 'last_boundary or existing_output or same_filesystem or rename_noreplace' -q
env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" diff --check
```

### Task 4: Prove non-vacuity, run full target verification, and land an additive commit

**Files:**
- Modify only the Task 2-3 target files.

- [ ] **Step 1: Prove the new guards are non-vacuous**

Temporarily mutate one final parent identity check, one source identity check, and the no-cleanup behavior separately; confirm the corresponding strict test fails for the expected reason; restore each mutation with a scoped patch. Do not leave a deferred defect. If an independently confirmed defect cannot be fixed, stop and apply R-VERIFY-TIER rather than proceeding.

- [ ] **Step 2: Run the full target suite and smoke**

```bash
set -euo pipefail
TARGET_WORKTREE=/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
cd "$TARGET_WORKTREE"
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest recommendation/tests/test_cli.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest recommendation/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" diff --check
```

All database tests use existing synthetic scratch databases only. No canonical workbook/database/resource read is permitted.

- [ ] **Step 3: Inspect the exact diff and commit once**

```bash
set -euo pipefail
TARGET_WORKTREE=/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11
cd "$TARGET_WORKTREE"
test "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" merge-base 8eaed44f803d871f09135c5d89395d38cf9e939e HEAD)" = 8eaed44f803d871f09135c5d89395d38cf9e939e
env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" diff -- recommendation/cli.py recommendation/tests/test_cli.py ARCHITECTURE.md
env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" add -- recommendation/cli.py recommendation/tests/test_cli.py ARCHITECTURE.md
env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" commit -m "fix(recommendation): harden artifact publication" -- recommendation/cli.py recommendation/tests/test_cli.py ARCHITECTURE.md
CORRECTED_HEAD="$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" rev-parse HEAD)"
test "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" rev-parse "$CORRECTED_HEAD^")" = 8eaed44f803d871f09135c5d89395d38cf9e939e
env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" diff-tree --no-commit-id --name-only -r "$CORRECTED_HEAD"
test -z "$(env -u GIT_INDEX_FILE git -C "$TARGET_WORKTREE" status --porcelain=v1 --untracked-files=all)"
```

If `ARCHITECTURE.md` did not need a change, omit it from add/commit and require the exact two code/test paths. Capture `CORRECTED_HEAD` in the target controller’s durable handoff. Do not push.

### Task 5: Run and reconcile the monotonic actual-diff review sequence

**Files:**
- Create under separate authority: first actual scope `coordination/verification/target-scopes/fe441a57-2c0c-4838-8622-8f10bfc0b05e.json` and any later uniquely generated scopes.

- [ ] **Step 1: Require reconciled design evidence and a clean exact target head**

The coordinator validates the exact design receipt is `reconciled`, its family invariants match, and `CORRECTED_HEAD` is a clean additive child of `8eaed44f803d871f09135c5d89395d38cf9e939e` with only allowlisted paths. A reviewed-but-not-reconciled design receipt is a blocker.

- [ ] **Step 2: Commit and validate the first actual scope**

Render the canonical actual scope bytes privately, then commit and validate a provider-zero scope-preparation route binding their future path+digest. Bind prior reconciled design receipt/scope digest, unchanged family invariants, exact `CORRECTED_HEAD`, current target/source/runtime blobs, and finite verification commands. The scope contains no later authority reference. Commit only `fe441a57-2c0c-4838-8622-8f10bfc0b05e.json`; capture its exact commit, blob OID, and byte digest; require it equals the preparation route digest and that the commit changed one path; then run static provider-free scope validation. No ambient `HEAD` may supply a scope identity.

- [ ] **Step 3: Commit fresh `actual-diff/2` route, consent, and token**

Create a later active Wave-2 attempt route bound to the exact actual preparation route, exact actual scope, and one fresh side-effect ID. Stop and obtain a second explicit user approval specifically for this real attempt. Record a still-later distinct committed consent event bound to scope+attempt route, then a complete new token bound to scope+attempt route+consent and naming one executor plus the exact review argv with the three committed references and side-effect ID. Resolve and validate the unique token’s path+commit+blob+digest, require strict ancestry, and reject self-reference or duplicates. Neither design-time authority nor this plan may be reused.

- [ ] **Step 4: Execute once and reconcile through a fresh route**

The token-named executor performs exactly one `actual-diff/2` attempt after the bridge’s immediate state refresh. Capture receipt JSON directly. The controller and Operator disposition findings with finite structured evidence; the coordinator commits a distinct reconciliation route bound to exact family/question/receipt/scope/closure; the bridge records reconciliation from its path+commit+blob+digest. Unavailable/uncertain results stop the sequence without retry.

- [ ] **Step 5: Continue monotonically when a finding requires code changes**

If an adopted/modified issue requires code changes:

1. reconcile `actual-diff/N` first;
2. route and land one new additive target correction commit under controller authority;
3. render a unique `actual-diff/N+1` scope, commit its provider-zero preparation route, then commit the matching scope with prior receipt/scope binding;
4. commit a fresh active attempt route for preparation route+scope, then distinct explicit user consent, then a complete token in strict ancestry order;
5. execute once and reconcile from a fresh committed route.

Never reuse `actual-diff/N`, its task ID, route, consent, token, or CAS key. If family invariants change, stop the sequence and start a new family at design-time. Task 6 begins only when the latest actual-diff receipt is reconciled and no unresolved finding blocks the Operator question.

### Task 6: Obtain the cumulative Operator verdict and freeze exact provenance

**Files:**
- Create under routed execution: one canonical Operator verification-report event.
- Create after GO: `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md`.

- [ ] **Step 1: Validate fresh verification authority**

From Pipeline, refresh coordinator guard, capacity, mailbox bodies, locks, and the exact target state. The route must name the final target head/range, all advisory question IDs/receipts/reconciliation routes, exact tests, write allowlist, and Operator as verifier of record. Missing or mismatched authority is a blocker; do not reconstruct it.

- [ ] **Step 2: Independently inspect and test the cumulative range**

Operator verifies ancestry from cumulative base `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa`, additive parent chain from `8eaed44f803d871f09135c5d89395d38cf9e939e`, exact changed paths, all reconciled advisory CAS identities, distinct consent/token per attempt, no provider retries, and no business-data access. Rerun the focused/full target suites and smoke. Mutate the three last-boundary guards to prove non-vacuous failure.

GO requires all prior corrected behavior retained, the three reported publication races closed within the stated threat model, latest actual-diff reconciliation complete, clean target, green tests, truthful architecture claims, and no authority/privacy violation. Opus status never determines the verdict.

- [ ] **Step 3: Send, commit, and capture the report from its producer**

The Operator first runs:

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
BODY_ROOT="$PIPELINE_ROOT/.codex/runtime/protocol-bodies"
cd "$PIPELINE_ROOT"
if test -e "$BODY_ROOT" || test -L "$BODY_ROOT"; then
  test -d "$BODY_ROOT"
  test ! -L "$BODY_ROOT"
  test "$(stat -f %u "$BODY_ROOT")" = "$(id -u)"
  test "$(stat -f %Lp "$BODY_ROOT")" = 700
else
  install -d -m 700 "$BODY_ROOT"
fi
test ! -L "$BODY_ROOT"
test "$(stat -f %u "$BODY_ROOT")" = "$(id -u)"
test "$(stat -f %Lp "$BODY_ROOT")" = 700
```

The Operator then creates the complete schema-valid report body with `apply_patch` at `$PIPELINE_ROOT/.codex/runtime/protocol-bodies/ppl-publication-race-verification-report.md`. It contains literal final target head/range, all reconciled receipt identities, commands/results, limitations, and GO/NITS/FAIL, and is parsed before send.

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
BODY_ROOT="$PIPELINE_ROOT/.codex/runtime/protocol-bodies"
VERIFICATION_REPORT_BODY="$BODY_ROOT/ppl-publication-race-verification-report.md"
test -f "$VERIFICATION_REPORT_BODY"
test ! -L "$VERIFICATION_REPORT_BODY"
test "$(dirname "$(realpath "$VERIFICATION_REPORT_BODY")")" = "$BODY_ROOT"
chmod 600 "$VERIFICATION_REPORT_BODY"
VERIFICATION_REPORT_BODY_DIGEST="$("$PIPELINE_ROOT/.venv/bin/python" -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$VERIFICATION_REPORT_BODY")"
REPORT_SEND_OUTPUT="$(coordination/bin/send-event operator all verification-report "PPL publication-race cumulative verdict" < "$VERIFICATION_REPORT_BODY")"
PPL_REPORT_PATH="${REPORT_SEND_OUTPUT#created }"
PPL_REPORT_PATH="${PPL_REPORT_PATH%% *}"
test -f "$PPL_REPORT_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -f -- "$PPL_REPORT_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "docs(verify): report PPL publication verdict" -- "$PPL_REPORT_PATH"
PPL_REPORT_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff-tree --no-commit-id --name-only -r "$PPL_REPORT_COMMIT")" = "$PPL_REPORT_PATH"
```

Do not discover the report later with `git show HEAD`; `PPL_REPORT_PATH` and `PPL_REPORT_COMMIT` are exact outputs of the producer/commit sequence.

- [ ] **Step 4: Close the join and write the handoff after GO**

NITS/FAIL creates a durable blocker and does not create the success handoff. On GO only, the coordinator commits a distinct Pipeline handoff-only route naming one routed Pipeline Director. It binds the content-addressed target-controller route and final target head/range, the producer-captured Operator report and GO, all reconciled receipt identities, the single allowed Pipeline path `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md`, exact required fields, and zero target/provider/merge/push/publication authority. The target controller cannot author or commit in Pipeline, and the coordinator cannot author the handoff.

The routed Pipeline Director validates that handoff route and creates the allowed handoff with `apply_patch`. The handoff records both repository heads, the content-addressed target-implementation route, exact cumulative/additive ranges, every question/scope/receipt/reconciliation route, user-consent and token identities without raw sensitive content, executed tests, `VERIFICATION_REPORT_BODY_DIGEST`, `PPL_REPORT_PATH`, `PPL_REPORT_COMMIT`, no business-data access, no retries, no push/publication, and these limitations:

- publication is fail-closed/no-clobber and defends all tested in-process pre-syscall seams;
- failed temporary names are never cleaned up automatically;
- cross-filesystem and unsupported platform/syscall cases fail before product I/O;
- hostile concurrent same-UID substitution between final check and pathname-based syscall is not claimed safe;
- push, merge, target artifact publication, activation, and quarantine cleanup need separate authority.

Validate the handoff, stage only its exact Pipeline path, commit with a strict pathspec, and capture `PPL_HANDOFF_COMMIT`, `PPL_HANDOFF_BLOB`, and its SHA-256 digest from that exact commit. Require the handoff commit's changed-path set to equal only the handoff path. The coordinator may close the PPL join only after those identities validate and the terminal `done_evidence` names both the content-addressed handoff and producer-captured GO report. An uncommitted document, report-only state, or later ambient `HEAD` is not terminal evidence.

## Plan Self-Review Record

- Review chain: design-time is reconciled before edits; every later question has a reconciled immediate predecessor, fresh active route, distinct explicit consent, complete token, unique scope, and monotonic sequence.
- Publication boundary: the real Darwin/Linux function performs final descriptor/path/fence/source/destination checks and directly invokes one same-process fd-relative no-clobber C syscall with no later Python seam.
- Cleanup: no failure path after temporary creation calls pathname deletion or replacement; private same-filesystem staging is preserved for separate cleanup authority.
- Provenance: scope and route references carry exact path+commit+blob+digest; Operator report path+commit come directly from the producer/commit operation, not ambient `HEAD`.
- Threat claim: different-user and in-process seam defenses are tested; hostile concurrent same-UID safety is explicitly excluded and blocks if later required.
- Authority: Opus is advisory, the target controller alone edits/commits, the Pipeline Operator alone issues GO/NITS/FAIL, and coordinator closeout consumes only the exact committed report.

## Exact Next Trigger

After the target-aware bridge and the post-candidate compatibility gate both receive independent GO, the coordinator may commit the `design-time/1` scope and then its fresh attempt route. The real attempt remains blocked until the user separately approves that exact scope+route and the later complete executor token validates. No target edit begins before the resulting receipt is reconciled and the distinct target-implementation route is committed and validated.
