# Coordination Reliability Friction Reduction Design

**Status:** verbal design approved; written spec awaiting user review
**Date:** 2026-07-20
**Coordinator route:** `coordination/mailbox/sent/2026-07-20T02-26-33Z-coordinator-to-all-coordination.md@4e36dfb98d58399eba166852e629fe410427319e`
**Design base:** `4e36dfb98d58399eba166852e629fe410427319e`

## 1. Decision

Make three small reliability corrections to the Codex coordination path:

1. In the known managed Pipeline checkout, an authorized Codex fixed-writer action uses the supported scoped execution profile on its first attempt.
2. Fast resume resolves and evaluates the exact expected task instead of allowing unrelated malformed historical routes to contaminate the decision. When fast resume cannot pass, `FULL ORIENTATION REQUIRED` includes a complete read-only orientation capsule assembled from evidence already collected.
3. Live-seat monitoring uses cursor-based task waiting first and falls back to bounded read-only thread snapshots when the wait handler is unavailable. Monitoring failure never causes redispatch.

This design removes repeated failed attempts and redundant orientation work. It does not add a coordinator service, task registry, broker, dependency, event-sourcing layer, or agent framework.

## 2. Confirmed Problem Boundaries

### Fixed writer

`coordination/bin/send-event` correctly delegates publication to `scripts/mailbox_writer.py`. The writer opens the Git-common-dir fence `.git/protocol-kernel-writer.lock` with the existing regular-file and `O_NOFOLLOW` protections. The committed Operator2 reproduction at `coordination/mailbox/sent/2026-07-18T03-49-51Z-operator2-to-coordinator-findings.md@c75627692f3f2b3f2bcae331ed5484e899d5b191` proved:

- the writer selectors pass in writable temporary repositories;
- the real managed checkout denies the lock open with `EPERM`; and
- the unchanged fixed writer succeeds under the authorized supported profile.

The classification is `environment-policy`, not a mailbox-writer source defect. The friction is the Codex launch choice: a known-denied default attempt is performed before the supported scoped invocation.

### Fast resume

`scripts/ledger_start_guard.py::build_resume` currently resolves a target-wide latest route before loading the exact `--resume-from` route. It then adds every `RouteBatchReader.issues` entry to the current resume reasons. `RouteBatchReader` collects malformed route-shaped events globally, so an unrelated historical task can force `FULL ORIENTATION REQUIRED` for an otherwise unchanged expected task.

Legacy routes correctly remain ineligible for `FAST RESUME: PASS` because they do not have immutable owner/revision evidence. The current fallback, however, prints reasons and ordinary startup commands without the route body, immutable route reference, Pipeline state, target state, or mailbox snapshot already gathered during the attempted resume.

### Live task monitoring

The Codex app owns `wait_threads` and `read_thread`; Pipeline has no local API implementation to patch. During live Task 2 coordination, `wait_threads` intermittently returned `No handler registered for tool: codex_app.wait_threads`, while bounded `read_thread` calls against the same task remained available. Existing protocol already defines a stable dispatch identity and forbids resending an in-progress or completed identity, but it does not define the safe handler-unavailable monitoring branch.

## 3. Scope

### Behavior-changing implementation

- task-scoped fast-resume selection and issue handling;
- a complete authority-free full-orientation capsule;
- Codex fixed-writer first-attempt launch guidance for the known managed Pipeline profile; and
- Codex task-monitor fallback guidance with explicit deduplication.

### Expected implementation surfaces

- `scripts/ledger_start_guard.py`
- `scripts/route_lineage.py`
- `scripts/codex_protocol_model.py`
- `tests/unit/test_ledger_fast_resume.py`
- `tests/unit/test_protocol_prompt_sync.py`
- `AGENTS.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`
- `docs/protocol/codex/continuation.md`
- `docs/protocol/codex/ledger-cli-adoption.md`

The implementation plan may remove a listed documentation surface if the prompt-sync tests prove it is not part of that contract. It may not add a production dependency or expand into product repositories.

### Explicit non-goals

