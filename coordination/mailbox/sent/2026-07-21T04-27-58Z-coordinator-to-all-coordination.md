# Coordinator → All: route Packet 4 CI and gate truthfulness

**When:** 2026-07-21T04:27:58Z · **From:** coordinator (online)

Task-board: ledger-audit-remediation-packet4-ci-gate-truthfulness-2026-07-21
Task ID: ledger-audit-remediation-packet4-ci-gate-truthfulness-2026-07-21
Status: ACTIVE — PACKET 4 CI AND GATE TRUTHFULNESS
Route generation: 12
Supersedes route: coordination/mailbox/sent/2026-07-21T04-13-05Z-coordinator-to-all-coordination.md
Expected control HEAD: ba9494b53d409137203db87cb17c5ef1b45cd378
Superseded route ref: coordination/mailbox/sent/2026-07-21T04-13-05Z-coordinator-to-all-coordination.md@8add50067d7ab3fc3f66ede119878e379d511d3c
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:authorized-then-continue-task-2026-07-21
Accepted Packet 3 GO: coordination/mailbox/sent/2026-07-21T03-27-09Z-operator2-to-all-verification-report.md@571960f7614e394a7a7e9e49f42ec789b7e30151
Accepted Packet 3 integration evidence: coordination/mailbox/sent/2026-07-21T04-22-15Z-director-to-all-coordination.md@ba9494b53d409137203db87cb17c5ef1b45cd378
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 4 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-ci-gate-truthfulness.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 4 plan SHA-256: 308dab0c23447079385aca9818c80c6bc120bf9219fbd888c92ed9594a6ee45a
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ci-truthfulness
Target branch: codex/audit-remediation-ci-truthfulness
Target base: 09127b5e486c0b6ca25f84d1bf4b835f41f52375
Accepted target HEAD: 09127b5e486c0b6ca25f84d1bf4b835f41f52375
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Outcome Contract

Execute the approved Packet 4 plan test-first in one dedicated target worktree.
The omitted checklist-coverage suite must execute in the hermetic CI lane, and
R4 must require one exact workflow invocation of a fixed standard-library runner
whose exported argv executes `tests/unit --runxfail`. Comments, step names,
unrelated marker strings, alternate scripts, and folded commands must not
satisfy the gate.

Keep the current architecture and existing verdict semantics. This packet adds
no YAML parser, framework, service, event type, approval step, or remote-CI
claim. It changes only the executable evidence path and its truthful docs.

## Director Autonomous Contract Revision 13

Before target mutation, Director publishes exactly one fresh director-to-all
coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-audit-remediation-packet4-ci-gate-truthfulness-2026-07-21
- Outcome contract: Execute the approved Packet 4 plan test-first in one dedicated target worktree, create exactly one verified target commit, and submit the immutable actual range for independent Operator2 review.
- Parent contract: this committed generation-12 Coordinator route's exact path at its full commit SHA
- Contract revision: 13
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: the full immutable ref of this route plus sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec and sha256:308dab0c23447079385aca9818c80c6bc120bf9219fbd888c92ed9594a6ee45a

Director proves the contract effective and global route lineage valid, then runs
the ordinary ledger Director start guard against that exact committed event.
Director uses the existing compatible Director Codex task and executes the
written plan directly; a child implementer is outside scope.

## Side-Effect Executor Token

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ci-truthfulness
- scope: branch=codex/audit-remediation-ci-truthfulness, parent=09127b5e486c0b6ca25f84d1bf4b835f41f52375

## Target Allowed Paths

- scripts/run_regression_pins.py
- scripts/check_no_ceremony.py
- tests/unit/test_regression_pin_runner.py
- tests/unit/test_ceremony_gates.py
- .github/workflows/ci.yml
- ARCHITECTURE.md
- OPERATIONS.md

Every other target path is frozen. All fixtures and probes are synthetic. The
normal checkout's pre-existing `.vscode/settings.json` remains untracked and
byte-identical at the protected hash above.

## Exact Preflight

Director stops without target mutation unless one fresh observation proves:

- Pipeline contains this exact committed route and its effective revision-13
  Director child; route validation, global lineage, and ledger start guard pass;
- evidence-ledger normal `main` and HEAD equal the accepted target head, with
  `.vscode/` as its only status entry and the protected settings hash unchanged;
- the authorized target worktree path and branch do not already exist;
- the approved design and Packet 4 plan bytes match their stated SHA-256 values;
- target base `09127b5e486c0b6ca25f84d1bf4b835f41f52375` is available locally; and
- no service, database stack, network call, or private-data access is needed.

Director creates only the exact local branch/worktree in the token, confirms the
new worktree is clean at the exact parent, then executes the plan in order.

