# Live-Caller-Only Terminal Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Leave Pipeline with one compact live protocol path by deleting dormant Phase 1-4, capability, selector, provider, and recovery machinery while retaining the compact pair and fixed mailbox writer.

**Architecture:** One Director writer owns the complete tracked deletion so shared files never have competing writers. The change keeps `scripts/compact_pair_loop.py`, the normal mailbox/cursor formats, and one Git-common-dir writer lock; it removes every unused alternate state model, activation mode, and stale plan. One non-author-model Operator reviews the single committed implementation range, after which the coordinator may perform only the separately listed local cleanup actions.

**Tech Stack:** Python standard library, Bash mailbox shims, Git, pytest, Markdown.

## Global Constraints

- Pipeline only. Do not enter or modify evidence-ledger or any other target repository.
- Apply the terminal rule **live caller or delete**. Tests, plans, fixtures, benchmarks, and self-imports are not production callers.
- Keep `scripts/compact_pair_loop.py`, `coordination/bin/send-event`, `coordination/bin/consume-events`, the common-dir lock, no-follow publication, fsync, no-clobber publication, exact-path staging, and non-author Operator GO/NITS/FAIL authority.
- Keep immutable `coordination/mailbox/sent/`, `coordination/verification/`, `coordination/capacity/`, `DECISIONS.md`, committed `logs/`, and historical handoffs byte-for-byte. Git history is the archive for deleted plans and executable experiments.
- Do not add a compatibility shim, archive index, migration reader, selector tombstone, recovery plan, new status field, or replacement framework.
- Do not activate a writer, create or update `refs/protocol/kernel-activation`, invoke a provider, consult GPT-Pro, use Opus, retry a paid request, consume a cursor, push, merge, or publish externally.
- Commit this plan alone before Task 1 begins so the abuse cases and deletion boundary precede the behavior change. That docs-only plan commit is not an implementation commit and grants no execution authority.
- The tracked implementation is one tightly coupled net-deletion commit from one Director writer. The Operator report is a separate report-only commit required by R-INDEPENDENCE; do not split the implementation into phase commits.
- Execute Tasks 1-3, then Task 5 Steps 1-4; run Task 4 only after Operator GO, and finish with Task 5 Step 5. Task numbering does not authorize pre-verdict cleanup.
- All ordinary Git and test commands begin with `env -u GIT_INDEX_FILE`. Stage only explicit tracked paths; never absorb the ambient untracked root files into the implementation commit.
- A newly discovered production caller protects only its exact dependency. Stop and remove that dependency from the deletion manifest; do not revive a phase or broaden the change.
- Each retained control must name the concrete failure it prevents. A control with no current caller and no failure-backed test is ceremony and is removed.

## Terminal Classification

| Class | Current surfaces | Disposition |
|---|---|---|
| Live and used | `scripts/compact_pair_loop.py`, normal mailbox/cursor tools, Operator verdict authority, fixed common-dir writer lock | Keep and regression-test |
| Implemented but not used | capability benchmark/reporter, capability receipt CLI, compact mapping/reducer/adapter, route-v2 schema/corpora, broad compact surface inventory | Delete executable, schemas, fixtures, and dedicated tests |
| Implemented but not activated | Git activation ref parser, epoch/compact writer modes, governance mirror, reader denial guards | Delete; replace `kernel_activation.py` with fixed `mailbox_writer.py` |
| Planned but not implemented | Phase 4 reader migration, mixed-version operation, compact activation, canaries, observation period, legacy pruning | Retire by deleting the active guide and superseded plan files from HEAD |
| Implemented and used but described incorrectly | compact-pair replacement and operative cross-provider surfaces | Keep runtime; correct prose once |
| Local residue | completed Antigravity scratch files, deleted-provider runtime residue, old worktrees/branches | Delete only proven disposable residue; retain unique branch refs and ambiguous dirty bytes |

Baseline evidence at plan authoring HEAD `88d77d84de68fa40c3813122bfdc40593e833ffa`:

