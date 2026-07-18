# Fast-Resume Startup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let an unchanged, already-routed Pipeline seat resume from one freshly derived capsule while preserving the ordinary startup path, exact route truth, non-author review, and separate external-effect authority.

**Architecture:** Replace mailbox-size-proportional route reads with one exact-object batch reader, expose one typed read-only startup snapshot shared by the status renderer and guard, and add an opt-in `--resume-from <path>@<full-commit>` evaluator. The evaluator either proves the current state unchanged, names the evidence requiring ordinary orientation, or preserves an existing hard guard failure. The current command and authority model remain the fallback; no cache, receipt, event, approval token, or coordinator gate is added.

**Tech Stack:** Python 3.11+ standard library, Git plumbing (`ls-tree`, `log`, `cat-file --batch`), pytest, Markdown protocol adapters, and the existing fixed Git-backed mailbox model.

## Global Constraints

- Source design: `docs/superpowers/specs/2026-07-19-fast-resume-startup-design.md@c650080003b14af9517cf1f3336902a1e3bdeef4`.
- The implementation owner chooses the method and may transfer, exchange, split, or reroute ownership through a durable accepted handoff without coordinator approval. Tasks 1 and 2 have disjoint write sets and may run in parallel; Task 3 waits for both. Never run concurrent implementers on the same file.
- Public compatibility, security invariants, and executable acceptance behaviors are binding; private helper names, internal partitioning, and the number of individual test functions are implementation guidance. The owner may simplify or combine them without coordinator approval when the same non-vacuous coverage and reviewable outcome remain.
- A coordinator may maintain this plan and reconcile evidence but does not author the behavior-changing implementation unless the user explicitly assigns that model a Director seat.
- Preflight is advisory. Do not add a pre-implementation `CLEAR` gate. The only acceptance review required by this plan is distinct-seat, different-model, non-author Operator review of the actual implementation range.
- Preserve all existing `route_lineage.py`, `ledger_start_guard.py`, and `seat_status.py` public interfaces and authority/exit semantics. The one intentional ordinary-output change is removal of standalone Git log/status instructions after `seat_status.py` renders those same facts from the shared snapshot. The ordinary guard command remains the compatible full-orientation path.
- Current committed Git and mailbox evidence outranks prose. Every route, parent, proposal, acceptance, finding, and handoff reference remains a canonical full immutable reference.
- Caller input supplies only the expected route ref. It cannot supply ownership, allowed paths, unread state, target identity, replay state, or external-effect authority.
- Version 1 is deliberately conservative: any unread or unavailable mailbox state requires full orientation; any dirty path without an exact committed path attribution requires full orientation; any target HEAD change from the route's pinned target HEAD requires full orientation.
- A fast-resume result never grants push, merge, lock, cursor consume, provider launch, service start, dependency installation, booking, spend, deployment, or any other external effect. External-effect work bypasses fast resume in the Codex adapter and uses its own fresh authority path.
- Fast resume is read-only: it must not write a cache, capsule, cursor, mailbox event, lock, Git index, worktree file, or ref.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest. Refresh `git log --oneline -3` and scoped status immediately before each write, stage, commit, or gate decision. Preserve unrelated peer work and stage exact pathspecs only.
- The under-two-second target is reported, not asserted in CI. Deterministic equivalence and bounded process count are the executable acceptance gates.
- No push, merge, cursor consumption, provider action, target service start, or other remote/external effect is authorized by this plan.

## File Structure

