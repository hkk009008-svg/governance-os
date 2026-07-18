# Pipeline Maintenance Priority Pause Design

**Status:** user-approved design, pending user review of this committed specification  
**Date:** 2026-07-18  
**Coordinator base:** `f38da0dcac562f8eb39333f532d3b0f9aac825b0`  
**Active ledger route:** `coordination/mailbox/sent/2026-07-18T02-40-57Z-coordinator-to-all-coordination.md`

## 1. Decision

Temporarily park the active evidence-ledger backend-checkpoint route and run a
Pipeline-only maintenance campaign first. The ledger cycle is paused by user
priority, not completed, excepted, failed, merged, or published. Its exact
target evidence, worktree state, unfinished `web/` setup, ownership, and
resume conditions remain durable.

The maintenance campaign uses a sequential implementation spine with two
independent read-only preflights:

1. Director2 establishes the design-time safety contract for deterministic
   handoff selection.
2. Operator2 reproduces and classifies the reported sandbox failure.
3. Director implements the approved handoff correction and two small cleanups
   only after the Director2 preflight is committed.
4. Operator independently verifies the exact committed maintenance range and
   alone issues GO, NITS, or FAIL.
5. Coordinator converges the maintenance results and resumes the ledger route
   only when every required maintenance branch is terminal.

A confirmed `send-event` repository defect does not enter the first
implementation range. It triggers a separate security-sensitive corrective
route before ledger resumption. An environment-only sandbox restriction closes
with evidence and no writer change.

## 2. Current State To Preserve

At the design base:

- Pipeline `main` is clean at `f38da0d`, one commit ahead of `origin/main`.
- Wave 2 is MET, coordinator unread is `0 / ref-bus`, and no coordination lock
  exists.
- The ledger route is active but no assigned seat has started it: Director,
  Director2, and Operator2 packets are `ready`; Operator and coordinator
  packets are `blocked` on their declared dependencies.
- The evidence-ledger target remains
  `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`
  at `a93d07196dd8622d753cdd5f8617af7df29eb1cf`, with only the pre-existing
  untracked `web/` setup visible.
- The normal evidence-ledger checkout contains unrelated user work and remains
  excluded.

The pause transition updates the five current ledger packet records to a
user-priority blocked state and records their original states. It must not add
completion evidence, a verification verdict, activation authority, or a
publication claim. Resume restores the original readiness only after fresh
Pipeline and target checks prove that the preserved boundaries still hold; a
changed boundary returns to coordinator reconciliation instead.

## 3. Scope

### Required implementation

- `scripts/latest_handoff.py`
- `tests/unit/test_latest_handoff.py`
- `scripts/bus_unread.py`, limited to correcting the stale test citation
- `tests/unit/test_keys.py`, limited to replacing direct `.__len__()` use with
  `len()`

### Required read-only investigation

- `coordination/bin/send-event`
- `tests/unit/test_coordination_tooling.py`
- the current managed sandbox permission profile and exact failing command

### Conditional follow-on scope

`coordination/bin/send-event` may be modified only in a separately committed
and validated route after Operator2 proves all of the following:

- the failure is reproducible from an exact committed Pipeline SHA;
- it occurs in a supported execution environment rather than only an external
  sandbox policy;
- the failing path and syscall are identified precisely;
- a repository change is necessary and cannot be replaced by the supported
  runner permission profile; and
- the proposed change preserves the writer's clean Git environment, mode-0700
  isolation, fixed finalizer, atomic publication, and no-inherited-config
  security boundaries.

### Non-goals

No evidence-ledger edit, target worktree refresh, dependency installation,
business-data access, owner ruling, policy activation, database operation,
mail cursor consume, lock action, remote-ref update, push, merge, deployment,
provider action, paid spend, pod action, cleanup, or ambient-WIP mutation is
part of this campaign.

## 4. Adversarial-Surface Classification

The handoff selector is an authority-orientation surface. A stale selection can
misdirect a live seat even though the helper itself is read-only. Therefore
R-INDEPENDENCE applies before implementation and at final review.

Director2 must enumerate and bind at least these abuse and drift cases as
acceptance tests:

- multiple same-seat handoffs on one calendar day;
- an older handoff touched after a newer handoff;
- equal or clone-like filesystem mtimes;
- missing, duplicated, malformed, non-UTC, or out-of-range `When:` values;
- filename date and metadata timestamp disagreement;
- canonical same-seat versus noncanonical near-match names;
- coordinator/coordinator2 canonical aliasing without cross-seat leakage;
- exact timestamp ties;
- an invalid newest-looking candidate attempting to suppress the newest valid
  candidate; and
- warning behavior that must remain visible without crashing `seat_status`.

The fixed mailbox writer is a security and shared-side-effect surface. A
confirmed writer correction requires its own design-time enumeration and a
fresh non-author review; the handoff preflight cannot authorize it.

## 5. Deterministic Handoff Selection Contract

The corrected selector must not use filesystem `mtime` for ordering and must
not implement the scan report's date-only filename sort.

For every canonical same-seat candidate:

1. Inspect only the bounded leading metadata block established by the
   Director2 corpus inventory.
2. Require exactly one canonical UTC `When:` value in strict
   `YYYY-MM-DDTHH:MM:SSZ` form.
3. Require the UTC calendar date to equal the date encoded in the canonical
   filename.
4. Exclude a missing, duplicated, malformed, non-UTC, or mismatched candidate
   from selection and emit a deterministic warning naming that file and
   reason.
5. Select the valid candidate with the greatest full UTC timestamp.
6. Use basename only as the deterministic tiebreaker for two valid candidates
   with exactly equal timestamps.