```text
$ wc -l scripts/capability_reducer.py scripts/capability_v1_adapter.py scripts/compact_state_mapping.py
  1313 scripts/capability_reducer.py
  2876 scripts/capability_v1_adapter.py
   478 scripts/compact_state_mapping.py
  4667 total

$ env -u GIT_INDEX_FILE git grep -n -E \
  'capability_baseline_runtime|protocol_effectiveness_report|route_capability|compact_state_mapping|capability_reducer|capability_v1_adapter|route-v2' \
  -- scripts coordination/bin .agents .codex .claude threeway \
  ':!scripts/capability_baseline_runtime.py' \
  ':!scripts/protocol_effectiveness_report.py' \
  ':!scripts/route_capability.py' \
  ':!scripts/compact_state_mapping.py' \
  ':!scripts/capability_reducer.py' \
  ':!scripts/capability_v1_adapter.py'
<no production caller>

$ git grep kernel_activation.py outside its implementation, tests, docs, and immutable history
coordination/bin/consume-events
coordination/bin/send-event
```

## Independent Abuse Cases

- A docs/test-only reference must not be misclassified as a live caller and preserve a dead subsystem.
- A real shell or Python production caller must not be hidden by path exclusions and then broken by deletion.
- Removing selector logic must not remove the shared lock, allow two mailbox writers, follow a symlink, overwrite an existing event, skip fsync, or stage an unintended path.
- Removing reader guards must not weaken target binding, mailbox validation, capacity validation, or Operator-only report publication.
- A stale Director, coordinator, or same-author model must still be unable to publish an authoritative verification report.
- Historical v1-v3 reports must remain readable only through their existing frozen historical checks; no deleted publication state may become active again.
- Local cleanup must not delete a dirty worktree, a branch with commits absent from `main`, or unique user-authored bytes.
- Stale three-way or role prose must not continue to advertise `TaskPublicationStore`, provider receipts, or lane-v-report/v3 as live machinery.

---

### Task 1: Delete the unused Phase 1-2 and capability stacks

**Files:**