- `scripts/protocol_mailbox.py`: split immutable event parsing from Git proof so the batch reader can reuse the same authority-sensitive parsers.
- `scripts/route_lineage.py`: add the context-managed exact-object batch reader while preserving all existing public loaders and resolvers.
- `scripts/startup_snapshot.py`: add small typed, read-only Pipeline/target/mailbox collectors shared by guard and presentation.
- `.agents/skills/four-seat-protocol/scripts/seat_status.py` and its `.claude/` mirror: render existing status output from the shared collectors without becoming an authority gate; keep only their provider-specific command-path docstrings different.
- `scripts/ledger_start_guard.py`: add exact route resolution, eligibility evaluation, compact capsule rendering, and the optional resume CLI.
- `scripts/measure_ledger_start_guard.py`: report elapsed time and Git process count without turning wall-clock time into a test gate.
- `scripts/codex_protocol_model.py`: hold the one canonical optional resume command and adapter rules.
- `AGENTS.md`, `.agents/skills/four-seat-protocol/SKILL.md`, `docs/protocol/codex/continuation.md`, and `docs/protocol/codex/ledger-cli-adoption.md`: thin eligibility and fallback instructions only.
- `tests/unit/test_protocol_mailbox.py`, `tests/unit/test_route_lineage.py`, `tests/unit/test_seat_status_all.py`, `tests/unit/test_ledger_fast_resume.py`, `tests/unit/test_codex_ledger_bridge.py`, and `tests/unit/test_protocol_prompt_sync.py`: focused TDD and compatibility coverage.
- `logs/fast-resume-startup-benchmark.json`: one machine-readable local-checkout measurement produced by the committed instrument after implementation.

---

### Task 1: Batch exact committed route and ownership evidence

**Files:**
- Modify: `scripts/protocol_mailbox.py`
- Modify: `scripts/route_lineage.py`
- Modify: `tests/unit/test_protocol_mailbox.py`
- Modify: `tests/unit/test_route_lineage.py`

**Interfaces:**

```python
def parse_committed_event_text(value: str, text: str) -> CommittedEventRef: ...
def parse_ownership_proposal_statement(
    event: CommittedEventRef,
) -> OwnershipProposalStatement: ...
def parse_ownership_acceptance_statement(
    event: CommittedEventRef,
) -> OwnershipAcceptanceStatement: ...
def parse_takeover_evidence_statement(
    event: CommittedEventRef,
) -> TakeoverEvidenceStatement: ...
def parse_takeover_confirmation_statement(
    event: CommittedEventRef,
) -> TakeoverConfirmationStatement: ...

class RouteBatchReader:
    def __init__(self, root: Path) -> None: ...
    def __enter__(self) -> RouteBatchReader: ...
    def __exit__(self, exc_type, exc, traceback) -> None: ...
    def candidate_routes(self) -> tuple[LineageRoute, ...]: ...
    def load_route_ref(self, route_ref: str) -> LineageRoute: ...
    def load_task_routes(self, task_id: str) -> list[LineageRoute]: ...
    def load_all_routes(self) -> list[LineageRoute]: ...
    @property
    def issues(self) -> tuple[str, ...]: ...
```

Keep these compatibility wrappers and constructor shapes unchanged:

```python
def load_committed_event_ref(root: Path, value: str) -> CommittedEventRef: ...
def load_routes(root: Path) -> list[LineageRoute]:
    with RouteBatchReader(root) as reader:
        return reader.load_all_routes()
```

- [ ] **Step 1: Refresh the owned scope**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/protocol_mailbox.py scripts/route_lineage.py \
  tests/unit/test_protocol_mailbox.py tests/unit/test_route_lineage.py
```

Expected: no unexplained peer edit overlaps these four paths. If one does, refresh and hand off or narrow ownership; do not overwrite it.

- [ ] **Step 2: Write failing pure-parser and batch-reader tests**

Add focused tests covering:

```python
def test_pure_event_parser_matches_existing_git_backed_loader(): ...
def test_pure_statement_parsers_preserve_duplicate_and_mismatch_rejection(): ...
def test_batch_candidate_scan_uses_exact_head_bodies_before_task_filter(): ...
def test_batch_task_load_includes_every_same_task_route_and_rejects_fork(): ...
def test_batch_task_load_skips_immutable_validation_for_unrelated_tasks(): ...
def test_batch_git_process_count_is_bounded_for_one_and_many_routes(): ...
def test_batch_exact_ref_preserves_commit_type_mode_and_envelope_checks(): ...
def test_batch_delete_readd_same_filename_binds_current_tree_blob(): ...
def test_batch_dirty_worktree_never_replaces_committed_body(): ...
def test_batch_unreadable_object_fails_closed_in_full_loader(): ...
def test_batch_malformed_route_shaped_event_is_visible_to_resume(): ...
def test_batch_reader_closes_cat_file_on_success_and_error(): ...
def test_non_git_route_loading_remains_compatible(): ...
def test_load_routes_wrapper_matches_batch_full_results(): ...
def test_route_lineage_check_cli_output_and_exit_codes_remain_compatible(): ...
```

The process-count test must count both `subprocess.run` and long-lived `subprocess.Popen` launches. Use equivalent repositories containing one route and at least 500 unrelated route-shaped events; require the many-route reader count to remain equal to the one-route count and no greater than six. Keep the existing delete/re-add and same-task fork tests active.

- [ ] **Step 3: Run the focused tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_route_lineage.py -q
```

