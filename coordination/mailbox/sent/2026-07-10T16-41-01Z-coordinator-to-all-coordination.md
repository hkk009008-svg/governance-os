# Coordinator → All: Task2T And Task3G Fail-Visible/Isolation Reroute

**When:** 2026-07-10T16:41:01Z · **From:** coordinator (online)

Event type: coordination
Task-board: `control-plane-authority-foundation-2026-07-10`
Supersedes route: `coordination/mailbox/sent/2026-07-10T14-25-40Z-coordinator-to-all-coordination.md`
Route base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Accepted Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Failed Task-2 candidate retained as provenance: `205f077a23291496ea4b84c8de1f8acdfa2bd040`
Reviewed-but-spec-failed Task-2 children retained as provenance:
`92d1fbcd1bb76ccb377d6bca1631374569696626`,
`ef76fd11ea61e27778d0cedf65c1a608cf826354`, and
`8cc4beed2c6c5836f915113ccd5104c3f039c8de`

## Durable Disposition

- Director's `2026-07-10T15-41-08Z` report is binding `BLOCKED / FRESH
  SPECIFICATION REVIEW ISSUES`: one global canonical mailbox-scan failure is
  recorded as invalid but then converted to an empty event list, rendering four
  false-clean zero counts and two false-success all-scope observations.
- Director2's `2026-07-10T15-18-04Z` report is binding `CONTRADICTION`: a
  gate-owned proof Gitdir remained mutable by another same-UID process; the
  bound-file selector did not place replacement after runtime load or include
  primary Git; CLI authority inputs and two direct callers exceeded the write
  set; and hostile Python equality could forge public comparison success.
- Task2S and Task3F close as durable failed-review/preflight evidence. New
  Task2T and Task3G packets are the only current Director and Director2 work.
  Operator remains blocked until one fresh cumulative request; Operator2 keeps
  its prior activation CLEAR without another pass.
- Task2T is one normal test-feasible correction to an unmerged candidate, not a
  suppressive pin. Task3G names a real distinct-UID deployment boundary and an
  honest privileged macOS selector; ordinary unprivileged CI is explicitly
  test-infeasible for that OS claim and no mock or skip may close it.
- Director2 preserved the already-confirmed one-capture/fresh-reparse,
  local/remote two-ref CAS, remote-lock, signed-fact, cursor, publication-
  grammar, and activation findings. Task 4 through EOF remains byte-identical
  at SHA-256
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- The routed worktree is clean at `8cc4bee`, whose sole parent is `ef76fd1` and
  which has no child. Unrelated AGENTS/Claude/Antigravity WIP remains outside
  this ten-path coordinator transition.

The user-principal's `continue as coordinator` selects one consolidated local
route mutation covering both binding reports. It grants no production edit,
account or LaunchDaemon installation, cursor movement, remote publication,
lock action, or other user-gated side effect.

## Task2T Design Correction

`collect_report()` retains a distinct global canonical-scan error from the one
`scan_mailbox_events()` call. A completed scan with malformed individual
envelopes remains available and computes unread from its valid events. If the
complete scan raises, all four pair and both coordinator observations are typed
`unavailable`; no numeric zero or `all-scope-unpinned` success is emitted. The
same error remains visible in invalid-scan metrics, cursor text remains
separately observable, and no second scan occurs.

The exact new selector is
`tests/unit/test_protocol_effectiveness_report.py::test_collect_report_marks_every_reader_unavailable_when_canonical_scan_fails`.
Its honest control uses valid cursors, one valid `to-all` event, and one invalid
individual envelope; its regression injects a global scanner exception; and
its one-fact flip ignores only the retained global error. The cumulative Task-2
set is eighteen named selectors.

Task2T is exactly one additive child of `8cc4bee`. The implementation scope is
only `scripts/protocol_effectiveness_report.py` and
`tests/unit/test_protocol_effectiveness_report.py`.

## Task3G Design Correction

The protected runtime binds distinct nonzero `gate_uid` and `proof_uid` values.
A root-protected system-domain LaunchDaemon runs a locked non-login proof
account, but the proof service itself binds/listens on the fixed protected Unix
stream socket so effective peer credentials name the proof UID rather than a
socket-activating launchd listener. The service accepts only the gate UID and
the client only the proof UID. Only the proof UID owns the private `0700`
Gitdir. The gate receives strict versioned canonical frames and never a proof
path, descriptor, Git command, URL/ref/registry/bus/policy/helper choice, or
writable capability.

The proof service retains the descriptor-bound fork/fchdir/execve runner,
no-config Gitdir, HTTPS-only acquisition, attested helpers/CA, and environment
built from empty. After successful runtime load and before every command, it
reopens and rechecks the runtime manifest, launchd plist, deployed service and
interpreter, primary Git executable, every exec/transport helper, every registry
key, authority manifest, and CA file. Post-command drift discards the output.
The bound-file selector replaces each item at that barrier and makes removal of
only its lifetime check RED.

`run_merge_gate.py`, `poll_once()`, `scripts/run_merge_gate.sh`, and the
activation-script direct caller expose no registry, bus, gate-seat, or policy
input. The parser rejects those flags and no compatibility authority keyword
remains. Public apply recursively requires exact dataclass/enum/scalar/container
types, canonicalizes validated primitives without invoking attacker equality,
compares the fresh exact-string outcome to literal `MERGEABLE`, and uses only
the fresh binding downstream.

Task3G adds
`tests/integration/test_proof_acquisition_macos.py::test_gate_uid_writer_cannot_mutate_proof_service_gitdir`
to the prior twenty selectors. That privileged control deliberately reveals the
service Gitdir to a gate-UID writer and proves create/replace/chmod/delete denial
plus an unchanged graph; changing only ownership/isolation so the gate UID owns
the Gitdir makes it RED. Unit mocks cover protocol behavior but never satisfy
the deployment gate. The cumulative Task-3D set is twenty-one selectors.

## Capacity Split Default

The single-pair fast path remains correct for tightly coupled Task2T
implementation and one final cumulative Operator Lane V. The production change
is not safely divisible. Pair B therefore performs only the focused read-only
Task3G runtime-isolation/contract check as bounded planning or preflight while
Operator2 holds its existing CLEAR. Coordinator owns convergence.

## Capacity Packet Coverage

Current packets:

- `coord-control-plane-authority-foundation-join`
- `director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`
- `director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight`
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

## Director — Task2T Global-Scan Fail-Visible Fix

Director owns
`director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`.
Preserve topology
`78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> ef76fd1 -> 8cc4bee` and land exactly
one direct child of `8cc4bee`. Use the same corrective implementer with strict
TDD for the single new regression, completed-scan control, one-fact flip, and
restoration. Run all eighteen cumulative selectors and focus, then obtain fresh
specification review of `8cc4bee..<fail-visible-child>`. Only after
specification passes run fresh quality review and send one cumulative Operator
verify-request for `78b48ed493899dd126de2d1764cbdbf022111dfd..<fail-visible-child>`
covering six commits. Do not amend, rewrite, or create another child.

## Operator — One Final Cumulative Lane V

Operator remains blocked on the new Director packet and fresh verify-request.
It then independently verifies the six-commit cumulative range and all eighteen
selectors/flips and returns one GO, NITS, or FAIL. Operator does not repair the
Director diff.

## Director2 — Task3G Runtime Isolation/Contract Closure

Director2 owns
`director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight`.
Read the `15-18-04Z` report and inspect only the distinct proof-service UID and
self-listening peer-authenticated boundary, causal bound-file lifetime matrix,
CLI/direct-caller authority-input removal, recursively exact public-result
comparison, and privileged writer selector. Return CLEAR only if all twenty-one
Task-3D selectors are exact, causal, and implementable, with the privileged OS
boundary honestly labeled test-infeasible outside its deployment. Inherit the
confirmed capture/reparse, two-ref CAS, remote-lock, signed-fact, cursor,
publication, and activation findings without another pass. Confirm their plan
segments and Task 4 onward remain unchanged. Return one CLEAR or CONTRADICTION;
do not implement, install the service, issue Operator GO, consume mail, or take
a user-gated side effect.

## Operator2 — CLEAR Hold

`operator2-control-plane-authority-foundation-activation-repreflight` remains
blocked/observer-only. Reuse its attached CLEAR while Task 4 through EOF and the
activation contract remain unchanged. Send no receipt or duplicate report.

## R-VERIFY-TIER Disposition

Task2T is a first pass on a newly reproduced global-scan availability defect in
an unmerged reviewed candidate. Its regression is test-feasible; a strict-xfail
or repair commit was simply outside the exhausted Task2S route, so this immediate
normal-regression reroute does not suppress or defer it. Task3G asks only the new
runtime-isolation, lifetime, CLI/write-set, and hostile-type questions raised by
the binding Task3F contradiction. The OS credential boundary is genuinely
test-infeasible in ordinary unprivileged CI and therefore requires the named
privileged macOS selector before Task-3 GO. Neither lane repeats already-closed
questions.

## Side-Effect Executor Token

- side_effect_id: `control-plane-authority-task2t-task3g-reroute-2026-07-10`
- executor: `coordinator`
- target: local route mutation limited to `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-coordinator-join.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director-task2-race-fix.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director-task2-global-scan-fail-visible-fix.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3f-runner-capture-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-director2-task3g-runtime-isolation-contract-closure-preflight.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator-replacement-lanev.json`, `coordination/capacity/packets/2026-07-10-control-plane-authority-foundation-operator2-repreflight.json`, `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`, `docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`, and `coordination/mailbox/sent/2026-07-10T16-41-01Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, strict-pathspec `env -u GIT_INDEX_FILE git add` for nine visible paths, `env -u GIT_INDEX_FILE git add -f` for the ignored route, cached-name verification of exactly ten paths, and one local coordinator commit; no other mutation class
- preflight: user-principal said `continue as coordinator`; expected Pipeline HEAD is `8157e71d4c5a1580c380fd8a6154439b61de6f01`; the `15-18-04Z` and `15-41-08Z` reports are the newest binding mail and were read in full; refreshed index was empty and the only unrelated working-tree changes were eight AGENTS/Claude/Antigravity skill/protocol paths outside these ten token paths; routed HEAD is the clean `8cc4beed2c6c5836f915113ccd5104c3f039c8de` whose sole parent is `ef76fd11ea61e27778d0cedf65c1a608cf826354`; no Task2T child, Task3G disposition, cumulative verify-request, or newer route exists; Task 3A-through-3C, the accepted two-ref CAS segment, and Task 4 onward retain their expected hashes; and this route is absent from HEAD
- stop_if_newer_mail_or_live_target_satisfied: refresh before commit if Pipeline HEAD changes, newer coordinator mail or route appears, a Task2T child or cumulative verify-request lands, a Task3G disposition lands, the edit exceeds the ten named paths, routed HEAD moves from or becomes dirty at `8cc4beed2c6c5836f915113ccd5104c3f039c8de`, another child appears, peer WIP overlaps a named path, any immutable segment changes, or another committed route already closes either report
- postcheck: the coordinator commit is a direct child of refreshed expected Pipeline HEAD; cached and committed scope contains exactly the ten named paths; capacity board and this route validate; protocol doctor, smoke, doc claims, scoped diff checks, packet JSON, exact 18/21 selector counts, immutable-segment hashes, and Task-4 suffix hash pass; coordinator made no routed-worktree edit
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no Task2T or Task-3 production edit, proof-account/LaunchDaemon installation, privileged isolation run, amend/reset/rebase/squash, key or signed-ref mutation, authority flip, cursor consume, lock action, remote-ref update/push, force update, target-checkout refresh, paid-service spend, pod action, production generation, merge, protected-main update, or external deployment