7. If no valid candidate remains, return no selection and visible warnings;
   never silently fall back to `mtime`, filename-day ordering, or an invalid
   candidate.

The existing canonical seat pattern and near-match warning contract remain in
force. Director2 must inventory the complete current canonical handoff corpus
before implementation. If the corpus contains an additional legitimate
metadata grammar, the preflight must state and test that grammar rather than
letting implementation infer it.

## 6. Small Cleanup Contract

The `scripts/bus_unread.py` comment must cite the exact existing non-vacuous
test `tests/unit/test_threeway_activation_scripts.py::test_bus_unread_script`.
That test proves the cursor floor indirectly through the public unread helper:
one event is unread before cursor advance and zero afterward. The cleanup must
not claim that `test_chief_emit.py` directly pins `iter_events_since`.

`tests/unit/test_keys.py` replaces
`bytes.fromhex(pub_hex).__len__() == 32` with
`len(bytes.fromhex(pub_hex)) == 32`. This is style-only and changes no key
contract.

The already-corrected mailbox bullet receives no edit.

## 7. Sandbox Reproduction Contract

Operator2 runs the smallest exact `send-event`-exercising selector under the
current managed sandbox and records:

- Pipeline full SHA and clean-tree state;
- exact command and test node IDs;
- operating system, Python, shell, Git, and permission-profile identity;
- stdout, stderr, exit status, failing path, and failing syscall;
- whether `/tmp` creation itself fails, Git common-dir locking fails, or a
  different boundary fails;
- the same selector's result under the repository's supported execution
  profile when that comparison is lawfully available; and
- a disposition of `repository-defect`, `environment-policy`, or
  `unable-to-verify`, with uncertainty stated explicitly.

Changing `TMPDIR` in `conftest.py` is not an accepted remedy because
`send-event` currently passes an explicit `/tmp/send-event-git.XXXXXX` path to
`mktemp`. Blanket sandbox bypass instructions are not a code fix. No source
change follows an `environment-policy` or `unable-to-verify` result.

## 8. Routing And Dependencies

The maintenance task-board uses one implementation pair and Pair B preflight:

- `director2`: `director-preflight`, ready; owns the handoff corpus and
  adversarial design-time report.
- `operator2`: `operator-preflight`, ready; owns only sandbox reproduction and
  classification.
- `director`: `director-implementation`, blocked on Director2; owns the four
  required implementation/test paths and one canonical verify-request.
- `operator`: `operator-verification`, blocked on Director; owns independent
  verification and the only GO/NITS/FAIL report.
- `coordinator`: `coordinator-join`, blocked on all four seats; owns pause,
  convergence, conditional follow-on routing, and eventual ledger resume.
- `coordinator2`: observer only; no implementation, verdict, route, cursor, or
  side-effect authority.

Director2 and Operator2 may run concurrently because both are read-only and
their evidence surfaces are disjoint. Director starts only after Director2's
committed findings. Operator starts only after Director's committed canonical
verify-request. Coordinator closes only after all four routed outputs are
durable.

## 9. Implementation Commit Shape

Director produces two sequential commits:

1. A non-behavioral cleanup commit containing only `scripts/bus_unread.py` and
   `tests/unit/test_keys.py`.
2. A behavior-changing handoff commit containing only
   `scripts/latest_handoff.py` and `tests/unit/test_latest_handoff.py`.

The canonical verify-request covers the complete two-commit range, names the
Director2 preflight, exact author seat, assigned Operator, four-path manifest,
focused and protocol tests, adversarial question, and excluded effects.

## 10. Verification

Director runs focused RED/GREEN evidence for the handoff change and the
smallest relevant checks for both cleanups. Before the verify-request, run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_latest_handoff.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_activation_scripts.py -k test_bus_unread_script -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_seat_status_all.py tests/unit/test_latest_handoff.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Operator independently reruns the focused suites and actively attempts to make
the selector choose a stale, invalid, cross-seat, or mtime-manipulated
candidate. GO requires exact four-path scope, clean staged/worktree state, no
silent fallback, warning preservation, protocol doctor PASS, and smoke OK.

The sandbox report is evidence for a conditional route, not part of the
handoff correctness verdict. If it proves a repository defect, the coordinator
must finish the separate writer route before resuming ledger work.

## 11. Ordered Seat Startup

The coordinator's committed maintenance route must print its exact generated
mailbox path in every seat's command block. Until that event exists, no
placeholder route command is authoritative.

### 1. Coordinator

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

### 2. Coordinator2 observer

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator2 --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

### 3. Director2 preflight

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director2 --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

### 4. Operator2 preflight

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator2 --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

### 5. Director implementation

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

### 6. Operator verification

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

### 7. Coordinator convergence

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git status --short --branch
```

The route event adds one exact `sed` command for its own generated path to
each non-coordinator startup block and adds the exact route path to the final
`protocol_doctor.py --route` command.

## 12. Closeout And Resume

Maintenance closes only after:

- Director2's design-time report is committed and honored;
- Director's exact two-commit range is reviewed;
- Operator publishes GO for that range;
- Operator2 publishes a complete sandbox classification;
- any confirmed repository writer defect is fixed and independently verified
  through its separate route;
- capacity, route validation, coordination checks, protocol doctor, smoke, and
  exact-scope checks pass; and
- fresh ledger target checks still match the parked evidence.

If all conditions hold, coordinator may restore the original ledger packet
readiness and issue one resume event. Any changed Pipeline or target boundary,
sandbox uncertainty requiring scope expansion, NITS, or FAIL keeps ledger
parked and returns the smallest blocker or corrective route.