Expected: the new tests fail because the pure parsers and `RouteBatchReader` do not exist. Existing tests should not gain unrelated failures.

- [ ] **Step 4: Extract pure immutable-event parsers without weakening proof**

Move only body parsing into the five pure parser functions. Keep `load_committed_event_ref()` and the four existing statement loaders as Git-proof wrappers over those parsers. Preserve all current checks:

- canonical lowercase 40-hex commit and normalized mailbox path;
- commit object type and exact `commit:path` object existence;
- regular-file mode `100644`;
- exact fixed-writer envelope, timestamp, and filename-derived sender identity;
- duplicate/missing/mismatched statement fields; and
- no working-tree fallback.

The batch reader must call these same pure parsers after proving the object metadata; it must not duplicate or relax their semantics.

- [ ] **Step 5: Implement one bounded Git reader**

Use a fixed number of Git launches:

1. one `git --no-replace-objects ls-tree -r -z HEAD -- coordination/mailbox/sent` for current paths, modes, and blob OIDs;
2. one `git --no-replace-objects -c diff.renames=false log --full-history` stream for exact-path introduction history, with no `--follow`;
3. one long-lived `git --no-replace-objects cat-file --batch` process for exact blobs, commit/tree objects, `commit:path` expressions, parent/proposal/acceptance evidence, object-type checks, and cached raw-tree traversal for exact path modes; and
4. at most the small fixed repository-identity setup calls allowed by the six-process test.

`candidate_routes()` must first obtain every candidate's exact committed HEAD body. Only then may the guard narrow by target keyword and task. `load_task_routes(task_id)` must validate every overlapping same-task route and immutable ownership reference so a fork cannot disappear behind filtering. `load_route_ref()` must load the exact expected historical route body even when it is no longer the current tree winner. Batch failure is an explicit exception/result, never an empty route set.

For exact-path introduction history, pair each logged commit/path with its
`commit:path` blob through the batch process and select the newest exact-path
commit whose blob OID equals the current HEAD-tree blob. Never use `--follow`;
copy similarity must not change current-path chronology. Record a malformed
route-shaped mailbox event in `issues` instead of silently treating it as an
unrelated non-route. The ordinary compatibility wrapper may preserve its
existing filtering, but resume must choose full orientation when unresolved
candidate issues could affect route truth.

Resolve historical path mode and object identity by walking cached raw commit
and tree objects through that same `cat-file --batch` process. Do not reintroduce
one `ls-tree` subprocess per immutable reference; the batch path must still
prove mode `100644` and blob type exactly.

Preserve:

- the first two positional `LineageRoute` fields and all current defaults;
- sorted path ordering and non-Git fixture fallback;
- exact-current-tree delete/re-add semantics;
- exact committed body in `LineageRoute.body`;
- final working-tree byte comparison for the selected route; and
- the existing `route_lineage.py --check` contract.

- [ ] **Step 6: Run compatibility and bounded-process tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_kernel_properties.py \
  tests/unit/test_target_binding.py -q
```

Expected: PASS, including the constant process-count assertion, delete/re-add regression, same-task fork failure, and legacy wrapper compatibility.

- [ ] **Step 7: Commit only Task 1**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/protocol_mailbox.py scripts/route_lineage.py \
  tests/unit/test_protocol_mailbox.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git diff --check -- \
  scripts/protocol_mailbox.py scripts/route_lineage.py \
  tests/unit/test_protocol_mailbox.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git add \
  scripts/protocol_mailbox.py scripts/route_lineage.py \
  tests/unit/test_protocol_mailbox.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "perf(protocol): batch exact route evidence"
```

---

### Task 2: Share one typed read-only startup snapshot

**Files:**
- Create: `scripts/startup_snapshot.py`
- Modify: `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- Modify: `.claude/skills/four-seat-protocol/scripts/seat_status.py`
- Modify: `tests/unit/test_seat_status_all.py`
- Create: `tests/unit/test_startup_snapshot.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class GitPathState:
    status: str
    path: str
    original_path: str | None = None