- Delete production: `scripts/capability_baseline_runtime.py`, `scripts/protocol_effectiveness_report.py`, `scripts/baselines/capability_first_five_profile_v1.json`, `scripts/route_capability.py`, `scripts/compact_state_mapping.py`, `scripts/capability_reducer.py`, `scripts/capability_v1_adapter.py`
- Delete schemas: `schemas/capability-v1.schema.json`, `schemas/capability-receipt-v1.schema.json`, `schemas/route-v2.schema.json`
- Delete fixtures: `tests/fixtures/compact_state_mapping/v1.json`, `tests/fixtures/compact_kernel/v1_surface_inventory.json`, `tests/fixtures/compact_kernel/v1_misuse_vectors.json`, `tests/fixtures/compact_kernel/v1_to_v2_replay.json`, `tests/fixtures/compact_kernel/v2_replay_vectors.json`
- Delete tests: `tests/unit/test_capability_baseline_runtime.py`, `tests/unit/test_protocol_effectiveness_report.py`, `tests/unit/test_route_capability.py`, `tests/unit/test_capability_security.py`, `tests/unit/test_capability_stateful.py`, `tests/unit/test_lineage_capability_stateful.py`, `tests/unit/test_compact_state_mapping.py`, `tests/unit/test_capability_reducer.py`, `tests/unit/test_capability_reducer_replay.py`, `tests/unit/test_capability_v1_adapter.py`, `tests/unit/test_route_v2_schema_sync.py`, `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `tests/unit/test_kernel_properties.py`, `tests/unit/test_route_lineage.py`
- Preserve unchanged: `logs/capability-first/**`, `coordination/mailbox/sent/**`, `coordination/verification/**`, `coordination/capacity/**`, `DECISIONS.md`

**Interfaces:**

- Consumes: current Markdown routes, capacity packets, mailbox events, and compact-pair request/report validation.
- Produces: no replacement API. All deleted APIs intentionally have zero live consumers.

- [ ] **Step 1: Re-run the production-caller proof against current HEAD**

  ```bash
  env -u GIT_INDEX_FILE git grep -n -E \
    'capability_baseline_runtime|protocol_effectiveness_report|route_capability|compact_state_mapping|capability_reducer|capability_v1_adapter|route-v2' \
    -- scripts coordination/bin .agents .codex .claude threeway \
    ':!scripts/capability_baseline_runtime.py' \
    ':!scripts/protocol_effectiveness_report.py' \
    ':!scripts/route_capability.py' \
    ':!scripts/compact_state_mapping.py' \
    ':!scripts/capability_reducer.py' \
    ':!scripts/capability_v1_adapter.py'
  ```

  Expected: no output. Any output is a real production-caller candidate; inspect it before deleting the named dependency.

- [ ] **Step 2: Remove the production modules, schemas, fixtures, and dedicated tests**

  Use `apply_patch` to delete exactly the paths in this task. Do not delete committed `logs/capability-first/**` or any coordination artifact: those remain historical evidence even though their producers are gone.

- [ ] **Step 3: Remove the shared-test dependencies without weakening unrelated guards**

  In `tests/unit/test_kernel_properties.py`, remove only these imports:

  ```python
  import route_capability
  import test_route_capability as tc
  ```

  Delete the contiguous section beginning `# ---- route_capability.validate_capability ----` and ending immediately before `# ---- packet_state.derive_* ----`. Keep all route-manifest, route-lineage, and packet-state property tests unchanged.

  In `tests/unit/test_route_lineage.py`, replace the obsolete sibling-capability explanation with:

  ```python
  # Bool is an int subclass, so the CAS boundary must require exact int types.
  # This prevents a future JSON/TOML boolean generation from satisfying successor
  # arithmetic even though True == 1.
  ```

- [ ] **Step 4: Prove the remaining live protocol does not import deleted code**

  ```bash
  env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
    tests/unit/test_kernel_properties.py \
    tests/unit/test_route_lineage.py \
    tests/unit/test_route_manifest.py \
    tests/unit/test_protocol_mailbox.py \
    tests/unit/test_compact_pair_loop.py -q
  env -u GIT_INDEX_FILE git grep -n -E \
    'import (route_capability|compact_state_mapping|capability_reducer|capability_v1_adapter)|from scripts import (capability_reducer|capability_v1_adapter|compact_state_mapping)' \
    -- scripts coordination/bin .agents .codex .claude threeway
  ```

  Expected: pytest passes; the import search prints no output.

---

### Task 2: Replace the dormant activation system with one fixed mailbox writer

**Files:**

- Rename/modify: `scripts/kernel_activation.py` → `scripts/mailbox_writer.py`
- Modify shell callers: `coordination/bin/send-event`, `coordination/bin/consume-events`
- Modify readers: `.agents/skills/four-seat-protocol/scripts/seat_status.py`, `scripts/continuation_readiness.py`, `scripts/ledger_start_guard.py`, `scripts/mailbox_monitor.py`, `scripts/protocol_capacity_board.py`, `scripts/protocol_doctor.py`, `scripts/route_lineage.py`, `scripts/status.py`
- Modify binding: `governance.toml`, `scripts/target_binding.py`
- Rename/modify test: `tests/unit/test_kernel_activation.py` → `tests/unit/test_mailbox_writer.py`
- Modify tests: `tests/unit/test_coordination_tooling.py`, `tests/unit/test_target_binding.py`

**Interfaces:**

- `writer_fence(repo_root: Path | str) -> Iterator[None]` owns the unchanged Git-common-dir `flock`.
- `mailbox_writer.py send-event-finalize --repo-root ... --candidate ... --final-relative ...` atomically publishes and stages one event.
- `mailbox_writer.py consume-events {director|director2|operator|operator2|coordinator|coordinator2} --repo-root ... [--to ISO_TIMESTAMP]` atomically replaces and stages one cursor.
- No selector read/update API, epoch, alternate writer, or reader guard remains.

- [ ] **Step 1: Rewrite the focused tests around the fixed behavior**

  Rename `tests/unit/test_kernel_activation.py` to `tests/unit/test_mailbox_writer.py`. Delete selector-blob, governance-mirror, compact-mode, selector-reread, and named-reader-denial tests. Keep and adapt the shared-worktree lock, mode-0600, envelope mismatch, cursor format, no-mutation, and staging tests to import `mailbox_writer`.

  In `tests/unit/test_coordination_tooling.py`:

  - remove the unused `json` import;
  - copy `scripts/mailbox_writer.py` into fixtures;
  - stop creating `[protocol.kernel]` in fixture `governance.toml`;
  - delete `_install_compact_selector` and both selector-denial tests;
  - retain all ordinary-event, Operator-report, no-clobber, temporary-file, and cursor tests.

  In `tests/unit/test_target_binding.py`, remove `FrozenInstanceError`, `KernelMirror`, `_replace_kernel_mirror`, and every kernel-mirror test. Keep all target registry, resolution-order, path-override, and fail-closed tests.

- [ ] **Step 2: Implement only the fixed lock and finalizers**

  Rename the production file and reduce its top-level boundary to this shape while retaining the existing `_git`, `_stage`, `_send_event_finalize`, `_consume_events_finalize`, filename/envelope validation, fsync, link/no-clobber, rollback, and CLI behavior:

  ```python
  class MailboxWriterError(RuntimeError):
      """The fixed mailbox writer or repository boundary is invalid."""


  @contextlib.contextmanager
  def writer_fence(repo_root: Path | str) -> Iterator[None]:
      root = Path(repo_root).resolve(strict=True)
      common_raw = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
      common = Path(common_raw.decode("utf-8", "strict").strip()).resolve(strict=True)
      flags = (
          os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
          | getattr(os, "O_NOFOLLOW", 0)
      )
      # Keep the established lock filename so old and new worktree shims cannot
      # split the writer lock during the local cutover.
      fd = os.open(common / "protocol-kernel-writer.lock", flags, 0o600)
      try:
          os.fchmod(fd, 0o600)
          if not stat.S_ISREG(os.fstat(fd).st_mode):
              raise MailboxWriterError("writer lock is not a regular file")
          fcntl.flock(fd, fcntl.LOCK_EX)
          yield
      finally:
          os.close(fd)
  ```

  Change both finalizers to `with writer_fence(root):`. Remove `KernelSelection`, `read_selection`, `_mirror`, `_selector_oid`, `_require_v1_reader`, `_reader_guard`, selector constants, JSON/TOML parsing, epoch/writer parameters, and compact-mode vocabulary. Change the CLI program/error prefix to `mailbox_writer.py` / `mailbox-writer`.

- [ ] **Step 3: Point the two shell tools at the fixed writer**

  In both shell scripts, use:

  ```bash
  MAILBOX_WRITER="$TOOL_ROOT/scripts/mailbox_writer.py"
  ```

  Replace every `KERNEL_FINALIZER` reference with `MAILBOX_WRITER`. Update comments and missing-tool errors to say `mailbox writer`; do not change event/report validation or trusted-Python selection.

- [ ] **Step 4: Remove hypothetical-mode guards from live readers and target binding**

  Delete `from kernel_activation import _reader_guard` and the corresponding early-return block from each named reader. Do not change the reader's real parsing, validation, or exit codes.

  Remove `[protocol.kernel]` from `governance.toml`. In `scripts/target_binding.py`, delete `KernelMirror`, `load_kernel_mirror`, the call in `main`, and the `kernel mirror:` output. The target registry remains fail-closed on its actual `[binding]`, `[targets.*]`, and `[paths]` fields.

- [ ] **Step 5: Run the fixed-writer and live-reader regressions**

  ```bash
  env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
    tests/unit/test_mailbox_writer.py \
    tests/unit/test_coordination_tooling.py \
    tests/unit/test_target_binding.py \
    tests/unit/test_target_binding_properties.py \
    tests/unit/test_protocol_capacity.py \
    tests/unit/test_route_lineage.py \
    tests/unit/test_seat_status_all.py \
    tests/unit/test_status.py \
    tests/unit/test_compact_pair_loop.py -q
  env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event coordination/bin/consume-events
  ```

  Expected: all tests pass and both Bash scripts parse successfully.

---

### Task 3: Leave one truthful documentation and plan surface

**Files:**

- Modify: `ARCHITECTURE.md`, `coordination/README.md`, `docs/protocol/codex/continuation.md`, `docs/protocol/claude/continuation.md`, `.claude/agents/readiness-bridge.md`
- Modify: `docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md`, `docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md`, `docs/protocol/threeway/ONBOARDING.md`, `docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`
- Delete obsolete guide/doc: `docs/protocol/capabilities.md`, `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
- Delete superseded Phase 1-4 plans: `docs/superpowers/plans/2026-07-15-capability-phase1-surface-inventory-closure.md`, `docs/superpowers/plans/2026-07-15-capability-compact-reducer-phase2.md`, `docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md`, `docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md`, `docs/superpowers/plans/2026-07-16-compact-kernel-phase4-activation.md`, `docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md`
- Delete superseded recovery/provider plans: `docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md`, `docs/superpowers/plans/2026-07-16-ppl-publication-race-correction.md`, `docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md`, `docs/superpowers/plans/2026-07-16-recovery-retirement-publication-reconciliation.md`, `docs/superpowers/plans/2026-07-16-target-aware-evidence-ledger-opus-bridge.md`, `docs/superpowers/plans/2026-07-16-provider-tools-targeted-decommission.md`, `docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md`, `docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction.md`, `docs/superpowers/plans/2026-07-17-compact-pair-loop-replacement.md`
- Delete superseded design specs: `docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-design.md`, `docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction-design.md`, `docs/superpowers/specs/2026-07-16-operative-doc-surface-compaction-proposal.md`, `docs/superpowers/specs/2026-07-16-opus-chatgpt-pro-targeted-decommission-design.md`, `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md`, `docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md`
- Preserve unchanged: `AGENTS.md`, `DECISIONS.md`, historical handoffs, mailbox events, verification scopes, capacity packets, committed logs

**Interfaces:**

- `ARCHITECTURE.md` describes only files and behavior present at final HEAD.
- All adoption/role surfaces point once to `scripts/codex_protocol_model.py` for the compact-pair invariant instead of mirroring lifecycle grammar.
- This plan is the sole remaining active plan for this cleanup; deleted plans remain available in Git history.

- [ ] **Step 1: Delete obsolete executable documentation and plans**

  Use `apply_patch` to delete exactly the listed guide, capability doc, plans, and design specs. Do not edit historical artifacts merely to repair their links.

- [ ] **Step 2: Rewrite architecture truth to the retained runtime**

  In `ARCHITECTURE.md`:

  - remove module-map rows for `load_kernel_mirror`, `read_selection`, `_accepted_context_keys`, `reduce_protocol_state`, and `adapt_v1_history`;
  - add `writer_fence` at `scripts/mailbox_writer.py`, describing the common-dir lock and fixed mailbox/cursor finalizers;
  - replace the selector/shadow runtime paragraph with: `The fixed mailbox writer serializes event and cursor publication with one Git-common-dir lock. No activation selector or alternate writer exists.`;
  - update `coordination/bin/send-event` to name `scripts/mailbox_writer.py`;
  - replace Lane-V-v3/publication wording with compact-pair request/report binding;
  - refresh changed line anchors and the verification footer using current source, not old SHAs.

- [ ] **Step 3: Remove stale utility references**

  In `coordination/README.md`, state that `coordination/bin/send-event` and `scripts/check_coordination.py` load the kind registry through `scripts/protocol_mailbox.py`; remove `protocol_effectiveness_report.py`.

  Remove the `protocol_effectiveness_report.py` bullet from the Codex continuation doc and the `docs/protocol/capabilities.md` bullet from the Claude continuation doc.

- [ ] **Step 4: Use one canonical compact-pair pointer on all stale surfaces**

  Replace each live `lane-v-report/v3` / `TaskPublicationStore` paragraph in the four three-way docs and `.claude/agents/readiness-bridge.md` with exactly:

  ```markdown
  Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. This
  surface intentionally does not restate its lifecycle grammar.
  ```

- [ ] **Step 5: Verify documentation and active-surface convergence**

  ```bash
  env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
    tests/unit/test_protocol_prompt_sync.py \
    tests/unit/test_protocol_doc_integrity.py -q
  env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py --sha-refs
  ! rg -n 'TaskPublicationStore|lane-v-report/v3|kernel_activation|refs/protocol/kernel-activation|protocol_effectiveness_report|docs/protocol/capabilities.md' \
    AGENTS.md ARCHITECTURE.md coordination/README.md docs/protocol .agents/skills .codex/agents .claude/agents
  ```

  Expected: tests and document checks pass; the active-surface search prints no output. Historical `DECISIONS.md`, mailbox, scope, handoff, and log references are outside this assertion.

---

### Task 4: Reconcile local untracked files and worktrees without losing unique bytes

**Files/local state:**

- Candidate untracked scratch: `.agents/BRIEFING.md`, `.agents/ORIGINAL_REQUEST.md`, `.agents/handoff.md`, `.agents/orchestrator/`, `.agents/teamwork_preview_explorer_discovery_1/`, `.agents/teamwork_preview_explorer_discovery_2/`, `.agents/teamwork_preview_explorer_discovery_3/`, `.agents/teamwork_preview_worker_alignment_1/`, `.agents/victory_auditor/`, `ORIGINAL_REQUEST.md`, `PROJECT.md`
- Candidate deleted-system residue: `.codex/runtime/`
- Worktrees: every path returned by `git worktree list --porcelain`
- Branches: only local branches currently attached to those worktrees

**Interfaces:**

- Produces no tracked file and no commit.
- A clean worktree may be removed. A branch may be deleted only when `git rev-list --count main..$branch` is `0` in the Step 3 loop.
- A clean worktree with a branch containing commits absent from `main` may be removed, but its branch ref is retained.
- A dirty worktree is retained unless every dirty byte is proven identical to current `main` or belongs to Task 1-3's deletion manifest.

- [ ] **Step 1: Refresh the local-state classification**

  ```bash
  env -u GIT_INDEX_FILE git status --short --branch
  env -u GIT_INDEX_FILE git worktree list --porcelain
  env -u GIT_INDEX_FILE git branch --format='%(refname:short) %(objectname)'
  find .codex/runtime -type f -print 2>/dev/null | sort
  ```

  Expected at the plan baseline: the primary tree has only the listed untracked paths; `compact-phase4-task1` is clean at `main`; the old preservation worktree is dirty; several provider branches retain commits absent from `main`.

- [ ] **Step 2: Delete completed, unreferenced local scratch**

  Reconfirm the Antigravity scratch handoffs say the work is complete. Prove no operative source or instruction reads the scratch/runtime paths:

  ```bash
  ! rg -n \
    'teamwork_preview|victory_auditor|\.agents/orchestrator|\.agents/BRIEFING|\.agents/handoff|\.codex/runtime' \
    AGENTS.md CLAUDE.md scripts coordination/bin docs/protocol .agents/skills .codex/agents .claude/agents
  ```

  Expected: no output. Historical handoffs and `DECISIONS.md` are intentionally outside this operative-surface proof.

  After receiving destructive-command approval at execution time, run exactly:

  ```bash
  /bin/rm -rf -- \
    .agents/BRIEFING.md \
    .agents/ORIGINAL_REQUEST.md \
    .agents/handoff.md \
    .agents/orchestrator \
    .agents/teamwork_preview_explorer_discovery_1 \
    .agents/teamwork_preview_explorer_discovery_2 \
    .agents/teamwork_preview_explorer_discovery_3 \
    .agents/teamwork_preview_worker_alignment_1 \
    .agents/victory_auditor \
    .codex/runtime \
    ORIGINAL_REQUEST.md \
    PROJECT.md
  ```

  Do not stage these paths; they are untracked local residue.

- [ ] **Step 3: Remove clean worktrees and only ancestry-safe branches**

  After receiving destructive-command approval at execution time, run this exact loop. It skips the primary root and every dirty worktree, removes each clean worktree, deletes only branches already contained in `main`, and retains branches with unique commits:

  ```bash
  root=$(env -u GIT_INDEX_FILE git rev-parse --show-toplevel)
  env -u GIT_INDEX_FILE git worktree list --porcelain \
    | awk '/^worktree / {sub(/^worktree /, ""); print}' \
    | while IFS= read -r worktree; do
        [ "$worktree" = "$root" ] && continue
        [ -z "$(env -u GIT_INDEX_FILE git -C "$worktree" status --porcelain)" ] \
          || continue
        branch=$(env -u GIT_INDEX_FILE git -C "$worktree" symbolic-ref --short -q HEAD || true)
        env -u GIT_INDEX_FILE git worktree remove "$worktree"
        if [ -n "$branch" ] && \
           [ "$(env -u GIT_INDEX_FILE git rev-list --count main.."$branch")" = 0 ]; then
          env -u GIT_INDEX_FILE git branch -d "$branch"
        fi
      done
  ```

  The baseline `compact-phase4-task1` worktree is the first expected clean/same-HEAD removal. Do not use `--force` for a clean worktree.

- [ ] **Step 4: Reconcile the dirty preservation worktree**

  For `.worktrees/main-wip-preserve-before-phase2-2026-07-16`, run:

  ```bash
  worktree=.worktrees/main-wip-preserve-before-phase2-2026-07-16
  env -u GIT_INDEX_FILE git -C "$worktree" status --short
  env -u GIT_INDEX_FILE git -C "$worktree" ls-files -m -o --exclude-standard -z \
    | while IFS= read -r -d '' path; do
        working_oid=$(env -u GIT_INDEX_FILE git hash-object "$worktree/$path")
        main_oid=$(env -u GIT_INDEX_FILE git rev-parse "main:$path" 2>/dev/null || printf absent)
        printf '%s|working=%s|main=%s\n' "$path" "$working_oid" "$main_oid"
      done
  ```

  A path is disposable only when its object ID equals `main`, or it is exactly one of the Task 1 deleted production/test/fixture paths or the already-deleted `scripts/chatgpt_pro_consult.py`. Any different `ARCHITECTURE.md`, `governance.toml`, `scripts/codex_protocol_model.py`, `scripts/target_binding.py`, or `tests/unit/test_target_binding.py` byte is ambiguous: retain the worktree and report only those paths, without creating another recovery document.

  If every path is disposable, request destructive-command approval at execution time and run:

  ```bash
  env -u GIT_INDEX_FILE git worktree remove --force \
    .worktrees/main-wip-preserve-before-phase2-2026-07-16
  if [ "$(env -u GIT_INDEX_FILE git rev-list --count \
         main..codex/main-wip-preserve-before-phase2-2026-07-16)" = 0 ]; then
    env -u GIT_INDEX_FILE git branch -d \
      codex/main-wip-preserve-before-phase2-2026-07-16
  fi
  ```

- [ ] **Step 5: Prune administrative worktree metadata and verify the result**

  ```bash
  env -u GIT_INDEX_FILE git worktree prune
  env -u GIT_INDEX_FILE git worktree list
  env -u GIT_INDEX_FILE git status --short --branch
  ```

  Expected: no disposable clean worktree remains; unique branch refs and any genuinely ambiguous dirty worktree remain; the primary root has no listed scratch/runtime residue.

---

### Task 5: Verify, commit the implementation once, and obtain one independent verdict

**Files:**

- Commit: exactly the tracked Task 1-3 changes; this plan must already be in the preceding docs-only plan commit
- Create after commit: one normal compact-pair verify-request and one Operator verification-report under `coordination/mailbox/sent/`
- Do not include: Task 4 local cleanup, committed historical artifacts, or unrelated ambient paths

**Interfaces:**

- Produces one net-deletion implementation commit.
- Produces one non-author-model Operator GO/NITS/FAIL over that exact commit and base.
- GO authorizes no push, merge, activation, provider use, cursor consumption, or further cleanup.

- [ ] **Step 1: Run the complete fresh verification pass**

  ```bash
  env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q
  env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
  env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
  env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event coordination/bin/consume-events
  env -u GIT_INDEX_FILE git diff --check
  wc -l scripts/compact_pair_loop.py scripts/mailbox_writer.py
  ```

  Expected: tests, smoke, doctor, Bash syntax, and diff checks pass. Both retained focused production modules remain below 500 lines and no new recovery module exists.

- [ ] **Step 2: Prove the deleted and inactive mechanisms are absent from active surfaces**

  ```bash
  ! rg -n \
    'capability_baseline_runtime|protocol_effectiveness_report|route_capability|compact_state_mapping|capability_reducer|capability_v1_adapter|route-v2|kernel_activation|refs/protocol/kernel-activation|TaskPublicationStore' \
    scripts coordination/bin AGENTS.md ARCHITECTURE.md coordination/README.md docs/protocol .agents/skills .codex/agents .claude/agents
  env -u GIT_INDEX_FILE git diff --stat
  env -u GIT_INDEX_FILE git diff --name-status
  ```

  Expected: the active-surface search prints no output; the diff is strongly net-negative and contains only this plan's tracked manifest.

- [ ] **Step 3: Create the single implementation commit**

  Immediately refresh `git log --oneline -3`, mailbox bodies, and `git status`. Stage only explicit Task 1-3 paths. Then commit:

  ```bash
  env -u GIT_INDEX_FILE git commit -m "refactor(protocol): remove dormant compact machinery"
  ```

  Expected: one local implementation commit; no push.

- [ ] **Step 4: Run one compact-pair independent review**

  The Director publishes one verify-request naming the exact parent/base, implementation HEAD, author model, assigned non-author-model Operator, changed paths, the Independent Abuse Cases above, and the Task 5 verification commands. The assigned Operator reviews the actual diff and publishes exactly one GO/NITS/FAIL through the fixed mailbox writer.

  Do not repeat unchanged verification. NITS permits only the named nit. FAIL returns the exact finding to the same single writer. GO closes the tracked cleanup.

- [ ] **Step 5: Report the terminal state without another closeout artifact**

  Report in chat:

  - implementation commit and Operator verdict commit;
  - production files retained;
  - dormant/inactive surfaces removed;
  - local worktrees/branches deleted or deliberately retained and why;
  - confirmation that no activation or push occurred.

  Do not create a new recovery plan, status packet, inventory, or handoff unless ownership actually transfers.
