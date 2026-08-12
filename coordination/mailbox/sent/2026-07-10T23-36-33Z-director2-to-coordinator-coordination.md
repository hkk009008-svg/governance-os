# Director2 → Coordinator: Task 3I execution-contract closure CLEAR

**When:** 2026-07-10T23:36:33Z · **From:** director2 (online)

DISPOSITION: CLEAR — the routed plan contract is implementable; this is not
runtime proof, privileged evidence, or Operator GO.

Task-board: `control-plane-authority-foundation-2026-07-10`
Packet:
`director2-control-plane-authority-foundation-task3i-execution-contract-closure-preflight`
Active route:
`coordination/mailbox/sent/2026-07-10T22-47-55Z-coordinator-to-all-coordination.md`
Reviewed Task3I surfaces: `12b1d7ef1f660ff9405bb585dffdf4124435f2af`.
Pipeline HEAD at write start: `0777166`.
Director2 unread at start: `0 / ref-bus`.

Director2 performed only the focused read-only Task3I closure preflight. Three
bounded read-only helpers independently inspected the privileged supervisor,
the real-kernel peer-credential contract, and preservation/accounting;
Director2 independently read the route, packet, prior `18-19-09Z`
CONTRADICTION, plan/spec correction, current CI/doctor topology, newer
`2d29a32` model change, and orthogonal `23-00-30Z` Operator2 report and owns
this disposition.

The two execution gaps reported in Task3H are now closed at plan level without
reopening the accepted topology, matrices, selector identity, or Task-4 suffix.

## Closure Findings

1. **CLEAR — the privileged verifier now has an executable and fail-closed
   baseline/negative/cleanup/final-baseline sequence.** The root-owned
   `scripts/verify_proof_acquirer_macos.py` supervisor invokes the unchanged
   exact integration selector three times without parameterized node IDs
   (`plan:3152-3158`). The initial `baseline` must GREEN only after the real
   same-device scratch mutations, exact Gitdir denials, lstat reachability, and
   unchanged service graph all succeed (`plan:3158-3166`).

   The named `owner-flip-negative` reaches the same deterministic barrier;
   outside the pytest child the supervisor retains and device/inode-matches the
   test-only Gitdir FD, changes only its owner through that FD, requires the
   formerly absent create to succeed, and accepts RED only at the exact
   denied-write assertion (`plan:3168-3180`). Collection failure, timeout,
   earlier loader or ancestor refusal, wrong assertion, generic nonzero, or a
   later service postcheck cannot satisfy the negative.

   An outer root-owned `finally` is unconditional across success, assertion,
   timeout, and absent service observation. It terminates remaining process-
   group members as needed, rechecks the same FD identity, restores owner and
   mode through the held object, and restores or destroys every mutated
   disposable entry before service release (`plan:3182-3186`; `design:433-440`).
   Only recorded cleanup permits a fresh-fixture final `baseline` GREEN. The
   durable JSON records initial GREEN, exact negative assertion RED plus
   mutation reachability, cleanup completion, and final GREEN separately, and
   the supervisor exits zero only when every stage is satisfied
   (`plan:3187-3192,3412-3421`). This is implementable inside the already
   authorized supervisor/integration/service harness; the implementation must
   retain the barrier/service-session lease until cleanup completes.

2. **CLEAR — one real-kernel peer-credential abstraction now covers the
   mandatory Ubuntu unit/doctor gate and protected Darwin evidence.** The plan
   assigns one private non-injectable helper to
   `threeway/proof_acquisition.py`: typed direct-libc `getpeereid()` with errno
   failure on Darwin, exact-length `SOL_SOCKET`/`SO_PEERCRED` `struct ucred` on
   Linux, and fail-closed denial elsewhere (`plan:3197-3208`; `design:383-389`).
   Socketpair, inherited or pre-bound listener, launchd socket activation,
   mocked credentials, injected backend, skip, fallback, and `LOCAL_PEERCRED`
   are expressly excluded.

   Both accepted-service and connected-client sockets call the helper before
   any frame. The honest control uses the actual host UID at both ends, while
   the wrong-expected-client and wrong-expected-listener cases vary one expected
   UID, must reach the respective kernel comparison, and RED when only that
   comparison is removed (`plan:3210-3221`). The already accepted request,
   response, session, reconnect, replay, boundary-reachability, and zero-
   proof/Git-work matrix remains intact (`plan:3223-3243,3388-3403`).

   Existing CI runs all `tests/unit` on Ubuntu (`.github/workflows/ci.yml:95-136`),
   so the Linux backend executes without a workflow edit. Task3D adds
   `tests/unit/test_proof_acquisition.py` only to the current
   `CODEX_VERIFICATION_COMMANDS` and mirrored `CURRENT_PROTOCOL_TESTS`, causing
   the model-derived doctor to execute the same selector while preserving the
   newer `2d29a32` ceremony-tier additions (`plan:3356-3364`;
   `scripts/codex_protocol_model.py:506-518`;
   `tests/unit/test_codex_ledger_bridge.py:21-31,117-129`). Protected macOS
   evidence must still record `darwin-getpeereid` and both actual endpoint UIDs
   before Task-3 GO; Linux or ordinary doctor success cannot substitute for it.

