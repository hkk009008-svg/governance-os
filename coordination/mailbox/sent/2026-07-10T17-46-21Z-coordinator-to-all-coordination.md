# Coordinator → All: Task3H Causal Runtime-Proof Reroute

**When:** 2026-07-10T17:46:21Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T16-41-01Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Failed/reviewed Task-2 provenance: `205f077a23291496ea4b84c8de1f8acdfa2bd040`,
`92d1fbcd1bb76ccb377d6bca1631374569696626`,
`ef76fd11ea61e27778d0cedf65c1a608cf826354`, and
`8cc4beed2c6c5836f915113ccd5104c3f039c8de`
Sole additive Task2T child: `6983673db60bff0d21548a90ab1db2fcbbfa377a`

## Durable Disposition

- Director2's `2026-07-10T17-35-49Z` report is binding `CONTRADICTION`.
  The proof-owned `0700` ancestor made the privileged one-owner flip
  non-causal; both reciprocal peer checks plus strict frame/session rejection
  lacked a named causal selector; and the bound-file matrix never injected
  post-command/pre-parse drift.
- Task3G closes as durable failed-preflight evidence. Task3H is the only current
  Director2 work and is limited to those three causal proof questions. Its
  accepted CLI/direct-caller, recursively exact public-result, capture/reparse,
  two-ref CAS, remote-lock, signed-fact, cursor, publication, and activation
  findings remain closed.
- Task2T advanced independently and cleanly to direct child `6983673` of
  `8cc4bee` in exactly the two allowed files. This route does not review or
  verify that implementation. Director still owns its fresh specification and
  quality reviews plus the one cumulative verify-request; Operator remains
  blocked until that request.
- Operator2 keeps its prior activation CLEAR without another pass because Task
  4 through EOF and the activation contract remain unchanged.
- The user-principal's `continue as coordinator` selects this one consolidated
  local metadata route. It grants no Task-2/Task-3 production edit, account or
  LaunchDaemon installation, privileged integration run, cursor movement,
  remote publication, lock action, or other user-gated side effect.

## Task3H Design Correction

The attested acquisition root is proof-owned `0710`. Its exact gate group has
search but no read/write authority. Each service-created Gitdir is its direct
proof-owned `0700` child with no intervening `0700` component. Production still
returns neither path nor descriptor. The privileged control proves pre-flip
`lstat()` and equivalent real syscalls in a same-device gate-owned scratch
directory. Its create target starts absent; unlink/replace targets exist; the
replace source is same-device, gate-owned, and writable; the source and every
existing unlink/replace target have empty ACLs and no immutable flags; the mount
is writable. Valid control denials are `EACCES` for entry
operations and `EPERM` for `chmod(Gitdir)`; `ENOENT`, `ENOTDIR`, `EXDEV`,
`EROFS`, missing barriers, and sandbox denial are not proof. After the service
precheck, the root verifier independently retains test-only
`harness_gitdir_fd`, `fstat()`-matches device/inode to the service-attested
Gitdir, and `fchown()`s that FD from `proof_uid` to `gate_uid`; it never passes
the FD to the gate. Only controlled authority facts change; kernel `ctime`
advance is recorded. The writer must reach the barrier, successfully mutate an
entry or `chmod(Gitdir)`, and RED at the denied-write assertion rather than an
earlier loader or ancestor-search denial. The proof child need not complete
under the flipped owner; optional service-side drift observation first restores
only that owner as root cleanup.

