# Capability Phase 1 Surface Inventory Closure Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to execute this plan and
> `superpowers:test-driven-development` for Task 1. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Close the last Phase-1 gate by making omission of a known live v1
surface fail deterministically and by classifying every public helper on those
surfaces without changing runtime behavior.

**Architecture:** Keep the existing JSON inventory as the descriptive record,
but add one independent, finite owner map in its test as the completeness
oracle. Extend the fixture with the exact current route, cursor, lock,
verification, runtime-launch, hook, status, provider, and migration roots; do
not add a recursive executable scanner or a second runtime registry.

**Tech Stack:** JSON fixture, Python `ast`, pytest, Markdown.

## Global Constraints

- Current v1 route, verification, cursor, lock, hook, provider, and runtime
  behavior remains unchanged; this plan modifies only tests, fixtures, and
  documentation.
- `REQUIRED_SURFACE_OWNERS` is handwritten and independent. It must not be
  derived from inventory `components`, `source_paths`, `reader_paths`,
  `writer_paths`, or `module_rules`.
- Every required path has exactly one expected component owner. Every required
  Python path also has exactly one `module_rules` entry, so its top-level public
  functions are AST-classified.
- Read-only components are named in an explicit set. A component with no Python
  source may have an empty `module_rules`; every component with Python sources
  must have exactly the matching Python module rules. `status.py --write` and
  every hook, cursor, ref, index, and lock writer remain explicit boundaries;
  they are never mislabeled read-only.
- The finite scope is: all existing inventory modules; guide-named Phase-4
  readers; every current executable that directly reads or mutates durable
  protocol state, launches a model/provider, or crosses a user-gated effect
  boundary; and direct public-helper modules used by those roots.
- Do not recursively classify generic smoke, test, documentation, or build
  utilities. Do not create a general shell-command authority taxonomy.
- No activation, mailbox/cursor mutation, lock action, model launch, provider
  call, spend, push, or production write is authorized by this plan.
- All Git and pytest commands use `env -u GIT_INDEX_FILE`.

## Independent abuse-case acceptance

Two independent same-model audits found that the old test was self-scoped: it
iterated only fixture-declared `module_rules`, so deleting a whole component or
leaving a Python reader/writer out of `module_rules` stayed green. Task 1 must
enforce these cases:

1. Removing a required module or executable from the fixture fails with its
   expected owner.
2. Moving a required path to the wrong component or declaring it twice fails.
3. Listing a required Python path only as a reader/writer, without a module
   rule, fails.
4. Removing a public helper override or naming an unknown helper fails under
   the existing AST checks.
5. A genuinely read-only component needs no invented writer.
6. Dot-prefixed or non-importable repository paths, including the seat-status
   skill path, resolve through their original path rather than reconstructing a
   false filesystem path from a dotted key.

---

### Task 1: Independent ownership oracle and complete v1 classifications

**Files:**

- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`

**Interfaces:**

- Produce `REQUIRED_SURFACE_OWNERS: dict[str, str]` in the test.
- Preserve fixture schema `compact-kernel-surface-inventory/v1`.
- Add compact components `live_v1_status_and_runtime_readers`,
  `coordination_lock_effects`, `codex_runtime_and_hook_adapter`, and
  `signed_bus_event_and_cursor_runtime`; retain route lineage as a separate
  read-only but live-v1 authority reader.

The independent owner map must retain all currently inventoried Python modules
and add these paths with these owners:

| Owner | Required paths |
|---|---|
| `target_binding` | `governance.toml` |
| `markdown_routes_and_mailbox_writer` | `scripts/protocol_mailbox.py`, `coordination/bin/send-event`, `coordination/bin/consume-events` |
| `capacity_reducer_and_packet_state_telemetry` | `scripts/protocol_capacity_board.py` |
| `verification_authority_and_publication` | `scripts/consume_reviewer_result.py` |
| `live_v1_route_lineage_reader` | `scripts/route_lineage.py` |
| `signed_bus_event_and_cursor_runtime` | `threeway/refstore.py`, `threeway/gate.py`, `threeway/cutover.py`, `scripts/seat_emit.py`, `scripts/chief_emit.py`, `scripts/overseer_emit.py`, `scripts/sign_ci_result.py`, `scripts/consume_bus.py`, `scripts/run_merge_gate.py`, `scripts/overseer_plan.py`, `scripts/agy_observer.py`, `scripts/bus_unread.py`, `scripts/execute_threeway_cutover.sh` |
| `live_v1_status_and_runtime_readers` | `scripts/mailbox_monitor.py`, `scripts/ledger_start_guard.py`, `scripts/codex_protocol_model.py`, `scripts/protocol_doctor.py`, `scripts/continuation_readiness.py`, `.agents/skills/four-seat-protocol/scripts/seat_status.py`, `scripts/status.py`, `scripts/latest_handoff.py` |
| `coordination_lock_effects` | `coordination/bin/claim-lock`, `coordination/bin/release-lock` |
| `codex_runtime_and_hook_adapter` | `coordination/bin/codex-seat`, `scripts/codex_seat_launcher.py`, `.codex/hooks.json`, `.codex/hooks/session-smoke.sh`, `.codex/hooks/guard-git-index.sh`, `.codex/hooks/update-state.sh` |

Required helper defaults and overrides:

- `protocol_mailbox` is `runtime_core`.
- `protocol_capacity_board.main`, `consume_reviewer_result.main`,
  `codex_seat_launcher.main`, every signed-bus CLI `main`, and every new
  status/runtime-module `main` are `cli_entrypoint` with disposition
  `keep_documented_cli`.
- `ledger_start_guard` and `codex_protocol_model` default to `runtime_core`.
- `mailbox_monitor`, `protocol_doctor`, `continuation_readiness`, `seat_status`,
  `status`, and `latest_handoff` default to `telemetry`; the status component
  records the explicit optional `STATUS.md` writer in its boundary.
- `consume_reviewer_result` defaults to `runtime_core` because it validates and
  may execute bounded verifier commands; only its CLI entrypoint is overridden.
- `codex_seat_launcher` defaults to `runtime_core`; its executor boundary names
  the per-seat index and selected model process without granting seat authority.
- `threeway/refstore.py`, `threeway/gate.py`, the three emitters,
  `sign_ci_result.py`, `consume_bus.py`, `run_merge_gate.py`,
  `overseer_plan.py`, and `threeway/cutover.py` default to `runtime_core`.
  `agy_observer.py` and `bus_unread.py` default to `telemetry`. Their component
  is live for the separate three-way toolchain but grants no compact-kernel
  route authority; the authority contract must say this explicitly.
- `route_lineage.py` is a read-only `live_v1_route_lineage_reader`, not a
  dormant adapter: ledger startup and capability currency use its resolution.
  Its public helpers remain `runtime_core`, except `check_cas` remains an
  explicit orphan and `main` remains a documented CLI.
- Shell/config/hook paths have no Python helper classification, but remain
  exact source/executor boundaries in their owning components.

- [x] **Step 1: Add the independent RED ownership test**

  Add `REQUIRED_SURFACE_OWNERS`, replace the singular read-only component ID
  with an explicit set, allow empty module rules only when no Python source is
  present, and parameterize this assertion without reading expected owners from
  the fixture. Replace dotted-key path reconstruction with a
  `module_key -> original repository path` map so the dot-prefixed seat-status
  path remains valid:

  ```python
  @pytest.mark.parametrize(
      ("path", "expected_owner"),
      sorted(REQUIRED_SURFACE_OWNERS.items()),
  )
  def test_required_surfaces_have_explicit_owner(path, expected_owner):
      components = _load_inventory()["components"]
      owners = [
          component["id"]
          for component in components
          if path in (
              {rule["path"] for rule in component["module_rules"]}
              if path.endswith(".py")
              else set(component["source_paths"])
          )
      ]
      assert owners == [expected_owner]
  ```

- [x] **Step 2: Run the focused test and verify RED**

  Run:

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest tests/unit/test_compact_kernel_surface_inventory.py -q
  ```

  Expected: failure naming the currently missing required owners; no syntax or
  fixture-parse error.

- [x] **Step 3: Extend the fixture minimally**

  Add the exact source/reader/writer roots and helper rules above. Record
  `coordination/mailbox/seen`, `coordination/locks`, `coordination/presence`,
  the optional local `STATUS.md` and `STATE.md` outputs, the per-seat
  index/runtime binding, and signed-bus event/cursor refs in the relevant
  component paths or executor-boundary text. Do not claim the live three-way
  tools are compact route authority, and do not claim the status component is
  read-only.

- [x] **Step 4: Run the focused test and verify GREEN**

  Run the Step-2 command. Expected: all inventory tests pass.

