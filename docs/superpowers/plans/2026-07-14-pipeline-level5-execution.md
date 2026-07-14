# Pipeline Level-5 Harness Execution Plan

> Execution requirement: use the four-seat protocol. Each implementation task
> runs in an isolated worktree, follows RED-GREEN-review, and receives an
> independent Operator GO/NITS/FAIL before integration. The coordinator routes
> and reconciles but does not author production behavior.

Design authority:
`docs/superpowers/specs/2026-07-14-pipeline-level5-execution-design.md`

## 1. Program Controls

- Preserve existing blocked Wave-2 FAIL, CONTRADICTION, and HOLD evidence.
- Run this program's conceptual Wave-0 cycle inside protocol Wave 2. The
  capacity loader is wave-scoped; keeping the protocol wave unchanged makes
  the parked Task2U/Task3I/PPL packets visible to the same validator and route.
- Never run parallel implementers on a shared path or in the same worktree.
- Use `env -u GIT_INDEX_FILE` for every ordinary Git and pytest command.
- Use a scoped temporary index for coordinator-only commits when the shared
  index contains unrelated state.
- Do not merge, push, claim/release locks, consume cursors, refresh targets,
  invoke paid providers, or perform other shared side effects without the
  exact routed single-executor token.
- Keep raw provider prompts/responses out of Git, mailbox bodies, command
  arguments, normal logs, screenshots, and transcript artifacts.
- A green capacity board or wave gate is process evidence only. Correctness
  requires the routed Operator report and executed evidence.

## 2. Preserved State And Ownership Transfer

The first coordinator route must keep these joins `blocked` and unchanged:

- `coord-control-plane-authority-foundation-join`
- `coord-ledger-ppl-recommendation-evaluation-join`

It parks their live triggers while Wave 0 has scheduling priority. It does not
convert prior evidence to GO or claim either campaign complete.

The route marks these four current Wave-2 seat packets `excepted` for scheduling
under direct user supersession, while preserving and appending to their
evidence:

- `director-control-plane-authority-foundation-task2u-fail-closed-closure`
- `operator-control-plane-authority-foundation-task2u-cumulative-lanev`
- `director2-control-plane-authority-foundation-task3i-execution-contract-closure-preflight`
- `operator2-control-plane-authority-foundation-activation-repreflight`

This is not a correctness exception, closeout, GO, or deletion. Their
coordinator join remains blocked, all findings and CLEAR limitations remain
binding, and any future continuation requires a fresh packet/reroute.

The dirty worktree at
`.worktrees/control-plane-authority-foundation-2026-07-10` remains untouched.
The Wave-0 route transfers only the current-main path
`scripts/consume_bus.py` away from the parked Task2U packet for the narrow
coordinator rejection. It transfers no dirty bytes, commits, review claims, or
other Task2U path.

The clean worktree at `.worktrees/opus-lanev-receipt-hardening` transfers to
Director2 for read-only finalization at exact head
`97c270f8f0e630fdaaded672e0da37ed32335de5`. Its existing commits are reused;
no second implementation is created.

## 3. First Dual-Pair Cycle

### Task A1 - Make coordinators non-consumable at executable boundaries

Owner: Director
Verifier: Operator
Execution: new isolated worktree based on the committed Wave-0 route

Allowed production paths:

- `coordination/bin/consume-events`
- `scripts/consume_bus.py`
- `scripts/status.py`
- `scripts/mailbox_monitor.py`
- `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- `.claude/skills/four-seat-protocol/scripts/seat_status.py`

Allowed test paths:

- new `tests/unit/test_coordinator_unpinned_mailbox.py`
- existing status/monitor/seat-status tests only when a new test cannot reach
  the public behavior without changing their fixture setup

Forbidden paths:

- every other dirty authority-foundation path;
- both coordinator cursor files and every pair-seat cursor;
- `threeway/refstore.py`, cutover/backfill, signed refs, packets, locks, route
  files except the final verify-request;
- every Opus hardening path.

Steps:

1. Grep every write to human and ref-bus cursor state, every consumable-seat
   roster, and every status recommendation. Record a sibling disposition for
   each: fix in scope, already rejects, read-only compatibility, or route
   contradiction.
2. Add failing public-entrypoint tests for both coordinator aliases against
   `consume-events` and `consume_bus.py`. Prove rejection happens before store
   construction, cursor read, file write, Git staging, or `--to` handling.
3. Add failing status tests proving coordinator output is `unpinned` and
   `all-scope`, does not read `seen/coordinator*.txt`, and never recommends a
   consume command. Pair-seat status behavior remains unchanged.
4. Implement the minimum rejection and read-only status behavior.
5. Mutation-check one shell guard and one Python guard by temporarily restoring
   a coordinator alias and proving the focused tests turn RED.
6. Run focused tests, the relevant existing status/coordination suites,
   `scripts/ci_smoke.py`, shell syntax, and `git diff --check`.
7. Obtain fresh specification review, then code-quality review. Commit the
   exact Task A1 paths only.

Stop condition: if another executable coordinator cursor writer is outside
this authorized slice, send one bounded contradiction to the coordinator. Do
not widen locally.

### Task A2 - Make the mechanism ledger evidence-aware

Owner: Director, after Task A1
Verifier: Operator, cumulative A1..A2 range

Allowed paths:

- `scripts/threeway_mechanism_ledger.py`
- new `tests/unit/test_threeway_mechanism_ledger.py`
- `docs/protocol/threeway/MECHANISM-LEDGER.md`
- `docs/protocol/threeway/README.md`
- `docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`

Steps:

1. Add RED tests showing `--check` rejects a missing cited test, an
   uncollectable selector, a deleted/renamed evidence target, and a claim whose
   status says verified without executed evidence.
2. Separate implementation presence, test collection, executed behavior
   evidence, parser/golden synchronization, and historical evidence in the
   ledger model.
3. Require every verified/live behavior claim to resolve to existing exact
   selectors and a committed HEAD-bound Operator execution artifact that names
   the command and successful result. Collection alone is not execution. Until
   Wave 2 defines the independent result schema, a claim without such an
   existing Operator artifact must be `implemented-unverified` or `planned`;
   do not invent tests, labels, or future evidence.
4. Regenerate the ledger and correct the two three-way overview documents so
   no prose overclaims missing evidence.
5. Prove the new oracle is independent: bypass the evidence-existence or
   collection predicate and show the focused test turns RED.
6. Run the complete new test file, relevant three-way doc/prompt checks,
   `scripts/ci_smoke.py`, and `git diff --check`.
7. Obtain fresh specification review, then code-quality review. Commit A2 as a
   distinct child of A1.

Operator verifies the exact two-commit range, repeats both mutations, audits
the complete changed path set, and returns one GO/NITS/FAIL. A1 and A2 are not
complete merely because generated Markdown matches itself.

### Task B1 - Finalize the existing Opus hardening branch

Owner: Director2
Verifier: Operator2
Execution: existing clean Opus worktree at exact head `97c270f`

Allowed durable writes:

- one SHA-bound Director2-to-Operator2 verify-request after local PASS;
- one content-free command-results artifact only if the route names it.

No code, plan, spec, descriptor, prompt, receipt schema, branch, or worktree
file may change in the first pass.

Steps:

1. Recheck worktree cleanliness, exact HEAD, branch divergence, descriptor
   digest, advisory prompt blobs, and plan final-integration requirements.
2. Run the plan's complete focused acceptance bundle and full unit suite.
3. Run GO schema, doc claims, changed-authority SHA checks, smoke, descriptor
   and prompt hashes, exact-range `git diff --check`, and final branch-state
   checks.
4. Perform the pre-stated Codex actual-diff question: does the complete
   `5550414..97c270f` range mechanically enforce every Section-9 case in
   `docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md`,
   with non-vacuous tests and no bypass around attempt uniqueness, scope
   authority, advisory prompt, exact report verdict, or no-replace publication?
5. If any local check fails, stop before provider launch and send a bounded
   FAIL/blocker to the coordinator. Do not fix code under this packet.
6. If all local checks pass on unchanged `97c270f`, use both the explicit user
   consent recorded in the coordinator route and its one-shot executor token to
   invoke the receipt-backed Opus review exactly once. The consent authorizes
   spend; the token elects Director2 as the sole executor. No retry, substitute
   reviewer, or fabricated receipt is permitted.
7. Reconcile the stored receipt with the provisional Codex findings. A receipt
   proves an attempt, never correctness. A degraded/unavailable receipt is
   preserved once but does not meet this program's Opus-complete exit.
8. Recheck exact HEAD and cleanliness, then send one verify-request to
   Operator2 naming the full range, commands, descriptor, receipt ID/status,
   findings/dispositions, exclusions, and known main divergence.

The provider-facing rendered prompt must contain no seat, controller, verdict,
lock, route, merge, shipping, push, or side-effect authority. Raw prompt and
response bytes must remain outside tracked or ordinary transcript surfaces.

### Task B2 - Independent Opus branch Lane V

Owner: Operator2, after the Task B1 verify-request

Operator2 independently:

1. proves the reviewed worktree is still clean at exact `97c270f`;
2. derives the actual merge base and reviews every changed file and commit;
3. reruns the complete focused/full/repository gate set;
4. tests prompt authority neutrality, scope/blob binding, replay,
   malformed/duplicate receipts, severity floors, publication recovery, and
   critical negative controls;
5. verifies the one receipt came from the routed attempt and was not manually
   synthesized or retried;
6. distinguishes provider availability from correctness;
7. returns one GO/NITS/FAIL bound to the immutable range.

Operator2 does not edit the branch, rerun the provider, merge, push, or publish.

## 4. First-Cycle Join

The coordinator joins only when:

- Operator returns GO for the exact Pair-A two-commit range and write set;
- Operator2 returns GO for immutable Opus head `97c270f`;
- the bridge records one real routed attempt and its status; a provider `pass`
  is a transport-completion criterion only, while Operator2 GO is the binding
  correctness verdict. A present or degraded receipt cannot close Opus
  transport completion;
- both prior Wave-2 joins remain visibly blocked/parked with their evidence
  unchanged;
- the dirty authority worktree remains untouched;
- fresh HEAD, mailbox, capacity, route, lock, and worktree checks show no drift;
- no unapproved side effect occurred.

The join authorizes a later integration decision. It does not merge either
branch, close PPL, claim Wave 0 complete, or prove current-main correctness.

## 5. Remaining Wave-0 Tasks

After the first join:

1. Build a machine-readable executable-surface manifest covering every Python,
   shell, hook, CI, schema, state mutator, provider adapter, and external
   side-effect entry point. Add a completeness gate based on tracked files and
   declared exclusions.
2. Reconcile the six authority-foundation commits and nine-file WIP against
   current main. Classify each hunk as reuse, reimplement, supersede, or reject;
   never transplant the dirty tree wholesale.
3. Make architecture freshness depend on relevant subsystem changes rather
   than only edits to `ARCHITECTURE.md`.
4. Make coordination fatal findings fail CI in the declared release profile.
5. Replace broad untracked-byte session-hook hashing with an explicit dependency
   manifest and content-minimized cache key.

Wave-0 exit requires Operator-verified evidence for each task and a generated
surface inventory with zero unexplained executable entries.

## 6. Wave-1 ChatGPT Hardening

Execute sequentially after the first cycle so its shared docs/tests do not
collide with Opus integration:

1. Canonical repository-wide idempotency registry across state filenames,
   worktrees, and processes.
2. Append-only lifecycle history; ambiguous/already-sent failures are not
   resumable without a distinct explicit duplicate-send capability.
3. One-shot transport token and content-free receipt; environment configuration
   alone cannot activate auto send.
4. Coordinator binding covers non-null HEAD, route, mailbox/cursors, relevant
   paths, capacity, and locks; each independent drift invalidates the packet.
5. Reject hard-linked state/lock files, verify ownership/mode/type, fsync the
   runtime directory, cap input/state size and records, and preserve sentinels.
6. Move raw prompt/response transfer off stdout and ordinary tool traces;
   define manual export as an explicit retention exception.
7. Field-complete provenance/sanitizer matrices for every input, output, and
   persistence channel.
8. Crash injection at reservation, output, send, receipt, replace, and import
   boundaries with deterministic recovery.
9. Replace self-attested acceptance Markdown with machine-generated,
   independently verified content-free artifacts.

Every task begins with RED, receives fresh spec/quality reviews, and gets a
separate Operator verdict. No browser send is required to prove pure state,
filesystem, schema, or recovery behavior.

## 7. Waves 2-7 Execution Order

### Wave 2 - Evidence verifier

1. Define claim-manifest and result schemas.
2. Implement source/selector resolution in a clean environment.
3. Bind execution results to HEAD, environment, dependencies, and verifier.
4. Add deletion, corruption, injected failure, and mutant negative controls.
5. Migrate the mechanism ledger and consultation acceptance artifacts.

### Wave 3 - Kernel extraction

1. Freeze provider-neutral state/authority interfaces.
2. Extract schemas, canonical events, roles, cursor policy, CAS, idempotency,
   reducers, and capability checks behind a compatibility facade.
3. Add static import/dependency rules and runtime bypass assertions.
4. Migrate one low-risk bridge and one representative provider slice.
5. Differentially compare normalized legacy/kernel state transitions.

### Wave 4 - Authority cutover

1. Implement durable inbox/outbox, deduplication, quarantine, and replay.
2. Define key lifecycle and emergency revocation.
3. Migrate consumer cursors one writer at a time with reconciliation proof.
4. Run crash, lost-ack, duplicate, concurrent-cursor, and rollback campaigns.
5. Enter bounded read-only compatibility only after exact reconciliation.

### Wave 5 - Provider convergence

1. Generate a common conformance suite.
2. Migrate each provider/bridge sequentially.
3. Render or mechanically verify provider prompts from canonical policy.
4. Record intentional extensions as expiring waivers.
5. Remove policy from adapters after conformance GO.

### Wave 6 - CI and supply chain

1. Resolve the supported platform/Python/sandbox matrix.
2. Hash-lock dependencies and pin CI actions by commit SHA.
3. Add lint/type, critical-branch coverage, mutation, fuzz, security, secret,
   license, SBOM, provenance, and reproducibility gates.
4. Make release-profile authority/coordination failures hard errors.
5. Capture a replay manifest for each certification run.

### Wave 7 - Shadow, cutover, deletion

1. Run isolated shadow/replay with canonical nondeterminism normalization.
2. Complete a predeclared soak window with zero unexplained divergence.
3. Exercise rollback from every stage.
4. Cut over the remaining single writers.
5. Delete legacy writable authority, duplicated hooks/policy, circular evidence
   checks, and bypass routes.

## 8. Integration Discipline

- A branch is not merge-ready merely because its own tests pass. Rebase or
  transplant onto the current verified integration head, then rerun its exact
  Operator gate.
- The Opus branch and authority branch overlap shared architecture, protocol,
  capacity, and verification files. Integrate them sequentially after explicit
  reconciliation; never merge both blindly.
- Local merge, push, publication, and cleanup are distinct user permissions.
- After every merge, verify the merged head before removing an owned worktree
  or branch.

## 9. Program Completion Gate

The coordinator may declare the Level-5 program complete only when the Wave-0
pre-wave gate and all seven migration-wave exits are Operator-verified, every
owner decision is closed,
the supported matrix passes, rollback has been exercised, the evidence verifier
reproduces the release from clean inputs, no unwaived critical/high finding or
critical mutant remains, and legacy writable paths are deleted.

Estimated elapsed time with consistently available four-seat execution is
6-9 weeks; normal partial utilization is 8-12 weeks. These are planning
estimates, not measured completion evidence.