Join condition: coordinator closes only after Director lands exactly one Task2T
child of `8cc4bee`, fresh specification and quality reviews pass, and one
cumulative verify-request names the six-commit range; Operator returns GO for
that exact range and all eighteen selectors/flips; Director2 returns CLEAR for
Task3G and all twenty-one Task-3D selectors while keeping the privileged
deployment boundary explicit; Operator2's prior CLEAR remains applicable;
routed provenance is clean; capacity board, route validation, protocol doctor,
smoke, doc claims, and immutable-segment checks pass; and no forbidden side
effect occurred. Any NITS, FAIL, CONTRADICTION, changed suffix, changed scope,
or newer route causes bounded reconciliation instead of closeout.

## Evidence

- The `15-18-04Z` and `15-41-08Z` mailbox bodies were read in full; no
  coordinator cursor was consumed.
- Direct reproduction against `8cc4bee` confirmed one global scan exception
  yields invalid count one, four `count=0` observations, and two
  `all-scope-unpinned` observations. The prior seventeen named nodes passed as
  nineteen parameterized cases; the new exact selector makes eighteen names.
- Source and call-site inspection confirmed `poll_once()` and the CLI accept
  registry/bus values, `scripts/run_merge_gate.sh` passes `--registry-dir`, and
  `tests/unit/test_threeway_activation_scripts.py` calls the old authority
  keywords outside the prior Task-3 write set.