@dataclass(frozen=True)
class GitSnapshot:
    root: Path
    head: str | None
    branch: str | None
    recent_commits: tuple[str, ...]
    dirty_paths: tuple[GitPathState, ...]
    errors: tuple[str, ...]

@dataclass(frozen=True)
class MailboxSnapshot:
    seat: str
    cursor: str | None
    unread_refs: tuple[str, ...]
    unavailable_reason: str | None

def collect_git_snapshot(root: Path, *, commits: int = 5) -> GitSnapshot: ...
def collect_mailbox_snapshot(root: Path, seat: str) -> MailboxSnapshot: ...
```

- [ ] **Step 1: Refresh the owned scope**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/startup_snapshot.py \
  .agents/skills/four-seat-protocol/scripts/seat_status.py \
  .claude/skills/four-seat-protocol/scripts/seat_status.py \
  tests/unit/test_seat_status_all.py tests/unit/test_startup_snapshot.py
```

- [ ] **Step 2: Write failing snapshot and compatibility tests**

Add tests covering:

```python
def test_git_snapshot_returns_full_head_branch_log_and_exact_dirty_paths(): ...
def test_git_snapshot_parses_rename_and_untracked_paths_without_loss(): ...
def test_git_snapshot_clears_inherited_git_index_file(): ...
def test_git_snapshot_reports_unavailable_state_instead_of_clean_state(): ...
def test_mailbox_snapshot_uses_live_ref_bus_cursor_without_consuming_it(): ...
def test_mailbox_snapshot_surfaces_legacy_filenames_and_unavailable_bus(): ...
def test_snapshot_collection_changes_no_cursor_index_ref_or_worktree_byte(): ...
def test_seat_status_single_and_all_rendering_remain_compatible(): ...
def test_codex_and_claude_status_adapters_share_behavior(): ...
```

Use `git status --porcelain=v1 -z --untracked-files=all` fixtures so rename and unusual path handling are non-vacuous. Snapshot errors must remain visible; they must never become an empty dirty list or zero unread count.

- [ ] **Step 3: Run the focused tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_startup_snapshot.py \
  tests/unit/test_seat_status_all.py -q
```

Expected: collection fails because `startup_snapshot.py` and its typed collectors do not exist.

- [ ] **Step 4: Implement the read-only collectors**

The Git collector must remove inherited `GIT_*` overrides, use deterministic locale, return the full 40-character HEAD, preserve exact dirty paths, and expose every command/read failure in `errors`. The mailbox collector must:

- use `bus_unread.bus_unread_events()` once for migrated cursors and render refs with `bus_unread.format_unread()`;
- use addressed immutable mailbox filenames for legacy ISO cursors;
- distinguish reachable zero unread from unavailable state; and
- never call either cursor-consumption path.

Keep this module descriptive. It does not decide authority, infer relevance, or mutate anything.

- [ ] **Step 5: Make `seat_status.py` a presentation adapter over the collectors**

Refactor both provider copies' HEAD, recent-log, and mailbox rendering to consume the new snapshots while retaining their current CLI, successful-render exit code, sections, unread warnings, `--all` behavior, and optional wave/smoke behavior. Keep their only intentional difference in the provider-specific usage path. Do not add gating semantics to `seat_status.py`. Existing output assertions may be adjusted only for the newly surfaced exact dirty-path line; do not remove existing facts.

- [ ] **Step 6: Run the focused and status regression suites**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_startup_snapshot.py \
  tests/unit/test_seat_status_all.py \
  tests/unit/test_status.py -q
```

Expected: PASS and the no-mutation fixture proves cursor, index, refs, and worktree bytes are identical before and after collection.

- [ ] **Step 7: Commit only Task 2**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/startup_snapshot.py \
  .agents/skills/four-seat-protocol/scripts/seat_status.py \
  .claude/skills/four-seat-protocol/scripts/seat_status.py \
  tests/unit/test_seat_status_all.py tests/unit/test_startup_snapshot.py
