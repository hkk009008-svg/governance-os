# Capability Baseline Runtime Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:test-driven-development` for every behavior change and obtain an
> independent task review before accepting the collector. The collector is
> sealed at `01d77653d5b7257bcef7c2517d958824eb8ff8a9`; generated cohort evidence
> and the closure report were committed at
> `8149df28b45bd2b0b159b243923d0ab439c3d815` and integrated by merge `d07fc4d`.
> That publication did not activate a compact path; v1 remains authoritative.

**Goal:** Collect one trusted, reproducible 25-run capability-first baseline
without constraining model tool choice or mutating live protocol authority.

**Architecture:** Add one parent-owned runtime collector around
`codex exec --json`. Minimal disposable benchmark repositories receive observer hooks that
timestamp `UserPromptSubmit` and wildcard `PreToolUse` with the host monotonic
clock; the parent cross-checks those records against the Codex JSONL lifecycle,
derives artifacts/reviews/effects itself, and passes an in-memory verified
provenance object to the existing effectiveness reporter. The existing
JSON-only reporter path remains structurally useful but can never claim
operational completion.

**Tech Stack:** Python 3 standard library, Codex CLI 0.144.4 structured JSONL,
fixture-scoped writable isolated workspaces, pytest, existing effectiveness
reporter and fixed five-profile contract.

## Global Constraints

- Exactly five profiles and ordinals 1 through 5, interleaved by ordinal.
- One runtime-derived host identity, pinned source HEAD, contract-approved Codex
  binary/version digest, model/config, contract,
  collector, reporter, prompt suffix, and instrumentation identity.
- The model never writes raw traces, observations, the final report, or trusted
  provenance; those remain outside the child sandbox.
- Use `UserPromptSubmit` for `accepted_input` and wildcard `PreToolUse` for
  `first_tool_callback`. Each disposable hook sends a minimal record to a
  random parent-owned AF_UNIX socket whose path exists only in that workspace's
  hook command; the parent timestamps receipt with `time.monotonic_ns()`.
- Cross-check root hook session identity and lifecycle against parent-captured
  `thread.started`, `turn.started`, and `turn.completed` JSONL events. The
  wildcard `PreToolUse` hook is the executable-boundary authority, so valid
  tool variants and subagent hook traffic do not reduce model capability.
  Missing, malformed, reordered, unknown, or contradictory evidence invalidates
  the run.
- Do not restrict eligible local model tools. The child workspace is read-only
  except for the exact fixture directory; network, browser, app, plugin,
  multi-agent, and other external-provider features are disabled. Hook payload
  prompt/tool input is hashed or discarded and never persisted raw. This uses
  `workspace-write` with the child CWD set to the fixture itself and both `/tmp`
  and `$TMPDIR` implicit write roots disabled; the parent `.git` and `.codex`
  directories therefore remain outside the writable root.
- Give each disposable workspace a fresh local `.git` directory solely to make
  Codex project-hook discovery deterministic. The child command supplies one
  session-only trust entry for that exact disposable path because ignored user
  config otherwise disables project-local hooks; hook trust is bypassed only
  for the parent-installed observer. The repository has no live remote, shared
  history, or authority; the child cannot write it, and fixture validation
  excludes only that parent-owned instrumentation metadata.
- The only external effect is one nonce-bound marker created inside the
  parent-owned cohort evidence root. Exactly five `effect_only` and five `combined`
  runs may execute it. No network, provider, browser, mailbox, lock, branch,
  push, paid API, or live protocol effect is permitted.
- Reserve each run and each effect before spawn/attempt. Fresh collection rejects
  existing state. A same-process single-run replay may diagnose immutable state,
  but resumed/self-authenticating records can never issue operational provenance;
  an interrupted cohort is terminal and a new cohort ID is required. Changed
  replay conflicts; uncertain effects reconcile from the marker and never retry.
- Collector, reporter, contract, benchmark instructions, and source snapshot
  must match committed blobs before a cohort may be called operational. Before
  the instrument commit and separate execution authorization existed, the real
  cohort stopped at this preflight; the completed cohort below passed the same
  committed-byte gate before and after collection.
- Existing direct `--baseline-observations` input remains unable to set
  `operational_complete=true`.
- All Git and pytest commands use `env -u GIT_INDEX_FILE`.

---

### Task 1: Trusted reporter boundary

**Files:**

- Modify: `scripts/protocol_effectiveness_report.py`
- Modify: `tests/unit/test_protocol_effectiveness_report.py`

**Interfaces:**

- Produce `VerifiedBaselineProvenance`, a frozen in-memory record binding the
  canonical contract/observation digests, cohort identity, collector identity,
  source HEAD, Codex identity, and exactly 25 run-record digests.
- Extend `_aggregate_baseline(..., verified_provenance=None)` without changing
  the existing CLI's JSON-only trust level.

- [x] Write failing tests proving a relabeled or structurally complete JSON
  cohort still exits incomplete, while a digest-matching in-memory verified
  provenance object may complete only an error-free exact 25-run cohort.
- [x] Write failing tests for mutated observations, contract mismatch, missing
  run digest, duplicate run identity, or changed cohort identity.
- [x] Run the focused tests and capture the expected failures.
- [x] Add the minimal frozen provenance type and exact digest comparisons.
- [x] Set `complete`, `operational_complete`, status, and operational provenance
  only after both structural completion and verified provenance pass.