- Darwin's local `launchd.plist(5)` manual confirms a system-domain job can run
  under `UserName`; `getpeereid(3)` confirms Unix-stream peer credentials are
  captured at connect/listen time. The design therefore uses a self-listening
  proof service rather than launchd socket activation.
- Capacity reconciliation is valid and active with new Director and Director2
  packets, while Operator and Operator2 remain blocked on their named
  dependencies. There are no locks.
- Packet JSON, exact 18/21 selector accounting, doc claims, and immutable plan
  hashes pass. Task 3A-through-3C is
  `f6f2052739c7cb7da49f0e9457578c391d532225874a470fc2d406d3c5705806`,
  the accepted two-ref CAS segment is
  `9b75fb1c81aaec449a247ded5d173dfcd2744b5149cf65c6b2d4cd652c7e3ad5`,
  and Task 4 through EOF is
  `8d44798592a4c87fc288f1cf25eff5c21e652574d0ed3a6076c4b72f8c14a6fd`.
- Three bounded read-only helpers independently checked Task2T root cause and
  selector arithmetic, Task3G security/caller boundaries, and the exact
  ten-path route mechanics. They made no edits and inherited no seat or side-
  effect authority.

## Exact Next Trigger

`continue as director` implements exactly one Task2T child of `8cc4bee`, then
runs fresh specification and quality review and sends the six-commit cumulative
verify-request. `continue as director2` performs only the Task3G runtime-
isolation/contract closure preflight and returns one CLEAR or CONTRADICTION.
Operator waits for the fresh request; Operator2 holds its existing CLEAR. No
proof-service installation, privileged integration run, remote publication, or
activation action is permitted.

Cursor at send: all-scope-unpinned