## Exact Implementation Contract

### 1. Fixed regression-pin runner

Add `scripts/run_regression_pins.py` with standard-library imports only. Its
public `pytest_argv` must return exactly `sys.executable`, `-m`, `pytest`,
`tests/unit`, `--runxfail`, `-q`; `main` invokes `subprocess.run` exactly once at
the repository root, without a shell, and returns both zero and nonzero child
codes unchanged. No arbitrary CLI targets or extra arguments are permitted.

### 2. R4 executable contract

Replace the substring detector with two pure helpers. The workflow helper accepts
only the exact non-comment line `run: python scripts/run_regression_pins.py`.
The runner helper loads only the canonical local module without calling `main`
and accepts only the exact synthetic-python argv contract. It must fail closed
without crashing for the routed import, syntax, attribute, file, and type errors.

Pin positive behavior and separate negative controls for a comment, a step name,
an unrelated `echo --runxfail`, another script, a folded command, and a runner
whose argv omits `--runxfail`. Preserve R1, R2, R3, R5, R6, architecture
freshness behavior, reviewer authority, and verdict semantics unchanged.

### 3. CI execution truth

Replace the raw pin command with exactly one single-line workflow invocation of
the fixed runner and remove comments that can spoof `--runxfail`. Add
`import/tests/test_checklist_coverage_unit.py` to the existing hermetic import
command while preserving all eight Packet 3 suites and excluding live-DSN files.

### 4. Truthful documentation

Collect the exact unit and hermetic inventories after implementation and use the
integers emitted by pytest. Update both architecture verification stamps against
the exact Packet 4 parent. Document the runner, exact R4 witness, negative spoof
cases, checklist CI execution, and unchanged architecture-freshness mechanism.
Do not claim a local run was a remote GitHub Actions run.

## TDD, Commit, And Verification

Director records focused failing tests before each production change, including
collection failure for the absent runner and failing R4 spoof/contract controls.
Director then creates exactly one local target commit with subject:

`fix(ci): require executable regression evidence`

The final range must be exactly one commit after the target base and exactly the
seven allowed paths. Stage explicit pathspecs only and preserve unrelated state.

On committed bytes, run the exact focused ceremony/runner tests, the fixed runner
itself, `scripts/check_no_ceremony.py`, the 13-test checklist suite, the exact
edited import-hermetic command and both collection inventories, documentation
anchors, architecture freshness, target `scripts/ci_smoke.py`, `git diff
--check`, exact range/path manifest, and clean-worktree checks. No acceptance
command may contact Postgres, start a service, access private data, or write a
remote-CI claim.

## Independent Review Contract

After every committed-byte gate passes, Director publishes exactly one immutable
verify-request assigned to non-author Operator2 and dispatches the existing
compatible Operator2 Codex task exactly once. The request binds the target
repository, exact base/head/one-commit range, seven-path manifest, author and
reviewer identities, RED/GREEN evidence, exact emitted counts, docs/smoke
evidence, and distinct finding refs for:

- checklist suite execution in CI;
- exact workflow runner invocation;
- fixed runner argv;
- shell-free subprocess behavior and return-code propagation;
- comment spoof rejection;
- step-name spoof rejection;
- unrelated-string and alternate-script rejection;
- folded-command rejection; and
- unchanged architecture-freshness behavior.

Operator2 must run the committed runner and negative R4 controls against the
actual range; generic smoke alone is insufficient. Operator2 is the only seat
authorized to issue GO, NITS, or FAIL. Director stops at that verdict. A verdict
grants no later effect authority.

## Frozen Boundaries

Target-main integration authority: none.
Remote-reference publication authority: none.
Target branch/worktree cleanup authority: none.
Dependency installation and network authority: none.
Service, local/managed database, managed Auth, and private-data authority: none.
Architecture-freshness mechanism change authority: none.
R1, R2, R3, R5, R6 and verdict-semantics change authority: none.
Cursor and protocol-lock authority: none.
Provider, deployment, booking, and spend authority: none.
Reset, rebase, amend, squash, revert, force deletion, and unrelated cleanup authority: none.

## Exact Next Trigger

Director reads this committed generation-12 route, publishes and proves its
revision-13 autonomous contract, runs the exact preflight, creates only the
authorized worktree, and executes the approved Packet 4 plan test-first. Director
creates exactly the one local target commit, proves the immutable actual range,
publishes the single verify-request, dispatches Operator2 once, and stops for the
independent verdict. Any lineage, RED-evidence, scope, test, documentation,
smoke, manifest, synthetic-data, or clean-state failure returns to Coordinator
with both repositories preserved.

Cursor at send: 0