env -u GIT_INDEX_FILE git diff --check -- \
  scripts/startup_snapshot.py \
  .agents/skills/four-seat-protocol/scripts/seat_status.py \
  .claude/skills/four-seat-protocol/scripts/seat_status.py \
  tests/unit/test_seat_status_all.py tests/unit/test_startup_snapshot.py
env -u GIT_INDEX_FILE git add \
  scripts/startup_snapshot.py \
  .agents/skills/four-seat-protocol/scripts/seat_status.py \
  .claude/skills/four-seat-protocol/scripts/seat_status.py \
  tests/unit/test_seat_status_all.py tests/unit/test_startup_snapshot.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): share read-only startup state"
```

---

### Task 3: Add the opt-in resume evaluator and compact capsule

**Files:**
- Modify: `scripts/ledger_start_guard.py`
- Create: `tests/unit/test_ledger_fast_resume.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`
- Modify: `tests/unit/test_target_binding.py`

**Interfaces:**

```python
class ResumeClassification(str, Enum):
    FAST_RESUME_PASS = "FAST RESUME: PASS"
    FULL_ORIENTATION_REQUIRED = "FULL ORIENTATION REQUIRED"
    START_GUARD_FAIL = "START GUARD: FAIL"

@dataclass(frozen=True)
class RouteGuidance:
    base: str | None = None
    worktree: str | None = None
    accepted_target_head: str | None = None
    allowed_paths: tuple[str, ...] = ()

@dataclass(frozen=True)
class ResumeEvidence:
    expected_route_ref: str
    current_route_ref: str | None
    route: route_lineage.LineageRoute | None
    pipeline: startup_snapshot.GitSnapshot
    target: startup_snapshot.GitSnapshot | None
    mailbox: startup_snapshot.MailboxSnapshot
    guidance: RouteGuidance
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class ResumeResult:
    classification: ResumeClassification
    lines: tuple[str, ...]
    reasons: tuple[str, ...]

def resolve_latest_ledger_route(
    root: Path,
    target: target_binding.TargetBinding | None = None,
    *,
    reader: route_lineage.RouteBatchReader | None = None,
) -> route_lineage.LineageRoute | None: ...

def parse_route_guidance_body(body: str) -> RouteGuidance: ...

def _build_guard_from_route(
    *,
    seat: str,
    root: Path,
    route: route_lineage.LineageRoute | None,
    kernel: Path,
    wave: int,
    target: target_binding.TargetBinding,
) -> GuardResult: ...

def build_resume(
    *,
    seat: str,
    root: Path,
    resume_from: str,
    kernel: Path = PIPELINE_KERNEL,
    wave: int = 2,
    target_name: str | None = None,
    binding_root: Path | None = None,
) -> ResumeResult: ...
```

Keep `find_latest_ledger_route(...) -> Path | None`, `route_guidance(path)`, `GuardResult`, `build_guard()`, and ordinary guard classifications/exit semantics as compatibility wrappers/paths. Its rendered command list intentionally stops repeating standalone Git log/status after `seat_status.py` renders them.

- [ ] **Step 1: Refresh the owned scope**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/ledger_start_guard.py tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_target_binding.py
```

- [ ] **Step 2: Write the resume classification tests first**

Cover the complete three-way contract:

```python
def test_unchanged_exact_route_clean_target_and_zero_unread_passes(): ...
def test_ordinary_cli_without_resume_from_preserves_guard_semantics_and_uses_one_status_snapshot(): ...
def test_malformed_missing_or_historical_expected_ref_requires_full_orientation(): ...
def test_replaced_forked_or_ineffective_route_requires_full_orientation(): ...
def test_changed_route_worktree_binding_or_target_head_requires_full_orientation(): ...
def test_changed_or_ambiguous_ownership_requires_full_orientation(): ...
def test_any_unread_or_unavailable_mailbox_state_requires_full_orientation(): ...
def test_exact_committed_allowed_paths_surface_attributable_wip(): ...
def test_missing_ambiguous_or_out_of_lane_dirty_paths_require_full_orientation(): ...
def test_pipeline_dirty_state_requires_full_orientation(): ...
def test_resume_preserves_valid_seats_and_rejects_coordinator2(): ...
def test_batch_unavailable_falls_back_to_ordinary_orientation(): ...
def test_existing_kernel_route_or_binding_failure_remains_start_guard_fail(): ...
def test_resume_resolves_route_once_and_guard_git_processes_are_bounded(): ...
def test_full_orientation_is_exit_zero_and_never_prints_blocked(): ...
def test_fast_capsule_contains_exact_body_state_ownership_and_no_effect_authority(): ...
def test_resume_collection_mutates_no_cursor_index_ref_lock_or_worktree_byte(): ...
def test_batch_and_reference_collectors_make_equal_decisions_over_shared_corpus(): ...
```