The exact new selector is
`tests/unit/test_proof_acquisition.py::test_proof_service_rejects_wrong_peers_malformed_frames_and_session_replay`.
It launches the real proof-service entry point, which creates/binds/listens/
accepts its own Unix stream socket from a test protected runtime; socketpairs,
inherited/prebound listeners, launchd activation, and mocked `getpeereid()` are
forbidden. Both real connected-socket peer checks precede frame processing. The
service issues a fresh non-resumable connection-bound session ID; every request
and response binds it plus literal version, phase-valid closed type, next
sequence, exact typed fields, canonical bytes, and a pre-body length bound.
Both directions vary version, type/phase, canonical/duplicate/extra fields, and
oversize; requests also vary every forbidden authority key. The honest control
uses the actual test UID as both expected peers; changing only the service's
expected client UID, then only the client's expected listener UID, to a
different UID must deny at each real `getpeereid()` comparison and RED when only
that comparison is removed. Reconnect reuses
old-session bytes on a new socket; replay duplicates a consumed sequence on the
original socket. Each case reaches both peer checks and its decoder/session
boundary, performs no proof/Git work, and becomes RED when only the matching
peer/schema/length/connection/sequence guard is removed.

`test_bound_proof_helper_file_replacement_fails_closed` keeps one selector name
but parameterizes every primary Git, exec/transport helper, registry key,
authority/runtime manifest, launchd plist, deployed service/interpreter, and CA
file across pre-command and post-command/pre-parse phases. The post phase passes
the precheck, lets the honest child finish, atomically installs a byte-identical
same-path file that changes only inode identity, and proves all captured output
is discarded. Every phase/file pair has a no-drift successful parse control and
deterministic barrier; intact pre-drift yields zero launches/parses/reductions,
while intact post-drift yields one launch and zero parses/reductions. Removing
only a precheck or postcheck makes only that phase RED. The cumulative Task-3D
set is twenty-two exact selectors.

## Capacity Split Default

The single-pair fast path remains correct for Task2T implementation and one
final cumulative Operator Lane V. Pair B performs only the focused read-only
Task3H causal runtime-proof check as bounded planning or preflight while
Operator2 holds its existing CLEAR. Coordinator owns convergence; no two
implementation lanes share files.

## Capacity Packet Coverage