- [x] **Step 5: Run changed-surface regressions**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest -q \
    tests/unit/test_compact_kernel_surface_inventory.py \
    tests/unit/test_protocol_mailbox.py \
    tests/unit/test_governance_hardening.py \
    tests/unit/test_codex_ledger_bridge.py \
    tests/unit/test_protocol_prompt_sync.py \
    tests/unit/test_protocol_capacity.py \
    tests/unit/test_route_lineage.py \
    tests/unit/test_seat_status_all.py \
    tests/unit/test_status.py \
    tests/unit/test_compact_state_mapping.py \
    tests/unit/test_codex_seat_launcher.py \
    tests/unit/test_threeway_activation_scripts.py \
    tests/unit/test_threeway_constants.py
  ```

  Expected: PASS with no xpass or warning-dependent success.

- [x] **Step 6: Commit Task 1**

  ```sh
  env -u GIT_INDEX_FILE git add \
    tests/unit/test_compact_kernel_surface_inventory.py \
    tests/fixtures/compact_kernel/v1_surface_inventory.json
  env -u GIT_INDEX_FILE git commit -m "test: close compact kernel surface inventory"
  ```

### Task 2: Reconcile Phase-1 completion records

**Files:**

- Modify: `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
- Modify: `docs/superpowers/plans/2026-07-15-capability-baseline-runtime-collector.md`
- Modify: `.superpowers/sdd/phase1-task-5-report.md`
- Modify: this plan

- [x] **Step 1: Mark Phase-1 truth, not aspiration**

  Mark all five Phase-1 guide items complete only after Task 1 is green. Add a
  compact closure note naming the independent owner oracle, total mappings,
  committed cohort, reporter contract, epoch-0/v1 mirror, and the exact Task-1
  test command/result.

- [x] **Step 2: Correct stale publication wording**

  Replace statements that the cohort/report are uncommitted with their actual
  commit `8149df28b45bd2b0b159b243923d0ab439c3d815` and integration merge
  `d07fc4d`. Keep the explicit statement that no activation occurred.

- [x] **Step 3: Mark this plan complete and verify documentation**

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
  env -u GIT_INDEX_FILE git diff --check
  env -u GIT_INDEX_FILE git status --short
  ```

- [x] **Step 4: Commit Task 2**

  ```sh
  env -u GIT_INDEX_FILE git add \
    docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md \
    docs/superpowers/plans/2026-07-15-capability-baseline-runtime-collector.md \
    docs/superpowers/plans/2026-07-15-capability-phase1-surface-inventory-closure.md
  env -u GIT_INDEX_FILE git add -f .superpowers/sdd/phase1-task-5-report.md
  env -u GIT_INDEX_FILE git commit -m "docs: close capability phase 1 gate"
  ```

## Phase-1 gate

The gate is met only when the independent owner oracle and AST classification
suite pass, all Section-4 mappings and trusted baseline evidence remain valid,
the kernel mirror remains epoch `0`/writer `v1`, and no compact path is
authoritative.

## Integration-review correction and reclosure

The independent review of `d07fc4d..fa3df0e` found two reproducible gaps, so
Task 2 did not close the gate at that time:

1. The finite root list omitted `scripts/run_merge_gate.sh`, and the classified
   roots directly import unowned local authority helpers. A bounded AST import
   trace from the current `module_rules` reaches 15 unowned `threeway` modules.
   The explicit cutover and CI launch surfaces also require
   `threeway/keys_bootstrap.py` and `.github/workflows/ci.yml`.
2. Removing a non-orphan override such as `scripts.mailbox_monitor.main` leaves
   the suite green because the function silently inherits its module default.

These were test-contract defects, not runtime defects. Task-3 commit
`09d2e7f768a0324ace1a6de61afc483ce222dd52` corrected them within the inventory
test and fixture: focused RED was `34 failed, 59 passed`; the override mutation
was `1 failed, 92 deselected`; focused GREEN was `93 passed`; the exact 13-file
changed-surface regression suite was `303 passed`; and project smoke was `OK`.
A fresh read-only Codex subagent independently reviewed
`1c3e5fdae3f072743155e2345e40cfe7b8b7df9d..09d2e7f768a0324ace1a6de61afc483ce222dd52`
and returned `RESOLVED`, with no Critical or Important issue and
`Ready to reclose: Yes`. Current v1 behavior, epoch `0`/writer `v1`, and the
no-activation boundary did not change.

### Task 3: Close root, import, and override omissions

**Files:**

- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`