The shared corpus must include legacy and autonomous routes, accepted transfer/exchange lineage, same-task forks, route replacement, unread/unavailable state, clean and dirty targets, changed target HEAD, and malformed Git output. Build the reference evidence with the existing non-batch proof functions in test code and compare its final classification with the production batch path.

- [ ] **Step 3: Run resume tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_target_binding.py -q
```

Expected: the new resume tests fail because the option, evidence type, and evaluator do not exist; ordinary guard tests remain green.

- [ ] **Step 4: Add strict route guidance parsing**

Parse guidance from the selected route's exact committed `LineageRoute.body`, not its mutable working-tree file. Accept only single unambiguous fields for `Target worktree`/`Route worktree`, `Accepted target HEAD`/`Target reviewed head`, and one exact `## Allowed Paths` or `## Target Allowed Paths` bullet section. Require a full lowercase target SHA. Reject duplicate headings/fields, absolute or parent-traversal paths, wildcard patterns, duplicate paths, and prose-inferred scope. Keep `route_guidance(path)` as the ordinary compatibility wrapper.

For version 1:

- clean target plus matching pinned HEAD needs no allowed-path section;
- dirty target can pass only when every exact dirty path is within the committed allowed-path list and the pinned HEAD still matches;
- missing path attribution, Pipeline dirty state, or a changed target HEAD requires full orientation.

- [ ] **Step 5: Resolve the exact current route once**

Refactor the existing selection into `resolve_latest_ledger_route()` so the batch reader and selected `LineageRoute` survive through evaluation. Preserve the current target keyword rules, legacy-resolution behavior, autonomous same-task fork rejection, working-tree byte check, and `find_latest_ledger_route()` return type.

The expected `--resume-from` ref must be canonical and readable, but it is only an expectation. Pass only when its ref exactly equals the freshly resolved effective route. Do not compare filename recency alone.

Extract `_build_guard_from_route()` from `build_guard()` so ordinary and resume
paths apply the same hard checks to the same resolved object. `build_guard()`
remains the public compatibility wrapper. `build_resume()` opens one batch
reader, resolves once, passes that route through the shared hard checks, and
keeps the reader alive for exact expected-ref and lineage evidence. It must not
call the public wrapper and repeat route discovery.

- [ ] **Step 6: Implement fail-conservative eligibility**

Run the existing hard checks through `_build_guard_from_route()` first. If they fail, return `START GUARD: FAIL`. Otherwise collect Pipeline, target, mailbox, exact-route, and ownership evidence once and evaluate:

- exact expected/current route equality;
- valid effective route lineage and ownership at its immutable parent/revision;
- target worktree top-level identity and Git common-dir relationship to the registered target;
- matching pinned target HEAD;
- clean or exactly attributed dirty paths;
- clean Pipeline worktree; and
- reachable zero unread state.

Do not require the invoking seat to be an owner merely to perform a routed read-only review; print current owners instead. The adapter/user task still determines whether the seat is doing local implementation or review, and the guard grants neither role nor effect authority.

Use these exit semantics:

| Classification | Exit | Meaning |
|---|---:|---|
| `FAST RESUME: PASS` | 0 | Exact unchanged state proved; proceed only within the already-routed local outcome. |
| `FULL ORIENTATION REQUIRED` | 0 | Advisory fallback; print exact reasons and the ordinary startup command/actions. |
| `START GUARD: FAIL` | 1 | Existing hard kernel, route, or target-binding boundary failed. |

Malformed expectation input, unavailable batch plumbing, unread ambiguity, and unprovable state select full orientation rather than manufacturing `BLOCKED`. Argparse misuse remains exit 2.

- [ ] **Step 7: Render one self-contained capsule**

For `FAST RESUME: PASS`, print exactly one derived capsule containing:

- classification and concrete seat;
- current Pipeline full HEAD, branch, and dirty state;
- exact route ref and exact committed route body;
- task ID, revision, current owners, and immutable finding refs;
- target name, registered repo, exact worktree, full HEAD, and dirty paths;
- unread state;
- routed outcome; and
- `External effects authorized: none by fast resume`.

For full orientation, print the classification, stable reason codes plus human-readable evidence, and the existing ordinary startup actions without duplicating `git log`/`git status` commands already rendered by the status snapshot. Do not write the capsule to disk.

Update `first_commands()` so the ordinary path invokes `seat_status.py` once
and no longer prints separate `git log` and `git status` commands. Preserve its
guard rerun, exact route-body read, ledger bridge read, target worktree warning,
target status, and coordinator boundary. Keep the ledger guard's existing five
valid identities; do not silently add `coordinator2` merely because the generic
status renderer can display it.

- [ ] **Step 8: Run focused and differential tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_startup_snapshot.py \
  tests/unit/test_seat_status_all.py \
  tests/unit/test_codex_ledger_bridge.py -q
```

Expected: PASS; ordinary output compatibility, three classifications, no mutation, exact route equality, and batch/reference differential decisions are all exercised.

- [ ] **Step 9: Commit only Task 3**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/ledger_start_guard.py tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE git diff --check -- \
  scripts/ledger_start_guard.py tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE git add \
  scripts/ledger_start_guard.py tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add unchanged-lane fast resume"
```

---

### Task 4: Keep adapters thin, measure, and prepare actual-diff review

**Files:**
- Create: `scripts/measure_ledger_start_guard.py`
- Create: `logs/fast-resume-startup-benchmark.json`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `AGENTS.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/codex/ledger-cli-adoption.md`

**Interfaces:**

```python
LEDGER_CLI_BRIDGE["guard_resume_command"] = (
    "scripts/ledger_start_guard.py --seat <seat> --wave 2 "
    "--resume-from <route-path>@<full-commit>"
)
```

Benchmark JSON schema:

```json
{
  "schema": "ledger-start-guard-benchmark-v1",
  "classification": "FAST RESUME: PASS",
  "elapsed_seconds": 0.0,
  "git_processes": 0,
  "pipeline_head": "<full-sha>",
  "resume_from": "<route-path>@<full-sha>"
}
```

- [ ] **Step 1: Refresh the owned scope**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/measure_ledger_start_guard.py scripts/codex_protocol_model.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md .agents/skills/four-seat-protocol/SKILL.md \
  docs/protocol/codex/continuation.md \
  docs/protocol/codex/ledger-cli-adoption.md \
  logs/fast-resume-startup-benchmark.json
```

- [ ] **Step 2: Write prompt-sync and benchmark tests first**

Add assertions that:

- the canonical model renders both the unchanged ordinary command and the optional resume command;
- adapters use fast resume only for a named seat/coordinator continuing an unchanged already-routed local implementation or review;
- fresh, transplanted, ambiguous, or external-effect requests use ordinary fresh orientation;
- every rendered resume instruction says it grants no effect authority;
- adapters name the three classifications and make full orientation an advisory fallback, not `BLOCKED`;
- the benchmark instrument emits the exact JSON keys and counts `run` plus `Popen` launches; and
- elapsed time is serialized but never asserted against two seconds in pytest.

- [ ] **Step 3: Run the adapter tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_protocol_prompt_sync.py -q
```

Expected: new assertions fail because the canonical resume command and adapter text are absent.

- [ ] **Step 4: Add one canonical rule and thin references**

Add `guard_resume_command` and concise eligibility/fallback rules to `LEDGER_CLI_BRIDGE`; update `render_ledger_start_guard()` from that source. The four text adapters should say only:

1. ordinary startup remains required for fresh, transplanted, ambiguous, or external-effect work;
2. an unchanged already-routed local continuation may pass its exact current route ref to the optional command;
3. `FULL ORIENTATION REQUIRED` means run the ordinary startup path; and
4. no fast-resume output grants external-effect authority.

Do not copy the eligibility checklist into every adapter. Do not modify concrete Director/Operator role prompts unless a focused prompt-sync test proves an actual contradiction; the umbrella four-seat skill and canonical model remain the routing source.

- [ ] **Step 5: Implement the read-only benchmark instrument**