- [x] Re-run focused reporter tests and the existing synthetic/relabel tests.

### Task 2: Parent-owned collector, observer, and profile enforcement

**Files:**

- Create: `scripts/capability_baseline_runtime.py`
- Create: `tests/unit/test_capability_baseline_runtime.py`
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`

**Interfaces:**

- `hook_main(event_kind, run_id, socket_path)` reads one hook JSON object from
  stdin, sends only identity/digest metadata to the parent socket, discards raw
  prompt/tool input, emits no output, and exits without affecting tool choice.
- `parse_runtime_trace(...)` returns one validated accepted-input/first-tool
  endpoint pair bound to one session/turn.
- `run_one(...)` reserves and executes one isolated profile/ordinal, returning
  an immutable run record or an explicit failed/uncertain record.
- `run_cohort(...)` uses order `(ordinal, profile)` and returns observations plus
  verified provenance only after all 25 exact runs pass.
- `main(...)` provides `--canary` and `--collect` modes with a fixed
  committed contract, byte-derived collector/Codex identities, a fixed output
  namespace, explicit model/source arguments, and explicit local-marker
  authorization for collection.

- [x] Write fake-Codex tests for the valid hook + JSONL sequence and verify RED
  because the collector is absent.
- [x] Add RED cases for missing/wrong session, duplicate prompt event,
  tool-before-input, absent tool, malformed JSONL, nested fake JSON in command
  output, unknown event, nonzero exit, timeout, and missing final result.
- [x] Add RED profile tests: required/forbidden coordination, review, and effect
  evidence; nonexistent/cross-run/symlink artifacts; mismatched review scope;
  and a nominal 25-run payload without profile evidence.
- [x] Add RED effect tests for the exact ten-run allowance, traversal/symlink
  refusal, reservation-before-attempt, completed replay, changed replay,
  crash-after-attempt reconciliation, and zero duplicate attempts.
- [x] Implement the stdin-only hook observer and parent JSONL capture using
  strict JSON, line limits, monotonic timestamps, a minimal scrubbed child
  environment, `--ignore-user-config`, `--ephemeral`, fixed model/config, and
  a minimal local repository whose nested fixture CWD is the only writable root.
- [x] Implement deterministic prompt construction from the fixed manifest plus
  a hashed benchmark suffix; scan child diffs and derive result/artifact/review
  identities rather than accepting model claims.
- [x] Implement one fixed O_EXCL marker executor in the parent-owned cohort root,
  effect reservation/reconciliation, atomic run records, and fresh-only
  operational provenance.
- [x] Add a dedicated non-authoritative benchmark-executor inventory component;
  classify collector `main` as CLI and all other public functions as telemetry.
- [x] Run collector, reporter, inventory, target-binding, and route/capability
  regression tests; run smoke, py_compile, and `git diff --check`.

### Task 3: Canary, committed-instrument gate, and operational cohort

**Files:**

- Create after authorized execution:
  `logs/capability-first/<cohort-id>/observations.json`
- Create after authorized execution:
  `logs/capability-first/<cohort-id>/baseline.json`
- Create after authorized execution:
  `logs/capability-first/<cohort-id>/records/<run-id>/{reservation,record}.json`
- Update after successful execution:
  `.superpowers/sdd/phase1-task-5-report.md`

**Interfaces:**

- Canary: one disposable run characterizes the installed Codex/hook event
  schema but cannot satisfy cohort completeness.
- Collection: exactly 25 non-retried runs, one per profile/ordinal pair.
- Final artifact: structural and operational completion, raw run hashes,
  per-profile medians, exact review identities, artifact class counts, and
  failure list.

- [x] Refuse collection until the collector, reporter, contract, benchmark
  instructions, and source snapshot resolve to committed bytes. This is a hard
  user-authorization gate, not a test bypass.
- Current execution status (2026-07-15): source HEAD
  `01d77653d5b7257bcef7c2517d958824eb8ff8a9`, cohort
  `phase1-01d7765-gpt56sol-max-20260715-v1`, model `gpt-5.6-sol`, reasoning
  effort `max`. The one canary completed with record digest
  `sha256:059d71368e30ffb7379394b2aaafa49c18103e13244464f69415764f056ffe82`
  and no effect. Collection exited `0` with
  `{"status":"complete","run_count":25}`. The exact evidence and verification
  record is `.superpowers/sdd/phase1-task-5-report.md`.
- [x] After the committed-instrument gate and separate execution authorization,
  run one guarded canary against the
  pinned Codex version/model and verify hook/JSONL agreement.
- [x] Execute the 25 runs sequentially in interleaved order. Persist failures;
  do not retry, replace, or select only successful attempts.
- [x] Verify 25 unique completed run IDs, 25 unique accepted-result digests,
  ten and only ten effect attempts, required profile artifacts/reviews, zero
  standby artifacts, zero duplicate effect/provider attempts, and complete
  endpoints.
- [x] Generate the final baseline through the committed reporter, run the full
  bounded verification suite, and record the exact result without activation.

## Stop conditions

- Stop before Task 3 if commit authorization is absent.
- Stop the cohort on source/config drift, malformed runtime evidence, effect
  uncertainty, any forbidden mutation/provider call, or the first invalid run.
- Never convert an incomplete/invalid cohort into a baseline by relabeling,
  hand-editing, retrying, or dropping failed runs.