- changing `coordination/bin/send-event` or `scripts/mailbox_writer.py`;
- weakening, relocating, bypassing, or deleting the writer fence;
- granting automatic mailbox, lock, cursor, merge, push, spend, provider, or other side-effect authority;
- rewriting or normalizing historical mailbox routes;
- making legacy routes pass fast resume;
- changing the Codex app's task-tool implementation;
- persisting a task registry or polling journal;
- installing `uv`, Ruff, psutil, or any other package as part of this slice; and
- changing evidence-ledger, private data, services, or remote state.

## 4. Fixed-Writer Launch Policy

The repository writer remains the only publication mechanism. The correction is a Codex adapter rule applied only when all of these are true:

1. the requested event publication is already authorized for the exact sender, recipient, kind, and scope;
2. the current checkout is the managed Pipeline workspace whose permission profile exposes the Git common directory as read-only to the default sandbox; and
3. the command is the fixed `coordination/bin/send-event` invocation, not a generic shell or direct Git/mailbox write.

When those conditions hold, Codex requests the supported scoped execution profile on the first fixed-writer attempt. The approval request names the exact writer action. Any reusable approval prefix is limited to `coordination/bin/send-event` plus the concrete sender seat; it is never a general shell, Python, Git, or filesystem rule.

If publication is not already authorized, Codex stops at the existing authority boundary. If the supported invocation fails, Codex reports the exact path, syscall, and error; it does not retry through a second writer, hand-edit the mailbox, inject `TMPDIR`, or weaken the sandbox or fence. Unknown checkouts retain ordinary execution rather than assuming escalation.

This is instruction-level behavior. Existing writer and coordination-tooling tests remain unchanged and must stay green. Prompt-sync tests pin the first-attempt conditions, fixed-writer-only scope, and absence of a fallback writer.

## 5. Task-Scoped Fast Resume

### Selection order

`build_resume` changes its read-only selection order:

1. Validate `--resume-from` as a canonical committed path plus full SHA.
2. Load that exact route through `RouteBatchReader.load_route_ref`.
3. Require a parseable expected task identity and evidence that the route belongs to the selected target.
4. Load and resolve only routes for that expected task with `load_task_routes` and `resolve_task_routes`.
5. Compare the expected immutable route with the authoritative tip for the same task.
6. Run the existing guidance, owner, Pipeline, target, dirty-path, and mailbox checks on that authoritative route.

An invalid or unreadable expected reference, missing expected task identity, different authoritative same-task tip, same-task fork, ineffective ownership change, or same-task malformed route-shaped event yields `FULL ORIENTATION REQUIRED`. Hard base-guard failures continue to yield `START GUARD: FAIL`.

### Scoped reader issues

`RouteBatchReader` retains its existing global string `issues` API for global diagnostics and adds task attribution for resume decisions. A malformed route-shaped event is attributed from its exact `Task-board` or autonomous `Task ID` when that identity can be parsed unambiguously.

- Issues attributed to the expected task fail closed to full orientation.
- Issues attributed to another task remain available through the global reader diagnostics but do not enter the expected-task resume reasons or classification.
- An issue that cannot be attributed safely remains relevant and fails closed.

No historical route is edited. Global route-lineage checks retain their current all-route behavior.

### Full-orientation capsule

`FULL ORIENTATION REQUIRED` remains advisory and returns exit zero. Its output is extended with a read-only capsule whenever collection reached those facts:

- expected and current immutable route references;
- current route body;
- task ID, revision, owners, outcome, and immutable finding references;
- Pipeline HEAD, branch, and dirty paths;
- registered target identity, selected worktree, target HEAD, and dirty paths;
- mailbox cursor, unread references, and availability state;
- parsed target guidance and allowed paths;
- deduplicated reasons for the fallback; and
- ordinary startup actions.

The capsule performs no second collection pass and mutates no cursor, index, ref, lock, worktree byte, or mailbox artifact. It always ends with the existing statement that fast resume grants no external-effect authority.

### Future route grammar

Future target-bound routes use these exact fields:

```text
Target worktree: <absolute path>
Accepted target HEAD: <40 lowercase hex SHA>

## Target Allowed Paths

- <repository-relative path>
```

The parser keeps its accepted legacy aliases for committed history. Documentation and adapter surfaces standardize the canonical labels so new routes do not depend on prose inference.

## 6. Live Task Monitoring Fallback

The canonical automatic-routing model keeps the existing dispatch identity:

```text
trigger path@full commit
+ assigned seat
+ Pipeline checkout
+ exact base/head and required reviewer model for reviews
```