`scripts/measure_ledger_start_guard.py` accepts the same seat, wave, target, and exact resume ref, plus optional `--output`. It calls the production evaluator once, wraps `subprocess.Popen` so both `subprocess.run` and direct long-lived processes are counted, measures with `time.perf_counter()`, and writes/prints the JSON schema above. It must propagate the evaluator classification, never alter that classification, and never treat elapsed time as authority or a process exit gate.

Run it against the implementation owner's current exact routed continuation. Use the immutable route ref printed by the ordinary guard; do not infer it from filename recency:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/measure_ledger_start_guard.py \
  --seat <current-owner-seat> --wave 2 \
  --resume-from <current-route-path>@<current-full-route-commit> \
  --output logs/fast-resume-startup-benchmark.json
```

Expected: valid JSON. Record the observed classification, elapsed seconds, and process count truthfully. A result above two seconds is an optimization finding to investigate before acceptance, not a falsified or manually edited report and not a CI failure.

- [ ] **Step 6: Run the complete focused verification profile**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_kernel_properties.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_startup_snapshot.py \
  tests/unit/test_seat_status_all.py \
  tests/unit/test_status.py \
  tests/unit/test_ledger_fast_resume.py \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all pytest selectors pass, placeholder check passes, `ci_smoke.py` prints `OK`, and the diff check is silent.

- [ ] **Step 7: Inspect the actual implementation diff for scope and abuse cases**

```bash
env -u GIT_INDEX_FILE git diff --name-status <task-1-parent>..HEAD
env -u GIT_INDEX_FILE git diff --stat <task-1-parent>..HEAD
env -u GIT_INDEX_FILE git diff --check <task-1-parent>..HEAD
```

Confirm directly that the range adds no cache/receipt/event/approval entity, caller-supplied scope, cursor write, effect authorization, concurrent authority definition, short immutable ref, `--follow` history, or timing gate. Confirm the ordinary command and non-Git fixture path still work.

- [ ] **Step 8: Commit Task 4 and record the exact review range**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/measure_ledger_start_guard.py scripts/codex_protocol_model.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md .agents/skills/four-seat-protocol/SKILL.md \
  docs/protocol/codex/continuation.md \
  docs/protocol/codex/ledger-cli-adoption.md \
  logs/fast-resume-startup-benchmark.json
env -u GIT_INDEX_FILE git add \
  scripts/measure_ledger_start_guard.py scripts/codex_protocol_model.py \
  tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md .agents/skills/four-seat-protocol/SKILL.md \
  docs/protocol/codex/continuation.md \
  docs/protocol/codex/ledger-cli-adoption.md \
  logs/fast-resume-startup-benchmark.json
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "docs(protocol): adopt measured fast resume"
env -u GIT_INDEX_FILE git rev-parse <task-1-parent>
env -u GIT_INDEX_FILE git rev-parse HEAD
```

- [ ] **Step 9: Request one actual-diff Operator review under the live route**

The implementation owner sends the exact base/head range, changed paths, focused commands, benchmark report, and these adversarial questions to a non-author Operator seat running a different model:

1. Can caller-controlled input invent route, ownership, path scope, unread state, or effect authority?
2. Can task filtering hide a same-task fork or malformed immutable reference?
3. Can batch failure, unavailable mailbox state, dirty state, or target mismatch silently become PASS?
4. Can any resume/status/benchmark path mutate a cursor, ref, index, lock, mailbox, or worktree?
5. Does the ordinary full-orientation path still behave compatibly?

Only the assigned non-author Operator issues GO/NITS/FAIL on the actual range. Seats may reroute or exchange review ownership through an accepted durable handoff without coordinator approval. A NITS/FAIL response returns directly to the implementation owner for a narrow correction and new exact-range review; it does not create another universal preflight cycle.

## Completion Gate

Implementation is accepted only when:

- the focused suite, placeholder check, smoke, and diff check are fresh and green on the exact head;
- batch/reference differential coverage and the bounded-process test pass;
- the benchmark report truthfully records the current checkout and the sub-two-second target is either met or preserved as a visible optimization finding;
- the actual-diff non-author, different-model Operator verdict is GO; and
- no push, merge, cursor consume, service start, provider action, booking, spend, deployment, or other external effect has been inferred from that GO.