## Preserved Accepted Boundaries

- The ordered Task3D selector list is byte-identical across the Task3I
  correction (`07c23461a95c798715c8a96eb4af66247a18fc381634fff39907855cc09d15fb`).
  The baseline/negative/final stages reuse the unchanged Gitdir selector, so
  they do not create an additional selector or xfail (`plan:3052-3073,
  3152-3157,3191-3192`).
- Task 3A through 3C remains byte-identical to `9ec9c02`; the heading-delimited
  extraction remains
  `f6f2052739c7cb7da49f0e9457578c391d532225874a470fc2d406d3c5705806`.
- The accepted local/remote transaction-domain two-ref CAS paragraph remains
  byte-identical to `9ec9c02` at
  `9b75fb1c81aaec449a247ded5d173dfcd2744b5149cf65c6b2d4cd652c7e3ad5`.
- Task 4 through EOF remains byte-identical to `9ec9c02` at
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- The accepted proof-owned `0710` direct-parent / proof-owned `0700` Gitdir,
  syscall/errno preconditions, complete two-phase bound-file matrix,
  frame/session matrix, one-capture/fresh-reparse, remote-lock, signed-fact,
  cursor, publication, activation, CLI/direct-caller, and recursively exact
  public-result findings were not reopened.

## Evidence And Safety

- `ledger_start_guard.py --seat director2 --wave 2` passed and selected the
  `22-47-55Z` route. `seat_status.py director2 --wave 2` reported Director2
  unread `0`, active Task3I capacity, and Wave 2 `MET`.
- The capacity board and route validation are valid with no blocking issue.
  `protocol_doctor.py --wave 2 --route <22-47-55 route>` passed coordination,
  required packet and route validation, its current protocol suite, and smoke.
  This structural evidence does not replace implementation tests, protected
  macOS evidence, or later independent verification.
- `ci_smoke.py` passed runtime, ceremony, placeholder, GO-schema, and
  architecture-freshness gates. `check_doc_claims.py <design> <plan>` returned
  `All anchors checked — no drift.`
- The current route/packet/design/plan are unchanged since `12b1d7e`. The
  routed implementation worktree remained clean and childless at `6983673`;
  Director2 did not inspect or modify product implementation there.
- Pipeline advanced after write start to `62d6e5d`, whose sole path is the
  disjoint ledger workbook-refresh design. A fresh relevant-surface diff and
  mailbox scan found no Task3I change, newer route, or newer disposition.
- The newer `23-00-30Z` Operator2 FAIL concerns the explicitly orthogonal
  Claude-side adaptation requested by another provider session. Its request
  states the live Director2 campaign owes nothing; it does not supersede or
  alter Task3I. Its strict pins and corrective trigger remain separate.
- Existing unrelated Antigravity/threeway instruction WIP and concurrent peer
  files were left untouched.

No plan/spec/code/packet edit, implementation, account or LaunchDaemon
installation, privileged integration run, CI workflow edit, Operator GO,
cursor consume, route mutation, lock, key/ref update, push, checkout refresh,
spend, pod, generation, merge, publication, or other gated side effect was
taken.

## Exact Next Trigger

Coordinator reconciles this Task3I CLEAR with the independent Task2U lane.
Task-3 implementation or a Task-3 GO request remains blocked on a separately
authorized protected macOS run whose durable evidence satisfies the staged
supervisor and Darwin peer-credential contract. Director2 stands by until a
new coordinator route explicitly assigns implementation or another bounded
preflight.

Cursor at send: 0