After one exact trigger has been sent:

1. Monitor with `wait_threads`, preserving the per-target cursor returned by the tool.
2. If and only if the tool reports a missing or unavailable wait handler, use `read_thread` for the same thread with the smallest useful snapshot (`turnLimit=1`, outputs omitted).
3. Poll snapshots at a bounded cadence rather than in a tight loop. Compare the latest turn/message identity with the previously observed identity and report only changes.
4. Continue monitoring an active task; reconcile a completed task's committed artifact; leave an approval or user-input request for the user.
5. Never send the trigger again, create a replacement task, or change seats merely because monitoring failed.

If the fallback snapshot is also unavailable, preserve the dispatch identity and perform at most one normal task discovery/deduplication refresh. Reuse the unique matching task if found. Ambiguous or unavailable state becomes one concrete tooling blocker; it does not authorize redispatch and does not ask the user to relay the seat prompt.

The fallback is observational. It grants no seat, mailbox, cursor, lock, merge, push, spend, provider, or product authority. Pipeline tests can pin this model and its synced instruction surfaces; they cannot claim to test the external Codex app handler itself.

## 7. Error Handling And Safety Invariants

| Condition | Result |
|---|---|
| Fixed-writer action lacks exact authority | Stop before launch |
| Known managed Git-common-dir restriction and exact writer action is authorized | Request supported scoped profile on first attempt |
| Supported writer attempt fails | Report exact failure; no alternate writer |
| Expected route ref is malformed, unreadable, or unattributable | `FULL ORIENTATION REQUIRED` with available capsule |
| Same-task route is malformed, forked, ineffective, or changed | `FULL ORIENTATION REQUIRED` with available capsule |
| Unrelated task has an attributable malformed historical route | Preserve diagnostic; do not contaminate current task |
| Base guard, forbidden root, or required target binding fails | `START GUARD: FAIL` |
| `wait_threads` succeeds | Continue cursor-based monitoring |
| Wait handler is missing/unavailable and `read_thread` succeeds | Continue bounded snapshot monitoring |
| Both monitoring paths are unavailable or ambiguous | Preserve identity and report one tooling blocker; no redispatch |

## 8. Verification Contract

Implementation uses RED→GREEN tests and the smallest sufficient profile.

### Fast resume

- a malformed route attributable to the expected task fails closed;
- malformed historical routes attributable only to unrelated tasks do not change an otherwise clean expected-task result;
- an unattributable malformed route fails closed;
- legacy/current-route fallback includes route body, Pipeline state, target state, mailbox state, reasons, and no-effect authority;
- canonical `Accepted target HEAD` and `## Target Allowed Paths` parse exactly;
- the existing fast-pass corpus and independent reference classifier remain aligned; and
- collection mutates no cursor, index, ref, lock, or worktree byte.

### Writer and task adapters

- synchronized Codex surfaces require the supported scoped first attempt only for an already-authorized exact fixed-writer action in the known managed context;
- the surfaces forbid direct mailbox writes, alternate writers, generic escalation, and security weakening;
- monitoring uses wait/cursor first and bounded read-only snapshots only on handler unavailability;
- fallback preserves dispatch identity and cannot cause duplicate dispatch; and
- task routing continues to grant no seat or external-effect authority.

### Required commands

At minimum, the implementation range runs:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_mailbox_writer.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

If `scripts/route_lineage.py` changes, its focused route-lineage tests are added to the plan after impact analysis. The final range must pass `git diff --check`, exact-path scope validation, current route validation, and fresh non-author Operator review.

## 9. Ownership, Rollout, And Rollback

One Director owns the complete implementation range so the resume code and synced protocol surfaces do not receive competing edits. A different-model, non-author Operator reviews the exact committed range and alone issues GO, NITS, or FAIL.

The change is local and backward compatible:

- writer bytes and lock semantics do not change;
- legacy route labels continue to parse;
- legacy routes still require full orientation;
- normal `wait_threads` behavior remains preferred; and
- no app, product, dependency, remote ref, or service changes.

Rollback is one local revert of the implementation range after separate authority. Because the patch creates no new state store or schema, rollback requires no migration or cleanup. Until Operator GO is coordinator-reconciled, the current behavior remains authoritative and no product work depends on this slice.