**Finite root additions:**

- `scripts/run_merge_gate.sh`
- `threeway/keys_bootstrap.py`
- `.github/workflows/ci.yml`

**Finite local-module closure:**

- `threeway/__init__.py`
- `threeway/approval_authority.py`
- `threeway/canon.py`
- `threeway/cursor_backfill.py`
- `threeway/envelope.py`
- `threeway/gitcas.py`
- `threeway/keys.py`
- `threeway/legacy_projector.py`
- `threeway/loop.py`
- `threeway/policy.py`
- `threeway/predicate.py`
- `threeway/reducer.py`
- `threeway/rework.py`
- `threeway/store.py`
- `threeway/tier.py`

Assign these paths to `signed_bus_event_and_cursor_runtime`. Classify
`cursor_backfill`, `legacy_projector`, and the dormant slice-1 `store` as
`historical_adapter`; classify the remaining helpers as `runtime_core`. Pin
`threeway.keys_bootstrap.main` as `cli_entrypoint/keep_documented_cli`. Record
the merge-gate wrapper, cutover key bootstrap, and manual CI signer in the
component boundary without granting compact authority.

- [x] **Step 1: Add RED owner/import-closure assertions**

  Extend the handwritten `REQUIRED_SURFACE_OWNERS` with the 18 paths above.
  Add a bounded assertion that parses only fixture-classified Python modules,
  resolves their direct repository-local `scripts`/`threeway` imports, and
  requires every resolved module to have exactly one fixture owner. It must not
  walk arbitrary executables or create a runtime registry. Add a finite
  `REQUIRED_WRITER_SURFACES` assertion for the signed-bus effect paths:
  `refstore`, `gate`, `cutover`, `gitcas`, `cursor_backfill`, `keys_bootstrap`,
  all five signing/consuming emitters, `run_merge_gate.py`,
  `run_merge_gate.sh`, `overseer_plan.py`, `execute_threeway_cutover.sh`, and
  the manual signer job in `.github/workflows/ci.yml`. Each must appear exactly
  once in the signed-bus component's `writer_paths`.

  Run:

  ```sh
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
    -m pytest tests/unit/test_compact_kernel_surface_inventory.py -q
  ```

  Expected: RED naming the missing root/helper owners; no syntax or fixture
  parse error.

- [x] **Step 2: Pin every required symbol override**

  Add an independent `REQUIRED_SYMBOL_OVERRIDES` map containing every required
  symbol, owner, helper class, and disposition, including all current orphan and
  CLI overrides plus `threeway.keys_bootstrap.main`. Assert the fixture has
  exactly the expected entry. Prove the pin is non-vacuous by temporarily
  deleting `scripts.mailbox_monitor.main`, observing the focused assertion fail,
  and restoring the fixture before continuing.

- [x] **Step 3: Extend the fixture minimally and verify GREEN**

  Add the named roots/modules and exact helper classifications. Keep all new
  paths in the signed-bus component, add `threeway/canon.py` as a reader of the
  route-manifest and capability-receipt components, record the finite effect
  roots in `writer_paths`, and preserve the authority contract
  `live_threeway_toolchain_not_compact_route_authority`.

  Re-run the Step-1 command. Expected: PASS.

- [x] **Step 4: Run changed-surface regressions and commit**

  Run the Task-1 changed-surface command, `scripts/ci_smoke.py`, and
  `git diff --check`. Commit only the two test/fixture paths with subject:

  ```text
  test: complete compact kernel surface closure
  ```

### Task 4: Reclose truthful Phase-1 records

**Files:**

- Modify: `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
- Modify: this plan
- Add: `.superpowers/sdd/phase1-inventory-reclosure-report.md`

- [x] Record the Task-3 RED/mutation/GREEN evidence and exact commit SHA.
- [x] Mark the first guide item and Tasks 3-4 complete only after an independent
  review finds no Critical or Important issue.
- [x] Re-run `scripts/ci_smoke.py` and `git diff --check`; commit only these
  completion records with subject `docs: reclose capability phase 1 gate`.

**Reclosure gate:** met. Every finite root has one owner; every
fixture-classified Python module's direct local imports have one owner; every
required override is pinned independently; the 49 Section-4 mappings and
trusted 25-run baseline remain valid; and the reporter contract remains bound
to its committed cohort evidence. Current v1 remains authoritative, while the
epoch `0`/writer `v1` kernel mirror remains declarative only. No compact path is
authoritative or activated.