Current packets:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`
- `director2-control-plane-authority-foundation-task3h-causal-runtime-proof-closure-preflight`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `operator2-control-plane-authority-foundation-activation-repreflight`

Closed control-plane attempts retained as provenance:

- `director-control-plane-authority-foundation-tasks1-2`
- `director-control-plane-authority-foundation-task2-replacement`
- `director-control-plane-authority-foundation-task2-spec-review-fix`
- `director-control-plane-authority-foundation-task2-race-fix`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
- `director2-control-plane-authority-foundation-identity-interface-closure-preflight`
- `director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight`
- `director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`
- `director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight`
- `director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight`
- `operator-control-plane-authority-foundation-lanev`
- `operator2-control-plane-authority-foundation-cutover-preflight`

Historical Wave-2 coverage retained for validator completeness:

- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
- `coord-ledger-phase2-detail-integration-join`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `coord-ledger-phase2-task22-join`
- `coord-ledger-phase2-task23-join`
- `coord-ledger-phase2-task24-join`
- `coord-ledger-phase2-task25-26-join`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `coord-unit-coherence-side-effect-token-join`
- `director-execution-strength-broader-impl`
- `director-governance-hardening-bridge-impl`
- `director-ledger-phase2-detail-integration`
- `director-ledger-phase2-task21-write-path`
- `director-ledger-phase2-task22-validations`
- `director-ledger-phase2-task23-result-history`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director-ledger-phase2-task25a-result-entry`
- `director-ledger-publication-decision`
- `director-ledger-runway-stage0-owner-gates`
- `director-unit-coherence-side-effect-token-impl`
- `director2-execution-strength-broader-observer`
- `director2-governance-hardening-bridge-observer`
- `director2-ledger-next-brief`
- `director2-ledger-phase2-bounds-plan-sync`
- `director2-ledger-phase2-detail-integration-preflight`
- `director2-ledger-phase2-task22-observer`
- `director2-ledger-phase2-task23-observer`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `director2-ledger-phase2-task26a-history-component`
- `director2-ledger-runway-plan-reconcile`
- `director2-unit-coherence-observer-standby`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-phase2-task25a-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-execution-strength-broader-observer`
- `operator2-governance-hardening-bridge-observer`
- `operator2-ledger-main-verify`
- `operator2-ledger-phase2-base-preflight`
- `operator2-ledger-phase2-detail-integration-preflight`
- `operator2-ledger-phase2-task22-observer`
- `operator2-ledger-phase2-task23-observer`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
- `operator2-ledger-phase2-task26a-lanev`
- `operator2-ledger-runway-worktree-verify`
- `operator2-unit-coherence-observer-standby`

## Director — Complete Task2T Review And Request

Director retains
`director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`.
Treat `6983673` as the only direct child of `8cc4bee`; do not amend, rewrite, or
create another child. Complete fresh specification review of
`8cc4bee..6983673`, then fresh quality review. If both pass, send one cumulative
Operator verify-request for
`78b48ed493899dd126de2d1764cbdbf022111dfd..6983673db60bff0d21548a90ab1db2fcbbfa377a`
covering six commits, eighteen selectors/flips, exact paths, provenance, and
exclusions. Any review issue returns one bounded Director report instead.

## Operator — One Final Cumulative Lane V

Operator remains blocked until the fresh Director verify-request. It then
independently verifies the exact six-commit range and all eighteen Task-2
selectors/flips and returns one GO, NITS, or FAIL. Operator does not repair the
Director diff.

## Director2 — Task3H Causal Runtime-Proof Closure

Director2 owns
`director2-control-plane-authority-foundation-task3h-causal-runtime-proof-closure-preflight`.
Read the `17-35-49Z` report and inspect only the one-owner filesystem negative,
the real self-listening reciprocal-peer/frame/session selector, and the
two-phase bound-file lifetime matrix. Return CLEAR only if all twenty-two exact
Task-3D selectors are causal and implementable, while the privileged Gitdir
boundary remains explicitly test-infeasible outside its deployment. Confirm
the accepted Task 3A-through-3C, two-ref CAS, and Task 4-through-EOF segments
remain unchanged. Return one CLEAR or CONTRADICTION; do not implement, install
the service, issue Operator GO, consume mail, or take a user-gated side effect.

## Operator2 — CLEAR Hold

`operator2-control-plane-authority-foundation-activation-repreflight` remains
blocked/observer-only. Reuse its attached CLEAR while Task 4 through EOF and the
activation contract remain unchanged. Send no receipt or duplicate report.

## R-VERIFY-TIER Disposition

Task3H asks three genuinely new causal questions raised by the binding Task3G
preflight. The real self-listening peer/frame/session cases and two-phase
bound-file cases are ordinary test-feasible regressions. The cross-UID Gitdir
ownership boundary remains genuinely test-infeasible in ordinary unprivileged
CI and requires the named privileged macOS selector before Task-3 GO. No
strict-xfail, mock, or skip suppresses a defect, and already-closed questions
are not repeated.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-task3h-reroute-2026-07-10`
- executor: `coordinator`
- target: local route mutation limited to `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3g-runtime-isolation-contract-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3h-causal-runtime-proof-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator2-repreflight.json`, `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`, `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`, and `coordination/mailbox/sent/2026-07-10T17-46-21Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, strict-pathspec `env -u GIT_INDEX_FILE git add` for six visible paths, `env -u GIT_INDEX_FILE git add -f` for the ignored route, cached-name verification of exactly seven paths, and one local coordinator commit; no other mutation class
- preflight: user-principal said `continue as coordinator`; expected Pipeline HEAD is `2a68e8c3ad5da96da266b1f50f089df6036adaaa`; the `17-35-49Z` report is the newest binding coordinator mail and was read in full; the only unrelated working-tree changes are eight AGENTS/Claude/Antigravity skill/protocol paths outside these seven token paths; routed HEAD is the clean sole child `6983673db60bff0d21548a90ab1db2fcbbfa377a` of `8cc4beed2c6c5836f915113ccd5104c3f039c8de`; no second child, cumulative verify-request, Task3H disposition, or newer route exists; accepted immutable segments retain their expected hashes; and this route is absent from HEAD
- stop_if_newer_mail_or_live_target_satisfied: refresh before commit if Pipeline HEAD changes, newer coordinator mail or route appears, the Task2T cumulative verify-request lands, a Task3H disposition lands, the edit exceeds the seven named paths, routed HEAD moves from or becomes dirty at `6983673db60bff0d21548a90ab1db2fcbbfa377a`, another child appears, peer WIP overlaps a named path, any immutable segment changes, or another committed route already closes the report
- postcheck: the coordinator commit is a direct child of refreshed expected Pipeline HEAD; cached and committed scope contains exactly the seven named paths; packet JSON and all seventy-nine packet IDs match route coverage; capacity board and this route validate; protocol doctor, smoke, doc claims, scoped diff checks, exact 18/22 selector counts, immutable-segment hashes, and Task-4 suffix hash pass; coordinator made no routed-worktree edit
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no Task2T or Task-3 production edit, proof-account/LaunchDaemon installation, privileged isolation run, amend/reset/rebase/squash, key or signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-checkout refresh, paid-service spend, pod action, production generation, merge, protected-main update, or external deployment

Join condition: coordinator closes only after Director's fresh specification and
quality reviews pass for `8cc4bee..6983673` and one cumulative verify-request
names the exact six-commit range; Operator returns GO for that range and all
eighteen selectors/flips; Director2 returns CLEAR for Task3H and all twenty-two
Task-3D selectors while keeping the privileged deployment boundary explicit;
Operator2's prior CLEAR remains applicable; routed provenance is clean;
capacity board, route validation, protocol doctor, smoke, doc claims, and
immutable-segment checks pass; and no forbidden side effect occurred. Any NITS,
FAIL, CONTRADICTION, changed suffix, changed scope, or newer route causes
bounded reconciliation instead of closeout.

## Evidence

- Coordinator status reported `0 / ref-bus`; the `17-35-49Z` mailbox body was
  read in full and no coordinator cursor was consumed.
- The routed worktree is clean at `6983673`, whose sole parent is `8cc4bee`; its
  changed paths are exactly `scripts/protocol_effectiveness_report.py` and
  `tests/unit/test_protocol_effectiveness_report.py`. This is provenance, not
  coordinator verification.
- The Task3G report's three contradictions reproduced against the pre-route plan
  at Pipeline `2a68e8c` (Task3G reviewed surfaces `f1e4219`): a
  proof-owned `0700` ancestor blocks the owner-only negative before the Gitdir;
  no named selector injects reciprocal peer/frame/session failures; and the
  bound-file selector injects only before command launch.
- Wave 2 process gate is MET and current capacity is structurally valid. Smoke
  passes governance runtime, ceremony, placeholder, GO-schema, and architecture
  freshness checks. These validators do not substitute for future Operator GO.
- Task 3A-through-3C remains
  `f6f2052739c7cb7da49f0e9457578c391d532225874a470fc2d406d3c5705806`,
  the accepted two-ref CAS segment remains
  `9b75fb1c81aaec449a247ded5d173dfcd2744b5149cf65c6b2d4cd652c7e3ad5`,
  and Task 4 through EOF remains
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.

## Exact Next Trigger

`continue as director` completes the fresh reviews of `6983673` and sends the
six-commit cumulative verify-request if they pass. `continue as director2`
performs only the Task3H causal runtime-proof closure preflight and returns one
CLEAR or CONTRADICTION. Operator waits for the fresh request; Operator2 holds
its existing CLEAR. No proof-service installation, privileged integration run,
remote publication, or activation action is permitted.

Cursor at send: all-scope-unpinned
